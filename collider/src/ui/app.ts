// The feed: vertical snap scrolling, a bounded engine window, overlay controls,
// remix / reorder / custom collisions, provenance, deterministic URLs, favorites.

import type { Collision, Synthesis } from "../model/types";
import { encodeAddress, decodeAddress, type CollisionAddress } from "../model/url";
import { remix, reorder, makeCollision } from "../model/collision";
import { fnv1a } from "../model/hash";
import { ARCHETYPE_BLURB } from "../render/archetypes";
import { Engine } from "../render/engine";
import { DataStore, FeedSource, mutationString } from "../data/store";
import { SynthesisService } from "../synthesis/service";
import { Sonifier } from "../audio/sonify";

const $ = <T extends HTMLElement>(s: string) => document.querySelector(s) as T;
const esc = (s: string) => s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]!));

interface Item {
  c: Collision;
  el: HTMLElement;
  remixTarget: 0 | 1 | 2;
  generation: number;
  synth?: Synthesis;
}

export class App {
  private items: Item[] = [];
  private active = 0;
  private engine: Engine;
  private feedEl = $("#feed");
  private source!: FeedSource;
  private synth: SynthesisService;
  private sound = new Sonifier();
  private wheelLock = 0;
  private wheelAcc = 0;
  private io!: IntersectionObserver;

  constructor(private store: DataStore) {
    this.engine = new Engine($("#gl") as unknown as HTMLCanvasElement);
    this.synth = new SynthesisService(store);
    this.engine.onStable = (id) => this.revealShard(id);
  }

  start() {
    const params = new URLSearchParams(location.search);
    const sessionSeed = params.get("feed") ? Number(params.get("feed")) >>> 0 : (Math.random() * 2 ** 31) >>> 0;
    this.source = new FeedSource(this.store, sessionSeed);
    const addr = decodeAddress(location.hash);
    const first = (addr && this.store.fromAddress(addr)) || this.source.first();
    this.append(first);
    for (let i = 0; i < 3; i++) this.append(this.source.next());
    this.io = new IntersectionObserver((entries) => {
      for (const e of entries) {
        if (e.isIntersecting && e.intersectionRatio > 0.55) {
          const idx = this.items.findIndex((it) => it.el === e.target);
          if (idx >= 0 && idx !== this.active) this.setActive(idx);
        }
      }
    }, { root: this.feedEl, threshold: [0.55, 0.9] });
    this.items.forEach((it) => this.io.observe(it.el));
    this.bindControls();
    this.setActive(0);
    setInterval(() => this.hud(), 500);
    const loopSound = () => { this.sound.tick(this.engine.world(this.items[this.active]?.c.id ?? "")); requestAnimationFrame(loopSound); };
    requestAnimationFrame(loopSound);
    // datalist for the custom collider
    const dl = $("#concepts");
    dl.innerHTML = this.store.concepts.map((c) => `<option value="${esc(c.name)}">${esc(c.field ?? "")}</option>`).join("");
  }

  // ------------------------------------------------------------------ slides
  private slideHTML(c: Collision): string {
    const p = c.provenance;
    const src = p.source === "hephaestus"
      ? `<span class="src hephaestus">historical · hephaestus / nous</span>`
      : p.source === "curated" ? `<span class="src curated">curated showcase</span>`
      : p.source === "user" ? `<span class="src user">your collision</span>`
      : `<span class="src generated">generated</span>`;
    const hist = p.source === "hephaestus" ? this.store.historicalRecord(p.historicalId!) : undefined;
    const bits: string[] = [src];
    if (hist?.forged) bits.push(`<span>forged</span>`);
    if (hist?.bestComposite != null) bits.push(`<span>nous ${hist.bestComposite.toFixed(1)}</span>`);
    if (p.derivedFromHistorical) bits.push(`<span class="mut">from historical</span>`);
    if (c.mutation?.kind === "replace") bits.push(`<span class="mut">remix · ${esc(c.mutation.oldConcept!)} → ${esc(c.mutation.newConcept!)}</span>`);
    if (c.mutation?.kind === "reorder") bits.push(`<span class="mut">reordered</span>`);
    const names = c.concepts.map((x, i) => `<button class="cname${i === 2 ? " target" : ""}" data-i="${i}" title="${esc(x.field ?? "user concept")} — tap to choose the concept Remix replaces">${esc(x.name)}</button>`)
      .join(`<span class="x">×</span>`);
    return `<div class="meta">
      <div class="badge">${bits.join("")}</div>
      <div class="triad">${names}</div>
      <div class="arch">${c.visualGenome.archetype.replace("_", " ")} · ${ARCHETYPE_BLURB[c.visualGenome.archetype]}</div>
      <div class="shard"><div class="shard-title"></div><p class="shard-text"></p><div class="epistemic"></div></div>
    </div>`;
  }

  private makeItem(c: Collision): Item {
    const el = document.createElement("section");
    el.className = "slide";
    el.dataset.id = c.id;
    el.innerHTML = this.slideHTML(c);
    const item: Item = { c, el, remixTarget: 2, generation: 0 };
    el.querySelectorAll<HTMLButtonElement>(".cname").forEach((b) => b.addEventListener("click", (ev) => {
      ev.stopPropagation();
      item.remixTarget = Number(b.dataset.i) as 0 | 1 | 2;
      el.querySelectorAll(".cname").forEach((x) => x.classList.toggle("target", x === b));
      this.toast(`remix will replace ${c.concepts[item.remixTarget].name}`);
    }));
    return item;
  }

  private append(c: Collision) {
    const it = this.makeItem(c);
    this.items.push(it);
    this.feedEl.appendChild(it.el);
    this.io?.observe(it.el);
  }

  private insertAfterActive(c: Collision) {
    const it = this.makeItem(c);
    const at = this.active + 1;
    this.items.splice(at, 0, it);
    this.feedEl.insertBefore(it.el, this.items[at + 1]?.el ?? null);
    this.io.observe(it.el);
    this.syncEngine();
    requestAnimationFrame(() => it.el.scrollIntoView({ behavior: "smooth" }));
  }

  private setActive(i: number) {
    this.active = i;
    while (this.items.length - i < 4) this.append(this.source.next());
    this.syncEngine();
    const c = this.items[i].c;
    history.replaceState(null, "", location.pathname + location.search + encodeAddress(this.address(c)));
    for (const j of [i - 1, i, i + 1]) if (this.items[j]) this.loadShard(this.items[j]);
    $("#rail").querySelector('[data-act="fav"]')!.classList.toggle("on", this.isFav(c));
    $("#rail").querySelector('[data-act="freeze"]')!.classList.toggle("on", !!this.engine.world(c.id)?.frozen);
    if (i > 0) $("#hint").classList.add("gone");
  }

  private syncEngine() {
    const i = this.active;
    const win = [i - 1, i, i + 1].filter((j) => j >= 0 && j < this.items.length).map((j) => this.items[j]);
    this.engine.setSlots(win.map((it) => ({ collision: it.c, el: it.el })));
    this.engine.setWindow(this.items[i].c.id, win.map((it) => it.c.id));
    // a world may already be past its reveal point when revisited
    for (const it of win) if (this.engine.world(it.c.id)?.revealed) this.revealShard(it.c.id);
  }

  private address(c: Collision): CollisionAddress {
    if (c.provenance.source === "hephaestus" && c.provenance.historicalId) return { historicalId: c.provenance.historicalId };
    const pinned = c.visualGenome.archetype !== makeCollision(c.concepts, c.seed, c.provenance).visualGenome.archetype;
    return {
      names: c.concepts.map((x) => x.name) as [string, string, string],
      seed: c.seed,
      source: c.provenance.source,
      parent: c.parentCollisionId,
      mutation: mutationString(c),
      archetype: pinned ? c.visualGenome.archetype : undefined,
    };
  }

  // ------------------------------------------------------------------ synthesis
  private async loadShard(it: Item) {
    if (it.synth) return;
    const s = await this.synth.get(it.c);
    it.synth = s;
    const box = it.el.querySelector(".shard")!;
    box.querySelector(".shard-title")!.textContent = s.title ?? "";
    box.querySelector(".shard-text")!.textContent = s.reasoningShard;
    box.querySelector(".epistemic")!.textContent =
      s.kind === "historical-nous-analysis" ? "historical nous analysis · llm output, 2026-03 · not validated"
      : s.kind === "external" ? "external synthesis · speculative · not a scientific claim"
      : "speculative synthesis · generated · not a scientific claim";
  }

  private revealShard(id: string) {
    const it = this.items.find((x) => x.c.id === id);
    if (it) it.el.querySelector(".shard")?.classList.add("on");
  }

  // ------------------------------------------------------------------ controls
  private bindControls() {
    const rail = $("#rail");
    rail.addEventListener("click", (e) => {
      const b = (e.target as HTMLElement).closest("button");
      if (b) this.act(b.dataset.act!);
    });
    $("#collide-open").addEventListener("click", () => this.openCollide());
    // a replay link pasted into an open tab: load that collision next to the current one
    window.addEventListener("hashchange", () => {
      const a = decodeAddress(location.hash);
      const c = a && this.store.fromAddress(a);
      if (c && c.id !== this.items[this.active].c.id) this.insertAfterActive(c);
    });
    $("#collide-cancel").addEventListener("click", () => ($("#modal").hidden = true));
    $("#collide-form").addEventListener("submit", (e) => { e.preventDefault(); this.customCollide(); });
    $("#sheet").addEventListener("click", (e) => { if (e.target === $("#sheet") || (e.target as HTMLElement).classList.contains("sheet-close")) $("#sheet").hidden = true; });
    let taps = 0, tapT = 0;
    $("#mark").addEventListener("click", () => {
      const now = performance.now();
      taps = now - tapT < 500 ? taps + 1 : 1;
      tapT = now;
      if (taps >= 3) { $("#hud").hidden = !$("#hud").hidden; taps = 0; }
    });
    window.addEventListener("keydown", (e) => {
      if ((e.target as HTMLElement).tagName === "INPUT") return;
      const k = e.key;
      if (e.ctrlKey || e.metaKey || e.altKey) return;
      // hotkeys must not also type into the input that opens (e.g. "c" -> collide modal)
      if (k.length === 1 && "rioscfmh".includes(k)) e.preventDefault();
      if (k === "ArrowDown" || k === "j" || k === "PageDown") { e.preventDefault(); this.go(1); }
      else if (k === "ArrowUp" || k === "k" || k === "PageUp") { e.preventDefault(); this.go(-1); }
      else if (k === " ") { e.preventDefault(); this.act("freeze"); }
      else if (k === "r") this.act("remix");
      else if (k === "o") this.act("reorder");
      else if (k === "i") this.act("info");
      else if (k === "s") this.act("share");
      else if (k === "f") this.act("fav");
      else if (k === "m") this.act("sound");
      else if (k === "c") this.openCollide();
      else if (k === "h") $("#hud").hidden = !$("#hud").hidden;
      else if (k === "Escape") { $("#sheet").hidden = true; $("#modal").hidden = true; }
    });
    // one collision per wheel gesture (trackpads emit bursts)
    this.feedEl.addEventListener("wheel", (e) => {
      if (Math.abs(e.deltaY) < Math.abs(e.deltaX)) return;
      e.preventDefault();
      const now = performance.now();
      if (now < this.wheelLock) return;
      this.wheelAcc += e.deltaY;
      if (Math.abs(this.wheelAcc) > 40) {
        this.go(this.wheelAcc > 0 ? 1 : -1);
        this.wheelAcc = 0;
        this.wheelLock = now + 650;
      }
    }, { passive: false });
  }

  private go(d: number) {
    const j = Math.max(0, Math.min(this.items.length - 1, this.active + d));
    this.items[j].el.scrollIntoView({ behavior: "smooth" });
  }

  private act(a: string) {
    const it = this.items[this.active];
    const w = this.engine.world(it.c.id);
    switch (a) {
      case "freeze": {
        if (!w) return;
        w.frozen = !w.frozen;
        $("#rail").querySelector('[data-act="freeze"]')!.classList.toggle("on", w.frozen);
        break;
      }
      case "remix": {
        const child = remix(it.c, it.remixTarget, this.store.concepts, it.generation++);
        this.insertAfterActive(child);
        break;
      }
      case "reorder": this.insertAfterActive(reorder(it.c)); break;
      case "info": this.showInfo(it); break;
      case "share": {
        const url = location.href;
        navigator.clipboard?.writeText(url).then(() => this.toast("replay link copied"), () => this.toast(url));
        break;
      }
      case "fav": {
        const on = this.toggleFav(it.c);
        $("#rail").querySelector('[data-act="fav"]')!.classList.toggle("on", on);
        this.toast(on ? "kept" : "released");
        break;
      }
      case "sound": this.sound.toggle().then((on) => $("#rail").querySelector('[data-act="sound"]')!.classList.toggle("on", on)); break;
    }
  }

  private openCollide() {
    $("#modal").hidden = false;
    ($("#collide-form").querySelector("input") as HTMLInputElement).focus();
  }

  private customCollide() {
    const f = $("#collide-form") as unknown as HTMLFormElement;
    const names = ["a", "b", "c"].map((n) => (f.elements.namedItem(n) as HTMLInputElement).value.trim());
    if (names.some((n) => !n)) return;
    const concepts = names.map((n) => this.store.concept(n)) as Collision["concepts"];
    const seed = fnv1a("user:" + names.join("|").toLowerCase());
    const c = makeCollision(concepts, seed, { source: "user" }, { createdAt: new Date().toISOString() });
    $("#modal").hidden = true;
    this.insertAfterActive(c);
  }

  // ------------------------------------------------------------------ provenance
  private async showInfo(it: Item) {
    const c = it.c;
    const g = c.visualGenome;
    const p = c.provenance;
    const rows: [string, string][] = [
      ["collision id", c.id],
      ["source", p.source],
      ["concept order", c.concepts.map((x, i) => `${i + 1}. ${x.name}${x.field ? ` (${x.field}, ${(x.sourceMetadata?.mechanism as string) ?? "?"})` : " (user)"}`).join("\n")],
      ["seed", String(c.seed)],
      ["archetype", g.archetype],
      ["replay link", location.href],
    ];
    if (c.parentCollisionId) rows.push(["parent", c.parentCollisionId]);
    if (c.mutation) rows.push(["mutation", mutationString(c)!]);
    if (p.derivedFromHistorical) rows.push(["historical root", p.derivedFromHistorical]);
    if (c.createdAt) rows.push(["created", c.createdAt]);
    let hist = "";
    if (p.source === "hephaestus" && p.historicalId) {
      rows.push(["artifact", `${p.artifactPath}:${p.artifactLine}`]);
      const d = await this.store.detail(p.historicalId);
      if (d) {
        const m = d.historicalMetadata;
        const occ = m.occurrences[0];
        rows.push(["nous model", occ?.model ?? "?"], ["nous time", occ?.timestamp ?? "?"],
          ["nous composite", String(m.bestComposite ?? "n/a")], ["evaluations", String(m.occurrences.length)],
          ["forge outcome", m.forge.length ? m.forge.map((f) => `${f.status}${f.reason ? ` (${f.reason})` : ""} acc=${f.accuracy}`).join("\n") : "not in ledger"]);
        if (m.forgeTools.length) rows.push(["forged tool", m.forgeTools.join("\n")]);
        if (m.humanReadable) rows.push(["report", m.humanReadable]);
        if (m.priorityReason) rows.push(["priority reason", m.priorityReason]);
        hist = `<p class="note">This triple is an authentic record from the Prometheus Hephaestus/Nous forge (March 2026). The text shown is the Nous model's own analysis, excerpted; the full response is at the artifact line above. It is historical LLM output, not a validated scientific result. The geometry is a creative visualization and is not evidence either.</p>`;
      }
    } else {
      hist = `<p class="note">${p.source === "curated" ? "A hand-picked triple of real dictionary concepts." : p.source === "user" ? "Your three ideas." : "A new triple sampled from the historical concept dictionary."} The reasoning shard is speculative text from a deterministic template grammar${p.source === "curated" && g.archetype ? "; the archetype may be pinned for showcase variety (recorded in the link)" : ""}. Neither the geometry nor the text is a scientific claim.</p>`;
    }
    const genome = {
      archetype: g.archetype, symmetry: g.symmetry, attractorCount: g.attractorCount, branchingFactor: g.branchingFactor,
      turbulence: +g.turbulence.toFixed(3), elasticity: +g.elasticity.toFixed(3), fractureThreshold: +g.fractureThreshold.toFixed(3),
      twist: +g.twist.toFixed(3), distortion: +g.distortion.toFixed(3), collisionStyle: g.collisionStyle, evolution: g.evolution,
      material: g.material.kind, timing: g.timing, bodies: g.bodies.map((b) => `${b.shape}/${b.material}`),
    };
    $("#sheet-body").innerHTML = `<h3>Provenance</h3>
      <dl class="kv">${rows.map(([k, v]) => `<dt>${esc(k)}</dt><dd>${esc(v).replace(/\n/g, "<br>")}</dd>`).join("")}</dl>
      ${hist}<h3>Visual genome</h3><pre>${esc(JSON.stringify(genome, null, 1))}</pre>`;
    $("#sheet").hidden = false;
  }

  // ------------------------------------------------------------------ favorites
  private favs(): { id: string; url: string; names: string[] }[] {
    try { return JSON.parse(localStorage.getItem("collider.favorites") ?? "[]"); } catch { return []; }
  }
  private isFav(c: Collision) { return this.favs().some((f) => f.id === c.id); }
  private toggleFav(c: Collision): boolean {
    let f = this.favs();
    const on = !f.some((x) => x.id === c.id);
    f = on ? [...f, { id: c.id, url: location.href, names: c.concepts.map((x) => x.name) }] : f.filter((x) => x.id !== c.id);
    try { localStorage.setItem("collider.favorites", JSON.stringify(f)); } catch { /* storage unavailable */ }
    return on;
  }

  private toast(msg: string) {
    const t = $("#toast");
    t.textContent = msg;
    t.classList.add("on");
    clearTimeout((t as any)._h);
    (t as any)._h = setTimeout(() => t.classList.remove("on"), 1400);
  }

  private hud() {
    const h = $("#hud");
    if (h.hidden) return;
    const s = this.engine.stats();
    const w = this.engine.world(this.items[this.active]?.c.id ?? "");
    h.textContent = [
      `fps ${s.fps.toFixed(0)}  frame ${s.frameMs.toFixed(1)}ms  tier ${s.tier}`,
      `worlds ${s.worlds}  created ${s.created}  disposed ${s.disposed}`,
      `particles ${s.particles}  geo ${s.geometries}  tex ${s.textures}  prog ${s.programs}`,
      `heap ${s.heapMB?.toFixed(0) ?? "n/a"}MB  slides ${this.items.length}  active ${this.active}`,
      `${w ? `${w.genome.archetype} ${w.phase} t=${w.t.toFixed(1)}` : ""}`,
      `webgpu ${s.webgpu ? "available (renderer: webgl2)" : "n/a"}`,
      `${s.gpu.slice(0, 48)}`,
    ].join("\n");
  }

  /** Exposed for automated inspection (scripts/snap.mjs). */
  debug() {
    return { active: this.active, items: this.items.length, stats: this.engine.stats(), ids: this.items.map((i) => i.c.id) };
  }
}
