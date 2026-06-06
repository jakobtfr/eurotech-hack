import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

const glowPanelVariants = cva("relative", {
  variants: {
    glow: {
      none: "",
      spectral: "shadow-[var(--shadow-card)]",
      cyan: "shadow-[var(--shadow-soft)]",
      pass: "ring-verdict-pass/30 shadow-[var(--shadow-card)]",
      review: "ring-verdict-review/35 shadow-[var(--shadow-card)]",
      reject: "ring-verdict-reject/35 shadow-[var(--shadow-card)]",
    },
  },
  defaultVariants: { glow: "none" },
});

interface GlowPanelProps
  extends React.ComponentProps<typeof Card>,
    VariantProps<typeof glowPanelVariants> {}

export function GlowPanel({ glow, className, ...props }: GlowPanelProps) {
  return (
    <Card
      data-slot="glow-panel"
      className={cn(glowPanelVariants({ glow }), className)}
      {...props}
    />
  );
}

export { glowPanelVariants };
