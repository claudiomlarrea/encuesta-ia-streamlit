import { readFileSync, existsSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath, pathToFileURL } from "url";
import { findAdminUser } from "./emails.mjs";

const __dirname = dirname(fileURLToPath(import.meta.url));
const withAudio = resolve(__dirname, "./presentations-admin-with-audio.mjs");
const { PRESENTATIONS } = await import(
  existsSync(withAudio)
    ? pathToFileURL(withAudio).href
    : "./presentations-admin.mjs"
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
  titulo: "IA para equipos administrativos",
  slug: "ia-para-equipos-administrativos",
  descripcion:
    "Curso práctico de 25 minutos para personal administrativo de empresas, gobiernos e instituciones. Aprendé a usar IA para mails, informes, actas, resúmenes y tablas, con buenas prácticas de confidencialidad y revisión humana. Sin conocimientos técnicos.",
  descripcion_corta:
    "IA en oficina. Mails, actas, resúmenes. 4×5 min, gratis, certificado.",
  precio: 0,
  moneda: "USD",
  publicado: true,
  gratuito: true,
  duracion_horas: 1,
  nivel: "principiante",
  categoria: "IA para Negocios",
  imagen_url: "/covers/ia-para-equipos-administrativos.svg",
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
        descripcion: "Para quién es este curso y qué vas a aprender.",
        contenido_texto: `# IA para equipos administrativos

Bienvenido a ALIAA. Este curso está pensado para quienes trabajan en **administración**, **gestión** o **mesa de entradas** en empresas, gobiernos, universidades u hospitales.

## Estructura (~25 minutos)

| Módulo | Tema | Duración |
|--------|------|----------|
| 1 | La IA en el trabajo administrativo | 5 min |
| 2 | Redactar documentos con IA | 5 min |
| 3 | Organizar información y ahorrar tiempo | 5 min |
| 4 | Buenas prácticas y confidencialidad | 5 min |

## Qué vas a poder hacer

- Redactar mails, circulares y notas con tono institucional
- Convertir notas de reunión en actas ordenadas
- Resumir informes y armar tablas de seguimiento
- Usar la IA con criterio y sin exponer datos sensibles

## Cursos relacionados en ALIAA

1. **Conocimientos de Inteligencia Artificial** — nociones base
2. **Cómo redactar prompts** — profundizar en instrucciones efectivas

Marcá esta lección como completada y empezá el Módulo 1.`,
      },
    ],
  },
  {
    titulo: "Módulo 1 — La IA en administración",
    descripcion: "Qué puede y qué no puede hacer la IA en tu área.",
    lecciones: [
      {
        titulo: "La IA en tu trabajo administrativo",
        tipo: "video",
        duracion_minutos: 5,
        contenido_texto: PRESENTATIONS.iaEnAdministracion,
        descripcion: "Casos de uso, límites y herramientas.",
      },
    ],
  },
  {
    titulo: "Módulo 2 — Documentos",
    descripcion: "Mails, circulares, actas y minutas.",
    lecciones: [
      {
        titulo: "Redactar documentos administrativos",
        tipo: "video",
        duracion_minutos: 5,
        contenido_texto: PRESENTATIONS.documentosAdministrativos,
        descripcion: "Fórmula CTF aplicada a la gestión.",
      },
    ],
  },
  {
    titulo: "Módulo 3 — Organización",
    descripcion: "Resúmenes, tablas y planificación.",
    lecciones: [
      {
        titulo: "Organizar información con IA",
        tipo: "video",
        duracion_minutos: 5,
        contenido_texto: PRESENTATIONS.organizarInformacion,
        descripcion: "De documentos largos a tablas y checklists.",
      },
    ],
  },
  {
    titulo: "Módulo 4 — Buenas prácticas",
    descripcion: "Confidencialidad, errores comunes y flujo de trabajo.",
    lecciones: [
      {
        titulo: "Buenas prácticas en el área administrativa",
        tipo: "video",
        duracion_minutos: 5,
        contenido_texto: PRESENTATIONS.buenasPracticas,
        descripcion: "Datos sensibles, revisión humana y próximos pasos.",
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

- La IA **asiste** en redacción, resúmenes y tablas — no reemplaza tu responsabilidad
- Usá **Contexto + Tarea + Formato** en cada pedido
- **Anonimizá** datos personales antes de pegar textos
- Flujo: **borrador con IA → revisión humana → envío**
- Verificá fechas, montos y referencias legales siempre

## Prompts útiles para guardar

1. *Redactá un mail cordial recordando plazo vencido, tono profesional, máx. 120 palabras*
2. *Convertí estas notas en acta con asistentes, acuerdos y responsables*
3. *Resumí en 5 viñetas para dirección, enfocate en decisiones y plazos*
4. *Armá tabla con columnas: responsable, tarea, fecha límite, prioridad*

Compartí estos modelos con tu equipo. ¡Gracias por aprender con ALIAA!`,
      },
      {
        titulo: "Evaluación final",
        tipo: "evaluacion",
        duracion_minutos: 3,
        contenido_texto: `# Evaluación

5 preguntas. Necesitás **70%** para aprobar y obtener tu certificado.`,
        quiz: {
          titulo: "Evaluación — IA para equipos administrativos",
          puntaje_aprobacion: 70,
          preguntas: [
            {
              pregunta: "¿Cuál es un uso adecuado de la IA en administración?",
              opciones: [
                "Redactar un borrador de circular interna",
                "Firmar contratos sin revisión humana",
                "Publicar datos personales de ciudadanos",
                "Decidir sanciones disciplinarias",
              ],
              respuesta_correcta: 0,
            },
            {
              pregunta: "Antes de pegar un documento en un asistente de IA, ¿qué conviene hacer con datos sensibles?",
              opciones: [
                "Anonimizar o no pegar la información",
                "Agregar más datos para que entienda mejor",
                "Compartir el expediente completo en redes",
                "Enviar capturas por WhatsApp",
              ],
              respuesta_correcta: 0,
            },
            {
              pregunta: "¿Qué significa la T en la fórmula CTF?",
              opciones: [
                "Tarea concreta que debe hacer la IA",
                "Tecnología del servidor",
                "Tiempo de respuesta del internet",
                "Tarifa del proveedor",
              ],
              respuesta_correcta: 0,
            },
            {
              pregunta: "¿Cuál es el flujo recomendado al usar IA en documentos oficiales?",
              opciones: [
                "Borrador con IA, revisión humana, luego envío",
                "Enviar directo lo que genera la IA",
                "Solo usar IA para decisiones legales",
                "Nunca revisar montos ni fechas",
              ],
              respuesta_correcta: 0,
            },
            {
              pregunta: "¿Para qué sirve pedir 'formato tabla' en un prompt?",
              opciones: [
                "Organizar información en columnas claras para seguimiento",
                "Cambiar el color del documento",
                "Imprimir automáticamente en PDF",
                "Enviar el mail sin asunto",
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
  console.log("📚 Creando curso IA para equipos administrativos...\n");

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
