// Concept names as matter: each name is a textured membrane that rides its body
// during approach, smears/stretches through the collision, then wraps into a slowly
// orbiting ring around the emergent structure.

import * as THREE from "three";

function textTexture(text: string, hueCss: string): { tex: THREE.CanvasTexture; aspect: number } {
  const c = document.createElement("canvas");
  const fontPx = 96;
  const ctx = c.getContext("2d")!;
  const label = text.toUpperCase();
  const font = `500 ${fontPx}px "Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif`;
  ctx.font = font;
  const spacing = fontPx * 0.18;
  const w = Math.ceil([...label].reduce((acc, ch) => acc + ctx.measureText(ch).width + spacing, 0)) + 40;
  c.width = Math.min(4096, w);
  c.height = fontPx + 40;
  const g = c.getContext("2d")!;
  g.font = font; // resizing the canvas reset the context state, so set it again
  g.textBaseline = "middle";
  g.shadowColor = hueCss;
  g.shadowBlur = 18;
  g.fillStyle = "#f4f1ea";
  let x = 20;
  for (const ch of label) {
    g.fillText(ch, x, c.height / 2);
    x += g.measureText(ch).width + spacing;
  }
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.minFilter = THREE.LinearMipmapLinearFilter;
  tex.anisotropy = 4;
  return { tex, aspect: c.width / c.height };
}

const VERT = /* glsl */ `
uniform vec3 uAnchor; uniform float uAspect; uniform float uScale;
uniform float uMorph; uniform float uStretch; uniform float uRingR; uniform float uAngle; uniform float uRingY;
uniform float uTime;
varying vec2 vUv; varying float vEdge;
void main(){
  vUv=uv;
  vec2 q=vec2((uv.x-0.5)*uAspect, uv.y-0.5)*uScale;
  // billboard near the body, stretched along x during the collision
  vec4 bill=viewMatrix*vec4(uAnchor,1.0);
  bill.xy+=vec2(q.x*(1.0+uStretch*2.5), q.y*(1.0-uStretch*0.6)+0.55*uScale*1.3);
  bill.y+=sin(uv.x*12.0+uTime*6.0)*uStretch*0.12;
  // ring: the name wraps an arc of radius uRingR around the vertical axis
  float arcLen=uAspect*uScale;
  float th=uAngle+(uv.x-0.5)*arcLen/uRingR;
  vec3 ringW=vec3(cos(th)*uRingR, uRingY+q.y+sin(th*3.0+uTime*0.7)*0.06, sin(th)*uRingR);
  vec4 ring=viewMatrix*vec4(ringW,1.0);
  vec4 mv=mix(bill, ring, uMorph);
  vEdge=abs(uv.x-0.5)*2.0;
  gl_Position=projectionMatrix*mv;
}`;

const FRAG = /* glsl */ `
uniform sampler2D uTex; uniform sampler2D uTexOld; uniform float uSwap;
uniform float uOpacity; uniform vec3 uTint; uniform float uStretch; uniform float uTime;
varying vec2 vUv; varying float vEdge;
float h(vec2 p){ return fract(sin(dot(p,vec2(12.9898,78.233)))*43758.5453); }
void main(){
  vec2 uv=vUv;
  uv.x+=(h(vec2(floor(uv.y*40.0),floor(uTime*20.0)))-0.5)*uStretch*0.08;
  vec4 a=texture2D(uTex,uv);
  vec4 o=texture2D(uTexOld,uv);
  float n=h(floor(uv*vec2(80.0,10.0)));
  float sw=smoothstep(n-0.1,n+0.1,uSwap);
  vec4 t=mix(o,a,sw);
  float alpha=t.a*uOpacity*(1.0-smoothstep(0.85,1.0,vEdge)*0.6);
  gl_FragColor=vec4(mix(t.rgb,uTint,0.25)*alpha, alpha);
}`;

export class ConceptGlyph {
  mesh: THREE.Mesh<THREE.PlaneGeometry, THREE.ShaderMaterial>;
  private tex: THREE.CanvasTexture;
  private old?: THREE.CanvasTexture;
  private baseAngle: number;

  constructor(name: string, hue: number, index: number, oldName?: string) {
    this.baseAngle = (index / 3) * Math.PI * 2;
    const color = new THREE.Color().setHSL(hue, 0.8, 0.6);
    const css = `#${color.getHexString()}`;
    const t = textTexture(name, css);
    this.tex = t.tex;
    let aspect = t.aspect;
    if (oldName) {
      const o = textTexture(oldName, css);
      this.old = o.tex;
      aspect = Math.max(aspect, o.aspect);
    }
    const geo = new THREE.PlaneGeometry(1, 1, 64, 1);
    const mat = new THREE.ShaderMaterial({
      vertexShader: VERT,
      fragmentShader: FRAG,
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      side: THREE.DoubleSide,
      uniforms: {
        uTex: { value: this.tex },
        uTexOld: { value: this.old ?? this.tex },
        uSwap: { value: oldName ? 0 : 1 },
        uAnchor: { value: new THREE.Vector3() },
        uAspect: { value: aspect },
        uScale: { value: 0.32 },
        uMorph: { value: 0 },
        uStretch: { value: 0 },
        uRingR: { value: 3.2 },
        uAngle: { value: (index / 3) * Math.PI * 2 },
        uRingY: { value: -2.1 + index * 0.18 },
        uOpacity: { value: 0 },
        uTint: { value: color },
        uTime: { value: 0 },
      },
    });
    this.mesh = new THREE.Mesh(geo, mat);
    this.mesh.frustumCulled = false;
    this.mesh.renderOrder = 10;
  }

  update(t: number, anchor: THREE.Vector3, ta: number, tc: number, te: number, ringR: number, spin: number) {
    const u = this.mesh.material.uniforms;
    u.uTime.value = t;
    u.uAnchor.value.copy(anchor);
    const approachIn = Math.min(1, t / 0.6);
    const collide = Math.max(0, Math.min(1, (t - ta + 0.3) / (tc - ta + 0.3)));
    const toRing = Math.max(0, Math.min(1, (t - tc) / (te - tc) * 1.4));
    u.uStretch.value = Math.sin(collide * Math.PI) * (1 - toRing);
    u.uMorph.value = toRing * toRing * (3 - 2 * toRing);
    u.uOpacity.value = approachIn * (0.95 - 0.55 * Math.sin(collide * Math.PI) * (1 - toRing)) * (1 - 0.45 * u.uMorph.value);
    u.uRingR.value = ringR;
    u.uSwap.value = this.old ? Math.min(1, Math.max(0, (t - 0.4) / (ta * 0.8))) : 1;
    // once formed, the ring of names turns slowly in the direction of the order twist
    u.uAngle.value = this.baseAngle + t * 0.06 * (spin >= 0 ? 1 : -1);
  }

  dispose() {
    this.mesh.geometry.dispose();
    this.mesh.material.dispose();
    this.tex.dispose();
    this.old?.dispose();
  }
}
