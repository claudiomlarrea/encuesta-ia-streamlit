import { redirect } from "next/navigation";
import { getProfile } from "@/lib/supabase/server";
import { ProfileNameForm } from "@/components/dashboard/profile-name-form";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Mi perfil",
};

export default async function PerfilPage() {
  const profile = await getProfile();
  if (!profile) redirect("/login");

  return (
    <div className="mx-auto max-w-lg">
      <h1 className="text-2xl font-bold">Mi perfil</h1>
      <p className="mt-1 text-[var(--aliaa-muted-foreground)]">
        Este nombre aparece en tus certificados ALIAA
      </p>
      <div className="mt-8">
        <ProfileNameForm
          initialName={profile.nombre_completo ?? ""}
          email={profile.email}
        />
      </div>
    </div>
  );
}
