import { Brain, Network } from "lucide-react";
import { cn } from "@/lib/utils";

interface CoverStyle {
  gradient: string;
  accent: string;
  subtitle: string;
  Icon: typeof Brain;
}

const COVERS: Record<string, CoverStyle> = {
  "conceptos-inteligencia-artificial": {
    gradient: "from-violet-600 via-fuchsia-600 to-orange-500",
    accent: "bg-yellow-300/30",
    subtitle: "Tokens · Prompts · ~20 min",
    Icon: Brain,
  },
  "fundamentos-machine-learning": {
    gradient: "from-teal-700 via-sky-600 to-indigo-600",
    accent: "bg-cyan-300/25",
    subtitle: "De cero a tu primer proyecto",
    Icon: Network,
  },
};

const DEFAULT_COVER: CoverStyle = {
  gradient: "from-blue-700 to-teal-600",
  accent: "bg-white/15",
  subtitle: "ALIAA",
  Icon: Brain,
};

interface CourseCoverProps {
  slug: string;
  titulo: string;
  className?: string;
}

export function CourseCover({ slug, titulo, className }: CourseCoverProps) {
  const cover = COVERS[slug] ?? DEFAULT_COVER;
  const Icon = cover.Icon;
  const shortTitle =
    titulo.length > 28 ? titulo.replace("Fundamentos de ", "").replace("Conceptos en ", "Conceptos ") : titulo;

  return (
    <div
      className={cn(
        "relative flex h-full w-full flex-col justify-between overflow-hidden bg-gradient-to-br p-5",
        cover.gradient,
        className
      )}
    >
      <div className={cn("absolute -right-8 -top-8 h-40 w-40 rounded-full blur-2xl", cover.accent)} />
      <div className={cn("absolute -bottom-10 -left-6 h-36 w-36 rounded-full blur-2xl", cover.accent)} />

      <div className="relative flex items-start justify-between">
        <span className="rounded-full bg-white/15 px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider text-white/90">
          ALIAA
        </span>
        <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white/15 backdrop-blur-sm">
          <Icon className="h-6 w-6 text-white" strokeWidth={1.75} />
        </div>
      </div>

      <div className="relative mt-auto">
        <p className="text-lg font-bold leading-tight text-white sm:text-xl">{shortTitle}</p>
        <p className="mt-1 text-xs text-white/80 sm:text-sm">{cover.subtitle}</p>
      </div>
    </div>
  );
}
