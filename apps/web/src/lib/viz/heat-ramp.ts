import { clamp, lerp } from "./seeded-random";

// Spectral anomaly ramp in OKLCH: cyan -> magenta -> red -> amber.
// Hue is allowed to exceed 360 so a plain linear lerp travels the intended
// direction (cyan->blue->magenta->red->orange->amber); we mod 360 at output.
// These stops mirror the --heat-* CSS variables in globals.css so Canvas/SVG
// fills match CSS-driven UI exactly.
interface Stop {
  t: number;
  l: number;
  c: number;
  h: number;
}

// Blue -> red thermal map (cold/normal -> hot/anomaly). Hue allowed to exceed
// 360 so a plain lerp travels blue -> indigo -> magenta -> red (no rainbow).
const STOPS: Stop[] = [
  { t: 0.0, l: 0.56, c: 0.15, h: 258 }, // blue    (--heat-0)
  { t: 0.4, l: 0.5, c: 0.19, h: 300 }, // indigo   (--heat-35)
  { t: 0.72, l: 0.55, c: 0.21, h: 350 }, // magenta (--heat-70)
  { t: 1.0, l: 0.58, c: 0.225, h: 385 }, // red=25  (--heat-100)
];

interface HeatLCH {
  l: number;
  c: number;
  h: number;
}

function sample(score: number): HeatLCH {
  const t = clamp(score);
  let lo = STOPS[0];
  let hi = STOPS[STOPS.length - 1];
  for (let i = 0; i < STOPS.length - 1; i++) {
    if (t >= STOPS[i].t && t <= STOPS[i + 1].t) {
      lo = STOPS[i];
      hi = STOPS[i + 1];
      break;
    }
  }
  const span = hi.t - lo.t || 1;
  const f = (t - lo.t) / span;
  return {
    l: lerp(lo.l, hi.l, f),
    c: lerp(lo.c, hi.c, f),
    h: lerp(lo.h, hi.h, f) % 360,
  };
}

/** OKLCH color string for an anomaly score (0..1), optional alpha (0..1). */
export function heatColor(score: number, alpha = 1): string {
  const { l, c, h } = sample(score);
  const a = clamp(alpha);
  return a >= 1
    ? `oklch(${l.toFixed(3)} ${c.toFixed(3)} ${h.toFixed(1)})`
    : `oklch(${l.toFixed(3)} ${c.toFixed(3)} ${h.toFixed(1)} / ${a.toFixed(3)})`;
}

/** A soft glow color (more saturated, semi-transparent) for a score. */
export function heatGlow(score: number, alpha = 0.5): string {
  const { l, c, h } = sample(score);
  return `oklch(${Math.min(l + 0.04, 0.92).toFixed(3)} ${(c + 0.03).toFixed(3)} ${h.toFixed(1)} / ${clamp(alpha).toFixed(3)})`;
}

/** Gradient stops for SVG <linearGradient>/<radialGradient>. */
export function heatStops(count = 6): { offset: number; color: string }[] {
  return Array.from({ length: count }, (_, i) => {
    const offset = i / (count - 1);
    return { offset, color: heatColor(offset) };
  });
}
