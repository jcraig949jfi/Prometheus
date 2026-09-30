// REACTION_DIFFUSION: the collision seeds a Gray-Scott reaction-diffusion system that
// runs on the GPU (ping-pong render targets) and grows across a living membrane. Each
// concept seeds one region; a diffusing hue vector carries concept identity, so the
// pattern shows where the three concepts' "chemistry" meets and mixes.
// Deterministic: sim steps are a fixed function of elapsed time, not of frame rate.

import * as THREE from "three";
import { World } from "../world";
import { COMMON_UNIFORMS } from "../glsl";

const REGIMES: [number, number][] = [
  [0.0545, 0.062], // coral
  [0.037, 0.06], // spots
  [0.029, 0.057], // labyrinth
  [0.039, 0.058], // worms
  [0.0367, 0.0649], // mitosis
  [0.026, 0.051], // chaos / waves
];

const QUAD_VERT = /* glsl */ `varying vec2 vUv; void main(){ vUv=uv; gl_Position=vec4(position.xy,0.0,1.0); }`;

const SIM_FRAG = /* glsl */ `
uniform sampler2D uState; uniform vec2 uTexel; uniform float uF; uniform float uKill;
varying vec2 vUv;
void main(){
  vec4 c=texture2D(uState,vUv);
  vec4 lap=-c;
  lap+=0.2*(texture2D(uState,vUv+vec2(uTexel.x,0.0))+texture2D(uState,vUv-vec2(uTexel.x,0.0))
           +texture2D(uState,vUv+vec2(0.0,uTexel.y))+texture2D(uState,vUv-vec2(0.0,uTexel.y)));
  lap+=0.05*(texture2D(uState,vUv+uTexel)+texture2D(uState,vUv-uTexel)
            +texture2D(uState,vUv+vec2(uTexel.x,-uTexel.y))+texture2D(uState,vUv+vec2(-uTexel.x,uTexel.y)));
  float A=c.r, B=c.g;
  float abb=A*B*B;
  float nA=A+(1.0*lap.r-abb+uF*(1.0-A));
  float nB=B+(0.5*lap.g+abb-(uKill+uF)*B);
  vec2 hue=c.ba+0.22*lap.ba*step(0.02,B+0.02);
  gl_FragColor=vec4(clamp(nA,0.0,1.0),clamp(nB,0.0,1.0),hue);
}`;

const SURF_VERT = /* glsl */ `
${COMMON_UNIFORMS}
uniform sampler2D uState;
varying vec3 vW; varying vec2 vUv2; varying float vB; varying vec3 vView;
void main(){
  vec3 n=normalize(position);
  vec2 uv=vec2(atan(n.z,n.x)/6.2831853+0.5, acos(clamp(n.y,-1.0,1.0))/3.14159265);
  vec4 st=texture2D(uState,uv);
  float grow=smoothstep(uTa,uTe,uTime);
  float disp=st.g*(0.22+0.45*uElastic)+sin(uTime*0.7+n.y*4.0)*0.02;
  vec3 p=n*(1.72+disp)*mix(0.05,1.0,grow*grow*(3.0-2.0*grow));
  vUv2=uv; vB=st.g;
  vec4 w=modelMatrix*vec4(p,1.0); vW=w.xyz;
  vec4 mv=viewMatrix*w; vView=-mv.xyz;
  gl_Position=projectionMatrix*mv;
}`;

const SURF_FRAG = /* glsl */ `
uniform sampler2D uState; uniform vec3 uHsl[3]; uniform float uTime;
varying vec3 vW; varying vec2 vUv2; varying float vB; varying vec3 vView;
vec3 hsl2rgb(vec3 c){ vec3 rgb=clamp(abs(mod(c.x*6.0+vec3(0.0,4.0,2.0),6.0)-3.0)-1.0,0.0,1.0); return c.z+c.y*(rgb-0.5)*(1.0-abs(2.0*c.z-1.0)); }
void main(){
  vec4 st=texture2D(uState,vUv2);
  vec3 n=normalize(cross(dFdx(vW),dFdy(vW)));
  vec3 v=normalize(vView);
  float fres=pow(1.0-abs(dot(n,v)),2.0);
  float h=atan(st.a,st.b)/6.2831853;
  float hueStrength=clamp(length(st.ba),0.0,1.0);
  vec3 tint=hsl2rgb(vec3(fract(h+1.0),0.75,0.55));
  vec3 base=mix(vec3(0.02,0.025,0.04), tint*0.35, hueStrength*0.6);
  float edge=smoothstep(0.08,0.32,st.g);
  vec3 c=mix(base, tint*1.3+0.1, edge);
  c+=fres*mix(vec3(0.3,0.4,0.6),tint,0.6)*0.9;
  c+=smoothstep(0.25,0.4,st.g)*0.25;
  gl_FragColor=vec4(c,1.0);
}`;

const EMERGE = /* glsl */ `
vec3 emerge(float k, vec4 r, float idx, float te, inout vec3 col, inout float alpha, inout float size){
  float u=r.x*6.2831853; float z=r.y*2.0-1.0; float s=sqrt(max(0.0,1.0-z*z));
  vec3 dir=vec3(cos(u)*s,z,sin(u)*s);
  float grow=smoothstep(0.0,uTe-uTa,te);
  vec3 hs=uHsl[int(k)];
  if(fract(r.w*9.1)<0.18){
    float ang=u+te*(0.2+0.3*r.z);
    vec3 p=vec3(cos(ang),(r.y-0.5)*0.35,sin(ang))*(2.3+r.z*1.1);
    p=rotX(0.4+k*0.9)*p;
    col=hsl2rgb(vec3(hs.x,hs.y,0.62)); alpha=0.7*grow; size=0.7;
    return p;
  }
  col=hsl2rgb(vec3(hs.x,hs.y,0.7)); alpha=1.0-grow*0.95; size=0.8;
  return dir*1.8;
}`;

export class ReactionWorld extends World {
  private rt!: [THREE.WebGLRenderTarget, THREE.WebGLRenderTarget];
  private simScene = new THREE.Scene();
  private simCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
  private simMat!: THREE.ShaderMaterial;
  private surfMat!: THREE.ShaderMaterial;
  private steps = 0;
  private cur = 0;
  private stepsPerSecond = 1000;

  build() {
    const size = this.ctx.tier === "high" ? 256 : this.ctx.tier === "mid" ? 192 : 128;
    // Full float is required: half-float rounds away Gray-Scott's small per-step
    // updates near A=1 and the pattern freezes (measured: identical state after
    // 1,900 extra steps). Linear filtering of float targets needs an extension.
    const gl = this.ctx.renderer.getContext();
    const linear = !!gl.getExtension("OES_texture_float_linear");
    const filt = linear ? THREE.LinearFilter : THREE.NearestFilter;
    const mk = () => this.track(new THREE.WebGLRenderTarget(size, size, {
      type: THREE.FloatType, format: THREE.RGBAFormat, minFilter: filt, magFilter: filt,
      wrapS: THREE.RepeatWrapping, wrapT: THREE.ClampToEdgeWrapping, depthBuffer: false,
    }));
    this.rt = [mk(), mk()];
    const g = this.genome;
    const [F, K] = REGIMES[Math.floor(g.params[3] * REGIMES.length) % REGIMES.length];
    // initial state: A=1, B=0, three concept seeds + symmetry-driven satellite seeds
    const data = new Float32Array(size * size * 4);
    for (let i = 0; i < size * size; i++) data.set([1, 0, 0, 0], i * 4);
    const seed = (u: number, v: number, rad: number, hue: number) => {
      const cx = u * size, cy = v * size;
      for (let y = Math.floor(cy - rad); y <= cy + rad; y++) for (let x = Math.floor(cx - rad); x <= cx + rad; x++) {
        if ((x - cx) ** 2 + (y - cy) ** 2 > rad * rad || y < 0 || y >= size) continue;
        const xi = ((x % size) + size) % size;
        const o = (y * size + xi) * 4;
        data[o] = 0.5; data[o + 1] = 0.25;
        data[o + 2] = Math.cos(hue * Math.PI * 2); data[o + 3] = Math.sin(hue * Math.PI * 2);
      }
    };
    g.bodies.forEach((b) => {
      const [x, y, z] = b.entry;
      seed(Math.atan2(z, x) / (Math.PI * 2) + 0.5, Math.acos(Math.max(-1, Math.min(1, y))) / Math.PI, size * 0.07, b.hue);
    });
    let s = g.seed >>> 0;
    const rnd = () => ((s = (Math.imul(s ^ (s >>> 15), 2246822519) + 0x6d2b79f5) >>> 0) / 4294967296);
    for (let i = 0; i < g.symmetry * 5; i++) seed(rnd(), 0.15 + rnd() * 0.7, size * 0.022, g.bodies[i % 3].hue);
    const init = this.track(new THREE.DataTexture(data, size, size, THREE.RGBAFormat, THREE.FloatType));
    init.needsUpdate = true;
    this.simMat = this.track(new THREE.ShaderMaterial({
      vertexShader: QUAD_VERT, fragmentShader: SIM_FRAG,
      uniforms: { uState: { value: init }, uTexel: { value: new THREE.Vector2(1 / size, 1 / size) }, uF: { value: F }, uKill: { value: K } },
    }));
    const quad = new THREE.Mesh(this.track(new THREE.PlaneGeometry(2, 2)), this.simMat);
    this.simScene.add(quad);
    this.initTex = init;

    const detail = this.ctx.tier === "high" ? 48 : this.ctx.tier === "mid" ? 32 : 20;
    const sphere = this.track(new THREE.IcosahedronGeometry(1, detail));
    this.surfMat = this.track(new THREE.ShaderMaterial({
      vertexShader: SURF_VERT, fragmentShader: SURF_FRAG,
      uniforms: { ...this.U, uState: { value: this.rt[0].texture } },
    }));
    const mesh = new THREE.Mesh(sphere, this.surfMat);
    mesh.frustumCulled = false;
    this.root.add(mesh);
    this.particles(this.ctx.budget * this.genome.particleCount * 0.45, EMERGE);
  }

  private initTex!: THREE.DataTexture;
  private primed = false;

  preRender(renderer: THREE.WebGLRenderer) {
    const te = Math.max(0, this.t - this.ta);
    const target = Math.floor(te * this.stepsPerSecond);
    const prevScissor = renderer.getScissorTest();
    renderer.setScissorTest(false);
    if (!this.primed) {
      this.simMat.uniforms.uState.value = this.initTex;
      renderer.setRenderTarget(this.rt[0]);
      renderer.render(this.simScene, this.simCam);
      this.cur = 0;
      this.primed = true;
    }
    let budget = 18; // at most 14 sim steps per frame; never stall
    while (this.steps < target && budget-- > 0) {
      const src = this.rt[this.cur], dst = this.rt[1 - this.cur];
      this.simMat.uniforms.uState.value = src.texture;
      renderer.setRenderTarget(dst);
      renderer.render(this.simScene, this.simCam);
      this.cur = 1 - this.cur;
      this.steps++;
    }
    renderer.setRenderTarget(null);
    renderer.setScissorTest(prevScissor);
    this.surfMat.uniforms.uState.value = this.rt[this.cur].texture;
  }
}
