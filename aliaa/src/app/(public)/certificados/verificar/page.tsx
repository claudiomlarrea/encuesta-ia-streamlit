"use client";

import { useState } from "react";
import { useSearchParams } from "next/navigation";
import { Suspense } from "react";
import { Search, CheckCircle, XCircle, Award } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { formatDate } from "@/lib/utils";

function VerificarContent() {
  const searchParams = useSearchParams();
  const [codigo, setCodigo] = useState(searchParams.get("codigo") || "");
  const [resultado, setResultado] = useState<{
    valido: boolean;
    estudiante?: string;
    curso?: string;
    fecha?: string;
  } | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleVerificar(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await fetch(`/api/certificates/verify/${encodeURIComponent(codigo)}`);
      const data = await res.json();
      setResultado(data);
    } catch {
      setResultado({ valido: false });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-lg px-4 py-16">
      <div className="text-center">
        <Award className="mx-auto mb-4 h-12 w-12 text-[var(--aliaa-primary)]" />
        <h1 className="text-2xl font-bold">Verificar Certificado</h1>
        <p className="mt-2 text-[var(--aliaa-muted-foreground)]">
          Ingresá el código de verificación para validar un certificado ALIAA
        </p>
      </div>

      <form onSubmit={handleVerificar} className="mt-8 flex gap-2">
        <Input
          value={codigo}
          onChange={(e) => setCodigo(e.target.value.toUpperCase())}
          placeholder="ALIAA-XXXXXXXX"
          className="font-mono"
          required
        />
        <Button type="submit" disabled={loading}>
          <Search className="h-4 w-4" />
        </Button>
      </form>

      {resultado && (
        <Card className="mt-6">
          <CardContent className="p-6 text-center">
            {resultado.valido ? (
              <>
                <CheckCircle className="mx-auto mb-3 h-10 w-10 text-emerald-500" />
                <p className="font-semibold text-emerald-600">Certificado válido</p>
                <div className="mt-4 space-y-1 text-sm">
                  <p><strong>Estudiante:</strong> {resultado.estudiante}</p>
                  <p><strong>Curso:</strong> {resultado.curso}</p>
                  <p><strong>Emitido:</strong> {resultado.fecha && formatDate(resultado.fecha)}</p>
                </div>
              </>
            ) : (
              <>
                <XCircle className="mx-auto mb-3 h-10 w-10 text-red-500" />
                <p className="font-semibold text-red-600">Certificado no encontrado</p>
                <p className="mt-2 text-sm text-[var(--aliaa-muted-foreground)]">
                  Verificá que el código sea correcto e intentá nuevamente.
                </p>
              </>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}

export default function VerificarCertificadoPage() {
  return (
    <Suspense>
      <VerificarContent />
    </Suspense>
  );
}
