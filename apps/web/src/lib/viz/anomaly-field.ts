import { clamp, rngFor } from "./seeded-random";

export interface Blob {
  x: number; // 0..1
  y: number; // 0..1
  r: number; // 0..1 (fraction of tile size)
  intensity: number; // 0..1 -> heat ramp
}

/** Primary anomaly focal point (0..1) — shared by heatmap and contour. */
export function focalPoint(tileId: string): { x: number; y: number } {
  const rng = rngFor(tileId, "focal");
  return { x: 0.28 + rng() * 0.44, y: 0.26 + rng() * 0.44 };
}

/**
 * Deterministic set of heat blobs for a tile. The first blob is the primary
 * anomaly at the focal point (sized + heated by score); the rest are cooler
 * background activity. Same inputs -> identical field on server and client.
 */
const BLOB_R = 0.12; // uniform radius for every probe circle

export function anomalyBlobs(tileId: string, score: number): Blob[] {
  const rng = rngFor(tileId, "heat");
  const focal = focalPoint(tileId);
  const count = 4 + Math.round(score * 4);
  const blobs: Blob[] = [];

  // Primary anomaly at the focal point — hottest, same size as the rest.
  blobs.push({
    x: focal.x,
    y: focal.y,
    r: BLOB_R,
    intensity: clamp(0.3 + score * 0.7),
  });

  for (let i = 1; i < count; i++) {
    const near = rng() < 0.5;
    const x = near
      ? clamp(focal.x + (rng() - 0.5) * 0.42, 0.08, 0.92)
      : 0.1 + rng() * 0.8;
    const y = near
      ? clamp(focal.y + (rng() - 0.5) * 0.42, 0.08, 0.92)
      : 0.1 + rng() * 0.8;
    blobs.push({
      x,
      y,
      r: BLOB_R,
      intensity: clamp(score * (0.4 + rng() * 0.45) + rng() * 0.08),
    });
  }
  return blobs;
}

/** A wobbly closed contour (SVG path) around the focal region, scaled by score. */
export function contourPath(tileId: string, score: number, size: number): string {
  const rng = rngFor(tileId, "contour");
  const focal = focalPoint(tileId);
  const cx = focal.x * size;
  const cy = focal.y * size;
  const baseR = (0.12 + score * 0.18) * size;
  const points = 18;
  const pts: [number, number][] = [];
  for (let i = 0; i < points; i++) {
    const a = (i / points) * Math.PI * 2;
    const wobble = 0.72 + rng() * 0.56;
    pts.push([cx + Math.cos(a) * baseR * wobble, cy + Math.sin(a) * baseR * wobble]);
  }
  // Catmull-Rom -> smooth closed path.
  let d = `M ${pts[0][0].toFixed(1)} ${pts[0][1].toFixed(1)} `;
  for (let i = 0; i < points; i++) {
    const p0 = pts[(i - 1 + points) % points];
    const p1 = pts[i];
    const p2 = pts[(i + 1) % points];
    const p3 = pts[(i + 2) % points];
    const c1x = p1[0] + (p2[0] - p0[0]) / 6;
    const c1y = p1[1] + (p2[1] - p0[1]) / 6;
    const c2x = p2[0] - (p3[0] - p1[0]) / 6;
    const c2y = p2[1] - (p3[1] - p1[1]) / 6;
    d += `C ${c1x.toFixed(1)} ${c1y.toFixed(1)}, ${c2x.toFixed(1)} ${c2y.toFixed(1)}, ${p2[0].toFixed(1)} ${p2[1].toFixed(1)} `;
  }
  return `${d}Z`;
}
