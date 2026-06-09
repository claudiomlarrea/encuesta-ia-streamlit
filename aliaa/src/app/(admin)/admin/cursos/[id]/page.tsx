import Link from "next/link";
import { notFound } from "next/navigation";
import { ExternalLink } from "lucide-react";
import { CourseForm } from "@/components/admin/course-form";
import { ModuleLessonManager } from "@/components/admin/module-lesson-manager";
import { Button } from "@/components/ui/button";
import { getCourseById, getCourseModules } from "@/lib/courses";
import type { Metadata } from "next";

interface PageProps {
  params: Promise<{ id: string }>;
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { id } = await params;
  const course = await getCourseById(id);
  return { title: course ? `Editar: ${course.titulo}` : "Editar curso" };
}

export default async function EditarCursoPage({ params }: PageProps) {
  const { id } = await params;
  const course = await getCourseById(id);
  if (!course) notFound();

  const modules = await getCourseModules(id);

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Editar curso</h1>
        {course.publicado && (
          <Link href={`/cursos/${course.slug}`} target="_blank">
            <Button variant="outline" size="sm">
              <ExternalLink className="mr-1 h-3.5 w-3.5" />
              Ver en el sitio
            </Button>
          </Link>
        )}
      </div>

      <CourseForm course={course} />

      <div>
        <h2 className="mb-4 text-xl font-semibold">Contenido del curso</h2>
        <ModuleLessonManager courseId={id} initialModules={modules} />
      </div>
    </div>
  );
}
