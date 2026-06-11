export type UserRole = "admin" | "docente" | "alumno";
export type LessonType = "video" | "pdf" | "texto" | "actividad" | "evaluacion";
export type PaymentProvider = "mercadopago" | "paypal";
export type PaymentStatus = "pendiente" | "completado" | "fallido" | "reembolsado";
export type CourseLevel = "principiante" | "intermedio" | "avanzado";

export interface Profile {
  id: string;
  email: string;
  nombre_completo: string | null;
  avatar_url: string | null;
  rol: UserRole;
  bio: string | null;
  pais: string | null;
  telefono: string | null;
  created_at: string;
  updated_at: string;
}

export interface Course {
  id: string;
  titulo: string;
  slug: string;
  descripcion: string | null;
  descripcion_corta: string | null;
  imagen_url: string | null;
  instructor_id: string | null;
  precio: number;
  moneda: string;
  publicado: boolean;
  gratuito: boolean;
  duracion_horas: number | null;
  nivel: CourseLevel | null;
  categoria: string | null;
  created_at: string;
  updated_at: string;
  instructor?: Profile;
}

export interface Module {
  id: string;
  course_id: string;
  titulo: string;
  descripcion: string | null;
  orden: number;
  lessons?: Lesson[];
}

export interface Lesson {
  id: string;
  module_id: string;
  titulo: string;
  descripcion: string | null;
  tipo: LessonType;
  contenido_url: string | null;
  contenido_texto: string | null;
  duracion_minutos: number | null;
  orden: number;
  vista_previa: boolean;
}

export interface Enrollment {
  id: string;
  user_id: string;
  course_id: string;
  inscrito_en: string;
  completado_en: string | null;
  progreso_porcentaje: number;
  nombre_certificado: string | null;
  course?: Course;
}

export interface Certificate {
  id: string;
  user_id: string;
  course_id: string;
  codigo_verificacion: string;
  emitido_en: string;
  nombre_estudiante: string | null;
  course?: Course;
  profile?: Profile;
}

export interface ForumTopic {
  id: string;
  course_id: string;
  user_id: string;
  titulo: string;
  contenido: string;
  fijado: boolean;
  created_at: string;
  profile?: Profile;
  replies_count?: number;
}

export interface ForumReply {
  id: string;
  topic_id: string;
  user_id: string;
  contenido: string;
  created_at: string;
  profile?: Profile;
}

export interface Payment {
  id: string;
  user_id: string;
  course_id: string;
  monto: number;
  moneda: string;
  proveedor: PaymentProvider;
  proveedor_pago_id: string | null;
  estado: PaymentStatus;
  created_at: string;
  course?: Course;
}

export interface Quiz {
  id: string;
  lesson_id: string;
  titulo: string;
  puntaje_aprobacion: number;
}

export interface CourseRating {
  id: string;
  user_id: string;
  course_id: string;
  estrellas: number;
  comentario: string | null;
  created_at: string;
  updated_at: string;
}

export interface QuizQuestion {
  id: string;
  quiz_id: string;
  pregunta: string;
  opciones: string[];
  respuesta_correcta: number;
  orden: number;
}
