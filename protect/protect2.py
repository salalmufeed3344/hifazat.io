"""Hifazat Step 2b — attack ArcFace directly, alignment warp inside the loop.

v1 (FaceNet surrogate) was invisible but did not transfer: ArcFace first warps
the face with a 5-point similarity transform, destroying noise tuned for a
different preprocessing. Here the exact warp is inside the optimization, and
the loss ensembles ArcFace (converted from buffalo_l ONNX, parity-verified)
with FaceNet. Budget unchanged: eps=8/255.
"""
import sys
import cv2
import numpy as np
import torch
import torch.nn.functional as F
from facenet_pytorch import InceptionResnetV1
from onnx2torch import convert
from skimage.transform import SimilarityTransform

sys.path.insert(0, "../harness")
from embed import _get_app  # noqa: E402
from protect import face_box, _facenet  # noqa: E402

EPS = 8 / 255
ALPHA = 1 / 255
STEPS = 200
ARCFACE_ONNX = "/home/hatch/.insightface/models/buffalo_l/w600k_r50.onnx"
# ArcFace 112x112 template (insightface face_align)
TEMPLATE = np.array(
    [[38.2946, 51.6963], [73.5318, 51.5014], [56.0252, 71.7366],
     [41.5493, 92.3655], [70.7299, 92.2041]], dtype=np.float32)

_arcface = None


def _arcface_model():
    global _arcface
    if _arcface is None:
        _arcface = convert(ARCFACE_ONNX).eval()
        for p in _arcface.parameters():
            p.requires_grad_(False)
    return _arcface


def _warp_matrix(img_bgr):
    """Affine grid matrix (dst 112x112 normalized -> src normalized) for grid_sample."""
    faces = _get_app().get(img_bgr)
    if not faces:
        raise ValueError("no face detected")
    f = max(faces, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]))
    tform = SimilarityTransform()
    tform.estimate(f.kps.astype(np.float32), TEMPLATE)
    M = np.vstack([tform.params[:2], [0, 0, 1]]).astype(np.float64)  # src px -> dst px
    M_inv = np.linalg.inv(M)  # dst px -> src px
    h, w = img_bgr.shape[:2]
    dst_n = np.array([[-1, -1], [1, -1], [-1, 1]], dtype=np.float64)
    dst_px = (dst_n + 1) / 2 * 112 - 0.5  # dst pixel-center coords
    src_px = (M_inv @ np.hstack([dst_px, np.ones((3, 1))]).T).T[:, :2]
    src_n = (src_px + 0.5) / np.array([w, h]) * 2 - 1
    A = np.hstack([dst_n, np.ones((3, 1))])
    theta = np.linalg.solve(A, src_n).T.astype(np.float32)  # 2x3
    return torch.from_numpy(theta).unsqueeze(0)


def _arcface_embed(x, theta):
    grid = F.affine_grid(theta, size=(1, 3, 112, 112), align_corners=False)
    crop = F.grid_sample(x, grid, mode="bilinear", padding_mode="zeros", align_corners=False)
    return _arcface_model()((crop - 0.5) / 0.5)  # arcface input norm


def _facenet_embed(x, box):
    x1, y1, x2, y2 = box
    crop = F.interpolate(x[:, :, y1:y2, x1:x2], size=(160, 160), mode="bilinear", align_corners=False)
    return _facenet()((crop * 2 - 1))


def protect2(in_path, out_path, steps=STEPS):
    img = cv2.imread(in_path)
    if img is None:
        raise ValueError(f"cannot read image: {in_path}")
    box, theta = face_box(img), _warp_matrix(img)
    x = torch.from_numpy(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)).permute(2, 0, 1).float().unsqueeze(0) / 255.0
    mask = torch.zeros_like(x)
    x1, y1, x2, y2 = box
    mask[:, :, y1:y2, x1:x2] = 1.0
    with torch.no_grad():
        t_arc, t_face = _arcface_embed(x, theta), _facenet_embed(x, box)
    delta = torch.zeros_like(x, requires_grad=True)
    for _ in range(steps):
        adv = (x + delta).clamp(0, 1)
        loss = (F.cosine_similarity(_arcface_embed(adv, theta), t_arc).mean()
                + F.cosine_similarity(_facenet_embed(adv, box), t_face).mean())
        loss.backward()
        with torch.no_grad():
            delta -= ALPHA * delta.grad.sign() * mask
            delta.clamp_(-EPS, EPS)
            delta.grad.zero_()
    out = ((x + delta.detach()).clamp(0, 1).squeeze(0).permute(1, 2, 0).numpy() * 255).astype(np.uint8)
    cv2.imwrite(out_path, cv2.cvtColor(out, cv2.COLOR_RGB2BGR))
    return float(loss.item())


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: protect2.py <input> <output>")
    print(f"final ensemble cosine sum vs clean: {protect2(sys.argv[1], sys.argv[2]):.4f}")
