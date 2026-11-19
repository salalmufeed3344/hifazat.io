import { NextResponse } from 'next/server';
// TRD §3: POST /api/awaaz/protect — proxies to the Awaaz FastAPI worker.
// Set AWAAZ_WORKER_URL (e.g. http://localhost:8001) where the worker runs.
// Cordum policy: DENY retention — worker processes in a temp dir, deletes after.
export async function POST(req: Request) {
  const base = process.env.AWAAZ_WORKER_URL;
  if (!base) {
    return NextResponse.json(
      { error: 'Awaaz worker is not running yet. Start workers/awaaz (uvicorn app:app --port 8001) and set AWAAZ_WORKER_URL. See workers/awaaz/README.md.', code: 'worker_unavailable' },
      { status: 503 },
    );
  }
  const form = await req.formData();
  const file = form.get('file');
  if (!(file instanceof File)) {
    return NextResponse.json({ error: 'send an audio file as form field "file"', code: 'bad_request' }, { status: 400 });
  }
  const upstream = new FormData(); upstream.append('file', file, file.name);
  const r = await fetch(`${base}/protect`, { method: 'POST', body: upstream });
  if (!r.ok) {
    const j = await r.json().catch(() => ({}));
    return NextResponse.json({ error: j.detail || j.error || `worker returned ${r.status}`, code: 'worker_error' }, { status: r.status });
  }
  return new NextResponse(r.body, {
    headers: {
      'Content-Type': 'audio/wav',
      'Content-Disposition': 'attachment; filename="awaaz-protected.wav"',
      'X-Hifazat-SNR-dB': r.headers.get('X-Hifazat-SNR-dB') || '',
    },
  });
}
