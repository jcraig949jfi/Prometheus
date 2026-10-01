// A World is one collision's universe: its scene, camera, lifecycle clock and GPU
// resources. Archetypes subclass it and add their emergent structures. The engine
// guarantees at most three Worlds exist (previous / current / next).

import * as THREE from "three";
import type { Collision, VisualGenome } from "../model/types";
import { ConceptGlyph } from "./glyphs";
import { PARTICLE_FRAGMENT, particleVertex } from "./glsl";

export type Phase = "approach" | "collide" | "emerge" | "stable";
export type Tier = "high" | "mid" | "low";

export interface WorldContext {
  renderer: THREE.WebGLRenderer;
  tier: Tier;
  budget: number; // particle budget for this device tier
  floatRT: boolean; // float/half-float render targets available
}

const SHAPE_ID = { shell: 0, ring: 1, lattice: 2, helix: 3, disc: 4, filament: 5 } as const;
const MAT_ID = { glass: 0, metal: 1, plasma: 2, bio: 3, ink: 4, ice: 5 } as const;

export abstract class World {
  readonly scene = new THREE.Scene();
  readonly camera = new THREE.PerspectiveCamera(38, 1, 0.1, 200);
  readonly root = new THREE.Group();
  readonly genome: VisualGenome;
  t = 0;
  frozen = false;
  readonly ta: number;
  readonly tc: number;
  readonly te: number;
  readonly bodyPos = [new THREE.Vector3(), new THREE.Vector3(), new THREE.Vector3()];
  particleCount = 0;
  onStable?: () => void;
  private stableFired = false;
  private glyphs: ConceptGlyph[] = [];
  private dust!: THREE.Points;
  private disposables: { dispose(): void }[] = [];
  protected readonly U: Record<string, THREE.IUniform>;
  private clear = new THREE.Color();

  constructor(readonly collision: Collision, protected ctx: WorldContext) {
    const g = (this.genome = collision.visualGenome);
    this.ta = g.timing.approach;
    this.tc = this.ta + g.timing.collide;
    this.te = this.tc + g.timing.emerge;
    this.scene.add(this.root);
    const B = g.bodies;
    this.U = {
      uTime: { value: 0 },
      uTa: { value: this.ta },
      uTc: { value: this.tc },
      uTe: { value: this.te },
      uBody: { value: this.bodyPos },
      uBodySize: { value: B.map((b) => b.size) },
      uShape: { value: B.map((b) => SHAPE_ID[b.shape]) },
      uMat: { value: B.map((b) => MAT_ID[b.material]) },
      uHsl: { value: B.map((b) => new THREE.Vector3(b.hue, b.sat, 0.6)) },
      uSpin: { value: B.map((b) => b.spin) },
      uG0: { value: new THREE.Vector4(g.params[0], g.params[1], g.params[2], g.params[3]) },
      uG1: { value: new THREE.Vector4(g.params[4], g.params[5], g.params[6], g.params[7]) },
      uSym: { value: g.symmetry },
      uTurb: { value: g.turbulence },
      uElastic: { value: g.elasticity },
      uTwist: { value: g.twist },
      uAttr: { value: g.attractorCount },
      uBranch: { value: g.branchingFactor },
      uFrac: { value: g.fractureThreshold },
      uCurl: { value: g.fieldForces.curl },
      uRadial: { value: g.fieldForces.radial },
      uAxial: { value: g.fieldForces.axial },
      uDistort: { value: g.distortion },
      uMut: { value: g.mutationRate },
      uPixel: { value: 300 },
      uSizeMul: { value: 1 },
    };
    this.clear.setHSL(B[0].hue, 0.4, 0.014, THREE.SRGBColorSpace); // near-black, tinted
    this.addDust();
    collision.concepts.forEach((c, i) => {
      const old = collision.mutation?.kind === "replace" && collision.mutation.replacedIndex === i ? collision.mutation.oldConcept : undefined;
      const gl = new ConceptGlyph(c.name, B[i].hue, i, old);
      this.glyphs.push(gl);
      this.scene.add(gl.mesh);
    });
    this.updateBodies();
  }

  /** Called once after construction by the factory; archetypes build geometry here. */
  abstract build(): void;

  /** Per-frame archetype hook (after common uniforms are updated). */
  protected frame(_dt: number): void {}

  /** GPU simulation passes (render-to-texture) before the world is drawn. */
  preRender(_renderer: THREE.WebGLRenderer): void {}

  get phase(): Phase {
    if (this.t < this.ta) return "approach";
    if (this.t < this.tc) return "collide";
    if (this.t < this.te) return "emerge";
    return "stable";
  }

  protected track<T extends { dispose(): void }>(d: T): T {
    this.disposables.push(d);
    return d;
  }

  /** Particle system sharing the common approach/collision grammar. */
  protected particles(count: number, emergeGLSL: string, opts: {
    extraDecl?: string;
    extraAttrs?: Record<string, THREE.BufferAttribute>;
    extraUniforms?: Record<string, THREE.IUniform>;
    blending?: THREE.Blending;
  } = {}): THREE.Points {
    const n = Math.max(200, Math.floor(count));
    const geo = new THREE.BufferGeometry();
    const aK = new Float32Array(n);
    const aR = new Float32Array(n * 4);
    const aI = new Float32Array(n);
    const pos = new Float32Array(n * 3);
    let s = (this.genome.seed ^ 0x9e3779b9) >>> 0;
    const rnd = () => {
      s = (s + 0x6d2b79f5) >>> 0;
      let t = s;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
    for (let i = 0; i < n; i++) {
      aK[i] = i % 3;
      for (let j = 0; j < 4; j++) aR[i * 4 + j] = rnd();
      aI[i] = i / n;
    }
    geo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
    geo.setAttribute("aK", new THREE.BufferAttribute(aK, 1));
    geo.setAttribute("aR", new THREE.BufferAttribute(aR, 4));
    geo.setAttribute("aI", new THREE.BufferAttribute(aI, 1));
    for (const [k, v] of Object.entries(opts.extraAttrs ?? {})) geo.setAttribute(k, v);
    geo.boundingSphere = new THREE.Sphere(new THREE.Vector3(), 50);
    const mat = new THREE.ShaderMaterial({
      vertexShader: particleVertex(emergeGLSL, opts.extraDecl ?? ""),
      fragmentShader: PARTICLE_FRAGMENT,
      uniforms: { ...this.U, ...(opts.extraUniforms ?? {}) },
      transparent: true,
      depthWrite: false,
      blending: opts.blending ?? THREE.AdditiveBlending,
    });
    const pts = new THREE.Points(geo, mat);
    pts.frustumCulled = false;
    this.track(geo);
    this.track(mat);
    this.particleCount += n;
    this.root.add(pts);
    return pts;
  }

  private addDust() {
    const n = this.ctx.tier === "low" ? 400 : 900;
    const pos = new Float32Array(n * 3);
    let s = this.genome.seed >>> 0;
    const r = () => ((s = (Math.imul(s ^ (s >>> 15), 2246822519) + 0x6d2b79f5) >>> 0) / 4294967296);
    for (let i = 0; i < n; i++) {
      const u = r() * Math.PI * 2, v = r() * 2 - 1, rad = 25 + r() * 40;
      const sv = Math.sqrt(1 - v * v);
      pos.set([Math.cos(u) * sv * rad, v * rad, Math.sin(u) * sv * rad], i * 3);
    }
    const geo = this.track(new THREE.BufferGeometry());
    geo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
    const col = new THREE.Color().setHSL(this.genome.bodies[1].hue, 0.3, 0.55);
    const mat = this.track(new THREE.PointsMaterial({ size: 1.4, sizeAttenuation: false, color: col, transparent: true, opacity: 0.35, depthWrite: false }));
    this.dust = new THREE.Points(geo, mat);
    this.scene.add(this.dust);
  }

  /** CPU-side approach paths: bodies fly in on curved paths and meet at the origin. */
  protected bodyPath(k: number, t: number, out: THREE.Vector3): THREE.Vector3 {
    const b = this.genome.bodies[k];
    const x = Math.min(1, t / this.ta);
    const e = 1 - Math.pow(1 - x, 2.2); // decelerating arrival
    const far = 9.5 * (1 - e) + 0.6 * (1 - Math.min(1, Math.max(0, (t - this.ta) / (this.tc - this.ta))));
    const swirl = Math.sin(e * Math.PI) * 1.4 * (k === 1 ? -1 : 1) * (0.6 + Math.abs(this.genome.twist));
    out.set(b.entry[0] * far, b.entry[1] * far, b.entry[2] * far);
    // perpendicular swirl (entry x up)
    out.x += -b.entry[2] * swirl;
    out.z += b.entry[0] * swirl;
    return out;
  }

  protected updateBodies() {
    for (let k = 0; k < 3; k++) this.bodyPath(k, this.t, this.bodyPos[k]);
  }

  update(dt: number, active: boolean) {
    if (active && !this.frozen) this.t += dt;
    const t = this.t;
    this.U.uTime.value = t;
    this.updateBodies();
    const g = this.genome;
    // post-impact evolution acts on the whole structure
    const post = Math.max(0, t - this.tc);
    const ax = g.rotation.axis;
    if (active && !this.frozen) {
      this.root.rotateOnAxis(new THREE.Vector3(ax[0], ax[1], ax[2]), g.rotation.speed * dt * Math.min(1, post));
    }
    let scale = 1;
    let sizeMul = 1;
    switch (g.evolution) {
      case "breathe": scale = 1 + 0.045 * Math.sin(post * 0.9); break;
      case "pulse": sizeMul = 1 + 0.35 * Math.pow(Math.max(0, Math.sin(post * 2.1)), 3); break;
      case "drift": this.root.position.y = Math.sin(post * 0.25) * 0.25; break;
      case "precess": this.root.rotation.x = Math.sin(post * 0.3) * 0.22; break;
      case "cycle": scale = 1 + 0.02 * Math.sin(post * 0.5); sizeMul = 1 + 0.15 * Math.sin(post * 0.5 + 1); break;
    }
    this.root.scale.setScalar(scale);
    this.U.uSizeMul.value = sizeMul;
    const ringR = 3.3;
    this.glyphs.forEach((gl, i) => gl.update(t, this.bodyPos[i], this.ta, this.tc, this.te, ringR, g.twist));
    this.dust.rotation.y = t * 0.01;
    this.frame(dt);
    if (!this.stableFired && t >= this.tc + (this.te - this.tc) * 0.75) {
      this.stableFired = true;
      this.onStable?.();
    }
  }

  get revealed() {
    return this.stableFired;
  }

  render(renderer: THREE.WebGLRenderer, x: number, y: number, w: number, h: number, pixelRatio: number) {
    const aspect = w / Math.max(1, h);
    this.camera.aspect = aspect;
    const t = this.t;
    const dist = 8.4 / Math.min(1, aspect * 1.35);
    const az = t * 0.05 * (this.genome.twist >= 0 ? 1 : -1) + this.genome.seed % 7;
    const el = 0.28 + 0.1 * Math.sin(t * 0.13);
    // subtle impact shake
    const shake = Math.exp(-Math.pow((t - this.ta - 0.25) * 4, 2)) * 0.18;
    this.camera.position.set(
      Math.cos(az) * Math.cos(el) * dist + Math.sin(t * 91) * shake,
      Math.sin(el) * dist + Math.cos(t * 77) * shake,
      Math.sin(az) * Math.cos(el) * dist,
    );
    this.camera.lookAt(0, 0, 0);
    this.camera.updateProjectionMatrix();
    this.U.uPixel.value = h * pixelRatio * 0.03 * (this.ctx.tier === "low" ? 1.3 : 1);
    renderer.setViewport(x, y, w, h);
    renderer.setScissor(x, y, w, h);
    renderer.setClearColor(this.clear, 1);
    renderer.clear();
    renderer.render(this.scene, this.camera);
  }

  dispose() {
    for (const d of this.disposables) d.dispose();
    for (const g of this.glyphs) g.dispose();
    this.disposables = [];
    this.glyphs = [];
    this.scene.clear();
  }
}
