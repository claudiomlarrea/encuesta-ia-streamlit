import { NextRequest, NextResponse } from "next/server";
import { MercadoPagoConfig, Preference } from "mercadopago";
import { createClient } from "@/lib/supabase/server";

export async function POST(request: NextRequest) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) {
    return NextResponse.json({ error: "No autenticado" }, { status: 401 });
  }

  const { courseId, courseTitle, amount, currency } = await request.json();
  const accessToken = process.env.MERCADOPAGO_ACCESS_TOKEN;

  if (!accessToken) {
    return NextResponse.json({ error: "Mercado Pago no configurado" }, { status: 500 });
  }

  const client = new MercadoPagoConfig({ accessToken });
  const preference = new Preference(client);

  const baseUrl = process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000";

  const result = await preference.create({
    body: {
      items: [
        {
          id: courseId,
          title: courseTitle,
          quantity: 1,
          unit_price: amount,
          currency_id: currency === "USD" ? "USD" : "ARS",
        },
      ],
      back_urls: {
        success: `${baseUrl}/dashboard/cursos?pago=exitoso`,
        failure: `${baseUrl}/cursos?pago=fallido`,
        pending: `${baseUrl}/dashboard/cursos?pago=pendiente`,
      },
      auto_return: "approved",
      external_reference: `${user.id}:${courseId}`,
      notification_url: `${baseUrl}/api/payments/mercadopago/webhook`,
    },
  });

  await supabase.from("payments").insert({
    user_id: user.id,
    course_id: courseId,
    monto: amount,
    moneda: currency,
    proveedor: "mercadopago",
    proveedor_pago_id: result.id,
    estado: "pendiente",
  });

  return NextResponse.json({ init_point: result.init_point });
}
