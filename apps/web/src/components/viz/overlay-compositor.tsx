import type { DemoExample } from "@/lib/types";
import { cn } from "@/lib/utils";
import { TileTexture } from "./tile-texture";
import { AnomalyHeatmap } from "./anomaly-heatmap";
import { ContourRing } from "./contour-ring";

interface OverlayCompositorProps {
  example: DemoExample;
  overlayOpacity?: number;
  showHeatmap?: boolean;
  showContour?: boolean;
  /** Real-PNG swap path (zero UI change). */
  rawSrc?: string;
  overlaySrc?: string;
  className?: string;
}

function Corner({ className }: { className?: string }) {
  return (
    <span
      className={cn("pointer-events-none absolute size-3.5 border-white/35", className)}
    />
  );
}

export function OverlayCompositor({
  example,
  overlayOpacity = 0.7,
  showHeatmap = true,
  showContour = true,
  rawSrc,
  overlaySrc,
  className,
}: OverlayCompositorProps) {
  const { registry, result } = example;
  const score = result?.anomaly_score ?? 0;

  return (
    <div
      className={cn(
        "group/comp relative aspect-square w-full overflow-hidden rounded-lg bg-canvas ring-1 ring-border shadow-[var(--shadow-card)]",
        className,
      )}
    >
      <div className="absolute inset-0">
        <TileTexture
          tileId={registry.tile_id}
          modality={registry.modality}
          src={rawSrc}
        />
      </div>

      {showHeatmap && (
        <div
          className="absolute inset-0 mix-blend-screen transition-opacity duration-500"
          style={{ opacity: overlayOpacity }}
        >
          <AnomalyHeatmap tileId={registry.tile_id} score={score} src={overlaySrc} />
        </div>
      )}

      {showContour && score >= 0.35 && (
        <div className="absolute inset-0">
          <ContourRing tileId={registry.tile_id} score={score} />
        </div>
      )}

      <Corner className="left-2.5 top-2.5 border-l border-t" />
      <Corner className="right-2.5 top-2.5 border-r border-t" />
      <Corner className="bottom-2.5 left-2.5 border-b border-l" />
      <Corner className="bottom-2.5 right-2.5 border-b border-r" />

      <div className="pointer-events-none absolute left-3.5 top-3.5 font-mono text-[0.62rem] leading-tight text-white/65">
        X{registry.tile_x ?? 0} · Y{registry.tile_y ?? 0}
      </div>

      <div className="pointer-events-none absolute bottom-3.5 right-3.5 flex items-center gap-1.5 font-mono text-[0.6rem] text-white/55">
        <span className="h-px w-8 bg-white/55" />
        <span>50µm</span>
      </div>
    </div>
  );
}
