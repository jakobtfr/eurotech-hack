"use client";

import { ChevronLeftIcon, ChevronRightIcon, PauseIcon, PlayIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import type { DemoStep } from "./demo-steps";

interface DemoNarrationProps {
  step: DemoStep;
  index: number;
  total: number;
  autoplay: boolean;
  isLast: boolean;
  onPrev: () => void;
  onNext: () => void;
  onToggle: () => void;
}

export function DemoNarration({
  step,
  index,
  total,
  autoplay,
  isLast,
  onPrev,
  onNext,
  onToggle,
}: DemoNarrationProps) {
  const progressSegments = Array.from({ length: total }, (_, i) => ({
    id: `progress-step-${i + 1}`,
    isComplete: i <= index,
  }));

  return (
    <div className="rounded-xl border border-border bg-card p-5 shadow-[var(--shadow-soft)]">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <p className="font-mono text-[0.66rem] uppercase tracking-[0.2em] text-primary">
            {step.kicker}
          </p>
          <h2 className="mt-1.5 font-display text-xl font-bold tracking-tight text-foreground">
            {step.title}
          </h2>
          <p className="mt-2 max-w-2xl text-sm leading-relaxed text-muted-foreground">
            {step.narration}
          </p>
        </div>

        <div className="flex shrink-0 items-center gap-1.5">
          <Button
            variant="outline"
            size="icon"
            onClick={onPrev}
            disabled={index === 0}
            aria-label="Previous step"
          >
            <ChevronLeftIcon />
          </Button>
          <Button
            variant={autoplay ? "secondary" : "default"}
            size="icon"
            onClick={onToggle}
            disabled={isLast}
            aria-label={autoplay ? "Pause" : "Play"}
          >
            {autoplay ? <PauseIcon /> : <PlayIcon />}
          </Button>
          <Button
            variant="outline"
            size="icon"
            onClick={onNext}
            disabled={isLast}
            aria-label="Next step"
          >
            <ChevronRightIcon />
          </Button>
        </div>
      </div>

      {/* progress segments */}
      <div className="mt-4 flex items-center gap-1.5">
        {progressSegments.map((segment) => (
          <span
            key={segment.id}
            className={cn(
              "h-1 flex-1 rounded-full transition-colors",
              segment.isComplete ? "bg-primary" : "bg-border",
            )}
          />
        ))}
        <span className="ml-2 shrink-0 font-mono text-[0.66rem] tabular-nums text-muted-foreground">
          {index + 1}/{total}
        </span>
      </div>
    </div>
  );
}
