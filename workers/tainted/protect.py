"""Tainted Video — TaintedPixels-method protection (serving path).

Method from: TaintedPixels, arXiv:2608.27492 (Aug 2026) — structured periodic
perturbations in the blue channel, restricted to facial regions, motion-
adaptive per frame. The protected video looks normal; a face-swap built from
it inherits visible periodic striping, so the fake exposes itself.
Implemented here from the paper's described method (no public code exists).

Honest framing: this does NOT block face-swaps. It makes them obvious.
"""
import os
import cv2
import numpy as np

MODEL_URL = "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx"
MODEL_PATH = os.environ.get("TAINTED_MODEL_PATH", os.path.join(os.path.dirname(__file__), "models", "face_detection_yunet_2023mar.onnx"))


def ensure_model() -> str:
    if not os.path.exists(MODEL_PATH):
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        import urllib.request
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    return MODEL_PATH


def make_detector(w: int, h: int):
    return cv2.FaceDetectorYN_create(ensure_model(), "", (w, h), 0.6, 0.3, 5000)


def detect_faces(detector, frame_bgr: np.ndarray):
    detector.setInputSize((frame_bgr.shape[1], frame_bgr.shape[0]))
    _, faces = detector.detect(frame_bgr)
    if faces is None:
        return []
    return [(int(f[0]), int(f[1]), int(f[2]), int(f[3])) for f in faces]  # x,y,w,h


def taint_frame(frame_bgr: np.ndarray, faces, frame_idx: int, prev_center=None,
                amplitude: float = 16.0, period: int = 24) -> np.ndarray:
    """Add periodic blue-channel perturbation inside feathered face boxes.
    Phase advances with frame index and face motion (motion-adaptive)."""
    out = frame_bgr.copy()
    h, w = frame_bgr.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    for (x, y, fw, fh) in faces:
        cx, cy = x + fw // 2, y + fh // 2
        motion = 0
        if prev_center is not None:
            motion = int(abs(cx - prev_center[0]) + abs(cy - prev_center[1]))
        phase = frame_idx + motion
        # feathered elliptical mask over the face box (expanded 10%)
        ex, ey = int(fw * 0.1), int(fh * 0.1)
        x0, y0 = max(0, x - ex), max(0, y - ey)
        x1, y1 = min(w, x + fw + ex), min(h, y + fh + ey)
        sub_yy, sub_xx = yy[y0:y1, x0:x1], xx[y0:y1, x0:x1]
        mask = (((sub_xx - cx) / max(fw / 2 + ex, 1)) ** 2 + ((sub_yy - cy) / max(fh / 2 + ey, 1)) ** 2) <= 1.0
        pattern = np.sign(np.sin(2 * np.pi * (sub_xx + sub_yy + phase) / period)) * amplitude
        blue = out[y0:y1, x0:x1, 0].astype(np.float32)
        blue[mask] = np.clip(blue[mask] + pattern[mask], 0, 255)
        out[y0:y1, x0:x1, 0] = blue.astype(np.uint8)
    return out


def protect_video(in_path: str, out_path: str, amplitude: float = 16.0, period: int = 24,
                  fallback_center: bool = False) -> dict:
    """Returns stats dict. Raises ValueError if no face in >50% of frames
    (unless fallback_center, a test/demo mode that taints the centre region)."""
    cap = cv2.VideoCapture(in_path)
    if not cap.isOpened():
        raise ValueError("could not decode video")
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    detector = make_detector(w, h)
    tmp = out_path + ".tmp.mp4"
    writer = cv2.VideoWriter(tmp, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
    idx, face_frames, prev_center = 0, 0, None
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        faces = detect_faces(detector, frame)
        if faces:
            face_frames += 1
            prev_center = (faces[0][0] + faces[0][2] // 2, faces[0][1] + faces[0][3] // 2)
        elif fallback_center:
            faces = [(w // 4, h // 4, w // 2, h // 2)]
        writer.write(taint_frame(frame, faces, idx, prev_center, amplitude, period) if faces else frame)
        idx += 1
    cap.release(); writer.release()
    if idx == 0:
        os.remove(tmp); raise ValueError("video has no frames")
    if not fallback_center and face_frames < idx * 0.5:
        os.remove(tmp)
        raise ValueError(f"face found in only {face_frames}/{idx} frames — use a clear face video (selfie-style)")
    # re-encode to broadly compatible H.264
    import subprocess
    r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", tmp, "-c:v", "libx264",
                        "-pix_fmt", "yuv420p", "-crf", "18", out_path], capture_output=True)
    os.remove(tmp)
    if r.returncode != 0:
        raise ValueError("ffmpeg re-encode failed")
    return {"frames": idx, "face_frames": face_frames, "fps": fps, "width": w, "height": h}
