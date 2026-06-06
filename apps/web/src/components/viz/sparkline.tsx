import { cn } from "@/lib/utils";
import { heatColor } from "@/lib/viz/heat-ramp";
import { clamp } from "@/lib/viz/seeded-random";

interface SparklineProps {
  values: number[]; // 0..1
  threshold?: number;
  width?: number;
  height?: number;
  marker?: number; // index to emphasize
  className?: string;
}

export function Sparkline({
  values,
  threshold,
  width = 220,
  height = 48,
  marker,
  className,
}: SparklineProps) {
  if (values.length === 0) return null;
  const pad = 4;
  const n = values.length;
  const x = (i: number) => pad + (i / Math.max(n - 1, 1)) * (width - pad * 2);
  const y = (v: number) => height - pad - clamp(v) * (height - pad * 2);

  const linePts = values
    .map((v, i) => `${x(i).toFixed(1)},${y(v).toFixed(1)}`)
    .join(" ");
  const areaPts = `${pad},${height - pad} ${linePts} ${width - pad},${height - pad}`;
  const points = values.map((v, i) => ({
    id: `${x(i).toFixed(1)}-${y(v).toFixed(1)}-${v.toFixed(4)}`,
    value: v,
    x: x(i),
    y: y(v),
    isMarker: i === marker,
  }));

  return (
    <svg
      viewBox={`0 0 ${width} ${height}`}
      className={cn("w-full", className)}
      preserveAspectRatio="none"
      role="img"
      aria-label="score distribution"
    >
      <title>Score distribution</title>
      <defs>
        <linearGradient id="spark-fill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="var(--primary)" stopOpacity="0.28" />
          <stop offset="100%" stopColor="var(--primary)" stopOpacity="0" />
        </linearGradient>
      </defs>
      {threshold !== undefined && (
        <line
          x1={pad}
          y1={y(threshold)}
          x2={width - pad}
          y2={y(threshold)}
          stroke="var(--verdict-review)"
          strokeWidth={1}
          strokeDasharray="3 3"
          opacity={0.7}
        />
      )}
      <polygon points={areaPts} fill="url(#spark-fill)" />
      <polyline
        points={linePts}
        fill="none"
        stroke="var(--primary)"
        strokeWidth={1.5}
        strokeLinejoin="round"
        strokeLinecap="round"
      />
      {points.map((point) => (
        <circle
          key={point.id}
          cx={point.x}
          cy={point.y}
          r={point.isMarker ? 3 : 1.8}
          fill={heatColor(point.value)}
          stroke={point.isMarker ? "var(--foreground)" : "none"}
          strokeWidth={point.isMarker ? 1 : 0}
        />
      ))}
    </svg>
  );
}
