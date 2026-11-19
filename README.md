# Hifazat — Pakistan AI Defence Suite

**Protect your photo, voice and video before you post them. Prove what was real if a fake circulates.**

A four-module protection suite built for ordinary Pakistanis — students, girls, creators, journalists — in Urdu and English, designed to survive WhatsApp forwarding and low-end phones.

| Module | What it does | Research basis |
|---|---|---|
| **Nishan** | Prove the original: invisible tracer + hash + timestamp, one-click Urdu/English evidence pack for NCCIA 1799 | Data Isotopes (UChicago, PETS 2024), SynthID / C2PA provenance |
| **Awaaz Shield** | Cloak your voice before posting, so a clone comes out garbled | Enkidu (ACM MM 2025), SafeSpeech / AntiFake |
| **Tainted Video** | Protect a video selfie so a face-swap exposes itself | TaintedPixels (NUS, arXiv:2608.27492, Aug 2026), MUTE (NeurIPS 2026) |
| **MIRAGE Shield** | Make ChatGPT / Gemini *refuse* to edit your photo | MIRAGE (Univ. of Washington / UCLA, arXiv:2606.26199, Jun 2026) |

## Documents in this folder

- `PRD.md` — Product Requirements Document: problem, users, goals, scope, success criteria
- `TRD.md` — Technical Requirements Document: stack, architecture, APIs, security, non-functional requirements
- `ARCHITECTURE.md` — System architecture, data flow, deployment
- `TEST-MATRIX.md` — How we measure precision: invisibility, refusal rate, clone failure, WhatsApp survival
- `ROADMAP.md` — 5-week build plan, module by module
- `PRESENTATION-PLAN.md` — How to present this at a high level in Pakistan (CUSIT, COMPPEC, NSIF)
- `PAKISTAN-CHECK.md` — Has anyone in Pakistan done this? Evidence and honest claim wording

## Honest claim (use this wording, nothing stronger)

> "The first usable, Urdu-first AI protection suite for ordinary Pakistanis. Research papers exist — including NUST SEECS RAPID (Jul 2026) — but no free web tool a student can use before posting a photo, voice note or video exists in Pakistan today."

Do **not** claim "first in Pakistan" as research. NUST already published in this field. Claim the *usable product* gap, which is real and verifiable.

## Core principle

Protection is friction, not a guarantee. Every module raises the cost and buys time + evidence. We measure survival vs JPEG, crop, screenshot and WhatsApp re-encode on stage, and we say the limits out loud. Judges trust honest numbers more than 100% claims.

## Owner

Salal Mufeed — 18, self-taught builder, Pakistan. Founder, Toolixy (194+ tools, 31K users).
Stack: Next.js / TypeScript / Python. Solo build.

## Status

Planning — Nov 19, 2026. No code yet. Build order: Nishan → Awaaz → Tainted Video → MIRAGE.

## Run locally

```bash
npm install
npm run dev    # http://localhost:3000
npm test       # hamming unit tests
npm run typecheck
npm run build
```

Nishan works fully client-side in v0.1. Awaaz / Tainted / MIRAGE pages describe the module and their API routes return 501 until their workers land (Weeks 2-5, see ROADMAP.md).

## Awaaz worker (Week 2)

```bash
cd workers/awaaz && pip install -r requirements.txt
uvicorn app:app --port 8001   # needs universal_noise.pt from train_noise.py
AWAAZ_WORKER_URL=http://localhost:8001 npm run dev
```

See workers/awaaz/README.md and RESULTS.md (Opus survival measured 2026-11-19).
