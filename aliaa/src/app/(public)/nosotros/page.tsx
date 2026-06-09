import { Brain, Target, Heart, Globe } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { SITE_FULL_NAME } from "@/lib/constants";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Nosotros",
};

const VALUES = [
  {
    icon: Brain,
    title: "Excelencia académica",
    description: "Contenido riguroso diseñado por expertos en IA con experiencia en la industria y la academia.",
  },
  {
    icon: Globe,
    title: "Enfoque latinoamericano",
    description: "Formación contextualizada para las realidades, idiomas y mercados de América Latina.",
  },
  {
    icon: Target,
    title: "Aplicación práctica",
    description: "Proyectos reales y casos de uso que podés implementar inmediatamente en tu trabajo.",
  },
  {
    icon: Heart,
    title: "Comunidad",
    description: "Red de profesionales, docentes y alumni que comparten conocimiento y oportunidades.",
  },
];

export default function NosotrosPage() {
  return (
    <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-3xl text-center">
        <h1 className="text-3xl font-bold sm:text-4xl">Sobre ALIAA</h1>
        <p className="mt-4 text-lg text-[var(--aliaa-muted-foreground)]">
          {SITE_FULL_NAME} nace con la misión de democratizar el acceso a la formación
          en inteligencia artificial aplicada para profesionales de toda América Latina.
        </p>
      </div>

      <div className="mt-16 grid gap-6 sm:grid-cols-2">
        {VALUES.map((value) => {
          const Icon = value.icon;
          return (
            <Card key={value.title}>
              <CardContent className="p-6">
                <Icon className="mb-4 h-10 w-10 text-[var(--aliaa-primary)]" />
                <h3 className="text-lg font-semibold">{value.title}</h3>
                <p className="mt-2 text-sm text-[var(--aliaa-muted-foreground)]">
                  {value.description}
                </p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <div className="mt-16 rounded-2xl bg-[var(--aliaa-muted)] p-8 text-center sm:p-12">
        <h2 className="text-2xl font-bold">Nuestra visión</h2>
        <p className="mx-auto mt-4 max-w-2xl text-[var(--aliaa-muted-foreground)]">
          Ser la academia de referencia en inteligencia artificial aplicada para
          América Latina, formando a miles de profesionales capaces de liderar la
          transformación digital en sus organizaciones y comunidades.
        </p>
      </div>
    </div>
  );
}
