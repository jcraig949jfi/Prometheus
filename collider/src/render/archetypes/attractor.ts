// STRANGE_ATTRACTOR: the collision ignites a chaotic flow. A real attractor
// (Lorenz, Thomas, Aizawa, Halvorsen, Dadras, Rossler, Chen) is integrated on the CPU
// once, stored in a float texture, and three interleaved particle streams, one per
// concept, ride it on the GPU as luminous ribbons.

import * as THREE from "three";
import { World } from "../world";

type Sys = (p: number[], k: number[]) => number[];

const SYSTEMS: { name: string; dt: number; stride: number; start: number[]; f: (q: number) => Sys }[] = [
  { name: "lorenz", dt: 0.005, stride: 3, start: [0.1, 0, 0], f: (q) => ([x, y, z]) => [10 * (y - x), x * (24 + q * 8 - z) - y, x * y - (8 / 3) * z] },
  { name: "thomas", dt: 0.06, stride: 2, start: [0.1, 0, 0], f: (q) => ([x, y, z]) => { const b = 0.16 + q * 0.06; return [Math.sin(y) - b * x, Math.sin(z) - b * y, Math.sin(x) - b * z]; } },
  { name: "aizawa", dt: 0.01, stride: 3, start: [0.1, 0, 0], f: (q) => ([x, y, z]) => { const a = 0.95, b = 0.7, c = 0.6, d = 3.5, e = 0.25, f = 0.1 * (0.5 + q); return [(z - b) * x - d * y, d * x + (z - b) * y, c + a * z - (z * z * z) / 3 - (x * x + y * y) * (1 + e * z) + f * z * x * x * x]; } },
  { name: "halvorsen", dt: 0.005, stride: 3, start: [-1.48, -1.51, 2.04], f: (q) => ([x, y, z]) => { const a = 1.3 + q * 0.6; return [-a * x - 4 * y - 4 * z - y * y, -a * y - 4 * z - 4 * x - z * z, -a * z - 4 * x - 4 * y - x * x]; } },
  { name: "dadras", dt: 0.005, stride: 3, start: [1.1, 2.1, -2], f: (q) => ([x, y, z]) => { const a = 3, b = 2.7, c = 1.7 + q * 0.3, d = 2, e = 9; return [y - a * x + b * y * z, c * y - x * z + z, d * x * y - e * z]; } },
  { name: "rossler", dt: 0.02, stride: 3, start: [0.1, 0, 0], f: (q) => ([x, y, z]) => [-y - z, x + 0.2 * y, 0.2 + z * (x - (5 + q * 2))] },
  { name: "chen", dt: 0.002, stride: 4, start: [-0.1, 0.5, -0.6], f: (q) => ([x, y, z]) => { const a = 35 + q * 5, b = 3, c = 28; return [a * (y - x), (c - a) * x - x * z + c * y, x * y - b * z]; } },
];

export function integrateAttractor(index: number, q: number, n: number): { data: Float32Array<ArrayBuffer>; name: string } {
  const S = SYSTEMS[index % SYSTEMS.length];
  const f = S.f(q);
  let p = S.start.slice();
  const step = (p: number[]) => {
    const h = S.dt;
    const k1 = f(p, []);
    const k2 = f(p.map((v, i) => v + (h / 2) * k1[i]), []);
    const k3 = f(p.map((v, i) => v + (h / 2) * k2[i]), []);
    const k4 = f(p.map((v, i) => v + h * k3[i]), []);
    return p.map((v, i) => v + (h / 6) * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]));
  };
  for (let i = 0; i < 1500; i++) p = step(p);
  const pts = new Float32Array(new ArrayBuffer(n * 16));
  const mean = [0, 0, 0];
  for (let i = 0; i < n; i++) {
    for (let s = 0; s < S.stride; s++) p = step(p);
    if (!p.every(Number.isFinite)) p = S.start.slice();
    pts.set([p[0], p[1], p[2], 1], i * 4);
    mean[0] += p[0] / n; mean[1] += p[1] / n; mean[2] += p[2] / n;
  }
  let r = 1e-6;
  for (let i = 0; i < n; i++) {
    const dx = pts[i * 4] - mean[0], dy = pts[i * 4 + 1] - mean[1], dz = pts[i * 4 + 2] - mean[2];
    r = Math.max(r, Math.hypot(dx, dy, dz));
  }
  const sc = 2.7 / r;
  for (let i = 0; i < n; i++) {
    pts[i * 4] = (pts[i * 4] - mean[0]) * sc;
    pts[i * 4 + 1] = (pts[i * 4 + 1] - mean[1]) * sc;
    pts[i * 4 + 2] = (pts[i * 4 + 2] - mean[2]) * sc;
  }
  return { data: pts, name: S.name };
}

const EMERGE = /* glsl */ `
vec3 pathAt(float s){
  float f=fract(s)*(uPathN-2.0); float i0=floor(f); float fr=f-i0;
  float i1=i0+1.0;
  vec2 uv0=vec2((mod(i0,uPathW)+0.5)/uPathW,(floor(i0/uPathW)+0.5)/uPathH);
  vec2 uv1=vec2((mod(i1,uPathW)+0.5)/uPathW,(floor(i1/uPathW)+0.5)/uPathH);
  return mix(texture2D(uPath,uv0).xyz, texture2D(uPath,uv1).xyz, fr);
}
vec3 emerge(float k, vec4 r, float idx, float te, inout vec3 col, inout float alpha, inout float size){
  float speed=0.006+uG0.x*0.012;
  float s=idx*0.97+te*speed*(1.0+0.35*k)+k*0.013;
  vec3 p=pathAt(s);
  vec3 q=pathAt(s+0.0012);
  vec3 tang=normalize(q-p+1e-5);
  vec3 side=normalize(cross(tang,vec3(0.0,1.0,0.0))+1e-4);
  vec3 up=cross(side,tang);
  float ribbon=(k-1.0)*0.07*(1.0+uDistort)+(r.x-0.5)*0.035;
  p+=side*ribbon+up*(r.y-0.5)*0.03;
  float grow=smoothstep(0.0,uTe-uTa,te);
  p*=mix(0.08,1.0,grow*grow*(3.0-2.0*grow));
  float speedTint=clamp(length(q-p)*40.0,0.0,1.0);
  vec3 hs=uHsl[int(k)];
  col=hsl2rgb(vec3(fract(hs.x+0.06*sin(s*50.0)+0.08*speedTint), hs.y, 0.5+0.2*speedTint));
  alpha=0.75; size=0.62;
  return p;
}`;

export class AttractorWorld extends World {
  attractorName = "";
  build() {
    const W = 128, H = 64, N = W * H;
    const which = Math.floor(this.genome.params[5] * 7) % 7;
    const { data, name } = integrateAttractor(which + (this.genome.seed % 3 === 0 ? 1 : 0), this.genome.params[6], N);
    this.attractorName = name;
    const tex = this.track(new THREE.DataTexture(data, W, H, THREE.RGBAFormat, THREE.FloatType));
    tex.minFilter = THREE.NearestFilter;
    tex.magFilter = THREE.NearestFilter;
    tex.needsUpdate = true;
    this.particles(this.ctx.budget * this.genome.particleCount * 1.1, EMERGE, {
      extraDecl: "uniform sampler2D uPath; uniform float uPathN; uniform float uPathW; uniform float uPathH;",
      extraUniforms: {
        uPath: { value: tex }, uPathN: { value: N }, uPathW: { value: W }, uPathH: { value: H },
      },
    });
  }
}
