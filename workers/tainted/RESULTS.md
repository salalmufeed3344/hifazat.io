# Tainted Video — measured results

## 2026-11-19 · Recompression survival sweep (synthetic video, signal-level)

Setup: synthetic 320×240 video, centre-region taint (no real face — fallback
mode), ffmpeg libx264 CRF 32 round-trip (WhatsApp/TikTok range), perturbation
correlation measured in the tainted region.

| Period (px) | Amplitude (blue delta) | CRF32 correlation | Survival |
|---|---|---|---|
| 8 | 10 | 0.101 | 0.577 |
| 16 | 10 | 0.315 | 0.631 |
| 16 | 16 | 0.598 | 0.602 |
| **24** | **16** | **0.787** | **0.732** |
| 32 | 20 | 0.899 | 0.801 |

Finding: fine patterns (period 8) are destroyed by social-platform
recompression. Low-frequency patterns survive. **Defaults set to period=24,
amplitude=16** (correlation 0.79 @CRF32); period 32/amp 20 survives better
(0.90) but is more visible — visibility on a real face must be checked before
raising defaults.

Unit tests pass: blue-channel only, inside face ellipse only, amplitude
bounded, phase advances per frame. Worker e2e verified (75 frames in/out).

**Not measured yet (required before any effectiveness claim):**
- Face-swap exposure with Roop/FaceFusion on protected real-face video
  (paper reports 90.72% human spotting — our number must be measured, not borrowed)
- Visibility/LPIPS on real faces at period 24 / amplitude 16
- WhatsApp/TikTok actual platform round-trip (CRF is a proxy)
