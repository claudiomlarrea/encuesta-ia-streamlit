import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { formatPrice, formatDate } from "@/lib/utils";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Pagos",
};

const PAYMENTS = [
  { id: "1", usuario: "María González", curso: "IA Generativa con LLMs", monto: 79.99, proveedor: "mercadopago", estado: "completado", fecha: "2025-12-08T10:00:00Z" },
  { id: "2", usuario: "Carlos Ruiz", curso: "Fundamentos de ML", monto: 49.99, proveedor: "paypal", estado: "completado", fecha: "2025-12-07T15:30:00Z" },
  { id: "3", usuario: "Ana Martínez", curso: "Deep Learning", monto: 89.99, proveedor: "mercadopago", estado: "pendiente", fecha: "2025-12-09T08:00:00Z" },
];

const STATUS_VARIANT: Record<string, "success" | "warning" | "destructive"> = {
  completado: "success",
  pendiente: "warning",
  fallido: "destructive",
};

export default function AdminPagosPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold">Gestión de Pagos</h1>
      <p className="mt-1 text-[var(--aliaa-muted-foreground)]">
        Historial de transacciones de Mercado Pago y PayPal
      </p>

      <Card className="mt-8">
        <CardContent className="p-0">
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
              {PAYMENTS.map((payment) => (
                <tr key={payment.id} className="border-b border-[var(--aliaa-border)] last:border-0">
                  <td className="p-4 font-medium">{payment.usuario}</td>
                  <td className="p-4">{payment.curso}</td>
                  <td className="p-4">{formatPrice(payment.monto)}</td>
                  <td className="p-4 capitalize">{payment.proveedor}</td>
                  <td className="p-4">
                    <Badge variant={STATUS_VARIANT[payment.estado]}>
                      {payment.estado}
                    </Badge>
                  </td>
                  <td className="p-4 text-[var(--aliaa-muted-foreground)]">
                    {formatDate(payment.fecha)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  );
}
