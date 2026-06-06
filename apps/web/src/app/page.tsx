import { Hero } from "@/components/marketing/hero";
import { HonestFraming } from "@/components/marketing/honest-framing";
import { HowItWorks } from "@/components/marketing/how-it-works";
import { LandingCta } from "@/components/marketing/landing-cta";
import { PitchClaim } from "@/components/marketing/pitch-claim";
import { ScarceLabelProblem } from "@/components/marketing/scarce-label-problem";
import { loadDemoManifest } from "@/lib/demo-manifest";

export default async function Home() {
  const manifest = await loadDemoManifest();

  return (
    <main className="flex-1">
      <Hero manifest={manifest} />
      <ScarceLabelProblem />
      <HowItWorks />
      <HonestFraming />
      <PitchClaim />
      <LandingCta />

      <footer className="border-t border-border">
        <div className="mx-auto flex w-full max-w-7xl flex-col items-start justify-between gap-3 px-6 py-8 font-mono text-[0.72rem] text-muted-foreground sm:flex-row sm:items-center">
          <span>
            <span className="font-display font-bold tracking-wide text-foreground">
              SUBSTRATE
            </span>{" "}
            — few-shot SiC anomaly workbench
          </span>
          <span>demo build · pre-rendered artifacts · offline</span>
        </div>
      </footer>
    </main>
  );
}
