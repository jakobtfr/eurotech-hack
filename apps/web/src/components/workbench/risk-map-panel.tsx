import { ArrowRightIcon } from "lucide-react";
import type { RiskMap } from "@/lib/types";
import { cn } from "@/lib/utils";
import { Card, CardContent } from "@/components/ui/card";
import { StatCard } from "@/components/ui/stat-card";
import { Button } from "@/components/ui/button";
import { ProvenanceTag } from "@/components/ui/provenance-tag";
import { VerdictBadge } from "@/components/ui/verdict-badge";
import { ModalityTag } from "@/components/ui/modality-tag";
import { WaferRiskMap } from "@/components/viz/wafer-risk-map";
import { getExample } from "@/lib/mock/selectors";

interface RiskMapPanelProps {
  riskMap: RiskMap;
  selectedTileId?: string | null;
  highlightTileId?: string | null;
  onSelectTile?: (id: string) => void;
  onOpenInspect?: (id: string) => void;
  className?: string;
}

export function RiskMapPanel({
  riskMap,
  selectedTileId,
  highlightTileId,
  onSelectTile,
  onOpenInspect,
  className,
}: RiskMapPanelProps) {
  const focused = selectedTileId ? getExample(selectedTileId) : undefined;
  const { summary } = riskMap;

  return (
    <div className={cn("grid gap-5 lg:grid-cols-[minmax(0,1fr)_20rem]", className)}>
      <Card>
        <CardContent className="flex flex-col gap-4">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div>
              <p className="eyebrow">wafer risk map</p>
              <p className="mt-1 font-mono text-sm text-foreground">
                {riskMap.wafer_id}
              </p>
            </div>
            <ProvenanceTag provenance={riskMap.provenance} />
          </div>
          <WaferRiskMap
            riskMap={riskMap}
            selectedTileId={selectedTileId}
            highlightTileId={highlightTileId}
            onSelectTile={onSelectTile}
          />
        </CardContent>
      </Card>

      <div className="flex flex-col gap-3">
        <div className="grid grid-cols-3 gap-3">
          <StatCard
            label="pass"
            value={summary.pass}
            accent="var(--verdict-pass)"
          />
          <StatCard
            label="review"
            value={summary.review}
            accent="var(--verdict-review)"
          />
          <StatCard
            label="reject"
            value={summary.reject}
            accent="var(--verdict-reject)"
          />
        </div>

        <Card size="sm">
          <CardContent className="flex flex-col gap-2 text-[0.8rem] text-muted-foreground">
            <span className="eyebrow">provenance note</span>
            <p>
              Tiles are a <span className="text-foreground">stitched field</span>{" "}
              assembled from related crops — not true wafer coordinates. Colour
              encodes the per-tile anomaly score.
            </p>
          </CardContent>
        </Card>

        {focused?.result ? (
          <Card size="sm" className="ring-primary/30">
            <CardContent className="flex flex-col gap-3">
              <div className="flex items-center justify-between gap-2">
                <span className="eyebrow">selected tile</span>
                <ModalityTag modality={focused.registry.modality} />
              </div>
              <p className="text-sm font-medium text-foreground">
                {focused.title}
              </p>
              <div className="flex items-center justify-between">
                <VerdictBadge verdict={focused.result.verdict} />
                <span className="font-mono text-sm tabular-nums text-foreground">
                  {focused.result.anomaly_score.toFixed(2)}
                </span>
              </div>
              {onOpenInspect && (
                <Button
                  size="sm"
                  className="w-full"
                  onClick={() => onOpenInspect(focused.registry.tile_id)}
                >
                  Open in Inspect <ArrowRightIcon />
                </Button>
              )}
            </CardContent>
          </Card>
        ) : (
          <Card size="sm">
            <CardContent className="text-[0.8rem] text-muted-foreground">
              Select a marked tile (◷) to inspect its heatmap and verdict.
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
