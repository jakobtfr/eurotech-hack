import { Reveal } from "./reveal";
import { SectionIntro } from "./section-intro";

const STEPS = [
  {
    n: "01",
    title: "Frozen features",
    body: "Extract DINOv2 patch embeddings from a few known-good tiles. No fine-tuning, no labels — the encoder stays frozen.",
  },
  {
    n: "02",
    title: "Subspace residual",
    body: "Fit a PCA subspace over the normal embeddings, then score every test patch by how far it falls outside that subspace.",
  },
  {
    n: "03",
    title: "Map & route",
    body: "Localise the residual into a heatmap, threshold the score, and route the tile: PASS, REVIEW, or REJECT.",
  },
];

export function HowItWorks() {
  return (
    <section className="border-y border-border bg-card/40">
      <div className="mx-auto w-full max-w-7xl px-6 py-20 lg:py-24">
        <Reveal>
          <SectionIntro
            index="02"
            eyebrow="How it works"
            title="Three steps. No training."
          />
        </Reveal>

        <div className="mt-14 grid gap-px overflow-hidden rounded-xl border border-border bg-border md:grid-cols-3">
          {STEPS.map((s, i) => (
            <Reveal key={s.n} delay={i * 0.08}>
              <div className="flex h-full flex-col gap-4 bg-background p-7">
                <div className="flex items-baseline justify-between">
                  <span className="font-display text-4xl font-bold text-primary">
                    {s.n}
                  </span>
                  <span className="font-mono text-[0.66rem] uppercase tracking-[0.2em] text-muted-foreground">
                    step
                  </span>
                </div>
                <h3 className="font-display text-xl font-semibold text-foreground">
                  {s.title}
                </h3>
                <p className="text-sm leading-relaxed text-muted-foreground">
                  {s.body}
                </p>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
