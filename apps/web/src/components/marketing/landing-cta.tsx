import { ArrowRightIcon } from "lucide-react";
import Link from "next/link";
import { Reveal } from "./reveal";

export function LandingCta() {
  return (
    <section className="mx-auto w-full max-w-7xl px-6 pb-24">
      <Reveal>
        <div className="relative overflow-hidden rounded-2xl bg-foreground px-8 py-16 text-background sm:px-14">
          {/* faint instrument arc */}
          <div
            aria-hidden
            className="pointer-events-none absolute -right-24 -top-24 size-72 rounded-full opacity-20 blur-2xl"
            style={{
              background: "radial-gradient(circle, var(--primary), transparent 70%)",
            }}
          />
          <div className="relative flex flex-col items-start gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-xl">
              <p className="font-mono text-[0.7rem] uppercase tracking-[0.2em] text-background/60">
                ready when you are
              </p>
              <h2 className="mt-3 font-display text-3xl font-bold tracking-tight sm:text-4xl">
                See it run.
              </h2>
              <p className="mt-3 text-background/70">
                Walk the four-minute guided path, or open the workbench and probe the
                tiles yourself. Everything runs offline from pre-rendered artifacts.
              </p>
            </div>
            <div className="flex flex-wrap items-center gap-3">
              <Link
                href="/demo"
                className="inline-flex h-11 items-center gap-2 rounded-lg bg-primary px-5 text-[0.95rem] font-medium text-primary-foreground transition-colors hover:bg-primary/90"
              >
                Run the guided demo <ArrowRightIcon className="size-4" />
              </Link>
              <Link
                href="/workbench"
                className="inline-flex h-11 items-center rounded-lg border border-background/25 px-5 text-[0.95rem] font-medium text-background transition-colors hover:bg-background/10"
              >
                Open the workbench
              </Link>
            </div>
          </div>
        </div>
      </Reveal>
    </section>
  );
}
