# Architecture — Hifazat Suite

## System diagram

```
┌─────────────────────────────────────────────────────────────┐
│  Browser — Next.js (Urdu / Roman Urdu / English, RTL)       │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐  │
│  │ Nishan   │  │ Awaaz    │  │ Tainted  │  │ MIRAGE     │  │
│  │ (client) │  │ (upload) │  │ (upload) │  │ (upload)   │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └─────┬──────┘  │
│       │             │             │              │         │
│  IndexedDB     ─────┼─────────────┼──────────────┘         │
│  (originals,        │             │   HTTPS, in-memory     │
│   Nishan records,   │             │   processing only      │
│   encrypted backup) │             │                        │
└─────────────────────┼─────────────┼────────────────────────┘
                      ▼             ▼
            ┌──────────────┐ ┌──────────────┐ ┌────────────────┐
            │ Awaaz worker │ │ Tainted      │ │ MIRAGE GPU     │
            │ FastAPI +    │ │ worker       │ │ worker         │
            │ Enkidu       │ │ FastAPI +    │ │ FastAPI +      │
            │ (CPU/GPU)    │ │ MediaPipe +  │ │ PyTorch PGD    │
            │              │ │ ffmpeg (CPU) │ │ (queued)       │
            └──────────────┘ └──────────────┘ └────────────────┘
                      │             │              │
                      └─────────────┴──────────────┘
                        Delete upload immediately
                        after response. No content logs.
```

## Data flow — protect a photo (MIRAGE)

1. User picks photo in browser. File validated locally (type, size).
2. Upload over HTTPS to MIRAGE worker. Worker loads ensemble encoders, runs PGD optimisation in memory.
3. Protected PNG returned. Worker deletes input + intermediates.
4. Browser shows before/after slider + invisibility metrics (PSNR/SSIM/LPIPS). User downloads, posts.

## Data flow — prove the original (Nishan, fully local)

1. User registers a photo **before posting**: SHA-256 + pHash + timestamp computed in browser, stored in IndexedDB. Photo never uploaded.
2. Fake circulates. User uploads the fake **in the browser only**.
3. pHash Hamming distance vs local records → match / no-match with confidence.
4. Evidence pack PDF generated locally (Urdu/English): original hash, timeline, side-by-side, NCCIA complaint draft.

## Trust boundaries

- **Device boundary is the security boundary.** Originals, Nishan records, voiceprints stay on device.
- Workers are stateless and untrusted with retention: in-memory only, immediate delete, no logs.
- No accounts, no server database in v1 → nothing to breach, nothing to leak.

## Failure modes

| Failure | Behaviour |
|---|---|
| GPU worker down / queue full | Urdu message with queue position + "try Nishan/Awaaz meanwhile" — never a silent spinner |
| No internet at booth | Offline demo mode: local Nishan + pre-recorded Awaaz/Tainted/MIRAGE demos, labelled with dates |
| WhatsApp strips protection | Test matrix shows the measured drop; Nishan still matches by pHash |
| Closed editor patches moderator | MIRAGE refusal rate re-measured at demo time; date-stamped result |
