export default function MiragePage() {
  return (<>
    <h1>MIRAGE Shield — Editors refuse</h1>
    <p className="sub">Weeks 4–5 module. Status: research replication — paper-only, no code exists yet.</p>
    <section className="panel">
      <h2>What it will do</h2>
      <p>Upload a photo → imperceptible perturbations align it to policy-violating concepts in an ensemble of open models (MIRAGE, arXiv:2606.26199, Jun 2026) → ChatGPT / Gemini&apos;s own safety moderator flags it and <strong>refuses</strong> to edit, regardless of prompt. Paper reports &gt;88% success (self-reported, no independent replication yet).</p>
      <p><strong>Why last:</strong> hardest module. GPU minutes per image, queued worker, live refusal test matrix vs GPT-Image + Gemini Flash Image, with PhotoGuard (2023) as baseline.</p>
      <p>API: <code>POST /api/mirage/protect</code> — see TRD.md §3. Returns 501 until the GPU worker lands.</p>
    </section>
  </>);
}
