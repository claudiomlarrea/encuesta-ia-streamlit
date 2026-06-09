import { redirect } from "next/navigation";
import { Sidebar } from "@/components/layout/sidebar";
import { ThemeToggle } from "@/components/layout/theme-toggle";
import { getProfile } from "@/lib/supabase/server";
import { LogOut } from "lucide-react";

export default async function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const profile = await getProfile();
  if (!profile) redirect("/login");
  if (profile.rol !== "admin") redirect("/dashboard");

  return (
    <div className="flex min-h-screen">
      <Sidebar role="admin" mode="admin" />
      <div className="flex flex-1 flex-col">
        <header className="flex h-16 items-center justify-between border-b border-[var(--aliaa-border)] px-6">
          <div>
            <p className="text-sm text-[var(--aliaa-muted-foreground)]">Panel de administración</p>
            <p className="font-semibold">{profile.nombre_completo}</p>
          </div>
          <div className="flex items-center gap-2">
            <ThemeToggle />
            <form action="/api/auth/signout" method="POST">
              <button
                type="submit"
                className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-[var(--aliaa-muted-foreground)] hover:bg-[var(--aliaa-muted)]"
              >
                <LogOut className="h-4 w-4" />
                Salir
              </button>
            </form>
          </div>
        </header>
        <main className="flex-1 overflow-auto p-6">{children}</main>
      </div>
    </div>
  );
}
