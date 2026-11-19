"""Awaaz worker API. Cordum policy: DENY retention — audio is processed in a
temp dir and deleted in the same request; nothing is logged but status codes.

Run: uvicorn app:app --host 0.0.0.0 --port 8001
Env: AWAAZ_NOISE_PATH (default ./universal_noise.pt), AWAAZ_NOISE_LEVEL (0.4)
"""
import os, subprocess, tempfile
import torch
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import Response

from protect import add_noise, read_wav_16k, write_wav_16k, snr_db

app = FastAPI(title="Hifazat Awaaz Worker", version="0.1.0")
NOISE_PATH = os.environ.get("AWAAZ_NOISE_PATH", "universal_noise.pt")
MAX_BYTES = 10 * 1024 * 1024  # TRD: ≤10 MB, ≤2 min
_noise = None


def load_noise():
    global _noise
    if _noise is None and os.path.exists(NOISE_PATH):
        _noise = torch.load(NOISE_PATH, map_location="cpu")
    return _noise


@app.get("/health")
def health():
    n = load_noise()
    return {"ok": True, "module": "awaaz", "noise_trained": n is not None,
            "detail": "ready" if n else "universal_noise.pt missing — run train_noise.py first"}


@app.post("/protect")
async def protect(file: UploadFile = File(...)):
    noise = load_noise()
    if noise is None:
        raise HTTPException(503, "universal noise not trained yet — run train_noise.py (see README)")
    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(413, "audio too large (max 10 MB)")
    with tempfile.TemporaryDirectory() as td:
        src, wav16, out = (os.path.join(td, n) for n in ("in.bin", "in16.wav", "out.wav"))
        open(src, "wb").write(data)
        # Any format -> 16kHz mono 16-bit wav via ffmpeg (WhatsApp .ogg/.opus included)
        r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, "-ac", "1", "-ar", "16000",
                            "-sample_fmt", "s16", wav16], capture_output=True)
        if r.returncode != 0:
            raise HTTPException(400, "could not decode audio (send wav/mp3/ogg/m4a, ≤2 min)")
        x = read_wav_16k(wav16)
        if x.numel() > 16000 * 120:
            raise HTTPException(413, "audio too long (max 2 min)")
        y = add_noise(x, noise["noise_real"], noise["noise_imag"],
                      noise_level=float(noise.get("noise_level", 0.4)))
        write_wav_16k(out, y)
        # Read bytes before the temp dir is deleted (FileResponse would stream after cleanup).
        return Response(content=open(out, "rb").read(), media_type="audio/wav",
                        headers={"Content-Disposition": 'attachment; filename="awaaz-protected.wav"',
                                 "X-Hifazat-SNR-dB": f"{snr_db(x, y):.1f}"})
