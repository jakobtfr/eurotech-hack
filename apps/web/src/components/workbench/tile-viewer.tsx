"use client";

import { ImageIcon, LayersIcon, ScanIcon } from "lucide-react";
import { useState } from "react";
import { OverlayCompositor } from "@/components/viz/overlay-compositor";
import { artifactUrl } from "@/lib/artifact-url";
import type { DemoExample } from "@/lib/types";
import { cn } from "@/lib/utils";

interface TileViewerProps {
  example: DemoExample;
  className?: string;
  initialOpacity?: number;
}

function Toggle({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-pressed={active}
      className={cn(
        "inline-flex items-center gap-1.5 rounded-md border px-2.5 py-1 font-mono text-[0.7rem] tracking-wide transition-colors [&>svg]:size-3.5",
        active
          ? "border-primary/50 bg-primary/10 text-primary"
          : "border-border bg-card/50 text-muted-foreground hover:text-foreground",
      )}
    >
      {children}
    </button>
  );
}

export function TileViewer({
  example,
  className,
  initialOpacity = 0.72,
}: TileViewerProps) {
  const [opacity, setOpacity] = useState(initialOpacity);
  const [showHeatmap, setShowHeatmap] = useState(true);
  const [showContour, setShowContour] = useState(true);

  return (
    <div className={cn("flex flex-col gap-3", className)}>
      <OverlayCompositor
        example={example}
        overlayOpacity={showHeatmap ? opacity : 0}
        showHeatmap={showHeatmap}
        showContour={showContour}
        rawSrc={artifactUrl(example.registry.image_path)}
        overlaySrc={artifactUrl(example.result?.heatmap_path)}
      />

      <div className="flex flex-wrap items-center gap-3">
        <Toggle active={showHeatmap} onClick={() => setShowHeatmap((v) => !v)}>
          <LayersIcon /> Heatmap
        </Toggle>
        <Toggle active={showContour} onClick={() => setShowContour((v) => !v)}>
          <ScanIcon /> ROI
        </Toggle>

        <label className="ml-auto flex flex-1 items-center gap-2 sm:flex-none">
          <span className="inline-flex items-center gap-1 font-mono text-[0.7rem] text-muted-foreground [&>svg]:size-3.5">
            <ImageIcon /> opacity
          </span>
          <input
            type="range"
            min={0}
            max={1}
            step={0.01}
            value={opacity}
            disabled={!showHeatmap}
            onChange={(e) => setOpacity(Number(e.target.value))}
            className="h-1 w-32 cursor-pointer appearance-none rounded-full bg-muted accent-primary disabled:opacity-40"
            aria-label="Overlay opacity"
          />
          <span className="w-8 text-right font-mono text-[0.7rem] tabular-nums text-foreground">
            {Math.round((showHeatmap ? opacity : 0) * 100)}
          </span>
        </label>
      </div>
    </div>
  );
}
