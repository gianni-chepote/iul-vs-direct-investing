// Build the self-contained page: inline the tested engine (calc.js) and the
// cached price data (prices.json) into app/template.html -> app/index.html.
// The result works via file:// and as a published artifact, with no imports or
// runtime fetches. Run: node scripts/build_page.mjs

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const APP = path.join(HERE, "../app");

const calc = fs.readFileSync(path.join(APP, "calc.js"), "utf8")
  .replaceAll("export ", ""); // functions/consts become script-local
const prices = fs.readFileSync(path.join(HERE, "../data/prices.json"), "utf8");
const template = fs.readFileSync(path.join(APP, "template.html"), "utf8");

const filled = template
  .replace("/*__CALC__*/", () => calc)
  .replace("/*__PRICES__*/", () => prices);

if (filled.includes("/*__CALC__*/") || filled.includes("/*__PRICES__*/")) {
  throw new Error("A placeholder was not substituted; check template markers.");
}

// Split the template into head content (title/meta/links/style) and body
// content, then wrap in a complete, standalone HTML document so the page works
// by double-click, on a static host, and inside a Streamlit embed.
const [head, body] = filled.split("<!--__SPLIT__-->");
if (body === undefined) throw new Error("Missing <!--__SPLIT__--> marker in template.");

const out = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
${head.trim()}
</head>
<body>
${body.trim()}
</body>
</html>
`;

const dest = path.join(APP, "index.html");
fs.writeFileSync(dest, out);
console.log(`Wrote ${dest} (${(out.length / 1024).toFixed(0)} KB)`);
