// Optional generative sound, muted until the user asks. Every parameter comes from
// the same visual genome: three voices (one per concept) arrive detuned, glide into
// a chord at the collision, the impact is a filtered noise burst plus a low thump,
// and the stable world breathes with its evolution mode. No samples, no assets.

import type { Collision } from "../model/types";
import type { World } from "../render/world";

export class Sonifier {
  private ac?: AudioContext;
  private master?: GainNode;
  private filter?: BiquadFilterNode;
  private voices: { osc: OscillatorNode; gain: GainNode; target: number; from: number }[] = [];
  private currentId?: string;
  private impacted = false;
  enabled = false;

  async toggle(): Promise<boolean> {
    if (!this.ac) {
      this.ac = new AudioContext();
      this.filter = this.ac.createBiquadFilter();
      this.filter.type = "lowpass";
      this.filter.frequency.value = 600;
      this.master = this.ac.createGain();
      this.master.gain.value = 0;
      this.filter.connect(this.master).connect(this.ac.destination);
    }
    this.enabled = !this.enabled;
    if (this.enabled) await this.ac.resume();
    this.master!.gain.setTargetAtTime(this.enabled ? 0.16 : 0, this.ac.currentTime, 0.3);
    return this.enabled;
  }

  private setCollision(c: Collision) {
    if (!this.ac || !this.filter) return;
    for (const v of this.voices) { v.gain.gain.setTargetAtTime(0, this.ac.currentTime, 0.2); v.osc.stop(this.ac.currentTime + 1); }
    this.voices = [];
    const g = c.visualGenome;
    const root = 55 * Math.pow(2, (g.seed % 12) / 12);
    const intervals = [1, g.symmetry % 2 ? 1.5 : 1.3348, 2 * Math.pow(2, (g.symmetry % 5) / 12)];
    const types: OscillatorType[] = ["sine", "triangle", "sine"];
    g.bodies.forEach((b, k) => {
      const osc = this.ac!.createOscillator();
      const gain = this.ac!.createGain();
      osc.type = types[k];
      const target = root * intervals[k];
      const from = target * (1 + (b.spin * 0.35 + (k - 1) * 0.12));
      osc.frequency.value = from;
      gain.gain.value = 0;
      osc.connect(gain).connect(this.filter!);
      osc.start();
      this.voices.push({ osc, gain, target, from });
    });
    this.currentId = c.id;
    this.impacted = false;
  }

  private impact(strength: number) {
    const ac = this.ac!;
    const len = Math.floor(ac.sampleRate * 0.6);
    const buf = ac.createBuffer(1, len, ac.sampleRate);
    const d = buf.getChannelData(0);
    let s = 12345;
    for (let i = 0; i < len; i++) { s = (s * 1103515245 + 12345) >>> 0; d[i] = ((s / 4294967296) * 2 - 1) * Math.exp(-i / (len * 0.18)); }
    const src = ac.createBufferSource();
    src.buffer = buf;
    const bp = ac.createBiquadFilter();
    bp.type = "bandpass";
    bp.frequency.value = 300 + strength * 900;
    const g = ac.createGain();
    g.gain.value = 0.9;
    src.connect(bp).connect(g).connect(this.master!);
    src.start();
    const thump = ac.createOscillator();
    const tg = ac.createGain();
    thump.frequency.setValueAtTime(90, ac.currentTime);
    thump.frequency.exponentialRampToValueAtTime(34, ac.currentTime + 0.5);
    tg.gain.setValueAtTime(0.8, ac.currentTime);
    tg.gain.exponentialRampToValueAtTime(0.001, ac.currentTime + 0.7);
    thump.connect(tg).connect(this.master!);
    thump.start();
    thump.stop(ac.currentTime + 0.8);
  }

  tick(w: World | undefined) {
    if (!this.enabled || !this.ac || !w) return;
    if (w.collision.id !== this.currentId) this.setCollision(w.collision);
    const now = this.ac.currentTime;
    const t = w.t;
    const glide = Math.min(1, t / w.ta);
    this.voices.forEach((v, k) => {
      const f = v.from + (v.target - v.from) * glide * glide;
      v.osc.frequency.setTargetAtTime(f, now, 0.05);
      const post = Math.max(0, t - w.tc);
      const breathe = 0.5 + 0.5 * Math.sin(post * (0.5 + k * 0.17));
      const level = t < w.ta ? 0.05 + 0.1 * glide : 0.08 + 0.07 * breathe;
      v.gain.gain.setTargetAtTime(w.frozen ? 0.02 : level, now, 0.1);
    });
    const open = t < w.ta ? 500 : t < w.te ? 500 + ((t - w.ta) / (w.te - w.ta)) * 2200 : 1400 + 500 * Math.sin(t * 0.3);
    this.filter!.frequency.setTargetAtTime(open, now, 0.2);
    if (!this.impacted && t >= w.ta + 0.2) {
      this.impacted = true;
      this.impact(w.genome.turbulence);
    }
  }
}
