// Building collisions: identity, lineage (remix/reorder), provenance.

import type { Collision, Concept, Mutation, Provenance, SourceKind } from "./types";
import { compileCollision } from "./genome";
import { fnv1a, rngFrom, slug } from "./hash";

export function collisionId(concepts: readonly Concept[], seed: number, source: SourceKind): string {
  const key = concepts.map((c) => c.name).join("|") + "#" + seed + "#" + source;
  return "c-" + fnv1a(key).toString(36) + fnv1a(key, 7).toString(36).slice(0, 3);
}

export function makeCollision(
  concepts: [Concept, Concept, Concept],
  seed: number,
  provenance: Provenance,
  extra: Partial<Pick<Collision, "parentCollisionId" | "mutation" | "synthesis" | "createdAt">> = {},
  fixedId?: string,
): Collision {
  return {
    id: fixedId ?? collisionId(concepts, seed, provenance.source),
    seed,
    concepts,
    provenance,
    visualGenome: compileCollision(concepts, seed),
    ...extra,
  };
}

export function userConcept(name: string, dictionary: Map<string, Concept>): Concept {
  const hit = dictionary.get(name.trim().toLowerCase());
  if (hit) return hit;
  return { id: "user-" + slug(name), name: name.trim() };
}

/** Preserve two concepts, replace the one at `index` with a new dictionary concept.
 *  Deterministic in (parent id, index, generation). Prefers a field not already present. */
export function remix(
  parent: Collision,
  index: 0 | 1 | 2,
  dictionary: Concept[],
  generation: number,
): Collision {
  const rng = rngFrom("remix", parent.id, index, generation);
  const keep = parent.concepts.filter((_, i) => i !== index);
  const keepNames = new Set(parent.concepts.map((c) => c.name));
  const keepFields = new Set(keep.map((c) => c.field));
  let pool = dictionary.filter((c) => !keepNames.has(c.name) && !keepFields.has(c.field));
  if (pool.length === 0) pool = dictionary.filter((c) => !keepNames.has(c.name));
  const next = pool[Math.floor(rng() * pool.length)];
  const concepts = parent.concepts.slice() as [Concept, Concept, Concept];
  const old = concepts[index];
  concepts[index] = next;
  const seed = Math.floor(rng() * 2 ** 31);
  const mutation: Mutation = { kind: "replace", replacedIndex: index, oldConcept: old.name, newConcept: next.name };
  return makeCollision(concepts, seed, {
    source: "generated",
    derivedFromHistorical: parent.provenance.historicalId ?? parent.provenance.derivedFromHistorical,
  }, { parentCollisionId: parent.id, mutation });
}

/** Same three concepts, rotated order, same seed: exposes order-sensitivity. */
export function reorder(parent: Collision): Collision {
  const [a, b, c] = parent.concepts;
  const concepts: [Concept, Concept, Concept] = [b, c, a];
  return makeCollision(concepts, parent.seed, {
    source: parent.provenance.source === "hephaestus" ? "generated" : parent.provenance.source,
    derivedFromHistorical: parent.provenance.historicalId ?? parent.provenance.derivedFromHistorical,
  }, { parentCollisionId: parent.id, mutation: { kind: "reorder", order: [1, 2, 0] } });
}
