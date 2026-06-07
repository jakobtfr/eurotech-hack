import { CardContent } from "@/components/ui/card";
import { CaveatBadge } from "@/components/ui/caveat-badge";
import { GlowPanel } from "@/components/ui/glow-panel";
import { ModalityTag } from "@/components/ui/modality-tag";
import { LicenseTag } from "@/components/ui/provenance-tag";
import { VerdictBadge } from "@/components/ui/verdict-badge";
import { ScoreGauge } from "@/components/viz/score-gauge";
import { tileDisplayName } from "@/lib/tile-name";
import type { DemoExample, Verdict } from "@/lib/types";
import { cn } from "@/lib/utils";

const GLOW = { PASS: "pass", REVIEW: "review", HOLD: "hold" } as const;

const VERDICT_COLOR: Record<Verdict, string> = {
  PASS: "var(--verdict-pass)",
  REVIEW: "var(--verdict-review)",
  HOLD: "var(--verdict-hold)",
};

interface ReadoutPanelProps {
  example: DemoExample;
  reviewAt: number;
  holdAt: number;
  className?: string;
}

function Fact({
  label,
  value,
  tone,
  wrap,
  small,
}: {
  label: string;
  value: string;
  tone?: string;
  wrap?: boolean;
  small?: boolean;
}) {
  return (
    <div className="flex min-w-0 flex-col gap-0.5">
      <dt className="font-mono text-[0.6rem] uppercase tracking-[0.16em] text-muted-foreground">
        {label}
      </dt>
      <dd
        className={cn(
          "font-medium",
          small ? "text-[0.75rem]" : "text-[0.82rem]",
          wrap ? "break-words" : "truncate",
        )}
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
  const name = tileDisplayName(registry);

  return (
    <GlowPanel glow={GLOW[verdict]} className={cn("h-fit", className)}>
      <CardContent className="flex flex-col gap-5">
        {/* header */}
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <p className="eyebrow">decision</p>
            <h3 className="mt-1 truncate font-display text-lg font-semibold leading-tight">
              {name.primary}
            </h3>
            <p className="mt-0.5 truncate text-[0.7rem] text-muted-foreground">
              {name.secondary}
            </p>
          </div>
          <VerdictBadge verdict={verdict} glow />
        </div>

        {/* score + headline findings */}
        <div className="flex items-center gap-5">
          <div className="flex flex-col items-center gap-1.5">
            <ScoreGauge
              score={score}
              reviewAt={reviewAt}
              holdAt={holdAt}
              size={132}
              color={VERDICT_COLOR[verdict]}
              tintValue
            />
            <span className="font-mono text-[0.6rem] text-muted-foreground">
              review {reviewAt.toFixed(2)} · hold {holdAt.toFixed(2)}
            </span>
          </div>
          <dl className="flex flex-1 flex-col gap-3">
            <Fact label="ground truth" value={registry.source_label ?? "unlabeled"} />
            <Fact label="region" value={result?.region_tag ?? "none localized"} wrap />
            {result?.semantic_hint && (
              <Fact label="hint" value={result.semantic_hint} tone="var(--chart-2)" wrap />
            )}
          </dl>
        </div>

        <div className="rule" />

        {/* provenance — demoted */}
        <div className="flex flex-col gap-2.5 text-muted-foreground">
          <div className="flex items-center justify-between">
            <span className="eyebrow">provenance</span>
            <div className="flex items-center gap-2">
              <ModalityTag modality={registry.modality} />
              <LicenseTag status={registry.license_status} />
            </div>
          </div>
          <dl className="grid grid-cols-2 gap-x-4 gap-y-2.5 text-foreground">
            <Fact label="source" value={registry.source_id} small />
            <Fact label="wafer" value={registry.wafer_id} small />
            <Fact label="support" value={`${example.k_shot}-shot`} small />
            <Fact label="preprocess" value={registry.preprocess ?? "—"} small />
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
