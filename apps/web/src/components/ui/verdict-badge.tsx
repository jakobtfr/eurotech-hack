import { cva, type VariantProps } from "class-variance-authority";
import { CircleCheckIcon, OctagonXIcon, TriangleAlertIcon } from "lucide-react";
import type * as React from "react";
import type { Verdict } from "@/lib/types";
import { cn } from "@/lib/utils";

const verdictBadgeVariants = cva(
  "inline-flex w-fit shrink-0 items-center gap-1.5 rounded-md border px-2 py-0.5 font-mono text-xs font-semibold uppercase tracking-wider [&>svg]:size-3.5",
  {
    variants: {
      verdict: {
        PASS: "border-verdict-pass/35 bg-verdict-pass/10 text-verdict-pass",
        REVIEW: "border-verdict-review/35 bg-verdict-review/10 text-verdict-review",
        HOLD: "border-verdict-hold/40 bg-verdict-hold/12 text-verdict-hold",
      },
      glow: { true: "", false: "" },
    },
    compoundVariants: [
      { verdict: "PASS", glow: true, className: "ring-1 ring-verdict-pass/30" },
      { verdict: "REVIEW", glow: true, className: "ring-1 ring-verdict-review/35" },
      { verdict: "HOLD", glow: true, className: "ring-1 ring-verdict-hold/35" },
    ],
    defaultVariants: { verdict: "PASS", glow: false },
  },
);

const ICONS: Record<Verdict, React.ElementType> = {
  PASS: CircleCheckIcon,
  REVIEW: TriangleAlertIcon,
  HOLD: OctagonXIcon,
};

interface VerdictBadgeProps
  extends Omit<React.ComponentProps<"span">, "children">,
    Omit<VariantProps<typeof verdictBadgeVariants>, "verdict"> {
  verdict: Verdict;
  showIcon?: boolean;
}

export function VerdictBadge({
  verdict,
  glow,
  showIcon = true,
  className,
  ...props
}: VerdictBadgeProps) {
  const Icon = ICONS[verdict];
  return (
    <span
      data-slot="verdict-badge"
      data-verdict={verdict}
      className={cn(verdictBadgeVariants({ verdict, glow }), className)}
      {...props}
    >
      {showIcon && <Icon aria-hidden />}
      {verdict}
    </span>
  );
}

export { verdictBadgeVariants };
