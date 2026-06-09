"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase/client";
import { looksLikeEmailUsername } from "@/lib/profile-name";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";

interface ProfileNameFormProps {
  initialName: string;
  email: string;
}

export function ProfileNameForm({ initialName, email }: ProfileNameFormProps) {
  const router = useRouter();
  const [nombre, setNombre] = useState(
    looksLikeEmailUsername(initialName, email) ? "" : initialName
  );
  const [loading, setLoading] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const trimmed = nombre.trim();
    if (trimmed.length < 3) {
      setError("Ingresá tu nombre completo.");
      return;
    }

    setLoading(true);
    setError("");
    const supabase = createClient();
    const {
      data: { user },
    } = await supabase.auth.getUser();
    if (!user) {
      setError("Sesión expirada. Volvé a ingresar.");
      setLoading(false);
      return;
    }

    const { error: updateError } = await supabase
      .from("profiles")
      .update({ nombre_completo: trimmed })
      .eq("id", user.id);

    if (updateError) {
      setError("No se pudo guardar. Intentá de nuevo.");
      setLoading(false);
      return;
    }

    setSaved(true);
    setLoading(false);
    router.refresh();
  }

  return (
    <Card>
      <CardContent className="p-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="rounded-lg bg-red-50 p-3 text-sm text-red-600 dark:bg-red-900/20 dark:text-red-400">
              {error}
            </div>
          )}
          {saved && (
            <div className="rounded-lg bg-emerald-50 p-3 text-sm text-emerald-800 dark:bg-emerald-900/20 dark:text-emerald-300">
              Nombre actualizado. Tus certificados mostrarán este nombre.
            </div>
          )}
          <div>
            <label htmlFor="email" className="mb-1.5 block text-sm font-medium">
              Correo
            </label>
            <Input id="email" value={email} disabled />
          </div>
          <div>
            <label htmlFor="nombre" className="mb-1.5 block text-sm font-medium">
              Nombre completo (como querés que figure en el certificado)
            </label>
            <Input
              id="nombre"
              value={nombre}
              onChange={(e) => setNombre(e.target.value)}
              placeholder="Ej: Claudio Alberto Larrea Méndez"
              required
            />
          </div>
          <Button type="submit" disabled={loading}>
            {loading ? "Guardando..." : "Guardar nombre"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
