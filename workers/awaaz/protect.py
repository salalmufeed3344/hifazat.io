"""Awaaz Shield — Enkidu-method voice protection (serving path).

Method from: Enkidu, ACM MM 2025 (arXiv:2507.12932) — universal frequential
perturbation: STFT the waveform, add a learned universal noise (real+imag)
tiled over 30-frame patches, Wiener-smooth, iSTFT back. Implemented here
from the paper's described method; the upstream repo ships no licence file,
so no upstream code is vendored.

The universal noise itself is NOT random: it must be trained against a
speaker-embedding model (see train_noise.py). Without a trained
universal_noise.pt this module refuses to protect — random noise would be
fake protection.
"""
import wave
import numpy as np
import torch

SR = 16000
N_FFT, HOP, WIN, FRAME = 1024, 512, 1024, 30


def read_wav_16k(path: str) -> torch.Tensor:
    """Read a 16-bit PCM wav, mono-mix, return float tensor [N] at file rate.
    Caller resamples to 16k with ffmpeg before calling (see app.py)."""
    with wave.open(path, "rb") as w:
        n, ch, sw = w.getnframes(), w.getnchannels(), w.getsampwidth()
        raw = w.readframes(n)
    if sw != 2:
        raise ValueError("only 16-bit PCM wav supported")
    x = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    if ch > 1:
        x = x.reshape(-1, ch).mean(axis=1)
    return torch.from_numpy(x.copy())


def write_wav_16k(path: str, x: torch.Tensor) -> None:
    pcm = (x.detach().cpu().clamp(-1, 1).numpy() * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def _wiener_smooth(stft: torch.Tensor, est_frames: int = 10, eps: float = 1e-8) -> torch.Tensor:
    mag, phase = stft.abs(), stft.angle()
    noise_mag = mag[..., :est_frames].mean(dim=-1, keepdim=True).expand_as(mag)
    gain = mag**2 / (mag**2 + noise_mag**2 + eps)
    enh = gain * mag
    return torch.complex(enh * torch.cos(phase), enh * torch.sin(phase))


def add_noise(waveform: torch.Tensor, noise_real: torch.Tensor, noise_imag: torch.Tensor,
              noise_level: float = 0.4, smooth: bool = True) -> torch.Tensor:
    """waveform [N] float at 16k -> protected [N]. noise_*: [1, 513, FRAME]."""
    x = waveform.flatten().float()
    window = torch.hann_window(N_FFT)
    stft = torch.stft(x, N_FFT, HOP, WIN, window=window, return_complex=True).unsqueeze(0)
    real, imag = stft.real.clone(), stft.imag.clone()
    frames = stft.size(2)
    if FRAME >= frames:
        real[:, :, :frames] += noise_real[:, :, :frames] * noise_level
        imag[:, :, :frames] += noise_imag[:, :, :frames] * noise_level
    else:
        for start in range(0, frames - FRAME + 1, FRAME):
            real[:, :, start:start + FRAME] += noise_real * noise_level
            imag[:, :, start:start + FRAME] += noise_imag * noise_level
    noisy = torch.complex(real, imag)
    if smooth:
        noisy = _wiener_smooth(noisy)
    out = torch.istft(noisy, N_FFT, HOP, WIN, window=window, length=x.size(-1))
    return out.flatten()[:x.size(-1)].clamp(-1.0, 1.0)


def snr_db(clean: torch.Tensor, noisy: torch.Tensor) -> float:
    diff = (noisy - clean).pow(2).mean()
    sig = clean.pow(2).mean()
    return float(10 * torch.log10(sig / (diff + 1e-12)))
