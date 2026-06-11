import { readFileSync, existsSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath, pathToFileURL } from "url";
import { findAdminUser } from "./emails.mjs";

const __dirname = dirname(fileURLToPath(import.meta.url));
const withAudio = resolve(__dirname, "./presentations-aula-with-audio.mjs");
const { PRESENTATIONS } = await import(
  existsSync(withAudio)
    ? pathToFileURL(withAudio).href
    : "./presentations-aula.mjs"
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
  titulo: "Prompts para generar actividades en el aula",
  slug: "prompts-actividades-aula",
  descripcion:
    "Curso práctico de 30 minutos para docentes que quieren usar inteligencia artificial en la planificación, las actividades y la evaluación. Seis módulos de 5 minutos: IA en educación, prompts pedagógicos, planificación de asignaturas, rúbricas y aprendizaje activo, debates y personalización, y uso ético con checklist final.",
  descripcion_corta:
    "IA para docentes. 6 módulos × 5 min, gratis, con certificado.",
  precio: 0,
  moneda: "USD",
  publicado: true,
  gratuito: true,
  duracion_horas: 1,
  nivel: "principiante",
  categoria: "Educación",
  imagen_url: "/covers/prompts-actividades-aula.svg",
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
        descripcion: "Qué vas a aprender en 30 minutos.",
        contenido_texto: `# Prompts para generar actividades en el aula

Bienvenido a ALIAA. Este curso está pensado para **docentes** de primaria, secundaria y universidad que quieren usar la inteligencia artificial de forma práctica en su trabajo cotidiano.

## Estructura (30 minutos)

| Módulo | Tema | Duración |
|--------|------|----------|
| 1 | IA en educación: oportunidades y cuidados | 5 min |
| 2 | Cómo escribir prompts pedagógicos | 5 min |
| 3 | Planificar una asignatura con IA | 5 min |
| 4 | Rúbricas y aprendizaje activo | 5 min |
| 5 | Debates, simulaciones y personalización | 5 min |
| 6 | Evaluaciones, ética y checklist | 5 min |

## Cómo tomarlo

- Escuchá cada lección audiovisual con audio
- Probá los prompts en tu asistente de IA favorito
- Aprobá la evaluación final para obtener tu certificado

> Si todavía no hiciste *Cómo redactar prompts*, conviene hacerlo antes o después: este curso aplica esas ideas al contexto del aula.

Marcá esta lección como completada y empezá el Módulo 1.`,
      },
    ],
  },
  {
    titulo: "Módulo 1 — IA en educación",
    descripcion: "Oportunidades, riesgos y herramientas para docentes.",
    lecciones: [
      {
        titulo: "La IA como aliada del docente",
        tipo: "video",
        duracion_minutos: 5,
        contenido_texto: PRESENTATIONS.iaEnEducacion,
        descripcion: "Beneficios, cuidados y herramientas.",
      },
    ],
  },
  {
    titulo: "Módulo 2 — Prompts pedagógicos",
    descripcion: "Principios y errores frecuentes.",
    lecciones: [
      {
        titulo: "Anatomía del prompt docente",
        tipo: "video",
        duracion_minutos: 5,
        contenido_texto: PRESENTATIONS.promptPedagogico,
        descripcion: "Claridad, contexto, formato y ejemplos.",
      },
    ],
  },
  {
    titulo: "Módulo 3 — Planificar asignaturas",
    descripcion: "Prompts secuenciales para el programa.",
    lecciones: [
      {
        titulo: "Planificación paso a paso",
        tipo: "video",
        duracion_minutos: 5,
        contenido_texto: PRESENTATIONS.planificarAsignatura,
        descripcion: "Contexto, contenidos, metodología y evaluación.",
      },
    ],
  },
  {
    titulo: "Módulo 4 — Rúbricas y actividades",
    descripcion: "Evaluación y aprendizaje activo.",
    lecciones: [
      {
        titulo: "Rúbricas, gamificación y consignas",
        tipo: "video",
        duracion_minutos: 5,
        contenido_texto: PRESENTATIONS.rubricasYActividades,
        descripcion: "Del diseño a la consigna para alumnos.",
      },
    ],
  },
  {
    titulo: "Módulo 5 — Debates y personalización",
    descripcion: "Pensamiento crítico y apoyo diferenciado.",
    lecciones: [
      {
        titulo: "Debates, rutas y refuerzo",
        tipo: "video",
        duracion_minutos: 5,
        contenido_texto: PRESENTATIONS.debatesYPersonalizacion,
        descripcion: "Simulaciones y personalización del aprendizaje.",
      },
    ],
  },
  {
    titulo: "Módulo 6 — Evaluación y ética",
    descripcion: "Uso responsable en el aula.",
    lecciones: [
      {
        titulo: "Evaluaciones, ética y checklist",
        tipo: "video",
        duracion_minutos: 5,
        contenido_texto: PRESENTATIONS.evaluacionYEtica,
        descripcion: "Cierre práctico para llevar a clase.",
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

- **IA en educación:** aliada del docente, con revisión humana y política institucional clara
- **Prompt pedagógico:** claridad, contexto, pasos, formato y ejemplos
- **Planificación:** prompts secuenciales (contexto → contenidos → metodología → evaluación)
- **Actividades:** rúbricas, gamificación, debates y personalización
- **Ética:** transparencia con alumnos, revisión de contenidos y checklist antes de clase

## Próximos pasos en ALIAA

1. **Cómo redactar prompts** — fundamentos de redacción para cualquier asistente de IA
2. **Conocimientos de Inteligencia Artificial** — nociones base de IA generativa

Guardá tus mejores prompts docentes y probalos con una actividad real en las próximas semanas. ¡Gracias por aprender con ALIAA!`,
      },
      {
        titulo: "Evaluación final",
        tipo: "evaluacion",
        duracion_minutos: 5,
        contenido_texto: `# Evaluación

8 preguntas. Necesitás **70%** para aprobar y obtener tu certificado.`,
        quiz: {
          titulo: "Evaluación — Prompts para actividades en el aula",
          puntaje_aprobacion: 70,
          preguntas: [
            {
              pregunta: "¿Cuál es el rol principal del docente al usar IA en el aula?",
              opciones: [
                "Revisar, adaptar y decidir qué se enseña y evalúa",
                "Delegar por completo la planificación sin revisar",
                "Evitar cualquier uso de tecnología",
                "Sustituir todas las evaluaciones por notas automáticas",
              ],
              respuesta_correcta: 0,
            },
            {
              pregunta: "¿Qué mejora un prompt pedagógico respecto a uno vago?",
              opciones: [
                "Incluir nivel, asignatura, objetivo y formato de salida",
                "Usar solo una palabra como tema",
                "Pedir todo el año lectivo en un mensaje",
                "Omitir el nivel del estudiante",
              ],
              respuesta_correcta: 0,
            },
            {
              pregunta: "¿Por qué conviene planificar una asignatura con prompts secuenciales?",
              opciones: [
                "Para revisar y ajustar cada paso antes de continuar",
                "Porque la IA solo responde una vez por mes",
                "Para evitar definir objetivos",
                "Porque no se pueden pedir contenidos por unidades",
              ],
              respuesta_correcta: 0,
            },
            {
              pregunta: "Al diseñar una rúbrica con IA, ¿qué debe definirse primero?",
              opciones: [
                "La actividad o evidencia que se va a evaluar",
                "El color del aula",
                "La cantidad de alumnos por apellido",
                "El horario de recreo",
              ],
              respuesta_correcta: 0,
            },
            {
              pregunta: "¿Qué elemento es clave en una actividad gamificada?",
              opciones: [
                "Reglas claras, objetivo pedagógico y forma de evaluar",
                "Solo puntos sin consigna",
                "Eliminar toda consigna escrita",
                "Evitar que participen los estudiantes",
              ],
              respuesta_correcta: 0,
            },
            {
              pregunta: "Para un debate en clase generado con IA, ¿qué conviene incluir?",
              opciones: [
                "Roles, reglas, preguntas guía y criterios de evaluación",
                "Solo el nombre del tema sin contexto",
                "Únicamente la fecha del examen final",
                "Nada: improvisar sin estructura",
              ],
              respuesta_correcta: 0,
            },
            {
              pregunta: "¿Cuál es un uso ético responsable de la IA en educación?",
              opciones: [
                "Política clara con estudiantes y revisión de contenidos generados",
                "Ocultar el uso de IA a la institución siempre",
                "Publicar material sin leerlo",
                "Calificar automáticamente sin criterios",
              ],
              respuesta_correcta: 0,
            },
            {
              pregunta: "Antes de llevar una actividad generada con IA al aula, ¿qué conviene verificar?",
              opciones: [
                "Objetivo, contenido factual, evaluación alineada y dinámica en clase",
                "Solo que el texto sea largo",
                "Que no tenga título",
                "Que nadie más lo haya usado nunca",
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
  console.log("📚 Creando curso Prompts para actividades en el aula...\n");

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
  console.log(`   Catálogo:  https://aliaa-six.vercel.app/cursos/${COURSE.slug}`);
  console.log(`   Estudiar:  https://aliaa-six.vercel.app/dashboard/cursos/${courseId}`);
}

main().catch((e) => {
  console.error("❌", e.message);
  process.exit(1);
});
