import { readFileSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

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
const h = { apikey: KEY, Authorization: `Bearer ${KEY}` };

async function get(path) {
  const r = await fetch(`${URL}${path}`, { headers: h });
  const data = await r.json();
  if (!r.ok) throw new Error(`${path}: ${JSON.stringify(data)}`);
  return data;
}

const courses = await get(
  "/rest/v1/courses?select=id,titulo,slug,publicado,gratuito&publicado=eq.true&order=titulo"
);

for (const c of courses) {
  const mods = await get(
    `/rest/v1/modules?course_id=eq.${c.id}&select=id,titulo,orden&order=orden`
  );
  let lessons = 0;
  let quizzes = 0;
  let withAudio = 0;
  const types = {};

  for (const m of mods) {
    const ls = await get(
      `/rest/v1/lessons?module_id=eq.${m.id}&select=tipo,titulo,contenido_texto&order=orden`
    );
    for (const l of ls) {
      lessons++;
      types[l.tipo] = (types[l.tipo] || 0) + 1;
      if (l.tipo === "evaluacion") quizzes++;
      if (l.contenido_texto?.includes("audio")) withAudio++;
    }
  }

  const enroll = await get(
    `/rest/v1/enrollments?course_id=eq.${c.id}&select=progreso_porcentaje,profile:profiles(email,nombre_completo)`
  );
  const certs = await get(`/rest/v1/certificates?course_id=eq.${c.id}&select=id`);

  console.log(`\n=== ${c.titulo} ===`);
  console.log(`Módulos: ${mods.length} | Lecciones: ${lessons} | Quiz: ${quizzes} | Audio: ${withAudio}`);
  console.log(`Tipos: ${JSON.stringify(types)}`);
  mods.forEach((m) => console.log(`  ${m.orden}. ${m.titulo}`));
  console.log(`Inscriptos: ${enroll.length} | Certificados: ${certs.length}`);
  enroll.forEach((e) =>
    console.log(`  - ${e.profile?.email} (${e.profile?.nombre_completo || "sin nombre"}) → ${e.progreso_porcentaje}%`)
  );
}

const profiles = await get(
  "/rest/v1/profiles?select=email,rol,created_at,nombre_completo&order=created_at.desc"
);
console.log(`\n=== USUARIOS (${profiles.length}) ===`);
profiles.forEach((p) =>
  console.log(`${p.created_at?.slice(0, 10)} | ${p.email} | ${p.rol} | ${p.nombre_completo || ""}`)
);
