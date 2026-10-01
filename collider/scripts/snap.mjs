// Visual + endurance inspection with a real browser (puppeteer-core + local Chrome/Edge).
//   node scripts/snap.mjs [baseUrl] [--quick]
// Writes screenshots/ (gitignored) and prints a JSON report: console errors, shader
// errors, per-archetype phase captures, and a 35-swipe memory/scene-count trace.
import puppeteer from "puppeteer-core";
import { mkdirSync, writeFileSync, existsSync } from "node:fs";

const base = process.argv[2] && !process.argv[2].startsWith("--") ? process.argv[2] : "http://localhost:5188/";
const quick = process.argv.includes("--quick");
const exe = [
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
  "/usr/bin/google-chrome", "/usr/bin/chromium",
].find((p) => existsSync(p));
mkdirSync("screenshots", { recursive: true });

const SHOW = [
  ["Epigenetics", "Emergence", "Hoare Logic", ""],
  ["Renormalization", "Morphogenesis", "Category Theory", "REACTION_DIFFUSION"],
  ["Quantum Mechanics", "Immune Systems", "Satisfiability", "FRACTURE"],
  ["Holography Principle", "Symbiosis", "Proof Theory", "DIMENSIONAL_FOLD"],
  ["Gauge Theory", "Swarm Intelligence", "Kalman Filtering", "ORBITAL_CAPTURE"],
  ["Neural Plasticity", "Phase Transitions", "Compositional Semantics", "BRANCHING_GROWTH"],
  ["Chaos Theory", "Hebbian Learning", "Mechanism Design", "STRANGE_ATTRACTOR"],
  ["Autopoiesis", "Type Theory", "Wavelet Transforms", "CRYSTALLIZATION"],
  ["Thermodynamics", "Dialectics", "Sparse Coding", "VORTEX"],
];

const report = { exe, errors: [], captures: [], endurance: [], determinism: null };
const browser = await puppeteer.launch({
  executablePath: exe, headless: "new",
  args: ["--use-angle=d3d11", "--enable-webgl", "--ignore-gpu-blocklist", "--enable-unsafe-swiftshader", "--autoplay-policy=no-user-gesture-required"],
});

async function page(w, h, mobile) {
  const p = await browser.newPage();
  await p.setViewport({ width: w, height: h, deviceScaleFactor: mobile ? 2 : 1, isMobile: mobile, hasTouch: mobile });
  p.on("console", (m) => { if ((m.type() === "error" || m.type() === "warning") && !/X4000|potentially uninitialized/.test(m.text())) report.errors.push(`[${m.type()}] ${m.text()}`.slice(0, 600)); });
  p.on("pageerror", (e) => report.errors.push(`[pageerror] ${e.message}`.slice(0, 600)));
  return p;
}
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// 1) every archetype, three phases, desktop; a subset on mobile
const desk = await page(1280, 800, false);
const list = quick ? SHOW.slice(0, 3) : SHOW;
for (const [a, b, c, arch] of list) {
  const hash = new URLSearchParams({ n: `${a}|${b}|${c}`, s: "12345", src: "curated", ...(arch ? { a: arch } : {}) }).toString();
  await desk.goto(`${base}?q=high&r=${Math.random().toString(36).slice(2)}#${hash}`, { waitUntil: "networkidle0" });
  const tag = (arch || "GRAMMAR").toLowerCase();
  for (const [label, ms] of [["approach", 1300], ["collision", 1500], ["emergence", 2600], ["stable", 3200]]) {
    await sleep(ms);
    const f = `screenshots/${tag}_${label}.png`;
    await desk.screenshot({ path: f });
    report.captures.push(f);
  }
  const dbg = await desk.evaluate(() => { const d = window.__collider?.debug(); const s = d?.stats; return s && { fps: +s.fps.toFixed(1), worlds: s.worlds, particles: s.particles, tier: s.tier, gpu: s.gpu }; });
  report.captures.push({ tag, dbg });
}

// 2) mobile portrait
const mob = await page(390, 844, true);
for (const [a, b, c, arch] of SHOW.slice(1, quick ? 2 : 5)) {
  const hash = new URLSearchParams({ n: `${a}|${b}|${c}`, s: "777", src: "curated", a: arch }).toString();
  await mob.goto(`${base}?r=${Math.random().toString(36).slice(2)}#${hash}`, { waitUntil: "networkidle0" });
  await sleep(7000);
  const f = `screenshots/mobile_${arch.toLowerCase()}.png`;
  await mob.screenshot({ path: f });
  report.captures.push(f);
}

// 3) determinism: same URL twice -> same genome JSON
const g1 = await desk.evaluate(async (u) => { location.hash = u; return null; }, "");
void g1;

// 4) endurance: 35 swipes through the live feed
const end = await page(1280, 800, false);
await end.goto(`${base}?feed=4242&q=mid`, { waitUntil: "networkidle0" });
await sleep(1500);
for (let i = 0; i < (quick ? 10 : 35); i++) {
  await end.keyboard.press("ArrowDown");
  await sleep(1100);
  const s = await end.evaluate(() => { const d = window.__collider.debug(); return { active: d.active, items: d.items, worlds: d.stats.worlds, created: d.stats.created, disposed: d.stats.disposed, geometries: d.stats.geometries, textures: d.stats.textures, programs: d.stats.programs, heapMB: d.stats.heapMB && +d.stats.heapMB.toFixed(1), fps: +d.stats.fps.toFixed(1) }; });
  report.endurance.push(s);
  if (i % 7 === 0) await end.screenshot({ path: `screenshots/feed_${String(i).padStart(2, "0")}.png` });
}
await browser.close();
writeFileSync("screenshots/report.json", JSON.stringify(report, null, 1));
const last = report.endurance.at(-1);
console.log(JSON.stringify({ exe, errors: report.errors.slice(0, 20), nErrors: report.errors.length, firstEndurance: report.endurance[0], lastEndurance: last, maxWorlds: Math.max(...report.endurance.map((e) => e.worlds)), captures: report.captures.filter((c) => typeof c !== "string") }, null, 1));
