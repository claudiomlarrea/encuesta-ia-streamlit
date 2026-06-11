import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { formatPrice, formatDate } from "@/lib/utils";
import { createAdminClient, requireAdmin } from "@/lib/supabase/admin";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Pagos",
};

const STATUS_VARIANT: Record<string, "success" | "warning" | "destructive"> = {
  completado: "success",
  pendiente: "warning",
  fallido: "destructive",
  reembolsado: "warning",
};

export default async function AdminPagosPage() {
  await requireAdmin();
  const supabase = createAdminClient();

  const { data: payments } = await supabase
    .from("payments")
    .select(
      "id, monto, moneda, proveedor, estado, created_at, profile:profiles(nombre_completo, email), course:courses(titulo)"
    )
    .order("created_at", { ascending: false });

  const rows = payments ?? [];

  return (
    <div>
      <h1 className="text-2xl font-bold">Gestión de Pagos</h1>
      <p className="mt-1 text-[var(--aliaa-muted-foreground)]">
        {rows.length === 0
          ? "Sin transacciones aún. Los cursos actuales son gratuitos."
          : `${rows.length} transacción${rows.length === 1 ? "" : "es"} de Mercado Pago y PayPal`}
      </p>

      <Card className="mt-8">
        <CardContent className="p-0">
          {rows.length === 0 ? (
            <p className="p-8 text-center text-[var(--aliaa-muted-foreground)]">
              Cuando alguien pague un curso de pago, el registro aparecerá acá.
            </p>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[var(--aliaa-border)] text-left">
                  <th className="p-4 font-medium">Usuario</th>
                  <th className="p-4 font-medium">Curso</th>
                  <th className="p-4 font-medium">Monto</th>
                  <th className="p-4 font-medium">Proveedor</th>
                  <th className="p-4 font-medium">Estado</th>
                  <th className="p-4 font-medium">Fecha</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((payment) => {
                  const profile = payment.profile as {
                    nombre_completo?: string;
                    email?: string;
                  } | null;
                  const course = payment.course as { titulo?: string } | null;
                  const nombre =
                    profile?.nombre_completo || profile?.email || "—";

                  return (
                    <tr
                      key={payment.id}
                      className="border-b border-[var(--aliaa-border)] last:border-0"
                    >
                      <td className="p-4 font-medium">{nombre}</td>
                      <td className="p-4">{course?.titulo || "—"}</td>
                      <td className="p-4">
                        {formatPrice(Number(payment.monto), payment.moneda)}
                      </td>
                      <td className="p-4 capitalize">{payment.proveedor}</td>
                      <td className="p-4">
                        <Badge
                          variant={
                            STATUS_VARIANT[payment.estado] ?? "warning"
                          }
                        >
                          {payment.estado}
                        </Badge>
                      </td>
                      <td className="p-4 text-[var(--aliaa-muted-foreground)]">
                        {formatDate(payment.created_at)}
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
