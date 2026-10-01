// Fit CALIBRATION offsets so archetypes are roughly equiprobable over the historical
// dictionary. Prints the offsets to paste into src/model/genome.ts (grammar version bump).
import { readFileSync } from "node:fs";
import { ARCHETYPES, CALIBRATION, compileCollision } from "../src/model/genome";
import { mulberry32 } from "../src/model/hash";
import type { Concept } from "../src/model/types";

const dict: Concept[] = JSON.parse(readFileSync("public/data/concepts.json", "utf8")).concepts;
const r = mulberry32(12345);
const triples: [Concept, Concept, Concept][] = [];
while (triples.length < 6000) {
  const t = [0, 1, 2].map(() => dict[Math.floor(r() * dict.length)]);
  if (new Set(t.map((c) => c.id)).size === 3) triples.push(t as [Concept, Concept, Concept]);
}
for (let it = 0; it < 60; it++) {
  const counts: Record<string, number> = Object.fromEntries(ARCHETYPES.map((a) => [a, 0]));
  triples.forEach((t, i) => counts[compileCollision(t, i * 104729 + 17).archetype]++);
  for (const a of ARCHETYPES) {
    const share = counts[a] / triples.length;
    CALIBRATION[a] -= 0.25 * (share - 1 / ARCHETYPES.length);
  }
  if (it === 59) console.log(JSON.stringify(Object.fromEntries(ARCHETYPES.map((a) => [a, (counts[a] / triples.length).toFixed(3)]))));
}
console.log(JSON.stringify(Object.fromEntries(ARCHETYPES.map((a) => [a, Number(CALIBRATION[a].toFixed(3))]))));
