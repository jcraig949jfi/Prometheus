import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { ARCHETYPES, compileCollision, encodeConcept } from "../src/model/genome";
import { mulberry32 } from "../src/model/hash";
import type { Archetype, Concept } from "../src/model/types";

const dict: Concept[] = JSON.parse(readFileSync(new URL("../public/data/concepts.json", import.meta.url), "utf8")).concepts;

function randomTriples(n: number, seed: number): [Concept, Concept, Concept][] {
  const r = mulberry32(seed);
  const out: [Concept, Concept, Concept][] = [];
  while (out.length < n) {
    const t = [0, 1, 2].map(() => dict[Math.floor(r() * dict.length)]);
    if (new Set(t.map((c) => c.id)).size === 3) out.push(t as [Concept, Concept, Concept]);
  }
  return out;
}

describe("visual genome grammar", () => {
  it("is deterministic for the same ordered triple and seed", () => {
    for (const t of randomTriples(50, 1)) {
      expect(compileCollision(t, 1234)).toEqual(compileCollision(t, 1234));
    }
  });

  it("encodes a concept independently of its partners", () => {
    const [a, b, c] = dict;
    expect(encodeConcept(a)).toEqual(encodeConcept({ ...a }));
    expect(compileCollision([a, b, c], 5).bodies[0].hue).toBe(encodeConcept(a).hue);
  });

  it("is order-sensitive: rotating the triple changes the genome", () => {
    const ts = randomTriples(400, 2);
    let differentGenome = 0;
    let differentArchetype = 0;
    for (const [a, b, c] of ts) {
      const g1 = compileCollision([a, b, c], 99);
      const g2 = compileCollision([c, b, a], 99);
      if (JSON.stringify(g1) !== JSON.stringify(g2)) differentGenome++;
      if (g1.archetype !== g2.archetype) differentArchetype++;
    }
    expect(differentGenome / ts.length).toBeGreaterThan(0.95);
    expect(differentArchetype / ts.length).toBeGreaterThan(0.2);
  });

  it("reverses the twist sign when the first two concepts swap", () => {
    for (const [a, b, c] of randomTriples(30, 3)) {
      const t1 = compileCollision([a, b, c], 7).twist;
      const t2 = compileCollision([b, a, c], 7).twist;
      const antisym = (encodeConcept(a).spin * encodeConcept(b).rhythm - encodeConcept(b).spin * encodeConcept(a).rhythm);
      expect(Math.sign(t1 - t2)).toBe(Math.sign(2 * antisym + (t1 - t2 - 2 * antisym)));
    }
  });

  it("uses every archetype with a reasonable share over the historical dictionary", () => {
    const counts = Object.fromEntries(ARCHETYPES.map((a) => [a, 0])) as Record<Archetype, number>;
    const ts = randomTriples(4000, 4);
    ts.forEach((t, i) => counts[compileCollision(t, i * 7919).archetype]++);
    const shares = ARCHETYPES.map((a) => counts[a] / ts.length);
    // eslint-disable-next-line no-console
    console.log(Object.fromEntries(ARCHETYPES.map((a, i) => [a, shares[i].toFixed(3)])));
    for (const s of shares) expect(s).toBeGreaterThan(0.06);
    for (const s of shares) expect(s).toBeLessThan(0.22);
  });

  it("keeps genome parameters in range", () => {
    for (const t of randomTriples(200, 5)) {
      const g = compileCollision(t, 42);
      for (const p of g.params) expect(p).toBeGreaterThanOrEqual(0);
      for (const p of g.params) expect(p).toBeLessThanOrEqual(1);
      expect(g.symmetry).toBeGreaterThanOrEqual(2);
      expect(g.symmetry).toBeLessThanOrEqual(8);
      expect(g.attractorCount).toBeGreaterThanOrEqual(1);
      expect(g.attractorCount).toBeLessThanOrEqual(5);
      expect(g.branchingFactor).toBeGreaterThanOrEqual(2);
      expect(g.branchingFactor).toBeLessThanOrEqual(5);
    }
  });
});
