import { CourseForm } from "@/components/admin/course-form";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Nuevo Curso",
};

export default function NuevoCursoPage() {
  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold">Crear nuevo curso</h1>
      <CourseForm />
    </div>
  );
}
