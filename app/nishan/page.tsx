'use client';
import { useEffect, useState } from 'react';
import { loadRecords, registerPhoto, verifyPhoto, type NishanRecord, type VerifyResult } from '@/lib/nishan';

export default function NishanPage() {
  const [records, setRecords] = useState<NishanRecord[]>([]);
  const [regFile, setRegFile] = useState<File | null>(null);
  const [verFile, setVerFile] = useState<File | null>(null);
  const [regMsg, setRegMsg] = useState('');
  const [ver, setVer] = useState<VerifyResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => { setRecords(loadRecords()); }, []);

  async function onRegister() {
    if (!regFile) return; setBusy(true); setError('');
    try { const rec = await registerPhoto(regFile); setRecords(loadRecords()); setRegMsg(`Registered ✓ ${rec.id} — post your photo now.`); }
    catch { setError('Could not read that image. Try a JPG/PNG photo.'); }
    setBusy(false);
  }
  async function onVerify() {
    if (!verFile) return; setBusy(true); setError(''); setVer(null);
    try { setVer(await verifyPhoto(verFile)); }
    catch { setError('Could not read that image. Try a JPG/PNG photo.'); }
    setBusy(false);
  }
  function exportBackup() {
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([JSON.stringify(loadRecords(), null, 2)], { type: 'application/json' }));
    a.download = 'hifazat-nishan-backup.json'; a.click();
  }

  return (
    <>
      <h1>Nishan — Prove the original</h1>
      <p className="sub">Private by design: your photo never leaves this device. No upload, no server, no account.</p>

      <section className="panel">
        <h2>1 · Register before posting</h2>
        <p>Choose the original photo. Nishan computes SHA-256 + perceptual hash on this device and stores only hashes + time.</p>
        <div className="row">
          <input type="file" accept="image/*" onChange={e => setRegFile(e.target.files?.[0] ?? null)} />
          <button onClick={onRegister} disabled={!regFile || busy}>Register / درج کریں</button>
        </div>
        {regMsg && <p className="ok">{regMsg}</p>}
      </section>

      <section className="panel">
        <h2>2 · Verify a circulating photo</h2>
        <p>Upload the suspected fake. WhatsApp forwarding changes the file, but the perceptual hash usually survives.</p>
        <div className="row">
          <input type="file" accept="image/*" onChange={e => setVerFile(e.target.files?.[0] ?? null)} />
          <button onClick={onVerify} disabled={!verFile || busy}>Verify / جانچیں</button>
        </div>
        {ver?.kind === 'exact' && <p className="ok"><strong>Exact match ✓</strong> — byte-identical to {ver.record.id} ({ver.record.created_at}).</p>}
        {ver?.kind === 'strong' && <p className="ok"><strong>Strong match ✓</strong> — distance {ver.distance}/64 to {ver.record.id}. Likely derived from your original. Print the evidence pack below.</p>}
        {ver?.kind === 'possible' && <p className="warn"><strong>Possible match</strong> — distance {ver.distance}/64 to {ver.record.id}. Compare visually before claiming.</p>}
        {ver?.kind === 'none' && <p className="bad"><strong>No match</strong> — closest distance {ver.distance}/64.</p>}
        {ver?.kind === 'empty' && <p className="warn">No Nishan records on this device yet — register the original first.</p>}
      </section>

      <section className="panel">
        <h2>Your Nishan records (this device only)</h2>
        {records.length === 0 ? <p>No records yet.</p> : (
          <table><thead><tr><th>ID</th><th>Registered</th><th>SHA-256</th><th>pHash</th></tr></thead>
          <tbody>{records.map(r => <tr key={r.id}><td className="mono">{r.id}</td><td>{r.created_at}</td><td className="mono">{r.sha256.slice(0, 16)}…</td><td className="mono">{r.phash}</td></tr>)}</tbody></table>
        )}
        <div className="row" style={{ marginTop: 12 }}>
          <button className="ghost" onClick={exportBackup}>Export backup (JSON)</button>
          <button className="ghost" onClick={() => window.print()}>Print evidence pack</button>
        </div>
      </section>
      {error && <p className="bad">{error}</p>}
    </>
  );
}
