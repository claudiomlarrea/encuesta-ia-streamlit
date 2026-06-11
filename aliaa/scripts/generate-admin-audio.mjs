import { mkdirSync, existsSync, writeFileSync, rmSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";
import { execSync } from "child_process";
import { PRESENTATIONS } from "./presentations-admin.mjs";

const __dirname = dirname(fileURLToPath(import.meta.url));
const AUDIO_DIR = resolve(__dirname, "../public/audio/admin");
const VOICE = "Eddy (Spanish (Mexico))";
const RATE = 135;
const FORCE = process.argv.includes("--force");

const LESSON_KEYS = {
  iaEnAdministracion: "ia-en-administracion",
  documentosAdministrativos: "documentos-administrativos",
  organizarInformacion: "organizar-informacion",
  buenasPracticas: "buenas-practicas",
};

function prepareForSpeech(text) {
  return text
    .replace(/\.\.\./g, "[[slnc 700]]")
    .replace(/\.\s+/g, ". [[slnc 550]] ")
    .replace(/;\s+/g, "; [[slnc 400]] ")
    .replace(/,\s+/g, ", [[slnc 280]] ")
    .replace(/:\s+/g, ": [[slnc 220]] ")
    .replace(/\?\s+/g, "? [[slnc 500]] ")
    .replace(/!\s+/g, "! [[slnc 500]] ");
}

function generateAudio(text, outputPath) {
  const prepared = prepareForSpeech(text);
  const aiff = outputPath.replace(".m4a", ".aiff");
  const escaped = prepared.replace(/"/g, '\\"').replace(/\n/g, " ");
  execSync(`say -v "${VOICE}" -r ${RATE} -o "${aiff}" "${escaped}"`);
  execSync(`afconvert -f m4af -d aac "${aiff}" "${outputPath}"`);
  execSync(`rm -f "${aiff}"`);
}

if (FORCE && existsSync(AUDIO_DIR)) {
  rmSync(AUDIO_DIR, { recursive: true, force: true });
}

mkdirSync(AUDIO_DIR, { recursive: true });

const manifest = {};

for (const [key, json] of Object.entries(PRESENTATIONS)) {
  const lessonSlug = LESSON_KEYS[key];
  const data = JSON.parse(json);
  manifest[key] = { format: "presentation", slides: [] };
  console.log(`🎙️  ${lessonSlug}`);

  data.slides.forEach((slide, i) => {
    const filename = `${lessonSlug}-${i}.m4a`;
    const filepath = resolve(AUDIO_DIR, filename);
    const audioUrl = `/audio/admin/${filename}`;
    if (FORCE || !existsSync(filepath)) {
      console.log(`   Slide ${i + 1}/${data.slides.length}...`);
      generateAudio(slide.narration, filepath);
    } else {
      console.log(`   Slide ${i + 1} (ya existe, omitido)`);
    }
    manifest[key].slides.push({ ...slide, audio: audioUrl });
  });
}

let moduleContent = `export function presentation(slides) {
  return JSON.stringify({ format: "presentation", slides });
}

export const PRESENTATIONS = {\n`;
for (const [key, val] of Object.entries(manifest)) {
  moduleContent += `  ${key}: ${JSON.stringify(JSON.stringify(val))},\n`;
}
moduleContent += `};\n`;

writeFileSync(resolve(__dirname, "./presentations-admin-with-audio.mjs"), moduleContent);
console.log(`\n✅ Audio admin listo (${Object.keys(LESSON_KEYS).length} lecciones)`);
