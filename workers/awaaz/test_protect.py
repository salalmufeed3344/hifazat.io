"""Unit tests for protect.py (run: python -m pytest test_protect.py -q, or python test_protect.py)."""
import torch
from protect import add_noise, snr_db, N_FFT, FRAME


def test_noise():
    g = torch.Generator().manual_seed(0)
    return (torch.randn((1, N_FFT // 2 + 1, FRAME), generator=g),
            torch.randn((1, N_FFT // 2 + 1, FRAME), generator=g))


def test_add_noise_changes_but_preserves():
    torch.manual_seed(0)
    x = torch.randn(16000 * 3) * 0.3  # 3s synthetic
    nr, ni = test_noise()
    y = add_noise(x, nr, ni, noise_level=0.4)
    assert y.shape == x.shape, "length preserved"
    assert y.abs().max() <= 1.0, "clamped to [-1,1]"
    assert not torch.allclose(x, y), "waveform actually changed"
    s = snr_db(x, y)
    assert -5 < s < 60, f"SNR sane, got {s:.1f} dB"
    print(f"ok: shape preserved, changed, SNR={s:.1f} dB")


def test_short_clip():
    x = torch.randn(8000) * 0.3  # 0.5s, shorter than one patch span
    nr, ni = test_noise()
    y = add_noise(x, nr, ni)
    assert y.shape == x.shape
    print("ok: short clip")


if __name__ == "__main__":
    test_add_noise_changes_but_preserves()
    test_short_clip()
    print("all protect tests passed")
