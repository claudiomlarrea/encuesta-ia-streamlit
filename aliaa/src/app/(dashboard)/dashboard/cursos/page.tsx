import Link from "next/link";
import { BookOpen } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { getUserEnrollments } from "@/lib/enrollments";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Mis Cursos",
};

export default async function MisCursosPage() {
  const enrollments = await getUserEnrollments();

  return (
    <div>
      <h1 className="text-2xl font-bold">Mis Cursos</h1>
      <p className="mt-1 text-[var(--aliaa-muted-foreground)]">
        Accedé a tus cursos inscritos y continuá aprendiendo
      </p>

      {enrollments.length === 0 ? (
        <Card className="mt-8">
          <CardContent className="py-12 text-center">
            <p className="text-[var(--aliaa-muted-foreground)]">
              Todavía no estás inscrito en ningún curso.
            </p>
            <Link href="/cursos" className="mt-4 inline-block">
              <Button>Explorar cursos</Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="mt-8 space-y-4">
          {enrollments.map((enrollment) => (
            <Card key={enrollment.id}>
              <CardContent className="flex items-center gap-4 p-6">
                <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-lg bg-[var(--aliaa-primary)]/10">
                  <BookOpen className="h-7 w-7 text-[var(--aliaa-primary)]" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold">{enrollment.course?.titulo}</h3>
                    {enrollment.course?.categoria && (
                      <Badge variant="secondary">{enrollment.course.categoria}</Badge>
                    )}
                    {enrollment.progreso_porcentaje >= 100 && (
                      <Badge variant="success">Completado</Badge>
                    )}
                  </div>
                  <div className="mt-3 max-w-md">
                    <Progress value={enrollment.progreso_porcentaje} showLabel />
                  </div>
                </div>
                <Link href={`/dashboard/cursos/${enrollment.course_id}`}>
                  <Button>
                    {enrollment.progreso_porcentaje >= 100 ? "Revisar" : "Continuar"}
                  </Button>
                </Link>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
