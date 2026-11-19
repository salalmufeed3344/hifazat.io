# Awaaz Worker — voice cloak (Enkidu method)

Protects a voice clip so a clone comes out garbled, while humans hear it fine.
Method: Enkidu (ACM MM 2025, arXiv:2507.12932) universal frequential perturbation.

## Honest status

- Serving code (`protect.py`, `app.py`) is real and tested.
- **Protection quality depends entirely on a trained `universal_noise.pt`.**
  The worker refuses to protect (503) until one exists — random noise would be fake protection.
- Training needs ECAPA speaker embeddings (SpeechBrain) + speech samples.
  Best run on a free Colab GPU; CPU works but is slow.

## 1. Train the universal noise (one-time)

```bash
pip install torch torchaudio speechbrain==1.0.0 numpy
mkdir train_wavs   # put 16kHz mono speech wavs here (e.g. LibriSpeech test-clean subset)
python train_noise.py --audios_dir ./train_wavs --steps 40 --out universal_noise.pt
```

Watch the printed cosine similarity: clean-vs-protected should drop well below 1.0.

## 2. Serve

```bash
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8001
curl localhost:8001/health
curl -F file=@voice.ogg localhost:8001/protect -o awaaz-protected.wav
```

Audio is decoded with ffmpeg (wav/mp3/ogg/m4a, ≤2 min, ≤10 MB), processed in a
temp dir, deleted with the request. Nothing is stored or logged (Cordum: DENY retention).

## 3. WhatsApp survival test (Week 2 Day 1)

```bash
python test_opus_survival.py clean.wav awaaz-protected.wav
```

Round-trips both through Opus 32k/48k (WhatsApp voice-note range) and reports
how much of the perturbation survives. Signal-level only — clone-failure is
measured separately (ECAPA similarity + XTTS clone, see TEST-MATRIX.md).

## Tests

```bash
python test_protect.py
```
