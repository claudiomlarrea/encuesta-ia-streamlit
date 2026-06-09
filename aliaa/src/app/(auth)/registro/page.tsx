import { RegisterForm } from "@/components/auth/register-form";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Registrarse",
};

export default function RegistroPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-[var(--aliaa-muted)] px-4 py-12">
      <RegisterForm />
    </div>
  );
}
