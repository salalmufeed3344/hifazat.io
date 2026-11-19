# PRD — Hifazat: Pakistan AI Defence Suite

**Version:** 1.0 — Nov 19, 2026
**Owner:** Salal Mufeed
**Status:** Approved for planning. Build starts with Nishan (Week 1).

---

## 1. Problem

In Pakistan, a single photo, voice note or video can be stolen and turned into a fake in seconds:

- **Photo edited into something illegal.** Anyone can take a profile photo and AI-edit it — change clothes, place the person somewhere they never were, sexualise it. PECA Section 21 covers superimposing a face onto sexually explicit content: up to 7 years imprisonment and Rs 5 million fine, non-bailable. FIA received **1,180 deepfake / non-consensual intimate image complaints in 2023**. UN Women (Feb 2026) linked deepfake abuse to honour-based violence risk in Pakistan.
- **Voice cloned for scams.** Only ~3 seconds of voice is needed to clone. A mother's WhatsApp voice note forwarded in a family group becomes a "beta, accident, send Rs 50,000" scam call.
- **Video face-swapped.** Short selfie videos and TikTok clips are swapped and lip-synced. Video is the trust medium in Pakistan — WhatsApp video messages, TikTok.
- **No proof when a fake circulates.** PECA makes it a crime, but a victim cannot *prove* which photo is real, when it was posted, or that the fake came later. NCCIA helpline is 1799, but there is no tool that gives a victim a ready-to-file evidence pack in Urdu.

Existing protection research (MIT PhotoGuard 2023, Glaze, Nightshade) is broken against 2026 editors and purification, and none of it is a usable tool for a Pakistani student on a low-end phone. See `PAKISTAN-CHECK.md`.

## 2. Users

**Primary:**
- Female students and young women posting profile photos on Instagram / WhatsApp — highest harm, honour-based risk.
- Students and creators posting voice notes, status videos, TikTok clips.
- Journalists and public figures whose photos/videos get swapped.

**Secondary:**
- Parents / elders receiving cloned-voice scam calls.
- Teachers, community groups, NCCIA awareness programmes.

**User constraints (design for these, not for a lab):**
- Low-end Android phone, patchy internet, WhatsApp-first sharing.
- Urdu / Roman Urdu first, English second. No technical vocabulary.
- Cannot pay. Must be free at point of use.
- Cannot trust a random website with intimate photos. **Originals must stay on-device.**

## 3. Goals

1. A free, Urdu-first web suite where a user protects a photo, voice note or video **before posting**, in under 2 minutes.
2. If a fake circulates, a one-click Urdu/English evidence pack for an NCCIA 1799 complaint.
3. Measured precision, not claims: every module ships with a test matrix (invisibility, protection rate, WhatsApp survival) shown live.
4. Presentable at a high level in Pakistan (CUSIT, COMPPEC NUST, NSIF) as a technical system with honest limits.

**Non-goals (v1):**
- No guarantee of safety. This raises the bar, buys time, creates evidence. Never market as "100% protection".
- No detection of arbitrary fakes (that is Sach Checker / PhishLens territory — separate).
- No server-side storage of user originals.
- No paid tier in v1.

## 4. The four modules

### 4.1 Nishan — Prove the original
Before posting, the tool embeds an invisible tracer + perceptual hash + timestamp, signs it (C2PA-style manifest, SHA-256 + pHash), and stores the original **on-device only**. If a fake circulates, the user uploads the fake, the tool matches it to the Nishan record, and generates an evidence pack: original hash, timeline, side-by-side, filled NCCIA complaint draft in Urdu/English.

- *Why first:* No GPU, works offline, guaranteed demo even if booth internet dies.
- *Success:* A fake uploaded after WhatsApp forwarding is correctly matched to its original in ≥90% of test cases (pHash survives recompression better than metadata).

### 4.2 Awaaz Shield — Cloak your voice
Upload or record a voice clip → apply a learned universal patch (Enkidu, ACM MM 2025) → download a protected clip that sounds identical to humans but clones badly. Optional enrolment: 3-second voiceprint for family verification.

- *Demo:* Clone unprotected voice with open XTTS → sounds like them. Clone protected → garbled / wrong speaker. Audience *hears* it fail.
- *Success:* Speaker-similarity of clones from protected audio drops measurably vs unprotected, tested through a real WhatsApp send (Opus compression), not just WAV.

### 4.3 Tainted Video — Make the fake expose itself
Upload a short face video → embed structured periodic perturbations in the blue channel of facial regions, motion-adaptive per frame (TaintedPixels, Aug 2026) → download a video that looks normal, but any face-swap / lip-sync forgery shows visible stripes/glitching.

- *Honest framing:* Does **not** stop the fake. Makes it *obvious*. Say "exposes", never "blocks".
- *Success:* Forgery detection (human + automated) significantly higher on protected vs unprotected, measured after WhatsApp/TikTok recompression.

### 4.4 MIRAGE Shield — Make commercial editors refuse
Upload a photo → imperceptible perturbations align it to policy-violating concepts in an ensemble of open embedding/moderation models (MIRAGE, Jun 2026) → ChatGPT / Gemini / Grok's own safety moderator flags it and **refuses** to edit, regardless of prompt.

- *Why last:* Hardest. Paper-only, no code exists. Replication is the research contribution. GPU minutes per image.
- *Success:* Refusal rate measured live against GPT-Image and Gemini Flash Image, reported honestly (paper claims >88%, self-reported, no independent replication yet).

## 5. User journeys

**Journey A — Protect before posting (2 minutes):**
Open site → choose Photo / Voice / Video → upload → choose protection level → download protected file → post it. Urdu labels, one button per step.

**Journey B — A fake is circulating (5 minutes):**
Open Nishan → upload fake → tool matches original → download evidence pack (PDF, Urdu/English) → file at NCCIA 1799 / cybercrime.gov.pk with the pack attached.

**Journey C — Judge / press demo (5 minutes, stage):**
Nishan proof pack → Awaaz clone fails live → Tainted Video fake exposes itself → MIRAGE refusal in ChatGPT → test matrix + honest limits.

## 6. Success criteria (v1, suite level)

- All four modules live on one domain, Urdu/English toggle, mobile-first.
- Each module has a published test matrix with real numbers (see `TEST-MATRIX.md`), including WhatsApp survival.
- No user original ever leaves the device unencrypted; Nishan originals never uploaded at all.
- Demo runs end-to-end in under 5 minutes, with recorded fallback if internet fails.
- Zero claims of "100% protection" anywhere in UI, poster or pitch.

## 7. Risks and mitigations

| Risk | Mitigation |
|---|---|
| MIRAGE moderators change / patch | Frame as time-limited friction; measure refusal rate at demo time, report date |
| Protection stripped by JPEG/crop/screenshot | Test matrix measures it; Nishan pHash survives recompression; never claim permanence |
| Users won't want visible marks | All v1 protections are invisible; visible "Zehr" pattern is a future option, not v1 |
| Sensitive photos on server = trust failure | Local-first architecture; GPU workers process in memory, delete immediately, log nothing |
| Over-claiming gets demolished by a judge | Honest limits slide in every presentation; percentages labelled "paper's claim" vs "our measured" |
| GPU cost for MIRAGE/Awaaz | Colab / RunPod spot for demo; queue + rate-limit free tier; Nishan/Tainted are CPU-cheap |

## 8. Out of scope / future

Kapra Shield (copying-as-defense), IDGuardian (one-photo face cloning), Anti-I2V (photo-to-video), Aposema/Zehr (visible warning), Gharana SafeWord (family safe word), Sach Checker (forward checker) — all researched Nov 18, 2026, all viable v2 modules. Not in v1 scope.

## 9. References

- MIRAGE: arXiv:2606.26199 (Jun 2026) — https://arxiv.org/abs/2606.26199
- Enkidu: arXiv:2507.12932 (ACM MM 2025) — https://github.com/NoobCodeNameless/Enkidu
- TaintedPixels: arXiv:2608.27492 (Aug 2026) — https://arxiv.org/abs/2608.27492
- Data Isotopes: PETS 2024 (UChicago SAND Lab)
- PhotoGuard: arXiv:2302.06588 (MIT CSAIL, 2023) — baseline, known broken vs 2026 editors
- RAPID: NUST SEECS (Jul 2026) — Pakistan research baseline, paper + code, no usable tool
- PECA 2016 §21, PECA Amendment 2025; NCCIA helpline 1799
