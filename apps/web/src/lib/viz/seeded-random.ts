// Deterministic, SSR-safe pseudo-randomness keyed off a string (tile_id).
// No Math.random() — server and client produce byte-identical fields.

/** FNV-1a string hash -> uint32 seed. */
export function hashSeed(input: string): number {
  let h = 0x811c9dc5;
  for (let i = 0; i < input.length; i++) {
    h ^= input.charCodeAt(i);
    h = Math.imul(h, 0x01000193);
  }
  return h >>> 0;
}

/** mulberry32 PRNG: pure, fast, returns a function yielding floats in [0, 1). */
export function mulberry32(seed: number): () => number {
  let a = seed >>> 0;
  return () => {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** Convenience: a PRNG seeded from a tile id (optionally salted). */
export function rngFor(tileId: string, salt = ""): () => number {
  return mulberry32(hashSeed(`${tileId}::${salt}`));
}

/** Linear interpolation. */
export function lerp(a: number, b: number, t: number): number {
  return a + (b - a) * t;
}

/** Clamp to [min, max]. */
export function clamp(v: number, min = 0, max = 1): number {
  return Math.max(min, Math.min(max, v));
}
