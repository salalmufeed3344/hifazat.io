import { NextResponse } from 'next/server';
// TRD §3: POST /api/awaaz/protect — multipart audio (≤2 min, ≤10 MB) -> protected audio.
// Cordum policy: DENY retention — worker must process in memory and delete immediately. Not wired yet (Week 2).
export async function POST() {
  return NextResponse.json(
    { error: 'Awaaz worker not wired yet (Week 2). See TRD.md §3.', code: 'not_implemented' },
    { status: 501 },
  );
}
