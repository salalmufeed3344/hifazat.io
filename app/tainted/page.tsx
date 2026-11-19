export default function TaintedPage() {
  return (<>
    <h1>Tainted Video — Fake exposes itself</h1>
    <p className="sub">Week 3 module. Status: API contract ready, worker not yet wired.</p>
    <section className="panel">
      <h2>What it will do</h2>
      <p>Upload a short face video → embed blue-channel periodic perturbations in facial regions, motion-adaptive per frame (TaintedPixels, Aug 2026) → download a video that looks normal, but any face-swap shows visible stripes.</p>
      <p><strong>Honest framing:</strong> does not stop the fake — makes it obvious. We say &quot;exposes&quot;, never &quot;blocks&quot;.</p>
      <p>API: <code>POST /api/tainted/protect</code> — see TRD.md §3. Returns 501 until the CPU worker lands.</p>
    </section>
  </>);
}
