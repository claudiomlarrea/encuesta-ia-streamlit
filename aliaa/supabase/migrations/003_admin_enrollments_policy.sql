-- Admin puede ver todas las inscripciones (para panel de métricas)
CREATE POLICY "Admin ve todas las inscripciones" ON enrollments
  FOR SELECT TO authenticated USING (
    auth.uid() IN (SELECT id FROM profiles WHERE rol = 'admin')
  );
