"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Play, FileText, CheckCircle, MessageSquare, BookOpen, Award } from "lucide-react";
import { createClient } from "@/lib/supabase/client";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { PresentationPlayer, parsePresentation } from "@/components/courses/presentation-player";
import { QuizPlayer } from "@/components/courses/quiz-player";
import { LessonMarkdown } from "@/components/courses/lesson-markdown";
import { LESSON_TYPE_LABELS } from "@/lib/constants";
import { cn, sumLessonMinutes } from "@/lib/utils";
import type { Course, Module, Lesson } from "@/types/database";
import type { QuizWithQuestions } from "@/lib/quizzes";

interface LessonWithProgress extends Lesson {
  completado: boolean;
}

interface ModuleWithLessons extends Module {
  lessons: LessonWithProgress[];
}

interface CoursePlayerProps {
  course: Course;
  modules: ModuleWithLessons[];
  initialProgress: number;
  userId: string;
  quizzes?: Record<string, QuizWithQuestions>;
  initialCertificateId?: string | null;
}

const TYPE_ICONS: Record<string, typeof Play> = {
  video: Play,
  pdf: FileText,
  texto: BookOpen,
  actividad: BookOpen,
  evaluacion: CheckCircle,
};

export function CoursePlayer({
  course,
  modules,
  initialProgress,
  userId,
  quizzes = {},
  initialCertificateId = null,
}: CoursePlayerProps) {
  const router = useRouter();
  const allLessons = modules.flatMap((m) => m.lessons ?? []);
  const [activeLesson, setActiveLesson] = useState<LessonWithProgress>(
    allLessons.find((l) => !l.completado) ?? allLessons[0]
  );
  const [progress, setProgress] = useState(initialProgress);
  const [completedIds, setCompletedIds] = useState(
    new Set(allLessons.filter((l) => l.completado).map((l) => l.id))
  );
  const [marking, setMarking] = useState(false);
  const [certificateId, setCertificateId] = useState<string | null>(initialCertificateId);
  const [autoStartNextLesson, setAutoStartNextLesson] = useState(false);

  const Icon = TYPE_ICONS[activeLesson?.tipo] ?? Play;
  const activeQuiz = activeLesson ? quizzes[activeLesson.id] : undefined;
  const isEvalWithQuiz = activeLesson?.tipo === "evaluacion" && !!activeQuiz;

  async function tryGenerateCertificate(pct: number) {
    if (pct !== 100 || certificateId) return;
    const res = await fetch("/api/certificates/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ courseId: course.id }),
    });
    if (res.ok) {
      const { certificate } = await res.json();
      setCertificateId(certificate.id);
    }
  }

  async function completeLesson(
    lessonId: string,
    options?: { navigateToNext?: boolean }
  ): Promise<Set<string>> {
    if (completedIds.has(lessonId)) return completedIds;

    const supabase = createClient();
    await supabase.from("lesson_progress").upsert({
      user_id: userId,
      lesson_id: lessonId,
      completado: true,
      completado_en: new Date().toISOString(),
    });

    const newCompleted = new Set(completedIds);
    newCompleted.add(lessonId);
    setCompletedIds(newCompleted);

    const pct = allLessons.length
      ? Math.round((newCompleted.size / allLessons.length) * 100)
      : 0;
    setProgress(pct);

    await supabase
      .from("enrollments")
      .update({
        progreso_porcentaje: pct,
        completado_en: pct === 100 ? new Date().toISOString() : null,
      })
      .eq("user_id", userId)
      .eq("course_id", course.id);

    await tryGenerateCertificate(pct);

    if (options?.navigateToNext !== false) {
      const next = allLessons.find((l) => !newCompleted.has(l.id));
      if (next) setActiveLesson({ ...next, completado: false });
    }

    router.refresh();
    return newCompleted;
  }

  async function finishLesson(lessonId: string) {
    await completeLesson(lessonId);
  }

  useEffect(() => {
    if (progress === 100) tryGenerateCertificate(100);
  }, [progress]); // eslint-disable-line react-hooks/exhaustive-deps

  async function markComplete() {
    if (!activeLesson || completedIds.has(activeLesson.id)) return;
    setMarking(true);
    await finishLesson(activeLesson.id);
    setMarking(false);
  }

  async function handleQuizPass() {
    if (!activeLesson || completedIds.has(activeLesson.id)) return;
    setMarking(true);
    await finishLesson(activeLesson.id);
    setMarking(false);
  }

  if (!activeLesson) {
    return <p className="text-[var(--aliaa-muted-foreground)]">Este curso aún no tiene lecciones.</p>;
  }

  const presentation = parsePresentation(activeLesson.contenido_texto);

  function selectLesson(lesson: LessonWithProgress, autoStart = false) {
    if (
      activeLesson &&
      activeLesson.id !== lesson.id &&
      !completedIds.has(activeLesson.id) &&
      ["texto", "actividad", "pdf"].includes(activeLesson.tipo)
    ) {
      void completeLesson(activeLesson.id, { navigateToNext: false });
    }
    setAutoStartNextLesson(autoStart);
    setActiveLesson(lesson);
  }

  async function handlePresentationComplete() {
    const idx = allLessons.findIndex((l) => l.id === activeLesson.id);
    let updatedCompleted = completedIds;

    if (!completedIds.has(activeLesson.id)) {
      setMarking(true);
      updatedCompleted = await completeLesson(activeLesson.id, { navigateToNext: false });
      setMarking(false);
    }

    if (idx < 0 || idx >= allLessons.length - 1) return;
    const next = allLessons[idx + 1];
    const nextIsPresentation =
      next.tipo === "video" && !!parsePresentation(next.contenido_texto);
    selectLesson(
      { ...next, completado: updatedCompleted.has(next.id) },
      nextIsPresentation
    );
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold">{course.titulo}</h1>
        <div className="mt-3 max-w-md">
          <Progress value={progress} showLabel />
        </div>
      </div>

      {progress === 100 && (
        <Card className="mb-6 border-emerald-500 bg-emerald-50 dark:bg-emerald-900/20">
          <CardContent className="flex items-center gap-4 p-6">
            <Award className="h-10 w-10 shrink-0 text-emerald-600" />
            <div className="flex-1">
              <h2 className="font-semibold text-emerald-800 dark:text-emerald-200">
                ¡Curso completado!
              </h2>
              <p className="text-sm text-emerald-700 dark:text-emerald-300">
                Felicitaciones, completaste todas las lecciones.
              </p>
            </div>
            {certificateId && (
              <Link href={`/dashboard/certificados/${certificateId}`}>
                <Button>Ver certificado</Button>
              </Link>
            )}
          </CardContent>
        </Card>
      )}

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <Card>
            <CardContent className="p-0">
              {activeLesson.tipo === "video" && presentation ? (
                <PresentationPlayer
                  key={activeLesson.id}
                  content={activeLesson.contenido_texto!}
                  lessonTitle={activeLesson.titulo}
                  autoStart={autoStartNextLesson}
                  onAutoStartConsumed={() => setAutoStartNextLesson(false)}
                  onComplete={() => void handlePresentationComplete()}
                />
              ) : activeLesson.tipo === "video" ? (
                <div className="flex aspect-video items-center justify-center rounded-t-xl bg-black">
                  <Play className="h-16 w-16 text-white/60" />
                </div>
              ) : null}

              {(activeLesson.tipo === "texto" ||
                activeLesson.tipo === "actividad" ||
                activeLesson.tipo === "pdf") &&
                activeLesson.contenido_texto && (
                  <LessonMarkdown content={activeLesson.contenido_texto} />
                )}

              {isEvalWithQuiz && activeLesson.contenido_texto && !completedIds.has(activeLesson.id) && (
                <LessonMarkdown content={activeLesson.contenido_texto} />
              )}

              {isEvalWithQuiz && !completedIds.has(activeLesson.id) && (
                <QuizPlayer quiz={activeQuiz} onPass={handleQuizPass} />
              )}

              {activeLesson.tipo === "evaluacion" &&
                !isEvalWithQuiz &&
                !completedIds.has(activeLesson.id) && (
                  <div className="space-y-4 p-6">
                    {activeLesson.contenido_texto && (
                      <LessonMarkdown content={activeLesson.contenido_texto} />
                    )}
                    <p className="rounded-lg bg-amber-50 p-4 text-sm text-amber-800 dark:bg-amber-900/20 dark:text-amber-300">
                      El cuestionario no está disponible. Contactá al administrador del curso.
                    </p>
                  </div>
                )}

              {activeLesson.tipo === "evaluacion" && completedIds.has(activeLesson.id) && (
                <div className="p-8 text-center">
                  <CheckCircle className="mx-auto h-12 w-12 text-emerald-500" />
                  <h3 className="mt-4 text-lg font-semibold">Evaluación aprobada</h3>
                  {progress < 100 && (
                    <p className="mt-2 text-sm text-[var(--aliaa-muted-foreground)]">
                      Progreso {progress}%. Escuchá o revisá las lecciones pendientes en el menú
                      lateral para llegar al 100% y obtener tu certificado.
                    </p>
                  )}
                  {certificateId ? (
                    <Link href={`/dashboard/certificados/${certificateId}`} className="mt-4 inline-block">
                      <Button>Ver certificado</Button>
                    </Link>
                  ) : progress === 100 ? (
                    <Button className="mt-4" onClick={() => tryGenerateCertificate(100)}>
                      Generar certificado
                    </Button>
                  ) : null}
                </div>
              )}

              <div className="border-t border-[var(--aliaa-border)] p-6">
                <div className="flex items-center gap-2">
                  <Icon className="h-5 w-5 text-[var(--aliaa-primary)]" />
                  <h2 className="text-lg font-semibold">{activeLesson.titulo}</h2>
                  <Badge variant="outline">{LESSON_TYPE_LABELS[activeLesson.tipo]}</Badge>
                </div>
                {activeLesson.descripcion && (
                  <p className="mt-2 text-sm text-[var(--aliaa-muted-foreground)]">
                    {activeLesson.descripcion}
                  </p>
                )}
                {!isEvalWithQuiz && (
                  <div className="mt-4 flex gap-3">
                    <Button
                      onClick={markComplete}
                      disabled={marking || completedIds.has(activeLesson.id)}
                    >
                      <CheckCircle className="mr-2 h-4 w-4" />
                      {completedIds.has(activeLesson.id)
                        ? "Completada"
                        : marking
                          ? "Guardando..."
                          : "Marcar como completada"}
                    </Button>
                    <Link href="/dashboard/foros">
                      <Button variant="outline">
                        <MessageSquare className="mr-2 h-4 w-4" />
                        Foro del curso
                      </Button>
                    </Link>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        <div>
          <Card>
            <CardContent className="p-4">
              <h3 className="mb-4 font-semibold">Contenido del curso</h3>
              {modules.map((mod) => {
                const modMinutes = sumLessonMinutes(mod.lessons ?? []);
                return (
                <div key={mod.id} className="mb-4">
                  <div className="mb-2 flex items-center justify-between gap-2">
                    <p className="text-xs font-medium uppercase text-[var(--aliaa-muted-foreground)]">
                      {mod.titulo}
                    </p>
                    <span className="shrink-0 text-xs text-[var(--aliaa-muted-foreground)]">
                      {modMinutes} min
                    </span>
                  </div>
                  {(mod.lessons ?? []).map((lec) => {
                    const LecIcon = TYPE_ICONS[lec.tipo] ?? Play;
                    const done = completedIds.has(lec.id);
                    return (
                      <button
                        key={lec.id}
                        onClick={() => selectLesson(lec)}
                        className={cn(
                          "flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-sm transition-colors",
                          activeLesson.id === lec.id
                            ? "bg-[var(--aliaa-primary)]/10 text-[var(--aliaa-primary)]"
                            : "hover:bg-[var(--aliaa-muted)]"
                        )}
                      >
                        {done ? (
                          <CheckCircle className="h-4 w-4 shrink-0 text-[var(--aliaa-secondary)]" />
                        ) : (
                          <LecIcon className="h-4 w-4 shrink-0" />
                        )}
                        <span className="flex-1 truncate">{lec.titulo}</span>
                        {lec.duracion_minutos && (
                          <span className="text-xs text-[var(--aliaa-muted-foreground)]">
                            {lec.duracion_minutos}m
                          </span>
                        )}
                      </button>
                    );
                  })}
                </div>
              );
              })}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
