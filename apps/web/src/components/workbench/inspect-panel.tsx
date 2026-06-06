import type { DemoExample } from "@/lib/types";
import { cn } from "@/lib/utils";
import { ExampleSelector } from "./example-selector";
import { ReadoutPanel } from "./readout-panel";
import { TileViewer } from "./tile-viewer";

interface InspectPanelProps {
  example: DemoExample;
  reviewAt: number;
  holdAt: number;
  examples?: DemoExample[];
  selectedId?: string;
  onSelectExample?: (id: string) => void;
  className?: string;
}

export function InspectPanel({
  example,
  reviewAt,
  holdAt,
  examples,
  selectedId,
  onSelectExample,
  className,
}: InspectPanelProps) {
  const withSelector = examples && onSelectExample && selectedId;

  return (
    <div
      className={cn(
        "grid gap-5",
        withSelector
          ? "lg:grid-cols-[15rem_minmax(0,1fr)_22rem]"
          : "lg:grid-cols-[minmax(0,1fr)_22rem]",
        className,
      )}
    >
      {withSelector && (
        <ExampleSelector
          examples={examples}
          selectedId={selectedId}
          onSelect={onSelectExample}
        />
      )}

      <div className="flex min-w-0 flex-col gap-3">
        <div className="flex items-baseline justify-between gap-3">
          <p className="text-sm text-muted-foreground">{example.caption}</p>
        </div>
        <TileViewer key={example.registry.tile_id} example={example} />
      </div>

      <ReadoutPanel example={example} reviewAt={reviewAt} holdAt={holdAt} />
    </div>
  );
}
