"use client";

import { useMemo } from "react";
import { ProvenanceTag } from "@/components/ui/provenance-tag";
import { WaferRiskMap } from "@/components/viz/wafer-risk-map";
import { useTileSelection } from "@/hooks/use-tile-selection";
import { getExampleOrDefault } from "@/lib/mock/selectors";
import type { DemoManifest } from "@/lib/types";
import { ReadoutPanel } from "./readout-panel";
import { TileViewer } from "./tile-viewer";
import { Worklist } from "./worklist";

interface WorkbenchShellProps {
  manifest: DemoManifest;
}

function Meta({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center gap-1.5">
      <span className="text-muted-foreground/70">{label}</span>
      <span className="text-foreground">{value}</span>
    </div>
  );
}

export function WorkbenchShell({ manifest }: WorkbenchShellProps) {
  const {
    risk_map: riskMap,
    threshold_review: reviewAt,
    threshold_hold: holdAt,
  } = manifest;

  // Highest anomaly score first — triage order.
  const queue = useMemo(
    () =>
      [...manifest.examples].sort(
        (a, b) => (b.result?.anomaly_score ?? 0) - (a.result?.anomaly_score ?? 0),
      ),
    [manifest.examples],
  );

  // Open on the highest-risk tile — the reason to look, not the nominal one.
  const { selectedId, setSelectedId } = useTileSelection(
    queue[0]?.registry.tile_id ?? manifest.default_example_id,
  );
  const example = getExampleOrDefault(manifest, selectedId);

  return (
    <main className="mx-auto flex w-full max-w-[90rem] flex-1 flex-col px-4 py-6 lg:px-6">
      {/* context strip */}
      <header className="flex flex-col gap-3 border-b border-border/60 pb-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="eyebrow">inspection workbench</p>
          <h1 className="mt-1.5 font-display text-2xl font-bold tracking-tight">
            Auditable SEM anomaly triage
          </h1>
          <p className="mt-1 max-w-xl text-sm text-muted-foreground">
            {manifest.metrics.framing}
          </p>
        </div>
        <dl className="flex flex-wrap items-center gap-x-5 gap-y-1.5 font-mono text-[0.7rem]">
          <Meta label="wafer" value={riskMap.wafer_id} />
          <Meta label="model" value={manifest.model} />
          <Meta label="review" value={reviewAt.toFixed(2)} />
          <Meta label="hold" value={holdAt.toFixed(2)} />
        </dl>
      </header>

      <div className="mt-5 grid flex-1 items-start gap-5 lg:grid-cols-[16rem_minmax(0,1fr)_22rem]">
        {/* left: worklist + spatial wafer map */}
        <aside className="flex flex-col gap-4">
          <Worklist
            examples={queue}
            selectedId={selectedId}
            onSelect={setSelectedId}
            className="max-h-[22rem]"
          />
          <div className="rule" />
          <div className="flex flex-col gap-2">
            <div className="flex items-center justify-between px-1">
              <span className="eyebrow">wafer map</span>
              <ProvenanceTag provenance={riskMap.provenance} />
            </div>
            <WaferRiskMap
              riskMap={riskMap}
              selectedTileId={selectedId}
              onSelectTile={setSelectedId}
              emphasizeInspected
            />
          </div>
        </aside>

        {/* center: inspection stage — where the defect is */}
        <section className="flex min-w-0 flex-col gap-3">
          <div className="mx-auto flex w-full max-w-[36rem] flex-col gap-3">
            <p className="text-sm text-muted-foreground">{example.caption}</p>
            <TileViewer key={example.registry.tile_id} example={example} />
          </div>
        </section>

        {/* right: readout — the decision */}
        <ReadoutPanel example={example} reviewAt={reviewAt} holdAt={holdAt} />
      </div>
    </main>
  );
}
