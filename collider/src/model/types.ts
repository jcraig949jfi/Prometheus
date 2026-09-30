// Core data model. The visual genome is the contract between the deterministic
// grammar (model/genome.ts) and the renderers (render/archetypes/*).

export type Mechanism = "structure" | "dynamics" | "constraint" | "measure";

export interface Concept {
  id: string;
  name: string;
  field?: string;
  tags?: string[];
  sourceMetadata?: Record<string, unknown>;
}

/** Where a collision's triple came from. Kept explicit so historical and new
 *  content are never silently mixed. */
export type SourceKind = "hephaestus" | "generated" | "curated" | "user";

export interface Provenance {
  source: SourceKind;
  artifactPath?: string;
  artifactLine?: number;
  historicalId?: string;
  derivedFromHistorical?: string; // a remix/reorder whose root was a historical record
}

export interface Mutation {
  kind: "replace" | "reorder";
  replacedIndex?: 0 | 1 | 2;
  oldConcept?: string;
  newConcept?: string;
  order?: [number, number, number];
}

export interface Synthesis {
  title: string | null;
  reasoningShard: string;
  speculativeMechanism?: string;
  kind: "historical-nous-analysis" | "template-speculation" | "external";
}

export type Archetype =
  | "CRYSTALLIZATION"
  | "VORTEX"
  | "FRACTURE"
  | "REACTION_DIFFUSION"
  | "ORBITAL_CAPTURE"
  | "BRANCHING_GROWTH"
  | "STRANGE_ATTRACTOR"
  | "DIMENSIONAL_FOLD";

export type BodyShape = "shell" | "ring" | "lattice" | "helix" | "disc" | "filament";
export type MaterialKind = "glass" | "metal" | "plasma" | "bio" | "ink" | "ice";

/** Per-concept latent signature (all fields in [0,1] unless stated). */
export interface ConceptSignature {
  hue: number;
  sat: number;
  warmth: number;
  density: number;
  angularity: number;
  flow: number;
  branchiness: number;
  symmetry: number; // integer 2..8
  elasticity: number;
  brittleness: number;
  chaos: number;
  rhythm: number;
  scale: number;
  spin: number; // [-1,1]
  shape: BodyShape;
  material: MaterialKind;
  mechanism: Mechanism;
  affinity: Record<Archetype, number>;
}

export interface BodyGene {
  shape: BodyShape;
  hue: number;
  sat: number;
  size: number;
  spin: number;
  entry: [number, number, number]; // unit direction the body arrives from
  material: MaterialKind;
}

export interface VisualGenome {
  version: 1;
  seed: number;
  archetype: Archetype;
  archetypeScores: Record<Archetype, number>;
  primitive: "points" | "ribbons" | "shards" | "surface" | "branches" | "rings" | "fibres";
  topology: string;
  symmetry: number;
  particleCount: number; // fraction of the device budget, 0.35..1
  branchingFactor: number; // 2..5
  fieldForces: { curl: number; radial: number; axial: number };
  attractorCount: number; // 1..5
  turbulence: number;
  elasticity: number;
  fractureThreshold: number;
  rotation: { axis: [number, number, number]; speed: number };
  distortion: number;
  material: { kind: MaterialKind; emission: number; hueShift: number };
  lifetime: number;
  mutationRate: number;
  collisionStyle: "fusion" | "penetration" | "interference" | "capture" | "shatter" | "nucleation";
  evolution: "breathe" | "drift" | "pulse" | "cycle" | "precess";
  timing: { approach: number; collide: number; emerge: number };
  bodies: [BodyGene, BodyGene, BodyGene];
  twist: number; // antisymmetric in (A,B): the order signal
  params: number[]; // 8 archetype-specific knobs in [0,1], extensible
}

export interface Collision {
  id: string;
  seed: number;
  concepts: [Concept, Concept, Concept];
  provenance: Provenance;
  visualGenome: VisualGenome;
  synthesis?: Synthesis;
  parentCollisionId?: string;
  mutation?: Mutation;
  createdAt?: string; // only for user-made collisions
}
