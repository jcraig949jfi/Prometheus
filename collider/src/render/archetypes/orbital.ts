// ORBITAL_CAPTURE: the three bodies are captured into a periodic three-body
// choreography (figure-eight, Lagrange circle, rosette, or trefoil, by symmetry).
// Each drags a Keplerian ring system that contracts as it is captured, and the
// shared orbit is written in luminous trails behind them.

import { World } from "../world";

const EMERGE = /* glsl */ `
vec3 choreo(float s){
  float m=mod(uSym,4.0);
  vec3 p;
  if(m<0.5) p=vec3(sin(s),0.5*sin(2.0*s),0.0)*2.3;
  else if(m<1.5) p=vec3(cos(s),0.0,sin(s))*1.9;
  else if(m<2.5) p=vec3(sin(s)+0.45*sin(3.0*s),0.0,cos(s)-0.45*cos(3.0*s))*1.55;
  else p=vec3(sin(s)+2.0*sin(2.0*s),cos(s)-2.0*cos(2.0*s),-sin(3.0*s))*0.6;
  return rotX(0.5+uG0.w)*rotZ(uTwist*0.4)*p;
}
vec3 emerge(float k, vec4 r, float idx, float te, inout vec3 col, inout float alpha, inout float size){
  float grow=smoothstep(0.0,uTe-uTa,te);
  float omega=0.32+uG0.x*0.35;
  float dir=uTwist>=0.0?1.0:-1.0;
  float sb=te*omega*dir+k*2.0943951;
  float sc=mix(0.2,1.0,grow);
  vec3 body=choreo(sb)*sc;
  vec3 hs=uHsl[int(k)];
  float role=fract(r.w*5.37);
  if(role<0.025){
    col=vec3(0.9)+hsl2rgb(vec3(hs.x,0.8,0.7)); size=3.5; alpha=1.0;
    return body+(r.xyz-0.5)*0.05;
  }
  if(role<0.55){
    float rr=0.16+pow(r.x,1.5)*0.72*(0.6+uG0.y);
    float capture=1.0+2.4*exp(-te*0.9);
    float ang=r.y*6.2831853+te*(0.9+uCurl)*0.3/pow(rr,1.5);
    vec3 ring=vec3(cos(ang),(r.z-0.5)*0.04,sin(ang))*rr*capture;
    ring=rotX(k*1.1+uG1.x*2.0)*rotZ(k*0.7)*ring;
    col=hsl2rgb(vec3(fract(hs.x+0.05*sin(ang*3.0)),hs.y,0.52+0.28*(1.0-rr))); alpha=0.8; size=0.7;
    return body+ring;
  }
  float lag=r.x*(2.0+uG1.y*2.2);
  vec3 p=choreo(sb-lag*dir)*sc+(r.yzw-0.5)*0.025*(1.0+lag);
  col=hsl2rgb(vec3(hs.x,hs.y,0.62)); alpha=(1.0-r.x)*0.95; size=0.62*(1.0-r.x*0.5);
  return p;
}`;

export class OrbitalWorld extends World {
  build() {
    this.particles(this.ctx.budget * this.genome.particleCount, EMERGE);
  }
}
