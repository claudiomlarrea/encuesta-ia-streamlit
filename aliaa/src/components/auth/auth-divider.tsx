export function AuthDivider({ label = "o" }: { label?: string }) {
  return (
    <div className="relative my-6">
      <div className="absolute inset-0 flex items-center">
        <span className="w-full border-t border-[var(--aliaa-border)]" />
      </div>
      <div className="relative flex justify-center text-xs uppercase">
        <span className="bg-[var(--aliaa-card)] px-2 text-[var(--aliaa-muted-foreground)]">
          {label}
        </span>
      </div>
    </div>
  );
}
