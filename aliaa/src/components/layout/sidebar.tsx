"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  BookOpen,
  Award,
  MessageSquare,
  Users,
  CreditCard,
  Settings,
  GraduationCap,
  BarChart3,
} from "lucide-react";
import { SITE_NAME } from "@/lib/constants";
import { cn } from "@/lib/utils";
import type { UserRole } from "@/types/database";

interface SidebarProps {
  role: UserRole;
  /** En /dashboard siempre "student"; en /admin siempre "admin" */
  mode?: "student" | "admin";
}

const studentLinks = [
  { href: "/dashboard", label: "Panel", icon: LayoutDashboard },
  { href: "/dashboard/cursos", label: "Mis Cursos", icon: BookOpen },
  { href: "/dashboard/certificados", label: "Certificados", icon: Award },
  { href: "/dashboard/perfil", label: "Mi perfil", icon: Users },
  { href: "/dashboard/foros", label: "Foros", icon: MessageSquare },
];

const teacherLinks = [
  { href: "/dashboard", label: "Panel", icon: LayoutDashboard },
  { href: "/dashboard/cursos", label: "Mis Cursos", icon: BookOpen },
  { href: "/dashboard/estudiantes", label: "Estudiantes", icon: Users },
  { href: "/dashboard/foros", label: "Foros", icon: MessageSquare },
];

const adminLinks = [
  { href: "/admin", label: "Administración", icon: BarChart3 },
  { href: "/admin/cursos", label: "Gestionar Cursos", icon: BookOpen },
  { href: "/admin/usuarios", label: "Usuarios", icon: Users },
  { href: "/admin/pagos", label: "Pagos", icon: CreditCard },
  { href: "/admin/configuracion", label: "Configuración", icon: Settings },
];

export function Sidebar({ role, mode = "student" }: SidebarProps) {
  const pathname = usePathname();

  const links =
    mode === "admin"
      ? adminLinks
      : role === "docente"
        ? teacherLinks
        : studentLinks;

  return (
    <aside className="hidden w-64 shrink-0 border-r border-[var(--aliaa-border)] bg-[var(--aliaa-card)] lg:block">
      <Link
        href="/"
        className="flex h-16 items-center gap-2 border-b border-[var(--aliaa-border)] px-6 transition-colors hover:bg-[var(--aliaa-muted)]"
        title="Ir a la página principal de ALIAA"
      >
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[var(--aliaa-primary)]">
          <GraduationCap className="h-4 w-4 text-white" />
        </div>
        <div>
          <span className="font-semibold">{SITE_NAME}</span>
          <p className="text-[10px] leading-tight text-[var(--aliaa-muted-foreground)]">
            Página principal
          </p>
        </div>
      </Link>
      <nav className="space-y-1 p-4">
        {links.map((link) => {
          const Icon = link.icon;
          const active = pathname === link.href || pathname.startsWith(link.href + "/");
          return (
            <Link
              key={link.href}
              href={link.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                active
                  ? "bg-[var(--aliaa-primary)]/10 text-[var(--aliaa-primary)]"
                  : "text-[var(--aliaa-muted-foreground)] hover:bg-[var(--aliaa-muted)] hover:text-[var(--aliaa-foreground)]"
              )}
            >
              <Icon className="h-4 w-4" />
              {link.label}
            </Link>
          );
        })}
        {mode === "student" && role === "admin" && (
          <Link
            href="/admin"
            className={cn(
              "mt-4 flex items-center gap-3 rounded-lg border border-[var(--aliaa-border)] px-3 py-2.5 text-sm font-medium transition-colors",
              pathname.startsWith("/admin")
                ? "bg-[var(--aliaa-primary)]/10 text-[var(--aliaa-primary)]"
                : "text-[var(--aliaa-muted-foreground)] hover:bg-[var(--aliaa-muted)] hover:text-[var(--aliaa-foreground)]"
            )}
          >
            <BarChart3 className="h-4 w-4" />
            Administración
          </Link>
        )}
      </nav>
    </aside>
  );
}
