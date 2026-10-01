// CRYSTALLIZATION (polycrystal): nucleation at the collision point. Each concept grows
// its own lattice GRAIN, rotated differently, inside the sector nearest to where it
// arrived. A growth front sweeps outward; behind it particles snap to their grain's
// lattice and bonds light up; the grain boundaries, where two concepts' orders
// disagree, stay molten and glow. A buckling wave runs through the solid.
// Lattice kind follows symmetry: cubic, hex-layered, fcc, or quasicrystal shells.

import * as THREE from "three";
import { World } from "../world";
import { COMMON_UNIFORMS, NOISE } from "../glsl";

const LATTICE = /* glsl */ `
uniform mat3 uGrain[3];
uniform vec3 uEntry[3];
const float LN=11.0;
vec3 latticeSite(vec4 r){
  vec3 q=floor(r.xyz*LN)-(LN-1.0)*0.5;
  if(uSym<3.5) return q;
  if(uSym<5.5) return vec3(q.x+0.5*mod(q.z,2.0), q.y, q.z*0.866);
  if(uSym<7.5) return q+0.5*step(0.5,r.w)*vec3(1.0,1.0,0.0);
  float i=floor(r.x*900.0); float gold=2.39996323; float z=1.0-fract(i*0.618034)*2.0;
  float rad=floor(r.y*6.0)+1.0; float s=sqrt(max(0.0,1.0-z*z));
  return vec3(cos(i*gold)*s, z, sin(i*gold)*s)*rad*0.9;
}
float latticeScale(){ return 0.36+0.08*uG0.y; }
float growthRadius(float te){ return pow(clamp(te/(uTe-uTa),0.0,1.5),0.8)*2.1; }
int grainOf(vec3 p){
  vec3 d=normalize(p+1e-4);
  float a=dot(d,uEntry[0]), b=dot(d,uEntry[1]), c=dot(d,uEntry[2]);
  return a>=b&&a>=c?0:(b>=c?1:2);
}
float boundaryDist(vec3 p){
  vec3 d=normalize(p+1e-4);
  float a=dot(d,uEntry[0]), b=dot(d,uEntry[1]), c=dot(d,uEntry[2]);
  float m=max(a,max(b,c)); float s=a+b+c-m-min(a,min(b,c));
  return m-s; // 0 on a boundary between the two strongest grains
}
vec3 buckle(vec3 s, float te){
  float d=length(s);
  return s+normalize(s+1e-4)*sin(d*2.1-te*(1.2+uG0.x))*0.11*uElastic*smoothstep(0.0,2.0,te)
          +vec3(0.0,sin(s.x*1.1+te*0.6)*0.06*uDistort,0.0);
}`;

const EMERGE = /* glsl */ `
${LATTICE}
vec3 emerge(float k, vec4 r, float idx, float te, inout vec3 col, inout float alpha, inout float size){
  int ki=int(k+0.5);
  vec3 site=uGrain[ki]*(latticeSite(r)*latticeScale());
  float gr=growthRadius(te);
  float d=length(site);
  vec3 hs=uHsl[ki];
  bool mine=grainOf(site)==ki && d<2.1;
  if(mine && d<gr){
    vec3 p=buckle(site,te);
    float front=exp(-pow((gr-d)*3.0,2.0));
    float edge=1.0-smoothstep(0.0,0.12,boundaryDist(site));
    col=hsl2rgb(vec3(hs.x,0.3+0.55*front,0.58+0.3*front))+front*0.4+edge*vec3(1.0,0.85,0.6)*0.5;
    alpha=0.55+front*0.6+edge*0.3; size=0.7+front*1.1+edge*0.6;
    return p;
  }
  // molten matter: rides the growth front, and pools along grain boundaries
  float a=r.x*6.2831853+te*(0.6+uCurl); float z=r.y*2.0-1.0; float s=sqrt(max(0.0,1.0-z*z));
  vec3 dir=vec3(cos(a)*s,z,sin(a)*s);
  float rad=min(gr+0.2+r.z*0.7, 2.5);
  vec3 p=dir*rad;
  p+=snoise3(p*1.3+te*0.3)*0.22*(0.4+uTurb);
  float edge=1.0-smoothstep(0.0,0.2,boundaryDist(p));
  col=mix(hsl2rgb(vec3(hs.x,hs.y,0.5)), vec3(1.0,0.8,0.55), edge*0.7);
  alpha=0.35+edge*0.5; size=0.5+edge*0.5;
  return p;
}`;

const BOND_VERT = /* glsl */ `
${COMMON_UNIFORMS}
attribute float aMid;
attribute float aK;
varying vec3 vCol; varying float vA;
${NOISE}
${LATTICE}
void main(){
  float te=max(uTime-uTa,0.0);
  float gr=growthRadius(te);
  vec3 p=buckle(position,te);
  float on=smoothstep(0.0,0.3,gr-aMid);
  float front=exp(-pow((gr-aMid)*3.0,2.0));
  vec3 hs=uHsl[int(aK+0.5)];
  vCol=hsl2rgb(vec3(hs.x,0.55,0.6))+front*0.7;
  vA=on*(0.22+front*0.8)*smoothstep(uTa,uTc,uTime);
  gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.0);
}`;

const BOND_FRAG = /* glsl */ `varying vec3 vCol; varying float vA; void main(){ gl_FragColor=vec4(vCol*vA,1.0); }`;

export class CrystalWorld extends World {
  build() {
    const g = this.genome;
    // one rotation per grain (concept), deterministic from the genome
    const grains = [0, 1, 2].map((k) => new THREE.Matrix3().setFromMatrix4(new THREE.Matrix4().makeRotationFromEuler(
      new THREE.Euler(g.params[k] * Math.PI + k * 0.7, g.params[k + 3] * Math.PI * 2 + k * 1.3, g.params[(k + 6) % 8] * 0.9))));
    const entries = g.bodies.map((b) => new THREE.Vector3(...b.entry).normalize());
    const extra = { uGrain: { value: grains }, uEntry: { value: entries } };
    this.particles(this.ctx.budget * g.particleCount, EMERGE, { extraUniforms: extra });
    if (g.symmetry >= 8) return; // quasicrystal shells: no periodic bonds

    const n = 11, half = (n - 1) / 2, scale = 0.36 + 0.08 * g.params[1], R = 2.1;
    const site = (i: number, j: number, k: number) => {
      const q = [i - half, j - half, k - half];
      if (g.symmetry >= 4 && g.symmetry < 6) return new THREE.Vector3(q[0] + 0.5 * (((k % 2) + 2) % 2), q[1], q[2] * 0.866);
      return new THREE.Vector3(q[0], q[1], q[2]);
    };
    const grainOf = (p: THREE.Vector3) => {
      const d = p.clone().normalize();
      const s = entries.map((e) => d.dot(e));
      return s[0] >= s[1] && s[0] >= s[2] ? 0 : s[1] >= s[2] ? 1 : 2;
    };
    const pos: number[] = [], mid: number[] = [], kk: number[] = [];
    const stride = this.ctx.tier === "low" ? 2 : 1;
    for (let gk = 0; gk < 3; gk++) {
      const M = grains[gk];
      for (let i = 0; i < n; i += stride) for (let j = 0; j < n; j += stride) for (let k = 0; k < n; k += stride) {
        const a = site(i, j, k).multiplyScalar(scale).applyMatrix3(M);
        if (a.length() > R || grainOf(a) !== gk) continue;
        for (const [di, dj, dk] of [[stride, 0, 0], [0, stride, 0], [0, 0, stride]]) {
          if (i + di >= n || j + dj >= n || k + dk >= n) continue;
          const b = site(i + di, j + dj, k + dk).multiplyScalar(scale).applyMatrix3(M);
          if (b.length() > R || grainOf(b) !== gk) continue;
          const m = a.clone().add(b).multiplyScalar(0.5).length();
          pos.push(a.x, a.y, a.z, b.x, b.y, b.z);
          mid.push(m, m);
          kk.push(gk, gk);
        }
      }
    }
    const geo = this.track(new THREE.BufferGeometry());
    geo.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
    geo.setAttribute("aMid", new THREE.Float32BufferAttribute(mid, 1));
    geo.setAttribute("aK", new THREE.Float32BufferAttribute(kk, 1));
    const mat = this.track(new THREE.ShaderMaterial({
      vertexShader: BOND_VERT, fragmentShader: BOND_FRAG, uniforms: { ...this.U, ...extra },
      transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
    }));
    const lines = new THREE.LineSegments(geo, mat);
    lines.frustumCulled = false;
    this.root.add(lines);
  }
}
