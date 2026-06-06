"use client";

import { ScanSearchIcon, LayoutGridIcon, GaugeIcon, FlaskConicalIcon } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { demoManifest } from "@/lib/mock/manifest";
import { getExampleOrDefault, scoreDistribution } from "@/lib/mock/selectors";
import { useTileSelection, type WorkbenchTab } from "@/hooks/use-tile-selection";
import { InspectPanel } from "./inspect-panel";
import { RiskMapPanel } from "./risk-map-panel";
import { EvidencePanel } from "./evidence-panel";
import { ResearchPanel } from "./research-panel";

const TABS = [
  { value: "inspect", label: "Inspect", Icon: ScanSearchIcon },
  { value: "risk-map", label: "Risk Map", Icon: LayoutGridIcon },
  { value: "evidence", label: "Evidence", Icon: GaugeIcon },
  { value: "research", label: "Research", Icon: FlaskConicalIcon },
] as const;

export function WorkbenchShell() {
  const { selectedId, setSelectedId, tab, setTab, inspect } = useTileSelection();
  const example = getExampleOrDefault(selectedId);

  return (
    <main className="mx-auto w-full max-w-7xl flex-1 px-6 py-8">
      <Tabs
        value={tab}
        onValueChange={(v) => setTab(v as WorkbenchTab)}
        className="flex flex-col gap-6"
      >
        <div className="flex flex-col gap-4 border-b border-border/60 pb-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="eyebrow">inspection workbench</p>
            <h1 className="mt-1.5 font-display text-2xl font-bold tracking-tight">
              Few-shot anomaly review
            </h1>
            <p className="mt-1 max-w-xl text-sm text-muted-foreground">
              Heatmaps and review decisions from scarce normal examples —
              proxy-validated evidence kept separate from qualitative SiC
              transfer.
            </p>
          </div>
          <TabsList variant="line" className="self-start lg:self-auto">
            {TABS.map(({ value, label, Icon }) => (
              <TabsTrigger key={value} value={value}>
                <Icon data-icon="inline-start" />
                {label}
              </TabsTrigger>
            ))}
          </TabsList>
        </div>

        <TabsContent value="inspect">
          <InspectPanel
            example={example}
            examples={demoManifest.examples}
            selectedId={selectedId}
            onSelectExample={setSelectedId}
            reviewAt={demoManifest.threshold_review}
            rejectAt={demoManifest.threshold_reject}
          />
        </TabsContent>

        <TabsContent value="risk-map">
          <RiskMapPanel
            riskMap={demoManifest.risk_map}
            selectedTileId={selectedId}
            onSelectTile={setSelectedId}
            onOpenInspect={inspect}
          />
        </TabsContent>

        <TabsContent value="evidence">
          <EvidencePanel
            metrics={demoManifest.metrics}
            distribution={scoreDistribution()}
            reviewAt={demoManifest.threshold_review}
          />
        </TabsContent>

        <TabsContent value="research">
          <ResearchPanel research={demoManifest.research} />
        </TabsContent>
      </Tabs>
    </main>
  );
}
