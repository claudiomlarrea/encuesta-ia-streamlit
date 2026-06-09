import { createClient } from "@/lib/supabase/server";
import type { Course, CourseLevel, Module, Lesson } from "@/types/database";

export async function getPublishedCourses(): Promise<Course[]> {
  const supabase = await createClient();
  const { data } = await supabase
    .from("courses")
    .select("*")
    .eq("publicado", true)
    .order("created_at", { ascending: false });
  return data ?? [];
}

export async function getAllCourses(): Promise<Course[]> {
  const supabase = await createClient();
  const { data } = await supabase
    .from("courses")
    .select("*")
    .order("created_at", { ascending: false });
  return data ?? [];
}

export async function getCourseBySlug(slug: string): Promise<Course | null> {
  const supabase = await createClient();
  const { data } = await supabase
    .from("courses")
    .select("*")
    .eq("slug", slug)
    .single();
  return data;
}

export async function getCourseById(id: string): Promise<Course | null> {
  const supabase = await createClient();
  const { data } = await supabase
    .from("courses")
    .select("*")
    .eq("id", id)
    .single();
  return data;
}

export async function getCourseModules(courseId: string): Promise<Module[]> {
  const supabase = await createClient();
  const { data: modules } = await supabase
    .from("modules")
    .select("*")
    .eq("course_id", courseId)
    .order("orden");

  if (!modules?.length) return [];

  const { data: lessons } = await supabase
    .from("lessons")
    .select("*")
    .in(
      "module_id",
      modules.map((m) => m.id)
    )
    .order("orden");

  return modules.map((mod) => ({
    ...mod,
    lessons: lessons?.filter((l) => l.module_id === mod.id) ?? [],
  }));
}

export interface CourseFormData {
  titulo: string;
  slug: string;
  descripcion_corta: string;
  descripcion: string;
  precio: number;
  gratuito: boolean;
  publicado: boolean;
  nivel: CourseLevel;
  categoria: string;
  duracion_horas: number;
}

export async function getEnrollmentCount(courseId: string): Promise<number> {
  const supabase = await createClient();
  const { count } = await supabase
    .from("enrollments")
    .select("*", { count: "exact", head: true })
    .eq("course_id", courseId);
  return count ?? 0;
}
