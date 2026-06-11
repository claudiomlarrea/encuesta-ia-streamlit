import { readFileSync, existsSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath, pathToFileURL } from "url";
import { findAdminUser } from "./emails.mjs";

const __dirname = dirname(fileURLToPath(import.meta.url));
const withAudio = resolve(__dirname, "./presentations-reuniones-with-audio.mjs");
const { PRESENTATIONS } = await import(
  existsSync(withAudio)
    ? pathToFileURL(withAudio).href
    : "./presentations-reuniones.mjs"
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
  titulo: "IA para reuniones",
  slug: "ia-para-reuniones",
  descripcion:
    "Curso práctico de 25 minutos para preparar agendas, redactar actas y hacer seguimiento de acuerdos con inteligencia artificial. Ideal para equipos de empresa, gobierno, educación y proyectos remotos o híbridos.",
  descripcion_corta:
    "Agendas, actas y seguimiento. 4×5 min, gratis, certificado.",
  precio: 0,
  moneda: "USD",
  publicado: true,
  gratuito: true,
  duracion_horas: 1,
  nivel: "principiante",
  categoria: "IA para Negocios",
  imagen_url: "/covers/ia-para-reuniones.svg",
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
        descripcion: "Qué vas a aprender sobre reuniones con IA.",
        contenido_texto: `# IA para reuniones

Bienvenido a ALIAA. Este curso te enseña a usar inteligencia artificial **antes, durante y después** de las reuniones para que sean más cortas, claras y con seguimiento real.

## Estructura (~25 minutos)

| Módulo | Tema | Duración |
|--------|------|----------|
| 1 | Reuniones más efectivas con IA | 5 min |
| 2 | Preparar agenda y convocatoria | 5 min |
| 3 | Actas y seguimiento de acuerdos | 5 min |
| 4 | Buenas prácticas y errores comunes | 5 min |

## Qué vas a poder hacer

- Armar agendas con tiempos y objetivos por tema
- Convertir notas sueltas en actas formales
- Generar tablas de seguimiento con responsables y plazos
- Redactar mails de cierre y recordatorios
- Evaluar si realmente hace falta reunirse

## Cursos relacionados

1. **Cómo redactar prompts** — mejorar tus instrucciones
2. **IA para equipos administrativos** — documentos de oficina
3. **Conocimientos de Inteligencia Artificial** — base conceptual

Marcá esta lección como completada y empezá el Módulo 1.`,
      },
    ],
  },
  {
    titulo: "Módulo 1 — Fundamentos",
    descripcion: "Antes, durante y después de la reunión.",
    lecciones: [
      {
        titulo: "Reuniones más efectivas con IA",
        tipo: "video",
        duracion_minutos: 5,
        contenido_texto: PRESENTATIONS.reunionesEfectivas,
        descripcion: "Por qué y cuándo usar IA en reuniones.",
      },
    ],
  },
  {
    titulo: "Módulo 2 — Preparación",
    descripcion: "Agenda, convocatoria y materiales previos.",
    lecciones: [
      {
        titulo: "Preparar agenda y convocatoria",
        tipo: "video",
        duracion_minutos: 5,
        contenido_texto: PRESENTATIONS.prepararAgenda,
        descripcion: "Objetivos, tiempos y lectura previa.",
      },
    ],
  },
  {
    titulo: "Módulo 3 — Documentación",
    descripcion: "Actas, tareas y reuniones remotas.",
    lecciones: [
      {
        titulo: "Actas y seguimiento de acuerdos",
        tipo: "video",
        duracion_minutos: 5,
        contenido_texto: PRESENTATIONS.actasYSeguimiento,
        descripcion: "De notas a acta y tabla de compromisos.",
      },
    ],
  },
  {
    titulo: "Módulo 4 — Buenas prácticas",
    descripcion: "Errores, privacidad y plantillas.",
    lecciones: [
      {
        titulo: "Buenas prácticas en reuniones con IA",
        tipo: "video",
        duracion_minutos: 5,
        contenido_texto: PRESENTATIONS.buenasPracticas,
        descripcion: "Grabaciones, consentimiento y prompts listos.",
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
        descripcion: "Síntesis y plantillas.",
        contenido_texto: `# Resumen

## Lo esencial

- **Antes:** agenda con objetivo, tiempos y lectura previa resumida
- **Durante:** notas por tema, roles claros (facilitador, notas)
- **Después:** acta + tabla de seguimiento + mail de cierre
- **Revisar** siempre nombres, plazos y acuerdos antes de circular
- **Grabar/transcribir** solo con política y consentimiento del equipo

## 3 prompts para guardar

**Agenda:**
> Armá agenda de 45 min con 4 temas, tiempo por ítem, resultado esperado y lectura previa.

**Acta:**
> Convertí estas notas en acta formal: asistentes, acuerdos numerados con responsable y fecha límite.

**Seguimiento:**
> Creá tabla con columnas: acuerdo, responsable, plazo, estado. Y mail de cierre de 5 líneas.

¡Gracias por aprender con ALIAA!`,
      },
      {
        titulo: "Evaluación final",
        tipo: "evaluacion",
        duracion_minutos: 3,
        contenido_texto: `# Evaluación

5 preguntas. Necesitás **70%** para aprobar y obtener tu certificado.`,
        quiz: {
          titulo: "Evaluación — IA para reuniones",
          puntaje_aprobacion: 70,
          preguntas: [
            {
              pregunta: "¿En qué fase de la reunión la IA ayuda a convertir notas en acta?",
              opciones: [
                "Después de la reunión",
                "Solo antes de convocar",
                "Solo durante la videollamada sin notas",
                "Nunca, la IA no sirve para actas",
              ],
              respuesta_correcta: 0,
            },
            {
              pregunta: "¿Qué debe incluir una buena convocatoria preparada con IA?",
              opciones: [
                "Objetivo, agenda con tiempos y resultado esperado por tema",
                "Solo la hora y el enlace de Zoom",
                "Únicamente la lista de asistentes",
                "Un chiste para romper el hielo",
              ],
              respuesta_correcta: 0,
            },
            {
              pregunta: "¿Qué es fundamental verificar en un acta generada por IA?",
              opciones: [
                "Que los acuerdos y plazos reflejen lo realmente decidido",
                "Que tenga más de diez páginas",
                "Que elimine todos los nombres",
                "Que no tenga numeración",
              ],
              respuesta_correcta: 0,
            },
            {
              pregunta: "¿Qué columna es clave en la tabla de seguimiento post-reunión?",
              opciones: [
                "Responsable y fecha límite de cada acuerdo",
                "Color favorito del participante",
                "Talle de remera del equipo",
                "Cantidad de cafés servidos",
              ],
              respuesta_correcta: 0,
            },
            {
              pregunta: "Antes de grabar o transcribir una reunión con IA, ¿qué debés hacer?",
              opciones: [
                "Consultar política de la organización y avisar a los participantes",
                "Grabar en secreto para mayor precisión",
                "Publicar la grabación en redes sociales",
                "Eliminar el acta después de transcribir",
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
  console.log("📚 Creando curso IA para reuniones...\n");

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
