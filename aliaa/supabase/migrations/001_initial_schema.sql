-- ALIAA - Academia Latinoamericana de Inteligencia Artificial Aplicada
-- Esquema inicial de base de datos

CREATE TYPE user_role AS ENUM ('admin', 'docente', 'alumno');
CREATE TYPE lesson_type AS ENUM ('video', 'pdf', 'texto', 'actividad', 'evaluacion');
CREATE TYPE payment_provider AS ENUM ('mercadopago', 'paypal');
CREATE TYPE payment_status AS ENUM ('pendiente', 'completado', 'fallido', 'reembolsado');
CREATE TYPE course_level AS ENUM ('principiante', 'intermedio', 'avanzado');

-- Perfiles de usuario (extiende auth.users)
CREATE TABLE profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT NOT NULL,
  nombre_completo TEXT,
  avatar_url TEXT,
  rol user_role NOT NULL DEFAULT 'alumno',
  bio TEXT,
  pais TEXT,
  telefono TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Cursos
CREATE TABLE courses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  titulo TEXT NOT NULL,
  slug TEXT UNIQUE NOT NULL,
  descripcion TEXT,
  descripcion_corta TEXT,
  imagen_url TEXT,
  instructor_id UUID REFERENCES profiles(id) ON DELETE SET NULL,
  precio DECIMAL(10,2) NOT NULL DEFAULT 0,
  moneda TEXT NOT NULL DEFAULT 'USD',
  publicado BOOLEAN NOT NULL DEFAULT false,
  gratuito BOOLEAN NOT NULL DEFAULT false,
  duracion_horas INTEGER,
  nivel course_level DEFAULT 'principiante',
  categoria TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Módulos de curso
CREATE TABLE modules (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
  titulo TEXT NOT NULL,
  descripcion TEXT,
  orden INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Lecciones
CREATE TABLE lessons (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  module_id UUID NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
  titulo TEXT NOT NULL,
  descripcion TEXT,
  tipo lesson_type NOT NULL DEFAULT 'video',
  contenido_url TEXT,
  contenido_texto TEXT,
  duracion_minutos INTEGER,
  orden INTEGER NOT NULL DEFAULT 0,
  vista_previa BOOLEAN NOT NULL DEFAULT false,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Inscripciones
CREATE TABLE enrollments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
  inscrito_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  completado_en TIMESTAMPTZ,
  progreso_porcentaje DECIMAL(5,2) NOT NULL DEFAULT 0,
  UNIQUE(user_id, course_id)
);

-- Progreso por lección
CREATE TABLE lesson_progress (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  lesson_id UUID NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
  completado BOOLEAN NOT NULL DEFAULT false,
  completado_en TIMESTAMPTZ,
  UNIQUE(user_id, lesson_id)
);

-- Evaluaciones
CREATE TABLE quizzes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  lesson_id UUID NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
  titulo TEXT NOT NULL,
  puntaje_aprobacion INTEGER NOT NULL DEFAULT 70,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE quiz_questions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  quiz_id UUID NOT NULL REFERENCES quizzes(id) ON DELETE CASCADE,
  pregunta TEXT NOT NULL,
  opciones JSONB NOT NULL,
  respuesta_correcta INTEGER NOT NULL,
  orden INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE quiz_attempts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  quiz_id UUID NOT NULL REFERENCES quizzes(id) ON DELETE CASCADE,
  puntaje INTEGER,
  aprobado BOOLEAN,
  respuestas JSONB,
  intentado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Certificados
CREATE TABLE certificates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
  codigo_verificacion TEXT UNIQUE NOT NULL,
  emitido_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(user_id, course_id)
);

-- Foros de discusión
CREATE TABLE forum_topics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  titulo TEXT NOT NULL,
  contenido TEXT NOT NULL,
  fijado BOOLEAN NOT NULL DEFAULT false,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE forum_replies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  topic_id UUID NOT NULL REFERENCES forum_topics(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  contenido TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Pagos
CREATE TABLE payments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
  monto DECIMAL(10,2) NOT NULL,
  moneda TEXT NOT NULL DEFAULT 'USD',
  proveedor payment_provider NOT NULL,
  proveedor_pago_id TEXT,
  estado payment_status NOT NULL DEFAULT 'pendiente',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índices para escalabilidad
CREATE INDEX idx_courses_slug ON courses(slug);
CREATE INDEX idx_courses_publicado ON courses(publicado);
CREATE INDEX idx_enrollments_user ON enrollments(user_id);
CREATE INDEX idx_enrollments_course ON enrollments(course_id);
CREATE INDEX idx_lesson_progress_user ON lesson_progress(user_id);
CREATE INDEX idx_forum_topics_course ON forum_topics(course_id);
CREATE INDEX idx_certificates_codigo ON certificates(codigo_verificacion);
CREATE INDEX idx_payments_user ON payments(user_id);
CREATE INDEX idx_profiles_rol ON profiles(rol);

-- Trigger: crear perfil al registrarse
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  INSERT INTO public.profiles (id, email, nombre_completo, rol, pais)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'nombre_completo', split_part(NEW.email, '@', 1)),
    'alumno'::user_role,
    NEW.raw_user_meta_data->>'pais'
  );
  RETURN NEW;
EXCEPTION
  WHEN unique_violation THEN
    RETURN NEW;
END;
$$;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION handle_new_user();

-- Trigger: actualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER profiles_updated_at BEFORE UPDATE ON profiles
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER courses_updated_at BEFORE UPDATE ON courses
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER forum_topics_updated_at BEFORE UPDATE ON forum_topics
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- RLS
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE courses ENABLE ROW LEVEL SECURITY;
ALTER TABLE modules ENABLE ROW LEVEL SECURITY;
ALTER TABLE lessons ENABLE ROW LEVEL SECURITY;
ALTER TABLE enrollments ENABLE ROW LEVEL SECURITY;
ALTER TABLE lesson_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE quizzes ENABLE ROW LEVEL SECURITY;
ALTER TABLE quiz_questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE quiz_attempts ENABLE ROW LEVEL SECURITY;
ALTER TABLE certificates ENABLE ROW LEVEL SECURITY;
ALTER TABLE forum_topics ENABLE ROW LEVEL SECURITY;
ALTER TABLE forum_replies ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;

-- Políticas: perfiles
CREATE POLICY "Perfiles visibles para autenticados" ON profiles
  FOR SELECT TO authenticated USING (true);
CREATE POLICY "Sistema crea perfiles al registrarse" ON profiles
  FOR INSERT TO authenticated WITH CHECK (auth.uid() = id);
CREATE POLICY "Usuarios actualizan su perfil" ON profiles
  FOR UPDATE TO authenticated USING (auth.uid() = id);

-- Políticas: cursos publicados visibles para todos
CREATE POLICY "Cursos publicados visibles" ON courses
  FOR SELECT USING (publicado = true OR auth.uid() IN (
    SELECT id FROM profiles WHERE rol IN ('admin', 'docente')
  ));
CREATE POLICY "Admin y docentes gestionan cursos" ON courses
  FOR ALL TO authenticated USING (
    auth.uid() IN (SELECT id FROM profiles WHERE rol IN ('admin', 'docente'))
  );

-- Políticas: módulos y lecciones
CREATE POLICY "Módulos visibles con curso" ON modules
  FOR SELECT USING (true);
CREATE POLICY "Lecciones visibles" ON lessons
  FOR SELECT USING (true);

-- Políticas: inscripciones
CREATE POLICY "Usuarios ven sus inscripciones" ON enrollments
  FOR SELECT TO authenticated USING (auth.uid() = user_id);
CREATE POLICY "Usuarios se inscriben" ON enrollments
  FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);

-- Políticas: progreso
CREATE POLICY "Usuarios gestionan su progreso" ON lesson_progress
  FOR ALL TO authenticated USING (auth.uid() = user_id);

-- Políticas: certificados
CREATE POLICY "Certificados visibles para dueño" ON certificates
  FOR SELECT TO authenticated USING (auth.uid() = user_id);
CREATE POLICY "Certificados verificables públicamente" ON certificates
  FOR SELECT USING (true);

-- Políticas: foros
CREATE POLICY "Foros visibles para inscritos" ON forum_topics
  FOR SELECT TO authenticated USING (true);
CREATE POLICY "Usuarios crean temas" ON forum_topics
  FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Respuestas visibles" ON forum_replies
  FOR SELECT TO authenticated USING (true);
CREATE POLICY "Usuarios responden" ON forum_replies
  FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);

-- Políticas: pagos
CREATE POLICY "Usuarios ven sus pagos" ON payments
  FOR SELECT TO authenticated USING (auth.uid() = user_id);
