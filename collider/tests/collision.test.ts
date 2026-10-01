import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { makeCollision, remix, reorder, userConcept } from "../src/model/collision";
import { decodeAddress, encodeAddress } from "../src/model/url";
import { DataStore, type HistoricalIndexRecord } from "../src/data/store";
import { TemplateProvider } from "../src/synthesis/service";
import type { Concept } from "../src/model/types";

const data = (p: string) => JSON.parse(readFileSync(new URL(`../public/data/${p}`, import.meta.url), "utf8"));
const dict: Concept[] = data("concepts.json").concepts;
const hist: HistoricalIndexRecord[] = data("hephaestus-collisions.json").records;
const byName = new Map(dict.map((c) => [c.name.toLowerCase(), c]));

function store(): DataStore {
  const s = new DataStore();
  (s as any).concepts = dict;
  for (const c of dict) (s as any).byName.set(c.name.toLowerCase(), c);
  (s as any).historical = hist;
  for (const r of hist) (s as any).histById.set(r.id, r);
  return s;
}

describe("collisions, lineage and addresses", () => {
  const [a, b, c] = ["Topology", "Gauge Theory", "Evolution"].map((n) => byName.get(n.toLowerCase())!);

  it("replays deterministically from its URL address", () => {
    const x = makeCollision([a, b, c], 42, { source: "generated" });
    const addr = decodeAddress(encodeAddress({ names: [a.name, b.name, c.name], seed: 42, source: "generated" }))!;
    const y = store().fromAddress(addr)!;
    expect(y.id).toBe(x.id);
    expect(y.visualGenome).toEqual(x.visualGenome);
  });

  it("remix preserves two concepts, replaces one, and records lineage", () => {
    const p = makeCollision([a, b, c], 7, { source: "generated" });
    const ch = remix(p, 2, dict, 0);
    expect(ch.concepts[0].name).toBe(a.name);
    expect(ch.concepts[1].name).toBe(b.name);
    expect(ch.concepts[2].name).not.toBe(c.name);
    expect(ch.parentCollisionId).toBe(p.id);
    expect(ch.mutation).toMatchObject({ kind: "replace", replacedIndex: 2, oldConcept: c.name, newConcept: ch.concepts[2].name });
    expect(remix(p, 2, dict, 0)).toEqual(ch); // deterministic
    expect(remix(p, 2, dict, 1).concepts[2].name).not.toBe(undefined);
  });

  it("reorder keeps the concepts and seed but changes the world", () => {
    const p = makeCollision([a, b, c], 7, { source: "curated" });
    const r = reorder(p);
    expect(r.concepts.map((x) => x.name).sort()).toEqual(p.concepts.map((x) => x.name).sort());
    expect(r.seed).toBe(p.seed);
    expect(r.visualGenome).not.toEqual(p.visualGenome);
    expect(r.parentCollisionId).toBe(p.id);
  });

  it("user concepts pick up dictionary metadata when names match", () => {
    expect(userConcept("topology", byName).field).toBe("Mathematics");
    const u = userConcept("Mycelial networks", byName);
    expect(u.id).toBe("user-mycelial-networks");
    expect(u.field).toBeUndefined();
  });
});

describe("historical provenance", () => {
  it("ingested every unique Nous triple with a source pointer", () => {
    expect(hist.length).toBe(5727);
    for (const r of hist.slice(0, 500)) {
      expect(r.source).toBe("hephaestus");
      expect(r.sourceArtifact).toMatch(/^agents\/nous\/runs\/.+\/responses\.jsonl$/);
      expect(r.sourceLine).toBeGreaterThan(0);
      expect(r.conceptNames).toHaveLength(3);
    }
  });

  it("Topology x Gauge Theory x Evolution is historical; Epigenetics x Emergence x Hoare Logic is not", () => {
    const s = store();
    expect(s.findHistorical(["Topology", "Gauge Theory", "Evolution"])).toBeDefined();
    expect(s.findHistorical(["Epigenetics", "Emergence", "Hoare Logic"])).toBeUndefined();
  });

  it("historical collisions keep their recorded order, id and artifact", () => {
    const s = store();
    const rec = hist[123];
    const col = s.historicalCollision(rec);
    expect(col.id).toBe(rec.id);
    expect(col.provenance).toMatchObject({ source: "hephaestus", historicalId: rec.id, artifactPath: rec.sourceArtifact, artifactLine: rec.sourceLine });
    expect(col.concepts.map((x) => x.name)).toEqual(rec.conceptNames);
    expect(s.historicalCollision(rec).visualGenome).toEqual(col.visualGenome);
    const addr = decodeAddress(encodeAddress({ historicalId: rec.id }))!;
    expect(s.fromAddress(addr)!.id).toBe(rec.id);
  });

  it("remixing a historical collision is labelled generated, derived from the historical root", () => {
    const s = store();
    const col = s.historicalCollision(hist[5]);
    const ch = remix(col, 0, dict, 0);
    expect(ch.provenance.source).toBe("generated");
    expect(ch.provenance.derivedFromHistorical).toBe(hist[5].id);
  });
});

describe("speculative synthesis", () => {
  it("is deterministic and labelled speculative", async () => {
    const [a, b, c] = dict.slice(10, 13);
    const col = makeCollision([a, b, c], 99, { source: "generated" });
    const s1 = await TemplateProvider.synthesize(col, store());
    const s2 = await TemplateProvider.synthesize(col, store());
    expect(s1).toEqual(s2);
    expect(s1!.kind).toBe("template-speculation");
    expect(s1!.reasoningShard.length).toBeGreaterThan(20);
  });
});
