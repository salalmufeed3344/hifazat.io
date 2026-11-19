"""Train the Enkidu universal noise against ECAPA speaker embeddings.

One-time (per noise version), NOT per request. Optimizes a universal
frequential perturbation so protected audio's speaker embedding moves away
from the clean embedding, with a perceptual (SNR) penalty.

Usage:
  pip install speechbrain torchaudio   # training-only deps
  python train_noise.py --audios_dir ./train_wavs --steps 40 --out universal_noise.pt

train_wavs: 16kHz mono wavs of speech (e.g. a LibriSpeech test-clean subset,
or consented samples). More speakers = more universal. The upstream Enkidu
example uses 40 samples from one speaker, steps=10-40, alpha=0.1.

Runs on CPU (slow) or CUDA if available. On a free Colab GPU this is minutes.
"""
import argparse, glob, os
import torch
import torch.nn.functional as F

from protect import add_noise, read_wav_16k, SR, N_FFT, FRAME


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audios_dir", required=True)
    ap.add_argument("--steps", type=int, default=40)
    ap.add_argument("--alpha", type=float, default=0.1)
    ap.add_argument("--noise_level", type=float, default=0.4)
    ap.add_argument("--lambda_perceptual", type=float, default=0.1)
    ap.add_argument("--out", default="universal_noise.pt")
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    args = ap.parse_args()

    from speechbrain.inference import SpeakerRecognition
    model = SpeakerRecognition.from_hparams(
        "speechbrain/spkrec-ecapa-voxceleb", run_opts={"device": args.device})

    files = sorted(glob.glob(os.path.join(args.audios_dir, "*.wav")))
    if not files:
        raise SystemExit(f"no .wav files in {args.audios_dir} (16kHz mono)")
    audios = [read_wav_16k(f).to(args.device) for f in files[:40]]
    print(f"{len(audios)} training clips on {args.device}")

    noise_real = torch.randn((1, N_FFT // 2 + 1, FRAME), requires_grad=True, device=args.device)
    noise_imag = torch.randn((1, N_FFT // 2 + 1, FRAME), requires_grad=True, device=args.device)
    opt = torch.optim.Adam([noise_real, noise_imag], lr=args.alpha, weight_decay=0.2)
    mse = torch.nn.MSELoss()

    def embed(x):
        return model.encode_batch(x.reshape(1, -1)).reshape(1, -1)

    for step in range(args.steps):
        opt.zero_grad()
        total = 0.0
        for a in audios:
            noisy = add_noise(a, noise_real, noise_imag, noise_level=args.noise_level)
            e_clean, e_noisy = embed(a), embed(noisy)
            sim = F.cosine_similarity(e_clean, e_noisy).mean()
            perceptual = ((noisy - a) ** 2).mean() / (a.pow(2).mean() + 1e-8)
            loss = (1 - mse(e_clean, e_noisy)) + args.lambda_perceptual * perceptual
            loss.backward()
            total += sim.item()
        opt.step()
        print(f"step {step}: mean cosine similarity clean-vs-protected = {total/len(audios):.4f} (lower = stronger protection)")

    torch.save({"noise_real": noise_real.detach().cpu(), "noise_imag": noise_imag.detach().cpu(),
                "noise_level": args.noise_level, "sr": SR}, args.out)
    print(f"saved {args.out}")


if __name__ == "__main__":
    main()
