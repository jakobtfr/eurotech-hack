"use client";

import { useState } from "react";
import type { RiskMap, RiskTile } from "@/lib/types";
import { cn } from "@/lib/utils";
import { heatColor } from "@/lib/viz/heat-ramp";

interface WaferRiskMapProps {
  riskMap: RiskMap;
  selectedTileId?: string | null;
  highlightTileId?: string | null;
  onSelectTile?: (tileId: string) => void;
  /** Show only inspected tiles as scored/clickable; render the rest as a
   *  neutral "not inspected" die outline instead of fabricated heat scores. */
  emphasizeInspected?: boolean;
  className?: string;
}

const VERDICT_RING: Record<string, string> = {
  PASS: "var(--verdict-pass)",
  REVIEW: "var(--verdict-review)",
  HOLD: "var(--verdict-hold)",
};

export function WaferRiskMap({
  riskMap,
  selectedTileId,
  highlightTileId,
  onSelectTile,
  emphasizeInspected = false,
  className,
}: WaferRiskMapProps) {
  const { cols, rows, tiles } = riskMap;
  const [hovered, setHovered] = useState<RiskTile | null>(null);

  // The die field is a cols×rows grid (cells span 0..cols, 0..rows). The wafer
  // disc hugs the actual in-wafer die field: radius = farthest die-center from
  // the grid center + one cell half-diagonal (~0.71) and a thin margin, so the
  // squares fill the disc edge-to-edge instead of floating in an empty ring.
  const cx = cols / 2;
  const cy = rows / 2;
  const dieReach = tiles.reduce((max, t) => {
    if (!t.in_wafer) return max;
    const dx = t.col + 0.5 - cx;
    const dy = t.row + 0.5 - cy;
    return Math.max(max, Math.hypot(dx, dy));
  }, 0);
  const r = dieReach + 0.85;
  const vbX = cx - r - 0.25;
  const vbY = cy - r - 0.25;
  const vbW = 2 * r + 0.5;
  const vbH = 2 * r + 0.55;
  const notch = 0.42;

  const active = hovered;
  const inspectedCount = tiles.filter((t) => t.in_wafer).length;
  const flaggedCount = riskMap.summary.review + riskMap.summary.hold;

  // Map grid/SVG coordinates to container-relative percentages for the click overlay.
  const pctX = (sx: number) => ((sx - vbX) / vbW) * 100;
  const pctY = (sy: number) => ((sy - vbY) / vbH) * 100;

  return (
    <div className={cn("flex flex-col gap-3", className)}>
      <div className="relative aspect-square w-full">
        <svg
          viewBox={`${vbX} ${vbY} ${vbW} ${vbH}`}
          className="size-full"
          role="img"
          aria-label="Wafer inspection field"
        >
          <title>Wafer inspection field</title>
          <defs>
            <radialGradient id="wafer-sheen" cx="38%" cy="30%" r="78%">
              <stop offset="0%" stopColor="oklch(0.42 0.02 255 / 0.18)" />
              <stop offset="100%" stopColor="oklch(0.1 0.01 255 / 0)" />
            </radialGradient>
          </defs>

          {/* wafer disc + bottom notch */}
          <circle
            cx={cx}
            cy={cy}
            r={r}
            fill="var(--canvas)"
            stroke="var(--plate-frame)"
            strokeWidth={0.05}
          />
          <circle cx={cx} cy={cy} r={r} fill="url(#wafer-sheen)" />
          <path
            d={`M ${cx - 0.24} ${cy + r} L ${cx} ${cy + r - notch} L ${cx + 0.24} ${cy + r} Z`}
            fill="var(--background)"
          />

          {tiles.map((t) => {
            if (!t.in_wafer) return null;
            const inspected = t.has_result;
            const isSelected = inspected && t.tile_id === selectedTileId;
            const isHighlight = inspected && t.tile_id === highlightTileId;
            const isDimmed = active && active !== t && active.in_wafer;
            return (
              <g key={`${t.col}-${t.row}`}>
                <rect
                  x={t.col + 0.09}
                  y={t.row + 0.09}
                  width={0.82}
                  height={0.82}
                  rx={0.07}
                  fill={
                    t.verdict === "PASS"
                      ? "oklch(0.34 0.028 248 / 0.9)"
                      : heatColor(t.anomaly_score, 0.9)
                  }
                  stroke={
                    isSelected
                      ? "oklch(1 0 0 / 0.95)"
                      : inspected
                        ? "oklch(0.97 0 0 / 0.55)"
                        : "oklch(0 0 0 / 0.22)"
                  }
                  strokeWidth={isSelected ? 0.07 : inspected ? 0.045 : 0.032}
                  className="transition-opacity duration-150"
                  style={{ opacity: isDimmed ? 0.45 : 1 }}
                />
                {inspected && (
                  <circle
                    cx={t.col + 0.5}
                    cy={t.row + 0.5}
                    r={0.08}
                    fill="oklch(1 0 0 / 0.9)"
                    pointerEvents="none"
                  />
                )}
                {isHighlight && (
                  <rect
                    x={t.col + 0.03}
                    y={t.row + 0.03}
                    width={0.94}
                    height={0.94}
                    rx={0.1}
                    fill="none"
                    stroke={VERDICT_RING[t.verdict]}
                    strokeWidth={0.09}
                    className="animate-pulse-ring origin-center"
                    style={{ transformBox: "fill-box" }}
                    pointerEvents="none"
                  />
                )}
              </g>
            );
          })}
        </svg>
        <div className="absolute inset-0">
          {tiles.map((t) => {
            if (!t.in_wafer) return null;
            if (emphasizeInspected && !t.has_result) return null;
            return (
              <button
                key={`${t.col}-${t.row}`}
                type="button"
                tabIndex={t.has_result ? 0 : -1}
                aria-disabled={!t.has_result}
                aria-label={`cell c${t.col} r${t.row}, score ${t.anomaly_score.toFixed(2)}, ${t.verdict}`}
                className={cn(
                  "absolute rounded-[3px] bg-transparent",
                  t.has_result && "cursor-pointer",
                )}
                style={{
                  left: `${pctX(t.col + 0.09)}%`,
                  top: `${pctY(t.row + 0.09)}%`,
                  width: `${(0.82 / vbW) * 100}%`,
                  height: `${(0.82 / vbH) * 100}%`,
                }}
                onMouseEnter={() => setHovered(t)}
                onMouseLeave={() => setHovered(null)}
                onFocus={() => setHovered(t)}
                onBlur={() => setHovered(null)}
                onClick={() => t.has_result && onSelectTile?.(t.tile_id)}
              />
            );
          })}
        </div>
      </div>

      {/* hover / legend readout */}
      <div className="flex items-center justify-between font-mono text-[0.7rem] text-muted-foreground">
        {active ? (
          <span className="text-foreground">
            cell c{active.col}·r{active.row}
            <span className="text-muted-foreground"> — score </span>
            {active.anomaly_score.toFixed(2)}
            <span className="text-muted-foreground"> — </span>
            <span style={{ color: VERDICT_RING[active.verdict] }}>
              {active.verdict}
            </span>
            {active.has_result && (
              <span className="text-primary"> · click to inspect</span>
            )}
          </span>
        ) : (
          <span>
            {emphasizeInspected
              ? `${inspectedCount} dies inspected · ${flaggedCount} flagged for review`
              : `${riskMap.summary.inspected} tiles · hover to probe · ◷ marked = full result`}
          </span>
        )}
        <span className="flex items-center gap-1.5">
          <span className="text-muted-foreground">low</span>
          <span
            className="h-2 w-20 rounded-full"
            style={{
              background:
                "linear-gradient(90deg, var(--heat-0), var(--heat-35), var(--heat-70), var(--heat-100))",
            }}
          />
          <span className="text-muted-foreground">high</span>
        </span>
      </div>
    </div>
  );
}
