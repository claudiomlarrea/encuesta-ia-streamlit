import { notFound } from "next/navigation";
import Link from "next/link";
import { Clock, BarChart3, Users, CheckCircle, Play } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { PaymentButtons } from "@/components/payments/payment-buttons";
import { EnrollButton } from "@/components/courses/enroll-button";
import { CourseCover } from "@/components/courses/course-cover";
import { formatPrice, sumLessonMinutes } from "@/lib/utils";
import { LEVEL_LABELS, LESSON_TYPE_LABELS } from "@/lib/constants";
import { getCourseBySlug, getCourseModules } from "@/lib/courses";
import { courseAccessLabel, getEnrollment } from "@/lib/enrollments";
import { profileNameForForm } from "@/lib/profile-name";
import { getProfile } from "@/lib/supabase/server";
import { createClient } from "@/lib/supabase/server";
import type { Metadata } from "next";

interface PageProps {
  params: Promise<{ slug: string }>;
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { slug } = await params;
  const course = await getCourseBySlug(slug);
  return { title: course?.titulo || "Curso" };
}

export default async function CursoDetallePage({ params }: PageProps) {
  const { slug } = await params;
  const course = await getCourseBySlug(slug);
  if (!course || !course.publicado) notFound();

  const modules = await getCourseModules(course.id);
  const profile = await getProfile();
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  const enrollment = user ? await getEnrollment(user.id, course.id) : null;
  const enrolled = !!enrollment;

  return (
    <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      <div className="grid gap-8 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <div className="mb-4 flex flex-wrap gap-2">
            {course.categoria && <Badge>{course.categoria}</Badge>}
            {course.nivel && <Badge variant="secondary">{LEVEL_LABELS[course.nivel]}</Badge>}
            {course.gratuito && <Badge variant="success">Gratuito</Badge>}
          </div>
          <h1 className="text-3xl font-bold">{course.titulo}</h1>
          <p className="mt-4 text-[var(--aliaa-muted-foreground)]">
            {course.descripcion || course.descripcion_corta}
          </p>

          <div className="mt-6 flex flex-wrap gap-6 text-sm text-[var(--aliaa-muted-foreground)]">
            {course.duracion_horas && (
              <span className="flex items-center gap-2">
                <Clock className="h-4 w-4" />
                {course.duracion_horas} horas
              </span>
            )}
            {course.nivel && (
              <span className="flex items-center gap-2">
                <BarChart3 className="h-4 w-4" />
                {LEVEL_LABELS[course.nivel]}
              </span>
            )}
            <span className="flex items-center gap-2">
              <Users className="h-4 w-4" />
              {modules.length} módulos
            </span>
          </div>

          <div className="mt-10">
            <h2 className="mb-4 text-xl font-semibold">Contenido del curso</h2>
            {modules.length === 0 ? (
              <p className="text-sm text-[var(--aliaa-muted-foreground)]">Contenido en preparación.</p>
            ) : (
              modules.map((mod, i) => {
                const modMinutes = sumLessonMinutes(mod.lessons ?? []);
                return (
                <Card key={mod.id} className="mb-4">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between gap-2">
                      <h3 className="font-semibold">
                        Módulo {i + 1}: {mod.titulo}
                      </h3>
                      <span className="shrink-0 text-sm text-[var(--aliaa-muted-foreground)]">
                        {modMinutes} min
                      </span>
                    </div>
                    <ul className="mt-3 space-y-2">
                      {(mod.lessons ?? []).map((lec) => (
                        <li
                          key={lec.id}
                          className="flex items-center gap-3 text-sm text-[var(--aliaa-muted-foreground)]"
                        >
                          <Play className="h-3.5 w-3.5" />
                          {lec.titulo}
                          <Badge variant="outline" className="ml-auto">
                            {LESSON_TYPE_LABELS[lec.tipo]}
                          </Badge>
                          {lec.duracion_minutos && (
                            <span>{lec.duracion_minutos} min</span>
                          )}
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              );
              })
            )}
          </div>
        </div>

        <div>
          <Card className="sticky top-24">
            <CardContent className="p-6">
              <div className="group mb-4 aspect-video overflow-hidden rounded-lg">
                <CourseCover slug={course.slug} titulo={course.titulo} className="rounded-lg" />
              </div>
              <p className="text-3xl font-bold text-[var(--aliaa-primary)]">
                {course.gratuito ? "Gratis" : formatPrice(course.precio, course.moneda)}
              </p>

              {profile ? (
                enrolled ? (
                  <Link href={`/dashboard/cursos/${course.id}`} className="mt-4 block">
                    <Button className="w-full">
                      {courseAccessLabel(enrollment.progreso_porcentaje)}
                    </Button>
                  </Link>
                ) : course.gratuito ? (
                  <div className="mt-4">
                    <EnrollButton
                      courseId={course.id}
                      defaultName={profile ? profileNameForForm(profile) : ""}
                    />
                  </div>
                ) : (
                  <div className="mt-4">
                    <PaymentButtons
                      courseId={course.id}
                      courseTitle={course.titulo}
                      amount={course.precio}
                      currency={course.moneda}
                    />
                  </div>
                )
              ) : (
                <Link href="/login" className="mt-4 block">
                  <Button className="w-full">Ingresar para inscribirte</Button>
                </Link>
              )}

              <ul className="mt-6 space-y-2 text-sm">
                {["Acceso de por vida", "Certificado verificable", "Foro de discusión", "Soporte del docente"].map(
                  (item) => (
                    <li key={item} className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-[var(--aliaa-secondary)]" />
                      {item}
                    </li>
                  )
                )}
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
