import { Hero } from "@/components/marketing/hero";
import { HonestFraming } from "@/components/marketing/honest-framing";
import { HowItWorks } from "@/components/marketing/how-it-works";
import { LandingCta } from "@/components/marketing/landing-cta";
import { PitchClaim } from "@/components/marketing/pitch-claim";
import { ScarceLabelProblem } from "@/components/marketing/scarce-label-problem";
import { loadDemoManifest } from "@/lib/demo-manifest";

const teamMembers = [
  {
    name: "Sparsh Tyagi",
    photo: "/team/Sparsh.jpg",
    degree: "Management & Technology",
    title: "BCG FDE, EuroTech fellow, applied AI operator",
  },
  {
    name: "Damia Vicens Ramis",
    photo: "/team/Damia.png",
    degree: "Quantum Systems",
    title: "Fraunhofer researcher, EuroTech & TUM Venture Labs fellow",
  },
  {
    name: "Jakob Friedrich",
    photo: "/team/Jakob.jpg",
    degree: "Computer Science",
    title: "Amazon SWE, TUM.ai software engineering lead",
  },
  {
    name: "Justin Lanfermann",
    photo: "/team/Justin.jpg",
    degree: "Computer Science",
    title: "TUM.ai software engineering lead, experienced fullstack and AI Dev",
  },
];

const logoRail = [
  {
    alt: "TUM",
    src: "/logos/TUM.png",
    className: "max-h-12 max-w-36",
  },
  {
    alt: "TUM.ai",
    src: "/logos/tumai.png",
  },
  {
    alt: "BCG",
    src: "/logos/BCG.png",
  },
  {
    alt: "Amazon",
    src: "/logos/Amazon.png",
  },
  {
    alt: "Fraunhofer",
    src: "/logos/Fraunhofer.png",
  },
  {
    alt: "Celonis",
    src: "/logos/Celonis.png",
  },
  {
    alt: "Allianz",
    src: "/logos/Allianz.png",
  },
  {
    alt: "University of Pennsylvania",
    src: "/logos/UPenn.png",
  },
  {
    alt: "University of Cambridge",
    src: "/logos/Cambridge.png",
  },
  {
    alt: "TUM Venture Labs",
    src: "/logos/TUM Venture labs.png",
  },
];

function TeamSection() {
  return (
    <section className="overflow-hidden border-t border-border bg-background py-16">
      <div className="mx-auto w-full max-w-7xl px-6">
        <div className="flex flex-col gap-3">
          <p className="font-mono text-xs uppercase tracking-[0.28em] text-primary">
            Team
          </p>
          <div className="grid gap-4 lg:grid-cols-[0.9fr_1.1fr] lg:items-end">
            <h2 className="max-w-3xl font-display text-3xl font-semibold tracking-tight text-foreground md:text-5xl">
              TUM builders with AI delivery, CS, quantum systems, and research
              depth.
            </h2>
            <p className="max-w-2xl text-base leading-7 text-muted-foreground">
              The team combines applied AI execution, software engineering
              leadership, semiconductor-relevant research, and investor-ready
              pilot thinking.
            </p>
          </div>
        </div>

        <div className="mt-9 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {teamMembers.map((member) => (
            <article
              className="rounded-lg border border-border bg-card/70 p-5 text-center shadow-sm"
              key={member.name}
            >
              <div className="flex flex-col items-center gap-3">
                <img
                  alt={member.name}
                  className="size-24 shrink-0 rounded-full border border-primary/35 object-cover shadow-sm"
                  src={member.photo}
                />
                <div>
                  <h3 className="font-display text-lg font-semibold text-foreground">
                    {member.name}
                  </h3>
                  <p className="font-mono text-[0.68rem] uppercase tracking-[0.18em] text-muted-foreground">
                    {member.degree}
                  </p>
                </div>
              </div>
              <p className="mx-auto mt-4 min-h-12 max-w-56 text-sm font-medium leading-6 text-foreground">
                {member.title}
              </p>
            </article>
          ))}
        </div>
      </div>

      <div className="mt-10 border-y border-border bg-muted/25 py-4">
        <div className="team-logo-rail flex w-max gap-3 px-6">
          {[...logoRail, ...logoRail].map((logo, index) => (
            <div
              className="flex h-16 min-w-40 items-center justify-center rounded-md border border-border bg-white px-5 shadow-sm"
              key={`${logo.alt}-${index}`}
            >
              <img
                alt={logo.alt}
                className={`${logo.className ?? "max-h-9 max-w-32"} object-contain`}
                src={logo.src}
              />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

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
      <TeamSection />

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
