import { readFileSync, existsSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath, pathToFileURL } from "url";
import { findAdminUser } from "./emails.mjs";

const __dirname = dirname(fileURLToPath(import.meta.url));
const withAudio = resolve(__dirname, "./presentations-prompts-with-audio.mjs");
const { PRESENTATIONS } = await import(
  existsSync(withAudio)
    ? pathToFileURL(withAudio).href
    : "./presentations-prompts.mjs"
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
  titulo: "Cómo redactar prompts",
  slug: "como-redactar-prompts",
  descripcion:
    "Curso práctico de 20 minutos para escribir prompts claros y efectivos. Cuatro módulos de 5 minutos: fundamentos, fórmula Contexto-Tarea-Formato, técnicas avanzadas y ejemplos reales. Ideal para equipos que empiezan a usar ChatGPT, Copilot o asistentes similares.",
  descripcion_corta:
    "Prompts que funcionan. 4 módulos × 5 min, gratis, con certificado.",
  precio: 0,
  moneda: "USD",
  publicado: true,
  gratuito: true,
  duracion_horas: 1,
  nivel: "principiante",
  categoria: "IA Generativa",
  imagen_url: "/covers/como-redactar-prompts.svg",
};

const MODULES = [
  {
    titulo: "Inicio",
    descripcion: "Orientación del curso.",
    lecciones: [
      {
        titulo: "Bienvenida",
        tipo: "texto",
        duracion_minutos: 2,
        descripcion: "Qué vas a aprender en 20 minutos.",
        contenido_texto: `# Cómo redactar prompts

Bienvenido a ALIAA. Este curso te enseña a **escribir instrucciones** que den respuestas útiles desde el primer intento.

## Estructura (20 minutos)

| Módulo | Tema | Duración |
|--------|------|----------|
| 1 | Fundamentos de la redacción | 5 min |
| 2 | Contexto, Tarea y Formato | 5 min |
| 3 | Rol, ejemplos e iteración | 5 min |
| 4 | Casos prácticos y checklist | 5 min |

## Cómo tomarlo

- Escuchá cada lección audiovisual con audio
- Probá los ejemplos en tu asistente favorito
- Aprobá la evaluación final para obtener tu certificado

> Si ya hiciste *Conocimientos de Inteligencia Artificial*, este curso profundiza en la parte práctica de los prompts.

Marcá esta lección como completada y empezá el Módulo 1.`,
      },
    ],
  },
  {
    titulo: "Módulo 1 — Fundamentos",
    descripcion: "Qué es redactar un prompt y por qué importa.",
    lecciones: [
      {
        titulo: "Fundamentos de la redacción",
        tipo: "video",
        duracion_minutos: 5,
        contenido_texto: PRESENTATIONS.fundamentos,
        descripcion: "Mentalidad y marco del curso.",
      },
    ],
  },
  {
    titulo: "Módulo 2 — Estructura CTF",
    descripcion: "Contexto, Tarea y Formato.",
    lecciones: [
      {
        titulo: "La fórmula Contexto + Tarea + Formato",
        tipo: "video",
        duracion_minutos: 5,
        contenido_texto: PRESENTATIONS.estructuraCTF,
        descripcion: "El esqueleto de todo buen prompt.",
      },
    ],
  },
  {
    titulo: "Módulo 3 — Técnicas",
    descripcion: "Rol, ejemplos, restricciones e iteración.",
    lecciones: [
      {
        titulo: "Técnicas que marcan la diferencia",
        tipo: "video",
        duracion_minutos: 5,
        contenido_texto: PRESENTATIONS.tecnicas,
        descripcion: "Llevar tus prompts al siguiente nivel.",
      },
    ],
  },
  {
    titulo: "Módulo 4 — Práctica",
    descripcion: "Ejemplos reales y checklist final.",
    lecciones: [
      {
        titulo: "De malo a excelente: ejemplos reales",
        tipo: "video",
        duracion_minutos: 5,
        contenido_texto: PRESENTATIONS.casosPracticos,
        descripcion: "Comparaciones y checklist antes de enviar.",
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
        descripcion: "Síntesis del curso.",
        contenido_texto: `# Resumen

## Lo esencial

- **Contexto:** situá al modelo (quién sos, para quién es la respuesta)
- **Tarea:** un verbo concreto y, si hace falta, pasos numerados
- **Formato:** longitud, estructura y tono de la salida
- **Técnicas:** rol, ejemplos, restricciones e iteración
- **Checklist:** contexto + tarea clara + formato definido

## Próximos pasos en ALIAA

1. **Conocimientos de Inteligencia Artificial** — tokens, IA generativa y nociones base
2. **Fundamentos de Machine Learning** — cómo aprenden los modelos desde datos

Guardá tus mejores prompts y compartilos con tu equipo. ¡Gracias por aprender con ALIAA!`,
      },
      {
        titulo: "Evaluación final",
        tipo: "evaluacion",
        duracion_minutos: 3,
        contenido_texto: `# Evaluación

5 preguntas. Necesitás **70%** para aprobar y obtener tu certificado.`,
        quiz: {
          titulo: "Evaluación — Cómo redactar prompts",
          puntaje_aprobacion: 70,
          preguntas: [
            {
              pregunta: "¿Qué describe mejor redactar un prompt?",
              opciones: [
                "Escribir instrucciones claras en lenguaje natural para la IA",
                "Programar en Python obligatoriamente",
                "Configurar el router de internet",
                "Instalar un antivirus en la PC",
              ],
              respuesta_correcta: 0,
            },
            {
              pregunta: "En la fórmula CTF, ¿qué aporta el Contexto?",
              opciones: [
                "Situación, perfil y audiencia para orientar la respuesta",
                "El color de fondo del chat",
                "La velocidad de internet",
                "El nombre del servidor de la IA",
              ],
              respuesta_correcta: 0,
            },
            {
              pregunta: "¿Cuál es un ejemplo de Tarea bien redactada?",
              opciones: [
                "Listá 5 ideas de contenido con gancho para el primer segundo",
                "Hacé algo de marketing",
                "Mejorá esto",
                "Pensá un poco",
              ],
              respuesta_correcta: 0,
            },
            {
              pregunta: "¿Para qué sirve asignar un rol al modelo?",
              opciones: [
                "Orientar vocabulario, profundidad y estilo de la respuesta",
                "Cambiar la contraseña de la cuenta",
                "Aumentar la memoria RAM del navegador",
                "Desactivar el modo oscuro",
              ],
              respuesta_correcta: 0,
            },
            {
              pregunta: "¿Qué conviene hacer si la primera respuesta no es ideal?",
              opciones: [
                "Refinar el prompt con ajustes concretos e iterar",
                "Dar por terminado y no volver a preguntar",
                "Apagar la computadora",
                "Borrar la cuenta de usuario",
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
  console.log("📚 Creando curso Cómo redactar prompts...\n");

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
