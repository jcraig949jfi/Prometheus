# tensor_decomp_qd — Quality-Diversity Archive for Low-Rank Tensor Decompositions

**Sibling project to Prometheus substrate.**

Thesis: produce a **behavior-diversity archive** (rank × canonical sparsity
× symmetry × coefficient-complexity) over tensor decompositions of known
tensors (matmul, polynomial mult, convolution), rather than chasing
single-point rank minima like AlphaTensor, AlphaEvolve, Flip Graph Search,
or StrassenNet do.

The *archive* is the product. Strassen is one cell in that archive; the
other cells are the unclaimed territory.

---

## Status (2026-04-23)

| Pilot | Outcome | Summary |
|---|---|---|
| `pilot_F2_2x2/` | B1 | Strassen isolated; rank-7 effectively unique over F_2 |
| `pilot_F2_3x3/` | B | Laderman verified + seeded; flip-graph moves implemented but don't fire over F_2 |
| `pilot_F3_2x2/` | (next) | Richer gauge (O_2(F_3) has 8 elements vs 2 over F_2); expected to show outcome A |

See each pilot's `PILOT_REPORT.md` for the full picture.

---

## Why F_3 next (not bigger)

The 2x2 + 3x3 pilots over F_2 converge on a single structural cause:
**char-2 orthogonality is too restrictive**. Over F_2:
- `O_2(F_2) = 2` (I and swap)
- `O_3(F_2) = 6` (permutation matrices only)
- Matmul isotropy subgroup shrinks from ~|GL_n|^3 to a small fraction

Over larger fields this collapse doesn't happen. F_3 is the smallest
field where this is no longer an issue:
- `O_2(F_3) = 8` elements (dihedral D_4)
- Matmul isotropy subgroup for 2x2 over F_3: 8 × 48 × 8 = 3072 elements
- Column scaling gauge is non-trivial (F_3* has 2 elements), adding
  real canonicalization work

If the 2x2 F_3 pilot shows outcome A (multiple rank-7 orbits, non-trivial
Pareto fronts, reseed stability), the QD thesis works and we can push to
3x3 F_3 or ℚ. If B again, the QD approach needs substantial
reformulation (probably toward LLM-assisted whole-decomposition edits).

---

## Architecture

Every pilot directory follows the same structure:

```
pilot_<ring>_<size>/
  core.py            # tensor definition, reconstruction, canonicalization helpers
  gauge.py           # GL_n enumeration, matmul isotropy subgroup, canonicalize
  known_decomps.py   # naive + verified seed(s)
  descriptors.py     # rank, canonical sparsity, stabilizer (all gauge-invariant)
  flipgraph.py       # rank-2 tensor decomposition + 3-to-2 + 2-to-2 moves
  map_elites.py      # QD loop, forbidden-cell enforcement, archive
  test_gauge.py      # canonicalizer unit tests (hard gate before any run)
  run_pilot.py       # full orchestrator: unit tests -> reseeded runs -> report
  PILOT_REPORT.md    # post-run outcome diagnosis + next steps
```

The canonicalizer is the load-bearing primitive: everything else depends
on its byte-stability under gauge action. Unit tests are the hard gate.

---

## Reusable infrastructure

Shared across pilots (factor-out planned once architecture stabilizes):
- **`laderman_solve.py` pattern** — given candidate products, solve for
  output formulas via Gaussian elimination over F_p. Generalizes to any
  published rank-r decomposition.
- **Vectorized bit-packed canonicalize** — ~200 ms per call at n=3 over
  F_2; scales reasonably to F_3.
- **Flip-graph primitives** (`rank_2_tensor_decomp`, `try_reduce_3_to_2`,
  `try_swap_2_to_2`) — F_2 implementation; F_p extension is mechanical
  mod-p arithmetic replacement.

---

## Running the pilots

```
# Unit tests (must pass first — canonicalizer correctness)
python -m tensor_decomp_qd.pilot_F2_2x2.test_gauge
python -m tensor_decomp_qd.pilot_F2_3x3.test_gauge

# Full pilot runs
python -m tensor_decomp_qd.pilot_F2_2x2.run_pilot
python -m tensor_decomp_qd.pilot_F2_3x3.run_pilot

# Neighborhood probes (diagnostic)
python -m tensor_decomp_qd.pilot_F2_2x2.neighborhood_probe
python -m tensor_decomp_qd.pilot_F2_2x2.brute_force_probe
```

All scripts deterministic under fixed seeds. No external APIs or network
calls. Requires numpy only.

---

## Relationship to Prometheus substrate

- Not an F-ID in the Prometheus tensor (this is a different domain).
- Discipline inherited: calibration-first, SHADOWS_ON_WALL
  lens-counting, B1-vs-B2 distinction in negative results, forbidden-
  cell enforcement operational-not-advisory.
- If the project matures, a `TENSOR_DECOMP_LENS@v1` entry in
  `harmonia/memory/methodology_toolkit.md` would be the bridge back.

---

## Pilot decision tree

Current state:

```
F_2 pilots → outcome B (char-2 orthogonality too restrictive)
    |
    v
F_3 2x2 pilot (richer gauge)
    |
    ├── A: method works over F_3 → push to 3x3 F_3 or Q
    |
    └── B: method still fails → escalate to:
              - 4-to-3 flip-graph moves (harder rank-3 decomp primitive)
              - Full matmul isotropy (transposition symmetry)
              - LLM-assisted whole-decomposition mutation
              - Different target tensors (convolution, polynomial mult)
```

---

## Provenance

- Lit scan: `harmonia/tmp/tensor_decomp_lit/SYNTHESIS.md`
- Session journals: `roles/Harmonia/worker_journal_sessionB_20260423.md`
- Memory: `project_tensor_decomp_qd` entry in auto-memory
- Started: 2026-04-23 by Harmonia_M2_sessionB
