import { Reveal } from "./reveal";
import { SectionIntro } from "./section-intro";

const POINTS = [
  {
    index: "i",
    title: "Defects are rare",
    body: "Only a handful of labelled examples exist per failure mode. Supervised detectors overfit — or never have enough to start.",
  },
  {
    index: "ii",
    title: "No catalog to learn from",
    body: "There is no public SiC defect benchmark. Teams can't pretrain on the very thing they need to find on the line.",
  },
  {
    index: "iii",
    title: "Labels cost a wafer",
    body: "PL dislocation signatures are often confirmed only by destructive KOH etching, so ground truth is scarce and expensive.",
  },
];

export function ScarceLabelProblem() {
  return (
    <section className="mx-auto w-full max-w-7xl px-6 py-20 lg:py-24">
      <div className="grid gap-12 lg:grid-cols-[0.85fr_1.15fr] lg:gap-16">
        <Reveal>
          <SectionIntro
            index="01"
            eyebrow="The problem"
            title={
              <>
                Labels are the bottleneck,
                <br className="hidden sm:block" /> not the model.
              </>
            }
          />
        </Reveal>

        <Reveal delay={0.1}>
          <div className="grid overflow-hidden rounded-xl border border-border bg-border sm:grid-cols-3 sm:gap-px">
            {POINTS.map((p) => (
              <div key={p.index} className="flex flex-col gap-3 bg-card p-6">
                <span className="font-mono text-sm text-primary">{p.index}</span>
                <h3 className="font-display text-lg font-semibold text-foreground">
                  {p.title}
                </h3>
                <p className="text-sm leading-relaxed text-muted-foreground">
                  {p.body}
                </p>
              </div>
            ))}
          </div>
        </Reveal>
      </div>
    </section>
  );
}
