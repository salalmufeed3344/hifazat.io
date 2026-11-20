# Hifazat — How AI Face-Swap, Voice Cloning & AI Editing Actually Work, and Where Invisible Defenses Can Break Them

**Defensive research synthesis, 20 Nov 2026.** Four parallel tracks (face-swap internals, voice cloning internals, inpainting/editor internals, invisible defenses 2024–2026), primary papers/repos read directly. **[SR]** = self-reported by the defense authors. **[IV]** = independently verified / reproduced by a different team / peer-reviewed attack paper. Architecture level only.

**Direction (Salal, 20 Nov 2026):** protection eyes cannot catch, with big impact on AI models. Visible-lines approaches are rejected as product direction (kept only as measured baseline). Learn first, pick ONE starting point, build step by step. No rushing.

**The one-sentence answer:** invisible protection is real physics — perturbations at LPIPS ≤0.05 / PSNR ≥35 dB / ε ≤8/255 are genuinely hard for eyes to catch — but *no* current defense at that budget has independently verified protection that survives JPEG + WhatsApp resize + purification. The field's honest state, in the words of 2026 reviews: "first generation broken, second generation unproven, removal improving" [https://poisoning.ai/articles/do-ai-poisoning-tools-actually-work/]. What follows is where the real openings are.

---

## A. The three pipelines, step by step

### A1. Face-swap (Roop / FaceFusion / inswapper_128 / InsightFace)

```
Source photo ──► [1 DETECT] ──► [2 ALIGN] ──► [3 EMBED IDENTITY] ──┐
                 SCRFD/YuNet     5 landmarks   ArcFace 512-D         │
                 640×640         112×112 crop  L2-normalized         ▼
Target video ──► [1 DETECT per frame] ──► [2 ALIGN 128×128] ──► [4 SWAP]
                                                        inswapper_128 (StyleGAN2-style,
                                                        AdaIN conditioning)
                                                              │
                              [5 PASTE BACK + MASK] ◄─────────┘
                              inverse warp, soft mask
                                      │
                              [6 ENHANCE] GFPGAN / CodeFormer (generative prior)
                                      │
                              [7 TEMPORAL] reference-face tracking, frame blending
```

Key facts:
- **Detection is a hard gate** — "roop can't swap a face it hasn't found" [https://vectree.io/pdf/c/roop]. Default stack is InsightFace `buffalo_l`: SCRFD-10GF detection (not RetinaFace anymore) + ResNet50@WebFace600K recognition [https://github.com/deepinsight/insightface/blob/HEAD/python-package/docs/model_zoo.md] **[IV, primary source]**.
- **Alignment** warps the face to a canonical template from just 5 points (2 eyes, nose, 2 mouth corners). ArcFace crop 112×112, inswapper crop 128×128.
- **Identity embedding:** ArcFace, **512-D, L2-normalized**, trained with angular margin s=64, m=0.5 rad. Cosine similarity thresholds are *deployment choices*, not universal: 0.25–0.70 across real systems (0.30 ID verification, ~0.45 District Seal, ~0.66 in one ONNX evaluation) [https://kahma.io/blog/choosing-an-arcface-verifier-thresholds-030-and-035.php ; https://mixpeek.com/docs/processing/extractors/face-identity]. A defense must displace the embedding *far*, not just cross one threshold.
- **Swap:** inswapper_128 takes the aligned target crop + source 512-D vector, outputs source identity with target pose/expression. Native 128×128 = soft/waxy, hence the enhancer. No peer-reviewed architecture paper exists for inswapper itself — treat as black-box conditioned generator. Models are non-commercial research licence [https://github.com/deepinsight/insightface/blob/HEAD/python-package/docs/model_zoo.md].
- **Enhancers (GFPGAN/CodeFormer) are generative priors** trained on degraded faces — they *heal* small perturbations. CodeFormer's discrete codebook additionally quantizes noise away. This is why raw pixel noise dies downstream.
- **Video:** inswapper has no temporal awareness; flicker is handled post-hoc (tracking + blending).

### A2. Voice cloning (XTTS / OpenVoice / CosyVoice / ElevenLabs-style)

```
Reference audio ──► [1 SPEAKER ENCODER] ──► speaker embedding / conditioning latents
                    ECAPA-TDNN 192-D / CAM++ / d-vector 512-D / XTTS 32×1024 latents
Text ─────────────► [2 ACOUSTIC/TOKEN MODEL] (AR transformer or flow-matching, conditioned on [1])
                    ──► mel-spectrogram or discrete speech tokens
                    ──► [3 TOKEN→MEL DECODER] (flow matching, ~10 ODE steps)
                    ──► [4 VOCODER] HiFi-GAN family ──► waveform 22.05–24 kHz
```

Key facts:
- **Two different attacker workflows:** (1) *zero-shot* — your published clip is a reference prompt at inference; (2) *fine-tuning* — attacker trains on your audio (30 min–3 h for ElevenLabs PVC). A defense for one does not automatically work for the other. This split organizes the whole literature.
- **"3 seconds"** originates from Microsoft VALL-E (2023) [https://arxiv.org/pdf/2301.02111] **[SR]**. In practice: XTTS-v2 sweet spot 10–30 s, ElevenLabs IVC recommends 1–2 min. 3 s captures timbre roughly; quality/consistency need more. Cleanliness beats length.
- **Speaker embedding is the primary attack surface** for zero-shot. The vocoder is *not* reachable by a publisher-side defense.
- Encoders differ per system (ECAPA 192-D, OpenVoice SE 256-D, CosyVoice CAM++ 192-D, XTTS 32×1024 latents + 512-D d-vector) — a defense tuned to one encoder may not transfer. ElevenLabs' architecture is undisclosed [https://tts.wiki/index.php?title=ElevenLabs&diff=54].

### A3. AI image editing / inpainting (SD 1.5 / SDXL / Flux / ChatGPT-4o / Gemini)

```
Photo ──► [VAE ENCODER] ──► latent 64×64×4 (48× compressed)
Mask + prompt ──► [TEXT ENCODER CLIP/T5] ──► token embeddings
                              │
                    [DENOISER: U-Net (SD1.5/SDXL) or DiT (Flux/SD3)]
                    inpainting U-Net reads 9 channels: noisy latent(4)+mask(1)+masked latent(4)
                    iterative denoising (~20+ steps), cross-attention to text
                              │
                    [VAE DECODER] ──► edited pixels
Identity add-ons: IP-Adapter (CLIP image → decoupled cross-attention, 22M params),
InstantID (face-recognition embedding + IdentityNet), PhotoMaker (stacked ID embedding),
ControlNet (spatial conditioning via zero-convolutions), Flux Kontext (reference image
as latent tokens, joint attention — no mask channel at all)
```

Key facts:
- **2025–2026 commercial editors changed architecture:** GPT-4o image is autoregressive (OpenAI system card: "unlike DALL·E, which operates as a diffusion model, 4o image generation is an autoregressive model") [https://cdn.openai.com/11998be9-5319-4302-bfbf-1167e093f1fb/Native_Image_Generation_System_Card.pdf?ref=blog.cansincengiz.me]; Gemini Flash Image generates 1,290 tokens autoregressively [https://simonwillison.net/2025/Nov/13/nano-banana-can-be-prompt-engineered/]. There is no SD-style VAE+U-Net gradient path to attack in these closed models.
- **March 2026 independent study (Zhao et al., arXiv:2603.13028):** ChatGPT-4o, Gemini Pro, Qwen-Image, Seedream, Step1X-Edit edited PhotoGuard-protected photos "with quality comparable to clean ones"; plain JPEG or the EditorClean purifier partly restores editing [https://arxiv.org/pdf/2603.13028 ; https://untrainable.org/en/tools/photoguard/] **[IV, preprint]**.

---

## B. Ranked invisible-defense attack surfaces

**Fragility ranking for face-swap** (most → least fragile): **Detection > Alignment > ArcFace embedding > Swap generator > Enhancer.**

1. **Face detection (hard gate, cascade failure).** FacePoison (arXiv:2412.01101) fools 5 detectors / 11 DeepFake models with imperceptible perturbations **[SR]** [https://arxiv.org/pdf/2412.01101]. Physical LED attack: 100% DoS vs RetinaFace **[SR]** [https://www.computer.org/csdl/journal/bd/2025/02/10535230/1X6biQUu2AM]. *Caveat:* FaceFusion-class stacks chain fallbacks (SCRFD→YOLO→YuNet→Haar), so single-detector defenses can be bypassed.
2. **Alignment / landmarks (geometric amplifier).** 5 points define the whole warp. Landmark Shift Attack (arXiv:2508.00620, 2025) proves the landmark head is independently attackable **[SR, backdoor threat model]** [https://arxiv.org/pdf/2508.00620].
3. **Identity embedding (ArcFace / ECAPA / FaceNet+CLIP).** The workhorse surface. Fawkes: 95%+ protection vs recognition **[SR]** [https://arxiv.org/pdf/2002.08327]. *Critical catch from Phantom (CVPR 2026):* generic FR perturbations often fail against face-swap because the generator's identity–style disentanglement suppresses them; identity-direction-aware perturbations improve protection +27.8% (UniFace), +25.6% (INSwapper), +16.6% (SimSwap) **[SR]** [https://arxiv.org/html/2606.31703].
4. **Safety moderator (commercial APIs only).** MIRAGE: align image to policy-violating concepts in an open CLIP ensemble → the API's own moderator refuses, prompt-agnostic. >88% on GPT-Image/Gemini/Grok at ε=16/255 **[SR, live APIs, no independent replication]** [https://arxiv.org/html/2606.26199v2]. Collapses to 12.5% under strong adaptive CLIP-undo attack; local open-weight editing bypasses moderators entirely.
5. **VAE encoder / diffusion trajectory (SD1.5-era).** PhotoGuard's surface. Independently broken by JPEG Q95–75 [http://arxiv.org:443/abs/2304.02234], purification, and model mismatch. Still disrupts matched SD1.5 pipelines only.
6. **Training objective (voice fine-tuning).** SafeSpeech/SPEC error-minimizing noise: fine-tuned model learns the noise shortcut, synthesis collapses (WER 24%→99.6%, SIM 0.604→0.204 at ε=8/255) **[SR]** [https://arxiv.org/html/2504.09839v1/], and RVCBench independently ranks SPEC ≥ SafeSpeech > Enkidu > POP in zero-shot mode **[IV]** [https://arxiv.org/abs/2602.00443].
7. **Audio-visual alignment (talking-head).** MUTE (NeurIPS 2026, arXiv:2611.11989): perturb audio only (‖δ‖∞ ≤0.004, 200 PGD steps, STFT high-energy constraint) to uncouple cross-modal attention + temporal embeddings; SyncNet 1.332 (TalkingHead-1KH) **[SR]**, code public [https://arxiv.org/abs/2611.11989]. Heavy compute per sample; 50 clips/dataset only.
8. **Attention inversion (DiT editors).** Copying-as-Defense: *maximize* target→reference attention in Flux Kontext early blocks → editing collapses into copying. Edit success 81.4%→24.0%, BodyBench 5.1% at ε=12/255 **[SR]** [https://arxiv.org/html/2610.35566v1]. Zero compression/purification evaluation.

**What breaks defenses (the other side):** noisy upscaling (Hönig ICLR 2025: Glaze/Anti-DreamBooth 56.6%, Mist 62.0% mimicry success — all above the 50% "indistinguishable" line) **[IV]**; IMPRESS purification (Glaze classifier 42.5%→87.0%) **[IV]** [https://arxiv.org/pdf/2310.19248]; LightShed depoisoning (Nightshade detection 99.98% TPR) **[IV, USENIX 2025]**; EditorClean purification (+3–6 dB PSNR, −50–70% FID across 6 defenses) **[IV]** [https://arxiv.org/pdf/2603.13028]; Fragile by Design (Chen et al.: *none* of Anti-DreamBooth/HF-ADB/SimAC/DisDiff retains protection after DiffPure; ISM restored 0.40→0.61 vs clean 0.69) **[IV]** [https://arxiv.org/pdf/2511.10382]; De-AntiFake/PhonePuRe and VocalBridge for audio (purification recovers 23–45% of cloneability) **[attack papers]** [https://arxiv.org/html/2507.02606v1 ; https://arxiv.org/html/2601.02444v1].

**Imperceptibility budget synthesis:** target **LPIPS ≤0.05, PSNR ≥35 dB, SSIM ≥0.97, ε ≤8/255** for faces. ε=16/255 (the benchmark standard) measures LPIPS 0.13–0.36 / PSNR 26–32 dB independently — often visible on faces. ε=8/255 → PSNR ~32–33 dB (IDGuardian 32.19 **[SR]**) — mostly invisible on textured content, faint on faces. ε=4/255 → genuinely hard to see but protection weak. TaintedPixels' LPIPS 0.0042 with 3.26% human suspicion **[SR]** shows true invisibility is possible only with highly restricted perturbation structure (blue channel + textured regions + video averaging).

---

## C. Per-guard-paper extraction

| Guard | Threat model | Budget | What it breaks | What breaks it | Code / licence |
|---|---|---|---|---|---|
| **PhotoGuard** (arXiv:2302.06588) | SD1.5 inpainting, white-box | ε=16/255 benchmarks; PSNR 28–32, LPIPS 0.13–0.34 [IV] | VAE latent / diffusion trajectory | JPEG Q≤85, purification, DiT/AR editors [IV] | github.com/MadryLab/photoguard; repo stale since Feb 2023 |
| **Glaze** | Style mimicry (fine-tuning) | LPIPS p=0.05 [SR]; re-measured PSNR 31.38, SSIM 0.99 [IV] | Style feature space | Noisy upscaling 56.6% [IV], IMPRESS 87% [IV] | Closed tool (UChicago SAND Lab) |
| **Nightshade** | Training-data poisoning | LPIPS p=0.07 [SR] | Concept binding in training | LightShed detection 99.98% TPR + depoison [IV] | Closed tool |
| **Mist** | Style mimicry | ε=17/255 [SR]; PSNR 26–28, LPIPS 0.26–0.36 [IV] | Diffusion training | Upscaling 62% [IV], purification | Research code |
| **Anti-DreamBooth** | Identity fine-tuning (DreamBooth) | ~11/255 [SR] | DreamBooth identity learning | DiffPure/filtering restore ISM [IV Fragile by Design] | Research code |
| **IDGuardian** (arXiv:2610.19717) | One-photo identity theft (IP-Adapter/InstantID/PhotoMaker/DreamBooth) | ε=8/255; PSNR 32.19, SSIM 0.842 [SR] | FaceNet+CLIP extraction + diffusion guidance | Untested vs DiffPure/LightShed/upscaling; JPEG Q unspecified | github.com/OpenAscent-L/IDGuardian (MIT per prior research) |
| **BlurGuard** (NeurIPS 2025) | Robustifier for any protective noise | ε=16/255 (also 8, 4); PSNR 31.1, LPIPS 0.21 [SR] | Frequency spectrum gap (makes noise irreversible) | No independent bypass/confirmation; failed transfer to commercial APIs in MIRAGE test | Paper + code referenced |
| **MIRAGE** (arXiv:2606.26199) | Commercial API editing (GPT-Image/Gemini/Grok) | ‖δ‖∞ ≤16/255, 5000 PGD steps + EOT [SR] | Pre-generation safety moderator → refusal | CLIP-undo →12.5%; local editing bypass; API drift | **No code/tool** (paper only) |
| **Copying-as-Defense** (arXiv:2610.35566) | DiT editors (Flux Kontext/FIBO) | ε=12/255 main; PSNR 28.7–29.8, LPIPS 0.31–0.39 [SR] | Target→reference attention (forces copying) | Compression/purification **not evaluated** | Paper only |
| **RAPID** (NUST SEECS, Jul 2026) | Instruction-guided diffusion editing | Amortized: Restormer predicts perturbation in 1 forward pass, ~0.10 s/image, 100× faster [SR] | VAE bottleneck semantic info (grey-box training, gradient-free inference) | Same VAE-surface fragility class as PhotoGuard; no independent JPEG/purification test found | github.com/dll-ncai/RAPID-Restorative-Amortized-Protection-for-ImageDiffusion (code+models public) [https://dll.seecs.nust.edu.pk/wp-content/uploads/2026/07/RAPID-Restorative-Amortative-Protection-for-Image-Diffusion.pdf] |
| **Enkidu** (arXiv:2507.12932) | Zero-shot voice cloning | Noise level η=0.4; MOS 3.01, STOI 0.71 [SR] | Speaker embedding (universal STFT patch) | RVCBench: weakest of 3 modern [IV]; Opus round-trip untested in paper | github.com/NoobCodeNameless/Enkidu (**no licence file**) |
| **SafeSpeech/SPEC** (USENIX 2025) | Voice fine-tuning (+zero-shot transfer) | ε=8/255; SIM 0.604→0.204, WER→99.6% [SR] | Training objective (error-minimizing noise) + speaker concealment | VocalBridge partial strip (ARR 28.9%) [attack paper] | github.com/wxzyd123/SafeSpeech |
| **AntiFake** (CCS 2023) | Zero-shot cloning incl. black-box ElevenLabs | Psychoacoustic-masked; SNR ~12.8–13.3 dB [IV re-measure] | Speaker embedding deviation | De-AntiFake purification [IV]; RTC 28× slow | Research code |
| **MUTE** (arXiv:2611.11989) | Talking-head generation (audio→lip-sync) | ‖δ‖∞ ≤0.004, 200 PGD steps [SR] | Cross-modal attention + temporal audio embeddings | Heavy compute; small eval (50 clips/dataset) | github.com/jindl465/MUTE |
| **TaintedPixels** (arXiv:2608.27492) | Face-swap forgery (expose, not block) | LPIPS 0.0042 [SR] | Forgery *credibility* (human spotting 90.72% vs 56.71%) | Adaptive forgers untested; authors don't claim block | No code found |
| **FacePoison** (arXiv:2412.01101) | DeepFake training + inference | Imperceptible (paper budgets) | Face *detection* (5 detectors, 11 DeepFake models) [SR] | Fallback detector chains | github.com/OUC-VAS/FacePoison (per paper) |
| **Phantom** (CVPR 2026) | Face-swap (INSwapper/SimSwap/UniFace) | Latent+spatial constrained [SR] | Identity direction in embedding + spatial regions | — (newest; no independent bypass yet) | Paper (arXiv:2606.31703) |

**Failure papers (read as primary):** Hönig et al. ICLR 2025 (upscaling breaks Glaze/Mist/Anti-DreamBooth) [IV]; LightShed USENIX Security 2025 (99.98% Nightshade detection + depoison) [IV]; Zhao et al. arXiv:2603.13028 (EditorClean purifies 6 defenses; commercial AR editors edit protected photos fine) [IV preprint]; Chen et al. arXiv:2511.10382 (no defense survives purification; visible stripe artifacts) [IV]; De-AntiFake ICML 2025 + VocalBridge 2026 for audio [attack papers].

---

## D. What a solo builder in Pakistan can realistically reproduce/test locally

**Fully local on CPU (no GPU, no API cost):**
- InsightFace `buffalo_l` ONNX (SCRFD + ArcFace ResNet50) via ONNX Runtime — detection + 512-D embedding + cosine measurement. This is the measurement backbone for everything face-related.
- YuNet (228 KB ONNX) face detection — already in the Hifazat repo.
- PGD optimization against ArcFace (and CLIP ViT) with PyTorch CPU — minutes per image at ε=8/255, 200 steps. IDGuardian's recipe (FaceNet+CLIP cosine minimization) is directly implementable from the paper; code is public.
- JPEG/WhatsApp simulation: PIL JPEG Q50–95 + resize ≤1600px + Opus/CRF round-trips via ffmpeg — already built in Hifazat workers.
- LPIPS/PSNR/SSIM measurement (torchmetrics / lpips package, CPU-ok).

**Small GPU / Colab free tier:**
- inswapper_128 swap test (ONNX, ~4 GB VRAM) + GFPGAN enhancer pass — the honest end-to-end test: protect → swap → enhance → measure identity similarity of output.
- SD 1.5 inpainting (diffusers) for PhotoGuard/RAPID reproduction; RAPID's pretrained models are public.
- ECAPA-TDNN (SpeechBrain) embedding measurement + XTTS-v2 / CosyVoice 2 zero-shot clone tests for voice (CPU-slow, GPU-comfortable).
- SafeSpeech training (BERT-VITS2 surrogate) — heavier; Colab.

**Not realistically reproducible solo:** MIRAGE at scale (5000 PGD steps × 8-model ensemble + live commercial API evaluation at >$50/image black-box alternative), MUTE (200 PGD steps with full diffusion forwards per sample), Copying-as-Defense (white-box Flux Kontext backprop, 12B model), Nightshade/Glaze (closed tools).

---

## E. Open questions

1. **Detector transferability:** does one perturbation fool SCRFD + YOLO-face + YuNet + Haar fallbacks simultaneously? FacePoison tested 5 detectors; nobody has published the FaceFusion fallback-chain test.
2. **Enhancer survival:** does *any* ε≤8/255 perturbation survive a GFPGAN/CodeFormer pass with identity still disrupted? Phantom suggests identity-direction-aware + spatially confined helps; no independent measurement exists.
3. **WhatsApp reality:** no defense paper has published an actual WhatsApp-send test (resize + proprietary encoder). All "platform" numbers are lab JPEG/CRF proxies.
4. **AR-editor surface:** for autoregressive editors (GPT-4o/Gemini), is there *any* input-side surface besides the moderator? Tokenizer-level attacks are unexplored in public literature.
5. **Voice codec gap:** no headline defense (AntiFake/Enkidu/SafeSpeech) publishes Opus 16–32 kbps round-trip survival of the protected reference. CodecAttack's lesson (concentrate energy <4 kHz) is unapplied to voice protection.
6. **Visibility ground truth:** PSNR/LPIPS thresholds vs real human side-by-side detection on Pakistani faces/skin tones — unmeasured. TaintedPixels' human-study protocol is the template.

---

## F. Recommendation: ONE starting point

**Start with ONE module, ONE surface: invisible ArcFace identity-embedding disruption for photos (the IDGuardian extraction arm, simplified Phantom-style).**

Why this one:
- It is the only surface that is (a) invisible-budget compatible (ε=8/255, PSNR ~32 dB), (b) testable end-to-end *locally on CPU* with open ONNX models, (c) relevant to *both* face-swap (inswapper consumes ArcFace vectors) and one-photo identity theft (InstantID/PhotoMaker consume face-recognition embeddings), and (d) measurable with a single honest number: cosine similarity before/after, plus swap-output identity similarity.
- Detection disruption is simpler but dies to fallback chains. MIRAGE is the strongest *claimed* commercial defense but is paper-only, API-fragile, and unreproducible solo. VAE attacks are independently broken. Voice needs training data + heavier compute before any result.

**Step-by-step reproduction path:**
1. **Baseline harness (week 1):** buffalo_l ONNX → detect/align/embed any photo; record ArcFace cosine between two photos of same person vs different. Success = harness reproduces published genuine/impostor separation.
2. **Perturbation v1 (week 2):** PGD (200 steps, ε=8/255, α=0.005) minimizing cosine(FaceNet/ArcFace(x+δ), ArcFace(x)) + cosine(CLIP(x+δ), CLIP(x)) — IDGuardian's dual-encoder loss, face-region masked. Measure: cosine displacement, PSNR/LPIPS/SSIM.
3. **Robustness (week 3):** EOT loop — JPEG Q50–95, resize 0.5–1.0, slight crop inside the optimization. Re-measure displacement after WhatsApp simulation (resize ≤1600 + JPEG Q~70).
4. **End-to-end honesty test (week 4):** run inswapper_128 with protected source → measure output identity similarity vs clean-source swap; then GFPGAN pass → re-measure. This is the number that decides if the module is real.
5. **Visibility test:** side-by-side human check (even 5–10 people) at the chosen budget, TaintedPixels-style. If eyes catch it, lower ε and accept weaker displacement — document the trade-off curve, don't hide it.

Kill criteria (per Salal's termination rule): if after EOT + enhancer pass the swap-output identity similarity returns to clean levels at ε≤8/255, terminate this surface and move to detection+alignment joint disruption. No shipping on hope.

**What stays parked:** MIRAGE replication (needs API budget + ensemble), MUTE, Copying-as-Defense, voice training (Colab, separate track), visible Tainted (baseline only, already in repo).

---

*Sources: full URL lists are embedded inline above per claim. Key primaries: PhotoGuard arXiv:2302.06588; MIRAGE https://arxiv.org/html/2606.26199v2; IDGuardian https://arxiv.org/html/2610.19717v1; Enkidu https://arxiv.org/html/2507.12932v2; SafeSpeech https://arxiv.org/html/2504.09839v1/; AntiFake https://cybersecurity.seas.wustl.edu/paper/AntiFakeCCS23.pdf; TaintedPixels https://arxiv.org/abs/2608.27492; MUTE https://arxiv.org/abs/2611.11989; Copying-as-Defense https://arxiv.org/html/2610.35566v1; RAPID https://dll.seecs.nust.edu.pk/wp-content/uploads/2026/07/RAPID-Restorative-Amortized-Protection-for-Image-Diffusion.pdf; failures: Hönig ICLR 2025 via https://poisoning.ai/articles/does-glaze-actually-work/, LightShed via https://poisoning.ai/articles/can-glaze-nightshade-be-bypassed/, Zhao https://arxiv.org/pdf/2603.13028, Chen https://arxiv.org/pdf/2511.10382, De-AntiFake https://arxiv.org/html/2507.02606v1, RVCBench https://arxiv.org/abs/2602.00443, Phantom https://arxiv.org/html/2606.31703, FacePoison https://arxiv.org/pdf/2412.01101.*
