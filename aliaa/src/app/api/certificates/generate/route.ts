import { NextRequest, NextResponse } from "next/server";
import { createAdminClient } from "@/lib/supabase/admin";
import { createClient } from "@/lib/supabase/server";
import { getCertificateStudentName } from "@/lib/profile-name";
import { generateVerificationCode } from "@/lib/utils";

export async function POST(request: NextRequest) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) {
    return NextResponse.json({ error: "No autenticado" }, { status: 401 });
  }

  const { courseId } = await request.json();

  const { data: enrollment } = await supabase
    .from("enrollments")
    .select("*, profile:profiles(nombre_completo, email)")
    .eq("user_id", user.id)
    .eq("course_id", courseId)
    .single();

  if (!enrollment || enrollment.progreso_porcentaje < 100) {
    return NextResponse.json(
      { error: "Debes completar el curso al 100% para obtener el certificado" },
      { status: 400 }
    );
  }

  const { data: existing } = await supabase
    .from("certificates")
    .select("*")
    .eq("user_id", user.id)
    .eq("course_id", courseId)
    .single();

  if (existing) {
    return NextResponse.json({ certificate: existing });
  }

  const codigo = generateVerificationCode();
  const profile = enrollment.profile as { nombre_completo?: string; email?: string } | null;
  const nombreEstudiante = getCertificateStudentName({
    nombreCertificado: enrollment.nombre_certificado,
    profile,
  });

  const admin = createAdminClient();
  const { data: certificate, error } = await admin
    .from("certificates")
    .insert({
      user_id: user.id,
      course_id: courseId,
      codigo_verificacion: codigo,
      nombre_estudiante: nombreEstudiante,
    })
    .select()
    .single();

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }

  return NextResponse.json({ certificate });
}
