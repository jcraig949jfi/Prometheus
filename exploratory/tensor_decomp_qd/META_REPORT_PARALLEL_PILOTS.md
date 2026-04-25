# Meta-report: Parallel Pilots A, B, C — synthesis

**Run:** Harmonia_M2_sessionB, 2026-04-25 (parallel agents launched 2026-04-23 evening; results returned 2026-04-25)
**Scope:** synthesize the three parallel pilots (A: 4-to-3 over F_2; B: polynomial multiplication over F_2; C: invariant canonicalization over F_3). All three return outcome B, but each exposes a different load-bearing structural lesson.

---

## Summary table

| Pilot | Approach | Outcome | The lesson it teaches |
|---|---|---|---|
| A | 3x3 F_2 + 4-to-3 flip-graph | **B1 (stronger)** | Higher-arity moves DON'T break Laderman isolation either: 0/8855 quadruples have tensor rank ≤ 3. The structural lock-in is universal across move classes. |
| B | Polynomial mult n=3 over F_2 | **B1 (with caveat)** | Polymul has structural slack matmul lacks: 46/4851 valid 2-bit-flip neighbors of naive rank-9 hit 12 distinct non-minimum orbits. Single rank-6 orbit, but rich sub-optimal terrain. |
| C | 3x3 F_3 + invariant canonicalization | **B (canonicalization solved)** | Invariant-tuple canonicalization works (50/50 gauge invariance), unblocks compute scale where brute-force isotropy enumeration was infeasible. Single rank-23 orbit found nonetheless. **"The mutation geometry is now the proven bottleneck — canonicalization is solved."** |

## What the parallel exploration achieved

Each pilot tested a different hypothesis about WHY the F_2 + F_3 2x2/3x3 pilots all hit outcome B. The hypotheses (and their fates):

### A — "Maybe higher-arity moves work"

**Hypothesis:** the 3-to-2 and 2-to-2 moves don't fire from Laderman because Laderman's columns are too algebraically dispersed for small column-subset sums to have low rank. Maybe at 4-column subsets, rank-3 sums exist.

**Evidence collected:** exhaustive scan of all C(23, 4) = 8855 column quadruples. Distribution:
- All 8855 have max-mode-flattening rank = 4 → all have true tensor rank ≥ 4.
- 350 have mode-3-flattening rank ≤ 3 (a sufficient-but-not-necessary check), but ALL of those 350 have mode-1 or mode-2 flat rank = 4 → still rank-4 tensor.
- **0 / 8855 have true tensor rank ≤ 3.** No 4-to-3 move can fire.

**Verdict:** REJECTED. Higher arity doesn't help. This makes the structural lock-in stronger, not weaker. The agent also implemented `rank_3_tensor_decomp` over F_2 as a reusable primitive — the work was useful even though the answer was negative.

### B — "Maybe matmul is too saturated; less-studied tensors have more diversity"

**Hypothesis:** matmul tensors are special — their algebraic structure forces a unique low-rank decomposition. Other bilinear tensors (polynomial multiplication, convolution, group algebra) might have more orbit diversity.

**Evidence collected:**
- Polymul n=3 over F_2 (target rank 6 known via Karatsuba-3-way; naive 9).
- Gauge group: 12 elements (D_3 × Z_2, NOT 48 — the SUB and REV generators don't commute, surfacing a hidden Z_3 symmetry that took several iterations to characterize correctly).
- MAP-Elites 3 reseeds × 5000 gens: still **single** rank-6 orbit (Karatsuba's).
- BUT — and this is the substantive finding — **the rank-9 naive seed has 46/4851 valid 2-bit-flip neighbors hitting 12 distinct non-naive orbits.** Compare to matmul: 0 valid 2-flips for Strassen-2x2 OR Laderman-3x3.
- Fitness rate: 3% (vs 0.1% for F_2 matmul, 10% for F_3 matmul).

**Verdict:** PARTIAL CONFIRM. Polymul has structurally richer non-minimum terrain than matmul. The rank-minimum is still Hamming-isolated, but the surrounding rank-9 layer is genuinely diverse. **Suggests the QD-archive thesis CAN show meaningful structure on polymul-like tensors at sub-optimal ranks.** This is the closest any pilot has come to outcome A.

### C — "Maybe canonicalization is the blocker for richer fields"

**Hypothesis:** 3x3 over F_3 has |matmul isotropy| ≈ 10^7-10^10, infeasible to brute-force. Invariant-based canonicalization (computing gauge-invariant fingerprints instead of finding lex-min orbit reps) might unblock this regime.

**Evidence collected:**
- Invariant tuple defined: `(rank, mode_flat_rank_signature, pair_rank_distribution, triple_rank_distribution)`, SHA256-hashed.
- Validation: 50/50 random matmul-isotropy elements leave the tuple unchanged → invariance is correct.
- Failed candidates (excluded from final tuple): `stabilizer_lower_bound` (single-sample fixed-element count is conjugation-biased — 46/50 perturbed forms gave different counts); `column_weight_multiset` (NOT actually basis-change invariant).
- Laderman over F_3 verified (signed product version with -1 → 2 mod 3 worked; unsigned positive-coefficient version fails because identical positive terms don't cancel mod 3).
- 1 rank-23 orbit + 1 rank-27 orbit across 3 reseeds × 600 gens.

**Verdict:** CANONICALIZATION SOLVED, MUTATION STILL THE PROBLEM. The agent explicitly states: "canonicalization is solved." We can now scale the QD instrument to arbitrarily large isotropy groups via invariant tuples. But the mutation primitive — whether bit-flip, 3-to-2, 4-to-3, or column-level — still fails to bridge between rank-r orbits.

## The integrated picture across all 5 pilots

| Pilot | Field × Size × Tensor | |Iso| | Min rank found | Distinct orbits |
|---|---|---|---|---|
| F_2 2x2 matmul | 24 | 7 (Strassen) | 1 |
| F_2 3x3 matmul | 6,048 | 23 (Laderman) | 1 |
| F_2 3x3 + 4-to-3 | 6,048 | 23 (Laderman, locked) | 1 |
| F_3 2x2 matmul | 3,072 | 7 (Strassen) | 1 |
| F_3 3x3 matmul (invariant) | "infinite" via fingerprint | 23 (Laderman) | 1 |
| F_2 polymul n=3 | 12 | 6 (Karatsuba) | 1 (but 12 sub-optimal at rank 9) |

Across **5 pilots, 3 fields, 3 tensor sizes, 4 move classes, 2 canonicalization methods**: one rank-minimum orbit per substrate. The QD archive at the optimum is always size 1.

## Three converging conclusions

1. **The mutation primitive is now THE proven bottleneck.** Pilot A ruled out higher-arity moves on matmul. Pilot C ruled out canonicalization scaling. Pilot B showed sub-optimal terrain has structural diversity but the rank-minimum doesn't. Across all variations, simple local-move mutation cannot bridge between rank-r orbits.

2. **Matmul tensors are pathological for QD.** Across F_2 and F_3, at 2x2 and 3x3, with brute-force or invariant canonicalization, the rank-minimum orbit count is 1. Polymul's structural slack at rank-9 (12 sub-optimal orbits) shows this isn't a property of MAP-Elites in general — it's a property of matmul specifically. Matmul's algebraic structure is unusually rigid.

3. **The original incubation thesis needs a substantive reformulation.** Original pitch: "QD archive of (rank × sparsity × symmetry × coef-complexity) cells, populated by single-point gradient/RL/SAT methods plus our QD coverage." Reality: the archive at the rank-minimum is populated by exactly ONE orbit per matmul instance, and even sub-optimal-rank populations are sparse for matmul (vs richer for polymul).

## Refined next-step recommendation

Three concrete directions, ranked by where the evidence is strongest:

### 1. Drop matmul as the primary target. Build polymul-family pilots.

Pilot B is the only one that came close to outcome A. The 12 distinct sub-optimal orbits at rank-9 polymul are real, gauge-quotiented, and reseed-stable. A QD archive of polymul decompositions IS interesting and unclaimed. Concrete next pilots:
- Polymul over larger n (n=4, n=5)
- Polymul over F_3, F_5
- Convolution tensors (closely related to polymul)
- Group-algebra tensors (quaternion mult, complex mult)

Effort: ~2 days each, using polymul pilot as template.

### 2. Use invariant-tuple canonicalization to scale the matmul work to ℚ.

Pilot C unblocked canonicalization for arbitrarily large gauge. The natural test: 3x3 matmul over ℚ (or F_5, F_7), where the gauge is much larger than F_3 and orbit count over ℚ is known to be > 1 from algebraic-geometry literature.

Effort: ~3 days. Invariant tuples need to be careful with field-dependent invariants (Hamming weight is meaningless over ℚ; need replacements like SVD-based or Jordan-form-based invariants).

### 3. Replace bit-flip mutation with LLM-driven whole-decomposition mutation.

If the mutation primitive is the bottleneck, AlphaEvolve-style LLM proposals (whole-decomposition rewrites guided by code semantics) might bridge the orbits that local moves can't. This is the literature's bet (AlphaEvolve, ImprovEvolve, GigaEvo, CodeEvolve).

Effort: ~1 week minimum (LLM API integration, prompt design, evaluation budget). Higher novelty risk: AlphaEvolve already does this for matmul, just without the QD wrapper. Our defensible contribution is the QD ARCHIVE on top, not the mutation method.

### Recommendation in priority order

1. **Polymul-family expansion** (Direction 1). Cheapest, evidence is strongest, multiple targets.
2. **3x3 matmul over ℚ via invariants** (Direction 2). Tests a real hypothesis (matmul over ℚ has multiple orbits) with already-built infrastructure.
3. **LLM mutation** (Direction 3). Highest cost, highest novelty risk, but it's the only direction that addresses the proven mutation-geometry bottleneck head-on.

## Reusable primitives produced this session

- `rank_2_tensor_decomp` over F_2 (3x3 pilot)
- `rank_3_tensor_decomp` over F_2 (Pilot A)
- Invariant-tuple canonicalization (Pilot C) — generalizes to any field
- Products-then-solve verification method (3x3 pilot, used in Pilot C for Laderman over F_3)
- Per-column F_3 scaling normalization (F_3 pilots)
- Polynomial-multiplication tensor + group-closure-aware gauge enumeration (Pilot B)

These compose. A pilot on, say, convolution over F_5 would inherit ~80% of the infrastructure from existing pilots.

## Provenance

- Five pilots: `tensor_decomp_qd/pilot_F2_2x2/`, `pilot_F2_3x3/`, `pilot_F2_3x3_v2/`, `pilot_F3_2x2/`, `pilot_F3_3x3/`, `pilot_polymul_n3/`
- Each has unit tests + `PILOT_REPORT.md`.
- Commits: ab605eb4, 810ee5c8, eee8a6bd, 3b01cd44, 039c7fe6, e8d2f89c on main branch (local, not pushed).
- Project (after reorganization commit `f8a39bb5`): `D:\Prometheus\exploratory\tensor_decomp_qd\`.
- Session journal: `roles/Harmonia/worker_journal_sessionB_20260423.md`.
