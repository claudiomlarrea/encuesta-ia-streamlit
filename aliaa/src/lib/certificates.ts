import { createClient } from "@/lib/supabase/server";
import type { Certificate, Course } from "@/types/database";

export async function getUserCertificates(): Promise<
  (Certificate & { course: Course })[]
> {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return [];

  const { data } = await supabase
    .from("certificates")
    .select("*, course:courses(*)")
    .eq("user_id", user.id)
    .order("emitido_en", { ascending: false });

  return (data as (Certificate & { course: Course })[]) ?? [];
}

export async function getCertificateById(id: string) {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return null;

  const { data } = await supabase
    .from("certificates")
    .select("*, course:courses(*), profile:profiles(nombre_completo, email)")
    .eq("id", id)
    .eq("user_id", user.id)
    .single();

  return data;
}
