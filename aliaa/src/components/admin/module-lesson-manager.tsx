"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Plus, Trash2, Video, FileText, BookOpen } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { LessonType, Module, Lesson } from "@/types/database";

interface ModuleLessonManagerProps {
  courseId: string;
  initialModules: Module[];
}

const TYPE_ICONS: Record<string, typeof Video> = {
  video: Video,
  pdf: FileText,
  texto: BookOpen,
};

export function ModuleLessonManager({ courseId, initialModules }: ModuleLessonManagerProps) {
  const router = useRouter();
  const [modules, setModules] = useState(initialModules);
  const [newModuleTitle, setNewModuleTitle] = useState("");
  const [loading, setLoading] = useState(false);

  async function addModule() {
    if (!newModuleTitle.trim()) return;
    setLoading(true);
    const res = await fetch("/api/admin/modules", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        course_id: courseId,
        titulo: newModuleTitle,
        orden: modules.length,
      }),
    });
    const data = await res.json();
    setLoading(false);
    if (res.ok) {
      setModules([...modules, { ...data, lessons: [] }]);
      setNewModuleTitle("");
      router.refresh();
    }
  }

  async function addLesson(moduleId: string, moduleIndex: number) {
    const mod = modules[moduleIndex];
    const res = await fetch("/api/admin/lessons", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        module_id: moduleId,
        titulo: "Nueva lección",
        tipo: "video" as LessonType,
        orden: mod.lessons?.length ?? 0,
        duracion_minutos: 10,
      }),
    });
    const data = await res.json();
    if (res.ok) {
      const updated = [...modules];
      updated[moduleIndex] = {
        ...mod,
        lessons: [...(mod.lessons ?? []), data as Lesson],
      };
      setModules(updated);
      router.refresh();
    }
  }

  async function updateLesson(
    lessonId: string,
    moduleIndex: number,
    lessonIndex: number,
    field: string,
    value: string
  ) {
    const payload: Record<string, string | number> = { id: lessonId, [field]: value };
    if (field === "duracion_minutos") payload[field] = parseInt(value) || 0;

    await fetch("/api/admin/lessons", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const updated = [...modules];
    const lessons = [...(updated[moduleIndex].lessons ?? [])];
    lessons[lessonIndex] = { ...lessons[lessonIndex], [field]: payload[field] };
    updated[moduleIndex] = { ...updated[moduleIndex], lessons };
    setModules(updated);
  }

  async function deleteLesson(lessonId: string, moduleIndex: number, lessonIndex: number) {
    await fetch("/api/admin/lessons", {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: lessonId }),
    });
    const updated = [...modules];
    const lessons = [...(updated[moduleIndex].lessons ?? [])];
    lessons.splice(lessonIndex, 1);
    updated[moduleIndex] = { ...updated[moduleIndex], lessons };
    setModules(updated);
    router.refresh();
  }

  return (
    <div className="space-y-6">
      {modules.map((mod, mi) => (
        <Card key={mod.id}>
          <CardHeader>
            <CardTitle className="text-base">Módulo {mi + 1}: {mod.titulo}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {(mod.lessons ?? []).map((lesson, li) => {
              const Icon = TYPE_ICONS[lesson.tipo] ?? Video;
              return (
                <div key={lesson.id} className="flex flex-wrap items-center gap-2 rounded-lg border border-[var(--aliaa-border)] p-3">
                  <Icon className="h-4 w-4 shrink-0 text-[var(--aliaa-primary)]" />
                  <Input
                    value={lesson.titulo}
                    onChange={(e) => updateLesson(lesson.id, mi, li, "titulo", e.target.value)}
                    className="min-w-[200px] flex-1"
                  />
                  <select
                    value={lesson.tipo}
                    onChange={(e) => updateLesson(lesson.id, mi, li, "tipo", e.target.value)}
                    className="h-10 rounded-lg border border-[var(--aliaa-border)] bg-[var(--aliaa-background)] px-2 text-sm"
                  >
                    <option value="video">Video</option>
                    <option value="pdf">PDF</option>
                    <option value="texto">Texto</option>
                    <option value="actividad">Actividad</option>
                    <option value="evaluacion">Evaluación</option>
                  </select>
                  <Input
                    type="number"
                    value={lesson.duracion_minutos ?? 0}
                    onChange={(e) => updateLesson(lesson.id, mi, li, "duracion_minutos", e.target.value)}
                    className="w-20"
                    placeholder="min"
                  />
                  <Input
                    value={lesson.contenido_url ?? ""}
                    onChange={(e) => updateLesson(lesson.id, mi, li, "contenido_url", e.target.value)}
                    placeholder="URL del video o PDF"
                    className="min-w-[200px] flex-1"
                  />
                  <Button variant="ghost" size="icon" onClick={() => deleteLesson(lesson.id, mi, li)}>
                    <Trash2 className="h-4 w-4 text-red-500" />
                  </Button>
                </div>
              );
            })}
            <Button variant="outline" size="sm" onClick={() => addLesson(mod.id, mi)}>
              <Plus className="mr-1 h-3.5 w-3.5" />
              Agregar lección
            </Button>
          </CardContent>
        </Card>
      ))}

      <Card>
        <CardContent className="flex gap-2 p-4">
          <Input
            value={newModuleTitle}
            onChange={(e) => setNewModuleTitle(e.target.value)}
            placeholder="Título del nuevo módulo"
            className="flex-1"
          />
          <Button onClick={addModule} disabled={loading}>
            <Plus className="mr-1 h-4 w-4" />
            Agregar módulo
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
