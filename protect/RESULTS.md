# Step 2 results — 2026-11-20 (v1: FaceNet surrogate)

Setup: PGD 200 steps, eps=8/255, alpha=1/255, face-box masked (+20%), optimized
against FaceNet (InceptionResnetV1/VGGFace2) cosine-to-clean. Measured with the
Step 1 ArcFace harness (buffalo_l). Test face: AI-generated fictional portrait.
Runtime: 15m58s on this CPU.

| Measurement | Value | Meaning |
|---|---|---|
| FaceNet cosine clean-vs-protected | **-0.8958** | surrogate fully fooled |
| **ArcFace cosine clean-vs-protected** | **0.9892** | **target NOT fooled** |
| PSNR | 45.36 dB | invisible |
| SSIM | 0.9998 | invisible |
| Max pixel change | 9/255 | within eps budget (+rounding) |

## Honest verdict: invisible YES, transfer NO

The perturbation is genuinely imperceptible, and it destroys the FaceNet
embedding. It does **not** transfer to ArcFace. Likely causes, in order:
1. **Alignment mismatch** — we optimized on a bbox crop+resize; ArcFace first
   warps the face with a 5-point similarity transform to 112x112. Resampling
   destroys high-frequency PGD noise tuned for a different preprocessing.
2. **Architecture mismatch** — FaceNet (InceptionResnet) vs ArcFace (ResNet50)
   adversarial transfer is weak at eps=8/255.

This matches the research warning (Phantom, CVPR 2026): generic FR
perturbations often fail downstream; identity-direction-aware, preprocessing-
matched attacks are needed.

## Step 2b (next): attack ArcFace directly
- Differentiable ArcFace in PyTorch (insightface arcface_torch weights),
  with the 5-point alignment warp **inside** the optimization loop
  (grid_sample), so the noise is optimized for the exact pixels ArcFace sees.
- Ensemble loss: ArcFace + FaceNet (+ CLIP later, IDGuardian-style).
- Same budget: eps=8/255. Success = ArcFace cosine < 0.35 (different-person
  territory) at PSNR >= 35 dB.
