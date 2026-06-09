-- Los alumnos inscriptos deben poder ver quizzes y preguntas

CREATE POLICY "Quizzes visibles para autenticados" ON quizzes
  FOR SELECT TO authenticated USING (true);

CREATE POLICY "Preguntas de quiz visibles" ON quiz_questions
  FOR SELECT TO authenticated USING (true);

CREATE POLICY "Usuarios registran intentos de quiz" ON quiz_attempts
  FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Usuarios ven sus intentos" ON quiz_attempts
  FOR SELECT TO authenticated USING (auth.uid() = user_id);
