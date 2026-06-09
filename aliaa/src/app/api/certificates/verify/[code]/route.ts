import { NextRequest, NextResponse } from "next/server";
import { createClient } from "@supabase/supabase-js";
import { getCertificateStudentName } from "@/lib/profile-name";

function getSupabaseAdmin() {
  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!
  );
}

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ code: string }> }
) {
  const { code } = await params;

  const { data: certificate } = await getSupabaseAdmin()
    .from("certificates")
    .select("*, profiles(nombre_completo, email), courses(titulo)")
    .eq("codigo_verificacion", code)
    .single();

  if (!certificate) {
    return NextResponse.json({ valido: false });
  }

  return NextResponse.json({
    valido: true,
    estudiante: getCertificateStudentName({
      nombreEstudiante: certificate.nombre_estudiante,
      profile: certificate.profiles,
    }),
    curso: certificate.courses?.titulo,
    fecha: certificate.emitido_en,
  });
}
