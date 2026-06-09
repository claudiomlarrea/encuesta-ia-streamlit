import { readFileSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const envPath = resolve(__dirname, "../.env.local");

function loadEnv() {
  const env = {};
  for (const line of readFileSync(envPath, "utf8").split("\n")) {
    const t = line.trim();
    if (!t || t.startsWith("#")) continue;
    const i = t.indexOf("=");
    if (i > 0) env[t.slice(0, i)] = t.slice(i + 1);
  }
  return env;
}

const env = loadEnv();
const PROJECT_REF = env.NEXT_PUBLIC_SUPABASE_URL?.match(
  /https:\/\/([^.]+)\.supabase\.co/
)?.[1];
const ACCESS_TOKEN = env.SUPABASE_ACCESS_TOKEN;
const sql = readFileSync(
  resolve(__dirname, "../supabase/migrations/005_quiz_policies.sql"),
  "utf8"
);

async function main() {
  if (!ACCESS_TOKEN || !PROJECT_REF) {
    console.log("ℹ️  Sin SUPABASE_ACCESS_TOKEN en .env.local.");
    console.log("   Ejecutá este SQL manualmente en Supabase → SQL Editor:\n");
    console.log(sql);
    console.log(
      "\n   O agregá SUPABASE_ACCESS_TOKEN (Personal Access Token de supabase.com/dashboard/account/tokens)"
    );
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
    console.error("❌ Error aplicando políticas:", body);
    process.exit(1);
  }

  console.log("✅ Políticas de quiz aplicadas en Supabase");
}

main().catch((e) => {
  console.error("❌", e.message);
  process.exit(1);
});
