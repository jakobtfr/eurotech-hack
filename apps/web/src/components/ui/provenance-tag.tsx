import * as React from "react";
import {
  CrosshairIcon,
  LayoutGridIcon,
  LayersIcon,
  ShieldCheckIcon,
  LockIcon,
  CircleHelpIcon,
} from "lucide-react";
import type { SourceRegistryRow, WaferMapProvenance } from "@/lib/types";
import { cn } from "@/lib/utils";

const PROVENANCE_META: Record<
  WaferMapProvenance,
  { icon: React.ElementType; className: string; hint: string }
> = {
  "real spatial": {
    icon: CrosshairIcon,
    className: "border-verdict-pass/30 bg-verdict-pass/10 text-verdict-pass",
    hint: "True wafer / source coordinates exist",
  },
  "stitched field": {
    icon: LayoutGridIcon,
    className: "border-chart-1/30 bg-chart-1/10 text-chart-1",
    hint: "Assembled from related tiles / crops",
  },
  "synthetic montage": {
    icon: LayersIcon,
    className: "border-chart-3/30 bg-chart-3/10 text-chart-3",
    hint: "Product concept visualization",
  },
};

export function ProvenanceTag({
  provenance,
  className,
  ...props
}: React.ComponentProps<"span"> & { provenance: WaferMapProvenance }) {
  const meta = PROVENANCE_META[provenance];
  const Icon = meta.icon;
  return (
    <span
      data-slot="provenance-tag"
      title={meta.hint}
      className={cn(
        "inline-flex w-fit items-center gap-1.5 rounded-md border px-2 py-0.5 font-mono text-[0.68rem] tracking-wide [&>svg]:size-3",
        meta.className,
        className,
      )}
      {...props}
    >
      <Icon aria-hidden />
      {provenance}
    </span>
  );
}

const LICENSE_META: Record<
  SourceRegistryRow["license_status"],
  { icon: React.ElementType; className: string }
> = {
  verified: { icon: ShieldCheckIcon, className: "text-verdict-pass" },
  restricted: { icon: LockIcon, className: "text-verdict-reject" },
  unknown: { icon: CircleHelpIcon, className: "text-muted-foreground" },
};

export function LicenseTag({
  status,
  className,
  ...props
}: React.ComponentProps<"span"> & {
  status: SourceRegistryRow["license_status"];
}) {
  const meta = LICENSE_META[status];
  const Icon = meta.icon;
  return (
    <span
      data-slot="license-tag"
      className={cn(
        "inline-flex items-center gap-1 font-mono text-[0.68rem] tracking-wide [&>svg]:size-3",
        meta.className,
        className,
      )}
      {...props}
    >
      <Icon aria-hidden />
      {status}
    </span>
  );
}
