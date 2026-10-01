// Loads the ingested historical data (public/data/*) and turns records into Collisions.
// Historical and generated content are kept apart by `provenance.source`.

import type { Archetype, Collision, Concept, SourceKind } from "../model/types";
import { makeCollision, userConcept } from "../model/collision";
import { withArchetype } from "../model/genome";
import { fnv1a, mulberry32, type Rng } from "../model/hash";
import type { CollisionAddress } from "../model/url";

export interface HistoricalIndexRecord {
  id: string;
  concepts: string[];
  conceptNames: string[];
  fields: string[];
  source: "hephaestus";
  sourceArtifact: string;
  sourceLine: number;
  title: string | null;
  bestComposite: number | null;
  forged: boolean;
  unproductive: boolean;
  shard: string;
}

export interface HistoricalDetail {
  synthesis: { title: string | null; excerpt: string; kind: string };
  historicalMetadata: {
    occurrences: { artifact: string; line: number; model: string; timestamp: string; composite: number | null; novelty: string; unproductive: boolean; highPotential: boolean }[];
    forge: { status: string; reason: string; accuracy: number; calibration: number; timestamp: string; line: number }[];
    forgeTools: string[];
    humanReadable: string | null;
    priorityReason: string | null;
    bestComposite: number | null;
    forged: boolean;
  };
}

export class DataStore {
  concepts: Concept[] = [];
  private byName = new Map<string, Concept>();
  historical: HistoricalIndexRecord[] = [];
  private histById = new Map<string, HistoricalIndexRecord>();
  private shards = new Map<string, Promise<Record<string, HistoricalDetail>>>();
  loaded = { concepts: false, historical: false };

  constructor(private base = "data/") {}

  async load() {
    const [c, h] = await Promise.allSettled([
      fetch(this.base + "concepts.json").then((r) => r.json()),
      fetch(this.base + "hephaestus-collisions.json").then((r) => r.json()),
    ]);
    if (c.status === "fulfilled") {
      this.concepts = c.value.concepts;
      for (const x of this.concepts) this.byName.set(x.name.toLowerCase(), x);
      this.loaded.concepts = true;
    }
    if (h.status === "fulfilled") {
      this.historical = h.value.records;
      for (const r of this.historical) this.histById.set(r.id, r);
      this.loaded.historical = true;
    }
  }

  get dictionary(): Map<string, Concept> {
    return this.byName;
  }

  concept(name: string): Concept {
    return userConcept(name, this.byName);
  }

  historicalRecord(id: string) {
    return this.histById.get(id);
  }

  findHistorical(names: string[]): HistoricalIndexRecord | undefined {
    const key = names.map((n) => n.toLowerCase()).sort().join("|");
    return this.historical.find((r) => r.conceptNames.map((n) => n.toLowerCase()).sort().join("|") === key);
  }

  async detail(id: string): Promise<HistoricalDetail | null> {
    const rec = this.histById.get(id);
    if (!rec) return null;
    if (!this.shards.has(rec.shard)) {
      this.shards.set(rec.shard, fetch(`${this.base}hephaestus/detail-${rec.shard}.json`).then((r) => r.json()).then((j) => j.records));
    }
    const shard = await this.shards.get(rec.shard)!;
    return shard[id] ?? null;
  }

  historicalCollision(rec: HistoricalIndexRecord): Collision {
    const concepts = rec.conceptNames.map((n) => this.concept(n)) as [Concept, Concept, Concept];
    return makeCollision(concepts, fnv1a(rec.id), {
      source: "hephaestus",
      artifactPath: rec.sourceArtifact,
      artifactLine: rec.sourceLine,
      historicalId: rec.id,
    }, {}, rec.id);
  }

  fromAddress(a: CollisionAddress): Collision | null {
    if (a.historicalId) {
      const rec = this.histById.get(a.historicalId);
      return rec ? this.historicalCollision(rec) : null;
    }
    if (!a.names) return null;
    const concepts = a.names.map((n) => this.concept(n)) as [Concept, Concept, Concept];
    const extra: Partial<Collision> = {};
    if (a.parent) extra.parentCollisionId = a.parent;
    if (a.mutation) extra.mutation = parseMutation(a.mutation);
    let c = makeCollision(concepts, a.seed ?? 0, { source: (a.source ?? "user") as SourceKind }, extra);
    if (a.archetype) c = { ...c, visualGenome: withArchetype(c.visualGenome, a.archetype as Archetype) };
    return c;
  }
}

export function mutationString(c: Collision): string | undefined {
  const m = c.mutation;
  if (!m) return undefined;
  if (m.kind === "reorder") return "reorder";
  return `replace:${m.replacedIndex}:${m.oldConcept}>${m.newConcept}`;
}

function parseMutation(s: string): Collision["mutation"] {
  if (s === "reorder") return { kind: "reorder", order: [1, 2, 0] };
  const m = /^replace:(\d):(.*)>(.*)$/.exec(s);
  if (!m) return undefined;
  return { kind: "replace", replacedIndex: Number(m[1]) as 0 | 1 | 2, oldConcept: m[2], newConcept: m[3] };
}

// ---------------------------------------------------------------------------------
// Curated showcase: real dictionary concepts, triples chosen by hand for visual range.
// Labelled "curated" everywhere; the archetype pin is recorded in the URL.
export const SHOWCASE: { names: [string, string, string]; archetype?: Archetype }[] = [
  { names: ["Epigenetics", "Emergence", "Hoare Logic"] },
  { names: ["Renormalization", "Morphogenesis", "Category Theory"], archetype: "REACTION_DIFFUSION" },
  { names: ["Quantum Mechanics", "Immune Systems", "Satisfiability"], archetype: "FRACTURE" },
  { names: ["Holography Principle", "Symbiosis", "Proof Theory"], archetype: "DIMENSIONAL_FOLD" },
  { names: ["Gauge Theory", "Swarm Intelligence", "Kalman Filtering"], archetype: "ORBITAL_CAPTURE" },
  { names: ["Neural Plasticity", "Phase Transitions", "Compositional Semantics"], archetype: "BRANCHING_GROWTH" },
  { names: ["Chaos Theory", "Hebbian Learning", "Mechanism Design"], archetype: "STRANGE_ATTRACTOR" },
  { names: ["Autopoiesis", "Type Theory", "Wavelet Transforms"], archetype: "CRYSTALLIZATION" },
  { names: ["Thermodynamics", "Dialectics", "Sparse Coding"], archetype: "VORTEX" },
];

/** Infinite, deterministic-per-session feed mixing historical, curated and generated
 *  collisions. Each collision is itself deterministic from its own seed. */
export class FeedSource {
  private rng: Rng;
  private n = 0;
  private curated = 0;
  private used = new Set<string>();
  private histPool: HistoricalIndexRecord[];
  private histWeights: number[];
  private histTotal: number;

  constructor(private store: DataStore, sessionSeed: number) {
    this.rng = mulberry32(sessionSeed);
    this.histPool = store.historical;
    this.histWeights = this.histPool.map((r) => (r.forged ? 3 : 1) * ((r.bestComposite ?? 0) >= 7 ? 2 : 1) * (r.unproductive ? 0.3 : 1) * (r.title ? 1.5 : 1));
    this.histTotal = this.histWeights.reduce((a, b) => a + b, 0);
  }

  first(): Collision {
    const rec = this.store.findHistorical(["Topology", "Gauge Theory", "Evolution"]);
    if (rec) {
      this.used.add(rec.id);
      return this.store.historicalCollision(rec);
    }
    return this.next();
  }

  next(): Collision {
    const i = this.n++;
    const slot = i % 3;
    if (slot === 1 && this.curated < SHOWCASE.length) return this.curatedNext();
    if (slot === 0 && this.histPool.length) return this.historicalNext();
    return this.generatedNext();
  }

  private curatedNext(): Collision {
    const s = SHOWCASE[this.curated++];
    const concepts = s.names.map((n) => this.store.concept(n)) as [Concept, Concept, Concept];
    const seed = fnv1a("curated:" + s.names.join("|"));
    let c = makeCollision(concepts, seed, { source: "curated" });
    if (s.archetype) c = { ...c, visualGenome: withArchetype(c.visualGenome, s.archetype) };
    return c;
  }

  private historicalNext(): Collision {
    for (let tries = 0; tries < 20; tries++) {
      let x = this.rng() * this.histTotal;
      let idx = 0;
      while (idx < this.histWeights.length - 1 && x > this.histWeights[idx]) x -= this.histWeights[idx++];
      const rec = this.histPool[idx];
      if (this.used.has(rec.id)) continue;
      this.used.add(rec.id);
      return this.store.historicalCollision(rec);
    }
    return this.generatedNext();
  }

  private generatedNext(): Collision {
    const d = this.store.concepts;
    let t: Concept[] = [];
    for (let tries = 0; tries < 50; tries++) {
      t = [0, 1, 2].map(() => d[Math.floor(this.rng() * d.length)]);
      const names = new Set(t.map((c) => c.name));
      const fields = new Set(t.map((c) => c.field));
      if (names.size === 3 && (fields.size >= 2 || this.rng() < 0.1)) break;
    }
    const seed = Math.floor(this.rng() * 2 ** 31);
    return makeCollision(t as [Concept, Concept, Concept], seed, { source: "generated" });
  }
}
