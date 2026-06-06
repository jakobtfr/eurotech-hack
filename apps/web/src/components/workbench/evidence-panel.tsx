import { InfoIcon } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { KeyValue } from "@/components/ui/key-value";
import { MetricRow } from "@/components/ui/metric-row";
import { StatCard } from "@/components/ui/stat-card";
import { Sparkline } from "@/components/viz/sparkline";
import type { MetricsManifest } from "@/lib/types";
import { cn } from "@/lib/utils";

interface EvidencePanelProps {
  metrics: MetricsManifest;
  distribution: number[];
  reviewAt: number;
  className?: string;
}

export function EvidencePanel({
  metrics,
  distribution,
  reviewAt,
  className,
}: EvidencePanelProps) {
  return (
    <div className={cn("grid gap-5 lg:grid-cols-[minmax(0,1fr)_19rem]", className)}>
      <Card>
        <CardContent className="flex flex-col gap-4">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div>
              <p className="eyebrow">proxy evaluation</p>
              <p className="mt-1 font-mono text-sm text-foreground">
                {metrics.dataset}
              </p>
            </div>
            <span className="font-mono text-[0.7rem] text-muted-foreground">
              {metrics.split} split · {metrics.k_shot}-shot · {metrics.image_res}px
            </span>
          </div>

          <div className="flex items-start gap-2.5 rounded-lg border border-chart-2/25 bg-chart-2/5 px-3 py-2.5 text-[0.78rem] leading-relaxed text-muted-foreground">
            <InfoIcon className="mt-0.5 size-4 shrink-0 text-chart-2" />
            <p>{metrics.framing}</p>
          </div>

          <table className="w-full border-collapse">
            <thead>
              <tr className="border-b border-border font-mono text-[0.66rem] uppercase tracking-wider text-muted-foreground">
                <th className="pb-2 text-left font-medium">metric</th>
                <th className="pb-2 text-right font-medium">value</th>
              </tr>
            </thead>
            <tbody>
              {metrics.metrics.map((m) => (
                <MetricRow key={m.name} metric={m} />
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>

      <div className="flex flex-col gap-3">
        <div className="grid grid-cols-2 gap-3">
          <StatCard
            label="model"
            value="DINOv2/PCA"
            sublabel="training-free"
          />
          <StatCard
            label="support"
            value={`${metrics.k_shot}-shot`}
            sublabel="normal tiles"
          />
        </div>

        <Card size="sm">
          <CardContent className="flex flex-col gap-2">
            <span className="eyebrow">score distribution</span>
            <Sparkline values={distribution} threshold={reviewAt} />
            <p className="font-mono text-[0.66rem] text-muted-foreground">
              {distribution.length} demo tiles · dashed = review threshold{" "}
              {reviewAt.toFixed(2)}
            </p>
          </CardContent>
        </Card>

        <Card size="sm">
          <CardContent className="flex flex-col">
            <span className="eyebrow pb-1">run artifacts</span>
            <KeyValue label="run dir" value={metrics.run_dir.split("/").pop()} />
            <KeyValue label="config" value="config.yaml" />
            <KeyValue label="dataset" value={metrics.dataset} />
            <KeyValue label="model" value={metrics.model} />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
