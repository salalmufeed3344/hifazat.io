import { NextResponse } from 'next/server';
// TRD §3: POST /api/tainted/protect — multipart video (≤60 s, ≤50 MB) -> protected mp4. CPU worker, Week 3.
export async function POST() {
  return NextResponse.json(
    { error: 'Tainted Video worker not wired yet (Week 3). See TRD.md §3.', code: 'not_implemented' },
    { status: 501 },
  );
}
