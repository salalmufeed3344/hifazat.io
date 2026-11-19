export default function AwaazPage() {
  return (<>
    <h1>Awaaz Shield — Cloak your voice</h1>
    <p className="sub">Week 2 module. Status: API contract ready, worker not yet wired.</p>
    <section className="panel">
      <h2>What it will do</h2>
      <p>Upload or record a voice clip → apply Enkidu&apos;s learned universal patch (ACM MM 2025) → download a protected clip that sounds identical to humans but clones badly. Demo: clone unprotected = sounds like them; clone protected = garbled.</p>
      <p><strong>Pakistan test (Week 2, Day 1):</strong> does the patch survive a real WhatsApp voice-note round-trip (Opus compression)? Measured, not assumed.</p>
      <p>API: <code>POST /api/awaaz/protect</code> — see TRD.md §3. Returns 501 until the FastAPI worker lands.</p>
    </section>
  </>);
}
