import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { ROLE_LABELS } from "@/lib/constants";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Usuarios",
};

const USERS = [
  { id: "1", nombre: "María González", email: "maria@email.com", rol: "alumno", pais: "Argentina" },
  { id: "2", nombre: "Prof. Carlos Ruiz", email: "carlos@aliaa.edu", rol: "docente", pais: "México" },
  { id: "3", nombre: "Ana Martínez", email: "ana@email.com", rol: "alumno", pais: "Colombia" },
  { id: "4", nombre: "Admin ALIAA", email: "admin@aliaa.edu", rol: "admin", pais: "Argentina" },
];

const ROLE_VARIANT: Record<string, "default" | "secondary" | "success"> = {
  admin: "default",
  docente: "secondary",
  alumno: "success",
};

export default function AdminUsuariosPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold">Gestión de Usuarios</h1>
      <p className="mt-1 text-[var(--aliaa-muted-foreground)]">
        Administrá los usuarios de la plataforma
      </p>

      <div className="mt-6">
        <Input placeholder="Buscar por nombre o email..." className="max-w-sm" />
      </div>

      <Card className="mt-6">
        <CardContent className="p-0">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[var(--aliaa-border)] text-left">
                <th className="p-4 font-medium">Nombre</th>
                <th className="p-4 font-medium">Email</th>
                <th className="p-4 font-medium">Rol</th>
                <th className="p-4 font-medium">País</th>
              </tr>
            </thead>
            <tbody>
              {USERS.map((user) => (
                <tr key={user.id} className="border-b border-[var(--aliaa-border)] last:border-0">
                  <td className="p-4 font-medium">{user.nombre}</td>
                  <td className="p-4 text-[var(--aliaa-muted-foreground)]">{user.email}</td>
                  <td className="p-4">
                    <Badge variant={ROLE_VARIANT[user.rol]}>
                      {ROLE_LABELS[user.rol]}
                    </Badge>
                  </td>
                  <td className="p-4 text-[var(--aliaa-muted-foreground)]">{user.pais}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  );
}
