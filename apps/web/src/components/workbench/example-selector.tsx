"use client";

import type { DemoExample } from "@/lib/types";
import { cn } from "@/lib/utils";
import { ModalityTag } from "@/components/ui/modality-tag";
import { heatColor } from "@/lib/viz/heat-ramp";

const VERDICT_COLOR: Record<string, string> = {
  PASS: "var(--verdict-pass)",
  REVIEW: "var(--verdict-review)",
  REJECT: "var(--verdict-reject)",
};

interface ExampleSelectorProps {
  examples: DemoExample[];
  selectedId: string;
  onSelect: (id: string) => void;
  className?: string;
}

export function ExampleSelector({
  examples,
  selectedId,
  onSelect,
  className,
}: ExampleSelectorProps) {
  return (
    <div className={cn("flex flex-col", className)}>
      <div className="flex items-center justify-between px-1 pb-2">
        <span className="eyebrow">support set · {examples.length} tiles</span>
      </div>
      <div className="flex max-h-[34rem] flex-col gap-1.5 overflow-y-auto pr-1">
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
