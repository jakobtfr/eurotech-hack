import { Reveal } from "./reveal";

export function PitchClaim() {
  return (
    <section className="mx-auto w-full max-w-4xl px-6 py-20 lg:py-28">
      <Reveal>
        <figure className="relative">
          <span
            aria-hidden
            className="pointer-events-none absolute -left-2 -top-10 select-none font-display text-[7rem] leading-none text-primary/15"
          >
            &ldquo;
          </span>
          <blockquote className="relative font-display text-2xl font-medium leading-snug tracking-tight text-foreground sm:text-[2rem]">
            We built an open, few-shot semiconductor anomaly workbench that produces
            heatmaps and review decisions from scarce normal examples — while explicitly
            separating <span className="text-primary">proxy-validated evidence</span>{" "}
            from{" "}
            <span className="underline decoration-border decoration-2 underline-offset-4">
              qualitative SiC transfer
            </span>
            .
          </blockquote>
          <figcaption className="mt-6 font-mono text-[0.72rem] uppercase tracking-[0.18em] text-muted-foreground">
            — the claim we can defend
          </figcaption>
        </figure>
      </Reveal>
    </section>
  );
}
