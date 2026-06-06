import { cn } from "@/lib/utils";

/**
 * Fixed, full-viewport instrument backdrop: fine grid + vignette + a faint
 * spectral aurora that anchors the dark "lab" atmosphere behind all content.
 */
export function GridBackdrop({ className }: { className?: string }) {
  return (
    <div
      aria-hidden
      className={cn(
        "pointer-events-none fixed inset-0 -z-10 overflow-hidden",
        className,
      )}
    >
      {/* drifting fine grid */}
      <div className="lab-grid absolute inset-0 animate-drift opacity-70" />
      {/* spectral aurora pools */}
      <div
        className="absolute -top-40 left-[8%] size-[42rem] rounded-full opacity-[0.16] blur-[120px]"
        style={{ background: "radial-gradient(circle, var(--heat-0), transparent 70%)" }}
      />
      <div
        className="absolute -bottom-52 right-[2%] size-[46rem] rounded-full opacity-[0.14] blur-[140px]"
        style={{ background: "radial-gradient(circle, var(--heat-35), transparent 70%)" }}
      />
      {/* vignette */}
      <div className="vignette absolute inset-0" />
    </div>
  );
}
