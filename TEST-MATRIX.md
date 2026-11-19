# Test Matrix — How We Measure Precision

**Rule:** No number goes on a poster, slide or pitch unless it was measured by us, on our test set, with the date and conditions written next to it. Paper claims are labelled "paper's claim, not independently replicated".

## Test set

- **Images:** 50 portraits (diverse, consented / synthetic), 20 non-face photos. No real intimate images, ever.
- **Audio:** 20 Urdu + 10 English voice clips, 5–60 s, recorded on low-end Android mics.
- **Video:** 20 short face videos, 5–30 s, phone-recorded.
- Every test runs an **unprotected control** side-by-side. Same prompt, same seed where applicable.

## Per-module metrics

### Nishan
| Metric | Target (v1) | How |
|---|---|---|
| Match rate after WhatsApp forward | ≥90% | Register → send via WhatsApp → receive → verify |
| False-match rate | <1% | Verify 100 unrelated photos against records |
| Time to evidence pack | <60 s | Stopwatch, low-end phone |

### Awaaz Shield
| Metric | Target (v1) | How |
|---|---|---|
| Clone speaker-similarity drop | Report measured Δ, no fixed promise | Enrol → protect → clone with XTTS (unprotected vs protected) → ECAPA cosine |
| Audibility | PESQ / human AB test: "can you hear a difference?" | 10 listeners, blind |
| WhatsApp survival | Report Δ after real WhatsApp send | Protect → WhatsApp voice note → receive → clone attempt |

### Tainted Video
| Metric | Target (v1) | How |
|---|---|---|
| Invisibility | LPIPS + human suspicion rate | Original vs protected, blind rating |
| Forgery exposure | Detection rate protected vs unprotected | FaceFusion/Roop swap on both, human + automated rating |
| Recompression survival | Report after WhatsApp + TikTok round-trip | Upload → download → swap again |

### MIRAGE Shield
| Metric | Target (v1) | How |
|---|---|---|
| Invisibility | PSNR / SSIM / LPIPS at ε=16/255 | Standard metrics, reported per image |
| Refusal rate — GPT-Image | Report measured %, date-stamped | 20 protected images × 3 edit prompts, live, manual |
| Refusal rate — Gemini Flash Image | Report measured %, date-stamped | Same set |
| Baseline comparison | PhotoGuard (2023) on same set | Shows the 2026 gap honestly |
| Robustness | Refusal after JPEG q75, crop 10%, screenshot | Re-test refusal on transformed copies |

## Robustness battery (all image/video modules)

JPEG quality 50 / 75 / 90 · Crop 10% / 25% · Resize 50% · Screenshot · WhatsApp send-and-receive · TikTok upload-and-download · Purification attempt (EditorClean-style, if available)

Report protection **after each transform**, not just on the pristine file. WhatsApp survival is the Pakistan test.

## Reporting template (every result)

```
Module: MIRAGE | Date: 2026-__-__ | Test set: 20 portraits | Editor: Gemini Flash Image
Unprotected edit success: __/20 | Protected refusal: __/20 | After JPEG q75: __/20
Invisibility: PSNR __ dB, SSIM __, LPIPS __ | Notes: ___
```

## Ethics of testing

- Synthetic / consented stand-ins only for any sexualised-edit test. Outputs blurred/redacted. Never generate real undressed images of real people, in testing or on stage.
- Voice cloning tests only on Salal's own voice and consented volunteers.
- Face-swap tests only on consented / synthetic faces.
