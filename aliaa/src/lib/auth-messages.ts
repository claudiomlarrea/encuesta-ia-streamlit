export function magicLinkErrorMessage(message: string): string {
  const lower = message.toLowerCase();

  if (
    lower.includes("rate") ||
    lower.includes("security purposes") ||
    lower.includes("only request")
  ) {
    return "Enviamos demasiados enlaces en poco tiempo. Esperá 1 minuto y volvé a intentar.";
  }

  if (lower.includes("email address") && lower.includes("invalid")) {
    return "El correo no es válido. Revisá que esté bien escrito.";
  }

  return "No pudimos enviar el enlace. Verificá el correo e intentá de nuevo.";
}
