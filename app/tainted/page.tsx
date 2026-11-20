'use client';
import { useState } from 'react';

export default function TaintedPage() {
  const [file, setFile] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState('');
  const [err, setErr] = useState('');

  async function onProtect() {
    if (!file) return; setBusy(true); setErr(''); setMsg('');
    try {
      const fd = new FormData(); fd.append('file', file);
      const r = await fetch('/api/tainted/protect', { method: 'POST', body: fd });
      if (!r.ok) {
        const j = await r.json().catch(() => ({}));
        throw new Error(j.error || `worker returned ${r.status}`);
      }
      const blob = await r.blob();
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob); a.download = 'tainted-protected.mp4'; a.click();
      setMsg(`Protected ✓ downloaded (face found in ${r.headers.get('X-Hifazat-Face-Frames') || '?'} of ${r.headers.get('X-Hifazat-Frames') || '?'} frames).`);
    } catch (e) { setErr(e instanceof Error ? e.message : 'failed'); }
    setBusy(false);
  }

  return (<>
    <h1>Tainted Video — Fake exposes itself</h1>
    <p className="sub">Upload a short face video (≤60s, selfie-style). Get back a video that looks normal — but a face-swap made from it shows visible stripes.</p>
    <section className="panel">
      <div className="row">
        <input type="file" accept="video/*" onChange={e => setFile(e.target.files?.[0] ?? null)} />
        <button onClick={onProtect} disabled={!file || busy}>{busy ? 'Protecting…' : 'Protect / محفوظ کریں'}</button>
      </div>
      {msg && <p className="ok">{msg}</p>}
      {err && <p className="bad">{err}</p>}
      <p><strong>Honest framing:</strong> this does not stop face-swaps — it makes them obvious. We say &quot;exposes&quot;, never &quot;blocks&quot;.</p>
      <p><strong>Measured so far:</strong> fine patterns die under WhatsApp/TikTok recompression; our low-frequency pattern (period 24) keeps 0.79 correlation after CRF32. Face-swap exposure on real faces is measured before any effectiveness claim (workers/tainted/RESULTS.md).</p>
    </section>
  </>);
}
