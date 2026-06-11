import Link from "next/link";
import {
  Brain,
  Award,
  BookOpen,
  Globe,
  TrendingUp,
  ArrowRight,
  CheckCircle,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { CourseCard } from "@/components/courses/course-card";
import { SITE_FULL_NAME } from "@/lib/constants";
import { getRatingsSummaryByCourseIds } from "@/lib/course-ratings";
import { getPublishedCourses } from "@/lib/courses";

const FEATURES = [
  "Cursos 100% asincrónicos y a tu ritmo",
  "Certificados verificables con código QR",
  "Foros de discusión con docentes expertos",
  "Contenido en español para Latinoamérica",
  "Evaluaciones y proyectos prácticos",
  "Inscripción gratuita mientras lanzamos",
];

export default async function HomePage() {
  const courses = await getPublishedCourses();
  const ratings = await getRatingsSummaryByCourseIds(courses.map((c) => c.id));

  const stats = [
    {
      icon: BookOpen,
      value: String(courses.length),
      label: courses.length === 1 ? "Curso disponible" : "Cursos",
    },
    { icon: Globe, value: "LATAM", label: "Enfoque regional" },
    { icon: Award, value: "QR", label: "Certificado verificable" },
    { icon: Brain, value: "100%", label: "En español" },
  ];

  return (
    <>
      <section className="relative overflow-hidden bg-gradient-to-br from-[var(--aliaa-primary)] via-[var(--aliaa-primary-dark)] to-[var(--aliaa-secondary)] text-white">
        <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-10" />
        <div className="relative mx-auto max-w-7xl px-4 py-24 sm:px-6 lg:px-8 lg:py-32">
          <div className="max-w-3xl">
            <div className="mb-4 inline-flex items-center gap-2 rounded-full bg-white/10 px-4 py-1.5 text-sm backdrop-blur">
              <Brain className="h-4 w-4" />
              Formación profesional en IA
            </div>
            <h1 className="text-4xl font-bold tracking-tight sm:text-5xl lg:text-6xl">
              {SITE_FULL_NAME}
            </h1>
            <p className="mt-6 text-lg text-white/80 sm:text-xl">
              Desarrollá competencias en inteligencia artificial aplicada con cursos
              diseñados para profesionales de América Latina. Aprendé a tu ritmo,
              obtené certificados verificables y unite a nuestra comunidad.
            </p>
            <div className="mt-8 flex flex-wrap gap-4">
              <Link href="/cursos">
                <Button size="lg" className="bg-white text-[var(--aliaa-primary)] hover:bg-white/90">
                  Explorar cursos
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
              <Link href="/registro">
                <Button size="lg" variant="outline" className="border-white/30 text-white hover:bg-white/10">
                  Registrarse gratis
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      <section className="border-b border-[var(--aliaa-border)] bg-[var(--aliaa-card)]">
        <div className="mx-auto grid max-w-7xl grid-cols-2 gap-6 px-4 py-12 sm:px-6 md:grid-cols-4 lg:px-8">
          {stats.map((stat) => {
            const Icon = stat.icon;
            return (
              <div key={stat.label} className="text-center">
                <Icon className="mx-auto mb-2 h-8 w-8 text-[var(--aliaa-primary)]" />
                <p className="text-2xl font-bold">{stat.value}</p>
                <p className="text-sm text-[var(--aliaa-muted-foreground)]">{stat.label}</p>
              </div>
            );
          })}
        </div>
      </section>

      <section className="py-16 sm:py-24">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mb-10 text-center">
            <h2 className="text-3xl font-bold">Cursos disponibles</h2>
            <p className="mt-2 text-[var(--aliaa-muted-foreground)]">
              {courses.length > 0
                ? "Empezá hoy. Nuevos cursos se suman a medida que los desarrollamos."
                : "Estamos preparando nuestro catálogo. Volvé pronto."}
            </p>
          </div>
          {courses.length > 0 ? (
            <div className="mx-auto grid max-w-lg gap-6 sm:max-w-none sm:grid-cols-2 lg:grid-cols-3">
              {courses.map((course) => (
                <CourseCard key={course.id} course={course} rating={ratings[course.id]} />
              ))}
            </div>
          ) : (
            <p className="text-center text-[var(--aliaa-muted-foreground)]">
              Próximamente.
            </p>
          )}
          {courses.length > 0 && (
            <div className="mt-10 text-center">
              <Link href="/cursos">
                <Button variant="outline" size="lg">
                  Ver catálogo completo
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
            </div>
          )}
        </div>
      </section>

      <section className="bg-[var(--aliaa-muted)] py-16 sm:py-24">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid items-center gap-12 lg:grid-cols-2">
            <div>
              <h2 className="text-3xl font-bold">¿Por qué elegir ALIAA?</h2>
              <p className="mt-4 text-[var(--aliaa-muted-foreground)]">
                Somos la academia de referencia en inteligencia artificial aplicada
                para América Latina, con un enfoque práctico y orientado a resultados.
              </p>
              <ul className="mt-8 space-y-3">
                {FEATURES.map((feature) => (
                  <li key={feature} className="flex items-center gap-3">
                    <CheckCircle className="h-5 w-5 shrink-0 text-[var(--aliaa-secondary)]" />
                    <span className="text-sm">{feature}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="grid grid-cols-2 gap-4">
              {[
                { icon: TrendingUp, title: "Carrera", desc: "Impulsá tu perfil profesional" },
                { icon: Brain, title: "Práctica", desc: "Proyectos del mundo real" },
                { icon: Globe, title: "Latinoamérica", desc: "Contenido regionalizado" },
                { icon: Award, title: "Certificación", desc: "Reconocimiento verificable" },
              ].map((item) => {
                const Icon = item.icon;
                return (
                  <Card key={item.title}>
                    <CardContent className="p-6 text-center">
                      <Icon className="mx-auto mb-3 h-8 w-8 text-[var(--aliaa-primary)]" />
                      <h3 className="font-semibold">{item.title}</h3>
                      <p className="mt-1 text-xs text-[var(--aliaa-muted-foreground)]">
                        {item.desc}
                      </p>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </div>
        </div>
      </section>

      <section className="py-16 sm:py-24">
        <div className="mx-auto max-w-3xl px-4 text-center sm:px-6">
          <h2 className="text-3xl font-bold">Comenzá tu formación hoy</h2>
          <p className="mt-4 text-[var(--aliaa-muted-foreground)]">
            Registrate gratis e inscribite al curso de Fundamentos de Machine Learning.
          </p>
          <Link href="/registro" className="mt-8 inline-block">
            <Button size="lg">
              Crear cuenta gratuita
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>
        </div>
      </section>
    </>
  );
}
