"""Tainted Video worker API. Cordum: DENY retention — temp dir, deleted per request.
Run: uvicorn app:app --host 0.0.0.0 --port 8002
Env: TAINTED_AMPLITUDE (default 10), TAINTED_FALLBACK_CENTER=1 (test/demo only)
"""
import os, tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import Response

from protect import protect_video, ensure_model

app = FastAPI(title="Hifazat Tainted Video Worker", version="0.1.0")
MAX_BYTES = 50 * 1024 * 1024  # TRD: ≤50 MB, ≤60 s
AMPLITUDE = float(os.environ.get("TAINTED_AMPLITUDE", "16"))
PERIOD = int(os.environ.get("TAINTED_PERIOD", "24"))
FALLBACK = os.environ.get("TAINTED_FALLBACK_CENTER") == "1"


@app.get("/health")
def health():
    try:
        ensure_model(); model_ok = True
    except Exception:
        model_ok = False
    return {"ok": True, "module": "tainted", "face_model_ready": model_ok, "amplitude": AMPLITUDE, "period": PERIOD}


@app.post("/protect")
async def protect(file: UploadFile = File(...)):
    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(413, "video too large (max 50 MB)")
    with tempfile.TemporaryDirectory() as td:
        src, out = os.path.join(td, "in.bin"), os.path.join(td, "out.mp4")
        open(src, "wb").write(data)
        try:
            stats = protect_video(src, out, amplitude=AMPLITUDE, period=PERIOD, fallback_center=FALLBACK)
        except ValueError as e:
            raise HTTPException(422, str(e))
        return Response(content=open(out, "rb").read(), media_type="video/mp4",
                        headers={"Content-Disposition": 'attachment; filename="tainted-protected.mp4"',
                                 "X-Hifazat-Frames": str(stats["frames"]),
                                 "X-Hifazat-Face-Frames": str(stats["face_frames"])})
