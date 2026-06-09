"use client";

import { useState } from "react";
import { Mail } from "lucide-react";
import { createClient } from "@/lib/supabase/client";
import { magicLinkErrorMessage } from "@/lib/auth-messages";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface MagicLinkFormProps {
  redirect?: string;
  buttonLabel?: string;
  /** Pedir nombre completo (registro) para certificados */
  requireName?: boolean;
}

export function MagicLinkForm({
  redirect = "/dashboard",
  buttonLabel = "Enviar enlace a mi correo",
  requireName = false,
}: MagicLinkFormProps) {
  const [nombre, setNombre] = useState("");
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState("");

  async function handleSend(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");

    const supabase = createClient();
    const redirectTo = `${window.location.origin}/auth/callback?next=${encodeURIComponent(redirect)}`;

    if (requireName && nombre.trim().length < 3) {
      setError("Ingresá tu nombre y apellido.");
      setLoading(false);
      return;
    }

    const { error: authError } = await supabase.auth.signInWithOtp({
      email,
      options: {
        emailRedirectTo: redirectTo,
        shouldCreateUser: true,
        data: requireName ? { nombre_completo: nombre.trim() } : undefined,
      },
    });

    if (authError) {
      setError(magicLinkErrorMessage(authError.message));
      setLoading(false);
      return;
    }

    setSent(true);
    setLoading(false);
  }

  if (sent) {
    return (
      <div className="rounded-lg border border-emerald-500/40 bg-emerald-50 p-4 text-sm text-emerald-800 dark:bg-emerald-900/20 dark:text-emerald-300">
        <p className="font-medium">Revisá tu bandeja de entrada</p>
        <p className="mt-1">
          Enviamos un enlace a <strong>{email}</strong>. Hacé clic para entrar sin contraseña.
          Si no lo ves, revisá la carpeta de spam.
        </p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSend} className="space-y-3">
      {error && (
        <div className="rounded-lg bg-red-50 p-3 text-sm text-red-600 dark:bg-red-900/20 dark:text-red-400">
          {error}
        </div>
      )}
      {requireName && (
        <div>
          <label htmlFor="magic-nombre" className="mb-1.5 block text-sm font-medium">
            Nombre completo
          </label>
          <Input
            id="magic-nombre"
            value={nombre}
            onChange={(e) => setNombre(e.target.value)}
            placeholder="Ej: María del Carmen González Pérez"
            required
          />
        </div>
      )}
      <div>
        <label htmlFor="magic-email" className="mb-1.5 block text-sm font-medium">
          Tu correo (Gmail, Hotmail u otro)
        </label>
        <Input
          id="magic-email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="tu@gmail.com"
          required
        />
      </div>
      <Button type="submit" className="w-full gap-2" disabled={loading}>
        <Mail className="h-4 w-4" />
        {loading ? "Enviando..." : buttonLabel}
      </Button>
    </form>
  );
}
