# Step 1 — ArcFace harness (the ruler)

Detect → align → embed with InsightFace `buffalo_l` (SCRFD + ArcFace ResNet50),
the same first steps Roop/FaceFusion take. Cosine similarity between two photos'
512-D identity vectors is the number every later Hifazat step is measured with.

Run: `python embed.py <image1> <image2>` · Self-check: `python test_harness.py <personA> <personB>`

Models auto-download to `~/.insightface` on first run (non-commercial research licence).
