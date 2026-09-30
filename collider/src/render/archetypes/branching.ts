// BRANCHING_GROWTH: after the collision, three lineages (one per concept) grow out of
// the impact point: recursive branching with the genome's branching factor, a spread
// set by symmetry, twist-driven phyllotaxis and tropism toward the other lineages.
// Growth is revealed segment by segment on the GPU; sap particles flow along born
// branches and spores leave the tips.

import * as THREE from "three";
import { World } from "../world";
import { COMMON_UNIFORMS, NOISE } from "../glsl";

interface Seg { a: THREE.Vector3; b: THREE.Vector3; birth: number; dur: number; depth: number; k: number; tip: boolean }

function growTree(g: { seed: number; branchingFactor: number; symmetry: number; twist: number; params: number[] }, budget: number): Seg[] {
  let s = (g.seed ^ 0xa5a5a5a5) >>> 0;
  const rnd = () => ((s = (Math.imul(s ^ (s >>> 15), 2246822519) + 0x6d2b79f5) >>> 0) / 4294967296);
  const b = g.branchingFactor;
  let depth = 1;
  while (3 * ((Math.pow(b, depth + 2) - 1) / (b - 1)) < budget && depth < 9) depth++;
  const spread = 0.35 + (g.symmetry / 8) * 0.55;
  const decay = 0.62 + g.params[2] * 0.2;
  const speed = 1.1 + g.params[1] * 1.2;
  const tropism = (g.params[4] - 0.5) * 0.8;
  const segs: Seg[] = [];
  const up = new THREE.Vector3(0, 1, 0);
  const grow = (p: THREE.Vector3, dir: THREE.Vector3, len: number, d: number, k: number, t0: number) => {
    const end = p.clone().addScaledVector(dir, len);
    const dur = len / speed;
    segs.push({ a: p, b: end, birth: t0, dur, depth: d, k, tip: d === depth });
    if (d === depth || segs.length > budget) return;
    const perp = new THREE.Vector3().crossVectors(dir, Math.abs(dir.y) < 0.9 ? up : new THREE.Vector3(1, 0, 0)).normalize();
    const n = b - (rnd() < 0.25 ? 1 : 0);
    for (let c = 0; c < n; c++) {
      const nd = dir.clone()
        .applyAxisAngle(perp, spread * (0.6 + rnd() * 0.8))
        .applyAxisAngle(dir, c * 2.39996 + g.twist * 2 + rnd() * 0.4);
      // tropism: lean toward/away from the vertical and outward
      nd.addScaledVector(up, tropism * 0.4).addScaledVector(end.clone().normalize(), 0.25).normalize();
      grow(end, nd, len * decay * (0.85 + rnd() * 0.3), d + 1, k, t0 + dur);
    }
  };
  for (let k = 0; k < 3; k++) {
    const a = (k / 3) * Math.PI * 2 + g.twist;
    const dir = new THREE.Vector3(Math.cos(a) * 0.8, 0.35 + rnd() * 0.3, Math.sin(a) * 0.8).normalize();
    grow(new THREE.Vector3(0, 0, 0), dir, 1.0 + g.params[0] * 0.5, 1, k, 0);
  }
  return segs;
}

const EMERGE = /* glsl */ `
vec3 emerge(float k, vec4 r, float idx, float te, inout vec3 col, inout float alpha, inout float size){
  float born=smoothstep(aSegBirth, aSegBirth+aSegDur, te*1.0);
  vec3 hs=uHsl[int(k)];
  if(aSegTip>0.5 && fract(r.w*7.7)<0.5){
    float age=max(te-aSegBirth-aSegDur,0.0);
    vec3 d=normalize(aSegB-aSegA+1e-4);
    vec3 p=aSegB+(d*0.6+snoise3(aSegB*2.0+age*0.3)*0.5)*age*0.25*(0.4+r.z);
    col=hsl2rgb(vec3(fract(hs.x+0.1),hs.y,0.7)); alpha=step(0.001,age)*exp(-age*0.12)*0.9; size=0.6;
    return p;
  }
  float f=fract(r.x+te*(0.25+0.3*r.z));
  vec3 p=mix(aSegA,mix(aSegA,aSegB,born),f);
  p+=vec3(sin(uTime*0.8+aSegDepth+p.x*2.0),0.0,cos(uTime*0.7+aSegDepth))*aSegDepth*0.012*uElastic;
  col=hsl2rgb(vec3(hs.x,hs.y,0.55+0.25*(1.0-born)));
  alpha=step(0.001,born)*0.85; size=0.55+0.4*(1.0-born);
  return p;
}`;

const LINE_VERT = /* glsl */ `
${COMMON_UNIFORMS}
attribute vec3 aStart; attribute float aT; attribute float aBirth; attribute float aDur; attribute float aDepth; attribute float aK;
varying vec3 vCol; varying float vA;
${NOISE}
void main(){
  float te=max(uTime-uTa,0.0);
  float f=clamp((te-aBirth)/aDur,0.0,1.0);
  vec3 p=aT<0.5?aStart:mix(aStart,position,f);
  p+=vec3(sin(uTime*0.8+aDepth+p.x*2.0),0.0,cos(uTime*0.7+aDepth))*aDepth*0.012*uElastic;
  vec3 hs=uHsl[int(aK+0.5)];
  float tipGlow=(f>0.0&&f<1.0)?1.0:0.0;
  vCol=hsl2rgb(vec3(fract(hs.x+aDepth*0.025),min(1.0,hs.y*1.1),0.42+0.03*aDepth))*0.8+tipGlow*0.5;
  vA=step(0.0001,f)*(0.75-aDepth*0.05)*smoothstep(uTa,uTc,uTime);
  gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.0);
}`;

const LINE_FRAG = /* glsl */ `varying vec3 vCol; varying float vA; void main(){ gl_FragColor=vec4(vCol*vA,1.0); }`;

export class BranchingWorld extends World {
  build() {
    const segBudget = this.ctx.tier === "high" ? 5200 : this.ctx.tier === "mid" ? 2800 : 1400;
    const segs = growTree(this.genome, segBudget);
    const maxBirth = Math.max(...segs.map((s) => s.birth + s.dur));
    const scale = (this.te - this.ta) * 0.95 / maxBirth; // finish growing by end of emergence
    for (const s of segs) { s.birth *= scale; s.dur *= scale; }
    // center the tree and normalize it into a bounded radius
    const c = new THREE.Vector3();
    for (const s of segs) c.addScaledVector(s.a.clone().add(s.b), 0.5 / segs.length);
    let rmax = 1e-6;
    for (const s of segs) { s.a.sub(c); s.b.sub(c); rmax = Math.max(rmax, s.a.length(), s.b.length()); }
    const k = 2.5 / rmax;
    for (const s of segs) { s.a.multiplyScalar(k); s.b.multiplyScalar(k); }

    const pos: number[] = [], st: number[] = [], tt: number[] = [], bb: number[] = [], du: number[] = [], de: number[] = [], kk: number[] = [];
    for (const s of segs) {
      for (const T of [0, 1]) {
        const p = T === 0 ? s.a : s.b;
        pos.push(p.x, p.y, p.z); st.push(s.a.x, s.a.y, s.a.z); tt.push(T); bb.push(s.birth); du.push(s.dur); de.push(s.depth); kk.push(s.k);
      }
    }
    const geo = this.track(new THREE.BufferGeometry());
    geo.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
    geo.setAttribute("aStart", new THREE.Float32BufferAttribute(st, 3));
    geo.setAttribute("aT", new THREE.Float32BufferAttribute(tt, 1));
    geo.setAttribute("aBirth", new THREE.Float32BufferAttribute(bb, 1));
    geo.setAttribute("aDur", new THREE.Float32BufferAttribute(du, 1));
    geo.setAttribute("aDepth", new THREE.Float32BufferAttribute(de, 1));
    geo.setAttribute("aK", new THREE.Float32BufferAttribute(kk, 1));
    const mat = this.track(new THREE.ShaderMaterial({
      vertexShader: LINE_VERT, fragmentShader: LINE_FRAG, uniforms: this.U,
      transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
    }));
    const lines = new THREE.LineSegments(geo, mat);
    lines.frustumCulled = false;
    this.root.add(lines);

    // particles assigned to segments of their own lineage
    const n = Math.floor(this.ctx.budget * this.genome.particleCount * 0.8);
    const byK: Seg[][] = [[], [], []];
    for (const s of segs) byK[s.k].push(s);
    const A = new Float32Array(n * 3), B = new Float32Array(n * 3), Bi = new Float32Array(n), Du = new Float32Array(n), De = new Float32Array(n), Tp = new Float32Array(n);
    let s0 = (this.genome.seed * 747796405) >>> 0;
    const rnd = () => ((s0 = (Math.imul(s0 ^ (s0 >>> 15), 2246822519) + 0x6d2b79f5) >>> 0) / 4294967296);
    for (let i = 0; i < n; i++) {
      const list = byK[i % 3];
      const sg = list[Math.floor(rnd() * list.length)];
      A.set([sg.a.x, sg.a.y, sg.a.z], i * 3); B.set([sg.b.x, sg.b.y, sg.b.z], i * 3);
      Bi[i] = sg.birth; Du[i] = sg.dur; De[i] = sg.depth; Tp[i] = sg.tip ? 1 : 0;
    }
    this.particles(n, EMERGE, {
      extraDecl: "attribute vec3 aSegA; attribute vec3 aSegB; attribute float aSegBirth; attribute float aSegDur; attribute float aSegDepth; attribute float aSegTip;",
      extraAttrs: {
        aSegA: new THREE.BufferAttribute(A, 3), aSegB: new THREE.BufferAttribute(B, 3),
        aSegBirth: new THREE.BufferAttribute(Bi, 1), aSegDur: new THREE.BufferAttribute(Du, 1),
        aSegDepth: new THREE.BufferAttribute(De, 1), aSegTip: new THREE.BufferAttribute(Tp, 1),
      },
    });
  }
}
