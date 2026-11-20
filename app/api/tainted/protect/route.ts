import { NextResponse } from 'next/server';
// TRD §3: POST /api/tainted/protect — proxies to the Tainted FastAPI worker.
// Set TAINTED_WORKER_URL (e.g. http://localhost:8002) where the worker runs.
export async function POST(req: Request) {
  const base = process.env.TAINTED_WORKER_URL;
  if (!base) {
    return NextResponse.json(
      { error: 'Tainted worker is not running yet. Start workers/tainted (uvicorn app:app --port 8002) and set TAINTED_WORKER_URL. See workers/tainted/README.md.', code: 'worker_unavailable' },
      { status: 503 },
    );
  }
  const form = await req.formData();
  const file = form.get('file');
  if (!(file instanceof File)) {
    return NextResponse.json({ error: 'send a video file as form field "file"', code: 'bad_request' }, { status: 400 });
  }
  const upstream = new FormData(); upstream.append('file', file, file.name);
  const r = await fetch(`${base}/protect`, { method: 'POST', body: upstream });
  if (!r.ok) {
    const j = await r.json().catch(() => ({}));
    return NextResponse.json({ error: j.detail || j.error || `worker returned ${r.status}`, code: 'worker_error' }, { status: r.status });
  }
  return new NextResponse(r.body, {
    headers: {
      'Content-Type': 'video/mp4',
      'Content-Disposition': 'attachment; filename="tainted-protected.mp4"',
      'X-Hifazat-Frames': r.headers.get('X-Hifazat-Frames') || '',
      'X-Hifazat-Face-Frames': r.headers.get('X-Hifazat-Face-Frames') || '',
    },
  });
}
