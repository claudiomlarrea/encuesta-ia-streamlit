"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase/client";
import { slugify } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { COURSE_CATEGORIES } from "@/lib/constants";
import type { Course, CourseLevel } from "@/types/database";

interface CourseFormProps {
  course?: Course;
}

export function CourseForm({ course }: CourseFormProps) {
  const router = useRouter();
  const [titulo, setTitulo] = useState(course?.titulo ?? "");
  const [slug, setSlug] = useState(course?.slug ?? "");
  const [descripcionCorta, setDescripcionCorta] = useState(course?.descripcion_corta ?? "");
  const [descripcion, setDescripcion] = useState(course?.descripcion ?? "");
  const [precio, setPrecio] = useState(course?.precio?.toString() ?? "0");
  const [gratuito, setGratuito] = useState(course?.gratuito ?? false);
  const [publicado, setPublicado] = useState(course?.publicado ?? false);
  const [nivel, setNivel] = useState<CourseLevel>(course?.nivel ?? "principiante");
  const [categoria, setCategoria] = useState(course?.categoria ?? COURSE_CATEGORIES[0]);
  const [duracionHoras, setDuracionHoras] = useState(course?.duracion_horas?.toString() ?? "10");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function handleTituloChange(value: string) {
    setTitulo(value);
    if (!course) setSlug(slugify(value));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");

    const supabase = createClient();
    const payload = {
      titulo,
      slug: slug || slugify(titulo),
      descripcion_corta: descripcionCorta,
      descripcion,
      precio: gratuito ? 0 : parseFloat(precio) || 0,
      moneda: "USD",
      gratuito,
      publicado,
      nivel,
      categoria,
      duracion_horas: parseInt(duracionHoras) || 0,
    };

    if (course) {
      const { error: updateError } = await supabase
        .from("courses")
        .update(payload)
        .eq("id", course.id);
      if (updateError) {
        setError(updateError.message);
        setLoading(false);
        return;
      }
      router.push("/admin/cursos");
    } else {
      const { data, error: insertError } = await supabase
        .from("courses")
        .insert(payload)
        .select()
        .single();
      if (insertError) {
        setError(insertError.message);
        setLoading(false);
        return;
      }
      router.push(`/admin/cursos/${data.id}`);
    }
    router.refresh();
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{course ? "Editar curso" : "Nuevo curso"}</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="rounded-lg bg-red-50 p-3 text-sm text-red-600 dark:bg-red-900/20 dark:text-red-400">
              {error}
            </div>
          )}

          <div className="grid gap-4 sm:grid-cols-2">
            <div className="sm:col-span-2">
              <label className="mb-1.5 block text-sm font-medium">Título del curso</label>
              <Input value={titulo} onChange={(e) => handleTituloChange(e.target.value)} required />
            </div>
            <div>
              <label className="mb-1.5 block text-sm font-medium">Slug (URL)</label>
              <Input value={slug} onChange={(e) => setSlug(e.target.value)} required />
            </div>
            <div>
              <label className="mb-1.5 block text-sm font-medium">Categoría</label>
              <select
                value={categoria}
                onChange={(e) => setCategoria(e.target.value)}
                className="flex h-10 w-full rounded-lg border border-[var(--aliaa-border)] bg-[var(--aliaa-background)] px-3 text-sm"
              >
                {COURSE_CATEGORIES.map((cat) => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
            </div>
            <div className="sm:col-span-2">
              <label className="mb-1.5 block text-sm font-medium">Descripción corta</label>
              <Input value={descripcionCorta} onChange={(e) => setDescripcionCorta(e.target.value)} required />
            </div>
            <div className="sm:col-span-2">
              <label className="mb-1.5 block text-sm font-medium">Descripción completa</label>
              <textarea
                value={descripcion}
                onChange={(e) => setDescripcion(e.target.value)}
                rows={4}
                className="flex w-full rounded-lg border border-[var(--aliaa-border)] bg-[var(--aliaa-background)] px-3 py-2 text-sm"
              />
            </div>
            <div>
              <label className="mb-1.5 block text-sm font-medium">Nivel</label>
              <select
                value={nivel}
                onChange={(e) => setNivel(e.target.value as CourseLevel)}
                className="flex h-10 w-full rounded-lg border border-[var(--aliaa-border)] bg-[var(--aliaa-background)] px-3 text-sm"
              >
                <option value="principiante">Principiante</option>
                <option value="intermedio">Intermedio</option>
                <option value="avanzado">Avanzado</option>
              </select>
            </div>
            <div>
              <label className="mb-1.5 block text-sm font-medium">Duración (horas)</label>
              <Input type="number" min="1" value={duracionHoras} onChange={(e) => setDuracionHoras(e.target.value)} />
            </div>
            <div>
              <label className="mb-1.5 block text-sm font-medium">Precio (USD)</label>
              <Input
                type="number"
                min="0"
                step="0.01"
                value={precio}
                onChange={(e) => setPrecio(e.target.value)}
                disabled={gratuito}
              />
            </div>
            <div className="flex flex-col justify-end gap-3">
              <label className="flex items-center gap-2 text-sm">
                <input type="checkbox" checked={gratuito} onChange={(e) => setGratuito(e.target.checked)} />
                Curso gratuito
              </label>
              <label className="flex items-center gap-2 text-sm">
                <input type="checkbox" checked={publicado} onChange={(e) => setPublicado(e.target.checked)} />
                Publicar curso
              </label>
            </div>
          </div>

          <div className="flex gap-3 pt-2">
            <Button type="submit" disabled={loading}>
              {loading ? "Guardando..." : course ? "Guardar cambios" : "Crear curso"}
            </Button>
            <Button type="button" variant="outline" onClick={() => router.back()}>
              Cancelar
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
