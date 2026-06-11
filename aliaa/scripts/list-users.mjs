/**
 * Lista usuarios e inscripciones reales en Supabase.
 * Uso: node scripts/list-users.mjs
 */
import { readFileSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const env = Object.fromEntries(
  readFileSync(resolve(__dirname, "../.env.local"), "utf8")
    .split("\n")
    .filter((l) => l.includes("="))
    .map((l) => {
      const i = l.indexOf("=");
      return [l.slice(0, i), l.slice(i + 1)];
    })
);

const URL = env.NEXT_PUBLIC_SUPABASE_URL;
const KEY = env.SUPABASE_SERVICE_ROLE_KEY;

async function api(path) {
  const res = await fetch(`${URL}${path}`, {
    headers: { apikey: KEY, Authorization: `Bearer ${KEY}` },
  });
  return res.json();
}

const { users = [] } = await api("/auth/v1/admin/users?page=1&per_page=50");
const profiles = await api("/rest/v1/profiles?select=id,email,nombre_completo,rol");
const enrollments = await api(
  "/rest/v1/enrollments?select=id,user_id,inscrito_en,profile:profiles(nombre_completo,email),course:courses(titulo)&order=inscrito_en.desc"
);

console.log("\n👤 Usuarios registrados:\n");
for (const u of users) {
  const p = profiles.find((x) => x.id === u.id);
  const n = enrollments.filter((e) => e.user_id === u.id).length;
  console.log(`  ${p?.nombre_completo || "(sin nombre)"} <${u.email}>`);
  console.log(`    Rol: ${p?.rol} · Inscripciones: ${n} · ID: ${u.id}\n`);
}

console.log("📋 Inscripciones recientes:\n");
for (const e of enrollments) {
  console.log(
    `  ${e.profile?.nombre_completo} — ${e.course?.titulo} (${new Date(e.inscrito_en).toLocaleDateString("es-AR")})`
  );
}
