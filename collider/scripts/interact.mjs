// Interaction checks in a real browser: remix, reorder, custom collide, freeze,
// provenance sheet, deterministic replay, and mobile touch scrolling.
import puppeteer from "puppeteer-core";
const base = process.argv[2] ?? "http://localhost:5188/";
const exe = "C:/Program Files/Google/Chrome/Application/chrome.exe";
const b = await puppeteer.launch({ executablePath: exe, headless: "new", args: ["--use-angle=d3d11", "--ignore-gpu-blocklist"], protocolTimeout: 60000 });
const kill = setTimeout(() => { console.log("watchdog"); b.close(); process.exit(2); }, 240000);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const out = {};
const errs = [];
try {
  const p = await b.newPage();
  await p.setViewport({ width: 1280, height: 800 });
  p.on("pageerror", (e) => errs.push(e.message));
  p.on("console", (m) => { if (m.type() === "error") errs.push(m.text()); });
  await p.goto(`${base}?feed=99&r=${Date.now()}`, { waitUntil: "load" });
  await sleep(2500);
  const st = () => p.evaluate(() => {
    const app = window.__collider; const it = app.items[app.active];
    const w = app.engine.world(it.c.id);
    return { active: app.active, n: app.items.length, id: it.c.id, src: it.c.provenance.source, names: it.c.concepts.map((c) => c.name), mut: it.c.mutation ?? null, parent: it.c.parentCollisionId ?? null, arch: it.c.visualGenome.archetype, t: w ? +w.t.toFixed(2) : null, frozen: w?.frozen ?? null, hash: location.hash.slice(0, 90) };
  });
  out.start = await st();
  // freeze
  await p.keyboard.press(" "); const f1 = await st(); await sleep(1000); const f2 = await st();
  out.freeze = { frozenFlag: f1.frozen, tBefore: f1.t, tAfter: f2.t, held: f1.t === f2.t };
  await p.keyboard.press(" ");
  // provenance sheet on the (historical) first collision
  await p.keyboard.press("i"); await sleep(600);
  out.sheet = await p.evaluate(() => ({ shown: !document.querySelector("#sheet").hidden, text: document.querySelector("#sheet-body").innerText.slice(0, 700) }));
  await p.screenshot({ path: "screenshots/ui_provenance.png" });
  await p.keyboard.press("Escape");
  // remix
  await p.keyboard.press("r"); await sleep(2200);
  out.remix = await st();
  await sleep(4000);
  await p.screenshot({ path: "screenshots/ui_remix.png" });
  // reorder
  await p.keyboard.press("o"); await sleep(2200);
  out.reorder = await st();
  // custom collide
  await p.keyboard.press("c"); await sleep(300);
  await p.type('input[name="a"]', "Quantum error correction");
  await p.type('input[name="b"]', "Mycelial networks");
  await p.type('input[name="c"]', "Constitutional law");
  await p.click('button[type="submit"]'); await sleep(2400);
  out.custom = await st();
  await sleep(6500);
  await p.screenshot({ path: "screenshots/ui_custom.png" });
  // deterministic replay: reload the custom collision's URL in a fresh page, compare genomes
  const url = await p.evaluate(() => location.href);
  const g1 = await p.evaluate(() => JSON.stringify(window.__collider.items[window.__collider.active].c.visualGenome));
  const p2 = await b.newPage();
  await p2.setViewport({ width: 900, height: 700 });
  await p2.goto(url.replace("#", `${url.includes("?") ? "&" : "?"}fresh=1#`), { waitUntil: "load" });
  await sleep(1500);
  const g2 = await p2.evaluate(() => JSON.stringify(window.__collider.items[0].c.visualGenome));
  out.replay = { url: url.slice(0, 160), identicalGenome: g1 === g2 };
  // mobile: touch-style scroll and snap
  const m = await b.newPage();
  await m.setViewport({ width: 390, height: 844, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
  await m.goto(`${base}?feed=7&r=${Date.now()}`, { waitUntil: "load" });
  await sleep(2000);
  for (let i = 0; i < 3; i++) {
    await m.evaluate(() => document.querySelector("#feed").scrollBy({ top: window.innerHeight * 0.6, behavior: "instant" }));
    await sleep(1400);
  }
  out.mobile = await m.evaluate(() => { const f = document.querySelector("#feed"); return { active: window.__collider.active, scrollTop: f.scrollTop, snapped: f.scrollTop % window.innerHeight < 2 || window.innerHeight - (f.scrollTop % window.innerHeight) < 2, vh: window.innerHeight }; });
  await sleep(5500);
  await m.screenshot({ path: "screenshots/ui_mobile_feed.png" });
} finally {
  clearTimeout(kill);
  console.log(JSON.stringify({ ...out, errors: errs.slice(0, 10) }, null, 1));
  await b.close();
}
