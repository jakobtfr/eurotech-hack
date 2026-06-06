import { CheckCircleIcon, CircleDashedIcon } from "lucide-react";
import type { CaveatKind } from "@/lib/types";
import { Reveal } from "./reveal";
import { SectionIntro } from "./section-intro";
import { CaveatBadge } from "@/components/ui/caveat-badge";

const CAVEATS: { kind: CaveatKind; note: string }[] = [
  { kind: "proxy metric", note: "Validated on SEM proxy data with real labels." },
  { kind: "SiC qualitative", note: "Transfer to SiC shown as hints, not scored." },
  { kind: "synthetic montage", note: "Assembled view — not true wafer coordinates." },
  { kind: "restricted source", note: "Proprietary / licence-restricted imagery." },
];

export function HonestFraming() {
  return (
    <section className="mx-auto w-full max-w-7xl px-6 py-20 lg:py-24">
      <Reveal>
        <SectionIntro
          index="03"
          eyebrow="What's verified"
          title="We separate proof from promise."
        />
      </Reveal>

      <div className="mt-12 grid gap-5 md:grid-cols-2">
        <Reveal delay={0.05}>
          <div className="flex h-full flex-col gap-4 rounded-xl border border-verdict-pass/30 bg-card p-7 shadow-[var(--shadow-soft)]">
            <div className="flex items-center gap-2 text-verdict-pass">
              <CheckCircleIcon className="size-4" />
              <span className="font-mono text-[0.7rem] uppercase tracking-[0.18em]">
                proxy-validated
              </span>
            </div>
            <div className="flex items-end gap-3">
              <span className="font-display text-5xl font-bold tabular-nums text-foreground">
                0.94
              </span>
              <span className="pb-1.5 font-mono text-[0.72rem] text-muted-foreground">
                image AUROC
                <br />
                MIIC SEM · 4-shot
              </span>
            </div>
            <p className="text-sm leading-relaxed text-muted-foreground">
              On the SEM proxy with real labels and a fixed split, the workbench
              produces metric-bearing results we can defend.
            </p>
            <CaveatBadge kind="proxy metric" className="mt-auto" />
          </div>
        </Reveal>

        <Reveal delay={0.12}>
          <div className="flex h-full flex-col gap-4 rounded-xl border border-border bg-card p-7 shadow-[var(--shadow-soft)]">
            <div className="flex items-center gap-2 text-chart-2">
              <CircleDashedIcon className="size-4" />
              <span className="font-mono text-[0.7rem] uppercase tracking-[0.18em]">
                qualitative transfer
              </span>
            </div>
            <div className="flex items-end gap-3">
              <span className="font-display text-5xl font-bold tabular-nums text-muted-foreground">
                —
              </span>
              <span className="pb-1.5 font-mono text-[0.72rem] text-muted-foreground">
                no SiC labels
                <br />
                heatmaps shown as hints
              </span>
            </div>
            <p className="text-sm leading-relaxed text-muted-foreground">
              SiC PL and etch-pit tiles are shown as heatmap hints only. Without
              labelled SiC data we make no accuracy claim — and we say so.
            </p>
            <div className="mt-auto flex flex-wrap gap-1.5">
              <CaveatBadge kind="SiC qualitative" />
              <CaveatBadge kind="restricted source" />
            </div>
          </div>
        </Reveal>
      </div>

      <Reveal delay={0.1}>
        <div className="mt-5 grid gap-px overflow-hidden rounded-xl border border-border bg-border sm:grid-cols-2 lg:grid-cols-4">
          {CAVEATS.map((c) => (
            <div key={c.kind} className="flex flex-col gap-2 bg-card p-4">
              <CaveatBadge kind={c.kind} />
              <p className="text-[0.78rem] leading-relaxed text-muted-foreground">
                {c.note}
              </p>
            </div>
          ))}
        </div>
      </Reveal>
    </section>
  );
}
