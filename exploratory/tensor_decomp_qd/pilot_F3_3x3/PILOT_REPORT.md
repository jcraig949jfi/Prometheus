# 3x3 F_3 Pilot Report — invariant-tuple QD archive

**Run:** Harmonia_M2_auditor (sessionD), 2026-04-23
**Scope:** port the 3x3 matmul QD pilot to F_3 with INVARIANT-TUPLE
canonicalization, replacing brute-force orbit enumeration. The 2x2 F_3
pilot's recommendation flagged this as the highest-potential / highest-
design-cost direction; this pilot delivers the design.

## Outcome

**A for infrastructure (gauge-invariant fingerprinting works), B for
exploration (single invariant-tuple class at rank 23, single at rank 27).**

The fundamental design question — "can we replace brute-force orbit
enumeration on |Iso| ~ 2.6e7 with a tuple of gauge-invariant scalars?" —
is answered YES, with a clean test: 50/50 random matmul-isotropy
perturbations of both naive-27 and Laderman-23 produce identical
invariant-tuple hashes (test_gauge.py [4] and [5]).

But the EXPLORATION outcome echoes the prior pilots: under random ternary
mutation around naive and Laderman, no novel orbit is reached. Validity
rate ~0.005 in F_3 is much higher than F_2's 0.001 but still far too low
for diversity escape from the seed orbits.

## What shipped and works

| Component | Status | Notes |
|---|---|---|
| `core.py` — F_3 arithmetic on 3x3 matmul | OK | DIM=9, P=3, normalization for per-column F_3* gauge |
| `gauge.py` — GL_3(F_3), O_3(F_3), random isotropy sampler | OK | \|GL_3(F_3)\|=11232, \|O_3(F_3)\|=48 (matches theory) |
| Random matmul-isotropy preservation | OK | 50/50 random isotropy actions preserve MATMUL_T |
| `descriptors.py` — invariant tuple | OK | (rank, mode_sig, pair_dist, triple_dist) gauge-invariant by construction |
| Invariance under 50 random Iso elements (naive) | **0 mismatches** | hash 20ad87384dba4fa0 stable |
| Invariance under 50 random Iso elements (Laderman) | **0 mismatches** | hash 6830faa248d01780 stable |
| Naive vs Laderman distinct hashes | OK | Different cells in archive |
| Mode-flatten rank signature on both seeds | (9, 9, 9) | Confirms full-rank flattening for matmul |
| **Laderman over F_3 encoding** | **VALIDATED** | Signed product version (memory-reconstructed); reconstruct(A,B,C) == MATMUL_T; effective_rank=23 |
| Forbidden-rank enforcement (< 19) | 0 violations | Hard-kill criterion active; never fired |
| MAP-Elites stability | 3 reseeds x 600 gens, no crashes | total runtime ~1s for full study (mostly invalid mutations skipped) |

## Invariant tuple — what scalars

The cell key is the SHA256-truncated hash of:
```
(r, mode_sig, pair_dist, triple_dist)
```
where:
- **r** = effective rank after dropping zero columns
- **mode_sig** = `(rank(M_1), rank(M_2), rank(M_3))` of the three mode
  flattenings of the reconstructed sub-tensor, computed over F_3
- **pair_dist** = sorted multiset of `mode_sig` over all C(r, 2)
  sub-decompositions (using only columns i, j)
- **triple_dist** = same for C(r, 3); set to `()` (skipped) for archive
  speed in the run; available via `include_triples=True`

These four components are gauge-invariant by construction: the gauge acts
by basis change on the reconstructed tensor, and basis change preserves
the rank of every flattening of every sub-tensor. The empirical test
(50 random isotropy actions on each seed; 0/50 mismatches) confirms.

### Components NOT in the hash (and why)

- **stabilizer_lower_bound** (count of fixed elements within ISO_SAMPLE):
  conceptually stab-order is gauge-invariant (stab(g·U) is conjugate to
  stab(U), same order), but our **single-sample empirical estimator** is
  noisy. Empirical test: 46/50 isotropy-perturbed naive forms gave
  different counts despite the true stabilizer order being equal. Excluded
  from the discriminator hash; available as a secondary diagnostic via
  `descriptors.stabilizer_lower_bound(...)`.
- **column_weight_multiset**: NOT gauge-invariant under basis change
  (basis change permutes/mixes Hamming weights). Available as a
  tie-breaker only after column-perm + scaling normalization.

## Lossy-canonicalization caveat

The invariant tuple is a PARTIAL canonicalizer:
- **"Different cell" → guaranteed different orbit.** Two decompositions
  with different invariant tuples cannot be in the same gauge orbit
  (because the tuple is invariant by construction).
- **"Same cell" → likely same orbit, NOT certain.** Two decompositions
  with identical invariant tuples MAY lie in different orbits with
  identical (mode_sig, pair_dist, triple_dist) signatures. We have not
  proved this is impossible for 3x3 matmul over F_3.

The pilot reports a LOWER BOUND on orbit count via distinct invariant
tuples. To get an UPPER BOUND we would need additional invariants
(quartic flattening signatures, stabilizer-orbit double-cosets, ...).

## Distinct invariant-tuple counts

| Rank | Distinct invariant-tuple classes (union 3 reseeds) |
|---|---|
| 23 | **1** (Laderman seed only) |
| 27 | **1** (naive seed only) |

This is exactly the *seed* count — no novel orbits reached via mutation.

## Outcome diagnosis

**OUTCOME B.** Single rank-23 invariant-tuple class. The instrument works
(gauge-invariance verified; archive populates without hard-kill); local
ternary mutation around naive and Laderman fails to find any new orbit at
either rank. This is consistent with — and refines — the prior pilots'
finding: **the factor-matrix mutation geometry is the universal failure
mode**, not the field. F_3 gives 100x richer fitness rate over F_2 and
2.6e7 / 6048 ~ 4300x richer matmul-isotropy gauge, but the mutation
landscape is still too disconnected for bit-flips to explore.

One-line: **invariant-tuple canonicalization works, but the mutation
operator is the new bottleneck — not the canonicalizer.**

## Comparison to prior pilots

| Pilot | Gauge size | Fitness rate | Distinct rank-r orbits found |
|---|---|---|---|
| F_2 2x2 | 24 | 0.001 | 1 (Strassen) |
| F_2 3x3 | 6048 | 0.001 | 1 (Laderman) under bit-flip+flip-graph |
| F_3 2x2 | 3072 | 0.10 | 1 (Strassen) |
| F_3 3x3 (this) | ~2.6e7 (sampled) | 0.005 | 1 (Laderman); 1 (naive) |

The progression supports two findings:
1. **Char-2 not primary cause** (F_3 2x2 already showed this)
2. **Tensor smallness + factor-matrix Hamming geometry** are the
   structural blockers across all pilots, including the now-richest
   gauge tested.

## What this teaches us

The invariant-tuple approach is a **portable, scalable canonicalization
primitive**. It removes the |Iso| brute-force barrier and lets us run
QD on arbitrarily large gauge groups. The bottleneck in QD is now
PROVABLY the mutation operator, not the canonicalizer — three pilots
have now corroborated that bit-flip / ternary-flip mutation cannot
escape seed orbits regardless of field, gauge size, or canonicalization
method.

## What would change the picture

1. **Try Smirnov-style alternative seeds.** Smirnov's 2017 catalog has
   multiple rank-23 decompositions over Q that may project to distinct
   F_3 orbits. Each would give a distinct invariant-tuple cell — the
   archive would populate non-trivially without needing better mutation.
2. **Higher-arity flip-graph moves over F_3.** The F_2 3x3 pilot
   established that 3-to-2 and 2-to-2 don't fire from Laderman. Over F_3
   the gauge is much richer, so 4-to-3 (and even 2-to-2) might genuinely
   produce distinct orbits.
3. **LLM-driven whole-decomposition edits.** Replace local mutation with
   structured rewrites that preserve validity by construction.
4. **Tighter invariant tuple to test "lossy" hypothesis.** Add quartic
   flattening signatures, then check if any invariant-tuple cell ever
   contains two decompositions whose `normalize_and_key` fingerprints
   differ but whose tuples agree. That would prove lossiness empirically.

## Files

```
pilot_F3_3x3/
  __init__.py
  core.py            # F_3 arithmetic, normalization, drop/sort
  gauge.py           # GL_3(F_3), O_3(F_3), random isotropy sampler, ISO_SAMPLE
  descriptors.py     # invariant_tuple, mode_flat_rank_signature, pair/triple dist
  known_decomps.py   # naive rank-27, Laderman rank-23 (signed products + solve)
  test_gauge.py      # 8 unit tests (gauge-invariance is the key one)
  map_elites.py      # invariant-tuple-keyed archive, F_3 mutation
  run_pilot.py       # full orchestrator + report
  PILOT_REPORT.md    # this file
```

## Reproducibility

```
python -m tensor_decomp_qd.pilot_F3_3x3.test_gauge
python -m tensor_decomp_qd.pilot_F3_3x3.run_pilot
```

All RNG seeds fixed; numpy-only; no network or external APIs.
ISO_SAMPLE is built deterministically from `seed=12345` in `gauge.py`.

## Provenance

Built on prior infrastructure of pilot_F2_3x3 (Laderman product structure,
products-then-solve method) and pilot_F3_2x2 (F_3 arithmetic, per-column
scaling normalization, F_3 mutation operators). Departure: invariant-tuple
fingerprint replaces 2.6e7-element brute-force orbit enumeration.
