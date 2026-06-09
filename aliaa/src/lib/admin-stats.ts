import { createAdminClient, requireAdmin } from "@/lib/supabase/admin";

export async function getAdminStats() {
  await requireAdmin();
  const supabase = createAdminClient();

  const [
    { count: users },
    { count: courses },
    { count: enrollments },
    { count: certificates },
  ] = await Promise.all([
    supabase.from("profiles").select("*", { count: "exact", head: true }),
    supabase.from("courses").select("*", { count: "exact", head: true }).eq("publicado", true),
    supabase.from("enrollments").select("*", { count: "exact", head: true }),
    supabase.from("certificates").select("*", { count: "exact", head: true }),
  ]);

  const { data: coursesList } = await supabase
    .from("courses")
    .select("id, titulo")
    .eq("publicado", true)
    .order("titulo");

  const popularCourses = await Promise.all(
    (coursesList ?? []).map(async (c) => {
      const { count } = await supabase
        .from("enrollments")
        .select("*", { count: "exact", head: true })
        .eq("course_id", c.id);
      return { nombre: c.titulo, inscritos: count ?? 0 };
    })
  );
  popularCourses.sort((a, b) => b.inscritos - a.inscritos);

  const { data: recentEnrollments } = await supabase
    .from("enrollments")
    .select("inscrito_en, course:courses(titulo), profile:profiles(nombre_completo)")
    .order("inscrito_en", { ascending: false })
    .limit(8);

  return {
    users: users ?? 0,
    courses: courses ?? 0,
    enrollments: enrollments ?? 0,
    certificates: certificates ?? 0,
    popularCourses,
    recentEnrollments: recentEnrollments ?? [],
  };
}
