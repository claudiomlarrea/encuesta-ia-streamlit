"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { createClient } from "@/lib/supabase/client";
import { OAuthButtons } from "@/components/auth/oauth-buttons";
import { MagicLinkForm } from "@/components/auth/magic-link-form";
import { AuthDivider } from "@/components/auth/auth-divider";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export function RegisterForm() {
  const router = useRouter();
  const [nombre, setNombre] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showPasswordForm, setShowPasswordForm] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");

    if (password.length < 8) {
      setError("La contraseña debe tener al menos 8 caracteres.");
      setLoading(false);
      return;
    }

    const supabase = createClient();
    const { error: authError } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: { nombre_completo: nombre },
      },
    });

    if (authError) {
      const messages: Record<string, string> = {
        "User already registered": "Este email ya está registrado. Probá ingresar.",
        "Database error saving new user": "Error al crear el perfil. Contactá al administrador.",
      };
      setError(messages[authError.message] ?? authError.message);
      setLoading(false);
      return;
    }

    router.push("/dashboard");
    router.refresh();
  }

  return (
    <Card className="w-full max-w-md">
      <CardHeader className="text-center">
        <CardTitle className="text-2xl">Crear cuenta</CardTitle>
        <CardDescription>
          Registrate en segundos — sin formularios largos
        </CardDescription>
      </CardHeader>
      <CardContent>
        <OAuthButtons redirect="/dashboard" />
        <AuthDivider label="o con tu correo" />
        <MagicLinkForm requireName buttonLabel="Crear cuenta con enlace mágico" />

        <AuthDivider label="o con contraseña" />
        {!showPasswordForm ? (
          <button
            type="button"
            onClick={() => setShowPasswordForm(true)}
            className="w-full text-center text-sm text-[var(--aliaa-primary)] hover:underline"
          >
            Preferís registrarte con contraseña
          </button>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="rounded-lg bg-red-50 p-3 text-sm text-red-600 dark:bg-red-900/20 dark:text-red-400">
                {error}
              </div>
            )}
            <div>
              <label htmlFor="nombre" className="mb-1.5 block text-sm font-medium">
                Nombre completo
              </label>
              <Input
                id="nombre"
                value={nombre}
                onChange={(e) => setNombre(e.target.value)}
                placeholder="Tu nombre"
                required
              />
            </div>
            <div>
              <label htmlFor="email" className="mb-1.5 block text-sm font-medium">
                Correo electrónico
              </label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="tu@gmail.com"
                required
              />
            </div>
            <div>
              <label htmlFor="password" className="mb-1.5 block text-sm font-medium">
                Contraseña
              </label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Mínimo 8 caracteres"
                required
              />
            </div>
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Creando cuenta..." : "Registrarse"}
            </Button>
          </form>
        )}

        <p className="mt-6 text-center text-sm text-[var(--aliaa-muted-foreground)]">
          ¿Ya tenés cuenta?{" "}
          <Link href="/login" className="font-medium text-[var(--aliaa-primary)] hover:underline">
            Ingresar
          </Link>
        </p>
      </CardContent>
    </Card>
  );
}
