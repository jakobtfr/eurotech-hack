import { cn } from "@/lib/utils";
import { heatColor } from "@/lib/viz/heat-ramp";
import { clamp } from "@/lib/viz/seeded-random";

interface ScoreGaugeProps {
  score: number;
  reviewAt: number;
  holdAt: number;
  size?: number;
  label?: string;
  className?: string;
}

const SWEEP = 270;
const START = -135;

function polar(cx: number, cy: number, r: number, angleDeg: number) {
  const a = ((angleDeg - 90) * Math.PI) / 180;
  return { x: cx + r * Math.cos(a), y: cy + r * Math.sin(a) };
}

function arc(cx: number, cy: number, r: number, a0: number, a1: number) {
  const p0 = polar(cx, cy, r, a0);
  const p1 = polar(cx, cy, r, a1);
  const large = Math.abs(a1 - a0) > 180 ? 1 : 0;
  return `M ${p0.x.toFixed(2)} ${p0.y.toFixed(2)} A ${r} ${r} 0 ${large} 1 ${p1.x.toFixed(2)} ${p1.y.toFixed(2)}`;
}

export function ScoreGauge({
  score,
  reviewAt,
  holdAt,
  size = 150,
  label = "anomaly score",
  className,
}: ScoreGaugeProps) {
  const f = clamp(score);
  const stroke = Math.max(7, Math.round(size * 0.06));
  const r = size / 2 - stroke;
  const cx = size / 2;
  const cy = size / 2;
  const color = heatColor(f); // single solid tone for the value arc

  // small notch marks at the thresholds
  const notch = (frac: number) => {
    const ang = START + frac * SWEEP;
    const a = polar(cx, cy, r + stroke / 2, ang);
    const b = polar(cx, cy, r - stroke / 2, ang);
    return { a, b };
  };
  const marks = [
    { id: "review", ...notch(reviewAt) },
    { id: "hold", ...notch(holdAt) },
  ];

  return (
    <div className={cn("relative", className)} style={{ width: size, height: size }}>
      <svg
        viewBox={`0 0 ${size} ${size}`}
        className="size-full"
        role="img"
        aria-label={`${label}: ${f.toFixed(2)}`}
      >
        <title>{`${label}: ${f.toFixed(2)}`}</title>
        {/* track */}
        <path
          d={arc(cx, cy, r, START, START + SWEEP)}
          fill="none"
          stroke="var(--muted)"
          strokeWidth={stroke}
          strokeLinecap="round"
        />
        {/* value — solid */}
        <path
          d={arc(cx, cy, r, START, START + f * SWEEP)}
          fill="none"
          stroke={color}
          strokeWidth={stroke}
          strokeLinecap="round"
        />
        {/* threshold notches */}
        {marks.map((m) => (
          <line
            key={m.id}
            x1={m.a.x}
            y1={m.a.y}
            x2={m.b.x}
            y2={m.b.y}
            stroke="var(--card)"
            strokeWidth={2}
            strokeLinecap="round"
          />
        ))}
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="font-display text-[1.7rem] font-bold tabular-nums leading-none text-foreground">
          {f.toFixed(2)}
        </span>
        <span className="mt-1.5 font-mono text-[0.5rem] uppercase tracking-[0.18em] text-muted-foreground">
          {label}
        </span>
      </div>
    </div>
  );
}
