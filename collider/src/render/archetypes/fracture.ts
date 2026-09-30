// FRACTURE: the bodies fuse into a single glass shell; at the fracture threshold the
// shell cracks with a flash and shards fly out, decelerate, and hang as a frozen
// explosion that slowly breathes back toward reassembly. Dust sprays from the cracks.

import * as THREE from "three";
import { World } from "../world";
import { COMMON_UNIFORMS, NOISE } from "../glsl";

const CRACK = /* glsl */ `
float crackTime(){ return (uTe-uTa)*(0.3+0.45*uFrac); }
`;

const EMERGE = /* glsl */ `
${CRACK}
vec3 emerge(float k, vec4 r, float idx, float te, inout vec3 col, inout float alpha, inout float size){
  float u=r.x*6.2831853; float z=r.y*2.0-1.0; float s=sqrt(max(0.0,1.0-z*z));
  vec3 dir=vec3(cos(u)*s,z,sin(u)*s);
  float crack=crackTime();
  float after=max(te-crack,0.0);
  vec3 hs=uHsl[int(k)];
  if(te<crack){
    col=hsl2rgb(vec3(hs.x,0.6,0.6))*(0.6+0.8*smoothstep(crack*0.6,crack,te)); alpha=0.6; size=0.7;
    return dir*1.3*(0.92+0.08*r.z)+snoise3(dir*3.0+te)*0.03;
  }
  float travel=(1.0-exp(-after*(0.8+r.z)))*(0.8+r.z*3.2);
  vec3 p=dir*(1.35+travel*0.7)+snoise3(dir*2.0+after*0.2)*0.25*uTurb*min(after,1.0);
  col=mix(vec3(1.0,0.9,0.75), hsl2rgb(vec3(hs.x,hs.y,0.6)), smoothstep(0.0,1.5,after));
  alpha=exp(-after*0.25)*0.9+0.08; size=0.55;
  return p;
}`;

const SHARD_VERT = /* glsl */ `
${COMMON_UNIFORMS}
attribute vec3 aDir; attribute vec4 aR; attribute float aK;
varying vec3 vN; varying vec3 vCol; varying float vGlow; varying vec3 vView;
${NOISE}
${CRACK}
mat3 rodrigues(vec3 a, float ang){
  float c=cos(ang), s=sin(ang), t=1.0-c;
  return mat3(t*a.x*a.x+c, t*a.x*a.y+s*a.z, t*a.x*a.z-s*a.y,
              t*a.x*a.y-s*a.z, t*a.y*a.y+c, t*a.y*a.z+s*a.x,
              t*a.x*a.z+s*a.y, t*a.y*a.z-s*a.x, t*a.z*a.z+c);
}
void main(){
  float te=max(uTime-uTa,0.0);
  float show=smoothstep(uTa-0.1,uTc,uTime);
  float crack=crackTime();
  float after=max(te-crack,0.0);
  float fly=1.0-exp(-after*(1.1+uG0.x*1.6));
  float dist=1.35+fly*(0.4+aR.x*1.5)*(0.6+uG1.z*0.6);
  int k=int(aK+0.5);
  vec3 shell=aDir*dist;
  vec3 centre=mix(uBody[k]+aDir*0.35, shell, smoothstep(uTa-0.2,uTc+0.3,uTime));
  float breathe=(sin(after*0.35-1.57)*0.5+0.5)*fly;
  centre*=1.0-0.18*breathe;
  float ang=after*(0.5+aR.y*2.2)*(1.0-0.6*fly)+aR.z*6.28;
  mat3 R=rodrigues(normalize(aR.xyz-0.5+1e-3),ang);
  float sz=(0.05+aR.w*0.08)*(0.7+uG0.y*0.6)*show;
  vec3 local=R*(position*vec3(1.0,mix(0.35,1.0,fly),1.0))*sz;
  vec3 wp=centre+local;
  vN=normalize(normalMatrix*(R*normal));
  vec4 mv=modelViewMatrix*vec4(wp,1.0);
  vView=-mv.xyz;
  vec3 hs=uHsl[k];
  vCol=hsl2rgb(vec3(hs.x,hs.y*0.6,0.5));
  vGlow=exp(-pow((te-crack)*3.5,2.0))*2.5+step(0.0,te-crack)*exp(-after*0.9)*0.7+(1.0-step(0.0,te-crack))*smoothstep(crack*0.5,crack,te)*0.6;
  gl_Position=projectionMatrix*mv;
}`;

const SHARD_FRAG = /* glsl */ `
varying vec3 vN; varying vec3 vCol; varying float vGlow; varying vec3 vView;
void main(){
  vec3 n=normalize(vN); vec3 v=normalize(vView);
  float fres=pow(1.0-abs(dot(n,v)),2.2);
  float lam=max(dot(n,normalize(vec3(0.4,0.8,0.5))),0.0);
  vec3 c=vCol*(0.05+0.3*lam)+fres*mix(vCol,vec3(0.9,0.95,1.0),0.35)*1.4+vGlow*vec3(1.0,0.86,0.62);
  gl_FragColor=vec4(c,0.35+0.6*fres+0.4*min(vGlow,1.0));
}`;

export class FractureWorld extends World {
  build() {
    this.particles(this.ctx.budget * this.genome.particleCount * 0.7, EMERGE);
    const n = this.ctx.tier === "high" ? 1400 : this.ctx.tier === "mid" ? 800 : 420;
    const base = new THREE.TetrahedronGeometry(1, 0).toNonIndexed();
    base.computeVertexNormals();
    const geo = this.track(new THREE.InstancedBufferGeometry());
    geo.setAttribute("position", base.getAttribute("position"));
    geo.setAttribute("normal", base.getAttribute("normal"));
    base.dispose();
    const dir = new Float32Array(n * 3), r = new Float32Array(n * 4), k = new Float32Array(n);
    let s = (this.genome.seed * 2654435761) >>> 0;
    const rnd = () => ((s = (Math.imul(s ^ (s >>> 15), 2246822519) + 0x6d2b79f5) >>> 0) / 4294967296);
    const golden = Math.PI * (3 - Math.sqrt(5));
    for (let i = 0; i < n; i++) {
      const y = 1 - (i / (n - 1)) * 2, rad = Math.sqrt(1 - y * y), th = golden * i;
      dir.set([Math.cos(th) * rad, y, Math.sin(th) * rad], i * 3);
      for (let j = 0; j < 4; j++) r[i * 4 + j] = rnd();
      k[i] = i % 3;
    }
    geo.setAttribute("aDir", new THREE.InstancedBufferAttribute(dir, 3));
    geo.setAttribute("aR", new THREE.InstancedBufferAttribute(r, 4));
    geo.setAttribute("aK", new THREE.InstancedBufferAttribute(k, 1));
    geo.instanceCount = n;
    const mat = this.track(new THREE.ShaderMaterial({
      vertexShader: SHARD_VERT, fragmentShader: SHARD_FRAG, uniforms: this.U,
      transparent: true, depthWrite: true, side: THREE.DoubleSide,
    }));
    const mesh = new THREE.Mesh(geo, mat);
    mesh.frustumCulled = false;
    this.root.add(mesh);
  }
}
