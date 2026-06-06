"use client";

import { ModalityTag } from "@/components/ui/modality-tag";
import type { DemoExample, Verdict } from "@/lib/types";
import { cn } from "@/lib/utils";
import { heatColor } from "@/lib/viz/heat-ramp";

const VERDICT_COLOR: Record<Verdict, string> = {
  PASS: "var(--verdict-pass)",
  REVIEW: "var(--verdict-review)",
  HOLD: "var(--verdict-hold)",
};

const ORDER: Verdict[] = ["PASS", "REVIEW", "HOLD"];

interface WorklistProps {
  examples: DemoExample[];
  selectedId: string;
  onSelect: (id: string) => void;
  className?: string;
}

/**
 * Triage queue for the inspection console — the inspected tiles, highest score
 * first. Selecting a row drives the stage, readout, and wafer map.
 */
export function Worklist({ examples, selectedId, onSelect, className }: WorklistProps) {
  const counts: Record<Verdict, number> = { PASS: 0, REVIEW: 0, HOLD: 0 };
  for (const ex of examples) counts[ex.result?.verdict ?? "PASS"]++;

  return (
    <div className={cn("flex min-h-0 flex-col", className)}>
      <div className="flex items-center justify-between px-1 pb-2">
        <span className="eyebrow">worklist · {examples.length}</span>
        <div className="flex items-center gap-2.5 font-mono text-[0.66rem] tabular-nums">
          {ORDER.map((v) => (
            <span
              key={v}
              className="flex items-center gap-1"
              style={{ color: VERDICT_COLOR[v] }}
              title={v}
            >
              <span className="size-1.5 rounded-full bg-current" />
              {counts[v]}
            </span>
          ))}
        </div>
      </div>

      <div className="flex min-h-0 flex-col gap-1.5 overflow-y-auto pr-1">
        {examples.map((ex) => {
          const score = ex.result?.anomaly_score ?? 0;
          const verdict = ex.result?.verdict ?? "PASS";
          const selected = ex.registry.tile_id === selectedId;
          return (
            <button
              key={ex.registry.tile_id}
              type="button"
              onClick={() => onSelect(ex.registry.tile_id)}
              aria-pressed={selected}
              className={cn(
                "group relative w-full rounded-lg border px-3 py-2.5 text-left transition-all",
                selected
                  ? "border-primary/50 bg-primary/[0.06] shadow-[var(--shadow-soft)]"
                  : "border-border bg-card hover:border-foreground/20 hover:bg-muted/50",
              )}
            >
              <span
                className="absolute inset-y-2 left-0 w-0.5 rounded-full transition-opacity"
                style={{
                  background: VERDICT_COLOR[verdict],
                  opacity: selected ? 1 : 0,
                }}
              />
              <div className="flex items-center justify-between gap-2">
                <ModalityTag modality={ex.registry.modality} />
                <span className="flex items-center gap-1.5 font-mono text-[0.7rem] tabular-nums">
                  <span
                    className="size-1.5 rounded-full"
                    style={{ background: heatColor(Math.max(score, 0.05)) }}
                  />
                  <span style={{ color: VERDICT_COLOR[verdict] }}>
                    {score.toFixed(2)}
                  </span>
                </span>
              </div>
              <p className="mt-1.5 text-sm font-medium leading-tight text-foreground">
                {ex.title}
              </p>
              <p className="mt-0.5 truncate font-mono text-[0.66rem] text-muted-foreground">
                {ex.registry.source_id} · {ex.registry.wafer_id}
              </p>
            </button>
          );
        })}
      </div>
    </div>
  );
}
