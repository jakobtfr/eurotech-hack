"use client";

import { ArrowRightIcon } from "lucide-react";
import { motion } from "motion/react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ModalityTag } from "@/components/ui/modality-tag";
import { VerdictBadge } from "@/components/ui/verdict-badge";
import { OverlayCompositor } from "@/components/viz/overlay-compositor";
import { requireExampleWithVerdict } from "@/lib/mock/selectors";

const CHIPS = ["offline", "source-traceable", "few-shot", "training-free"];

const ease = [0.22, 1, 0.36, 1] as const;

export function Hero() {
  const hold = requireExampleWithVerdict("HOLD");
  const score = hold.result?.anomaly_score ?? 0;

  return (
    <section className="relative overflow-hidden">
      <div className="mx-auto grid w-full max-w-7xl items-center gap-16 px-6 py-20 lg:grid-cols-[1.05fr_0.95fr] lg:py-28">
        {/* Left: copy */}
        <div>
          <motion.p
            className="eyebrow"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, ease }}
          >
            Few-shot semiconductor inspection
          </motion.p>

          <motion.h1
            className="mt-5 font-display text-5xl font-bold leading-[0.98] tracking-tight text-foreground sm:text-6xl lg:text-[4.25rem]"
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.05, ease }}
          >
            Few normal tiles in.
            <br />
            Every anomaly
            <span className="relative whitespace-nowrap">
              {" "}
              mapped out
              <span className="absolute -bottom-1 left-1 right-0 h-[3px] bg-primary" />
            </span>
            .
          </motion.h1>

          <motion.p
            className="mt-6 max-w-xl text-base leading-relaxed text-muted-foreground sm:text-lg"
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.12, ease }}
          >
            An open inspection workbench for silicon-carbide imagery. It turns a handful
            of known-good tiles into heatmaps, risk maps, and review decisions — and
            shows exactly what is proxy-validated versus what stays qualitative.
          </motion.p>

          <motion.div
            className="mt-8 flex flex-wrap items-center gap-3"
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.19, ease }}
          >
            <Button asChild size="lg" className="h-11 px-5 text-[0.95rem]">
              <Link href="/demo">
                Run the guided demo <ArrowRightIcon />
              </Link>
            </Button>
            <Button
              asChild
              variant="outline"
              size="lg"
              className="h-11 px-5 text-[0.95rem]"
            >
              <Link href="/workbench">Open the workbench</Link>
            </Button>
          </motion.div>

          <motion.div
            className="mt-10 flex flex-wrap items-center gap-x-5 gap-y-2 font-mono text-[0.72rem] text-muted-foreground"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.3 }}
          >
            {CHIPS.map((c, i) => (
              <span key={c} className="flex items-center gap-5">
                {i > 0 && <span className="text-border">/</span>}
                <span>{c}</span>
              </span>
            ))}
          </motion.div>
        </div>

        {/* Right: layered plate showpiece */}
        <motion.div
          className="relative mx-auto w-full max-w-md"
          initial={{ opacity: 0, scale: 0.96, y: 16 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.15, ease }}
        >
          <OverlayCompositor example={hold} />

          {/* floating modality chip */}
          <div className="absolute -right-3 -top-4 flex items-center gap-2 rounded-lg border border-border bg-card px-3 py-2 shadow-[var(--shadow-card)]">
            <ModalityTag modality={hold.registry.modality} />
            <span className="font-mono text-[0.66rem] text-muted-foreground">
              {hold.registry.wafer_id}
            </span>
          </div>

          {/* floating decision chip */}
          <div className="absolute -bottom-6 -left-5 flex items-center gap-3.5 rounded-xl border border-border bg-card px-4 py-3 shadow-[var(--shadow-lift)]">
            <span className="font-display text-3xl font-bold tabular-nums text-foreground">
              {score.toFixed(2)}
            </span>
            <span className="h-9 w-px bg-border" />
            <div className="flex flex-col gap-1">
              <VerdictBadge verdict={hold.result?.verdict ?? "HOLD"} />
              <span className="font-mono text-[0.66rem] text-muted-foreground">
                {hold.title.toLowerCase()}
              </span>
            </div>
          </div>
        </motion.div>
      </div>

      <div className="mx-auto max-w-7xl px-6">
        <div className="rule" />
      </div>
    </section>
  );
}
