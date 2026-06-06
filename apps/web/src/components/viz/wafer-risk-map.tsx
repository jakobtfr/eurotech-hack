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
  className?: string;
}

const VERDICT_RING: Record<string, string> = {
  PASS: "var(--verdict-pass)",
  REVIEW: "var(--verdict-review)",
  REJECT: "var(--verdict-reject)",
};

export function WaferRiskMap({
  riskMap,
  selectedTileId,
  highlightTileId,
  onSelectTile,
  className,
}: WaferRiskMapProps) {
  const { cols, rows, tiles } = riskMap;
  const [hovered, setHovered] = useState<RiskTile | null>(null);
  const cx = (cols - 1) / 2 + 0.5;
  const cy = (rows - 1) / 2 + 0.5;
  const r = Math.min(cols, rows) / 2 + 0.1;

  const active = hovered;

  return (
    <div className={cn("flex flex-col gap-3", className)}>
      <div className="relative aspect-square w-full">
        <svg
          viewBox={`-0.5 -0.5 ${cols + 1} ${rows + 1}`}
          className="size-full"
          role="group"
          aria-label="Wafer risk map"
        >
          <defs>
            <radialGradient id="wafer-sheen" cx="40%" cy="32%" r="80%">
              <stop offset="0%" stopColor="oklch(0.4 0.02 255 / 0.25)" />
              <stop offset="100%" stopColor="oklch(0.1 0.01 255 / 0)" />
            </radialGradient>
          </defs>

          {/* wafer disc */}
          <circle
            cx={cx}
            cy={cy}
            r={r}
            fill="var(--canvas)"
            stroke="var(--border)"
            strokeWidth={0.08}
          />
          <circle cx={cx} cy={cy} r={r} fill="url(#wafer-sheen)" />

          {tiles.map((t) => {
            if (!t.in_wafer) return null;
            const isSelected = t.has_result && t.tile_id === selectedTileId;
            const isHighlight = t.has_result && t.tile_id === highlightTileId;
            const fill = heatColor(t.anomaly_score, 0.85);
            const hot = t.verdict !== "PASS";
            return (
              <g key={`${t.col}-${t.row}`}>
                <rect
                  x={t.col + 0.08}
                  y={t.row + 0.08}
                  width={0.84}
                  height={0.84}
                  rx={0.16}
                  fill={fill}
                  stroke={
                    isSelected
                      ? "oklch(1 0 0 / 0.95)"
                      : t.has_result
                        ? "oklch(0.95 0 0 / 0.5)"
                        : "oklch(0 0 0 / 0.25)"
                  }
                  strokeWidth={isSelected ? 0.09 : t.has_result ? 0.05 : 0.02}
                  className={cn(
                    "transition-[opacity,transform] duration-150",
                    t.has_result && "cursor-pointer",
                  )}
                  style={{
                    filter: hot
                      ? `drop-shadow(0 0 ${0.12 + t.anomaly_score * 0.3}px ${heatColor(t.anomaly_score)})`
                      : undefined,
                    opacity:
                      active && active !== t && active.in_wafer ? 0.55 : 1,
                  }}
                  onMouseEnter={() => setHovered(t)}
                  onMouseLeave={() => setHovered(null)}
                  onClick={() =>
                    t.has_result && onSelectTile?.(t.tile_id)
                  }
                />
                {t.has_result && (
                  <circle
                    cx={t.col + 0.5}
                    cy={t.row + 0.5}
                    r={0.09}
                    fill="oklch(1 0 0 / 0.92)"
                    pointerEvents="none"
                  />
                )}
                {isHighlight && (
                  <rect
                    x={t.col + 0.02}
                    y={t.row + 0.02}
                    width={0.96}
                    height={0.96}
                    rx={0.2}
                    fill="none"
                    stroke={VERDICT_RING[t.verdict]}
                    strokeWidth={0.1}
                    className="animate-pulse-ring origin-center"
                    style={{ transformBox: "fill-box" }}
                    pointerEvents="none"
                  />
                )}
              </g>
            );
          })}
        </svg>
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
            {riskMap.summary.inspected} tiles · hover to probe · ◷ marked = full
            result
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
