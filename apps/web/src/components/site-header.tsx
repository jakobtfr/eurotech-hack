import { Badge } from "@/components/ui/badge";

export function SiteHeader() {
  return (
    <header className="border-b">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="flex size-9 items-center justify-center rounded-lg bg-primary text-primary-foreground font-mono text-sm font-bold">
            SiC
          </div>
          <div>
            <h1 className="text-base font-semibold leading-tight">
              SiC Anomaly Workbench
            </h1>
            <p className="text-xs text-muted-foreground">
              Few-shot semiconductor inspection · heatmaps · risk maps
            </p>
          </div>
        </div>
        <Badge variant="outline" className="font-mono">
          scaffold
        </Badge>
      </div>
    </header>
  );
}
