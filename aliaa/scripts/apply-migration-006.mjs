import { readFileSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const env = Object.fromEntries(
  readFileSync(resolve(__dirname, "../.env.local"), "utf8")
    .split("\n")
    .filter((l) => l && !l.startsWith("#"))
    .map((l) => {
      const i = l.indexOf("=");
      return [l.slice(0, i), l.slice(i + 1)];
    })
);

const ACCESS_TOKEN = env.SUPABASE_ACCESS_TOKEN;
const PROJECT_REF = env.NEXT_PUBLIC_SUPABASE_URL?.match(
  /https:\/\/([^.]+)\.supabase\.co/
)?.[1];
const sql = readFileSync(
  resolve(__dirname, "../supabase/migrations/006_certificate_student_name.sql"),
  "utf8"
);

async function main() {
  if (!ACCESS_TOKEN || !PROJECT_REF) {
    console.log("Sin SUPABASE_ACCESS_TOKEN. Ejecutá en SQL Editor:\n");
    console.log(sql);
    process.exit(0);
  }

  const res = await fetch(
    `https://api.supabase.com/v1/projects/${PROJECT_REF}/database/query`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${ACCESS_TOKEN}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query: sql }),
    }
  );
  const body = await res.text();
  if (!res.ok) {
    console.error("❌", body);
    process.exit(1);
  }
  console.log("✅ Migración 006 aplicada");
}

main();
