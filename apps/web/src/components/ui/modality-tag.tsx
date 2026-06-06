import type * as React from "react";
import type { Modality } from "@/lib/types";
import { cn } from "@/lib/utils";

const META: Record<Modality, { label: string; className: string }> = {
  SEM: { label: "SEM", className: "text-foreground/80" },
  PL: { label: "PL", className: "text-chart-2" },
  etch: { label: "ETCH", className: "text-chart-4" },
  optical: { label: "OPT", className: "text-chart-5" },
  wafer_map: { label: "WAFER", className: "text-chart-1" },
  synthetic: { label: "SYNTH", className: "text-chart-3" },
  other: { label: "OTHER", className: "text-muted-foreground" },
};

export function ModalityTag({
  modality,
  className,
  ...props
}: React.ComponentProps<"span"> & { modality: Modality }) {
  const meta = META[modality];
  return (
    <span
      data-slot="modality-tag"
      data-modality={modality}
      className={cn(
        "inline-flex items-center rounded border border-border bg-muted/40 px-1.5 py-0.5 font-mono text-[0.62rem] font-semibold tracking-[0.14em]",
        meta.className,
        className,
      )}
      {...props}
    >
      {meta.label}
    </span>
  );
}
