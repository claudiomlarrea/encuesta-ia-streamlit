-- Nombre para certificado: se guarda al inscribirse en cada curso
ALTER TABLE enrollments
  ADD COLUMN IF NOT EXISTS nombre_certificado TEXT;

ALTER TABLE certificates
  ADD COLUMN IF NOT EXISTS nombre_estudiante TEXT;

CREATE POLICY "Usuarios actualizan sus inscripciones" ON enrollments
  FOR UPDATE TO authenticated
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Usuarios generan su certificado" ON certificates
  FOR INSERT TO authenticated
  WITH CHECK (auth.uid() = user_id);
