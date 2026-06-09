"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { createClient } from "@/lib/supabase/client";
import { OAuthButtons } from "@/components/auth/oauth-buttons";
import { MagicLinkForm } from "@/components/auth/magic-link-form";
import { AuthDivider } from "@/components/auth/auth-divider";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const redirect = searchParams.get("redirect") || "/dashboard";
  const oauthError = searchParams.get("error") === "oauth";
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(oauthError ? "No se pudo completar el inicio de sesión. Intentá de nuevo." : "");
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");

    const supabase = createClient();
    const { error: authError } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    if (authError) {
      setError(
        authError.message === "Invalid login credentials"
          ? "Credenciales incorrectas. Verificá tu email y contraseña."
          : authError.message
      );
      setLoading(false);
      return;
    }

    router.push(redirect);
    router.refresh();
  }

  return (
    <Card className="w-full max-w-md">
      <CardHeader className="text-center">
        <CardTitle className="text-2xl">Ingresar a ALIAA</CardTitle>
        <CardDescription>Entrá en segundos con Google, Microsoft o tu correo</CardDescription>
      </CardHeader>
      <CardContent>
        <OAuthButtons redirect={redirect} />
        <AuthDivider label="o con tu correo" />
        <MagicLinkForm redirect={redirect} buttonLabel="Enviar enlace de acceso" />

        <AuthDivider label="o con contraseña" />
        {!showPassword ? (
          <button
            type="button"
            onClick={() => setShowPassword(true)}
            className="w-full text-center text-sm text-[var(--aliaa-primary)] hover:underline"
          >
            Ingresar con email y contraseña
          </button>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="rounded-lg bg-red-50 p-3 text-sm text-red-600 dark:bg-red-900/20 dark:text-red-400">
                {error}
              </div>
            )}
            <div>
              <label htmlFor="email" className="mb-1.5 block text-sm font-medium">
                Correo electrónico
              </label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="tu@email.com"
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
                placeholder="••••••••"
                required
              />
            </div>
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Ingresando..." : "Ingresar"}
            </Button>
          </form>
        )}

        <p className="mt-6 text-center text-sm text-[var(--aliaa-muted-foreground)]">
          ¿No tenés cuenta?{" "}
          <Link href="/registro" className="font-medium text-[var(--aliaa-primary)] hover:underline">
            Registrate gratis
          </Link>
        </p>
      </CardContent>
    </Card>
  );
}
