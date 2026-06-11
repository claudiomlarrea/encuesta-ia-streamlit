import Link from "next/link";
import { Clock } from "lucide-react";
import { Card, CardContent, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { CourseCover } from "@/components/courses/course-cover";
import { StarRatingDisplay } from "@/components/courses/star-rating-display";
import { formatPrice } from "@/lib/utils";
import { LEVEL_LABELS } from "@/lib/constants";
import type { CourseRatingSummary } from "@/lib/course-ratings";
import type { Course } from "@/types/database";

interface CourseCardProps {
  course: Course;
  rating?: CourseRatingSummary;
}

export function CourseCard({ course, rating }: CourseCardProps) {
  return (
    <Card className="group overflow-hidden transition-shadow hover:shadow-lg">
      <div className="relative aspect-video overflow-hidden bg-[var(--aliaa-muted)]">
        <CourseCover slug={course.slug} titulo={course.titulo} />
        {course.nivel && (
          <Badge className="absolute left-3 top-3" variant="secondary">
            {LEVEL_LABELS[course.nivel]}
          </Badge>
        )}
        {course.gratuito && (
          <Badge className="absolute right-3 top-3" variant="success">
            Gratuito
          </Badge>
        )}
      </div>
      <CardContent className="p-4">
        {course.categoria && (
          <p className="mb-1 text-xs font-medium text-[var(--aliaa-primary)]">
            {course.categoria}
          </p>
        )}
        <h3 className="mb-2 line-clamp-2 text-base font-semibold">{course.titulo}</h3>
        <p className="line-clamp-2 text-sm text-[var(--aliaa-muted-foreground)]">
          {course.descripcion_corta}
        </p>
        <div className="mt-3 flex items-center gap-4 text-xs text-[var(--aliaa-muted-foreground)]">
          {course.duracion_horas && (
            <span className="flex items-center gap-1">
              <Clock className="h-3.5 w-3.5" />
              {course.duracion_horas}h
            </span>
          )}
          {rating && rating.total > 0 && (
            <StarRatingDisplay
              value={rating.promedio}
              total={rating.total}
              showValue
            />
          )}
        </div>
      </CardContent>
      <CardFooter className="flex items-center justify-between p-4 pt-0">
        <span className="text-lg font-bold text-[var(--aliaa-primary)]">
          {course.gratuito ? "Gratis" : formatPrice(course.precio, course.moneda)}
        </span>
        <Link href={`/cursos/${course.slug}`}>
          <Button size="sm">Ver curso</Button>
        </Link>
      </CardFooter>
    </Card>
  );
}
