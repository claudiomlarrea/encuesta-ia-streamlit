import { redirect, notFound } from "next/navigation";
import { CoursePlayer } from "@/components/courses/course-player";
import { getCourseById, getCourseModules } from "@/lib/courses";
import { getUserCourseRating } from "@/lib/course-ratings";
import { getLessonProgress, isEnrolled } from "@/lib/enrollments";
import { getQuizzesForLessons } from "@/lib/quizzes";
import { createClient } from "@/lib/supabase/server";

interface PageProps {
  params: Promise<{ id: string }>;
}

export default async function CursoPlayerPage({ params }: PageProps) {
  const { id } = await params;
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) redirect("/login");

  const enrolled = await isEnrolled(user.id, id);
  if (!enrolled) redirect(`/cursos`);

  const course = await getCourseById(id);
  if (!course) notFound();

  const modules = await getCourseModules(id);
  const lessonIds = modules.flatMap((m) => (m.lessons ?? []).map((l) => l.id));
  const completedSet = await getLessonProgress(user.id, lessonIds);

  const modulesWithProgress = modules.map((mod) => ({
    ...mod,
    lessons: (mod.lessons ?? []).map((l) => ({
      ...l,
      completado: completedSet.has(l.id),
    })),
  }));

  const progress = lessonIds.length
    ? Math.round((completedSet.size / lessonIds.length) * 100)
    : 0;

  const quizzes = await getQuizzesForLessons(lessonIds);

  let initialCertificateId: string | null = null;
  let initialUserRating: { estrellas: number; comentario: string | null } | null = null;
  if (progress === 100) {
    const [{ data: cert }, userRating] = await Promise.all([
      supabase
        .from("certificates")
        .select("id")
        .eq("user_id", user.id)
        .eq("course_id", id)
        .single(),
      getUserCourseRating(user.id, id),
    ]);
    initialCertificateId = cert?.id ?? null;
    if (userRating) {
      initialUserRating = {
        estrellas: userRating.estrellas,
        comentario: userRating.comentario,
      };
    }
  }

  return (
    <CoursePlayer
      course={course}
      modules={modulesWithProgress}
      initialProgress={progress}
      userId={user.id}
      quizzes={quizzes}
      initialCertificateId={initialCertificateId}
      initialUserRating={initialUserRating}
    />
  );
}
