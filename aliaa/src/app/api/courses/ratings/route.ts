import { NextRequest, NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";

export async function GET(request: NextRequest) {
  const courseId = request.nextUrl.searchParams.get("courseId");
  if (!courseId) {
    return NextResponse.json({ error: "Falta courseId" }, { status: 400 });
  }

  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  const { data: rows } = await supabase
    .from("course_ratings")
    .select("estrellas")
    .eq("course_id", courseId);

  const total = rows?.length ?? 0;
  const promedio =
    total > 0
      ? Math.round(
          (rows!.reduce((sum, row) => sum + row.estrellas, 0) / total) * 10
        ) / 10
      : 0;

  let userRating = null;
  if (user) {
    const { data } = await supabase
      .from("course_ratings")
      .select("estrellas, comentario, updated_at")
      .eq("user_id", user.id)
      .eq("course_id", courseId)
      .maybeSingle();
    userRating = data;
  }

  return NextResponse.json({ promedio, total, userRating });
}

export async function POST(request: NextRequest) {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) {
    return NextResponse.json({ error: "No autenticado" }, { status: 401 });
  }

  const { courseId, estrellas, comentario } = await request.json();
  const stars = Number(estrellas);
  if (!courseId || !Number.isInteger(stars) || stars < 1 || stars > 5) {
    return NextResponse.json(
      { error: "Indicá un curso y una valoración de 1 a 5 estrellas." },
      { status: 400 }
    );
  }

  const { data: enrollment } = await supabase
    .from("enrollments")
    .select("progreso_porcentaje")
    .eq("user_id", user.id)
    .eq("course_id", courseId)
    .single();

  if (!enrollment || Number(enrollment.progreso_porcentaje) < 100) {
    return NextResponse.json(
      { error: "Solo podés valorar un curso que hayas completado." },
      { status: 403 }
    );
  }

  const comment =
    typeof comentario === "string" ? comentario.trim().slice(0, 500) : null;

  const { data, error } = await supabase
    .from("course_ratings")
    .upsert(
      {
        user_id: user.id,
        course_id: courseId,
        estrellas: stars,
        comentario: comment || null,
        updated_at: new Date().toISOString(),
      },
      { onConflict: "user_id,course_id" }
    )
    .select("estrellas, comentario, updated_at")
    .single();

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 400 });
  }

  return NextResponse.json({ success: true, userRating: data });
}
