import {
  Brain,
  Briefcase,
  CalendarDays,
  GraduationCap,
  HardHat,
  MessageSquareText,
  Network,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface CoverStyle {
  gradient: string;
  accent: string;
  subtitle: string;
  /** Título en la portada del catálogo (si difiere del nombre completo del curso) */
  displayTitle?: string;
  Icon: typeof Brain;
}

const COVERS: Record<string, CoverStyle> = {
  "conceptos-inteligencia-artificial": {
    gradient: "from-violet-600 via-fuchsia-600 to-orange-500",
    accent: "bg-yellow-300/30",
    subtitle: "Tokens · Prompts · ~20 min",
    displayTitle: "Conocimientos de Inteligencia Artificial",
    Icon: Brain,
  },
  "fundamentos-machine-learning": {
    gradient: "from-teal-700 via-sky-600 to-indigo-600",
    accent: "bg-cyan-300/25",
    subtitle: "De cero a tu primer proyecto",
    displayTitle: "Fundamentos de Machine Learning",
    Icon: Network,
  },
  "como-redactar-prompts": {
    gradient: "from-rose-600 via-amber-500 to-orange-500",
    accent: "bg-rose-200/30",
    subtitle: "CTF · Técnicas · 4×5 min",
    displayTitle: "Cómo redactar prompts",
    Icon: MessageSquareText,
  },
  "prompts-actividades-aula": {
    gradient: "from-emerald-700 via-teal-600 to-blue-600",
    accent: "bg-emerald-200/25",
    subtitle: "Docentes · Aula · 6×5 min",
    displayTitle: "Prompts para actividades en el aula",
    Icon: GraduationCap,
  },
  "ia-para-equipos-administrativos": {
    gradient: "from-blue-800 via-indigo-600 to-violet-600",
    accent: "bg-indigo-200/25",
    subtitle: "Oficina · Trámites · 4×5 min",
    displayTitle: "IA para equipos administrativos",
    Icon: Briefcase,
  },
  "ia-para-equipos-de-mineria": {
    gradient: "from-green-900 via-amber-800 to-stone-700",
    accent: "bg-amber-300/20",
    subtitle: "Faena · SSO · 4×5 min",
    displayTitle: "IA para equipos de minería",
    Icon: HardHat,
  },
  "ia-para-reuniones": {
    gradient: "from-cyan-800 via-teal-600 to-cyan-500",
    accent: "bg-cyan-200/25",
    subtitle: "Agendas · Actas · 4×5 min",
    displayTitle: "IA para reuniones",
    Icon: CalendarDays,
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
  const displayTitle = cover.displayTitle ?? titulo;

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
        <p
          className={cn(
            "font-bold leading-tight text-white",
            displayTitle.length > 32 ? "text-sm sm:text-base" : "text-lg sm:text-xl"
          )}
        >
          {displayTitle}
        </p>
        <p className="mt-1 text-xs text-white/80 sm:text-sm">{cover.subtitle}</p>
      </div>
    </div>
  );
}
