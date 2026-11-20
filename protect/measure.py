"""Measure a protected image with the Step 1 ArcFace ruler + visibility numbers."""
import sys
import cv2
import numpy as np

sys.path.insert(0, "../harness")
from embed import embed, cosine  # noqa: E402


def psnr(a, b):
    mse = ((a.astype(float) - b.astype(float)) ** 2).mean()
    return float(10 * np.log10(255 ** 2 / mse)) if mse else float("inf")


def ssim(a, b):
    a, b = a.astype(float), b.astype(float)
    c1, c2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2
    mu_a, mu_b = a.mean(), b.mean()
    var_a, var_b = a.var(), b.var()
    cov = ((a - mu_a) * (b - mu_b)).mean()
    return float(((2 * mu_a * mu_b + c1) * (2 * cov + c2)) / ((mu_a**2 + mu_b**2 + c1) * (var_a + var_b + c2)))


if __name__ == "__main__":
    clean, prot = sys.argv[1], sys.argv[2]
    a, b = cv2.imread(clean), cv2.imread(prot)
    print(f"ArcFace cosine clean-vs-protected: {cosine(embed(clean), embed(prot)):.4f}  (clean-vs-clean = 1.0, different person ~0.2)")
    print(f"PSNR: {psnr(a, b):.2f} dB   SSIM: {ssim(a, b):.4f}   max pixel change: {np.abs(a.astype(int)-b.astype(int)).max()}/255")
