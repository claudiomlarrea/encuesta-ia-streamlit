export function looksLikeEmailUsername(
  name: string | null | undefined,
  email: string | null | undefined
): boolean {
  if (!name?.trim()) return true;
  if (!email) return false;
  const prefix = email.split("@")[0]?.toLowerCase();
  return name.trim().toLowerCase() === prefix;
}

export function profileNameForForm(profile: {
  nombre_completo?: string | null;
  email?: string | null;
}): string {
  const name = profile.nombre_completo?.trim();
  if (name && !looksLikeEmailUsername(name, profile.email)) {
    return name;
  }
  return "";
}

export function getStudentDisplayName(profile: {
  nombre_completo?: string | null;
  email?: string | null;
}): string {
  const name = profile.nombre_completo?.trim();
  if (name && !looksLikeEmailUsername(name, profile.email)) {
    return name;
  }
  return "Estudiante ALIAA";
}

/** Nombre impreso en el certificado: prioriza el de la inscripción/curso */
export function getCertificateStudentName(options: {
  nombreEstudiante?: string | null;
  nombreCertificado?: string | null;
  profile?: { nombre_completo?: string | null; email?: string | null } | null;
}): string {
  const fromCert = options.nombreEstudiante?.trim();
  if (fromCert) return fromCert;

  const fromEnrollment = options.nombreCertificado?.trim();
  if (fromEnrollment) return fromEnrollment;

  if (options.profile) {
    return getStudentDisplayName(options.profile);
  }

  return "Estudiante ALIAA";
}
