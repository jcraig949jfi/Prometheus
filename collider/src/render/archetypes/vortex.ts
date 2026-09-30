// VORTEX: the three bodies are captured into toroidal-poloidal flow. The attractor
// count sets how many interlocking cores; the axial field fires particle jets up
// the core; turbulence roughens the tubes; twist (order signal) sets handedness.

import { World } from "../world";

const EMERGE = /* glsl */ `
vec3 emerge(float k, vec4 r, float idx, float te, inout vec3 col, inout float alpha, inout float size){
  float cores=uAttr;
  float c=floor(fract(r.w*7.13)*cores);
  float ang0=c/cores*6.2831853;
  vec3 center=cores>1.5 ? vec3(cos(ang0),0.25*sin(ang0*2.0),sin(ang0))*(1.25+0.5*uG0.y) : vec3(0.0);
  float grow=smoothstep(0.0,uTe-uTa,te);
  float R=(0.7+r.z*1.4)*(0.55+0.45*grow)/sqrt(max(1.0,cores*0.6));
  float rr=(0.04+pow(r.y,3.0)*0.55)*(0.5+uG0.z);
  float dir=uTwist>=0.0?1.0:-1.0;
  float speed=(0.5+uCurl*1.6)/(rr+0.25);
  float th=r.x*6.2831853+te*speed*0.5*dir;
  float ph=r.y*97.0+te*speed*(1.3+uG1.x);
  vec3 p=vec3((R+rr*cos(ph))*cos(th), rr*sin(ph), (R+rr*cos(ph))*sin(th));
  vec3 hs=uHsl[int(k)];
  float jet=step(fract(r.w*13.7), 0.06+uAxial*0.2);
  if(jet>0.5){
    float h=fract(r.x+te*(0.3+uG1.y*0.4))*2.0-1.0;
    float spread=0.03+abs(h)*0.2;
    p=vec3(cos(r.y*80.0+te)*spread, h*(2.2+uAxial*2.2), sin(r.y*80.0+te)*spread);
    col=mix(hsl2rgb(vec3(hs.x,0.9,0.72)), vec3(1.0), 0.45);
    alpha=1.0-abs(h)*0.85; size=0.75;
  } else {
    float lum=0.42+0.38*(1.0-rr);
    col=hsl2rgb(vec3(fract(hs.x+rr*0.18*uDistort+0.04*sin(th*uSym)), hs.y, lum));
    alpha=0.85; size=1.0-rr*0.4;
  }
  p=rotX(ang0*0.7+uG0.w*1.5)*rotZ(ang0*0.5)*p;
  p+=snoise3(p*0.6+vec3(0.0,te*0.15,0.0))*uTurb*0.22*grow;
  return center+p*(0.2+0.8*grow);
}`;

export class VortexWorld extends World {
  build() {
    this.particles(this.ctx.budget * this.genome.particleCount, EMERGE);
  }
}
