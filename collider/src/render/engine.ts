// One WebGL context for the whole feed. Each visible slide is rendered into its own
// scissored viewport that tracks the slide's on-screen rectangle, so during a swipe
// two worlds slide past each other exactly like two posts. At most three Worlds exist
// (previous / current / next); everything else is disposed.

import * as THREE from "three";
import type { Collision } from "../model/types";
import { createWorld } from "./archetypes";
import type { Tier, World, WorldContext } from "./world";

export interface SlotView {
  collision: Collision;
  el: HTMLElement;
}

export interface EngineStats {
  fps: number;
  frameMs: number;
  worlds: number;
  created: number;
  disposed: number;
  particles: number;
  geometries: number;
  textures: number;
  programs: number;
  heapMB: number | null;
  tier: Tier;
  webgpu: boolean;
  gpu: string;
}

const BUDGET: Record<Tier, number> = { high: 46000, mid: 24000, low: 11000 };

export class Engine {
  readonly renderer: THREE.WebGLRenderer;
  private worlds = new Map<string, World>();
  private slots: SlotView[] = [];
  private activeId: string | null = null;
  private last = performance.now();
  private created = 0;
  private disposed = 0;
  private frameTimes: number[] = [];
  private slowFrames = 0;
  tier: Tier;
  private pixelRatio: number;
  private gpuName = "unknown";
  private floatRT: boolean;
  onStable?: (id: string) => void;
  paused = false;

  constructor(canvas: HTMLCanvasElement) {
    this.renderer = new THREE.WebGLRenderer({ canvas, antialias: false, alpha: false, powerPreference: "high-performance" });
    this.renderer.autoClear = false;
    this.renderer.setScissorTest(true);
    this.tier = detectTier(this.renderer);
    this.pixelRatio = Math.min(window.devicePixelRatio || 1, this.tier === "high" ? 2 : 1.5);
    this.renderer.setPixelRatio(this.pixelRatio);
    this.floatRT = this.renderer.capabilities.isWebGL2;
    const dbg = this.renderer.getContext().getExtension("WEBGL_debug_renderer_info");
    if (dbg) this.gpuName = String(this.renderer.getContext().getParameter(dbg.UNMASKED_RENDERER_WEBGL));
    this.resize();
    window.addEventListener("resize", () => this.resize());
    requestAnimationFrame(this.loop);
  }

  private ctx(): WorldContext {
    return { renderer: this.renderer, tier: this.tier, budget: BUDGET[this.tier], floatRT: this.floatRT };
  }

  resize() {
    this.renderer.setSize(window.innerWidth, window.innerHeight, false);
  }

  setSlots(slots: SlotView[]) {
    this.slots = slots;
  }

  /** Keep worlds for `keepIds` (the bounded window), dispose the rest. */
  setWindow(activeId: string, keepIds: string[]) {
    this.activeId = activeId;
    const keep = new Set(keepIds);
    for (const [id, w] of this.worlds) {
      if (!keep.has(id)) {
        w.dispose();
        this.worlds.delete(id);
        this.disposed++;
      }
    }
    for (const id of keepIds) {
      if (this.worlds.has(id)) continue;
      const slot = this.slots.find((s) => s.collision.id === id);
      if (!slot) continue;
      const w = createWorld(slot.collision, this.ctx());
      w.onStable = () => this.onStable?.(id);
      this.renderer.compile(w.scene, w.camera); // preload: compile before it is seen
      this.worlds.set(id, w);
      this.created++;
    }
  }

  world(id: string): World | undefined {
    return this.worlds.get(id);
  }

  /** Rebuild one world (e.g. after a quality-tier change). */
  rebuild(id: string) {
    const w = this.worlds.get(id);
    if (!w) return;
    const t = w.t, frozen = w.frozen;
    w.dispose();
    this.disposed++;
    const slot = this.slots.find((s) => s.collision.id === id)!;
    const nw = createWorld(slot.collision, this.ctx());
    nw.t = t;
    nw.frozen = frozen;
    nw.onStable = () => this.onStable?.(id);
    this.worlds.set(id, nw);
    this.created++;
  }

  private loop = (now: number) => {
    requestAnimationFrame(this.loop);
    const dt = Math.min(0.05, (now - this.last) / 1000);
    this.last = now;
    if (this.paused || document.hidden) return;
    this.frameTimes.push(dt * 1000);
    if (this.frameTimes.length > 120) this.frameTimes.shift();
    this.adapt(dt);

    const W = window.innerWidth, H = window.innerHeight;
    const r = this.renderer;
    r.setScissor(0, 0, W, H);
    r.setViewport(0, 0, W, H);
    r.setClearColor(0x000000, 1);
    r.clear();
    for (const slot of this.slots) {
      const w = this.worlds.get(slot.collision.id);
      if (!w) continue;
      const rect = slot.el.getBoundingClientRect();
      const visible = rect.bottom > 0 && rect.top < H;
      const active = slot.collision.id === this.activeId;
      w.update(dt, active);
      if (!visible) continue;
      w.preRender(r);
      r.setScissorTest(true);
      // GL viewport origin is bottom-left
      const x = Math.round(rect.left), y = Math.round(H - rect.bottom);
      w.render(r, x, y, Math.round(rect.width), Math.round(rect.height), this.pixelRatio);
    }
  };

  /** Drop a quality tier if frame time stays high; affects newly built worlds and the
   *  active world is rebuilt at the lower budget. */
  private adapt(dt: number) {
    if (dt * 1000 > 26) this.slowFrames++;
    else this.slowFrames = Math.max(0, this.slowFrames - 1);
    if (this.slowFrames > 90 && this.tier !== "low") {
      this.tier = this.tier === "high" ? "mid" : "low";
      this.slowFrames = 0;
      this.pixelRatio = Math.min(this.pixelRatio, this.tier === "mid" ? 1.5 : 1);
      this.renderer.setPixelRatio(this.pixelRatio);
      this.resize();
      if (this.activeId) this.rebuild(this.activeId);
    }
  }

  stats(): EngineStats {
    const ft = this.frameTimes;
    const avg = ft.length ? ft.reduce((a, b) => a + b, 0) / ft.length : 0;
    const info = this.renderer.info;
    const mem = (performance as any).memory;
    let particles = 0;
    for (const w of this.worlds.values()) particles += w.particleCount;
    return {
      fps: avg ? 1000 / avg : 0,
      frameMs: avg,
      worlds: this.worlds.size,
      created: this.created,
      disposed: this.disposed,
      particles,
      geometries: info.memory.geometries,
      textures: info.memory.textures,
      programs: info.programs?.length ?? 0,
      heapMB: mem ? mem.usedJSHeapSize / 1048576 : null,
      tier: this.tier,
      webgpu: typeof navigator !== "undefined" && "gpu" in navigator,
      gpu: this.gpuName,
    };
  }
}

function detectTier(r: THREE.WebGLRenderer): Tier {
  const q = new URLSearchParams(location.search).get("q");
  if (q === "high" || q === "mid" || q === "low") return q;
  const mobile = /Android|iPhone|iPad|iPod|Mobile/i.test(navigator.userAgent) || matchMedia("(pointer: coarse)").matches;
  const mem = (navigator as any).deviceMemory ?? 8;
  const cores = navigator.hardwareConcurrency ?? 4;
  const gl = r.getContext();
  const maxTex = gl.getParameter(gl.MAX_TEXTURE_SIZE) as number;
  if (mobile) return mem >= 6 && maxTex >= 8192 ? "mid" : "low";
  if (cores >= 8 && maxTex >= 16384) return "high";
  return "mid";
}
