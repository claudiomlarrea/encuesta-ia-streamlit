import { readFileSync, existsSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath, pathToFileURL } from "url";
import { findAdminUser } from "./emails.mjs";

const __dirname = dirname(fileURLToPath(import.meta.url));
const withAudio = resolve(__dirname, "./presentations-ml-with-audio.mjs");
const { PRESENTATIONS } = await import(
  existsSync(withAudio)
    ? pathToFileURL(withAudio).href
    : "./presentations-ml.mjs"
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
  titulo: "Fundamentos de Machine Learning",
  slug: "fundamentos-machine-learning",
  descripcion:
    "El punto de partida ideal para profesionales latinoamericanos que quieren entender y aplicar Machine Learning. Aprendé los conceptos esenciales con lecciones audiovisuales narradas, lecturas guiadas, una actividad práctica y una evaluación con certificado verificable. Sin requisitos previos en IA: solo ganas de aprender.",
  descripcion_corta:
    "De cero a tu primer proyecto de ML. Conceptos claros, audio profesional, actividad práctica y certificado ALIAA.",
  precio: 0,
  moneda: "USD",
  publicado: true,
  gratuito: true,
  duracion_horas: 2,
  nivel: "principiante",
  categoria: "Machine Learning",
  imagen_url: "/covers/fundamentos-machine-learning.svg",
};

const MODULES = [
  {
    titulo: "Bienvenida",
    descripcion: "Orientación, objetivos y cómo aprovechar al máximo el curso.",
    lecciones: [
      {
        titulo: "Cómo tomar este curso",
        tipo: "texto",
        duracion_minutos: 12,
        descripcion: "Objetivos, metodología y recomendaciones de estudio.",
        contenido_texto: `# Bienvenido a ALIAA

Felicitaciones por dar el primer paso. Este curso fue diseñado para que entiendas Machine Learning sin abrumarte con matemáticas ni jerga innecesaria.

## ¿Para quién es este curso?

- Profesionales de negocios, salud, educación o tecnología
- Analistas de datos que quieren dar el salto al ML
- Emprendedores que exploran soluciones con IA
- Cualquier persona curiosa, sin experiencia previa en IA

## Objetivos de aprendizaje

Al finalizar vas a poder:

1. Explicar qué es Machine Learning y en qué se diferencia de la programación tradicional
2. Distinguir aprendizaje supervisado, no supervisado y por refuerzo
3. Describir el ciclo completo de un proyecto de ML
4. Definir un caso de uso real para tu contexto profesional

## Cómo está organizado

| Módulo | Contenido | Formato |
|--------|-----------|---------|
| Fundamentos | Conceptos clave de ML | Lecciones audiovisuales |
| Del problema al proyecto | Ciclo de trabajo y datos | Lecturas guiadas |
| Práctica guiada | Tu primer caso de uso | Actividad |
| Evaluación y cierre | Quiz + certificado | Evaluación |

## Recomendaciones

- Dedicá entre 30 y 45 minutos por sesión de estudio
- Escuchá cada lección con audio antes de marcarla como completada
- Tomá notas con tus propios ejemplos del sector en el que trabajás
- Participá en el foro si tenés dudas

> **Tip ALIAA:** No apures las lecciones audiovisuales. El audio está pensado para que absorbas cada idea con calma.

Cuando termines de leer esto, marcá la lección como completada y continuá con el Módulo 2.`,
      },
    ],
  },
  {
    titulo: "Fundamentos de ML",
    descripcion: "Los conceptos esenciales explicados con claridad y ejemplos reales.",
    lecciones: [
      {
        titulo: "¿Qué es Machine Learning?",
        tipo: "video",
        duracion_minutos: 9,
        contenido_texto: PRESENTATIONS.queEsML,
        descripcion: "Definición, aplicaciones en Latinoamérica y qué vas a lograr en el curso.",
      },
      {
        titulo: "Tipos de aprendizaje automático",
        tipo: "video",
        duracion_minutos: 10,
        contenido_texto: PRESENTATIONS.tiposAprendizaje,
        descripcion: "Supervisado, no supervisado y por refuerzo: cuándo usar cada uno.",
      },
    ],
  },
  {
    titulo: "Del problema al proyecto",
    descripcion: "Cómo pasar de una idea a un proyecto de ML bien planteado.",
    lecciones: [
      {
        titulo: "El ciclo de un proyecto de ML",
        tipo: "texto",
        duracion_minutos: 18,
        descripcion: "Las cinco etapas que todo proyecto exitoso recorre.",
        contenido_texto: `# El ciclo de un proyecto de Machine Learning

Todo proyecto de ML —desde predecir ventas hasta detectar fraude— sigue un ciclo ordenado. Saltarte un paso suele costar caro.

## Etapa 1: Definir el problema

Antes de elegir algoritmos, respondé:

- ¿Qué decisión queremos mejorar?
- ¿Qué métrica define el éxito? (menos errores, más ventas, menos churn...)
- ¿Tenemos datos históricos suficientes?

> Un buen problema está bien acotado. "Mejorar el negocio" no es un problema de ML. "Reducir el abandono de clientes en los próximos 30 días" sí lo es.

## Etapa 2: Recolectar y explorar datos

- Verificá calidad: valores faltantes, duplicados, errores de carga
- Explorá distribuciones y relaciones entre variables
- Preguntate: ¿estos datos representan la realidad que quiero predecir?

## Etapa 3: Preparar los datos

- Limpiar y transformar variables
- Dividir en entrenamiento y prueba (típicamente 80% / 20%)
- Nunca evalúes el modelo con los mismos datos con los que lo entrenaste

## Etapa 4: Entrenar y evaluar

- Empezá con un modelo simple
- Medí el rendimiento en datos que el modelo no vio
- Iterá: mejorá datos, probá otro enfoque, ajustá

## Etapa 5: Desplegar y monitorear

- Integrá el modelo en un proceso real (dashboard, alerta, API)
- Monitoreá si el rendimiento cae con el tiempo (deriva de datos)
- Documentá decisiones para tu equipo

## Resumen visual del ciclo

Problema → Datos → Preparación → Modelo → Evaluación → Producción → Monitoreo

En el curso avanzado de **Modelos y Métricas** profundizarás en algoritmos y técnicas de evaluación. Por ahora, lo importante es que entiendas el mapa completo.`,
      },
      {
        titulo: "Datos: tu activo más importante",
        tipo: "texto",
        duracion_minutos: 12,
        descripcion: "Por qué los datos determinan el éxito de cualquier modelo.",
        contenido_texto: `# Datos: el corazón de todo proyecto de ML

Hay un dicho en la industria: *garbage in, garbage out*. Si los datos son malos, ningún algoritmo los salvará.

## ¿Qué hace que un dato sea útil?

1. **Relevancia:** mide algo relacionado con tu problema
2. **Volumen:** suficientes ejemplos para aprender patrones
3. **Calidad:** pocos errores, pocos faltantes, bien documentados
4. **Representatividad:** refleja la realidad que querés predecir

## Tipos de datos que vas a encontrar

| Tipo | Ejemplo | Uso típico |
|------|---------|------------|
| Numérico | Edad, monto, temperatura | Regresión, scoring |
| Categórico | Ciudad, plan, rubro | Clasificación |
| Texto | Reseñas, emails | NLP, sentimiento |
| Fecha/hora | Timestamp de compra | Series temporales |

## Errores comunes al empezar

- Usar datos del pasado que no se parecen al presente
- Mezclar datos de entrenamiento y prueba
- Ignorar valores faltantes o outliers sin analizarlos
- Asumir que más datos siempre es mejor (la calidad importa más)

## Ejercicio mental

Pensá en un problema de tu trabajo o sector:

- ¿Qué datos tendrías disponibles?
- ¿Están etiquetados (con respuesta conocida)?
- ¿Son suficientes para entrenar un modelo?

Guardá estas respuestas: las vas a usar en la actividad práctica del Módulo 4.`,
      },
    ],
  },
  {
    titulo: "Práctica guiada",
    descripcion: "Aplicá lo aprendido definiendo tu primer caso de uso.",
    lecciones: [
      {
        titulo: "Define tu primer caso de uso",
        tipo: "actividad",
        duracion_minutos: 35,
        descripcion: "Plantilla guiada para diseñar un proyecto ML en tu contexto.",
        contenido_texto: `# Actividad: Tu primer caso de uso de ML

Completá esta plantilla con un problema real de tu entorno profesional. No hace falta programar todavía: el objetivo es pensar como un profesional de ML.

## Ejemplo resuelto (referencia)

**Problema:** Una fintech quiere anticipar qué usuarios dejarán de usar la app en los próximos 30 días.

**Métrica de éxito:** Detectar al menos el 70% de los usuarios que harán churn, con menos del 20% de falsas alarmas.

**Datos disponibles:** antigüedad de cuenta, frecuencia de login, monto promedio de transacciones, tickets de soporte, plan contratado.

**Tipo de aprendizaje:** Supervisado (clasificación), porque hay historial de usuarios que se fueron y usuarios que se quedaron.

**Primer paso:** Reunir 6 meses de datos etiquetados y validar calidad con el equipo de producto.

Usá este ejemplo como guía de nivel de detalle. Ahora completá el tuyo:

## Parte 1 — El problema

**¿Qué decisión querés mejorar?**
(Escribí 2-3 oraciones concretas)

**¿Cómo medirías el éxito?**
(Ejemplo: reducir churn un 10%, detectar 80% de fraudes...)

## Parte 2 — Los datos

**¿Qué datos tenés o podrías obtener?**
(Listá al menos 5 variables posibles)

**¿Tenés ejemplos con respuesta conocida (etiquetas)?**
- [ ] Sí → aprendizaje supervisado
- [ ] No → explorar no supervisado

**¿Cuántos registros históricos estimás tener?**
(Menos de 100 / 100-1.000 / más de 1.000)

## Parte 3 — El enfoque

**¿Es clasificación, regresión u otro tipo?**

**¿Qué riesgo tiene un error del modelo?**
(Ejemplo: falso positivo en fraude vs. falso negativo en diagnóstico)

## Parte 4 — Próximos pasos

**¿Qué harías primero para avanzar?**
(Ejemplo: reunir datos, hablar con el área de sistemas, tomar el curso de Modelos y Métricas...)

---

## Criterios de entrega

Para marcar esta actividad como completada, asegurate de haber respondido las cuatro partes. Podés escribirlo en un documento personal o en el foro del curso para recibir feedback de otros estudiantes.

> **Recuerda:** Un buen caso de uso bien definido vale más que diez modelos mal planteados.`,
      },
    ],
  },
  {
    titulo: "Evaluación y cierre",
    descripcion: "Validá tus conocimientos y recibí tu certificado ALIAA.",
    lecciones: [
      {
        titulo: "Evaluación final",
        tipo: "evaluacion",
        duracion_minutos: 12,
        contenido_texto: `# Evaluación final

Antes de comenzar, recordá:

- Son **5 preguntas** de opción múltiple
- Necesitás **70% o más** para aprobar
- Podés reintentar si no alcanzás el mínimo
- Al aprobar y completar el módulo de cierre, obtenés tu **certificado ALIAA**

Leé cada pregunta con calma. Cubren los módulos de fundamentos, tipos de aprendizaje, ciclo de proyecto y calidad de datos.

Cuando estés listo, respondé el cuestionario debajo.`,
        quiz: {
          titulo: "Evaluación final — Fundamentos de Machine Learning",
          puntaje_aprobacion: 70,
          preguntas: [
            {
              pregunta: "¿Qué caracteriza al aprendizaje supervisado?",
              opciones: [
                "Usa datos con etiquetas o respuestas conocidas",
                "No necesita datos históricos",
                "Solo funciona con imágenes",
                "No se aplica en negocios",
              ],
              respuesta_correcta: 0,
            },
            {
              pregunta: "¿Cuál es un ejemplo de aprendizaje no supervisado?",
              opciones: [
                "Agrupar clientes por comportamiento de compra",
                "Predecir si un email es spam",
                "Estimar el precio de una vivienda",
                "Clasificar documentos por categoría",
              ],
              respuesta_correcta: 0,
            },
            {
              pregunta: "¿Cuál debería ser el PRIMER paso de un proyecto de ML?",
              opciones: [
                "Entrenar un modelo complejo",
                "Definir el problema y la métrica de éxito",
                "Desplegar en producción",
                "Comprar infraestructura en la nube",
              ],
              respuesta_correcta: 1,
            },
            {
              pregunta: "¿Por qué se divide el dataset en entrenamiento y prueba?",
              opciones: [
                "Para evaluar el modelo en datos que no vio durante el entrenamiento",
                "Para acelerar el entrenamiento",
                "Porque los algoritmos lo exigen siempre",
                "Para eliminar outliers automáticamente",
              ],
              respuesta_correcta: 0,
            },
            {
              pregunta: "¿Qué significa 'garbage in, garbage out' en ML?",
              opciones: [
                "Si los datos son de mala calidad, el modelo también lo será",
                "Hay que eliminar todos los datos viejos",
                "Solo se usan datos de fuentes gratuitas",
                "Los modelos generan basura por defecto",
              ],
              respuesta_correcta: 0,
            },
          ],
        },
      },
      {
        titulo: "Cierre y próximos pasos",
        tipo: "texto",
        duracion_minutos: 6,
        descripcion: "Felicitaciones, resumen del recorrido y camino de continuidad.",
        contenido_texto: `# ¡Felicitaciones!

Completaste **Fundamentos de Machine Learning** de ALIAA. Recorriste un camino que muchos profesionales postergan por miedo a la complejidad técnica.

## Lo que lograste

- Entendiste qué es Machine Learning y para qué sirve
- Distinguiste los tres tipos de aprendizaje automático
- Conociste el ciclo completo de un proyecto de ML
- Definiste un caso de uso aplicado a tu contexto
- Aprobaste la evaluación y obtenés tu certificado verificable

## Tu certificado

Tu certificado ALIAA incluye un código QR único que cualquier empleador o cliente puede verificar en nuestra plataforma. Encontralo en **Mi Panel → Certificados**.

## ¿Qué sigue?

Este curso te dio las bases. Para profundizar en algoritmos, métricas de evaluación y proyectos con Python, te recomendamos el próximo curso de la ruta ALIAA:

### Próximo en la ruta: Modelos y Métricas de ML

- Regresión lineal y clasificación en profundidad
- Árboles de decisión y Random Forest
- Métricas: F1, precision, recall, RMSE
- Proyecto práctico con Python y scikit-learn

## Mantente conectado

- Participá en el **foro del curso** para seguir aprendiendo con la comunidad
- Seguinos para novedades de nuevos cursos y talleres en vivo

> Gracias por confiar en ALIAA. El futuro de la IA aplicada en Latinoamérica se construye profesional por profesional — y vos ya diste un paso importante.

**— El equipo de ALIAA**`,
      },
    ],
  },
];

async function main() {
  console.log("📚 Creando curso de Machine Learning...\n");

  const existing = await api(
    `/rest/v1/courses?slug=eq.${COURSE.slug}&select=id`
  );
  if (existing.data?.length) {
    await api(`/rest/v1/courses?id=eq.${existing.data[0].id}`, {
      method: "DELETE",
      prefer: "return=minimal",
    });
    console.log("🗑️  Curso anterior eliminado");
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

  console.log(`\n🎉 Curso listo!`);
  console.log(`   Precio:    ${COURSE.precio} ${COURSE.moneda}`);
  console.log(`   Duración:  ~${COURSE.duracion_horas} horas`);
  console.log(`   Catálogo:  http://localhost:3000/cursos/${COURSE.slug}`);
  console.log(`   Admin:     http://localhost:3000/admin/cursos/${courseId}`);
  console.log(`   Estudiar:  http://localhost:3000/dashboard/cursos/${courseId}`);
}

main().catch((e) => {
  console.error("❌", e.message);
  process.exit(1);
});
