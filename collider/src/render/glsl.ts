// Shared GLSL chunks. Every particle world shares the APPROACH -> COLLISION blend;
// each archetype supplies only `vec3 emerge(...)`.

export const NOISE = /* glsl */ `
vec3 mod289(vec3 x){return x-floor(x*(1.0/289.0))*289.0;}
vec4 mod289(vec4 x){return x-floor(x*(1.0/289.0))*289.0;}
vec4 permute(vec4 x){return mod289(((x*34.0)+1.0)*x);}
vec4 taylorInvSqrt(vec4 r){return 1.79284291400159-0.85373472095314*r;}
float snoise(vec3 v){
  const vec2 C=vec2(1.0/6.0,1.0/3.0); const vec4 D=vec4(0.0,0.5,1.0,2.0);
  vec3 i=floor(v+dot(v,C.yyy)); vec3 x0=v-i+dot(i,C.xxx);
  vec3 g=step(x0.yzx,x0.xyz); vec3 l=1.0-g; vec3 i1=min(g.xyz,l.zxy); vec3 i2=max(g.xyz,l.zxy);
  vec3 x1=x0-i1+C.xxx; vec3 x2=x0-i2+C.yyy; vec3 x3=x0-D.yyy;
  i=mod289(i);
  vec4 p=permute(permute(permute(i.z+vec4(0.0,i1.z,i2.z,1.0))+i.y+vec4(0.0,i1.y,i2.y,1.0))+i.x+vec4(0.0,i1.x,i2.x,1.0));
  float n_=0.142857142857; vec3 ns=n_*D.wyz-D.xzx;
  vec4 j=p-49.0*floor(p*ns.z*ns.z); vec4 x_=floor(j*ns.z); vec4 y_=floor(j-7.0*x_);
  vec4 x=x_*ns.x+ns.yyyy; vec4 y=y_*ns.x+ns.yyyy; vec4 h=1.0-abs(x)-abs(y);
  vec4 b0=vec4(x.xy,y.xy); vec4 b1=vec4(x.zw,y.zw);
  vec4 s0=floor(b0)*2.0+1.0; vec4 s1=floor(b1)*2.0+1.0; vec4 sh=-step(h,vec4(0.0));
  vec4 a0=b0.xzyw+s0.xzyw*sh.xxyy; vec4 a1=b1.xzyw+s1.xzyw*sh.zzww;
  vec3 p0=vec3(a0.xy,h.x); vec3 p1=vec3(a0.zw,h.y); vec3 p2=vec3(a1.xy,h.z); vec3 p3=vec3(a1.zw,h.w);
  vec4 norm=taylorInvSqrt(vec4(dot(p0,p0),dot(p1,p1),dot(p2,p2),dot(p3,p3)));
  p0*=norm.x; p1*=norm.y; p2*=norm.z; p3*=norm.w;
  vec4 m=max(0.6-vec4(dot(x0,x0),dot(x1,x1),dot(x2,x2),dot(x3,x3)),0.0); m=m*m;
  return 42.0*dot(m*m,vec4(dot(p0,x0),dot(p1,x1),dot(p2,x2),dot(p3,x3)));
}
vec3 snoise3(vec3 p){ return vec3(snoise(p), snoise(p+vec3(31.4,17.1,-9.2)), snoise(p+vec3(-7.7,43.3,21.9))); }
vec3 hsl2rgb(vec3 c){ vec3 rgb=clamp(abs(mod(c.x*6.0+vec3(0.0,4.0,2.0),6.0)-3.0)-1.0,0.0,1.0); return c.z+c.y*(rgb-0.5)*(1.0-abs(2.0*c.z-1.0)); }
mat3 rotY(float a){ float c=cos(a), s=sin(a); return mat3(c,0.0,-s, 0.0,1.0,0.0, s,0.0,c); }
mat3 rotX(float a){ float c=cos(a), s=sin(a); return mat3(1.0,0.0,0.0, 0.0,c,s, 0.0,-s,c); }
mat3 rotZ(float a){ float c=cos(a), s=sin(a); return mat3(c,s,0.0, -s,c,0.0, 0.0,0.0,1.0); }
`;

export const COMMON_UNIFORMS = /* glsl */ `
uniform float uTime;        // seconds since this world became active (frozen-aware)
uniform float uTa;          // end of approach
uniform float uTc;          // end of collision
uniform float uTe;          // end of emergence
uniform vec3  uBody[3];     // body centres (CPU-driven approach paths)
uniform float uBodySize[3];
uniform float uShape[3];    // 0 shell 1 ring 2 lattice 3 helix 4 disc 5 filament
uniform float uMat[3];      // 0 glass 1 metal 2 plasma 3 bio 4 ink 5 ice
uniform vec3  uHsl[3];      // body hue/sat/light
uniform float uSpin[3];
uniform vec4  uG0;          // params[0..3]
uniform vec4  uG1;          // params[4..7]
uniform float uSym, uTurb, uElastic, uTwist, uAttr, uBranch, uFrac, uCurl, uRadial, uAxial, uDistort, uMut;
uniform float uPixel;       // point size scale (px)
uniform float uSizeMul;
`;

export const BODY_SHAPE = /* glsl */ `
vec3 bodyShape(float s, vec4 r){
  float u=r.x*6.2831853; float v=r.y*2.0-1.0;
  if(s<0.5){ float sv=sqrt(max(0.0,1.0-v*v)); return vec3(sv*cos(u),v,sv*sin(u))*(0.9+0.12*r.z); }
  if(s<1.5){ float rr=0.8+0.25*r.z; return vec3(cos(u)*rr,(r.w-0.5)*0.14,sin(u)*rr); }
  if(s<2.5){ vec3 q=floor(r.xyz*5.0)/4.0-0.5; return q*1.5+ (r.wzy-0.5)*0.03; }
  if(s<3.5){ float h=r.x*2.0-1.0; float a=h*9.0+step(0.5,r.w)*3.14159; float rad=0.34+0.1*r.z; return vec3(cos(a)*rad,h*1.15,sin(a)*rad); }
  if(s<4.5){ float rad=sqrt(r.z); return vec3(cos(u)*rad,(r.w-0.5)*0.05,sin(u)*rad); }
  float strand=floor(r.w*5.0); float h=r.x*2.0-1.0;
  return vec3(sin(h*3.0+strand)*0.28,h*1.25,cos(h*2.0+strand*1.7)*0.28)+(r.yzw-0.5)*0.05;
}
`;

/** Vertex shader template for particle worlds. `emergeGLSL` must define
 *    vec3 emerge(float k, vec4 r, float idx, float te, inout vec3 col, inout float alpha, inout float size)
 *  where te = seconds since the collision began. */
export function particleVertex(emergeGLSL: string, extraDecl = ""): string {
  return /* glsl */ `
${COMMON_UNIFORMS}
attribute float aK;
attribute vec4 aR;
attribute float aI;
${extraDecl}
varying vec3 vColor;
varying float vAlpha;
varying float vMat;
${NOISE}
${BODY_SHAPE}
${emergeGLSL}
void main(){
  int k=int(aK+0.5);
  vec3 hsl=uHsl[k];
  float spin=uSpin[k];
  // APPROACH: each concept is its own body with its own shape and material
  vec3 local=bodyShape(uShape[k],aR)*uBodySize[k];
  local=rotY(uTime*(0.6+spin*0.9))*rotX(uTime*0.3*spin)*local;
  vec3 approach=uBody[k]+local;
  vec3 acol=hsl2rgb(vec3(hsl.x, hsl.y, 0.55+0.15*aR.z));
  // EMERGENCE (archetype-specific)
  float te=max(uTime-uTa,0.0);
  vec3 ecol=acol; float ealpha=1.0; float esize=1.0;
  vec3 em=emerge(aK,aR,aI,te,ecol,ealpha,esize);
  // COLLISION: staggered blend + an impact impulse
  float d=aR.w*0.45;
  float b=smoothstep(uTa-0.15+d, uTc+d, uTime);
  vec3 pos=mix(approach, em, b);
  float impact=exp(-pow((uTime-uTa-0.25)*5.0,2.0));
  pos+=normalize(pos+vec3(1e-4))*impact*(0.35+0.6*aR.z)*(1.0-0.5*b);
  vec3 col=mix(acol, ecol, b)+impact*0.6;
  float alpha=mix(0.85, ealpha, b);
  vec4 mv=modelViewMatrix*vec4(pos,1.0);
  gl_Position=projectionMatrix*mv;
  float sz=mix(1.0, esize, b)*(0.55+aR.y*0.9)*(1.0+impact*1.5);
  gl_PointSize=clamp(sz*uSizeMul*uPixel/max(0.1,-mv.z), 0.0, 64.0);
  vColor=col; vAlpha=alpha; vMat=mix(uMat[k], 2.0, b*0.5);
}`;
}

export const PARTICLE_FRAGMENT = /* glsl */ `
varying vec3 vColor;
varying float vAlpha;
varying float vMat;
void main(){
  vec2 c=gl_PointCoord-0.5; float d=length(c)*2.0;
  if(d>1.0) discard;
  float soft=pow(1.0-d,1.6);
  float core=smoothstep(0.35,0.0,d);
  float ring=smoothstep(0.25,0.0,abs(d-0.7));
  float a;
  if(vMat<0.5) a=ring*0.8+core*0.35;            // glass: hollow rings
  else if(vMat<1.5) a=core*1.2+soft*0.25;       // metal: hard cores
  else if(vMat<2.5) a=soft;                     // plasma: glow
  else if(vMat<3.5) a=soft*0.8+core*0.4;        // bio: blobs
  else if(vMat<4.5) a=smoothstep(1.0,0.6,d)*0.9;// ink: flat discs
  else a=ring*0.5+core*0.7;                     // ice
  gl_FragColor=vec4(vColor*a*vAlpha, 1.0);
}`;
