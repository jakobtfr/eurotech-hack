"use client";

import { CheckIcon } from "lucide-react";
import { cn } from "@/lib/utils";
import type { DemoStep } from "./demo-steps";

interface StepperRailProps {
  steps: DemoStep[];
  activeIndex: number;
  onSelect: (i: number) => void;
}

export function StepperRail({ steps, activeIndex, onSelect }: StepperRailProps) {
  return (
    <ol className="relative flex flex-col gap-1">
      {steps.map((step, i) => {
        const done = i < activeIndex;
        const active = i === activeIndex;
        return (
          <li key={step.id} className="relative">
            {i < steps.length - 1 && (
              <span
                className={cn(
                  "absolute left-[0.8125rem] top-7 h-[calc(100%-0.5rem)] w-px",
                  done ? "bg-primary/50" : "bg-border",
                )}
              />
            )}
            <button
              type="button"
              onClick={() => onSelect(i)}
              className={cn(
                "group flex w-full items-start gap-3 rounded-lg px-2 py-2 text-left transition-colors",
                active ? "bg-muted/60" : "hover:bg-muted/40",
              )}
            >
              <span
                className={cn(
                  "mt-0.5 grid size-[1.625rem] shrink-0 place-items-center rounded-full border font-mono text-[0.7rem] tabular-nums transition-colors",
                  active
                    ? "border-primary bg-primary text-primary-foreground"
                    : done
                      ? "border-primary/50 bg-primary/10 text-primary"
                      : "border-border bg-card text-muted-foreground",
                )}
              >
                {done ? <CheckIcon className="size-3.5" /> : i + 1}
              </span>
              <span className="min-w-0 flex-1">
                <span
                  className={cn(
                    "block text-[0.8rem] font-medium leading-tight",
                    active ? "text-foreground" : "text-muted-foreground",
                  )}
                >
                  {step.title}
                </span>
                <span className="mt-0.5 block font-mono text-[0.62rem] uppercase tracking-wider text-muted-foreground/70">
                  {step.kicker}
                </span>
              </span>
            </button>
          </li>
        );
      })}
    </ol>
  );
}
