# Step 2 — invisible perturbation

PGD (eps=8/255) against a differentiable face-identity model, face-masked.
v1 attacked FaceNet as surrogate — invisible (PSNR 45.4 dB) but did not transfer
to ArcFace (see RESULTS.md). Step 2b attacks ArcFace directly with the alignment
warp inside the loop.

Run: `python protect.py <input> <output>` · Measure: `python measure.py <clean> <protected>`
