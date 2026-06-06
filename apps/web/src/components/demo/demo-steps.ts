import { requireExampleWithVerdict } from "@/lib/mock/selectors";
import type { DemoManifest } from "@/lib/types";

export type DemoView = "intro" | "risk-map" | "inspect" | "evidence" | "research";

export interface DemoStep {
  id: string;
  kicker: string;
  title: string;
  narration: string;
  view: DemoView;
  focusExampleId?: string;
  highlightTileId?: string;
  dwellMs: number;
}

export function buildDemoSteps(manifest: DemoManifest): DemoStep[] {
  const pass = requireExampleWithVerdict(manifest, "PASS").registry.tile_id;
  const review = requireExampleWithVerdict(manifest, "REVIEW").registry.tile_id;
  const hold = requireExampleWithVerdict(manifest, "HOLD").registry.tile_id;

  return [
    {
      id: "intro",
      kicker: "01 · Setup",
      title: "Scarcity is the starting point",
      narration:
        "Inspection starts with scarcity — a few known-good tiles and no catalog of defects. Watch the workbench turn that into a defect map, a wafer risk overview, and a review decision you can defend.",
      view: "intro",
      dwellMs: 9000,
    },
    {
      id: "risk-map",
      kicker: "02 · Overview",
      title: "Start at the wafer",
      narration:
        "Every tile is scored against the normal support set; colour encodes the anomaly score. One cluster runs hot — that's where a reviewer looks first. The marked tiles carry a full result.",
      view: "risk-map",
      highlightTileId: hold,
      dwellMs: 11000,
    },
    {
      id: "inspect-pass",
      kicker: "03 · Clean tile",
      title: "A tile that passes",
      narration:
        "Here the residual heatmap stays cold, the score sits well below the review threshold, and the decision is PASS — no human needed. This is what 'normal' looks like to the model.",
      view: "inspect",
      focusExampleId: pass,
      dwellMs: 10000,
    },
    {
      id: "inspect-review",
      kicker: "04 · Anomaly",
      title: "A tile that needs review",
      narration:
        "A particle residue breaks the lattice. The heatmap localises it, a contour rings the region, the score crosses the review line — and the tile is routed to a human as REVIEW with a semantic hint.",
      view: "inspect",
      focusExampleId: review,
      dwellMs: 12000,
    },
    {
      id: "evidence",
      kicker: "05 · Evidence",
      title: "Nothing claimed without provenance",
      narration:
        "Image metrics are proxy-validated on labelled SEM data. Pixel PRO and any SiC metric are withheld until aligned masks and labelled SiC data exist — shown as gated, not faked.",
      view: "evidence",
      dwellMs: 11000,
    },
    {
      id: "research",
      kicker: "06 · Honesty",
      title: "What transfers, and what doesn't",
      narration:
        "SubspaceAD is the executable baseline, FoundAD the research headline, and the SEM→SiC domain gap is stated plainly. We show what transfers from proxy data and what still needs labelled SiC.",
      view: "research",
      dwellMs: 10000,
    },
  ];
}
