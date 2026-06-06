import { cn } from "@/lib/utils";
import { contourPath, focalPoint } from "@/lib/viz/anomaly-field";
import { heatColor } from "@/lib/viz/heat-ramp";

interface ContourRingProps {
  tileId: string;
  score: number;
  className?: string;
  animated?: boolean;
}

const SIZE = 512;

/** ROI contour traced around the hottest region, with a crosshair marker. */
export function ContourRing({ tileId, score, className, animated = true }: ContourRingProps) {
  const d = contourPath(tileId, score, SIZE);
  const focal = focalPoint(tileId);
  const cx = focal.x * SIZE;
  const cy = focal.y * SIZE;
  const color = heatColor(Math.max(score, 0.4));

  return (
    <svg
      viewBox={`0 0 ${SIZE} ${SIZE}`}
      preserveAspectRatio="none"
      className={cn("size-full", className)}
      aria-hidden
    >
      <path
        d={d}
        fill="none"
        stroke={color}
        strokeWidth={2}
        strokeDasharray="8 6"
        opacity={0.95}
        style={{ filter: `drop-shadow(0 0 6px ${color})` }}
      >
        {animated && (
          <animate
            attributeName="stroke-dashoffset"
            from="0"
            to="-28"
            dur="1.2s"
            repeatCount="indefinite"
          />
        )}
      </path>
      {/* crosshair on focal point */}
      <g stroke={color} strokeWidth={1.4} opacity={0.85}>
        <line x1={cx - 16} y1={cy} x2={cx - 6} y2={cy} />
        <line x1={cx + 6} y1={cy} x2={cx + 16} y2={cy} />
        <line x1={cx} y1={cy - 16} x2={cx} y2={cy - 6} />
        <line x1={cx} y1={cy + 6} x2={cx} y2={cy + 16} />
      </g>
    </svg>
  );
}
