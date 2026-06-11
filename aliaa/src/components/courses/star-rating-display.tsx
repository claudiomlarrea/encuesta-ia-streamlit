import { Star } from "lucide-react";
import { cn } from "@/lib/utils";

interface StarRatingDisplayProps {
  value: number;
  total?: number;
  size?: "sm" | "md";
  showValue?: boolean;
  className?: string;
}

export function StarRatingDisplay({
  value,
  total,
  size = "sm",
  showValue = true,
  className,
}: StarRatingDisplayProps) {
  if (!value && !total) return null;

  const iconClass = size === "sm" ? "h-3.5 w-3.5" : "h-4 w-4";
  const rounded = Math.round(value * 2) / 2;

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 text-[var(--aliaa-muted-foreground)]",
        size === "sm" ? "text-xs" : "text-sm",
        className
      )}
    >
      <span className="flex items-center gap-0.5" aria-hidden>
        {Array.from({ length: 5 }, (_, i) => {
          const filled = rounded >= i + 1;
          const half = !filled && rounded >= i + 0.5;
          return (
            <Star
              key={i}
              className={cn(
                iconClass,
                filled || half
                  ? "fill-amber-400 text-amber-400"
                  : "text-[var(--aliaa-border)]"
              )}
            />
          );
        })}
      </span>
      {showValue && value > 0 && (
        <span>
          {value.toFixed(1)}
          {total !== undefined && total > 0 && (
            <span className="text-[var(--aliaa-muted-foreground)]"> ({total})</span>
          )}
        </span>
      )}
    </span>
  );
}
