import type { DemoManifest } from "@/lib/types";
import {
  DEFAULT_EXAMPLE_ID,
  DEMO_EXAMPLES,
  THRESHOLD_REJECT,
  THRESHOLD_REVIEW,
} from "./examples";
import { RISK_MAP } from "./risk-tiles";
import { METRICS } from "./metrics";
import { RESEARCH } from "./research";

/**
 * The single import surface for the whole demo — the literal stand-in for
 * `fetch("/demo/manifest.json")`. Shaped to the artifact contract in
 * planning/output/implementation_plan.md so real model outputs can replace it.
 * `generated_at` is hardcoded (no Date.now) for SSR stability.
 */
export const demoManifest: DemoManifest = {
  version: "0.1.0-demo",
  generated_at: "2026-06-03T10:42:00Z",
  model: "subspacead",
  default_example_id: DEFAULT_EXAMPLE_ID,
  threshold_review: THRESHOLD_REVIEW,
  threshold_reject: THRESHOLD_REJECT,
  examples: DEMO_EXAMPLES,
  risk_map: RISK_MAP,
  metrics: METRICS,
  research: RESEARCH,
};
