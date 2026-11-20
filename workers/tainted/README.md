# Tainted Video Worker — fake exposes itself

Method: TaintedPixels (arXiv:2608.27492, Aug 2026) — periodic blue-channel
perturbations inside facial regions, motion-adaptive per frame. A face-swap
made from a protected video inherits visible striping.

**Honest framing: this does not block face-swaps. It makes them obvious.**

## Run

```bash
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8002
curl localhost:8002/health
curl -F file=@selfie.mp4 localhost:8002/protect -o tainted-protected.mp4
```

Face model (YuNet ONNX, 228KB, from opencv_zoo) downloads automatically on
first run to `models/` — it is a binary, so it is gitignored, not committed.
Video ≤60s, ≤50 MB, clear face (selfie-style). Processed in a temp dir,
deleted with the request. Nothing stored.

Env: `TAINTED_AMPLITUDE` (default 10, blue-channel delta), `TAINTED_MODEL_PATH`.

## Tests

```bash
python test_taint.py                       # perturbation unit tests
python test_recompress.py clean.mp4 protected.mp4   # WhatsApp/TikTok survival
```

See RESULTS.md for measured numbers. Face-swap exposure (Roop/FaceFusion)
must be measured before any effectiveness claim — see TEST-MATRIX.md.
