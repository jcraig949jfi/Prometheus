// The deterministic generative grammar:
//   A = encodeConcept(a); B = encodeConcept(b); C = encodeConcept(c)
//   genome = collisionOperator(A, B, C, seed)
// Same triple (same ORDER) + same seed => identical genome. Order is part of the
// input: the operator weights positions unequally and includes antisymmetric terms,
// so A x B x C and C x B x A are generally different worlds.

import type {
  Archetype, BodyGene, BodyShape, Concept, ConceptSignature, MaterialKind, Mechanism, VisualGenome,
} from "./types";
import { clamp01, fnv1a, mulberry32, normalizeName, pick, rngFrom } from "./hash";

export const ARCHETYPES: Archetype[] = [
  "CRYSTALLIZATION", "VORTEX", "FRACTURE", "REACTION_DIFFUSION",
  "ORBITAL_CAPTURE", "BRANCHING_GROWTH", "STRANGE_ATTRACTOR", "DIMENSIONAL_FOLD",
];

const SHAPES: BodyShape[] = ["shell", "ring", "lattice", "helix", "disc", "filament"];
const MATERIALS: MaterialKind[] = ["glass", "metal", "plasma", "bio", "ink", "ice"];
const MECHS: Mechanism[] = ["structure", "dynamics", "constraint", "measure"];

type Aff = Partial<Record<Archetype, number>>;

const MECH_AFFINITY: Record<Mechanism, Aff> = {
  structure: { CRYSTALLIZATION: 0.9, DIMENSIONAL_FOLD: 0.8, FRACTURE: 0.45, BRANCHING_GROWTH: 0.35 },
  dynamics: { VORTEX: 0.85, STRANGE_ATTRACTOR: 0.8, ORBITAL_CAPTURE: 0.5, BRANCHING_GROWTH: 0.45, REACTION_DIFFUSION: 0.45 },
  constraint: { FRACTURE: 0.9, CRYSTALLIZATION: 0.65, ORBITAL_CAPTURE: 0.45, DIMENSIONAL_FOLD: 0.3 },
  measure: { REACTION_DIFFUSION: 0.8, ORBITAL_CAPTURE: 0.7, DIMENSIONAL_FOLD: 0.45, STRANGE_ATTRACTOR: 0.3 },
};

// Field priors: hue (0..1) and archetype leanings. Unknown fields fall back to hashing.
const FIELD: Record<string, { hue: number; aff: Aff; material: MaterialKind }> = {
  "Mathematics": { hue: 0.58, aff: { DIMENSIONAL_FOLD: 0.6, CRYSTALLIZATION: 0.4 }, material: "glass" },
  "Physics": { hue: 0.62, aff: { ORBITAL_CAPTURE: 0.55, VORTEX: 0.45 }, material: "plasma" },
  "Computer Science": { hue: 0.48, aff: { CRYSTALLIZATION: 0.45, FRACTURE: 0.4 }, material: "metal" },
  "Biology": { hue: 0.33, aff: { BRANCHING_GROWTH: 0.65, REACTION_DIFFUSION: 0.45 }, material: "bio" },
  "Cognitive Science": { hue: 0.78, aff: { BRANCHING_GROWTH: 0.4, DIMENSIONAL_FOLD: 0.35 }, material: "ink" },
  "Signal Processing": { hue: 0.52, aff: { ORBITAL_CAPTURE: 0.45, VORTEX: 0.4 }, material: "plasma" },
  "Philosophy": { hue: 0.1, aff: { FRACTURE: 0.45, DIMENSIONAL_FOLD: 0.4 }, material: "ink" },
  "Complex Systems": { hue: 0.02, aff: { STRANGE_ATTRACTOR: 0.6, REACTION_DIFFUSION: 0.45 }, material: "plasma" },
  "Information Science": { hue: 0.45, aff: { REACTION_DIFFUSION: 0.4, CRYSTALLIZATION: 0.35 }, material: "ice" },
  "Neuroscience": { hue: 0.85, aff: { BRANCHING_GROWTH: 0.55, STRANGE_ATTRACTOR: 0.35 }, material: "bio" },
  "Control Theory": { hue: 0.08, aff: { STRANGE_ATTRACTOR: 0.5, VORTEX: 0.4 }, material: "metal" },
  "Linguistics": { hue: 0.92, aff: { BRANCHING_GROWTH: 0.5, CRYSTALLIZATION: 0.25 }, material: "ink" },
  "Economics": { hue: 0.13, aff: { ORBITAL_CAPTURE: 0.5, FRACTURE: 0.35 }, material: "metal" },
  "Game Theory": { hue: 0.15, aff: { ORBITAL_CAPTURE: 0.55, FRACTURE: 0.35 }, material: "metal" },
  "Theoretical Neuroscience": { hue: 0.82, aff: { STRANGE_ATTRACTOR: 0.5, BRANCHING_GROWTH: 0.35 }, material: "bio" },
  "Statistical Physics": { hue: 0.66, aff: { REACTION_DIFFUSION: 0.5, STRANGE_ATTRACTOR: 0.4 }, material: "plasma" },
  "Logic": { hue: 0.55, aff: { CRYSTALLIZATION: 0.55, FRACTURE: 0.4 }, material: "ice" },
  "Formal Methods": { hue: 0.5, aff: { CRYSTALLIZATION: 0.55, FRACTURE: 0.45 }, material: "ice" },
  "Software Engineering": { hue: 0.4, aff: { FRACTURE: 0.45, CRYSTALLIZATION: 0.4 }, material: "metal" },
  "Statistics": { hue: 0.7, aff: { REACTION_DIFFUSION: 0.45, ORBITAL_CAPTURE: 0.35 }, material: "glass" },
};

// Calibration offsets keep the archetype distribution over the historical dictionary
// roughly even (tested in tests/genome.test.ts). They are part of the grammar version.
export const CALIBRATION: Record<Archetype, number> = {
  // fitted by scripts/calibrate.ts over 6,000 dictionary triples (grammar v1)
  CRYSTALLIZATION: -0.153, VORTEX: 0.014, FRACTURE: 0.004, REACTION_DIFFUSION: 0.053,
  ORBITAL_CAPTURE: 0.039, BRANCHING_GROWTH: 0.096, STRANGE_ATTRACTOR: -0.016, DIMENSIONAL_FOLD: -0.117,
};

export function conceptMechanism(c: Concept): Mechanism {
  const m = (c.sourceMetadata?.mechanism as string | undefined) ?? c.tags?.find((t) => (MECHS as string[]).includes(t));
  if (m && (MECHS as string[]).includes(m)) return m as Mechanism;
  return MECHS[fnv1a("mech:" + normalizeName(c.name)) % 4];
}

/** Latent visual signature of one concept. Depends only on the concept (name, field,
 *  mechanism), never on its partners or the seed. */
export function encodeConcept(c: Concept): ConceptSignature {
  const key = normalizeName(c.name);
  const r = mulberry32(fnv1a("concept:" + key));
  const field = c.field ? FIELD[c.field] : undefined;
  const mech = conceptMechanism(c);
  const hue = field ? (field.hue + (r() - 0.5) * 0.14 + 1) % 1 : r();
  const affinity = {} as Record<Archetype, number>;
  for (const a of ARCHETYPES) {
    affinity[a] = (MECH_AFFINITY[mech][a] ?? 0.1) * 0.8 + (field?.aff[a] ?? 0.15) * 0.6 + r() * 0.55;
  }
  return {
    hue,
    sat: 0.55 + r() * 0.4,
    warmth: r(),
    density: r(),
    angularity: mech === "constraint" || mech === "structure" ? 0.4 + r() * 0.6 : r() * 0.6,
    flow: mech === "dynamics" ? 0.5 + r() * 0.5 : r() * 0.7,
    branchiness: r(),
    symmetry: 2 + Math.floor(r() * 7),
    elasticity: r(),
    brittleness: mech === "constraint" ? 0.5 + r() * 0.5 : r() * 0.7,
    chaos: mech === "dynamics" ? 0.4 + r() * 0.6 : r() * 0.6,
    rhythm: r(),
    scale: 0.6 + r() * 0.8,
    spin: r() * 2 - 1,
    shape: SHAPES[Math.floor(r() * SHAPES.length)],
    material: field?.material && r() < 0.6 ? field.material : MATERIALS[Math.floor(r() * MATERIALS.length)],
    mechanism: mech,
    affinity,
  };
}

const W = [0.5, 0.3, 0.2]; // positional weights: order matters

function weighted(sigs: ConceptSignature[], f: (s: ConceptSignature) => number): number {
  return sigs.reduce((acc, s, i) => acc + W[i] * f(s), 0);
}

function entryDir(rng: () => number, k: number, twist: number): [number, number, number] {
  // three bodies arrive from roughly separated directions; twist rotates the frame
  const base = (k / 3) * Math.PI * 2 + twist * 1.2 + (rng() - 0.5) * 0.6;
  const elev = (rng() - 0.5) * 1.1;
  return [Math.cos(base) * Math.cos(elev), Math.sin(elev), Math.sin(base) * Math.cos(elev)];
}

export function collisionOperator(
  A: ConceptSignature, B: ConceptSignature, C: ConceptSignature, seed: number,
): VisualGenome {
  const sigs = [A, B, C];
  const rng = mulberry32(fnv1a(`op:${seed}`));
  // antisymmetric order signal: swapping A and B flips its sign
  const twist = A.spin * B.rhythm - B.spin * A.rhythm + 0.5 * (A.flow * C.angularity - C.flow * A.angularity);

  const scores = {} as Record<Archetype, number>;
  for (const a of ARCHETYPES) {
    const lin = weighted(sigs, (s) => s.affinity[a]);
    const inter = 0.35 * A.affinity[a] * B.affinity[a] - 0.15 * B.affinity[a] * C.affinity[a];
    scores[a] = lin + inter + CALIBRATION[a] + rng() * 0.32;
  }
  const archetype = ARCHETYPES.reduce((best, a) => (scores[a] > scores[best] ? a : best), ARCHETYPES[0]);

  const turbulence = clamp01(Math.abs(A.flow - B.angularity) * 0.8 + C.chaos * 0.5 + rng() * 0.15);
  const symmetry = 2 + ((A.symmetry * 3 + B.symmetry * 2 + C.symmetry + (seed % 5)) % 7);
  const elasticity = clamp01(weighted(sigs, (s) => s.elasticity) + (A.elasticity - C.elasticity) * 0.2);
  const brittle = weighted(sigs, (s) => s.brittleness);
  const matSig = sigs[rng() < 0.55 ? 0 : rng() < 0.6 ? 1 : 2];

  const bodies = sigs.map((s, k): BodyGene => ({
    shape: s.shape,
    hue: s.hue,
    sat: s.sat,
    size: 0.55 + s.scale * 0.45,
    spin: s.spin,
    entry: entryDir(rng, k, twist),
    material: s.material,
  })) as [BodyGene, BodyGene, BodyGene];

  const axisRaw: [number, number, number] = [rng() - 0.5, 1 + rng(), rng() - 0.5];
  const al = Math.hypot(...axisRaw);

  const styles: VisualGenome["collisionStyle"][] = ["fusion", "penetration", "interference", "capture", "shatter", "nucleation"];
  const evolutions: VisualGenome["evolution"][] = ["breathe", "drift", "pulse", "cycle", "precess"];

  const params: number[] = [];
  for (let i = 0; i < 8; i++) {
    const s = sigs[i % 3];
    const src = [s.density, s.flow, s.branchiness, s.chaos, s.rhythm, s.elasticity, s.angularity, s.warmth][i];
    params.push(clamp01(src * 0.6 + rng() * 0.4 + (i === 0 ? twist * 0.1 : 0)));
  }

  return {
    version: 1,
    seed,
    archetype,
    archetypeScores: scores,
    primitive: ({
      CRYSTALLIZATION: "points", VORTEX: "fibres", FRACTURE: "shards", REACTION_DIFFUSION: "surface",
      ORBITAL_CAPTURE: "rings", BRANCHING_GROWTH: "branches", STRANGE_ATTRACTOR: "ribbons", DIMENSIONAL_FOLD: "points",
    } as const)[archetype],
    topology: pick(rng, ["sphere", "torus", "knot", "lattice", "tree", "cloud", "klein", "shell"] as const),
    symmetry,
    particleCount: 0.55 + weighted(sigs, (s) => s.density) * 0.45,
    branchingFactor: 2 + Math.floor(weighted(sigs, (s) => s.branchiness) * 3.99),
    fieldForces: {
      curl: clamp01(weighted(sigs, (s) => s.flow) + twist * 0.3),
      radial: clamp01(weighted(sigs, (s) => 1 - s.flow) * 0.9),
      axial: clamp01(Math.abs(twist) * 0.8 + rng() * 0.3),
    },
    attractorCount: 1 + Math.floor(clamp01(C.chaos * 0.6 + rng() * 0.5) * 4.99),
    turbulence,
    elasticity,
    fractureThreshold: clamp01(1 - brittle),
    rotation: { axis: [axisRaw[0] / al, axisRaw[1] / al, axisRaw[2] / al], speed: 0.04 + Math.abs(twist) * 0.12 + rng() * 0.06 },
    distortion: clamp01(C.chaos * 0.5 + Math.abs(twist) * 0.5),
    material: { kind: matSig.material, emission: 0.5 + rng() * 0.5, hueShift: (twist * 0.08 + 1) % 1 },
    lifetime: 6 + rng() * 10,
    mutationRate: clamp01(weighted(sigs, (s) => s.chaos) * 0.8 + rng() * 0.2),
    collisionStyle: styles[Math.floor(clamp01(brittle * 0.6 + rng() * 0.4) * 5.99)],
    evolution: evolutions[Math.floor(rng() * evolutions.length)],
    timing: { approach: 1.8 + rng() * 0.8, collide: 0.8 + rng() * 0.5, emerge: 2.6 + rng() * 1.4 },
    bodies,
    twist,
    params,
  };
}

export function compileCollision(concepts: [Concept, Concept, Concept], seed: number): VisualGenome {
  const [A, B, C] = concepts.map(encodeConcept);
  return collisionOperator(A, B, C, seed >>> 0);
}

/** Force a specific archetype (showcase curation, debugging). Everything else in the
 *  genome still comes from the grammar. */
export function withArchetype(g: VisualGenome, a: Archetype): VisualGenome {
  return { ...g, archetype: a };
}

export const seedFor = (...parts: (string | number)[]) => {
  const r = rngFrom(...parts);
  return Math.floor(r() * 2 ** 31);
};
