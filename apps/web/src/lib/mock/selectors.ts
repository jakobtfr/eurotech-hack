import type { DemoExample, DemoManifest, Verdict } from "@/lib/types";

export function getExample(
  manifest: DemoManifest,
  tileId: string,
): DemoExample | undefined {
  return manifest.examples.find((e) => e.registry.tile_id === tileId);
}

export function getExampleOrDefault(
  manifest: DemoManifest,
  tileId: string | null | undefined,
): DemoExample {
  return (
    (tileId ? getExample(manifest, tileId) : undefined) ??
    getExample(manifest, manifest.default_example_id) ??
    manifest.examples[0]
  );
}

export function getExamplesByVerdict(
  manifest: DemoManifest,
  verdict: Verdict,
): DemoExample[] {
  return manifest.examples.filter((e) => e.result?.verdict === verdict);
}

export function firstExampleWithVerdict(
  manifest: DemoManifest,
  verdict: Verdict,
): DemoExample | undefined {
  return manifest.examples.find((e) => e.result?.verdict === verdict);
}

export function requireExampleWithVerdict(
  manifest: DemoManifest,
  verdict: Verdict,
): DemoExample {
  const example = firstExampleWithVerdict(manifest, verdict);
  if (!example) {
    throw new Error(`Missing demo example with ${verdict} decision`);
  }
  return example;
}

/** Distribution of anomaly scores across all demo examples (for sparklines). */
export function scoreDistribution(manifest: DemoManifest): number[] {
  return manifest.examples
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
