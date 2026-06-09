import Link from "next/link";
import { GraduationCap, Mail, MapPin } from "lucide-react";
import { CONTACT_EMAIL, SITE_FULL_NAME, SITE_NAME } from "@/lib/constants";

export function Footer() {
  return (
    <footer className="border-t border-[var(--aliaa-border)] bg-[var(--aliaa-muted)]">
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="grid gap-8 md:grid-cols-4">
          <div className="md:col-span-2">
            <div className="flex items-center gap-2">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[var(--aliaa-primary)]">
                <GraduationCap className="h-5 w-5 text-white" />
              </div>
              <span className="text-lg font-bold">{SITE_NAME}</span>
            </div>
            <p className="mt-3 max-w-md text-sm text-[var(--aliaa-muted-foreground)]">
              {SITE_FULL_NAME}. Formación de excelencia en inteligencia artificial
              aplicada, diseñada para profesionales de América Latina.
            </p>
          </div>

          <div>
            <h4 className="mb-3 text-sm font-semibold">Plataforma</h4>
            <ul className="space-y-2 text-sm text-[var(--aliaa-muted-foreground)]">
              <li><Link href="/cursos" className="hover:text-[var(--aliaa-primary)]">Cursos</Link></li>
              <li><Link href="/certificados/verificar" className="hover:text-[var(--aliaa-primary)]">Verificar Certificado</Link></li>
              <li><Link href="/nosotros" className="hover:text-[var(--aliaa-primary)]">Nosotros</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="mb-3 text-sm font-semibold">Contacto</h4>
            <ul className="space-y-2 text-sm text-[var(--aliaa-muted-foreground)]">
              <li className="flex items-center gap-2">
                <Mail className="h-4 w-4" />
                <a
                  href={`mailto:${CONTACT_EMAIL}`}
                  className="hover:text-[var(--aliaa-primary)]"
                >
                  {CONTACT_EMAIL}
                </a>
              </li>
              <li className="flex items-center gap-2">
                <MapPin className="h-4 w-4" />
                América Latina
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-8 border-t border-[var(--aliaa-border)] pt-8 text-center text-xs text-[var(--aliaa-muted-foreground)]">
          © {new Date().getFullYear()} {SITE_FULL_NAME}. Todos los derechos reservados.
        </div>
      </div>
    </footer>
  );
}
