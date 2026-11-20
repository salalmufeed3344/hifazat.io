"""Self-check: same person must score high, different person low."""
import sys
import cv2
from embed import embed, cosine

A, B = sys.argv[1], sys.argv[2]  # A = person 1, B = different person

img = cv2.imread(A)
h, w = img.shape[:2]
variant = cv2.resize(img[int(h * 0.05):, int(w * 0.05):], (w, h))  # crop+resize
variant = cv2.convertScaleAbs(variant, alpha=1.05, beta=5)          # light change
cv2.imwrite("/tmp/harness_variant.jpg", variant, [cv2.IMWRITE_JPEG_QUALITY, 85])

ea, ev, eb = embed(A), embed("/tmp/harness_variant.jpg"), embed(B)
same, variant_sim, diff = cosine(ea, ea), cosine(ea, ev), cosine(ea, eb)
print(f"self:            {same:.4f}  (expect ~1.0)")
print(f"same, re-photo'd:{variant_sim:.4f}  (expect > 0.5)")
print(f"different person:{diff:.4f}  (expect < 0.35)")
assert same > 0.999 and variant_sim > 0.5 and diff < 0.35, "harness separation FAILED"
print("harness separation OK")
