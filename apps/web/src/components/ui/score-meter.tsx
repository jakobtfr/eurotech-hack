import * as React from "react";
import { cn } from "@/lib/utils";
import { clamp } from "@/lib/viz/seeded-random";

interface ScoreMeterProps extends React.ComponentProps<"div"> {
  score: number;
  reviewAt: number;
  rejectAt: number;
  showValue?: boolean;
}

export function ScoreMeter({
  score,
  reviewAt,
  rejectAt,
  showValue = true,
  className,
  ...props
}: ScoreMeterProps) {
  const f = clamp(score);
  return (
    <div
      data-slot="score-meter"
      className={cn("flex items-center gap-2", className)}
      {...props}
    >
      <div className="relative h-2 flex-1 overflow-hidden rounded-full bg-muted ring-1 ring-inset ring-border">
        <div
          className="h-full rounded-full transition-[width] duration-700 ease-out"
          style={{
            width: `${f * 100}%`,
            background:
              "linear-gradient(90deg, var(--heat-0), var(--heat-35), var(--heat-70), var(--heat-100))",
            backgroundSize: `${100 / Math.max(f, 0.001)}% 100%`,
          }}
        />
        {/* threshold ticks */}
        <span
          className="absolute top-0 h-full w-px bg-background/80"
          style={{ left: `${reviewAt * 100}%` }}
        />
        <span
          className="absolute top-0 h-full w-px bg-background/80"
          style={{ left: `${rejectAt * 100}%` }}
        />
      </div>
      {showValue && (
        <span className="w-9 shrink-0 text-right font-mono text-xs tabular-nums text-foreground">
          {f.toFixed(2)}
        </span>
      )}
    </div>
  );
}
