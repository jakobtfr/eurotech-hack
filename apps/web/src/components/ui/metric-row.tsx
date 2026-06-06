import * as React from "react";
import { LockIcon } from "lucide-react";
import type { EvidenceMetric } from "@/lib/types";
import { cn } from "@/lib/utils";

function formatValue(metric: EvidenceMetric): string {
  if (metric.value === null) return "—";
  switch (metric.format) {
    case "percent":
      return `${(metric.value * 100).toFixed(1)}%`;
    case "raw":
      return metric.value.toFixed(2);
    default:
      return metric.value.toFixed(3);
  }
}

function EvidenceChip({ kind }: { kind: EvidenceMetric["evidence_class"] }) {
  return (
    <span
      className={cn(
        "rounded px-1.5 py-0.5 font-mono text-[0.58rem] uppercase tracking-wider",
        kind === "verified"
          ? "bg-verdict-pass/12 text-verdict-pass"
          : "bg-chart-2/12 text-chart-2",
      )}
    >
      {kind}
    </span>
  );
}

export function MetricRow({
  metric,
  className,
  ...props
}: React.ComponentProps<"div"> & { metric: EvidenceMetric }) {
  const gated = metric.value === null || !metric.available;
  return (
    <div
      data-slot="metric-row"
      role="row"
      className={cn(
        "grid grid-cols-[1fr_auto] items-center gap-x-4 gap-y-1 border-b border-border/50 py-3 last:border-b-0",
        className,
      )}
      {...props}
    >
      <div className="flex items-center gap-2">
        <span className="text-sm font-medium text-foreground">{metric.name}</span>
        <EvidenceChip kind={metric.evidence_class} />
      </div>

      <div className="text-right">
        {gated ? (
          <span className="inline-flex items-center gap-1.5 rounded-md border border-dashed border-border bg-muted/30 px-2 py-1 font-mono text-[0.7rem] text-muted-foreground [&>svg]:size-3">
            <LockIcon aria-hidden />
            requires {metric.requires}
          </span>
        ) : (
          <span
            className={cn(
              "font-mono text-xl font-semibold tabular-nums",
              metric.evidence_class === "verified"
                ? "text-foreground"
                : "text-chart-2",
            )}
          >
            {formatValue(metric)}
          </span>
        )}
      </div>

      {metric.note && (
        <p className="col-span-2 font-mono text-[0.68rem] leading-relaxed text-muted-foreground">
          {metric.note}
        </p>
      )}
    </div>
  );
}
