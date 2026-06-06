import type { Modality } from "@/lib/types";
import { cn } from "@/lib/utils";
import { hashSeed, mulberry32 } from "@/lib/viz/seeded-random";

interface TileTextureProps {
  tileId: string;
  modality: Modality;
  className?: string;
  /** When provided, renders a real image instead of the procedural texture. */
  src?: string;
}

const MODALITY_TINT: Record<Modality, { base: string; tint: string }> = {
  SEM: { base: "oklch(0.28 0.006 255)", tint: "oklch(0.55 0.01 255 / 0)" },
  PL: { base: "oklch(0.24 0.05 250)", tint: "oklch(0.5 0.12 250 / 0.18)" },
  etch: { base: "oklch(0.27 0.03 70)", tint: "oklch(0.55 0.08 60 / 0.16)" },
  wafer_map: { base: "oklch(0.26 0.01 255)", tint: "oklch(0.5 0.02 255 / 0)" },
  synthetic: { base: "oklch(0.25 0.02 290)", tint: "oklch(0.5 0.08 300 / 0.14)" },
};

function sanitize(id: string): string {
  return id.replace(/[^a-zA-Z0-9_-]/g, "");
}

export function TileTexture({ tileId, modality, className, src }: TileTextureProps) {
  if (src) {
    return (
      // eslint-disable-next-line @next/next/no-img-element
      <img
        src={src}
        alt=""
        className={cn("size-full object-cover", className)}
        draggable={false}
      />
    );
  }

  const uid = `tx-${sanitize(tileId)}-${modality}`;
  const seed = hashSeed(tileId);
  const rng = mulberry32(seed);
  const tint = MODALITY_TINT[modality];

  // Frequency / grain character per modality.
  const baseFreq =
    modality === "PL"
      ? 0.012 + rng() * 0.01
      : modality === "etch"
        ? 0.03 + rng() * 0.02
        : modality === "synthetic"
          ? 0.02 + rng() * 0.015
          : 0.05 + rng() * 0.04; // SEM = fine grain

  // Decorative deterministic features.
  const grainLines = Array.from({ length: modality === "SEM" ? 6 : 3 }, () => ({
    x1: rng() * 512,
    y1: rng() * 512,
    x2: rng() * 512,
    y2: rng() * 512,
  }));
  const pits =
    modality === "etch"
      ? Array.from({ length: 26 }, () => ({
          cx: rng() * 512,
          cy: rng() * 512,
          r: 2 + rng() * 5,
        }))
      : [];

  return (
    <svg
      viewBox="0 0 512 512"
      preserveAspectRatio="none"
      className={cn("size-full", className)}
      aria-hidden
    >
      <defs>
        <filter id={`${uid}-grain`} x="0" y="0" width="100%" height="100%">
          <feTurbulence
            type="fractalNoise"
            baseFrequency={baseFreq}
            numOctaves={3}
            seed={seed % 100}
            stitchTiles="stitch"
            result="noise"
          />
          <feColorMatrix in="noise" type="saturate" values="0" result="gray" />
          <feComponentTransfer>
            <feFuncA type="linear" slope={modality === "PL" ? 0.4 : 0.7} />
          </feComponentTransfer>
        </filter>
        <radialGradient id={`${uid}-vign`} cx="50%" cy="42%" r="75%">
          <stop offset="55%" stopColor="oklch(0 0 0 / 0)" />
          <stop offset="100%" stopColor="oklch(0.06 0.01 255 / 0.7)" />
        </radialGradient>
        {modality === "PL" && (
          <radialGradient id={`${uid}-lum`} cx="42%" cy="38%" r="60%">
            <stop offset="0%" stopColor="oklch(0.62 0.12 245 / 0.5)" />
            <stop offset="100%" stopColor="oklch(0.62 0.12 245 / 0)" />
          </radialGradient>
        )}
      </defs>

      <rect width="512" height="512" fill={tint.base} />
      <rect width="512" height="512" filter={`url(#${uid}-grain)`} opacity="0.9" />
      {modality === "PL" && <rect width="512" height="512" fill={`url(#${uid}-lum)`} />}
      <rect width="512" height="512" fill={tint.tint} />

      {modality === "SEM" &&
        grainLines.map((l, i) => (
          <line
            key={i}
            x1={l.x1}
            y1={l.y1}
            x2={l.x2}
            y2={l.y2}
            stroke="oklch(0.7 0.01 255 / 0.12)"
            strokeWidth={1}
          />
        ))}

      {pits.map((p, i) => (
        <circle
          key={i}
          cx={p.cx}
          cy={p.cy}
          r={p.r}
          fill="oklch(0.12 0.02 60 / 0.55)"
          stroke="oklch(0.6 0.06 70 / 0.25)"
          strokeWidth={0.6}
        />
      ))}

      {modality === "synthetic" && (
        <g stroke="oklch(0.6 0.02 290 / 0.14)" strokeWidth="1" fill="none">
          {Array.from({ length: 7 }, (_, i) => (
            <line key={`v${i}`} x1={(i + 1) * 64} y1={0} x2={(i + 1) * 64} y2={512} />
          ))}
          {Array.from({ length: 7 }, (_, i) => (
            <line key={`h${i}`} x1={0} y1={(i + 1) * 64} x2={512} y2={(i + 1) * 64} />
          ))}
        </g>
      )}

      <rect width="512" height="512" fill={`url(#${uid}-vign)`} />
    </svg>
  );
}
