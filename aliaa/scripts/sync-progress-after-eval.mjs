/**
 * Si el alumno aprobó la evaluación final pero el progreso quedó incompleto
 * (p. ej. escuchó audios antes del auto-marcado), completa todas las lecciones
 * del curso y sincroniza inscripción + certificado.
 */
import { readFileSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";
import { findAdminUser } from "./emails.mjs";

const __dirname = dirname(fileURLToPath(import.meta.url));
const envPath = resolve(__dirname, "../.env.local");

function loadEnv() {
  const env = {};
  for (const line of readFileSync(envPath, "utf8").split("\n")) {
    const t = line.trim();
    if (!t || t.startsWith("#")) continue;
    const i = t.indexOf("=");
    if (i > 0) env[t.slice(0, i)] = t.slice(i + 1);
  }
  return env;
}

const env = loadEnv();
const URL = env.NEXT_PUBLIC_SUPABASE_URL;
const KEY = env.SUPABASE_SERVICE_ROLE_KEY;

async function api(path, options = {}) {
  const res = await fetch(`${URL}${path}`, {
    ...options,
    headers: {
      apikey: KEY,
      Authorization: `Bearer ${KEY}`,
      "Content-Type": "application/json",
      Prefer: options.prefer || "return=representation",
      ...options.headers,
    },
  });
  const text = await res.text();
  return { ok: res.ok, data: text ? JSON.parse(text) : null };
}

function generateVerificationCode() {
  const chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
  let code = "ALIAA-";
  for (let i = 0; i < 8; i++) code += chars[Math.floor(Math.random() * chars.length)];
  return code;
}

async function main() {
  const users = await api("/auth/v1/admin/users?page=1&per_page=50");
  const admin = findAdminUser(users.data?.users ?? []);
  if (!admin) throw new Error("Usuario admin no encontrado");

  const { data: enrollments } = await api(
    `/rest/v1/enrollments?user_id=eq.${admin.id}&select=id,course_id,progreso_porcentaje,nombre_certificado,course:courses(titulo,slug)`
  );

  for (const enrollment of enrollments ?? []) {
    const courseId = enrollment.course_id;
    const courseTitle = enrollment.course?.titulo ?? courseId;

    const { data: modules } = await api(
      `/rest/v1/modules?course_id=eq.${courseId}&select=id,lessons(id,tipo,titulo)`
    );
    const lessons = (modules ?? []).flatMap((m) => m.lessons ?? []);
    if (!lessons.length) continue;

    const lessonIds = lessons.map((l) => l.id);
    const evalLesson = lessons.find((l) => l.tipo === "evaluacion");
    if (!evalLesson) continue;

    const { data: progressRows } = await api(
      `/rest/v1/lesson_progress?user_id=eq.${admin.id}&lesson_id=in.(${lessonIds.join(",")})&completado=eq.true&select=lesson_id`
    );
    const completed = new Set((progressRows ?? []).map((r) => r.lesson_id));

    if (!completed.has(evalLesson.id)) {
      console.log(`⏭️  ${courseTitle}: evaluación no aprobada, omitido`);
      continue;
    }

    if (completed.size === lessons.length && enrollment.progreso_porcentaje === 100) {
      console.log(`✅ ${courseTitle}: ya al 100%`);
      continue;
    }

    const missing = lessons.filter((l) => !completed.has(l.id));
    console.log(`\n📚 ${courseTitle}: completando ${missing.length} lección(es) pendiente(s)`);

    for (const lesson of missing) {
      await api("/rest/v1/lesson_progress", {
        method: "POST",
        prefer: "resolution=merge-duplicates",
        body: JSON.stringify({
          user_id: admin.id,
          lesson_id: lesson.id,
          completado: true,
          completado_en: new Date().toISOString(),
        }),
      });
      console.log(`   ✓ ${lesson.titulo}`);
    }

    await api(`/rest/v1/enrollments?id=eq.${enrollment.id}`, {
      method: "PATCH",
      prefer: "return=minimal",
      body: JSON.stringify({
        progreso_porcentaje: 100,
        completado_en: new Date().toISOString(),
      }),
    });

    const { data: existingCert } = await api(
      `/rest/v1/certificates?user_id=eq.${admin.id}&course_id=eq.${courseId}&select=id,codigo_verificacion`
    );

    if (!existingCert?.length) {
      const { data: profile } = await api(
        `/rest/v1/profiles?id=eq.${admin.id}&select=nombre_completo,email`
      );
      const nombre =
        enrollment.nombre_certificado ||
        profile?.[0]?.nombre_completo ||
        profile?.[0]?.email ||
        "Estudiante ALIAA";

      const { data: cert, ok } = await api("/rest/v1/certificates", {
        method: "POST",
        body: JSON.stringify({
          user_id: admin.id,
          course_id: courseId,
          codigo_verificacion: generateVerificationCode(),
          nombre_estudiante: nombre,
        }),
      });
      if (ok) {
        console.log(`   🎓 Certificado creado: ${cert[0].codigo_verificacion}`);
      }
    } else {
      console.log(`   🎓 Certificado existente: ${existingCert[0].codigo_verificacion}`);
    }
  }

  console.log("\n🎉 Sincronización lista");
}

main().catch((e) => {
  console.error("❌", e.message);
  process.exit(1);
});
