export const SITE_NAME = "ALIAA";
export const SITE_FULL_NAME =
  "Academia Latinoamericana de Inteligencia Artificial Aplicada";
export const SITE_DESCRIPTION =
  "Formación profesional en inteligencia artificial aplicada para América Latina. Cursos asincrónicos, certificados verificables y comunidad de aprendizaje.";

/** Correo público de ALIAA (footer, certificados, etc.) */
export const CONTACT_EMAIL = "contacto.aliaa@gmail.com";
/** Cuenta personal del responsable / admin principal */
export const OWNER_EMAIL = "claudio17larrea@gmail.com";

export const ROLE_LABELS: Record<string, string> = {
  admin: "Administrador",
  docente: "Docente",
  alumno: "Alumno",
};

export const LEVEL_LABELS: Record<string, string> = {
  principiante: "Principiante",
  intermedio: "Intermedio",
  avanzado: "Avanzado",
};

export const LESSON_TYPE_LABELS: Record<string, string> = {
  video: "Lección audiovisual",
  pdf: "Documento PDF",
  texto: "Lectura",
  actividad: "Actividad",
  evaluacion: "Evaluación",
};

export const NAV_LINKS = [
  { href: "/cursos", label: "Cursos" },
  { href: "/nosotros", label: "Nosotros" },
  { href: "/certificados/verificar", label: "Verificar Certificado" },
];

export const COURSE_CATEGORIES = [
  "Machine Learning",
  "Deep Learning",
  "NLP",
  "Visión por Computadora",
  "IA Generativa",
  "MLOps",
  "Ética en IA",
  "IA para Negocios",
];
