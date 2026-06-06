"use client";

import { useCallback, useEffect, useState } from "react";
import { DEMO_STEPS } from "@/components/demo/demo-steps";

const STEP_COUNT = DEMO_STEPS.length;

export function useDemoStepper() {
  const [index, setIndex] = useState(0);
  const [autoplay, setAutoplay] = useState(false);

  const total = STEP_COUNT;
  const step = DEMO_STEPS[index];
  const isLast = index === total - 1;

  const goTo = useCallback((i: number) => {
    setAutoplay(false);
    setIndex(Math.max(0, Math.min(STEP_COUNT - 1, i)));
  }, []);

  const next = useCallback(() => {
    setAutoplay(false);
    setIndex((i) => Math.min(STEP_COUNT - 1, i + 1));
  }, []);

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
