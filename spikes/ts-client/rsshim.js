// The three Rust functions this client actually uses, in plain JS.
export function foo(x) { return x === 'me' ? 'yes' : 'no'; }

export function rs_hash_string(s) {
  let hash = 0;
  for (const ch of s) hash = (Math.imul(hash, 61) + ch.codePointAt(0) - 32) | 0;
  return hash;
}

function fromSignedBE(bytes) {
  let v = 0n;
  for (const b of bytes) v = (v << 8n) | BigInt(b & 0xff);
  if (bytes.length && (bytes[0] & 0x80)) v -= 1n << BigInt(8 * bytes.length);   // two's complement
  return v;
}
function toSignedBE(v) {
  if (v === 0n) return new Uint8Array([0]);
  let hex = v.toString(16);
  if (hex.length % 2) hex = '0' + hex;
  let out = hex.match(/../g).map(h => parseInt(h, 16));
  if (out[0] & 0x80) out.unshift(0);            // keep it positive, as num-bigint does
  return new Uint8Array(out);
}
function modpow(base, exp, mod) {
  let r = 1n; base %= mod;
  while (exp > 0n) { if (exp & 1n) r = (r * base) % mod; base = (base * base) % mod; exp >>= 1n; }
  return r;
}
export function rs_encrypt_bytes(bytes, modulus, publicKey) {
  return toSignedBE(modpow(fromSignedBE(bytes), BigInt(publicKey), BigInt(modulus)));
}

export function noise(x, y) {
  let n = (x + Math.imul(y, 57)) | 0;
  n = (n ^ (n << 13)) | 0;
  const t = (Math.imul(n, (Math.imul(Math.imul(n, n), 15731) + 789221) | 0) + 1376312589) | 0;
  return ((t & 0x7fffffff) >> 19) & 255;
}
