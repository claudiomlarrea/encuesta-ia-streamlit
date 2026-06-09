"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface EnrollButtonProps {
  courseId: string;
  label?: string;
  defaultName?: string;
}

export function EnrollButton({
  courseId,
  label = "Comenzar curso",
  defaultName = "",
}: EnrollButtonProps) {
  const router = useRouter();
  const [nombreCertificado, setNombreCertificado] = useState(defaultName);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleEnroll(e: React.FormEvent) {
    e.preventDefault();
    const nombre = nombreCertificado.trim();
    if (nombre.length < 3) {
      setError("Ingresá tu nombre completo tal como debe figurar en el certificado.");
      return;
    }

    setLoading(true);
    setError("");
    const res = await fetch("/api/enrollments", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ courseId, nombreCertificado: nombre }),
    });
    setLoading(false);

    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      setError(data.error || "No se pudo completar la inscripción.");
      return;
    }

    router.push(`/dashboard/cursos/${courseId}`);
  }

  return (
    <form onSubmit={handleEnroll} className="space-y-3">
      {error && (
        <div className="rounded-lg bg-red-50 p-3 text-sm text-red-600 dark:bg-red-900/20 dark:text-red-400">
          {error}
        </div>
      )}
      <div>
        <label htmlFor={`cert-name-${courseId}`} className="mb-1.5 block text-sm font-medium">
          Nombre completo para el certificado
        </label>
        <Input
          id={`cert-name-${courseId}`}
          value={nombreCertificado}
          onChange={(e) => setNombreCertificado(e.target.value)}
          placeholder="Ej: María del Carmen González Pérez"
          required
        />
        <p className="mt-1.5 text-xs text-[var(--aliaa-muted-foreground)]">
          Escribí todos tus nombres y apellidos. Así figurarán en el certificado de este curso.
        </p>
      </div>
      <Button type="submit" className="w-full" disabled={loading}>
        {loading ? "Inscribiendo..." : label}
      </Button>
    </form>
  );
}
