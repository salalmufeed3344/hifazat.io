// Nishan core — client-only. Originals never leave the device (Cordum: DENY server upload by construction).
// shortcut: localStorage, not IndexedDB/encrypted vault yet — upgrade when records exceed ~50 (PRD Week 1.1).
import { hammingHex } from './hamming.js';

export type NishanRecord = {
  id: string;
  created_at: string;
  sha256: string;
  phash: string;
  tool: string;
};

const KEY = 'hifazat-nishan-v1';
export const TOOL_VERSION = 'hifazat-nishan-0.1';

export function loadRecords(): NishanRecord[] {
  try { return JSON.parse(localStorage.getItem(KEY) || '[]'); } catch { return []; }
}
export function saveRecords(r: NishanRecord[]) { localStorage.setItem(KEY, JSON.stringify(r)); }

export async function sha256Hex(file: File): Promise<string> {
  const buf = await file.arrayBuffer();
  const h = await crypto.subtle.digest('SHA-256', buf);
  return [...new Uint8Array(h)].map(b => b.toString(16).padStart(2, '0')).join('');
}

/** dHash: 9x8 grayscale, adjacent-pixel comparison -> 64-bit perceptual hash (16 hex chars). */
export async function dhashHex(file: File): Promise<string> {
  const bmp = await createImageBitmap(file);
  const c = document.createElement('canvas'); c.width = 9; c.height = 8;
  const x = c.getContext('2d'); if (!x) throw new Error('canvas unavailable');
  x.drawImage(bmp, 0, 0, 9, 8);
  const d = x.getImageData(0, 0, 9, 8).data;
  let bits = '';
  for (let r = 0; r < 8; r++) for (let col = 0; col < 8; col++) {
    const i = (r * 9 + col) * 4, j = i + 4;
    const g1 = .299 * d[i] + .587 * d[i + 1] + .114 * d[i + 2];
    const g2 = .299 * d[j] + .587 * d[j + 1] + .114 * d[j + 2];
    bits += g1 > g2 ? '1' : '0';
  }
  let hex = ''; for (let i = 0; i < 64; i += 4) hex += parseInt(bits.slice(i, i + 4), 2).toString(16);
  return hex;
}

export async function registerPhoto(file: File): Promise<NishanRecord> {
  const [sha256, phash] = await Promise.all([sha256Hex(file), dhashHex(file)]);
  const rec: NishanRecord = {
    id: 'N-' + Date.now().toString(36).toUpperCase(),
    created_at: new Date().toISOString(), sha256, phash, tool: TOOL_VERSION,
  };
  const r = loadRecords(); r.unshift(rec); saveRecords(r);
  return rec;
}

export type VerifyResult =
  | { kind: 'exact'; record: NishanRecord }
  | { kind: 'strong'; record: NishanRecord; distance: number }
  | { kind: 'possible'; record: NishanRecord; distance: number }
  | { kind: 'none'; distance: number }
  | { kind: 'empty' };

export async function verifyPhoto(file: File): Promise<VerifyResult> {
  const records = loadRecords();
  if (!records.length) return { kind: 'empty' };
  const [sha256, phash] = await Promise.all([sha256Hex(file), dhashHex(file)]);
  const exact = records.find(r => r.sha256 === sha256);
  if (exact) return { kind: 'exact', record: exact };
  let best: NishanRecord | null = null, bd = Infinity;
  for (const r of records) { const d = hammingHex(phash, r.phash); if (d < bd) { bd = d; best = r; } }
  if (!best) return { kind: 'none', distance: bd };
  if (bd <= 10) return { kind: 'strong', record: best, distance: bd };
  if (bd <= 18) return { kind: 'possible', record: best, distance: bd };
  return { kind: 'none', distance: bd };
}
