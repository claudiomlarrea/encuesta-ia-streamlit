import { readFileSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";
import { OWNER_EMAIL, OWNER_NAME } from "./emails.mjs";

const __dirname = dirname(fileURLToPath(import.meta.url));
const env = Object.fromEntries(
  readFileSync(resolve(__dirname, "../.env.local"), "utf8")
    .split("\n")
    .filter((l) => l && !l.startsWith("#"))
    .map((l) => {
      const i = l.indexOf("=");
      return [l.slice(0, i), l.slice(i + 1)];
    })
);

const URL = env.NEXT_PUBLIC_SUPABASE_URL;
const KEY = env.SUPABASE_SERVICE_ROLE_KEY;
const h = {
  apikey: KEY,
  Authorization: `Bearer ${KEY}`,
  "Content-Type": "application/json",
  Prefer: "return=representation",
};

async function api(path, options = {}) {
  const res = await fetch(`${URL}${path}`, { ...options, headers: { ...h, ...options.headers } });
  const data = await res.json().catch(() => null);
  return { ok: res.ok, data };
}

async function main() {
  const users = await api("/auth/v1/admin/users?page=1&per_page=100");
  const user = users.data?.users?.find((u) => u.email === OWNER_EMAIL);
  if (!user) throw new Error("Usuario no encontrado");

  const profile = await api(`/rest/v1/profiles?id=eq.${user.id}&select=nombre_completo`);
  const nombre = profile.data?.[0]?.nombre_completo?.trim() || OWNER_NAME;

  const enrollPatch = await api(`/rest/v1/enrollments?user_id=eq.${user.id}`, {
    method: "PATCH",
    body: JSON.stringify({ nombre_certificado: nombre }),
  });
  if (!enrollPatch.ok) {
    console.error("❌ enrollments:", enrollPatch.data);
    console.log("   Ejecutá primero supabase/migrations/006_certificate_student_name.sql");
    process.exit(1);
  }
  console.log(`✅ Inscripciones actualizadas (${enrollPatch.data?.length ?? 0})`);

  const certPatch = await api(`/rest/v1/certificates?user_id=eq.${user.id}`, {
    method: "PATCH",
    body: JSON.stringify({ nombre_estudiante: nombre }),
  });
  if (!certPatch.ok) {
    console.error("❌ certificates:", certPatch.data);
    process.exit(1);
  }
  console.log(`✅ Certificados actualizados (${certPatch.data?.length ?? 0}) con: ${nombre}`);
}

main().catch((e) => {
  console.error("❌", e.message);
  process.exit(1);
});
