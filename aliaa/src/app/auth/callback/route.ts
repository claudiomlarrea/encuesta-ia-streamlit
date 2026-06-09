import { NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";

export async function GET(request: Request) {
  const { searchParams, origin } = new URL(request.url);
  const code = searchParams.get("code");
  const next = searchParams.get("next") ?? "/dashboard";

  if (code) {
    const supabase = await createClient();
    const { error } = await supabase.auth.exchangeCodeForSession(code);
    if (!error) {
      const {
        data: { user },
      } = await supabase.auth.getUser();
      if (user) {
        const metaName =
          user.user_metadata?.nombre_completo ||
          user.user_metadata?.full_name ||
          user.user_metadata?.name;
        if (typeof metaName === "string" && metaName.trim()) {
          const { data: profile } = await supabase
            .from("profiles")
            .select("nombre_completo, email")
            .eq("id", user.id)
            .single();
          const prefix = user.email?.split("@")[0]?.toLowerCase();
          const current = profile?.nombre_completo?.trim().toLowerCase();
          if (!current || current === prefix) {
            await supabase
              .from("profiles")
              .update({ nombre_completo: metaName.trim() })
              .eq("id", user.id);
          }
        }
      }
      return NextResponse.redirect(`${origin}${next}`);
    }
  }

  return NextResponse.redirect(`${origin}/login?error=oauth`);
}
