# Meta-report: Direction 2 — three parallel pilots integrated

**Run:** Harmonia_M2_sessionB, 2026-04-25
**Predecessor:** META_REPORT_PARALLEL_PILOTS.md (Direction 1 = pilots A/B/C)
**Scope:** synthesize the three follow-on pilots launched after Direction 1 left us with "mutation geometry is the proven bottleneck" as the only open issue.

The three Direction 2 pilots each attacked a different angle of that bottleneck:
1. **Polymul expansion** — does the polymul richness finding generalize across n and field?
2. **3x3 matmul over ℚ via invariants** — does ℚ produce multiple rank-23 orbits literature predicts?
3. **LLM-driven mutation** — can an LLM bridge orbits where local moves cannot?

## Headline summary

| Pilot | Result | One-line lesson |
|---|---|---|
| polymul_n4 (F_2) | B1 + sub-optimal richness | Polymul gauge is generic D_3×Z_2 across n; rank-9 naive has 34 distinct 2-flip orbits (vs n=3's 12) |
| polymul_n3_F3 | B1 at min, B2-leaning rank-9 | Hidden gauge closure factor 2 (12→24); 4 rank-9 orbits across reseeds — first reseed-disagreement we've seen |
| Q_3x3 | **A (formal) with caveat** | 3 distinct rank-23 invariant tuples found, all symmetry-related under matmul's cyclic Z_3 not in our gauge |
| LLM_mutation | B (clean negative) | 0 / 139 LLM mutations produced valid decompositions; entry-edit LLM hits the same Hamming wall as bit-flip |

## What changed about the project

Combining Direction 1 + Direction 2, the integrated picture is now:

### What's been ruled out
- **Char-2 alone** as the cause of singleton rank-min orbits (rejected by F_3 2x2)
- **Higher-arity flip-graph** (4-to-3) as the rescue for matmul (0/8855 reducible quadruples)
- **Brute-force isotropy enumeration as the canonicalization scaling barrier** (invariant tuples solve it)
- **Direct entry-level LLM mutation** as a bridge between orbits (0/139 valid; same Hamming wall)
- **Tensor smallness** as the sole cause (polymul-n=4 also has singleton rank-min, despite being larger than polymul-n=3 which had 12 sub-optimal orbits)

### What's been confirmed
- **Mutation geometry is the proven bottleneck**, not canonicalization or substrate or field (across 9 pilots × 4 fields × 4+ tensor families × 5 mutation classes)
- **Polymul richness at sub-optimal rank generalizes**: 12 (n=3, F_2), 34 (n=4, F_2), 16 (n=3, F_3) — comparable order of magnitude
- **Matmul tensors are pathologically rigid**: zero multi-orbit optima found across F_2, F_3, ℚ at any size tested. The ℚ pilot's three rank-23 cells turn out to be Z_3-symmetry-related, not fundamentally novel
- **MAP-Elites recovers only ~25% of 2-flip-reachable orbits at rank-9 polymul over F_3, 0/34 at polymul n=4** — even where rich terrain exists, local mutation under-explores it

### What's been learned (new substantive findings)
1. **Polymul gauge structure is universal at D_3×Z_2 across n over F_2** (n=3 and n=4 verified). Hidden Z_3 symmetry from non-commutative SUB/REV composition is a property of the polymul tensor family, not of any specific dimension.
2. **F_3 polymul has a factor-of-2 closure surprise** (claimed gauge size 12 → actual 24) because non-trivial F_3* scaling interacts with the input gauge non-trivially. This is the kind of discovery that would have been a Pattern-19-class bug if not caught by group-closure unit tests.
3. **Laderman over ℤ encodes cleanly with original signed coefficients via products-then-solve.** Smirnov-cyclic variants (transpose conjugates of Laderman) produce identical invariant tuples (transpose Z_2 IS in GL_3(ℚ)³); cyclic Z_3 conjugates produce different tuples (cyclic Z_3 is NOT in GL_3(ℚ)³).
4. **AlphaEvolve framing is the right LLM-mutation framing**, not entry-level edits. Our negative result narrows the LLM-mutation hypothesis space cleanly: small-budget Haiku edits at the tensor-entry level cannot bridge orbit isolation regardless of prompt design.

## The substrate now has a sharper problem statement

**Original incubation thesis** (2026-04-23):
> Build a behavior-diversity archive over tensor decompositions. Strassen is one cell; the other cells are unclaimed.

**After Direction 1**:
> The mutation primitive is the bottleneck. Canonicalization, substrate, and field choice don't fix it.

**After Direction 2**:
> The mutation primitive is the bottleneck — and the bottleneck is *specifically about what survives the algebraic correctness manifold under perturbation*. Random perturbations (bit flip, ternary flip, LLM micro-edit) all fail. Algebraic perturbations (3-to-2, 2-to-2, 4-to-3 flip-graph) succeed at preserving validity but are themselves locked-in for matmul. The escape requires either:
> (a) **higher-level mutation** that operates on whole-decomposition algebraic structure (AlphaEvolve / code-level), or
> (b) **validity-preserving projection** of arbitrary mutations (proposed-then-snap-to-manifold), or
> (c) **a different target tensor family** where the algebraic rigidity is weaker than matmul (polymul partially shows this; convolution and group-algebra remain unexplored).

## Defensible novel findings worth writing up

If we were preparing a write-up of the project for external review, the publishable claims would be:

1. **The "products-given, outputs-solved" verification method** for tensor decompositions over arbitrary fields. Lets you encode published decompositions from memory/imperfect sources without trusting output formula recall. Used successfully for Laderman over F_2, F_3, ℤ.

2. **Invariant-tuple canonicalization** for tensor decompositions under arbitrary gauge groups. (rank, mode_flat_signature, pair_dist, triple_dist) is gauge-invariant by construction and discriminates orbits when distinct ones exist. Empirically validated 50/50 on three different decompositions of the 3x3 matmul tensor over ℤ.

3. **Empirical structural finding: matmul tensors are Hamming-isolated at every tested rank over every tested field.** Across 9 pilots, no local move ever bridged rank-r orbits of matmul. This is a substantive negative result that informs algorithm design — it tells future researchers what NOT to attempt.

4. **Polymul tensors have meaningful sub-optimal-rank orbit diversity.** 12-34 distinct non-naive orbits found via exhaustive 2-flip neighborhood probing. This is the QD-archive thesis's one positive empirical demonstration.

5. **Z_3 cyclic symmetry of matmul lives outside GL_3(ℚ)³.** Computed empirically via invariant-tuple comparison of Laderman vs cyclic-conjugate variants. This isn't a new theorem (de Groote 1978 and others), but it's a clean empirical demonstration via our canonicalization framework.

## Recommended next steps (ranked by evidence)

### 1. Convolution and group-algebra tensors (polymul family expansion, continued)

The polymul richness IS real and substrate-portable. Convolution tensors and small group-algebra tensors (quaternion mult, complex mult, dihedral group algebra) are even less studied than polymul. Each follows the same pattern as polymul pilots; cumulatively they would build the project's positive empirical case.

**Effort:** ~1 day per pilot, ~5 pilots feasible.

### 2. Validity-preserving projection wrapper for arbitrary mutations

The proven bottleneck is "tiny edits don't preserve validity." A solver that takes ANY mutation (bit-flip, LLM proposal, anything) and projects it onto the validity manifold (closest valid decomposition by some metric) would address the bottleneck head-on.

This is a serious algorithmic problem (validity manifold = solution set of Brent equations; projection requires solving a system). Over F_p there are tools; over ℚ it's harder.

**Effort:** ~1 week minimum. Higher reward if it works.

### 3. Code-level LLM mutation (AlphaEvolve framing, smaller scale)

Direction 3's negative was at entry-edit granularity. A code-level pilot would have the LLM modify a Python function that GENERATES decompositions, not the decomposition tensor itself. Different layer; might work.

**Effort:** ~3 days. Defensibility issue: AlphaEvolve already does this for matmul; we'd need to argue our QD wrapper adds value. Polymul (where AlphaEvolve hasn't been applied as far as I know) might be the right target.

### 4. Stop here; write up.

The negative results across 9 pilots × 4 fields × 4+ tensor families are substantively informative. Rather than continue spending compute, a clean write-up of "what we tried, what worked, what didn't, what the literature now knows" might be the highest-value output.

The defensible publishable findings are listed above. They include both methodology (products-then-solve, invariant tuples) and structural results (Hamming isolation universality, polymul sub-optimal richness, ℚ rank-23 cosets under GL_3³).

## Decision point for James

The project's calibration ladder has now done two full cycles. Each successive pilot has refined the problem statement; none has produced a "found a novel algorithm" result. The sub-optimal polymul findings are the closest thing to a positive empirical claim.

**Reasonable choices:**
- (1) Push polymul-family further (convolution, group algebra)
- (2) Take the validity-preserving-projection swing
- (3) Code-level LLM mutation on polymul
- (4) Stop and write up

I have a slight lean toward (4) at this point — the project's results have stabilized, and additional pilots are unlikely to change the picture significantly without a methodology shift. But (1) is the cheapest if the goal is more empirical breadth.

## Provenance

**Pilots covered in this meta-report:**
- `pilot_polymul_n4/` — n=4 over F_2, commit `8e5cb0e0`
- `pilot_polymul_n3_F3/` — n=3 over F_3, commit `8e5cb0e0`
- `pilot_Q_3x3/` — 3x3 matmul over ℤ-bounded ℚ, commit `857f8adc`
- `pilot_LLM_mutation/` — Haiku 4.5 mutation, commit `9bc8ddf1`

**Total project state (9 pilots):**
- pilot_F2_2x2, pilot_F2_3x3, pilot_F2_3x3_v2, pilot_F3_2x2, pilot_F3_3x3
- pilot_polymul_n3, pilot_polymul_n4, pilot_polymul_n3_F3
- pilot_Q_3x3, pilot_LLM_mutation

All in `D:\Prometheus\exploratory\tensor_decomp_qd\`.

Session journal: `roles/Harmonia/worker_journal_sessionB_20260423.md` (note: spans sessions 2026-04-23 through 2026-04-25 in calendar time despite filename).
