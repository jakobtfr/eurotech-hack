import { CardContent } from "@/components/ui/card";
import { CaveatBadge } from "@/components/ui/caveat-badge";
import { GlowPanel } from "@/components/ui/glow-panel";
import { ModalityTag } from "@/components/ui/modality-tag";
import { LicenseTag } from "@/components/ui/provenance-tag";
import { VerdictBadge } from "@/components/ui/verdict-badge";
import { ScoreGauge } from "@/components/viz/score-gauge";
import type { DemoExample } from "@/lib/types";
import { cn } from "@/lib/utils";

const GLOW = { PASS: "pass", REVIEW: "review", HOLD: "hold" } as const;

interface ReadoutPanelProps {
  example: DemoExample;
  reviewAt: number;
  holdAt: number;
  className?: string;
}

function Fact({ label, value, tone }: { label: string; value: string; tone?: string }) {
  return (
    <div className="flex min-w-0 flex-col gap-0.5">
      <dt className="font-mono text-[0.6rem] uppercase tracking-[0.16em] text-muted-foreground">
        {label}
      </dt>
      <dd
        className="truncate text-[0.82rem] font-medium"
        style={tone ? { color: tone } : undefined}
      >
        {value}
      </dd>
    </div>
  );
}

export function ReadoutPanel({
  example,
  reviewAt,
  holdAt,
  className,
}: ReadoutPanelProps) {
  const { registry, result } = example;
  const score = result?.anomaly_score ?? 0;
  const verdict = result?.verdict ?? "PASS";

  return (
    <GlowPanel glow={GLOW[verdict]} className={cn("h-fit", className)}>
      <CardContent className="flex flex-col gap-5">
        {/* header */}
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <p className="eyebrow">decision</p>
            <h3 className="mt-1 font-display text-lg font-semibold leading-tight">
              {example.title}
            </h3>
            <p className="mt-0.5 truncate font-mono text-[0.64rem] text-muted-foreground">
              {registry.tile_id}
            </p>
          </div>
          <VerdictBadge verdict={verdict} glow />
        </div>

        {/* gauge + key facts */}
        <div className="flex items-center gap-5">
          <div className="flex flex-col items-center gap-1.5">
            <ScoreGauge score={score} reviewAt={reviewAt} holdAt={holdAt} size={132} />
            <span className="font-mono text-[0.6rem] text-muted-foreground">
              review {reviewAt.toFixed(2)} · hold {holdAt.toFixed(2)}
            </span>
          </div>
          <dl className="flex flex-1 flex-col gap-3">
            <Fact
              label="novelty"
              value={result?.novelty_flag ? "flagged" : "clear"}
              tone={
                result?.novelty_flag ? "var(--verdict-review)" : "var(--verdict-pass)"
              }
            />
            <Fact label="region" value={result?.region_tag ?? "none localized"} />
            {result?.semantic_hint && (
              <Fact label="hint" value={result.semantic_hint} tone="var(--chart-2)" />
            )}
          </dl>
        </div>

        <div className="rule" />

        {/* provenance — curated */}
        <div className="flex flex-col gap-3">
          <div className="flex items-center justify-between">
            <span className="eyebrow">provenance</span>
            <div className="flex items-center gap-2">
              <ModalityTag modality={registry.modality} />
              <LicenseTag status={registry.license_status} />
            </div>
          </div>
          <dl className="grid grid-cols-2 gap-x-4 gap-y-3">
            <Fact label="source" value={registry.source_id} />
            <Fact label="wafer" value={registry.wafer_id} />
            <Fact label="support" value={`${example.k_shot}-shot`} />
            <Fact label="preprocess" value={registry.preprocess ?? "—"} />
          </dl>
          <div className="flex flex-wrap gap-1.5 pt-0.5">
            {example.caveats.map((c) => (
              <CaveatBadge key={c} kind={c} />
            ))}
          </div>
        </div>
      </CardContent>
    </GlowPanel>
  );
}
