# Awaaz — measured results

## 2026-11-19 · Opus survival feasibility (signal-level only)

Setup: synthetic voice-like clip (harmonic stack, 4s @16k), **untrained** test
noise at noise_level=0.4 through `protect.add_noise`, then ffmpeg libopus
round-trip at WhatsApp voice-note bitrates.

| Bitrate | Perturbation survival | Correlation before/after |
|---|---|---|
| 32k | 1.505 | 0.575 |
| 48k | 1.163 | 0.795 |

Reading: Opus does not fully strip an STFT-domain perturbation, but at 32k the
perturbation's structure is substantially altered (correlation 0.58). Training
must include Opus augmentation, or WhatsApp forwarding may weaken protection.
Survival >1 means Opus artifacts add energy — energy alone is not protection.

**Not measured yet (required before any protection claim):**
- ECAPA cosine similarity clean-vs-protected with *trained* noise on real speech
- XTTS clone intelligibility/similarity, before and after WhatsApp round-trip
- Human audibility (SNR + listening test) at the chosen noise_level

Unit tests: `test_protect.py` passes (shape preserved, clamped, SNR 8.5 dB on
white-noise input with untrained noise — trained noise on speech will differ).
