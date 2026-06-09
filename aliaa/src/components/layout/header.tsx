"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Menu, X, GraduationCap, LogOut } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/layout/theme-toggle";
import { NAV_LINKS, SITE_NAME } from "@/lib/constants";
import { cn } from "@/lib/utils";
import type { Profile } from "@/types/database";

interface HeaderProps {
  profile?: Profile | null;
}

export function Header({ profile }: HeaderProps) {
  const [open, setOpen] = useState(false);
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-50 border-b border-[var(--aliaa-border)] bg-[var(--aliaa-background)]/80 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Link href="/" className="flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[var(--aliaa-primary)]">
            <GraduationCap className="h-5 w-5 text-white" />
          </div>
          <div className="hidden sm:block">
            <span className="text-lg font-bold text-[var(--aliaa-foreground)]">{SITE_NAME}</span>
            <p className="text-[10px] leading-tight text-[var(--aliaa-muted-foreground)]">
              Inteligencia Artificial Aplicada
            </p>
          </div>
        </Link>

        <nav className="hidden items-center gap-6 md:flex">
          {NAV_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={cn(
                "text-sm font-medium transition-colors hover:text-[var(--aliaa-primary)]",
                pathname === link.href
                  ? "text-[var(--aliaa-primary)]"
                  : "text-[var(--aliaa-muted-foreground)]"
              )}
            >
              {link.label}
            </Link>
          ))}
        </nav>

        <div className="flex items-center gap-2">
          <ThemeToggle />
          {profile ? (
            <>
              <Link href="/dashboard">
                <Button variant="outline" size="sm">
                  Mi Panel
                </Button>
              </Link>
              <form action="/api/auth/signout" method="POST" className="hidden sm:block">
                <Button type="submit" variant="ghost" size="sm" className="gap-1.5">
                  <LogOut className="h-4 w-4" />
                  Salir
                </Button>
              </form>
            </>
          ) : (
            <>
              <Link href="/login" className="hidden sm:block">
                <Button variant="ghost" size="sm">
                  Ingresar
                </Button>
              </Link>
              <Link href="/registro">
                <Button size="sm">Registrarse</Button>
              </Link>
            </>
          )}
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden"
            onClick={() => setOpen(!open)}
            aria-label="Menú"
          >
            {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </Button>
        </div>
      </div>

      {open && (
        <nav className="border-t border-[var(--aliaa-border)] px-4 py-4 md:hidden">
          {NAV_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="block py-2 text-sm font-medium text-[var(--aliaa-foreground)]"
              onClick={() => setOpen(false)}
            >
              {link.label}
            </Link>
          ))}
          {profile ? (
            <>
              <Link
                href="/dashboard"
                className="block py-2 text-sm font-medium"
                onClick={() => setOpen(false)}
              >
                Mi Panel
              </Link>
              <form action="/api/auth/signout" method="POST">
                <button
                  type="submit"
                  className="flex w-full items-center gap-2 py-2 text-sm font-medium text-[var(--aliaa-foreground)]"
                  onClick={() => setOpen(false)}
                >
                  <LogOut className="h-4 w-4" />
                  Salir
                </button>
              </form>
            </>
          ) : (
            <Link href="/login" className="block py-2 text-sm font-medium" onClick={() => setOpen(false)}>
              Ingresar
            </Link>
          )}
        </nav>
      )}
    </header>
  );
}
