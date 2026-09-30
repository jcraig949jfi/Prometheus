// Pluggable synthesis boundary. Providers are tried in order; the first non-null
// result wins. The visual collision never depends on synthesis.
//   1. HistoricalProvider: the real Nous analysis for historical triples
//   2. ExternalProvider:   optional HTTP service (VITE_SYNTH_URL), off by default
//   3. TemplateProvider:   deterministic speculative grammar (always available)

import type { Collision, Concept, Mechanism, Synthesis } from "../model/types";
import { conceptMechanism } from "../model/genome";
import { rngFrom, pick } from "../model/hash";
import type { DataStore } from "../data/store";

export interface SynthesisProvider {
  id: string;
  synthesize(c: Collision, store: DataStore): Promise<Synthesis | null>;
}

export const HistoricalProvider: SynthesisProvider = {
  id: "historical",
  async synthesize(c, store) {
    if (c.provenance.source !== "hephaestus" || !c.provenance.historicalId) return null;
    const d = await store.detail(c.provenance.historicalId);
    if (!d) return null;
    return { title: d.synthesis.title, reasoningShard: d.synthesis.excerpt, kind: "historical-nous-analysis" };
  },
};

export const ExternalProvider: SynthesisProvider = {
  id: "external",
  async synthesize(c) {
    const url = (import.meta as any).env?.VITE_SYNTH_URL as string | undefined;
    if (!url) return null;
    try {
      const r = await fetch(url, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ id: c.id, seed: c.seed, concepts: c.concepts.map((x) => ({ name: x.name, field: x.field })) }),
      });
      if (!r.ok) return null;
      const j = await r.json();
      if (typeof j.reasoningShard !== "string") return null;
      return { title: j.title ?? null, reasoningShard: j.reasoningShard, speculativeMechanism: j.speculativeMechanism, kind: "external" };
    } catch {
      return null;
    }
  },
};

const VOCAB: Record<Mechanism, { nouns: string[]; verb: string; act: string }> = {
  structure: { nouns: ["invariants", "scaffolds", "lattices", "morphisms", "shapes"], verb: "gives form to", act: "preserve" },
  dynamics: { nouns: ["flows", "trajectories", "feedback loops", "cascades", "rhythms"], verb: "sets in motion", act: "sustain" },
  constraint: { nouns: ["boundaries", "admissibility conditions", "proof obligations", "filters"], verb: "prunes", act: "certify" },
  measure: { nouns: ["gradients", "ledgers", "entropy budgets", "scores"], verb: "weighs", act: "account for" },
};

function gist(c: Concept): string {
  const d = (c.sourceMetadata?.shortDescription as string | undefined) ?? "";
  if (!d) return c.name.toLowerCase();
  const first = d.split(/[;:]/)[0].split(",")[0].trim().replace(/\.$/, "");
  return first.charAt(0).toLowerCase() + first.slice(1);
}

export const TemplateProvider: SynthesisProvider = {
  id: "template",
  async synthesize(c) {
    const [A, B, C] = c.concepts;
    const [mA, mB, mC] = c.concepts.map(conceptMechanism);
    const r = rngFrom("shard", c.id, c.seed);
    const nA = pick(r, VOCAB[mA].nouns), nB = pick(r, VOCAB[mB].nouns), nC = pick(r, VOCAB[mC].nouns);
    const templates = [
      () => `Local ${nB} from ${B.name} press against the global ${nA} of ${A.name}. ${C.name} is where the disagreement becomes visible.`,
      () => `Treat ${gist(C)} as the medium in which ${A.name}'s ${nA} and ${B.name}'s ${nB} compete. What persists may be only what ${C.name} can still ${VOCAB[mC].act}.`,
      () => `If ${A.name} ${VOCAB[mA].verb} ${B.name}, then ${C.name} becomes the ${nC.replace(/s$/, "")} that separates a stable structure from a lucky one.`,
      () => `${A.name} supplies the ${nA}; ${B.name} ${VOCAB[mB].verb} them; ${C.name} decides which survive being ${mC === "measure" ? "counted" : mC === "constraint" ? "checked" : "reshaped"}.`,
      () => `A system that keeps only those ${nB} of ${B.name} which remain legible under ${gist(A)}, and lets ${C.name} erase the rest.`,
      () => `Selection may favour ${nA} whose value exists only across a family of ${B.name.toLowerCase()} transformations, never in any single state, as ${C.name} would register it.`,
    ];
    const shard = pick(r, templates)();
    return { title: null, reasoningShard: shard, kind: "template-speculation" };
  },
};

export class SynthesisService {
  private cache = new Map<string, Promise<Synthesis>>();
  constructor(private store: DataStore, private providers: SynthesisProvider[] = [HistoricalProvider, ExternalProvider, TemplateProvider]) {}

  get(c: Collision): Promise<Synthesis> {
    if (!this.cache.has(c.id)) {
      this.cache.set(c.id, (async () => {
        for (const p of this.providers) {
          const s = await p.synthesize(c, this.store);
          if (s) return s;
        }
        return { title: null, reasoningShard: "", kind: "template-speculation" } as Synthesis;
      })());
    }
    return this.cache.get(c.id)!;
  }
}
