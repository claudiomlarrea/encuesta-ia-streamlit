import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { ROLE_LABELS } from "@/lib/constants";
import { formatDate } from "@/lib/utils";
import { createAdminClient, requireAdmin } from "@/lib/supabase/admin";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Usuarios",
};

const ROLE_VARIANT: Record<string, "default" | "secondary" | "success"> = {
  admin: "default",
  docente: "secondary",
  alumno: "success",
};

export default async function AdminUsuariosPage() {
  await requireAdmin();
  const supabase = createAdminClient();

  const [{ data: profiles }, { data: enrollments }] = await Promise.all([
    supabase
      .from("profiles")
      .select("id, nombre_completo, email, rol, pais, created_at")
      .order("created_at", { ascending: false }),
    supabase
      .from("enrollments")
      .select("id, user_id, progreso_porcentaje, inscrito_en, course:courses(titulo)"),
  ]);

  const users = profiles ?? [];
  const enrollmentsByUser = new Map<string, typeof enrollments>();

  for (const enrollment of enrollments ?? []) {
    const list = enrollmentsByUser.get(enrollment.user_id) ?? [];
    list.push(enrollment);
    enrollmentsByUser.set(enrollment.user_id, list);
  }

  return (
    <div>
      <h1 className="text-2xl font-bold">Gestión de Usuarios</h1>
      <p className="mt-1 text-[var(--aliaa-muted-foreground)]">
        {users.length} usuario{users.length === 1 ? "" : "s"} registrado
        {users.length === 1 ? "" : "s"} en la plataforma
      </p>

      <Card className="mt-6">
        <CardContent className="p-0">
          {users.length === 0 ? (
            <p className="p-8 text-center text-[var(--aliaa-muted-foreground)]">
              Aún no hay usuarios. Cuando alguien se registre, aparecerá acá.
            </p>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[var(--aliaa-border)] text-left">
                  <th className="p-4 font-medium">Nombre</th>
                  <th className="p-4 font-medium">Email</th>
                  <th className="p-4 font-medium">Rol</th>
                  <th className="p-4 font-medium">Inscripciones</th>
                  <th className="p-4 font-medium">Registro</th>
                  <th className="p-4 font-medium">País</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => {
                  const userEnrollments = enrollmentsByUser.get(user.id) ?? [];

                  return (
                    <tr key={user.id} className="border-b border-[var(--aliaa-border)] last:border-0">
                      <td className="p-4 font-medium">
                        {user.nombre_completo || "—"}
                      </td>
                      <td className="p-4 text-[var(--aliaa-muted-foreground)]">{user.email}</td>
                      <td className="p-4">
                        <Badge variant={ROLE_VARIANT[user.rol] ?? "success"}>
                          {ROLE_LABELS[user.rol] ?? user.rol}
                        </Badge>
                      </td>
                      <td className="p-4">
                        {userEnrollments.length === 0 ? (
                          <span className="text-[var(--aliaa-muted-foreground)]">Sin inscripción</span>
                        ) : (
                          <ul className="space-y-1">
                            {userEnrollments.map((enrollment) => {
                              const course = enrollment.course as { titulo?: string } | null;
                              return (
                                <li key={enrollment.id} className="text-sm">
                                  <span className="font-medium">{course?.titulo ?? "Curso"}</span>
                                  <span className="text-[var(--aliaa-muted-foreground)]">
                                    {" "}
                                    · {Math.round(enrollment.progreso_porcentaje)}%
                                  </span>
                                </li>
                              );
                            })}
                          </ul>
                        )}
                      </td>
                      <td className="p-4 text-[var(--aliaa-muted-foreground)]">
                        {formatDate(user.created_at)}
                      </td>
                      <td className="p-4 text-[var(--aliaa-muted-foreground)]">
                        {user.pais || "—"}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
