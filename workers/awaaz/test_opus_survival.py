"""Week 2 Day-1 test: does an STFT-domain perturbation survive WhatsApp?

WhatsApp voice notes are Opus (~32-48 kbps mono). This script:
  1. takes a clean wav + protected wav (same length)
  2. round-trips BOTH through ffmpeg libopus at 32k (worst case) and 48k
  3. measures how much of the perturbation (protected-clean) survives:
     survival = ||pert_after|| / ||pert_before||, plus correlation.

Signal-level feasibility only. Clone-failure (ECAPA/XTTS) is a separate test
in TEST-MATRIX.md — do not claim protection from this script alone.

Usage: python test_opus_survival.py clean.wav protected.wav
"""
import subprocess, sys, tempfile, os
import torch
from protect import read_wav_16k, write_wav_16k


def opus_roundtrip(x: torch.Tensor, bitrate: str) -> torch.Tensor:
    with tempfile.TemporaryDirectory() as td:
        a, b, c = (os.path.join(td, n) for n in ("a.wav", "b.ogg", "c.wav"))
        write_wav_16k(a, x)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", a, "-c:a", "libopus", "-b:a", bitrate, "-ac", "1", b], check=True)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", b, "-ac", "1", "-ar", "16000", "-sample_fmt", "s16", c], check=True)
        return read_wav_16k(c)


def main():
    clean, prot = read_wav_16k(sys.argv[1]), read_wav_16k(sys.argv[2])
    n = min(len(clean), len(prot)); clean, prot = clean[:n], prot[:n]
    pert = prot - clean
    print(f"perturbation energy before: {pert.pow(2).mean().item():.6f}")
    for br in ("32k", "48k"):
        c2, p2 = opus_roundtrip(clean, br), opus_roundtrip(prot, br)
        m = min(len(c2), len(p2), n)
        pert2 = p2[:m] - c2[:m]
        survival = (pert2.pow(2).mean() / (pert[:m].pow(2).mean() + 1e-12)).sqrt().item()
        corr = torch.corrcoef(torch.stack([pert[:m], pert2]))[0, 1].item()
        print(f"opus {br}: survival={survival:.3f}  correlation={corr:.3f}  "
              f"({'patch largely survives' if survival > 0.5 else 'patch mostly stripped — retrain with opus augmentation'})")


if __name__ == "__main__":
    main()
