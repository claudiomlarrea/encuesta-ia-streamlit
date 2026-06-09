import { CourseCatalog } from "@/components/courses/course-catalog";
import { getPublishedCourses } from "@/lib/courses";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Cursos",
};

export default async function CursosPage() {
  const courses = await getPublishedCourses();

  return (
    <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      <div className="mb-10">
        <h1 className="text-3xl font-bold">Catálogo de Cursos</h1>
        <p className="mt-2 text-[var(--aliaa-muted-foreground)]">
          Explorá nuestra oferta formativa en inteligencia artificial aplicada
        </p>
      </div>

      <CourseCatalog courses={courses} />
    </div>
  );
}
