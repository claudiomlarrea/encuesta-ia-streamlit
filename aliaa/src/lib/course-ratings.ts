import { createClient } from "@/lib/supabase/server";

export interface CourseRatingSummary {
  promedio: number;
  total: number;
}

export interface CourseRating {
  id: string;
  user_id: string;
  course_id: string;
  estrellas: number;
  comentario: string | null;
  created_at: string;
  updated_at: string;
}

export async function getRatingsSummaryByCourseIds(
  courseIds: string[]
): Promise<Record<string, CourseRatingSummary>> {
  if (!courseIds.length) return {};

  const supabase = await createClient();
  const { data } = await supabase
    .from("course_ratings")
    .select("course_id, estrellas")
    .in("course_id", courseIds);

  const buckets = new Map<string, { sum: number; count: number }>();
  for (const row of data ?? []) {
    const current = buckets.get(row.course_id) ?? { sum: 0, count: 0 };
    current.sum += row.estrellas;
    current.count += 1;
    buckets.set(row.course_id, current);
  }

  const result: Record<string, CourseRatingSummary> = {};
  for (const [courseId, { sum, count }] of buckets) {
    result[courseId] = {
      promedio: Math.round((sum / count) * 10) / 10,
      total: count,
    };
  }
  return result;
}

export async function getUserCourseRating(
  userId: string,
  courseId: string
): Promise<CourseRating | null> {
  const supabase = await createClient();
  const { data } = await supabase
    .from("course_ratings")
    .select("*")
    .eq("user_id", userId)
    .eq("course_id", courseId)
    .maybeSingle();
  return data;
}
