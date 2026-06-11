import { createClient } from "@/lib/supabase/server";
import type { Course, Enrollment } from "@/types/database";

export async function getUserEnrollments(): Promise<(Enrollment & { course: Course })[]> {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return [];

  const { data } = await supabase
    .from("enrollments")
    .select("*, course:courses(*)")
    .eq("user_id", user.id)
    .order("inscrito_en", { ascending: false });

  return (data as (Enrollment & { course: Course })[]) ?? [];
}

export async function getLessonProgress(userId: string, lessonIds: string[]) {
  if (!lessonIds.length) return new Set<string>();
  const supabase = await createClient();
  const { data } = await supabase
    .from("lesson_progress")
    .select("lesson_id")
    .eq("user_id", userId)
    .eq("completado", true)
    .in("lesson_id", lessonIds);
  return new Set(data?.map((p) => p.lesson_id) ?? []);
}

export async function isEnrolled(userId: string, courseId: string): Promise<boolean> {
  const enrollment = await getEnrollment(userId, courseId);
  return !!enrollment;
}

export async function getEnrollment(
  userId: string,
  courseId: string
): Promise<Enrollment | null> {
  const supabase = await createClient();
  const { data } = await supabase
    .from("enrollments")
    .select("*")
    .eq("user_id", userId)
    .eq("course_id", courseId)
    .single();
  return data;
}

export function courseAccessLabel(
  progress: number | string | null | undefined
): "Comenzar curso" | "Continuar curso" | "Revisar curso" {
  const pct = Number(progress ?? 0);
  if (pct >= 100) return "Revisar curso";
  if (pct > 0) return "Continuar curso";
  return "Comenzar curso";
}
