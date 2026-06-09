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
const COURSE_SLUG = process.argv[2] || "conceptos-inteligencia-artificial";

const h = {
  apikey: KEY,
  Authorization: `Bearer ${KEY}`,
  "Content-Type": "application/json",
};

async function api(path, options = {}) {
  const res = await fetch(`${URL}${path}`, {
    ...options,
    headers: { ...h, Prefer: options.prefer || "return=representation", ...options.headers },
  });
  const text = await res.text();
  return { ok: res.ok, data: text ? JSON.parse(text) : null };
}

function verificationCode() {
  const chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
  let code = "ALIAA-";
  for (let i = 0; i < 8; i++) {
    code += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return code;
}

async function main() {
  const users = await api("/auth/v1/admin/users?page=1&per_page=100");
  const user = users.data?.users?.find((u) => u.email === OWNER_EMAIL);
  if (!user) throw new Error(`Usuario no encontrado: ${OWNER_EMAIL}`);

  const courses = await api(
    `/rest/v1/courses?slug=eq.${COURSE_SLUG}&select=id,titulo`
  );
  const course = courses.data?.[0];
  if (!course) throw new Error(`Curso no encontrado: ${COURSE_SLUG}`);

  const lessons = await api(
    `/rest/v1/lessons?select=id,module:modules!inner(course_id)&module.course_id=eq.${course.id}`
  );

  for (const lesson of lessons.data ?? []) {
    await api("/rest/v1/lesson_progress", {
      method: "POST",
      prefer: "resolution=merge-duplicates",
      body: JSON.stringify({
        user_id: user.id,
        lesson_id: lesson.id,
        completado: true,
        completado_en: new Date().toISOString(),
      }),
    });
  }

  await api("/rest/v1/enrollments", {
    method: "POST",
    prefer: "resolution=merge-duplicates",
    body: JSON.stringify({
      user_id: user.id,
      course_id: course.id,
      progreso_porcentaje: 100,
      completado_en: new Date().toISOString(),
      nombre_certificado: OWNER_NAME,
    }),
  });

  const existing = await api(
    `/rest/v1/certificates?user_id=eq.${user.id}&course_id=eq.${course.id}&select=id`
  );

  let certId;
  if (existing.data?.length) {
    certId = existing.data[0].id;
    console.log("ℹ️  Certificado ya existía, reutilizando");
  } else {
    const created = await api("/rest/v1/certificates", {
      method: "POST",
      body: JSON.stringify({
        user_id: user.id,
        course_id: course.id,
        codigo_verificacion: verificationCode(),
        nombre_estudiante: OWNER_NAME,
      }),
    });
    if (!created.ok) throw new Error(JSON.stringify(created.data));
    certId = created.data[0].id;
  }

  const certUrl = `https://aliaa-six.vercel.app/dashboard/certificados/${certId}`;
  console.log(`✅ Certificado emitido para ${OWNER_EMAIL}`);
  console.log(`   Curso: ${course.titulo}`);
  console.log(`   URL:   ${certUrl}`);
}

main().catch((e) => {
  console.error("❌", e.message);
  process.exit(1);
});
