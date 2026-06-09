import { Users, BookOpen, UserPlus, Award } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getAdminStats } from "@/lib/admin-stats";
import { formatDate } from "@/lib/utils";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Administración",
};

export default async function AdminPage() {
  const stats = await getAdminStats();

  const cards = [
    { icon: Users, label: "Usuarios registrados", value: stats.users },
    { icon: BookOpen, label: "Cursos publicados", value: stats.courses },
    { icon: UserPlus, label: "Inscripciones totales", value: stats.enrollments },
    { icon: Award, label: "Certificados emitidos", value: stats.certificates },
  ];

  return (
    <div>
      <h1 className="text-2xl font-bold">Panel de Administración</h1>
      <p className="mt-1 text-[var(--aliaa-muted-foreground)]">
        Vista general de la plataforma ALIAA
      </p>

      <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {cards.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.label}>
              <CardContent className="p-6">
                <Icon className="h-8 w-8 text-[var(--aliaa-primary)]" />
                <p className="mt-4 text-2xl font-bold">{stat.value}</p>
                <p className="text-xs text-[var(--aliaa-muted-foreground)]">{stat.label}</p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Inscripciones recientes</CardTitle>
          </CardHeader>
          <CardContent>
            {stats.recentEnrollments.length === 0 ? (
              <p className="text-sm text-[var(--aliaa-muted-foreground)]">
                Aún no hay inscripciones. Compartí el link del curso para empezar a medir.
              </p>
            ) : (
              <ul className="space-y-3 text-sm">
                {stats.recentEnrollments.map((e, i) => {
                  const course = e.course as { titulo?: string } | null;
                  const profile = e.profile as { nombre_completo?: string } | null;
                  return (
                    <li key={i} className="flex justify-between gap-4">
                      <span className="truncate">
                        {profile?.nombre_completo ?? "Usuario"} — {course?.titulo ?? "Curso"}
                      </span>
                      <span className="shrink-0 text-[var(--aliaa-muted-foreground)]">
                        {formatDate(e.inscrito_en)}
                      </span>
                    </li>
                  );
                })}
              </ul>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Inscripciones por curso</CardTitle>
          </CardHeader>
          <CardContent>
            {stats.popularCourses.length === 0 ? (
              <p className="text-sm text-[var(--aliaa-muted-foreground)]">Sin cursos publicados.</p>
            ) : (
              <ul className="space-y-3 text-sm">
                {stats.popularCourses.map((curso) => (
                  <li key={curso.nombre} className="flex justify-between">
                    <span>{curso.nombre}</span>
                    <span className="font-medium">{curso.inscritos}</span>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
