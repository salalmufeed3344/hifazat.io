import test from 'node:test';
import assert from 'node:assert/strict';
import { hammingHex } from './hamming.js';

test('identical hashes distance 0', () => {
  assert.equal(hammingHex('0000000000000000', '0000000000000000'), 0);
});
test('opposite hashes distance 64', () => {
  assert.equal(hammingHex('ffffffffffffffff', '0000000000000000'), 64);
});
test('one bit differs', () => {
  assert.equal(hammingHex('8000000000000000', '0000000000000000'), 1);
});
test('different lengths -> Infinity', () => {
  assert.equal(hammingHex('ff', 'ffff'), Infinity);
});
