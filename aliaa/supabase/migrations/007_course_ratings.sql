-- Valoraciones de cursos (1-5 estrellas) por alumnos que completaron el curso
CREATE TABLE course_ratings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
  estrellas INTEGER NOT NULL CHECK (estrellas >= 1 AND estrellas <= 5),
  comentario TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(user_id, course_id)
);

CREATE INDEX idx_course_ratings_course ON course_ratings(course_id);
CREATE INDEX idx_course_ratings_user ON course_ratings(user_id);

ALTER TABLE course_ratings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Valoraciones visibles públicamente" ON course_ratings
  FOR SELECT USING (true);

CREATE POLICY "Alumnos crean su valoración" ON course_ratings
  FOR INSERT TO authenticated
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Alumnos actualizan su valoración" ON course_ratings
  FOR UPDATE TO authenticated
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Admin gestiona valoraciones" ON course_ratings
  FOR ALL TO authenticated USING (
    auth.uid() IN (SELECT id FROM profiles WHERE rol = 'admin')
  );
