// DIMENSIONAL_FOLD: the collision opens a fourth dimension. Particles are placed on
// fibres of the Hopf fibration of S^3 (every fibre a great circle, every pair
// linked), the whole 3-sphere rotates in the xw and yz planes, and it is
// stereographically projected into view. It begins collapsed onto a flat 3D slice
// and unfolds as the emergence proceeds.

import { World } from "../world";

const EMERGE = /* glsl */ `
vec3 emerge(float k, vec4 r, float idx, float te, inout vec3 col, inout float alpha, inout float size){
  float bands=3.0+floor(uG0.x*4.0);
  float band=floor(r.x*bands);
  float theta=(band+0.5)/bands*3.14159*0.88+0.06;
  float fibres=16.0+uSym*4.0;
  float phi=floor(r.y*fibres)/fibres*6.2831853+k*0.33;
  float psi=r.z*6.2831853+te*(0.22+uG0.y*0.4);
  vec4 q=vec4(cos(theta*0.5)*cos(psi+phi), cos(theta*0.5)*sin(psi+phi), sin(theta*0.5)*cos(psi), sin(theta*0.5)*sin(psi));
  float a=te*(0.11+uG1.x*0.18)+uTwist;
  float b=te*(0.07+uG1.y*0.14);
  q=vec4(q.x*cos(a)-q.w*sin(a), q.y*cos(b)-q.z*sin(b), q.y*sin(b)+q.z*cos(b), q.x*sin(a)+q.w*cos(a));
  vec3 p=q.xyz/max(0.09,1.0-q.w)*1.05;
  float len=length(p);
  p*=min(1.0,5.2/max(len,1e-3));
  float grow=smoothstep(0.0,uTe-uTa,te);
  vec3 flat3=normalize(q.xyz+1e-4)*1.5;
  p=mix(flat3,p,grow*grow*(3.0-2.0*grow));
  vec3 hs=uHsl[int(k)];
  float nearPole=smoothstep(2.5,5.2,len);
  col=hsl2rgb(vec3(fract(hs.x+band/bands*0.22*(0.5+uDistort)+phi*0.015), hs.y, 0.55+0.15*(1.0-nearPole)));
  alpha=0.82*(1.0-0.6*nearPole); size=0.6+0.5*nearPole;
  return p;
}`;

export class FoldWorld extends World {
  build() {
    this.particles(this.ctx.budget * this.genome.particleCount, EMERGE);
  }
}
