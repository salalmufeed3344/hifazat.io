'use client';
import { useState } from 'react';

export default function AwaazPage() {
  const [file, setFile] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState('');
  const [err, setErr] = useState('');

  async function onProtect() {
    if (!file) return; setBusy(true); setErr(''); setMsg('');
    try {
      const fd = new FormData(); fd.append('file', file);
      const r = await fetch('/api/awaaz/protect', { method: 'POST', body: fd });
      if (!r.ok) {
        const j = await r.json().catch(() => ({}));
        throw new Error(j.error || `worker returned ${r.status}`);
      }
      const blob = await r.blob();
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob); a.download = 'awaaz-protected.wav'; a.click();
      setMsg(`Protected ✓ downloaded (SNR ${r.headers.get('X-Hifazat-SNR-dB') || '?'} dB — higher = closer to original).`);
    } catch (e) { setErr(e instanceof Error ? e.message : 'failed'); }
    setBusy(false);
  }

  return (<>
    <h1>Awaaz Shield — Cloak your voice</h1>
    <p className="sub">Upload a voice clip (≤2 min). Get back a protected clip that sounds like you to humans, but clones badly.</p>
    <section className="panel">
      <div className="row">
        <input type="file" accept="audio/*" onChange={e => setFile(e.target.files?.[0] ?? null)} />
        <button onClick={onProtect} disabled={!file || busy}>{busy ? 'Protecting…' : 'Protect / محفوظ کریں'}</button>
      </div>
      {msg && <p className="ok">{msg}</p>}
      {err && <p className="bad">{err}</p>}
      <p>Method: Enkidu universal frequential perturbation (ACM MM 2025). Your audio is processed in memory and deleted with the request — never stored.</p>
      <p><strong>Measured so far:</strong> an STFT-domain patch partly survives WhatsApp Opus (correlation 0.58 @32k, 0.80 @48k — synthetic test, see workers/awaaz/RESULTS.md). Clone-failure with trained noise is measured before any protection claim is made.</p>
    </section>
  </>);
}
