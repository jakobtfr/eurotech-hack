import { FlaskConicalIcon, LayersIcon, LockIcon, MicroscopeIcon } from "lucide-react";
import type * as React from "react";
import type { CaveatKind } from "@/lib/types";
import { cn } from "@/lib/utils";

const META: Record<
  CaveatKind,
  { icon: React.ElementType; className: string; short: string }
> = {
  "proxy metric": {
    icon: FlaskConicalIcon,
    className: "border-chart-1/30 bg-chart-1/10 text-chart-1",
    short: "Proxy-validated metric (SEM)",
  },
  "SiC qualitative": {
    icon: MicroscopeIcon,
    className: "border-chart-2/30 bg-chart-2/10 text-chart-2",
    short: "SiC transfer — qualitative only",
  },
  "synthetic montage": {
    icon: LayersIcon,
    className: "border-chart-3/30 bg-chart-3/10 text-chart-3",
    short: "Synthetic montage — concept view",
  },
  "restricted source": {
    icon: LockIcon,
    className: "border-chart-4/30 bg-chart-4/10 text-chart-4",
    short: "Restricted / proprietary source",
  },
};

interface CaveatBadgeProps extends React.ComponentProps<"span"> {
  kind: CaveatKind;
  long?: boolean;
}

export function CaveatBadge({ kind, long, className, ...props }: CaveatBadgeProps) {
  const meta = META[kind];
  const Icon = meta.icon;
  return (
    <span
      data-slot="caveat-badge"
      data-caveat={kind}
      title={meta.short}
      className={cn(
        "inline-flex w-fit shrink-0 items-center gap-1.5 rounded-full border px-2 py-0.5 font-mono text-[0.68rem] tracking-wide [&>svg]:size-3",
        meta.className,
        className,
      )}
      {...props}
    >
      <Icon aria-hidden />
      {long ? meta.short : kind}
    </span>
  );
}
