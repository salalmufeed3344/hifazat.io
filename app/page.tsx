import Link from 'next/link';

const modules = [
  { href: '/nishan', name: 'Nishan — Prove the original', desc: 'Register a photo before posting. If a fake circulates, match it and print an evidence pack for NCCIA 1799. Works offline, photo never leaves your device.', status: 'Live in v0.1' },
  { href: '/awaaz', name: 'Awaaz Shield — Cloak your voice', desc: 'Protect a voice clip so a clone comes out garbled. Based on Enkidu (ACM MM 2025).', status: 'Week 2' },
  { href: '/tainted', name: 'Tainted Video — Fake exposes itself', desc: 'Protect a video selfie so a face-swap shows visible stripes. Based on TaintedPixels (Aug 2026).', status: 'Week 3' },
  { href: '/mirage', name: 'MIRAGE Shield — Editors refuse', desc: 'Invisible noise that makes ChatGPT / Gemini refuse to edit your photo. Based on MIRAGE (Jun 2026, paper-only — replication is the research).', status: 'Weeks 4–5' },
];

export default function Home() {
  return (
    <>
      <h1>Protect your photo, voice and video <em>before</em> you post them.</h1>
      <p className="sub">Pakistan&apos;s AI defence suite — Urdu-first, free, private by design. FIA received 1,180 deepfake complaints in 2023. PECA §21 already makes AI-editing someone&apos;s photo into illegal content a crime. Hifazat gives ordinary Pakistanis the tool to protect themselves first, and prove what was real after.</p>
      <div className="grid">
        {modules.map(m => (
          <article className="card" key={m.href}>
            <h3><Link href={m.href}>{m.name}</Link></h3>
            <p>{m.desc}</p>
            <p><strong>{m.status}</strong></p>
          </article>
        ))}
      </div>
      <section className="panel">
        <h2>Honest claim</h2>
        <p>Research papers exist — including NUST SEECS RAPID (Jul 2026) — but no free web tool a student can use before posting a photo, voice note or video exists in Pakistan today. That is the gap Hifazat fills. Protection raises the bar and creates evidence; it does not guarantee safety. Every module ships with measured test results, including WhatsApp survival.</p>
      </section>
    </>
  );
}
