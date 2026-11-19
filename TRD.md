# TRD — Hifazat: Pakistan AI Defence Suite

**Version:** 1.0 — Nov 19, 2026
**Companion:** `PRD.md` (what/why), `ARCHITECTURE.md` (system diagram), `TEST-MATRIX.md` (measurement)

---

## 1. Stack

| Layer | Choice | Why |
|---|---|---|
| Frontend | Next.js 14+ (App Router), TypeScript, Tailwind | Salal's stack; mobile-first; Urdu RTL support |
| i18n | next-intl, Urdu (Nastaliq) + Roman Urdu + English | Primary users are Urdu-first |
| API | Python FastAPI, one service per module | ML libraries are Python-native; modules fail independently |
| ML — MIRAGE | PyTorch, open CLIP-style encoders + open moderation models (e.g. ShieldGemma), PGD-style optimisation | Paper §III–IV recipe; transfer attack, no closed-model weights needed |
| ML — Awaaz | Enkidu repo (PyTorch), torchaudio, librosa; XTTS/IndexTTS for attack demo only | Enkidu inference is real-time (0.004 RTC), no GPU at inference |
| ML — Tainted Video | OpenCV + MediaPipe Face Mesh, ffmpeg; MUTE repo optional (audio) | CPU-feasible; blue-channel periodic perturbation, motion-adaptive |
| Nishan | SHA-256 + pHash (imagehash), C2PA JS SDK-style manifest, StegaStamp-style watermark (v1.1), PDF generation (Urdu/English) | No GPU; pHash survives WhatsApp recompression |
| Storage | **Local-first.** IndexedDB / OPFS on device for originals + Nishan records. Server stores nothing by default. | Trust: intimate photos never on Salal's server |
| GPU compute | Colab T4 (dev) → RunPod / HF Spaces GPU (demo), queue with rate limit | MIRAGE is minutes/image; cannot run free unlimited |
| Hosting | Frontend: Netlify/Vercel. Workers: DeployXA / HF Spaces. | PhishLens already on DeployXA; check live after every push |
| Auth | None in v1 (anonymous, local-first). Optional passphrase-encrypted local vault. | No accounts = no breach surface, no CNIC/age gate |

## 2. Architecture (summary — full diagram in ARCHITECTURE.md)

```
Browser (Next.js, Urdu/English)
  ├─ Nishan (fully client-side: hash, sign, evidence pack PDF)
  ├─ Awaaz  ──► FastAPI worker (Enkidu patch, in-memory, delete after)
  ├─ Tainted ─► FastAPI worker (MediaPipe + ffmpeg, CPU)
  └─ MIRAGE ──► FastAPI GPU worker (PGD optimisation, queued)
```

**Privacy invariant:** Originals are processed in memory and deleted immediately after the response. No logs of image/audio content. Nishan originals never leave the device at all.

## 3. API contracts (v1)

### POST /api/nishan/register (client-side only, no server call)
Input: image file (browser). Output: `{ nishan_id, sha256, phash, timestamp, manifest }` stored in IndexedDB.
Evidence pack: `POST /api/nishan/verify` is also client-side — match uploaded fake against local records by pHash Hamming distance, generate PDF locally.

### POST /api/awaaz/protect
Input: multipart audio (wav/mp3/ogg, ≤2 min, ≤10 MB), `enrol` flag.
Output: protected audio file + `{ speaker_similarity_before, speaker_similarity_after }` (measured vs enrolment clip if provided).
Errors: 400 unsupported format, 413 too large, 429 rate-limited.

### POST /api/tainted/protect
Input: multipart video (mp4, ≤60 s, ≤50 MB).
Output: protected mp4 + `{ frames_processed, lpips_estimate }`.
Processing: face-track per frame, blue-channel periodic perturbation in facial ROI, motion-adaptive strength, re-encode H.264.

### POST /api/mirage/protect
Input: multipart image (jpg/png, ≤10 MB), `strength` (ε budget, default 16/255).
Output: protected PNG + `{ psnr, ssim, lpips, refusal_test: { gpt_image, gemini } }` — refusal test is **manual/live** in v1 (no API keys for closed editors assumed); automated test harness is v1.1.
Async: returns `job_id`, poll `GET /api/mirage/jobs/{id}`. Target: minutes, not seconds. Queue position shown in UI (Urdu).

All endpoints: Urdu + English error messages, `X-Request-Id` for debugging (no content logging).

## 4. Non-functional requirements

- **Performance:** Nishan <2 s (client). Awaaz <30 s for 60 s audio. Tainted <2× video duration on CPU. MIRAGE: queued, honest ETA, no fake progress bar.
- **Mobile:** Works on a low-end Android Chrome over 3G. Uploads chunked/resumable where possible. UI usable at 360px width.
- **Offline demo mode:** Pre-recorded demo assets + local Nishan/Awaaz samples so a booth demo survives no internet. Live MIRAGE test needs internet — fallback is a dated screen recording, labelled as such.
- **Security:** HTTPS only. No content logs. Workers run with no persistent disk for uploads. Rate-limit per IP. File-type validation by magic bytes, not extension. No secrets in repo — keys in env vars only.
- **Accessibility:** Urdu RTL, large touch targets, audio descriptions for Awaaz demo, captions on Tainted Video demo.

## 5. Data model (local, per device)

```
NishanRecord {
  id: uuid,
  created_at: iso8601,
  sha256: hex,
  phash: hex64,
  manifest: { signer: "hifazat-local", timestamp, tool_version },
  thumbnail: data-url (optional, user-controlled),
  notes: string (optional)
}
```
No server database in v1. Export/import as encrypted JSON backup (passphrase, AES-GCM) — user holds the key.

## 6. Testing requirements

Every module ships with the test matrix in `TEST-MATRIX.md` filled with **measured** numbers, not paper claims:
- Invisibility: PSNR / SSIM / LPIPS (images, video), SNR / PESQ (audio), human suspicion rate.
- Protection: refusal rate (MIRAGE), clone speaker-similarity drop (Awaaz), forgery detection rate (Tainted), match rate after WhatsApp forward (Nishan).
- Robustness: JPEG q=50/75/90, crop 10/25%, resize 50%, screenshot, WhatsApp send-and-receive, TikTok upload-and-download.
- Baselines: unprotected control in every test. PhotoGuard (2023) as a second baseline for MIRAGE to show the 2026 gap.

## 7. Deployment

- Frontend: Netlify (mind credit freeze history — check before production deploys) or Vercel.
- Workers: DeployXA for CPU modules (Nishan is client-only anyway, Tainted CPU), HF Spaces / RunPod for GPU (MIRAGE, Awaaz enrolment).
- CI: typecheck + build on every push; **verify live after every push** (DeployXA auto-deploy failed once on PhishLens, Nov 13).
- Versioning: tool version stamped into every Nishan manifest and every protected file's metadata sidecar.

## 8. Open technical questions (resolve in Week 1)

1. MIRAGE: which open ensemble transfers best to GPT-Image + Gemini in Nov 2026? (Paper uses CLIP-style + ShieldGemma — verify availability/licence.)
2. Awaaz: does Enkidu's patch survive WhatsApp Opus at voice-note bitrates? Test through a real WhatsApp send in Week 2, Day 1.
3. Tainted: does blue-channel perturbation survive TikTok recompression? Measure before claiming.
4. Nishan: pHash threshold that matches a WhatsApp-forwarded fake without false-matching a different photo? Calibrate on a 100-image test set.

## 9. Licence / ethics

- Build on published research with attribution (MIRAGE, Enkidu, TaintedPixels, Data Isotopes, PhotoGuard, RAPID). Check each repo licence before reuse; Enkidu/IDGuardian-style repos are research code.
- Defensive use only. Never demo with real undressed/sexualised edits. Synthetic stand-ins only, blurred/redacted outputs, per PRD §7.
- No false DOB / borrowed ID for any gated service. Ever.
