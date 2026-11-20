"""Hifazat Step 1 — ArcFace identity-embedding harness (the ruler).

Detect -> align -> embed, exactly the first steps a face-swap app takes.
No protection here. Later steps are measured with this.
"""
import sys
import cv2
import numpy as np
from insightface.app import FaceAnalysis

_app = None


def _get_app():
    global _app
    if _app is None:
        _app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
        _app.prepare(ctx_id=-1, det_size=(640, 640))
    return _app


def embed(path):
    """Return the 512-D ArcFace identity vector for the largest face in an image."""
    img = cv2.imread(path)
    if img is None:
        raise ValueError(f"cannot read image: {path}")
    faces = _get_app().get(img)
    if not faces:
        raise ValueError(f"no face detected: {path}")
    face = max(faces, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]))
    return face.normed_embedding  # 512-D, L2-normalized


def cosine(a, b):
    return float(np.dot(a, b))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: embed.py <image1> <image2>")
    print(f"cosine similarity: {cosine(embed(sys.argv[1]), embed(sys.argv[2])):.4f}")
