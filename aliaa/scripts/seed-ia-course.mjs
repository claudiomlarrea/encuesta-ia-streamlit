import { readFileSync, existsSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath, pathToFileURL } from "url";
import { findAdminUser } from "./emails.mjs";

const __dirname = dirname(fileURLToPath(import.meta.url));
const withAudio = resolve(__dirname, "./presentations-ia-with-audio.mjs");
const { PRESENTATIONS } = await import(
  existsSync(withAudio)
    ? pathToFileURL(withAudio).href
    : "./presentations-ia.mjs"
);

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

const COURSE = {
  titulo: "Conceptos en Inteligencia Artificial",
  slug: "conceptos-inteligencia-artificial",
  descripcion:
    "Curso express para entender qué es la Inteligencia Artificial, cómo se usa hoy, qué es un token y cómo escribir buenos prompts. Ideal como primer contacto con la IA aplicada, sin tecnicismos innecesarios.",
  descripcion_corta:
    "IA, tokens y prompts. ~20 minutos, gratis, con certificado.",
  precio: 0,
  moneda: "USD",
  publicado: true,
  gratuito: true,
  duracion_horas: 1,
  nivel: "principiante",
  categoria: "IA para Negocios",
  imagen_url: "/covers/conceptos-inteligencia-artificial.svg",
};

const MODULES = [
  {
    titulo: "Inicio",
    descripcion: "Orientación rápida del curso.",
    lecciones: [
      {
        titulo: "Bienvenida al curso",
        tipo: "texto",
        duracion_minutos: 2,
        descripcion: "Qué vas a aprender en este curso express.",
        contenido_texto: `# Conceptos en Inteligencia Artificial

Bienvenido a ALIAA. Este es un **curso express** para que entiendas la IA con claridad, sin abrumarte.

## En este curso vas a aprender

1. Qué es la Inteligencia Artificial y en qué se diferencia de un programa común
2. La diferencia entre IA tradicional e IA generativa
3. Qué es un **token** y por qué importa cuando usás ChatGPT u otros asistentes
4. Qué es un **prompt** y cómo escribir instrucciones que den mejores respuestas

## Cómo tomarlo

- Escuchá las lecciones audiovisuales con audio
- Leé el cierre breve
- Aprobá la evaluación final para obtener tu certificado

> Duración total: **unos 20 minutos**. Ideal para compartir con tu equipo antes de cursos más avanzados.

Marcá esta lección como completada y continuá.`,
      },
    ],
  },
  {
    titulo: "Conceptos esenciales",
    descripcion: "Definiciones claras con ejemplos del mundo real.",
    lecciones: [
      {
        titulo: "¿Qué es la Inteligencia Artificial?",
        tipo: "video",
        duracion_minutos: 5,
        contenido_texto: PRESENTATIONS.queEsIA,
        descripcion: "Definición, tipos de IA y ejemplos cotidianos.",
      },
      {
        titulo: "¿Qué es un token?",
        tipo: "video",
        duracion_minutos: 5,
        contenido_texto: PRESENTATIONS.queEsToken,
        descripcion: "Unidad básica del lenguaje en modelos de IA generativa.",
      },
      {
        titulo: "¿Qué es un prompt?",
        tipo: "video",
        duracion_minutos: 5,
        contenido_texto: PRESENTATIONS.queEsPrompt,
        descripcion: "Cómo dar instrucciones claras a un asistente de IA.",
      },
    ],
  },
  {
    titulo: "Cierre y evaluación",
    descripcion: "Resumen y certificado.",
    lecciones: [
      {
        titulo: "Resumen y próximos pasos",
        tipo: "texto",
        duracion_minutos: 1,
        descripcion: "Síntesis del curso y ruta de continuidad.",
        contenido_texto: `# Resumen

## Lo esencial

- **IA:** sistemas que realizan tareas que requieren inteligencia humana, entrenados con datos
- **IA generativa:** crea contenido nuevo (texto, imágenes, código)
- **Token:** unidad mínima de texto que procesa un modelo; define límites y costos
- **Prompt:** la instrucción que le das al modelo; claridad y contexto mejoran la respuesta

## Próximos pasos en ALIAA

Si querés profundizar, te recomendamos:

1. **Fundamentos de Machine Learning** — cómo aprenden los modelos desde datos
2. Próximamente: cursos de modelos, métricas y proyectos con Python

Participá en el foro si tenés dudas. ¡Gracias por aprender con ALIAA!`,
      },
      {
        titulo: "Evaluación final",
        tipo: "evaluacion",
        duracion_minutos: 2,
        contenido_texto: `# Evaluación

4 preguntas rápidas. Necesitás **70%** para aprobar y obtener tu certificado.`,
        quiz: {
          titulo: "Evaluación — Conceptos en IA",
          puntaje_aprobacion: 70,
          preguntas: [
            {
              pregunta: "¿Qué describe mejor a la Inteligencia Artificial?",
              opciones: [
                "Sistemas que realizan tareas que requieren inteligencia humana",
                "Cualquier programa con botones y formularios",
                "Solo robots físicos en fábricas",
                "Un tipo de base de datos",
              ],
              respuesta_correcta: 0,
            },
            {
              pregunta: "¿Qué hace la IA generativa?",
              opciones: [
                "Crea contenido nuevo como texto o imágenes",
                "Solo elimina virus de la computadora",
                "Únicamente clasifica emails",
                "Reemplaza todas las bases de datos",
              ],
              respuesta_correcta: 0,
            },
            {
              pregunta: "¿Qué es un token en un modelo de lenguaje?",
              opciones: [
                "Una unidad básica en la que el modelo divide el texto",
                "Una contraseña de acceso a la API",
                "Un archivo de imagen comprimido",
                "Un tipo de certificado digital",
              ],
              respuesta_correcta: 0,
            },
            {
              pregunta: "¿Qué es un prompt?",
              opciones: [
                "La instrucción o pregunta que le das a un modelo de IA",
                "Un virus que infecta el navegador",
                "El nombre del servidor donde vive ChatGPT",
                "Un tipo de contraseña de dos factores",
              ],
              respuesta_correcta: 0,
            },
          ],
        },
      },
    ],
  },
];

async function main() {
  console.log("📚 Creando curso de Conceptos en IA...\n");

  const existing = await api(
    `/rest/v1/courses?slug=eq.${COURSE.slug}&select=id`
  );
  if (existing.data?.length) {
    await api(`/rest/v1/courses?id=eq.${existing.data[0].id}`, {
      method: "DELETE",
      prefer: "return=minimal",
    });
    console.log("🗑️  Versión anterior eliminada");
  }

  const { data: course, ok } = await api("/rest/v1/courses", {
    method: "POST",
    body: JSON.stringify(COURSE),
  });
  if (!ok) throw new Error("Error creando curso: " + JSON.stringify(course));
  console.log(`✅ Curso creado: ${course[0].titulo} (${course[0].id})`);

  const courseId = course[0].id;

  for (let mi = 0; mi < MODULES.length; mi++) {
    const mod = MODULES[mi];
    const { data: moduleRows, ok: modOk } = await api("/rest/v1/modules", {
      method: "POST",
      body: JSON.stringify({
        course_id: courseId,
        titulo: mod.titulo,
        descripcion: mod.descripcion,
        orden: mi,
      }),
    });
    if (!modOk) throw new Error("Error módulo: " + JSON.stringify(moduleRows));
    const moduleId = moduleRows[0].id;
    console.log(`  📁 Módulo ${mi + 1}: ${mod.titulo}`);

    for (let li = 0; li < mod.lecciones.length; li++) {
      const lec = mod.lecciones[li];
      const { quiz, ...lessonData } = lec;
      const { data: lessonRows, ok: lecOk } = await api("/rest/v1/lessons", {
        method: "POST",
        body: JSON.stringify({
          module_id: moduleId,
          titulo: lessonData.titulo,
          descripcion: lessonData.descripcion,
          tipo: lessonData.tipo,
          contenido_url: lessonData.contenido_url || null,
          contenido_texto: lessonData.contenido_texto || null,
          duracion_minutos: lessonData.duracion_minutos,
          orden: li,
          vista_previa: mi === 0 && li === 0,
        }),
      });
      if (!lecOk) throw new Error("Error lección: " + JSON.stringify(lessonRows));
      console.log(`    📄 Lección: ${lec.titulo}`);

      if (quiz) {
        const { data: quizRows } = await api("/rest/v1/quizzes", {
          method: "POST",
          body: JSON.stringify({
            lesson_id: lessonRows[0].id,
            titulo: quiz.titulo,
            puntaje_aprobacion: quiz.puntaje_aprobacion,
          }),
        });
        const quizId = quizRows[0].id;
        for (let qi = 0; qi < quiz.preguntas.length; qi++) {
          const q = quiz.preguntas[qi];
          await api("/rest/v1/quiz_questions", {
            method: "POST",
            prefer: "return=minimal",
            body: JSON.stringify({
              quiz_id: quizId,
              pregunta: q.pregunta,
              opciones: q.opciones,
              respuesta_correcta: q.respuesta_correcta,
              orden: qi,
            }),
          });
        }
        console.log(`    ✅ Quiz con ${quiz.preguntas.length} preguntas`);
      }
    }
  }

  const users = await api(`/auth/v1/admin/users?page=1&per_page=50`);
  const admin = findAdminUser(users.data?.users ?? []);
  if (admin) {
    await api("/rest/v1/enrollments", {
      method: "POST",
      prefer: "resolution=merge-duplicates",
      body: JSON.stringify({ user_id: admin.id, course_id: courseId }),
    });
    console.log(`\n👤 Admin inscrito en el curso`);
  }

  const totalMin = MODULES.flatMap((m) => m.lecciones).reduce(
    (s, l) => s + l.duracion_minutos,
    0
  );

  console.log(`\n🎉 Curso listo! (${totalMin} minutos)`);
  console.log(`   Catálogo:  http://localhost:3000/cursos/${COURSE.slug}`);
  console.log(`   Estudiar:  http://localhost:3000/dashboard/cursos/${courseId}`);
}

main().catch((e) => {
  console.error("❌", e.message);
  process.exit(1);
});
