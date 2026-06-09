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
const ANON_KEY = env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

const ADMIN_EMAIL = OWNER_EMAIL;
const ADMIN_PASSWORD = "Aliaa2025";
const ADMIN_NAME = "Claudio";
const ADMIN_PAIS = "Argentina";

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

async function publicApi(path, options = {}) {
  const res = await fetch(`${URL}${path}`, {
    ...options,
    headers: {
      apikey: ANON_KEY,
      Authorization: `Bearer ${ANON_KEY}`,
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
  console.log("🔧 Configurando Supabase para ALIAA...\n");

  if (!URL?.includes(".supabase.co")) {
    throw new Error("NEXT_PUBLIC_SUPABASE_URL inválida en .env.local");
  }

  // 1. Listar y eliminar usuarios existentes con ese email
  const { data: listData } = await api("/auth/v1/admin/users?page=1&per_page=50");
  const existing = listData?.users?.filter((u) => u.email === ADMIN_EMAIL) ?? [];
  for (const user of existing) {
    console.log(`🗑️  Eliminando usuario previo: ${user.email}`);
    await api(`/auth/v1/admin/users/${user.id}`, { method: "DELETE" });
  }

  // 2. Crear usuario admin vía API admin (evita problemas de trigger)
  console.log(`👤 Creando usuario: ${ADMIN_EMAIL}`);
  const create = await api("/auth/v1/admin/users", {
    method: "POST",
    body: JSON.stringify({
      email: ADMIN_EMAIL,
      password: ADMIN_PASSWORD,
      email_confirm: true,
      user_metadata: {
        nombre_completo: ADMIN_NAME,
        pais: ADMIN_PAIS,
      },
    }),
  });

  if (!create.ok) {
    console.error("Error creando usuario:", create.data);
    throw new Error("No se pudo crear el usuario");
  }

  const userId = create.data.user?.id ?? create.data.id;
  console.log(`✅ Usuario creado: ${userId}`);

  // 3. Asegurar perfil y rol admin
  const profileCheck = await api(`/rest/v1/profiles?id=eq.${userId}&select=*`);
  if (!profileCheck.data?.length) {
    console.log("📝 Creando perfil manualmente...");
    const insert = await api("/rest/v1/profiles", {
      method: "POST",
      headers: { Prefer: "return=representation" },
      body: JSON.stringify({
        id: userId,
        email: ADMIN_EMAIL,
        nombre_completo: ADMIN_NAME,
        pais: ADMIN_PAIS,
        rol: "admin",
      }),
    });
    if (!insert.ok) {
      console.error("Error creando perfil:", insert.data);
    } else {
      console.log("✅ Perfil creado");
    }
  } else {
    const update = await api(`/rest/v1/profiles?id=eq.${userId}`, {
      method: "PATCH",
      body: JSON.stringify({
        nombre_completo: ADMIN_NAME,
        pais: ADMIN_PAIS,
        rol: "admin",
      }),
    });
    if (update.ok) console.log("✅ Perfil actualizado a admin");
  }

  // 4. Curso piloto — ejecutar: npm run seed:ml
  const courses = await api("/rest/v1/courses?select=slug");
  if (!courses.data?.length) {
    console.log("📚 Sin cursos. Ejecutá: npm run seed:ml");
  } else {
    console.log(`✅ Ya hay ${courses.data.length} curso(s) en la base`);
  }

  // 5. Probar login
  const login = await publicApi("/auth/v1/token?grant_type=password", {
    method: "POST",
    body: JSON.stringify({ email: ADMIN_EMAIL, password: ADMIN_PASSWORD }),
  });

  if (login.ok) {
    console.log("✅ Login verificado correctamente");
  } else {
    console.warn("⚠️  Login falló:", login.data);
  }

  console.log("\n🎉 Listo! Credenciales de acceso:");
  console.log(`   URL:      http://localhost:3000/login`);
  console.log(`   Email:    ${ADMIN_EMAIL}`);
  console.log(`   Password: ${ADMIN_PASSWORD}`);
  console.log(`   Admin:    http://localhost:3000/admin`);
}

main().catch((err) => {
  console.error("\n❌ Error:", err.message);
  process.exit(1);
});
