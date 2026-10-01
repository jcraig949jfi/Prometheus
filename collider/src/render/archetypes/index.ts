// Archetype registry. To add an archetype: add its name to `Archetype` in
// model/types.ts and ARCHETYPES in model/genome.ts, write a World subclass with a
// `build()` (and usually an `emerge()` GLSL function), and register it here.

import type { Archetype, Collision } from "../../model/types";
import type { World, WorldContext } from "../world";
import { VortexWorld } from "./vortex";
import { CrystalWorld } from "./crystal";
import { AttractorWorld } from "./attractor";
import { FractureWorld } from "./fracture";
import { ReactionWorld } from "./reaction";
import { OrbitalWorld } from "./orbital";
import { BranchingWorld } from "./branching";
import { FoldWorld } from "./fold";

type Ctor = new (c: Collision, ctx: WorldContext) => World;

export const ARCHETYPE_WORLDS: Record<Archetype, Ctor> = {
  VORTEX: VortexWorld,
  CRYSTALLIZATION: CrystalWorld,
  STRANGE_ATTRACTOR: AttractorWorld,
  FRACTURE: FractureWorld,
  REACTION_DIFFUSION: ReactionWorld,
  ORBITAL_CAPTURE: OrbitalWorld,
  BRANCHING_GROWTH: BranchingWorld,
  DIMENSIONAL_FOLD: FoldWorld,
};

export function createWorld(c: Collision, ctx: WorldContext): World {
  const W = ARCHETYPE_WORLDS[c.visualGenome.archetype];
  const w = new W(c, ctx);
  w.build();
  return w;
}

export const ARCHETYPE_BLURB: Record<Archetype, string> = {
  CRYSTALLIZATION: "nucleation · lattice growth · buckling",
  VORTEX: "toroidal flow · interlocking cores · axial jets",
  FRACTURE: "fusion shell · fracture · frozen explosion",
  REACTION_DIFFUSION: "Gray–Scott morphogenesis on a living membrane",
  ORBITAL_CAPTURE: "three-body choreography · captured rings",
  BRANCHING_GROWTH: "tropic branching · sap flow",
  STRANGE_ATTRACTOR: "integrated chaotic flow · ribbons",
  DIMENSIONAL_FOLD: "4D Hopf fibration · stereographic collapse",
};
