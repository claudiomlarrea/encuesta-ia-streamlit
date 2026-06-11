export function presentation(slides) {
  return JSON.stringify({ format: "presentation", slides });
}

export const PRESENTATIONS = {
  iaEnMineria: presentation([
    {
      title: "La IA en operaciones mineras",
      highlight: "Asistente para informes y comunicación — no reemplaza ingeniería ni seguridad crítica",
      bullets: [
        "Partes de turno, novedades de faena y seguimiento operativo",
        "Resúmenes de informes de producción y mantenimiento",
        "Borradores para seguridad, ambiente y relación con comunidades",
      ],
      narration:
        "En minería, la inteligencia artificial puede ayudar a equipos de faena, planta, seguridad e higiene, medio ambiente y administración de operaciones. Redactar partes de turno, ordenar notas de inspección, resumir informes extensos o preparar comunicaciones internas. No reemplaza el criterio del supervisor, el ingeniero de minas ni el responsable de seguridad. Es un asistente que acelera el borrador para que un profesional revise y apruebe.",
    },
    {
      title: "Qué sí y qué no delegar en faena",
      bullets: [
        "Sí: borradores, resúmenes, tablas, checklists, mails internos",
        "No: decisiones de detención de faena por riesgo crítico",
        "No: datos de ubicación de personal ni información reservada",
      ],
      narration:
        "Usá la IA para tareas de formato y redacción. Pedile un borrador de parte de turno, una tabla de demoras o un recordatorio de uso de EPP. No uses la IA como única base para decidir detener una operación, modificar un procedimiento de seguridad o interpretar una norma ambiental. Y nunca pegues en herramientas públicas datos sensibles: ubicación exacta de personal, reservas, contratos, salarios o información de comunidades en conflicto.",
    },
    {
      title: "Herramientas y políticas del sitio",
      bullets: [
        "ChatGPT, Copilot, Gemini u otras según política de la empresa",
        "Consultá con TI y seguridad de la información de tu operación",
        "Preferí versiones empresariales cuando manejes datos internos",
      ],
      narration:
        "Muchas mineras ya evalúan asistentes de IA con políticas claras de uso. Antes de pegar procedimientos internos o informes de producción, consultá con sistemas o con tu jefe de área. Si tu empresa ofrece Copilot o una IA corporativa, usala para mayor control de datos. Este curso te enseña buenas prácticas; la política formal la define tu empleador.",
    },
  ]),

  informesComunicacion: presentation([
    {
      title: "Partes de turno y novedades de faena",
      highlight: "De notas sueltas a informe claro en minutos",
      bullets: [
        "Producción, demoras, equipos detenidos y acciones pendientes",
        "Formato tabla o viñetas para el relevo de turno",
        "Revisar cifras y horarios antes de enviar",
      ],
      narration:
        "Al cierre de turno, muchas veces quedan apuntes dispersos. Pegá tus notas y pedí: convertí esto en parte de turno con secciones producción, demoras, equipos detenidos y pendientes para el próximo turno. Formato tabla. La IA ordena la información. Tu responsabilidad es verificar toneladas, horas, códigos de equipo y nombres de sectores. Un error en el parte puede afectar la planificación del turno siguiente.",
    },
    {
      title: "Comunicación interna y con contratistas",
      bullets: [
        "Mails sobre demoras, mantenimiento programado o cambios de procedimiento",
        "Recordatorios de cumplimiento de EPP y procedimientos",
        "Tono claro, directo y respetuoso",
      ],
      narration:
        "Ejemplo: redactá un mail al contratista de mantenimiento recordando la entrega del plan de trabajo para la parada de planta, plazo vencido en tres días, tono profesional y breve. O: prepará un aviso interno sobre cambio de horario de ingreso por condiciones climáticas, audiencia supervisores de faena. Indicá siempre contexto, tarea y formato en el prompt.",
    },
    {
      title: "Actas de comité de seguridad",
      bullets: [
        "Asistentes, temas, acuerdos, responsables y plazos",
        "Estructura formal a partir de notas de reunión",
        "Verificar que los compromisos reflejen lo acordado",
      ],
      narration:
        "Después de un comité de seguridad, pegá las notas y pedí acta formal con fecha, asistentes, temas tratados, acuerdos y responsable de cada acción. La IA estructura el documento. Revisá que cada compromiso coincida con lo discutido. En minería, un acta mal redactada puede generar confusiones en seguimiento de incidentes o capacitaciones pendientes.",
    },
  ]),

  datosOperativos: presentation([
    {
      title: "Resumir informes de producción y mantenimiento",
      highlight: "Diez páginas a cinco puntos para gerencia o jefatura",
      bullets: [
        "Enfoque en desvíos, causas y acciones correctivas",
        "Indicar audiencia: operaciones, mantenimiento, dirección",
        "No sustituye el análisis técnico del especialista",
      ],
      narration:
        "Pedí: resumí este informe semanal de producción en cinco viñetas para el gerente de operaciones. Enfocate en desvíos respecto al plan, causas principales y acciones en curso. Máximo veinte palabras por punto. Para mantenimiento: resumí las fallas recurrentes de correas en el último mes y proponé tabla con equipo, falla, frecuencia y prioridad sugerida. La IA ayuda a sintetizar; el análisis de causa raíz sigue siendo trabajo humano.",
    },
    {
      title: "Tablas de incidentes y seguimiento",
      bullets: [
        "Fecha, sector, tipo, estado y responsable",
        "Cronogramas de acciones correctivas",
        "Priorización visual para reuniones de seguridad",
      ],
      narration:
        "Cuando tenés texto narrativo sobre incidentes o near-miss, pedí formato tabla. Columnas sugeridas: fecha, sector, clasificación, descripción breve, estado, responsable y fecha límite. Eso facilita el seguimiento en reuniones de seguridad y la presentación a auditorías internas. Siempre contrastá con el registro oficial del sistema de gestión de la empresa.",
    },
    {
      title: "Checklists de inspección",
      bullets: [
        "Inspecciones de equipos, áreas y procedimientos",
        "Listas a partir de normas o procedimientos internos",
        "Revisar ítems críticos con el procedimiento vigente",
      ],
      narration:
        "Pedí: a partir de este procedimiento de inspección de chancado, armá una checklist semanal con ítems verificables, formato sí o no y espacio para observaciones. La IA acelera la estructura. El especialista de seguridad o mantenimiento debe validar que no falte ningún punto crítico del procedimiento oficial. Una checklist incompleta es un riesgo.",
    },
  ]),

  seguridadAmbiente: presentation([
    {
      title: "Seguridad, ambiente y comunidades",
      bullets: [
        "Recordatorios de EPP y procedimientos sin tono agresivo",
        "Resúmenes de informes ambientales para gerencia",
        "Borradores de respuesta a consultas vecinales",
      ],
      narration:
        "En seguridad: redactá un recordatorio sobre uso obligatorio de arnés en zona de trabajo en altura, tono firme y respetuoso, máximo cien palabras. En ambiente: resumí este informe de monitoreo en puntos clave, desvíos y plazos de corrección. En relación con comunidades: borrador de respuesta institucional a consulta sobre polvo y horarios, sin comprometer datos operativos sensibles. Siempre revisión de área legal o de comunidades antes de enviar.",
    },
    {
      title: "Confidencialidad en operaciones mineras",
      bullets: [
        "No pegar reservas, contratos, planos reservados ni datos de personal",
        "Anonimizar sectores y personas en ejemplos",
        "Usar herramientas aprobadas por la empresa",
      ],
      narration:
        "La minería maneja información estratégica y sensible. Antes de usar un asistente, preguntate si el contenido podría publicarse sin daño a la operación o a las personas. Anonimizá: Sector A en lugar del nombre real del frente, Operador uno en lugar del nombre. Muchas operaciones prohíben herramientas públicas para documentos internos. Respetá esa política; este curso no la reemplaza.",
    },
    {
      title: "Flujo recomendado en minería",
      bullets: [
        "1. Borrador con IA · 2. Revisión del supervisor o especialista · 3. Registro oficial",
        "Guardá prompts útiles por área: turno, SSO, ambiente",
        "Complementá con Cómo redactar prompts en ALIAA",
      ],
      narration:
        "Adoptá un flujo disciplinado. La IA genera el borrador. Un supervisor, técnico de seguridad o ingeniero revisa datos, riesgos y cumplimiento. Recién ahí se publica en el canal oficial o se carga al sistema de gestión. Compartí con tu equipo los prompts que funcionen para partes de turno, actas y resúmenes. En ALIAA podés profundizar con el curso de redacción de prompts. La productividad con IA en minería se construye con práctica y cultura de seguridad.",
    },
  ]),
};
