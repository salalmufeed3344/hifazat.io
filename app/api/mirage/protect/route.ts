import { NextResponse } from 'next/server';
// TRD §3: POST /api/mirage/protect — multipart image (≤10 MB), async job, GPU worker. Weeks 4-5.
export async function POST() {
  return NextResponse.json(
    { error: 'MIRAGE GPU worker not wired yet (Weeks 4-5). See TRD.md §3.', code: 'not_implemented' },
    { status: 501 },
  );
}
