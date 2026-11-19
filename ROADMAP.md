# Roadmap — 5-Week Build Plan

Solo build, Salal + Muse. One module per week, hardest last. Each week ends with a working demo + filled test matrix row — not just code.

## Week 1 — Nishan (proof)
- [ ] Browser-only register: SHA-256 + pHash + timestamp → IndexedDB
- [ ] Verify flow: upload fake → Hamming-distance match → confidence
- [ ] Evidence pack PDF (Urdu/English): hashes, timeline, side-by-side, NCCIA complaint draft
- [ ] Encrypted backup export/import (AES-GCM, passphrase)
- [ ] Test: WhatsApp forward match rate on 50-image set
- **Exit demo:** Register a photo, WhatsApp it, fake it, match it, print the pack. Offline.

## Week 2 — Awaaz Shield (voice)
- [ ] Enkidu repo running locally; protect a 10 s Urdu clip
- [ ] FastAPI worker + Next.js upload/record UI (Urdu labels)
- [ ] Attack demo: XTTS clone unprotected vs protected, speaker-similarity numbers
- [ ] **Day-1 test:** real WhatsApp voice-note round-trip survival
- [ ] Blind AB audibility test (10 listeners)
- **Exit demo:** Audience hears the clone fail. 30 seconds.

## Week 3 — Tainted Video
- [ ] MediaPipe face tracking + blue-channel periodic perturbation, motion-adaptive
- [ ] ffmpeg pipeline, CPU worker, upload UI
- [ ] Attack demo: FaceFusion swap on unprotected vs protected
- [ ] Recompression test: WhatsApp + TikTok round-trip
- **Exit demo:** Original looks normal, swap exposes stripes.

## Weeks 4–5 — MIRAGE Shield (research replication)
- [ ] Read MIRAGE paper end-to-end; list ensemble models, licences, availability
- [ ] Reproduce PGD optimisation vs open ensemble in Colab (T4)
- [ ] Live refusal test vs GPT-Image + Gemini Flash Image on 20-image set
- [ ] PhotoGuard baseline on same set (show the gap)
- [ ] Robustness battery: JPEG / crop / screenshot → re-test refusal
- [ ] GPU worker + queue UI (Urdu ETA, honest)
- **Exit demo:** Protected photo → both editors refuse, live. Date-stamped.

## Week 6 — Suite integration + presentation prep
- [ ] One domain, four modules, Urdu/English toggle, mobile-first polish
- [ ] Offline demo mode (recorded fallbacks, labelled)
- [ ] Poster + 5-minute stage script (Urdu story → 4 demos → test matrix → honest limits)
- [ ] Press pack: screenshots, 60-second demo video, founder story (18, self-taught, Pakistan, Toolixy 31K users)
- [ ] Venue applications: CUSIT (needs poster/date from Salal), COMPPEC NUST, NSIF — next cycles

## Rules for every week

1. No module is "done" until its test-matrix row is filled with measured numbers.
2. Verify live after every deploy. Check the actual URL, not the build log.
3. Nothing external (press, venues, posts) without Salal's explicit approval of exact text.
4. No "100% protection" language anywhere. Ever.
