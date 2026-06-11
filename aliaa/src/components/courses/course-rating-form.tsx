"use client";

import { useState } from "react";
import { Star } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface CourseRatingFormProps {
  courseId: string;
  initialStars?: number;
  initialComment?: string | null;
}

export function CourseRatingForm({
  courseId,
  initialStars = 0,
  initialComment = "",
}: CourseRatingFormProps) {
  const [stars, setStars] = useState(initialStars);
  const [hover, setHover] = useState(0);
  const [comment, setComment] = useState(initialComment ?? "");
  const [loading, setLoading] = useState(false);
  const [saved, setSaved] = useState(initialStars > 0);
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (stars < 1) {
      setError("Elegí de 1 a 5 estrellas.");
      return;
    }

    setLoading(true);
    setError("");
    const res = await fetch("/api/courses/ratings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ courseId, estrellas: stars, comentario: comment }),
    });
    setLoading(false);

    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      setError(data.error || "No se pudo guardar tu valoración.");
      return;
    }

    setSaved(true);
  }

  const active = hover || stars;

  return (
    <form onSubmit={handleSubmit} className="mt-4 border-t border-emerald-200/60 pt-4 dark:border-emerald-800/60">
      <p className="text-sm font-medium text-emerald-900 dark:text-emerald-100">
        {saved ? "Tu valoración" : "¿Cómo fue tu experiencia con este curso?"}
      </p>
      <p className="mt-1 text-xs text-emerald-800/80 dark:text-emerald-200/80">
        Valoralo de 1 a 5 estrellas. Solo alumnos que completaron el curso pueden valorar.
      </p>

      <div
        className="mt-3 flex items-center gap-1"
        role="radiogroup"
        aria-label="Valoración del curso"
      >
        {Array.from({ length: 5 }, (_, i) => {
          const value = i + 1;
          const filled = active >= value;
          return (
            <button
              key={value}
              type="button"
              role="radio"
              aria-checked={stars === value}
              aria-label={`${value} estrella${value === 1 ? "" : "s"}`}
              className="rounded p-0.5 transition-transform hover:scale-110"
              onMouseEnter={() => setHover(value)}
              onMouseLeave={() => setHover(0)}
              onClick={() => {
                setStars(value);
                setSaved(false);
              }}
            >
              <Star
                className={cn(
                  "h-8 w-8",
                  filled ? "fill-amber-400 text-amber-400" : "text-emerald-300 dark:text-emerald-700"
                )}
              />
            </button>
          );
        })}
        {stars > 0 && (
          <span className="ml-2 text-sm font-medium text-emerald-900 dark:text-emerald-100">
            {stars}/5
          </span>
        )}
      </div>

      <label className="mt-3 block text-xs font-medium text-emerald-900 dark:text-emerald-100">
        Comentario opcional
        <textarea
          value={comment}
          onChange={(e) => {
            setComment(e.target.value);
            setSaved(false);
          }}
          rows={2}
          maxLength={500}
          placeholder="¿Qué te resultó más útil?"
          className="mt-1.5 w-full rounded-lg border border-emerald-200 bg-white/80 px-3 py-2 text-sm text-[var(--aliaa-foreground)] placeholder:text-[var(--aliaa-muted-foreground)] dark:border-emerald-800 dark:bg-emerald-950/40"
        />
      </label>

      {error && <p className="mt-2 text-sm text-red-600 dark:text-red-400">{error}</p>}

      <Button
        type="submit"
        size="sm"
        className="mt-3"
        disabled={loading || stars < 1}
        variant={saved ? "outline" : "default"}
      >
        {loading ? "Guardando..." : saved ? "Actualizar valoración" : "Enviar valoración"}
      </Button>
    </form>
  );
}
