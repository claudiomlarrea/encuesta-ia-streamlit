import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { CONTACT_EMAIL, SITE_FULL_NAME } from "@/lib/constants";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Configuración",
};

export default function AdminConfigPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold">Configuración</h1>
      <p className="mt-1 text-[var(--aliaa-muted-foreground)]">
        Ajustes generales de la plataforma
      </p>

      <div className="mt-8 space-y-6 max-w-2xl">
        <Card>
          <CardHeader>
            <CardTitle>Información institucional</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="mb-1.5 block text-sm font-medium">Nombre de la academia</label>
              <Input defaultValue={SITE_FULL_NAME} />
            </div>
            <div>
              <label className="mb-1.5 block text-sm font-medium">Email de contacto</label>
              <Input defaultValue={CONTACT_EMAIL} />
            </div>
            <Button>Guardar cambios</Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Integraciones de pago</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="mb-1.5 block text-sm font-medium">Mercado Pago Access Token</label>
              <Input type="password" placeholder="APP_USR-..." />
            </div>
            <div>
              <label className="mb-1.5 block text-sm font-medium">PayPal Client ID</label>
              <Input placeholder="Client ID de PayPal" />
            </div>
            <Button>Guardar integraciones</Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
