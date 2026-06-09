import { Suspense } from "react";
import { LoginForm } from "@/components/auth/login-form";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Ingresar",
};

export default function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-[var(--aliaa-muted)] px-4">
      <Suspense>
        <LoginForm />
      </Suspense>
    </div>
  );
}
