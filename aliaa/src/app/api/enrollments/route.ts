import { NextRequest, NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";

export async function POST(request: NextRequest) {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) {
    return NextResponse.json({ error: "No autenticado" }, { status: 401 });
  }

  const { courseId, nombreCertificado } = await request.json();

  const nombre = typeof nombreCertificado === "string" ? nombreCertificado.trim() : "";
  if (nombre.length < 3) {
    return NextResponse.json(
      { error: "Ingresá tu nombre completo para el certificado." },
      { status: 400 }
    );
  }
  const { data: course } = await supabase
    .from("courses")
    .select("gratuito, precio")
    .eq("id", courseId)
    .single();

  if (!course) {
    return NextResponse.json({ error: "Curso no encontrado" }, { status: 404 });
  }

  if (!course.gratuito && course.precio > 0) {
    return NextResponse.json({ error: "Curso de pago" }, { status: 402 });
  }

  const { error } = await supabase.from("enrollments").upsert({
    user_id: user.id,
    course_id: courseId,
    nombre_certificado: nombre,
  });

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 400 });
  }

  return NextResponse.json({ success: true });
}
