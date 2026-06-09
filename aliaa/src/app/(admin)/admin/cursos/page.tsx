import Link from "next/link";
import { Plus, Edit, Eye } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { getAllCourses, getEnrollmentCount } from "@/lib/courses";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Gestionar Cursos",
};

export default async function AdminCursosPage() {
  const courses = await getAllCourses();

  const coursesWithCounts = await Promise.all(
    courses.map(async (course) => ({
      ...course,
      inscritos: await getEnrollmentCount(course.id),
    }))
  );

  return (
    <div>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Gestionar Cursos</h1>
          <p className="mt-1 text-[var(--aliaa-muted-foreground)]">
            Creá, editá y publicá cursos en la plataforma
          </p>
        </div>
        <Link href="/admin/cursos/nuevo">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Nuevo curso
          </Button>
        </Link>
      </div>

      {coursesWithCounts.length === 0 ? (
        <Card className="mt-8">
          <CardContent className="py-12 text-center text-[var(--aliaa-muted-foreground)]">
            No hay cursos todavía.{" "}
            <Link href="/admin/cursos/nuevo" className="text-[var(--aliaa-primary)] hover:underline">
              Creá el primero
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="mt-8 space-y-3">
          {coursesWithCounts.map((course) => (
            <Card key={course.id}>
              <CardContent className="flex items-center gap-4 p-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold">{course.titulo}</h3>
                    <Badge variant={course.publicado ? "success" : "warning"}>
                      {course.publicado ? "Publicado" : "Borrador"}
                    </Badge>
                    {course.gratuito && <Badge variant="secondary">Gratuito</Badge>}
                  </div>
                  <p className="mt-1 text-sm text-[var(--aliaa-muted-foreground)]">
                    {course.inscritos} inscritos · {course.gratuito ? "Gratis" : `$${course.precio} USD`}
                  </p>
                </div>
                <div className="flex gap-2">
                  {course.publicado && (
                    <Link href={`/cursos/${course.slug}`} target="_blank">
                      <Button variant="outline" size="sm">
                        <Eye className="mr-1 h-3.5 w-3.5" />
                        Ver
                      </Button>
                    </Link>
                  )}
                  <Link href={`/admin/cursos/${course.id}`}>
                    <Button variant="outline" size="sm">
                      <Edit className="mr-1 h-3.5 w-3.5" />
                      Editar
                    </Button>
                  </Link>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
