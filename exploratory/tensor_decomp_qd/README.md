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

| Pilot | Outcome | Key finding |
|---|---|---|
| `pilot_F2_2x2/` | B1 | Strassen isolated at Hamming ≥ 6; rank-7 effectively unique over F_2 |
| `pilot_F2_3x3/` | B | Laderman verified + seeded; flip-graph 3-to-2 and 2-to-2 moves don't fire (all 1771 triples have tensor rank 3; 0/253 pair-swaps give new orbit) |
| `pilot_F3_2x2/` | B1 | 100× better fitness rate than F_2, local connectivity within Strassen orbit, but still single rank-7 orbit → **rejects "char-2 is primary cause"** hypothesis |

See each pilot's `PILOT_REPORT.md` for the full diagnostic picture.

---

## What the calibration ladder has now established

Three hypotheses distinguished across the three pilots:

1. ~~**Char-2 orthogonality degeneracy**~~ — tested directly via 2x2 F_3
   pilot. Rejected as primary cause: F_3 has 128× richer gauge and
   100× higher fitness rate, yet same outcome.
2. **2x2 matmul tensor is too small** (supported): rank-7 of 2x2 matmul
   has essentially a single equivalence class under column-perm +
   scaling + basis-change over both F_2 and F_3.
3. **Factor-matrix Hamming geometry** (universal across all pilots):
   valid decompositions are isolated or sparsely connected in
   factor-matrix space. Mutation must bridge larger moves.

The ladder has **ruled out** a cheap fix (larger field) and **narrowed** the
real issue (tensor smallness + mutation geometry). The next substrate must
address both.

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

## Pilot decision tree (updated after F_3 pilot)

Current state:

```
F_2 pilots → outcome B  (char-2 hypothesis: not ruled out yet)
    |
    v
F_3 2x2 pilot → outcome B1 (char-2 hypothesis ruled out; tensor smallness is the cause)
    |
    v
NEXT: pick one of three directions
    |
    ├── (A) 3x3 F_2 with 4-to-3 flip-graph moves
    |      Requires rank-3 tensor decomposition primitive over F_2.
    |      Extends existing 3x3 F_2 infrastructure.
    |      Tests whether higher-arity moves break Laderman isolation.
    |
    ├── (B) less-saturated bilinear tensors (polynomial mult, convolution, group algebra)
    |      Fresh architecture but simpler tensors.
    |      Literature coverage is thinner — genuinely unclaimed.
    |
    └── (C) 3x3 F_3 with invariant-based canonicalization
           Blocked: |matmul isotropy| ≈ 10^10; brute-force infeasible.
           Would need gauge-invariant fingerprinting approach.
           Highest potential but biggest design cost.
```

---

## Provenance

- Lit scan: `harmonia/tmp/tensor_decomp_lit/SYNTHESIS.md`
- Session journals: `roles/Harmonia/worker_journal_sessionB_20260423.md`
- Memory: `project_tensor_decomp_qd` entry in auto-memory
- Started: 2026-04-23 by Harmonia_M2_sessionB
