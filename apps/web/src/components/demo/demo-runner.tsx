"use client";

import { ArrowRightIcon } from "lucide-react";
import { AnimatePresence, motion } from "motion/react";
import { useState } from "react";
import { VerdictBadge } from "@/components/ui/verdict-badge";
import { OverlayCompositor } from "@/components/viz/overlay-compositor";
import { EvidencePanel } from "@/components/workbench/evidence-panel";
import { InspectPanel } from "@/components/workbench/inspect-panel";
import { ResearchPanel } from "@/components/workbench/research-panel";
import { RiskMapPanel } from "@/components/workbench/risk-map-panel";
import { useDemoStepper } from "@/hooks/use-demo-stepper";
import { artifactUrl } from "@/lib/artifact-url";
import {
  getExampleOrDefault,
  requireExampleWithVerdict,
  scoreDistribution,
} from "@/lib/mock/selectors";
import type { DemoManifest } from "@/lib/types";
import { DemoNarration } from "./demo-narration";
import { buildDemoSteps } from "./demo-steps";
import { StepperRail } from "./stepper-rail";

const REVIEW_STEP = 3; // index of the inspect-review step
const INTRO_POINTS = [
  "Scan the wafer risk map for hot clusters.",
  "Inspect a clean tile, then an anomalous one.",
  "Check the evidence — and what stays qualitative.",
] as const;

function IntroView({ manifest }: { manifest: DemoManifest }) {
  const hold = requireExampleWithVerdict(manifest, "HOLD");
  return (
    <div className="grid items-center gap-8 rounded-xl border border-border bg-card p-7 shadow-[var(--shadow-soft)] lg:grid-cols-[1fr_20rem]">
      <div>
        <p className="font-display text-xl font-semibold leading-snug text-foreground">
          From a handful of known-good tiles to a defect map, a wafer risk overview, and
          a review decision you can defend.
        </p>
        <ol className="mt-6 flex flex-col gap-3">
          {INTRO_POINTS.map((t, i) => (
            <li
              key={t}
              className="flex items-center gap-3 text-sm text-muted-foreground"
            >
              <span className="grid size-6 shrink-0 place-items-center rounded-full bg-primary/10 font-mono text-[0.7rem] text-primary">
                {i + 1}
              </span>
              {t}
            </li>
          ))}
        </ol>
      </div>
      <div className="relative mx-auto w-full max-w-[18rem]">
        <OverlayCompositor
          example={hold}
          rawSrc={artifactUrl(hold.registry.image_path)}
          overlaySrc={artifactUrl(hold.result?.heatmap_path)}
        />
        <div className="absolute -bottom-4 -left-3 flex items-center gap-2 rounded-lg border border-border bg-card px-3 py-2 shadow-[var(--shadow-card)]">
          <span className="font-display text-lg font-bold tabular-nums text-foreground">
            {(hold.result?.anomaly_score ?? 0).toFixed(2)}
          </span>
          <VerdictBadge verdict={hold.result?.verdict ?? "HOLD"} />
        </div>
      </div>
    </div>
  );
}

interface DemoRunnerProps {
  manifest: DemoManifest;
}

export function DemoRunner({ manifest }: DemoRunnerProps) {
  const steps = buildDemoSteps(manifest);
  const { index, step, total, isLast, autoplay, goTo, next, prev, toggleAutoplay } =
    useDemoStepper(steps);
  const [selectedTileId, setSelectedTileId] = useState<string | null>(null);

  function renderView() {
    switch (step.view) {
      case "intro":
        return <IntroView manifest={manifest} />;
      case "risk-map":
        return (
          <RiskMapPanel
            riskMap={manifest.risk_map}
            examples={manifest.examples}
            selectedTileId={selectedTileId}
            highlightTileId={step.highlightTileId}
            onSelectTile={setSelectedTileId}
            onOpenInspect={() => goTo(REVIEW_STEP)}
          />
        );
      case "inspect":
        return (
          <InspectPanel
            example={getExampleOrDefault(manifest, step.focusExampleId)}
            reviewAt={manifest.threshold_review}
            holdAt={manifest.threshold_hold}
          />
        );
      case "evidence":
        return (
          <EvidencePanel
            metrics={manifest.metrics}
            distribution={scoreDistribution(manifest)}
            reviewAt={manifest.threshold_review}
          />
        );
      case "research":
        return <ResearchPanel research={manifest.research} />;
    }
  }

  return (
    <main className="mx-auto w-full max-w-7xl flex-1 px-6 py-8">
      <div className="flex flex-col gap-2 border-b border-border pb-5">
        <p className="eyebrow">guided demo</p>
        <h1 className="font-display text-2xl font-bold tracking-tight">
          The four-minute path
        </h1>
        <p className="max-w-2xl text-sm text-muted-foreground">
          A scripted walk through the workbench — press play to auto-advance, or step
          through it yourself.
        </p>
      </div>

        <div className="mt-8 grid gap-8 lg:grid-cols-[15rem_minmax(0,1fr)]">
        <div className="lg:sticky lg:top-24 lg:self-start">
          <StepperRail steps={steps} activeIndex={index} onSelect={goTo} />
          {isLast && (
            <a
              href="/workbench"
              className="mt-4 inline-flex items-center gap-2 px-2 font-mono text-[0.75rem] text-primary hover:underline"
            >
              explore the workbench <ArrowRightIcon className="size-3.5" />
            </a>
          )}
        </div>

        <div className="flex min-w-0 flex-col gap-5">
          <DemoNarration
            step={step}
            index={index}
            total={total}
            autoplay={autoplay}
            isLast={isLast}
            onPrev={prev}
            onNext={next}
            onToggle={toggleAutoplay}
          />
          <AnimatePresence mode="wait">
            <motion.div
              key={step.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
            >
              {renderView()}
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
    </main>
  );
}
