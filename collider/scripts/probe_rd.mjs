import puppeteer from "puppeteer-core";
const b = await puppeteer.launch({ executablePath: "C:/Program Files/Google/Chrome/Application/chrome.exe", headless: "new", args: ["--use-angle=d3d11","--ignore-gpu-blocklist"], protocolTimeout: 30000 });
setTimeout(() => { b.close(); process.exit(2); }, 60000);
try {
  const p = await b.newPage(); await p.setViewport({ width: 1280, height: 800 });
  await p.goto("http://localhost:5188/?q=high&r=rd1#n=Renormalization|Morphogenesis|Category%20Theory&s=12345&src=curated&a=REACTION_DIFFUSION", { waitUntil: "load", timeout: 30000 });
  for (const wait of [3500, 3000]) {
    await new Promise(r => setTimeout(r, wait));
    console.log(await p.evaluate(() => {
      const eng = window.__collider.engine; const w = [...eng.worlds.values()].find(x => x.rt);
      const r = eng.renderer; const rt = w.rt[w.cur]; const S = rt.width;
      const buf = new Float32Array(S * S * 4);
      try { r.readRenderTargetPixels(rt, 0, 0, S, S, buf); } catch (e) { return "read failed " + e.message; }
      const h2f = (h) => { const s = (h & 0x8000) ? -1 : 1, e = (h >> 10) & 31, f = h & 1023; return e === 0 ? s * f * 2 ** -24 : e === 31 ? NaN : s * (1 + f / 1024) * 2 ** (e - 15); };
      let sumA = 0, sumB = 0, maxB = 0, nB = 0;
      for (let i = 0; i < S * S; i++) { const A = buf[i * 4], B = buf[i * 4 + 1]; sumA += A; sumB += B; maxB = Math.max(maxB, B); if (B > 0.1) nB++; }
      return JSON.stringify({ t: +w.t.toFixed(2), steps: w.steps, meanA: +(sumA / S / S).toFixed(3), meanB: +(sumB / S / S).toFixed(4), maxB: +maxB.toFixed(3), fracB: +(nB / S / S).toFixed(4), F: w.simMat.uniforms.uF.value, K: w.simMat.uniforms.uKill.value, ext: !!r.getContext().getExtension("EXT_color_buffer_float") });
    }));
  }
} finally { await b.close(); process.exit(0); }
