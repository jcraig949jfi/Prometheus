"""
MAP-Elites evolutionary loop.

Parents chosen by tournament over archive; mutation operates on SUB-GENES
independently (type-preserving: preserves quadratic / ridge / gmm character).
Crossover: uniform at sub-gene boundary.

Fitness for placement = multi-component weighted scalar from fitness.py.

Archive: {cell_key -> (Landscape, DescriptorResult, trajs, disagreement, fitness)}.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np

from ergon.meta.landscape import (
    Landscape, QuadGene, RidgeGene, GaussGene, FourierGene,
    MODE_SAMPLERS, sample_mixed_landscape,
)
from ergon.meta.descriptors import (
    compute_descriptors, cell_key, fit_quantile_edges, DESCRIPTOR_NAMES,
    DescriptorResult,
)
from ergon.meta.optimizers import run_panel
from ergon.meta.trajectory import assign_final_basin
from ergon.meta.fitness import (
    compute_disagreement, weighted_scalar, DisagreementComponents,
)


# ---------- archive entry ----------------------------------------------------

@dataclass
class ArchiveEntry:
    landscape: Landscape
    descriptor: DescriptorResult
    trajs: list
    disagreement: DisagreementComponents
    fitness: float
    generation: int
    cell: tuple


# ---------- mutation ---------------------------------------------------------

def _mutate_quad(q: QuadGene, rng, sigma: float = 0.2) -> QuadGene:
    return QuadGene(d=q.d, upper=q.upper + sigma * rng.standard_normal(q.upper.shape))


def _mutate_ridge(r: RidgeGene, rng, sigma: float = 0.2) -> RidgeGene:
    u = r.direction + sigma * 0.3 * rng.standard_normal(r.direction.shape)
    u = u / (np.linalg.norm(u) + 1e-12)
    return RidgeGene(
        direction=u,
        amplitude=r.amplitude + sigma * rng.standard_normal(),
        bias=r.bias + sigma * rng.standard_normal(),
        width=max(0.1, r.width + sigma * 0.3 * rng.standard_normal()),
        shape=r.shape,
    )


def _mutate_gauss(g: GaussGene, rng, sigma: float = 0.2) -> GaussGene:
    return GaussGene(
        center=g.center + sigma * rng.standard_normal(g.center.shape),
        log_sigma=g.log_sigma + sigma * 0.3 * rng.standard_normal(g.log_sigma.shape),
        weight=g.weight + sigma * rng.standard_normal(),
    )


def _mutate_fourier(f: FourierGene, rng, sigma: float = 0.2) -> FourierGene:
    omega = f.omega + sigma * 0.3 * rng.standard_normal(f.omega.shape)
    return FourierGene(
        omega=omega,
        phase=(f.phase + sigma * 0.5 * rng.standard_normal()) % (2 * np.pi),
        amplitude=f.amplitude + sigma * rng.standard_normal(),
    )


def mutate(L: Landscape, rng: np.random.Generator, sigma: float = 0.2) -> Landscape:
    """Gaussian perturbation on each sub-gene; mode preserved."""
    new_quad = _mutate_quad(L.quad, rng, sigma)
    new_ridges = [_mutate_ridge(r, rng, sigma) for r in L.ridges]
    new_gmm = [_mutate_gauss(g, rng, sigma) for g in L.gmm]
    new_fourier = [_mutate_fourier(f, rng, sigma) for f in L.fourier]
    return Landscape(
        d=L.d, quad=new_quad, ridges=new_ridges, gmm=new_gmm, fourier=new_fourier,
        mode=L.mode,
        genome_id=f"mut_{rng.integers(1 << 31)}",
        parent_ids=(L.genome_id,),
    )


def crossover(A: Landscape, B: Landscape, rng: np.random.Generator) -> Landscape:
    """Uniform crossover at sub-gene boundary; requires same mode for coherence."""
    if A.mode != B.mode:
        return mutate(A, rng)

    # 50/50 per sub-gene element
    quad_mask = rng.random(A.quad.upper.shape) < 0.5
    new_quad = QuadGene(
        d=A.d,
        upper=np.where(quad_mask, A.quad.upper, B.quad.upper),
    )

    # Ridges + GMMs: take by-index, fall back to A if lengths differ
    n_r = min(len(A.ridges), len(B.ridges))
    new_ridges = [A.ridges[i] if rng.random() < 0.5 else B.ridges[i]
                  for i in range(n_r)]
    # Pad with A's remaining (or B's if A shorter)
    if len(A.ridges) > n_r:
        new_ridges.extend(A.ridges[n_r:])
    elif len(B.ridges) > n_r:
        new_ridges.extend(B.ridges[n_r:])

    n_g = min(len(A.gmm), len(B.gmm))
    new_gmm = [A.gmm[i] if rng.random() < 0.5 else B.gmm[i] for i in range(n_g)]
    if len(A.gmm) > n_g:
        new_gmm.extend(A.gmm[n_g:])
    elif len(B.gmm) > n_g:
        new_gmm.extend(B.gmm[n_g:])

    n_f = min(len(A.fourier), len(B.fourier))
    new_fourier = [A.fourier[i] if rng.random() < 0.5 else B.fourier[i]
                   for i in range(n_f)]
    if len(A.fourier) > n_f:
        new_fourier.extend(A.fourier[n_f:])
    elif len(B.fourier) > n_f:
        new_fourier.extend(B.fourier[n_f:])

    return Landscape(
        d=A.d, quad=new_quad, ridges=new_ridges, gmm=new_gmm, fourier=new_fourier,
        mode=A.mode,
        genome_id=f"xover_{rng.integers(1 << 31)}",
        parent_ids=(A.genome_id, B.genome_id),
    )


# ---------- archive + main loop ----------------------------------------------

class MAPEliteArchive:
    def __init__(self, edges: dict):
        self.edges = edges
        self.entries: Dict[tuple, ArchiveEntry] = {}
        self.history: list = []   # all evaluated entries

    def try_place(self, entry: ArchiveEntry) -> bool:
        cell = entry.cell
        self.history.append(entry)
        cur = self.entries.get(cell)
        if cur is None or entry.fitness > cur.fitness:
            self.entries[cell] = entry
            return True
        return False

    def sample_parents(self, rng, n: int = 2) -> list:
        if len(self.entries) < 2:
            return list(self.entries.values())
        keys = list(self.entries.keys())
        picks = rng.choice(len(keys), size=min(n, len(keys)), replace=False)
        return [self.entries[keys[i]] for i in picks]

    def coverage(self, total_cells: int) -> float:
        return len(self.entries) / total_cells


def evaluate_landscape(L: Landscape, generation: int, rng,
                       descriptor_edges: dict,
                       budget: int = 500, box: float = 4.0) -> ArchiveEntry:
    """Full evaluation pipeline for one landscape."""
    desc = compute_descriptors(L, rng=rng)
    trajs = run_panel(L, budget=budget, box=box)
    # Assign final basins from discovered minima
    for t in trajs:
        t.final_basin = assign_final_basin(t, desc.minima, box_scale=box)
    disagreement = compute_disagreement(trajs)
    fitness = weighted_scalar(disagreement)
    cell = cell_key(desc, descriptor_edges)
    return ArchiveEntry(
        landscape=L, descriptor=desc, trajs=trajs,
        disagreement=disagreement, fitness=fitness,
        generation=generation, cell=cell,
    )


def run_evolution(
    n_generations: int,
    children_per_gen: int,
    seed: int = 123,
    pilot_sample_size: int = 40,
    d: int = 2,
    budget: int = 500,
    mutation_sigma: float = 0.2,
    box: float = 4.0,
    verbose: bool = True,
) -> MAPEliteArchive:
    """Full MAP-Elites run. Serial execution (Phase 2a default)."""
    rng = np.random.default_rng(seed)

    # --- 1. Pilot sample to fit quantile bin edges ---
    if verbose:
        print(f"[evolve] pilot sample of {pilot_sample_size} for quantile binning...")
    pilot_descs = []
    for _ in range(pilot_sample_size):
        L = sample_mixed_landscape(d=d, rng=rng)
        desc = compute_descriptors(L, rng=rng)
        pilot_descs.append(desc)
    edges = fit_quantile_edges(pilot_descs)
    if verbose:
        print(f"[evolve] quantile edges fit:")
        for n, e in edges.items():
            print(f"  {n}: {e}")

    archive = MAPEliteArchive(edges)

    # --- 2. Seed archive with pilot landscapes evaluated on optimizer panel ---
    if verbose:
        print(f"[evolve] seeding archive with {pilot_sample_size} evaluated pilot landscapes...")
    for g_idx in range(pilot_sample_size):
        L = sample_mixed_landscape(d=d, rng=rng)
        entry = evaluate_landscape(L, generation=0, rng=rng,
                                   descriptor_edges=edges, budget=budget, box=box)
        archive.try_place(entry)
    if verbose:
        print(f"[evolve] initial archive: {len(archive.entries)} cells filled")

    # --- 3. Evolutionary loop ---
    total_cells = 3 ** len(DESCRIPTOR_NAMES)
    for gen in range(1, n_generations + 1):
        for _ in range(children_per_gen):
            if len(archive.entries) < 2 or rng.random() < 0.3:
                # Occasionally sample fresh from a random mode to keep diversity
                L = sample_mixed_landscape(d=d, rng=rng)
            else:
                parents = archive.sample_parents(rng, n=2)
                if len(parents) == 2 and rng.random() < 0.5:
                    L = crossover(parents[0].landscape, parents[1].landscape, rng)
                else:
                    L = mutate(parents[0].landscape, rng, sigma=mutation_sigma)
            entry = evaluate_landscape(L, generation=gen, rng=rng,
                                       descriptor_edges=edges, budget=budget, box=box)
            archive.try_place(entry)
        if verbose:
            cov = archive.coverage(total_cells)
            best = max((e.fitness for e in archive.entries.values()), default=0)
            print(f"[evolve] gen {gen:3d}: cells={len(archive.entries)}/{total_cells} "
                  f"({100*cov:.0f}%)  best_fit={best:.3f}")

    return archive
