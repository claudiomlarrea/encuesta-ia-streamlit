import { createAdminClient } from "@/lib/supabase/admin";
import type { Quiz, QuizQuestion } from "@/types/database";

export interface QuizWithQuestions extends Quiz {
  questions: QuizQuestion[];
}

export async function getQuizByLessonId(
  lessonId: string
): Promise<QuizWithQuestions | null> {
  const supabase = createAdminClient();
  const { data: quiz, error } = await supabase
    .from("quizzes")
    .select("*")
    .eq("lesson_id", lessonId)
    .maybeSingle();
  if (error || !quiz) return null;

  const { data: questions } = await supabase
    .from("quiz_questions")
    .select("*")
    .eq("quiz_id", quiz.id)
    .order("orden");

  return {
    ...quiz,
    questions: (questions ?? []).map((q) => ({
      ...q,
      opciones: q.opciones as string[],
    })),
  };
}

export async function getQuizzesForLessons(
  lessonIds: string[]
): Promise<Record<string, QuizWithQuestions>> {
  const map: Record<string, QuizWithQuestions> = {};
  await Promise.all(
    lessonIds.map(async (id) => {
      const quiz = await getQuizByLessonId(id);
      if (quiz) map[id] = quiz;
    })
  );
  return map;
}
