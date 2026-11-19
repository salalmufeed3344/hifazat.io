// Hamming distance between two equal-length hex strings (perceptual hashes).
// Plain JS so it can be unit-tested with `node --test` without a TS loader.
export function hammingHex(a, b) {
  if (a.length !== b.length) return Infinity;
  let n = 0;
  for (let i = 0; i < a.length; i++) {
    let v = parseInt(a[i], 16) ^ parseInt(b[i], 16);
    while (v) { n += v & 1; v >>= 1; }
  }
  return n;
}
