# N4 note: which tt_digits topology mutations cuTensorNet makes cheap

Lane T (Nestor-T[m1-9ff9deec]), 2026-09-14. Evidence: primordial/ledger/rows/T/N4-timing-cutn.jsonl
(leased; plan_s per shape) and the tests in primordial/nv/tensornet/tests/test_tt_cutn.py.
Correctness is established before any cost claim: 32/32 oracle cells exact, and the stride cheat
is caught in every cell (N4-cutensornet-tt-digits-oracle).

## What a cuTensorNet plan depends on

A plan (Network + contract_path) is a function of the network's topology and extents only: the
labels, the core count, the bond dimension r, the action count A and the batch size B. Tensor
values do not enter it. That gives three classes of mutation.

| mutation class | examples | cuTensorNet cost | evidence |
|---|---|---|---|
| value-only | Gaussian mutate of alpha / G / Wo; crossover of equal-shape genomes; codebook swap | no replan: `reset_operands` + contract | test_planned_network_reused_across_genomes (3 genomes, one plan, exact) |
| extent change | bond dimension r (3 -> 4, rank grow/shrink); A; B | replan: 0.01-0.05 s at 16 cores, 0.19-0.37 s at 64 cores (leased rows) | plan_s is nearly flat in r (4..64) and in B (1024..1M); it scales with core count |
| topology change | core order permutation; add/delete a core (the stride cheat is a deletion); multi-read of one digit; a branch (tree instead of chain) | replan, same range as above; arbitrary graphs are allowed, not just chains | stride-2 networks planned in 0.005-0.05 s |

The first plan in a process paid 1.23 s (one-time library/handle init; the next d16 plan took 0.011 s).
Amortise it per process, not per genome.

## What this means for round 6 traits

- Cheap to search with cuTensorNet: every value mutation (the whole current tt_digits operator set) with
  zero replans. A population of equal-shape genomes shares one plan per (cores, r, B).
- Cheap enough per generation: bond-dimension and core-order/core-count mutations. Cache plans keyed
  by (cores, r, A, B, topology hash). Replan cost is at most ~0.4 s for 64 cores, so a population
  can hold a few dozen distinct topologies per generation before planning dominates.
- New and not possible in the torch bucket kernel without new code: non-chain topologies (trees, a digit
  read by two cores, shared cores). The bucket kernel is hard-wired to a left-to-right chain; the
  cuTensorNet path just takes a different label list.
- Not cheap: shapes that do not fit in device memory. d16 r64 B=1M reported a 16.3 GB cupy pool and a
  3.1 s median (vs 0.19 s at B=262k, ~16x for 4x rows), which reads as spill past the 16 GB card.
  The planner reported num_slices = 1 everywhere (no slicing chosen under default memory limits).

## Speed vs the torch bucket kernel (leased, 28 of 36 shapes; rows N4-timing-combine.json)

- Exactness holds on every measured cell on both sides, and the cuTN cheat is caught 5/5.
- cuTN executes faster on 22 of 28 shapes: 2.3-11.7x at B <= 16k, and about 1x at d64 r4 with B >= 262k.
  The bucket kernel wins at r >= 16 with large B (0.03-0.59x), where the cuTN pool runs into memory spill.
- Planning never dominates where cuTN wins: break-even at 0.8-45 executions, excluding the 1.23 s first-plan
  cell and a 1.00x tie.
- Confound: small-B e2e is CPU-dispatch dominated and the two sides ran under different host CPU load. The
  lease covers the GPU only, so the small-B ratios are recorded, not a clean kernel comparison.
- Missing: d64 r16 B >= 262k and all of d64 r64 (timeout, then a hung resume during the reboot quiesce).
