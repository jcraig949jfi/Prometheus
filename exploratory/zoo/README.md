# Zoo — High-Dimensional Function Approximation Playground

**Status:** MVP, Phase 1 (2026-04-24).
**Discipline tier:** standalone playground. Verdicts here do NOT migrate to the landscape tensor. Calibration anchors ARE load-bearing from day one. Not yet Pattern-30 / null-protocol tier.
**Toolkit pointer:** referenced from `harmonia/memory/methodology_toolkit.md` as `TT_APPROX_MAP@v0` CANDIDATE.

---

## What this is

A MAP-Elites-driven archive of tensor-train (TT) approximations to a catalog of test functions. Each cell holds the (function, TT-approximation) pair whose behavior descriptors landed in that cell. The **product is the map**, not the individual approximations — where in function-space does TT-structure compress, and where does it surprise us.

Coordinate system of legibility: descriptors define a grid; MAP-Elites populates it; the map reveals which function-shapes admit which compressions.

## What it is NOT (yet)

- **Not substrate-tier.** No F-IDs, no P-IDs, no entries in `signals.specimens`. Verdicts live in `zoo/results/*.json`.
- **Not null-audited.** No block-shuffle analog wired in yet. A Phase-2 `decomposition_lineage` check (Pattern-30 analog) is specified but not implemented.
- **Not a discovery tool** — it's an instrument-calibration playground. We're building the ruler before claiming measurements.

## Epistemic guardrails (Phase 1)

1. **Calibration anchors are load-bearing.** Every experiment includes functions with known TT rank (low or incompressible). If the archive fails to place a calibration anchor in its expected cell band, the experiment is INVALID — not a finding.
2. **No cross-experiment aggregation until Phase 2.** Each run is a single snapshot. No "44 cells populated" counts.
3. **Reward-capture watch.** A function that lands in an unexpected cell is interesting if and only if calibration anchors landed correctly. Novelty without calibration = artifact.

## Phase roadmap

**Phase 1 (now):** smallest vertical slice.
- 3 functions: `prod(x_i)` (calibration, TT-rank 1), random tensor (calibration, incompressible), `tanh(sum of pairwise products)` (frontier).
- TT via TT-SVD (numpy).
- 2 descriptors: log₁₀(params), log₁₀(L² relative error).
- MAP-Elites 20×20 grid, rank-perturbation mutation.
- 50-generation run, JSON archive dump.

**Phase 2:** second descriptor pair (spectral decay, Lipschitz ratio). DMRG local refinement. Separable-sum calibration. Frontier expansion (Lorenz grid, Gabor packet, 2D heat PDE). `decomposition_lineage` Pattern-30 analog.

**Phase 3:** graduation to parallel substrate. F-IDs per function, P-IDs per descriptor + rank scheme, `zoo_tensor`, symbol promotion `TT_APPROX_MAP@v0 → @v1`, null protocol definition, `signals.specimens` integration.

## Layout

```
zoo/
  README.md                  # this file
  functions/                 # test functions (calibration + frontier)
  tt/                        # tensor-train core + evolution operators
  map_elites/                # grid, archive, loop
  descriptors/               # behavior descriptor functions (Phase 2+)
  experiments/               # entry-point runners
  results/                   # JSON archive dumps (gitignored)
  manifests/                 # experiment specs + calibration verdict contracts
```

## Running the MVP

```bash
cd D:/Prometheus
python -m zoo.experiments.run_mvp
```

Expected runtime: under 60s on CPU. Output: `zoo/results/mvp_<timestamp>.json` + console calibration-verdict line.

## Calibration verdict contract (Phase 1)

For the run to be considered VALID:

- `prod(x_i)` on a 6D grid must land at log₁₀(params) ≤ 2.5 with log₁₀(L² relative error) ≤ -6 at some achievable rank. (Expected TT-rank 1, ~12 params, near-exact.)
- Random tensor at the same shape must NOT land below log₁₀(params) ≈ log₁₀(dense_size) - 0.3 — i.e., it should resist compression.

If either fails, the MVP instrument itself is broken, not the functions.
