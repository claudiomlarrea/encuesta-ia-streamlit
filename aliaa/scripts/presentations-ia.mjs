export function presentation(slides) {
  return JSON.stringify({ format: "presentation", slides });
}

export const PRESENTATIONS = {
  queEsIA: presentation([
    {
      title: "¿Qué es la Inteligencia Artificial?",
      highlight: "Sistemas que realizan tareas que requieren inteligencia humana",
      bullets: [
        "Reconocer patrones, decidir y generar contenido",
        "No es magia: es software entrenado con datos",
        "Incluye chatbots, visión, voz y recomendaciones",
      ],
      narration:
        "La Inteligencia Artificial es la disciplina que busca que las máquinas realicen tareas que normalmente requieren inteligencia humana. Reconocer imágenes, entender texto, tomar decisiones o generar respuestas. No es magia. Es software que aprende patrones a partir de datos y experiencia.",
    },
    {
      title: "IA tradicional vs IA generativa",
      bullets: [
        "Tradicional: clasifica, predice o detecta",
        "Generativa: crea texto, imágenes o código",
        "Hoy conviven ambas en productos reales",
      ],
      narration:
        "La IA tradicional suele clasificar o predecir. Por ejemplo, detectar spam, o estimar una venta. La IA generativa crea contenido nuevo: un email, una imagen, un resumen. Hoy, muchos productos combinan las dos. Un asistente que entiende tu pregunta, y además redacta la respuesta.",
    },
    {
      title: "IA en tu día a día",
      bullets: [
        "Filtros de correo y traducción automática",
        "Recomendaciones en streaming y e-commerce",
        "Asistentes con lenguaje natural",
      ],
      narration:
        "Ya usás IA sin darte cuenta. El correo filtra spam. El traductor sugiere frases. Netflix recomienda series. Y los asistentes de chat responden en lenguaje natural. Entender qué es la IA te ayuda a usarla mejor, y a evaluar cuándo conviene confiar en una respuesta.",
    },
  ]),

  queEsToken: presentation([
    {
      title: "¿Qué es un token?",
      highlight: "La unidad básica con la que los modelos leen y escriben texto",
      bullets: [
        "No siempre es una palabra completa",
        "Puede ser sílabas, prefijos o signos",
        "El modelo procesa texto token por token",
      ],
      narration:
        "Un token es la unidad mínima en la que un modelo de lenguaje divide el texto. No siempre coincide con una palabra. A veces es una sílaba, un prefijo, o un signo de puntuación. El modelo no lee párrafos enteros de una vez. Procesa secuencias de tokens, de izquierda a derecha.",
    },
    {
      title: "Ejemplos de tokens",
      bullets: [
        '"Inteligencia" puede ser 1 token o varios',
        "Los espacios y emojis también cuentan",
        "En español, ~1 token cada 3 o 4 caracteres",
      ],
      narration:
        'La frase "Inteligencia Artificial" puede dividirse en dos, tres o más tokens, según el modelo. Los espacios, números y emojis también consumen tokens. Como regla práctica en español, contá aproximadamente un token cada tres o cuatro caracteres. No hace falta ser exacto. Es una estimación útil.',
    },
    {
      title: "Por qué importan los tokens",
      bullets: [
        "Definen cuánto texto entra en cada consulta",
        "Impactan el costo en APIs de IA",
        "Límites de contexto = límite de tokens",
      ],
      narration:
        "Los tokens importan por tres razones. Primero, definen cuánto texto podés enviar en una sola consulta. Segundo, muchas APIs cobran por token procesado. Tercero, cada modelo tiene un límite de contexto, medido en tokens. Si tu documento es muy largo, hay que resumirlo, dividirlo, o elegir un modelo con ventana más amplia.",
    },
  ]),

  queEsPrompt: presentation([
    {
      title: "¿Qué es un prompt?",
      highlight: "La instrucción que le das a un modelo de IA",
      bullets: [
        "Es el texto que enviás al asistente",
        "Define qué querés que haga o responda",
        "Cuanto más claro, mejor el resultado",
      ],
      narration:
        "Un prompt es la instrucción o pregunta que le escribís a un modelo de inteligencia artificial. Cuando abrís ChatGPT, Copilot o un chatbot, lo que tipeás es tu prompt. No es un comando técnico secreto. Es lenguaje natural, con un objetivo claro: que la IA genere una respuesta útil para vos.",
    },
    {
      title: "Anatomía de un buen prompt",
      bullets: [
        "Contexto: quién sos y para qué necesitás la respuesta",
        "Tarea: qué debe hacer el modelo, paso a paso",
        "Formato: lista, tabla, tono formal, máximo de palabras",
      ],
      narration:
        "Un buen prompt suele tener tres partes. Contexto: explicá la situación. Por ejemplo, soy docente y preparo una clase introductoria. Tarea: pedí algo concreto. Resume este texto en cinco puntos. Formato: indicá cómo querés la salida. Usá viñetas, máximo cien palabras, tono cercano. Esa estructura reduce respuestas vagas o genéricas.",
    },
    {
      title: "Errores comunes y cómo mejorar",
      bullets: [
        "Evitá pedidos demasiado amplios o ambiguos",
        "Iterá: refiná el prompt con la respuesta anterior",
        "Probar variantes cuesta poco y mejora mucho",
      ],
      narration:
        "El error más frecuente es pedir demasiado en una sola frase. En lugar de ayudame con mi trabajo, probá: redactá un email de seguimiento a un cliente que no respondió en diez días, tono profesional y breve. Si la respuesta no convence, refiná el prompt. La IA no lee la mente. Cuanto más preciso seas, más útil será el resultado.",
    },
  ]),
};
