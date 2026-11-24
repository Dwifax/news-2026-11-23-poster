// make.fun news-image entry point.
// Copies the pre-rendered, committed entry.png to the grader's output directory.
// The image is produced ahead of time by tools/render_poster.py so this program
// needs no dependencies beyond Node's standard library and always writes the
// exact same bytes.
import { copyFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const src = join(here, "entry.png");
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const dest = join(outDir, "entry.png");

mkdirSync(outDir, { recursive: true });
copyFileSync(src, dest);
