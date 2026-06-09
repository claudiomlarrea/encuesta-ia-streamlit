import { NextRequest, NextResponse } from "next/server";
import { createClient } from "@supabase/supabase-js";

function getSupabaseAdmin() {
  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!
  );
}

export async function POST(request: NextRequest) {
  const body = await request.json();

  if (body.type === "payment" && body.data?.id) {
    const paymentId = body.data.id;
    const supabaseAdmin = getSupabaseAdmin();

    const { data: payment } = await supabaseAdmin
      .from("payments")
      .select("*")
      .eq("proveedor_pago_id", paymentId)
      .single();

    if (payment) {
      await supabaseAdmin
        .from("payments")
        .update({ estado: "completado" })
        .eq("id", payment.id);

      await supabaseAdmin.from("enrollments").upsert({
        user_id: payment.user_id,
        course_id: payment.course_id,
      });
    }
  }

  return NextResponse.json({ received: true });
}
