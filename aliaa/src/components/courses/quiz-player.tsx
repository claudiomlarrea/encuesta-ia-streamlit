"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import type { QuizWithQuestions } from "@/lib/quizzes";

interface QuizPlayerProps {
  quiz: QuizWithQuestions;
  onPass: () => Promise<void>;
}

export function QuizPlayer({ quiz, onPass }: QuizPlayerProps) {
  const [answers, setAnswers] = useState<Record<string, number>>({});
  const [submitted, setSubmitted] = useState(false);
  const [score, setScore] = useState(0);
  const [loading, setLoading] = useState(false);

  function submit() {
    let correct = 0;
    quiz.questions.forEach((q) => {
      if (answers[q.id] === q.respuesta_correcta) correct++;
    });
    const pct = Math.round((correct / quiz.questions.length) * 100);
    setScore(pct);
    setSubmitted(true);
  }

  async function handleContinue() {
    if (score >= quiz.puntaje_aprobacion) {
      setLoading(true);
      await onPass();
      setLoading(false);
    }
  }

  const passed = submitted && score >= quiz.puntaje_aprobacion;

  return (
    <div className="space-y-4 p-6">
      <h3 className="text-lg font-semibold">{quiz.titulo}</h3>
      <p className="text-sm text-[var(--aliaa-muted-foreground)]">
        {quiz.questions.length} preguntas · Mínimo {quiz.puntaje_aprobacion}% para aprobar
      </p>

      {quiz.questions.map((q, qi) => (
        <Card key={q.id}>
          <CardContent className="p-4">
            <p className="mb-3 font-medium">
              {qi + 1}. {q.pregunta}
            </p>
            <div className="space-y-2">
              {q.opciones.map((opt, oi) => {
                const selected = answers[q.id] === oi;
                const showResult = submitted;
                const isCorrect = oi === q.respuesta_correcta;
                return (
                  <button
                    key={oi}
                    disabled={submitted}
                    onClick={() => setAnswers({ ...answers, [q.id]: oi })}
                    className={cn(
                      "w-full rounded-lg border px-3 py-2 text-left text-sm transition-colors",
                      selected && !showResult && "border-[var(--aliaa-primary)] bg-[var(--aliaa-primary)]/10",
                      showResult && isCorrect && "border-emerald-500 bg-emerald-50 dark:bg-emerald-900/20",
                      showResult && selected && !isCorrect && "border-red-500 bg-red-50 dark:bg-red-900/20",
                      !selected && !showResult && "border-[var(--aliaa-border)] hover:bg-[var(--aliaa-muted)]"
                    )}
                  >
                    {opt}
                  </button>
                );
              })}
            </div>
          </CardContent>
        </Card>
      ))}

      {!submitted ? (
        <Button
          onClick={submit}
          disabled={Object.keys(answers).length < quiz.questions.length}
          className="w-full"
        >
          Enviar respuestas
        </Button>
      ) : (
        <Card className={passed ? "border-emerald-500" : "border-amber-500"}>
          <CardContent className="p-4 text-center">
            <p className="text-2xl font-bold">{score}%</p>
            <p className="mt-1 text-sm">
              {passed
                ? "¡Aprobaste! Ya podés obtener tu certificado."
                : `Necesitás ${quiz.puntaje_aprobacion}%. Revisá las lecciones e intentá de nuevo.`}
            </p>
            {passed && (
              <Button className="mt-4" onClick={handleContinue} disabled={loading}>
                {loading ? "Guardando..." : "Completar curso y obtener certificado"}
              </Button>
            )}
            {!passed && (
              <Button className="mt-4" variant="outline" onClick={() => { setSubmitted(false); setAnswers({}); }}>
                Reintentar
              </Button>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
