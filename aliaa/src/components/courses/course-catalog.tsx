"use client";

import { useState } from "react";
import { CourseCard } from "@/components/courses/course-card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { Course } from "@/types/database";

interface CourseCatalogProps {
  courses: Course[];
}

export function CourseCatalog({ courses }: CourseCatalogProps) {
  const [activeId, setActiveId] = useState<string | null>(null);

  const visible =
    activeId === null ? courses : courses.filter((c) => c.id === activeId);

  if (courses.length === 0) {
    return (
      <p className="text-center text-[var(--aliaa-muted-foreground)]">
        Próximamente nuevos cursos disponibles.
      </p>
    );
  }

  return (
    <>
      <div className="mb-8 flex flex-wrap gap-2">
        <button type="button" onClick={() => setActiveId(null)}>
          <Badge
            variant={activeId === null ? "default" : "outline"}
            className={cn(
              "cursor-pointer transition-colors",
              activeId !== null && "hover:bg-[var(--aliaa-muted)]"
            )}
          >
            Todos
          </Badge>
        </button>
        {courses.map((course) => (
          <button key={course.id} type="button" onClick={() => setActiveId(course.id)}>
            <Badge
              variant={activeId === course.id ? "default" : "outline"}
              className={cn(
                "cursor-pointer transition-colors",
                activeId !== course.id && "hover:bg-[var(--aliaa-muted)]"
              )}
            >
              {course.titulo}
            </Badge>
          </button>
        ))}
      </div>

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {visible.map((course) => (
          <CourseCard key={course.id} course={course} />
        ))}
      </div>
    </>
  );
}
