import { forwardRef, type InputHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

const Input = forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement>>(
  ({ className, type, ...props }, ref) => (
    <input
      type={type}
      className={cn(
        "flex h-10 w-full rounded-lg border border-[var(--aliaa-border)] bg-[var(--aliaa-background)] px-3 py-2 text-sm text-[var(--aliaa-foreground)] placeholder:text-[var(--aliaa-muted-foreground)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--aliaa-primary)] disabled:cursor-not-allowed disabled:opacity-50",
        className
      )}
      ref={ref}
      {...props}
    />
  )
);
Input.displayName = "Input";

export { Input };
