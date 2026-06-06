import type * as React from "react";
import { cn } from "@/lib/utils";

interface KeyValueProps extends Omit<React.ComponentProps<"div">, "children"> {
  label: string;
  value: React.ReactNode;
  mono?: boolean;
  valueClassName?: string;
}

export function KeyValue({
  label,
  value,
  mono = true,
  valueClassName,
  className,
  ...props
}: KeyValueProps) {
  return (
    <div
      data-slot="key-value"
      className={cn(
        "flex items-center justify-between gap-3 border-b border-border/50 py-1.5 text-sm last:border-b-0",
        className,
      )}
      {...props}
    >
      <span className="shrink-0 font-mono text-[0.72rem] uppercase tracking-wider text-muted-foreground">
        {label}
      </span>
      <span
        className={cn(
          "min-w-0 truncate text-right text-foreground",
          mono && "font-mono text-xs tabular-nums",
          valueClassName,
        )}
      >
        {value}
      </span>
    </div>
  );
}
