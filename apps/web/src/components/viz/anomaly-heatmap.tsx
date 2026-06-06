"use client";

import { useEffect, useRef } from "react";
import { cn } from "@/lib/utils";
import { anomalyBlobs } from "@/lib/viz/anomaly-field";
import { heatColor } from "@/lib/viz/heat-ramp";

interface AnomalyHeatmapProps {
  tileId: string;
  score: number;
  className?: string;
  /** When provided, renders a real overlay PNG instead of the procedural field. */
  src?: string;
}

const RES = 360;

export function AnomalyHeatmap({ tileId, score, className, src }: AnomalyHeatmapProps) {
  const ref = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (src) return;
    const canvas = ref.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.clearRect(0, 0, RES, RES);
    ctx.globalCompositeOperation = "source-over";

    for (const blob of anomalyBlobs(tileId, score)) {
      const cx = blob.x * RES;
      const cy = blob.y * RES;
      const r = blob.r * RES;
      // Solid core with a short, defined falloff — reads as a discrete probe,
      // not a fuzzy gradient cloud.
      const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, r);
      grad.addColorStop(0, heatColor(blob.intensity, 0.95));
      grad.addColorStop(0.6, heatColor(blob.intensity, 0.88));
      grad.addColorStop(0.82, heatColor(blob.intensity, 0.45));
      grad.addColorStop(1, heatColor(blob.intensity, 0));
      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.fill();
    }
  }, [tileId, score, src]);

  if (src) {
    return (
      // eslint-disable-next-line @next/next/no-img-element
      <img
        src={src}
        alt=""
        className={cn("size-full object-cover", className)}
        draggable={false}
      />
    );
  }

  return (
    <canvas
      ref={ref}
      width={RES}
      height={RES}
      className={cn("size-full", className)}
      aria-hidden
    />
  );
}
