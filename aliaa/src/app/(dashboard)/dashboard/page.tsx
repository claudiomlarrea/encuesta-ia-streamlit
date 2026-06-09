import Link from "next/link";
import { BookOpen, Award, TrendingUp, Clock } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { getUserEnrollments } from "@/lib/enrollments";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Panel",
};

export default async function DashboardPage() {
  const enrollments = await getUserEnrollments();
  const activos = enrollments.filter((e) => e.progreso_porcentaje < 100);
  const completados = enrollments.filter((e) => e.progreso_porcentaje >= 100);
  const promedio =
    enrollments.length > 0
      ? Math.round(
          enrollments.reduce((s, e) => s + e.progreso_porcentaje, 0) / enrollments.length
        )
      : 0;
  const horas = enrollments.reduce(
    (s, e) => s + (e.course?.duracion_horas ?? 0) * (e.progreso_porcentaje / 100),
    0
  );

  const stats = [
    { icon: BookOpen, label: "Cursos activos", value: String(activos.length) },
    { icon: Award, label: "Certificados", value: String(completados.length) },
    { icon: TrendingUp, label: "Progreso promedio", value: `${promedio}%` },
    { icon: Clock, label: "Horas de estudio", value: `${Math.round(horas)}h` },
  ];

  return (
    <div>
      <h1 className="text-2xl font-bold">Panel de aprendizaje</h1>
      <p className="mt-1 text-[var(--aliaa-muted-foreground)]">
        Seguí tu progreso y continuá aprendiendo
      </p>

      <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.label}>
              <CardContent className="flex items-center gap-4 p-6">
                <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-[var(--aliaa-primary)]/10">
                  <Icon className="h-6 w-6 text-[var(--aliaa-primary)]" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{stat.value}</p>
                  <p className="text-xs text-[var(--aliaa-muted-foreground)]">{stat.label}</p>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <Card className="mt-8">
        <CardHeader>
          <CardTitle>Mis cursos en progreso</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {enrollments.length === 0 ? (
            <div className="text-center">
              <p className="text-[var(--aliaa-muted-foreground)]">
                Todavía no estás inscrito en ningún curso.
              </p>
              <Link href="/cursos" className="mt-4 inline-block">
                <Button>Explorar cursos</Button>
              </Link>
            </div>
          ) : (
            enrollments.map((enrollment) => (
              <div key={enrollment.id}>
                <div className="mb-2 flex items-center justify-between">
                  <h3 className="font-medium">{enrollment.course?.titulo}</h3>
                  <Link href={`/dashboard/cursos/${enrollment.course_id}`}>
                    <Button size="sm" variant="outline">
                      {enrollment.progreso_porcentaje >= 100 ? "Revisar" : "Continuar"}
                    </Button>
                  </Link>
                </div>
                <Progress value={enrollment.progreso_porcentaje} showLabel />
              </div>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  );
}
