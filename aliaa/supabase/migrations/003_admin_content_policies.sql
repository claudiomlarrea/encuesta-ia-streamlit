-- Permisos para que admin/docente gestionen módulos y lecciones

CREATE POLICY "Admin gestiona módulos" ON modules
  FOR ALL TO authenticated
  USING (auth.uid() IN (SELECT id FROM profiles WHERE rol IN ('admin', 'docente')))
  WITH CHECK (auth.uid() IN (SELECT id FROM profiles WHERE rol IN ('admin', 'docente')));

CREATE POLICY "Admin gestiona lecciones" ON lessons
  FOR ALL TO authenticated
  USING (auth.uid() IN (SELECT id FROM profiles WHERE rol IN ('admin', 'docente')))
  WITH CHECK (auth.uid() IN (SELECT id FROM profiles WHERE rol IN ('admin', 'docente')));
