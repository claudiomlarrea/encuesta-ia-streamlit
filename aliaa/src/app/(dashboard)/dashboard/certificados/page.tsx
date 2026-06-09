import Link from "next/link";
import { Award, ExternalLink } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { formatDate } from "@/lib/utils";
import { getUserCertificates } from "@/lib/certificates";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Certificados",
};

export default async function CertificadosPage() {
  const certificates = await getUserCertificates();

  return (
    <div>
      <h1 className="text-2xl font-bold">Mis Certificados</h1>
      <p className="mt-1 text-[var(--aliaa-muted-foreground)]">
        Descargá y compartí tus certificados verificables
      </p>

      {certificates.length === 0 ? (
        <Card className="mt-8">
          <CardContent className="flex flex-col items-center py-12 text-center">
            <Award className="mb-4 h-12 w-12 text-[var(--aliaa-muted-foreground)]" />
            <p className="text-[var(--aliaa-muted-foreground)]">
              Aún no tenés certificados. Completá un curso para obtener el tuyo.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="mt-8 space-y-4">
          {certificates.map((cert) => (
            <Card key={cert.id}>
              <CardContent className="flex items-center gap-4 p-6">
                <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-lg bg-[var(--aliaa-primary)]/10">
                  <Award className="h-7 w-7 text-[var(--aliaa-primary)]" />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold">{cert.course?.titulo}</h3>
                  <p className="text-sm text-[var(--aliaa-muted-foreground)]">
                    Código: {cert.codigo_verificacion} · Emitido:{" "}
                    {formatDate(cert.emitido_en)}
                  </p>
                </div>
                <Link href={`/dashboard/certificados/${cert.id}`}>
                  <Button variant="outline">
                    <ExternalLink className="mr-2 h-4 w-4" />
                    Ver certificado
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
