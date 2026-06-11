/**
 * Elimina un usuario de prueba y todos sus datos (inscripciones, progreso, certificados).
 * Uso: node scripts/delete-user.mjs investigacion@uccuyo.edu.ar
 */
import { readFileSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";
import { OWNER_EMAIL } from "./emails.mjs";

const __dirname = dirname(fileURLToPath(import.meta.url));
const email = process.argv[2];

if (!email) {
  console.error("Uso: node scripts/delete-user.mjs <email>");
  process.exit(1);
}

if (email === OWNER_EMAIL) {
  console.error(`❌ No se puede eliminar la cuenta principal (${OWNER_EMAIL})`);
  process.exit(1);
}

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

async function api(path, options = {}) {
  const res = await fetch(`${URL}${path}`, {
    ...options,
    headers: {
      apikey: KEY,
      Authorization: `Bearer ${KEY}`,
      "Content-Type": "application/json",
      Prefer: options.prefer || "return=minimal",
      ...options.headers,
    },
  });
  return { ok: res.ok, status: res.status };
}

const { users = [] } = await (async () => {
  const res = await fetch(`${URL}/auth/v1/admin/users?page=1&per_page=50`, {
    headers: { apikey: KEY, Authorization: `Bearer ${KEY}` },
  });
  return res.json();
})();

const user = users.find((u) => u.email === email);
if (!user) {
  console.error(`❌ No existe usuario con email: ${email}`);
  process.exit(1);
}

console.log(`🗑️  Eliminando ${email} (${user.id})...`);

// CASCADE en profiles borra enrollments, lesson_progress, certificates vía FK
const del = await api(`/auth/v1/admin/users/${user.id}`, { method: "DELETE" });

if (del.ok) {
  console.log("✅ Usuario y datos asociados eliminados");
} else {
  console.error(`❌ Error HTTP ${del.status}`);
  process.exit(1);
}
