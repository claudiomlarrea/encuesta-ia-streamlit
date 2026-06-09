import { mkdirSync, existsSync, writeFileSync, rmSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";
import { execSync } from "child_process";
import { PRESENTATIONS } from "./presentations-ml.mjs";

const __dirname = dirname(fileURLToPath(import.meta.url));
const AUDIO_DIR = resolve(__dirname, "../public/audio/ml");
const VOICE = "Eddy (Spanish (Mexico))";
const RATE = 135; // palabras por minuto (más lento = más natural)
const FORCE = process.argv.includes("--force");

const LESSON_KEYS = {
  queEsML: "que-es-ml",
  tiposAprendizaje: "tipos-aprendizaje",
};

/** Inserta pausas de silencio para que macOS `say` respete ritmo y puntuación */
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
  console.log("🗑️  Audio anterior eliminado\n");
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
    const audioUrl = `/audio/ml/${filename}`;
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

writeFileSync(resolve(__dirname, "./presentations-ml-with-audio.mjs"), moduleContent);
console.log(`\n✅ Audio listo (${Object.keys(LESSON_KEYS).length} lecciones, ${RATE} ppm)`);
