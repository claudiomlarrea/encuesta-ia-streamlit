/** Correos oficiales de ALIAA — usados en scripts y seeds */
export const OWNER_EMAIL = "claudio17larrea@gmail.com";
export const OWNER_NAME = "Claudio Larrea";
export const CONTACT_EMAIL = "contacto.aliaa@gmail.com";
export const LEGACY_ADMIN_EMAILS = ["investigacion@uccuyo.edu.ar"];

export function findAdminUser(users) {
  const emails = [OWNER_EMAIL, ...LEGACY_ADMIN_EMAILS];
  return users.find((u) => emails.includes(u.email)) ?? null;
}
