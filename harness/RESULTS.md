# Step 1 results — 2026-11-20

Setup: InsightFace buffalo_l (SCRFD + ArcFace ResNet50), CPU. Test faces:
two AI-generated fictional portraits (young woman = person A, bearded man = person B).
"Re-photo'd" = 5% crop + resize + brightness shift + JPEG Q85 of person A.

| Comparison | Cosine | Expected |
|---|---|---|
| A vs A (self) | **1.0000** | ~1.0 |
| A vs A re-photo'd | **0.9501** | > 0.5 |
| A vs B (different person) | **0.2002** | < 0.35 |

Harness separation OK — the ruler matches published genuine/impostor behaviour.
Every later step (perturbation, JPEG/WhatsApp robustness, swap test) is measured
against these numbers.
