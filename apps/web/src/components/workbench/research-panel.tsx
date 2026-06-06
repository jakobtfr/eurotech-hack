import type { VariantProps } from "class-variance-authority";
import { CardContent } from "@/components/ui/card";
import { CaveatBadge } from "@/components/ui/caveat-badge";
import { GlowPanel, type glowPanelVariants } from "@/components/ui/glow-panel";
import type { ResearchSection } from "@/lib/types";
import { cn } from "@/lib/utils";

type Glow = VariantProps<typeof glowPanelVariants>["glow"];

const STATUS_STYLE: Record<ResearchSection["status"], { glow: Glow; chip: string }> = {
  "executable baseline": {
    glow: "cyan",
    chip: "border-verdict-pass/30 bg-verdict-pass/10 text-verdict-pass",
  },
  "research headline": {
    glow: "spectral",
    chip: "border-chart-2/30 bg-chart-2/10 text-chart-2",
  },
  "open caveat": {
    glow: "review",
    chip: "border-verdict-review/30 bg-verdict-review/10 text-verdict-review",
  },
};

export function ResearchPanel({
  research,
  className,
}: {
  research: ResearchSection[];
  className?: string;
}) {
  return (
    <div className={cn("grid gap-5 md:grid-cols-3", className)}>
      {research.map((section) => {
        const style = STATUS_STYLE[section.status];
        return (
          <GlowPanel key={section.id} glow={style.glow} className="flex flex-col">
            <CardContent className="flex flex-1 flex-col gap-3">
              <div className="flex items-center justify-between gap-2">
                <span
                  className={cn(
                    "rounded-full border px-2 py-0.5 font-mono text-[0.6rem] uppercase tracking-wider",
                    style.chip,
                  )}
                >
                  {section.status}
                </span>
              </div>

              <div>
                <h3 className="font-display text-xl font-bold tracking-tight">
                  {section.title}
                </h3>
                <p className="mt-1 font-mono text-[0.72rem] text-muted-foreground">
                  {section.tagline}
                </p>
              </div>

              <div className="flex flex-1 flex-col gap-2.5 text-[0.82rem] leading-relaxed text-muted-foreground">
                {section.body.map((p) => (
                  <p key={p}>{p}</p>
                ))}
              </div>

              {section.badges.length > 0 && (
                <div className="flex flex-wrap gap-1.5">
                  {section.badges.map((b) => (
                    <CaveatBadge key={b} kind={b} />
                  ))}
                </div>
              )}

              {section.source_ref && (
                <p className="border-t border-border/50 pt-2.5 font-mono text-[0.62rem] text-muted-foreground/70">
                  {section.source_ref}
                </p>
              )}
            </CardContent>
          </GlowPanel>
        );
      })}
    </div>
  );
}
