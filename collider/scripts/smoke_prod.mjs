import puppeteer from "puppeteer-core";
const b = await puppeteer.launch({ executablePath: "C:/Program Files/Google/Chrome/Application/chrome.exe", headless: "new", args: ["--use-angle=d3d11","--ignore-gpu-blocklist","--autoplay-policy=no-user-gesture-required"], protocolTimeout: 60000 });
const kill = setTimeout(() => { b.close(); process.exit(2); }, 90000);
const errs = [];
try {
  const p = await b.newPage(); await p.setViewport({ width: 1280, height: 800 });
  p.on("pageerror", e => errs.push(e.message)); p.on("console", m => { if (m.type() === "error") errs.push(m.text()); });
  await p.goto(process.argv[2] ?? "http://localhost:5189/", { waitUntil: "load" });
  await new Promise(r => setTimeout(r, 2500));
  await p.keyboard.press("m"); await new Promise(r => setTimeout(r, 1500));
  await p.keyboard.press("ArrowDown"); await new Promise(r => setTimeout(r, 4000));
  const s = await p.evaluate(() => ({ items: window.__collider.items.length, active: window.__collider.active, sound: window.__collider.sound.enabled, fps: +window.__collider.engine.stats().fps.toFixed(0), hist: window.__collider.store.historical.length }));
  console.log(JSON.stringify({ ...s, errors: errs }));
} finally { clearTimeout(kill); await b.close(); }
