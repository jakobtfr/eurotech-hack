import type { DemoExample, Verdict } from "@/lib/types";
import { demoManifest } from "./manifest";

export function getExample(tileId: string): DemoExample | undefined {
  return demoManifest.examples.find((e) => e.registry.tile_id === tileId);
}

export function getExampleOrDefault(tileId: string | null | undefined): DemoExample {
  return (
    (tileId ? getExample(tileId) : undefined) ??
    getExample(demoManifest.default_example_id) ??
    demoManifest.examples[0]
  );
}

export function getExamplesByVerdict(verdict: Verdict): DemoExample[] {
  return demoManifest.examples.filter((e) => e.result?.verdict === verdict);
}

export function firstExampleWithVerdict(verdict: Verdict): DemoExample | undefined {
  return demoManifest.examples.find((e) => e.result?.verdict === verdict);
}

export function requireExampleWithVerdict(verdict: Verdict): DemoExample {
  const example = firstExampleWithVerdict(verdict);
  if (!example) {
    throw new Error(`Missing demo example with ${verdict} decision`);
  }
  return example;
}

/** Distribution of anomaly scores across all demo examples (for sparklines). */
export function scoreDistribution(): number[] {
  return demoManifest.examples
    .map((e) => e.result?.anomaly_score ?? 0)
    .sort((a, b) => a - b);
}

export const VERDICT_META: Record<
  Verdict,
  { label: string; tone: "pass" | "review" | "hold"; blurb: string }
> = {
  PASS: {
    label: "Pass",
    tone: "pass",
    blurb: "All tile scores below the review threshold.",
  },
  REVIEW: {
    label: "Review",
    tone: "review",
    blurb: "Localized anomaly or high-uncertainty flag — route to a human.",
  },
  HOLD: {
    label: "Hold",
    tone: "hold",
    blurb: "High-area anomaly or clustered hot tiles — escalate inspection.",
  },
};
