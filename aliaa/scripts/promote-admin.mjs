import { readFileSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";
import { OWNER_EMAIL } from "./emails.mjs";

const __dirname = dirname(fileURLToPath(import.meta.url));
const envPath = resolve(__dirname, "../.env.local");

function loadEnv() {
  const env = {};
  for (const line of readFileSync(envPath, "utf8").split("\n")) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const idx = trimmed.indexOf("=");
    if (idx === -1) continue;
    env[trimmed.slice(0, idx)] = trimmed.slice(idx + 1);
  }
  return env;
}

const env = loadEnv();
const URL = env.NEXT_PUBLIC_SUPABASE_URL;
const SERVICE_KEY = env.SUPABASE_SERVICE_ROLE_KEY;

async function api(path, options = {}) {
  const res = await fetch(`${URL}${path}`, {
    ...options,
    headers: {
      apikey: SERVICE_KEY,
      Authorization: `Bearer ${SERVICE_KEY}`,
      "Content-Type": "application/json",
      ...options.headers,
    },
  });
  const text = await res.text();
  let data;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = text;
  }
  return { ok: res.ok, status: res.status, data };
}

async function main() {
  const users = await api("/auth/v1/admin/users?page=1&per_page=100");
  const user = users.data?.users?.find((u) => u.email === OWNER_EMAIL);

  if (!user) {
    console.error(`❌ No existe usuario con email ${OWNER_EMAIL}`);
    console.log("   Registrate primero en /registro o /login con enlace mágico.");
    process.exit(1);
  }

  const profile = await api(`/rest/v1/profiles?id=eq.${user.id}&select=rol,email,nombre_completo`);
  const current = profile.data?.[0];

  const update = await api(`/rest/v1/profiles?id=eq.${user.id}`, {
    method: "PATCH",
    headers: { Prefer: "return=representation" },
    body: JSON.stringify({ rol: "admin", email: OWNER_EMAIL }),
  });

  if (!update.ok) {
    console.error("❌ No se pudo actualizar el perfil:", update.data);
    process.exit(1);
  }

  console.log(`✅ ${OWNER_EMAIL} ahora es administrador`);
  if (current?.rol) {
    console.log(`   Rol anterior: ${current.rol}`);
  }
  console.log(`   Admin: https://aliaa-six.vercel.app/admin`);
}

main().catch((err) => {
  console.error("❌", err.message);
  process.exit(1);
});
