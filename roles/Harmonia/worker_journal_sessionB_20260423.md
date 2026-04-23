# Harmonia sessionB Journal — 2026-04-23

**Instance:** Harmonia_M2_sessionB
**Role:** tensor-decomposition QD incubation (non-standard for Harmonia —
see Session arc)

---

## Session arc

Started as a normal Harmonia restore (v4.3 protocol, 24 symbols, tensor
v17). Found team mid-wind-down from the 2026-04-22/23 collaborative day:
sessionA, sessionC, and auditor all posted SESSION_CLOSE. No URGENT items.
Posted SESSION_OPEN; self-sourced work per `feedback_autonomous_when_idle`.

James redirected the session to a different track: **incubating "Discovering
Novel Low-Rank Tensor Identities"** — a QD / MAP-Elites approach to
searching for tensor decompositions, Strassen-style.

The session then ran a focused 6-phase program:

1. **Incubation framing** (2-3 sentences each, north-star alignment check).
2. **Literature scan** (3 passes via Eos primitives: arxiv + OpenAlex +
   Semantic Scholar; ~255 unique papers).
3. **2x2 pilot** (F_2, Strassen calibration target, canonicalizer-first
   discipline, full unit-test gate).
4. **2x2 diagnosis** (outcome B; brute-force sampling + local Hamming-
   neighborhood probe distinguished B1 from B2).
5. **3x3 pilot** (F_2, naive + Laderman-23 seeded; verified Laderman via
   a "products-given, outputs-solved" Gaussian elimination method).
6. **Flip-graph primitives + 3x3 exhaustive analysis** (3-to-2 and 2-to-2
   moves implemented, unit-tested, then exhaustively applied to Laderman;
   no reductions or alternative orbits found).

Closed the session with a journal + memory entries + commit + port to F_3
2x2 as the next substrate (whose richer gauge we expect to reveal outcome A).

---

## What shipped

- **Literature synthesis** at `harmonia/tmp/tensor_decomp_lit/SYNTHESIS.md`
  (3 passes, ≈255 unique papers; identifies AlphaTensor, AlphaEvolve, Flip
  Graph Search, StrassenNet as primary competition; MAP-Elites × tensor
  decomp as the unclaimed combination; Yang 2024 SAT forbidden-cell results).
- **2x2 F_2 pilot** at `tensor_decomp_qd/pilot_F2_2x2/`:
  - canonicalizer + gauge enumeration (24-element subgroup after char-2
    orthogonality filter)
  - 8/8 unit tests green
  - MAP-Elites loop with Strassen seed
  - brute-force probe (0/200K random rank-7 triples valid)
  - local-neighborhood probe (Strassen at Hamming ≥ 6 from nearest other)
  - PILOT_REPORT.md documenting outcome B1 (method OK, domain degenerate)
- **3x3 F_2 pilot** at `tensor_decomp_qd/pilot_F2_3x3/`:
  - canonicalizer + gauge enumeration (6048-element subgroup)
  - vectorized bit-packed canonicalize (~200 ms per call, 7× speedup)
  - Laderman-23 verified via "products-given, outputs-solved" method
  - flip-graph primitives: `rank_2_tensor_decomp` + `try_reduce_3_to_2`
    + `try_swap_2_to_2`
  - exhaustive analysis: 0/1771 triples reducible, 0/253 pair-swaps
    produce new orbits
  - PILOT_REPORT.md with the complete structural picture

---

## Key findings

1. **Hamming isolation is universal over F_2 matmul decompositions.** At
   2x2 (Strassen), 3x3 naive, and 3x3 Laderman: all tested decompositions
   have zero valid neighbors at Hamming distance ≤ 3 (exhaustive) to 4
   (mostly exhaustive). Pure bit-flip MAP-Elites cannot connect orbits
   regardless of compute budget. This is a **geometric property** of the
   factor-matrix parameterization, not an algorithmic failure.

2. **Flip-graph moves do not fire from the specific F_2 decompositions
   tested.** Over F_2:
   - From naive rank-27: no triple has rank-reducible sum (all sums of
     3 distinct basis-vector outer-products are rank 3).
   - From Laderman rank-23: 0/1771 triples have true tensor rank ≤ 2
     (16 candidates had mode-3-flattening rank 2 but mode-1 or mode-2
     rank 3, meaning true tensor rank 3).
   - 0/253 Laderman pairs have an alternative rank-2 decomposition
     different from the current one.

3. **Char-2 orthogonality is the likely culprit.** Over F_2 with n=3,
   O_3(F_2) = 6 permutation matrices only. Over ℝ or F_p for p > 2, the
   orthogonal group is much larger. The matmul isotropy "collapses" over
   F_2 in a way that shrinks orbit diversity and deadens the flip-graph
   move space. The lesson: F_2 was the right calibration substrate
   (cheap to diagnose on) but the wrong production substrate (too
   degenerate to show QD's strength).

4. **The calibration-ladder approach worked exactly as intended.** We
   spent ~6 seconds of compute on the aggressive 3x3 run and days of
   analysis to extract these findings. At a larger scale, discovering
   the same lessons would have cost orders of magnitude more.

---

## Discipline lessons

1. **Products-then-solve is a robust verification method for tensor
   decompositions.** When you have candidate product definitions (a-side
   and b-side of each rank-1 summand) but uncertainty about output
   formulas, solve the linear system `contrib · s = target` over the
   relevant field. `tensor_decomp_qd/pilot_F2_3x3/laderman_solve.py`
   generalizes to any candidate product set — reusable for Smirnov's
   catalog, Heun's variants, etc.

2. **Distinguishing B1 vs B2 is load-bearing.** Per James's 2026-04-23
   feedback on the 2x2 report: "you preempt the obvious criticism" —
   before concluding outcome B, distinguish (B1) domain genuinely
   singleton from (B2) exploration insufficient. Both pilots used
   brute-force sampling + local neighborhood probes to demonstrate
   B1 (not just fail to find B2).

3. **Memory-reconstructed product definitions can be right even when
   output formulas are wrong.** My first Laderman attempt had correct
   products (a-side and b-side) but 20 wrong output-formula bits. The
   solver recovered. Without it, the session would have wasted hours
   on memory debugging.

4. **Forbidden-cell discipline (operational, not advisory) matters.**
   Per James's report-tightening feedback: "any canonical in a forbidden
   cell is canonicalizer failure until proven otherwise" makes the check
   non-negotiable. Both pilots ran 400K+ submissions with zero forbidden-
   rank violations — instrument reliability confirmed.

5. **Calibration-first protects the project.** Over a total compute
   cost measurable in seconds-to-minutes, we learned that:
   - pure bit-flip mutation fails (shown in both 2x2 and 3x3)
   - flip-graph moves don't fire over F_2 (shown in 3x3 with Laderman)
   - char-2 orthogonality is the likely structural cause
   
   Without the ladder, any of these could have been discovered much
   later, at much higher cost, on a larger problem.

---

## Handoff items

**Immediate next work** (this session continues):
- Journal + memory entries (this file)
- Commit the 2x2 + 3x3 + literature scan work
- Port to **2x2 matmul over F_3** as the next substrate (richer gauge;
  O_2(F_3) has 8 elements vs 2 over F_2; matmul isotropy ~3072 elements;
  expected to show outcome A if the char-2 hypothesis is right)

**Deferred** (future Harmonia work or separate sub-agent):
- 3x3 over F_3 requires smart canonicalization (brute-force over
  GL_3(F_3)^3 = 10^12 elements infeasible); likely needs learned or
  algorithmic canonicalization
- 4-to-3 flip-graph moves (harder rank-3 tensor decomposition primitive)
- Full matmul isotropy including transposition symmetry (adds factor 2
  or 3 to gauge size)
- LLM-driven whole-decomposition mutation (AlphaEvolve-style, wraps QD)

**Substrate integration** (if project matures):
- Shelf entry `TENSOR_DECOMP_LENS@v1` in `harmonia/memory/methodology_toolkit.md`
- New generator `gen_12` in generator pipeline (searches for invariants
  across tensor-decomposition landscapes)
- Cross-project memory entry linking to `tensor_decomp_qd/`

**Pattern 5 / known-bridges check:**
- The Kauers-Moosbauer 2025 flip-graph paper (pass 1 lit scan) implements
  essentially this move set for matmul over F_2 and F_3. Their results on
  structured matmul (triangular, symmetric) improved 13/15 formats. Our
  QD layer would add behavior-descriptor coverage that their single-point
  search doesn't provide — but we should read their code before claiming
  novelty in any quantitative sense.

---

## Personal observation

This session ran against a different grain than standard Harmonia work.
The usual Harmonia mode is substrate maintenance + epistemic audit +
symbol promotion. This session was a self-contained incubation: scope the
idea, check the literature, build the instrument, validate at small scale,
diagnose honestly, and report.

The discipline that carried over from standard Harmonia:
- Calibration-first (don't celebrate novelty until it passes F001-F005-
  analog anchor checks)
- SHADOWS_ON_WALL lens-count before committing to a stance
- Explicit B1-vs-B2 distinction in negative results (preempt the obvious
  criticism)
- Forbidden-cell discipline made operational, not advisory
- "We learned this the cheapest possible way" is the whole point of the
  ladder

The discipline that was new here:
- Products-then-solve as a verification method
- Flip-graph primitives as first-class algorithmic objects
- Literature-scan as incubation step rather than post-hoc citation
- Reward-signal-capture check at each phase (is this novel, or are we
  re-deriving AlphaTensor?)

Overall texture: **a fundable research proposal would now have a clear
"what's new" answer: the QD-archive-as-product frame with gauge-invariant
descriptors, validated by a cheap F_2 calibration, extended to a
richer-gauge substrate.** Before this session, it was an under-specified
thesis. Now it has a spec, an instrument, and a calibration.
