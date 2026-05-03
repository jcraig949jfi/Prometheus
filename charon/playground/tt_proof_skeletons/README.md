# TT Proof Skeletons — Playground

Evolve sequences of tensor-train transformation operators. MAP-Elites archive
keyed on (achieved max rank × approximation error) preserves a distinct
"strategy" per cell.

Status: **phase 1 works.** The machinery finds true rank, populates the
frontier, and archives genuinely diverse sequences in adjacent cells.

## Phase 1 — clean starting point

Per the brief: approximate a high-dimensional function with a TT, GA over
operator sequences, MAP-Elites with axes (TT rank, approximation error).

**Target**: f(x₁,…,x₆) = sin⊗⁶(kx) + cos⊗⁶(kx) + poly⊗⁶(x), xᵢ ∈ {0,…,7}.
True TT rank = 3 by construction. N⁶ = 262 144 entries.

**Operators** (each: TT → TT):
| Op | Effect | Proof-step analogue |
|---|---|---|
| `ansatz(rank)` | TT-SVD of target at given rank cap | posit a low-complexity form |
| `refine(eps)` | SVD rounding to tolerance | tighten / canonicalise |
| `perturb(sigma)` | Gaussian noise on cores | introduce symmetry-breaking term |
| `expand(bond,amt)` | grow one bond rank with random pad | add a new degree of freedom |
| `compress(target)` | truncate to rank budget | enforce canonical form |
| `symmetrize` | average with mode-reversed copy | invoke symmetry |
| `reseed(rank)` | replace with fresh random TT | restart from scratch |

**Search**: MAP-Elites with GA variation — tournament-by-cell, mutation
(replace/insert/delete/shuffle op), single-point crossover on sequences.

**Run** (`POP=30 GENS=40 python evolve_tt.py`, ~36 s):

```
Rank\ErrBin     0      1      2      3      4     13
      1      7e-01   .      .      .      .      .
      2      7e-01  1e-02  8e-03   .      .      .
      3      1e-01  1e-02  8e-03   .      .    1e-14   <- true rank, nailed
      4      2e-01  2e-02  1e-03  2e-04  2e-05  1e-14
      5      4e-01  2e-02  1e-03  3e-04  2e-05  1e-14
      6      2e-01  1e-02  1e-03  9e-04  2e-05  1e-14
      7      2e-01  2e-02  1e-03   .     2e-05  1e-14
      8      2e-01  2e-02  1e-03   .     2e-05  1e-14
      9      2e-01   .     3e-03   .      .      .
     10        .     .      .      .     3e-05    .
```

39/60 cells populated. Pareto frontier (best err per rank): 7.06e-01 → 7.85e-03
at rank 2 → 1.05e-14 at true rank 3 → machine precision beyond.

## What the archive tells us

Three sequences, all archived, all reaching rank ≤ 4 at error ≤ 1e-14:

```
rank=3, err=1.05e-14, len=4:  [ansatz, ansatz, refine, compress]
rank=4, err=1.38e-14, len=6:  [ansatz, ansatz, ansatz, reseed, ansatz, compress]
rank=8, err=1.49e-14, len=8:  [ansatz, symmetrize, perturb, ansatz, perturb,
                                compress, refine, ansatz]
```

These are genuinely different *strategies* for the same theorem. Phase-1 is a
functional proof-of-concept that the (GA + MAP-Elites) pairing does preserve
strategy diversity rather than collapsing to a single best.

## What phase 1 doesn't yet probe

`ansatz` is a cheat — it's TT-SVD of the full target. That makes the "proof"
trivially one-shot. For the phase-2 probe to be interesting the operators must
work without direct access to the target value at every grid point.

## Phase-2 on-ramps (three directions, increasing ambition)

### (A) Sample-only learning
Replace `ansatz` with `fit_to_samples(n)` that sees f only at n uniformly
random grid points. Operators become a real search: when to sample, when to
exploit structure, when to add degrees of freedom. MAP-Elites axis gains
*sample budget* as a third behaviour descriptor.

### (B) Charon-domain target
Target tensor = a real dataset from our shadow tensor or an LMFDB slice
(e.g., EC rank-0 × nbp × CM-disc × torsion × conductor-decile). Fitness =
compression ratio at fixed reconstruction error. MAP-Elites axes =
(compression, reconstruction, strategy style). Ties directly to the
Harmonia TT-cross exploration already on the pillar.

### (C) The actual proof-skeleton probe (ambitious)
Target = a known algebraic identity encoded as LHS−RHS tensor. Operators =
generalised creative-telescoping primitives (shift, Gosper step, residue,
substitution). Fitness = residual norm after applying sequence. MAP-Elites
axes = (sequence length × residual × *style bucket* via operator-entropy
signature — algebraic / combinatorial / analytic).

A positive result would look like: evolution recovers the WZ-style proof of a
simple binomial identity as a short sequence, with different cells
corresponding to genuinely different proof-classes. Even partial success
(identity reduced to smaller canonical piece) is informative about the
boundary between search and reasoning.

## Files

```
evolve_tt.py        phase-1 driver
archive.json        saved MAP-Elites archive (39 cells, full genomes)
run1.log            run transcript
```
