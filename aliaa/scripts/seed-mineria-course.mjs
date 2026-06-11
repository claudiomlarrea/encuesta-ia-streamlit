import { readFileSync, existsSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath, pathToFileURL } from "url";
import { findAdminUser } from "./emails.mjs";

const __dirname = dirname(fileURLToPath(import.meta.url));
const withAudio = resolve(__dirname, "./presentations-mineria-with-audio.mjs");
const { PRESENTATIONS } = await import(
  existsSync(withAudio)
    ? pathToFileURL(withAudio).href
    : "./presentations-mineria.mjs"
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
  titulo: "IA para equipos de minería",
  slug: "ia-para-equipos-de-mineria",
  descripcion:
    "Curso práctico de 25 minutos para personal de faena, planta, seguridad, medio ambiente y administración de operaciones mineras. Aprendé a usar IA para partes de turno, informes, checklists y comunicación, con buenas prácticas de confidencialidad y revisión profesional.",
  descripcion_corta:
    "IA en minería. Turnos, SSO, informes. 4×5 min, gratis, certificado.",
  precio: 0,
  moneda: "USD",
  publicado: true,
  gratuito: true,
  duracion_horas: 1,
  nivel: "principiante",
  categoria: "IA para Negocios",
  imagen_url: "/covers/ia-para-equipos-de-mineria.svg",
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
        descripcion: "Para quién es este curso en el sector minero.",
        contenido_texto: `# IA para equipos de minería

Bienvenido a ALIAA. Este curso está pensado para quienes trabajan en **operaciones mineras**: faena, planta, seguridad e higiene, medio ambiente, mantenimiento y administración de sitio.

## Estructura (~25 minutos)

| Módulo | Tema | Duración |
|--------|------|----------|
| 1 | La IA en operaciones mineras | 5 min |
| 2 | Informes y comunicación de faena | 5 min |
| 3 | Datos operativos y seguimiento | 5 min |
| 4 | Seguridad, ambiente y buenas prácticas | 5 min |

## Qué vas a poder hacer

- Redactar partes de turno y novedades de faena
- Preparar actas de comité de seguridad
- Resumir informes de producción y mantenimiento
- Armar tablas de incidentes y checklists de inspección
- Usar la IA sin exponer datos sensibles de la operación

## Cursos relacionados en ALIAA

1. **Conocimientos de Inteligencia Artificial** — nociones base
2. **IA para equipos administrativos** — gestión de oficina e instituciones
3. **Cómo redactar prompts** — profundizar en instrucciones efectivas

Marcá esta lección como completada y empezá el Módulo 1.`,
      },
    ],
  },
  {
    titulo: "Módulo 1 — Operaciones",
    descripcion: "La IA en faena y límites de uso.",
    lecciones: [
      {
        titulo: "La IA en operaciones mineras",
        tipo: "video",
        duracion_minutos: 5,
        contenido_texto: PRESENTATIONS.iaEnMineria,
        descripcion: "Casos de uso, límites y políticas del sitio.",
      },
    ],
  },
  {
    titulo: "Módulo 2 — Comunicación",
    descripcion: "Partes de turno, mails y actas.",
    lecciones: [
      {
        titulo: "Informes y comunicación de faena",
        tipo: "video",
        duracion_minutos: 5,
        contenido_texto: PRESENTATIONS.informesComunicacion,
        descripcion: "Turnos, contratistas y comité de seguridad.",
      },
    ],
  },
  {
    titulo: "Módulo 3 — Datos operativos",
    descripcion: "Producción, mantenimiento y seguimiento.",
    lecciones: [
      {
        titulo: "Datos operativos y seguimiento",
        tipo: "video",
        duracion_minutos: 5,
        contenido_texto: PRESENTATIONS.datosOperativos,
        descripcion: "Resúmenes, tablas e inspecciones.",
      },
    ],
  },
  {
    titulo: "Módulo 4 — Seguridad y ambiente",
    descripcion: "SSO, medio ambiente, confidencialidad.",
    lecciones: [
      {
        titulo: "Seguridad, ambiente y buenas prácticas",
        tipo: "video",
        duracion_minutos: 5,
        contenido_texto: PRESENTATIONS.seguridadAmbiente,
        descripcion: "EPP, informes ambientales y flujo de trabajo.",
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

- La IA **asiste** en partes de turno, informes y comunicación — no reemplaza criterio técnico ni de seguridad
- **No** decidir detención de faena ni riesgos críticos solo con IA
- **Anonimizá** datos sensibles: ubicaciones, personal, reservas, contratos
- Flujo: **borrador con IA → revisión del supervisor o especialista → registro oficial**
- Verificá cifras de producción, horarios y compromisos de actas

## Prompts útiles para guardar

1. *Convertí estas notas en parte de turno: producción, demoras, equipos detenidos y pendientes. Formato tabla.*
2. *Redactá recordatorio de uso de EPP en zona de altura, tono firme y respetuoso, máx. 100 palabras.*
3. *Resumí informe de producción en 5 viñetas: desvíos, causas y acciones en curso.*
4. *Armá checklist semanal de inspección según este procedimiento.*

Compartí estos modelos con tu equipo. ¡Gracias por aprender con ALIAA!`,
      },
      {
        titulo: "Evaluación final",
        tipo: "evaluacion",
        duracion_minutos: 3,
        contenido_texto: `# Evaluación

5 preguntas. Necesitás **70%** para aprobar y obtener tu certificado.`,
        quiz: {
          titulo: "Evaluación — IA para equipos de minería",
          puntaje_aprobacion: 70,
          preguntas: [
            {
              pregunta: "¿Cuál es un uso adecuado de la IA en minería?",
              opciones: [
                "Redactar un borrador de parte de turno",
                "Decidir detener faena por riesgo crítico sin supervisión",
                "Publicar ubicación exacta de personal en tiempo real",
                "Reemplazar el análisis de causa raíz de incidentes",
              ],
              respuesta_correcta: 0,
            },
            {
              pregunta: "Antes de pegar un documento interno en un asistente de IA, ¿qué debés hacer?",
              opciones: [
                "Consultar la política de TI y seguridad de tu operación",
                "Agregar todos los datos para mayor precisión",
                "Compartir el archivo en redes sociales",
                "Enviar copia al proveedor de la IA por mail",
              ],
              respuesta_correcta: 0,
            },
            {
              pregunta: "¿Qué información NO deberías pegar en herramientas de IA públicas?",
              opciones: [
                "Reservas minerales, contratos y datos de personal identificable",
                "Un recordatorio genérico de uso de casco",
                "Un ejemplo anonimizado de formato de tabla",
                "Un borrador sin cifras reales",
              ],
              respuesta_correcta: 0,
            },
            {
              pregunta: "¿Cuál es el flujo recomendado para un informe de faena?",
              opciones: [
                "Borrador con IA, revisión del supervisor, luego registro oficial",
                "Enviar directo lo que genera la IA al sistema",
                "Solo usar IA para decisiones de seguridad crítica",
                "Omitir revisión de cifras de producción",
              ],
              respuesta_correcta: 0,
            },
            {
              pregunta: "¿Para qué sirve pedir 'formato tabla' en un parte de turno?",
              opciones: [
                "Organizar producción, demoras y pendientes de forma clara para el relevo",
                "Cambiar el color del informe impreso",
                "Enviar automáticamente al regulador ambiental",
                "Desactivar procedimientos de seguridad",
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
  console.log("📚 Creando curso IA para equipos de minería...\n");

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
