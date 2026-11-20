"""Tests for taint_frame (run: python test_taint.py). No face photo needed:
perturbation is tested with an explicit face box."""
import numpy as np
from protect import taint_frame


def test_blue_only_inside_face():
    frame = np.full((200, 200, 3), 128, dtype=np.uint8)
    out = taint_frame(frame, [(50, 50, 100, 100)], frame_idx=0, amplitude=10)
    assert np.array_equal(out[:, :, 1], frame[:, :, 1]), "green untouched"
    assert np.array_equal(out[:, :, 2], frame[:, :, 2]), "red untouched"
    assert not np.array_equal(out[:, :, 0], frame[:, :, 0]), "blue changed"
    # outside the face ellipse (corner) blue must be untouched
    assert out[0, 0, 0] == 128 and out[199, 199, 0] == 128, "outside face untouched"
    diff = np.abs(out[:, :, 0].astype(int) - 128)
    assert diff.max() <= 10, f"amplitude bounded, got {diff.max()}"
    print(f"ok: blue-only, inside-face, max delta {diff.max()}")


def test_phase_advances():
    frame = np.full((200, 200, 3), 128, dtype=np.uint8)
    a = taint_frame(frame, [(50, 50, 100, 100)], frame_idx=0, amplitude=10)
    b = taint_frame(frame, [(50, 50, 100, 100)], frame_idx=1, amplitude=10)
    assert not np.array_equal(a, b), "pattern changes per frame (motion-adaptive phase)"
    print("ok: phase advances per frame")


def test_no_faces_no_change():
    frame = np.full((100, 100, 3), 90, dtype=np.uint8)
    assert np.array_equal(taint_frame(frame, [], 0), frame)
    print("ok: no faces -> unchanged")


if __name__ == "__main__":
    test_blue_only_inside_face(); test_phase_advances(); test_no_faces_no_change()
    print("all taint tests passed")
