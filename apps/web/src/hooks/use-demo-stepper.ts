"use client";

import { useCallback, useEffect, useState } from "react";
import type { DemoStep } from "@/components/demo/demo-steps";

export function useDemoStepper(steps: DemoStep[]) {
  const [index, setIndex] = useState(0);
  const [autoplay, setAutoplay] = useState(false);

  const total = steps.length;
  const step = steps[index] ?? steps[0];
  const isLast = index === total - 1;

  const goTo = useCallback((i: number) => {
    setAutoplay(false);
    setIndex(Math.max(0, Math.min(steps.length - 1, i)));
  }, [steps.length]);

  const next = useCallback(() => {
    setAutoplay(false);
    setIndex((i) => Math.min(steps.length - 1, i + 1));
  }, [steps.length]);

  const prev = useCallback(() => {
    setAutoplay(false);
    setIndex((i) => Math.max(0, i - 1));
  }, []);

  const toggleAutoplay = useCallback(() => setAutoplay((a) => !a), []);

  // Auto-advance while playing; no-op on the last step.
  useEffect(() => {
    if (!autoplay || isLast) return;
    const t = setTimeout(() => setIndex((i) => i + 1), step.dwellMs);
    return () => clearTimeout(t);
  }, [autoplay, isLast, step.dwellMs]);

  return {
    index,
    step,
    total,
    isLast,
    autoplay,
    goTo,
    next,
    prev,
    toggleAutoplay,
  };
}
