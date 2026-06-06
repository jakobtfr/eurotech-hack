import * as React from "react";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface StatCardProps extends Omit<React.ComponentProps<"div">, "children"> {
  label: string;
  value: React.ReactNode;
  sublabel?: React.ReactNode;
  accent?: string;
  icon?: React.ReactNode;
}

export function StatCard({
  label,
  value,
  sublabel,
  accent,
  icon,
  className,
  ...props
}: StatCardProps) {
  return (
    <Card
      size="sm"
      data-slot="stat-card"
      className={cn("relative", className)}
      {...props}
    >
      <CardContent className="flex flex-col gap-1">
        <div className="flex items-center justify-between">
          <span className="eyebrow">{label}</span>
          {icon && <span className="text-muted-foreground [&>svg]:size-3.5">{icon}</span>}
        </div>
        <span
          className="font-display text-2xl font-bold tabular-nums leading-none"
          style={accent ? { color: accent } : undefined}
        >
          {value}
        </span>
        {sublabel && (
          <span className="font-mono text-[0.68rem] text-muted-foreground">
            {sublabel}
          </span>
        )}
      </CardContent>
    </Card>
  );
}
