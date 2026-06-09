import Link from "next/link";
import { MessageSquare, Pin, Clock } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatDate } from "@/lib/utils";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Foros",
};

const TOPICS = [
  {
    id: "1",
    titulo: "¿Cómo elegir el algoritmo correcto?",
    curso: "Fundamentos de Machine Learning",
    autor: "María González",
    respuestas: 12,
    fijado: true,
    fecha: "2025-12-01T14:00:00Z",
  },
  {
    id: "2",
    titulo: "Dudas sobre el proyecto final",
    curso: "Fundamentos de Machine Learning",
    autor: "Carlos Ruiz",
    respuestas: 5,
    fijado: false,
    fecha: "2025-12-05T09:30:00Z",
  },
  {
    id: "3",
    titulo: "Recursos adicionales en español",
    curso: "Introducción a la IA Aplicada",
    autor: "Ana Martínez",
    respuestas: 8,
    fijado: false,
    fecha: "2025-11-28T16:00:00Z",
  },
];

export default function ForosPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold">Foros de Discusión</h1>
      <p className="mt-1 text-[var(--aliaa-muted-foreground)]">
        Participá en las conversaciones de tus cursos
      </p>

      <div className="mt-8 space-y-3">
        {TOPICS.map((topic) => (
          <Link key={topic.id} href={`/dashboard/foros/${topic.id}`}>
            <Card className="transition-shadow hover:shadow-md">
              <CardContent className="flex items-center gap-4 p-4">
                <MessageSquare className="h-5 w-5 shrink-0 text-[var(--aliaa-primary)]" />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    {topic.fijado && <Pin className="h-3.5 w-3.5 text-[var(--aliaa-accent)]" />}
                    <h3 className="truncate font-medium">{topic.titulo}</h3>
                  </div>
                  <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-[var(--aliaa-muted-foreground)]">
                    <Badge variant="outline">{topic.curso}</Badge>
                    <span>{topic.autor}</span>
                    <span className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {formatDate(topic.fecha)}
                    </span>
                  </div>
                </div>
                <span className="text-sm text-[var(--aliaa-muted-foreground)]">
                  {topic.respuestas} respuestas
                </span>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
