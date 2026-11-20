"""Hifazat Step 2 — invisible perturbation (PGD) against face-identity embedding.

Optimizes against FaceNet (differentiable surrogate), measured with the ArcFace
harness. Perturbation budget: eps=8/255, face-region masked. Eyes should not
catch it; the identity vector should move far.
"""
import sys
import cv2
import numpy as np
import torch
import torch.nn.functional as F
from facenet_pytorch import InceptionResnetV1

sys.path.insert(0, "../harness")
from embed import _get_app  # noqa: E402  (reuse buffalo_l detector)

EPS = 8 / 255
ALPHA = 1 / 255
STEPS = 200

_model = None


def _facenet():
    global _model
    if _model is None:
        _model = InceptionResnetV1(pretrained="vggface2").eval()
        for p in _model.parameters():
            p.requires_grad_(False)
    return _model


def face_box(img_bgr):
    faces = _get_app().get(img_bgr)
    if not faces:
        raise ValueError("no face detected")
    f = max(faces, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]))
    x1, y1, x2, y2 = [int(v) for v in f.bbox]
    mx, my = int((x2 - x1) * 0.2), int((y2 - y1) * 0.2)  # expand 20%
    h, w = img_bgr.shape[:2]
    return max(0, x1 - mx), max(0, y1 - my), min(w, x2 + mx), min(h, y2 + my)


def _embed_tensor(x, box):
    x1, y1, x2, y2 = box
    crop = x[:, :, y1:y2, x1:x2]
    crop = F.interpolate(crop, size=(160, 160), mode="bilinear", align_corners=False)
    return _facenet()((crop * 2 - 1))  # facenet standardization


def protect(in_path, out_path, steps=STEPS):
    img = cv2.imread(in_path)
    if img is None:
        raise ValueError(f"cannot read image: {in_path}")
    box = face_box(img)
    x = torch.from_numpy(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)).permute(2, 0, 1).float().unsqueeze(0) / 255.0
    mask = torch.zeros_like(x)
    x1, y1, x2, y2 = box
    mask[:, :, y1:y2, x1:x2] = 1.0
    with torch.no_grad():
        target = _embed_tensor(x, box)
    delta = torch.zeros_like(x, requires_grad=True)
    for _ in range(steps):
        emb = _embed_tensor((x + delta).clamp(0, 1), box)
        loss = F.cosine_similarity(emb, target).mean()  # minimize identity match
        loss.backward()
        with torch.no_grad():
            delta -= ALPHA * delta.grad.sign() * mask
            delta.clamp_(-EPS, EPS)
            delta.grad.zero_()
    adv = (x + delta.detach()).clamp(0, 1)
    out = (adv.squeeze(0).permute(1, 2, 0).numpy() * 255).astype(np.uint8)
    cv2.imwrite(out_path, cv2.cvtColor(out, cv2.COLOR_RGB2BGR))
    return float(loss.item())


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: protect.py <input> <output>")
    print(f"final FaceNet cosine vs clean: {protect(sys.argv[1], sys.argv[2]):.4f}")
