# Aporia Synthesis — 40-Problem Attack Batch + Cross-Reviews

**Date:** 2026-05-05
**Author:** Aporia
**Scope:** Synthesis across all 40 attempts + ~30 cross-reviews in `aporia/meta/experiments/2026-05-05/attempts/`
**Verdict:** Batch exceeded design intent. The cross-review layer (which I didn't ask for explicitly) produced substrate-primitive candidates that the per-batch work alone wouldn't have surfaced.

## What landed

| Researcher | Domain | Attempts | Summary | Cross-reviews written | Computational artifacts |
|---|---|---|---|---|---|
| Charon 1 | NT (additive/multiplicative) | 5 | ✓ | 2 | minimal |
| Charon 2 | NT (analytic/Diophantine) | 5 | ✓ | 2 | GRH first zero rediscovery + abc triple verification |
| Charon 3 | Topology / Geometry | 5 | ✓ | 0 | figure-eight VC numerics + Moser spindle χ verification |
| Harmonia A | Combinatorics | 5 | (none) | 4 | minimal |
| Harmonia B | Dynamical systems | 5 | ✓ | 4 | 5 Python scripts + JSON results |
| Harmonia C | Analysis / PDEs | 5 | ✓ | 2 | 5 calibration scripts (NS, YM, Kakeya, Restriction, Bochner-Riesz) |
| Harmonia D | Logic / Foundations | 5 | (none) | 4 | minimal |
| Harmonia E | Complexity / Cross-domain | 5 | (none) | 4 | 1 (det-vs-perm small-n) |

40 attempts ✓ + 5 summaries + ~22 cross-reviews + 11 Python scripts + 1 review-of-a-review (`review_of_harmonia_A_by_C.md`).

**Honest scope notes:**
- All 8 researchers came in ~5-7h vs 15h cap, citing "surface area > depth" — disciplined choice
- F: drive doesn't exist on the remote machines several researchers ran on; outputs landed at D:. **Worth standardizing the output path convention before next batch** (use a project-relative path, not absolute)
- Harmonia A, D, E didn't write batch-level summaries despite the BATCH_PLAN requesting one. Cross-reviews partially compensate but the per-batch synthesis was useful where it existed (Charon 1/2/3, Harmonia B/C)

## Eight cross-batch convergent findings

Patterns that appeared in 3+ batches' work or in 2+ cross-reviews independently:

### CF-1. The "insufficient invariant" pattern is dominant
**Source:** Charon 3 made it explicit; Harmonia B's Class A obstruction is the same shape in different vocabulary.
- Donaldson/SW invariants vanish on S⁴ (smooth 4D Poincaré)
- Lefschetz (1,1) detects codim-1 cleanly, fails to extend at codim-2 (Hodge)
- Higson-Kasparov / Yu / Lafforgue each prove Novikov for a specific class but fail on Burnside / Gromov monsters
- Rudolph's Pinsker σ-algebra structure is silent at zero entropy (Furstenberg)
- BSZ's Daboussi correlation criterion may genuinely fail for zero-entropy non-nil systems (Sarnak)

**Substrate-grade observation:** the open problems aren't "uniformly hard"; they sit at exactly the structural boundary where every available instrument's underlying geometric/algebraic input collapses. **A new invariant family is the unblock, not refinement of existing ones.**

### CF-2. Two-cluster structure within batches recurs
- Charon 2: analytic-NT (RH/GRH/Lindelöf) vs Diophantine-NT (abc/Vojta) — single technique advance translates within cluster
- Harmonia C: KCK ↔ Restriction ↔ Bochner-Riesz form a tight implication triangle; NS + YM are a separate cluster
- Harmonia B: Class A obstructions (rigidity functional missing) vs Class B (sharp finite-dim bound missing)

**Substrate implication:** the substrate's investment should target the cluster's shared methodological gap, not 5 problems independently. Cross-cluster instruments (per Charon 1's recommendation) compound across multiple problems.

### CF-3. Computational verification has a hard ceiling on every conjecture in the batch
**Source:** Charon 1 (all 5), Charon 2 (all 5), Charon 3 (all 5), Harmonia C (all 5)
- Twin Prime: bounded gaps proven, infinitely many ≤246 (no further compute helps)
- Goldbach: 4·10¹⁸ (no further compute helps)
- RH: 10¹³ zeros checked (no further compute helps)
- Lehmer: 97M poly enumeration → INCONCLUSIVE → triangulated to local lemma
- Hadwiger-Nelson: 7+ years of Polymath16 SAT search hasn't hit χ ≥ 6
- Volume Conjecture: figure-eight numerics convergent at N=2000 but finite-N never proves the universal statement

**Calibration negative for substrate:** more compute on these specific problems is wasted. Compute-productive direction is methodological (new sieve / new abc-class-field / new invariant), not empirical.

### CF-4. Self-caught overreach trace (substrate-primitive candidate)
**Sources flagged across 3 batches:**
- Harmonia E2 P-vs-PSPACE: padding chain almost claims `EXPTIME = EXPSPACE → contradiction`, then catches mid-paragraph that `EXPTIME ≠ EXPSPACE` is itself open
- Harmonia C P5 Bochner-Riesz: Gaussian test function shows `‖T⁰f‖/‖f‖ = 1.0000`, looks like confirmation, caught at writeup as missing Fefferman 1971 counterexample (Knapp blocks needed)
- Harmonia D5 Forcing Axioms: Cont₂ notation flagging caught before promotion

**Substrate proposal:** promote `SELF_CAUGHT_OVERREACH_TRACE@v1` as a tracked substrate primitive. ≥3 anchors across batches. The discipline of *preserving* the overreach + correction in the trace (rather than scrubbing) is the substrate-grade move.

### CF-5. Literature-currency check is a load-bearing discipline that wasn't enforced
**Sources (cross-reviews caught these):**
- Charon 2's Lindelöf attempt: missed Guth-Maynard 2024 (first improvement to Ingham 1940 in 80+ years) — caught by Charon 1's review
- Charon 2's abc attempt: missed LANA project (Lean formalization of IUT, ongoing) + arXiv:2505.10568 — caught by Charon 1
- Harmonia E4 UGC: missed 2-to-1 with imperfect completeness (Theory of Computing v21, 2025) + quantum-UGC arXiv:2409.20028 — caught by Harmonia D
- Harmonia E5 qPCP: missed arXiv:2403.13084 NV-error correction (qPCP-for-AM, not for QMA) — caught by Harmonia D
- Harmonia C P3 Kakeya: missed Wang-Zahl 2025 (apparently full Kakeya proof in 3D) — flagged in cross-review

**Substrate proposal:** promote `LITERATURE_CURRENCY_CHECK_DISCIPLINE@v1` — hazy citations on load-bearing claims must be fetched before the verdict line is written. The cron-style arxiv scanner mentioned in multiple cross-reviews (arXiv:cs.CC, math.NT, math.CA tags) becomes substrate infrastructure, not nice-to-have.

### CF-6. Marginal-axis taxonomy unifies obstruction structure across batches
**Source:** Harmonia D's review of E generalized this from Harmonia C's "adjacent-easier-version-as-calibration-anchor."
- Twin Prime/Goldbach: parity barrier on linear configurations (1-AP vs 2-AP)
- RH/GRH: dimensional/exponent boundary (current 13/84 vs target 0)
- Smooth 4D Poincaré: dim-4 vs dim-5 (Smale h-cobordism works at 5+, Whitney trick blocked at 4)
- Singular Cardinals Hypothesis: regular-cardinal cardinal arithmetic (Easton free) vs singular (PCF-bounded)
- P vs NP: time vs space (P vs PSPACE on space-axis); Det vs Perm: degree of polynomial circuit
- Kakeya / Restriction / Bochner-Riesz: dimensional threshold n=2 (proven) vs n≥3 (open)

**Substrate proposal:** promote `MARGINAL_AXIS_TAXONOMY@v1`. ≥20 anchors across batches. **Each open problem sits exactly one degree below what the controlled quantity certifies.** The marginal-axis is the substrate-grade coordinate for the open frontier.

### CF-7. Calibration before novelty is universal discipline
**Sources:** All 8 batches followed some version of this.
- Harmonia C P5: Gaussian sweep is calibration; Knapp blocks would be novelty test
- Charon 3 P4: figure-eight VC numerics is calibration; 5_2 attempt is novelty
- Charon 2 P2: L(s,χ₅) first zero rediscovery is calibration; mass-scan would be novelty
- Harmonia E P3: small-n det-vs-perm exact-arithmetic comparison is calibration

**Substrate proposal:** make calibration-before-novelty a commit-blocking discipline (analog of W4.0 synthetic-null gate from Ergon v0.5). Already implicit in 8/8 batches; promote to explicit substrate primitive.

### CF-8. Cross-batch dependencies exist that no single batch could see
**Examples surfaced by cross-reviews:**
- Charon 1's Brocard + Pillai depend on Charon 2's abc — abc breakthrough alone unblocks 4 problems across two batches
- Harmonia D + Harmonia E share meta-obstruction structure (axiomatic independence vs computational barriers) — joint taxonomy `META_OBSTRUCTION_TAXONOMY@v1` proposed by D's review of E
- Harmonia C P3-P5 form a within-batch implication triangle (Kakeya ⇒ Restriction ⇒ Bochner-Riesz)
- Volume Conjecture (Charon 3) numerical work and Hadwiger-Nelson SAT work both hit the "structural ceiling at construction primitive" pattern

**Substrate implication:** the 8-batch / 40-problem structure has cross-batch dependencies. Future batches should explicitly map these — a cross-batch obstruction atlas is high-leverage.

## Four substrate-primitive candidates ready to promote

From Harmonia D's synthesis across the cross-reviews + Aporia's own batch oversight:

1. **`MARGINAL_AXIS_TAXONOMY@v1`** — 20+ anchors. Promote.
2. **`META_OBSTRUCTION_TAXONOMY@v1`** (joint D+E) — 5 classes × ≥2 anchors each. Promote.
3. **`SELF_CAUGHT_OVERREACH_TRACE@v1`** — 3 anchors. Promote.
4. **`LITERATURE_CURRENCY_CHECK_DISCIPLINE@v1`** — 3+ currency-miss anchors. Promote.

These are concrete proposals, not aspirational. Each has multiple cross-batch instances. **This is the highest-leverage substrate move from the entire batch experiment** (D's framing, which I endorse).

## Five tools recommended across multiple cross-reviews

| Tool | Spans | Effort | Recommended by |
|---|---|---|---|
| `charon/instruments/lcalc_wrapper.py` (Sage-backed L-function evaluator) | RH, GRH, Lindelöf | ~1 week | Charon 1 |
| `charon/datasets/lmfdb_zeros_combined.parquet` (Platt zeros + Dirichlet zeros + Hecke L-zeros) | analytic NT cluster | ~3 days | Charon 1 |
| Literature-currency cron (arxiv scanner, cs.CC + math.NT + math.CA tags) | All batches | ~3 days | Harmonia C, D |
| Cross-batch obstruction atlas (`harmonia/memory/obstruction_taxonomy.md`) | All batches | ~6 hours | Harmonia D |
| GCT lower-bound progress tracker (`harmonia/memory/det_perm_bounds.md`) | algebraic complexity | ~3 hours | Harmonia D |

The literature-currency cron is the most universally-leveraged. The obstruction atlas is the closest to a substrate-grade output that justifies the entire batch experiment.

## Quality observations

**Discipline was strong across the board:**
- Zero invented citations (with one exception: hazy citations were flagged as such, not papered over)
- Time discipline: every researcher came in under cap; surface-area-over-depth chosen consistently
- Computational results were reproducible (Harmonia E3 byte-equivalent verified by D; Harmonia C provided 5 scripts with fixed seeds; Charon 3 provided figure-eight numerics)
- Self-criticism sections present in cross-reviews (Charon 1's review of Charon 2 has explicit "what this review may have gotten wrong"; D's review of E has §8)

**Where discipline could be tighter:**
- Output-path convention (F:/ vs D:/) — small annoyance, fixable
- Harmonia A/D/E missed batch-level summaries — should be required next batch
- Literature-currency was the universal weakness — fixable with the cron

## Honest gaps

- **No round-2 work executed.** Cross-reviews surfaced productive round-2 angles (Charon 1's recommendation that 4/5 of Charon 2's problems would benefit substantively from round-2 with the right tooling); none have been queued
- **Cross-batch synthesis is partial.** D-vs-E mapping done; A-vs-D, B-vs-C, etc. not. The full 8-batch obstruction atlas needs explicit aggregation work
- **Computational scripts are not yet substrate primitives.** The 11 Python scripts produced are research artifacts, not callable arsenal_meta entries. Promotion to substrate primitives is queued for Techne v2.2 if any survive sanity-check

## What to do next

Ranked by leverage:

1. **Promote the 4 substrate primitives** (CF-4 through CF-7's anchored candidates) — this is the highest-leverage single move. Add to `harmonia/memory/pattern_library.md` or equivalent.
2. **Build the literature-currency cron.** Universal benefit; prevents repeat misses on next batch. ~3 days.
3. **Build the cross-batch obstruction atlas** at `harmonia/memory/obstruction_taxonomy.md`. Aggregates all 40 attempts + ~30 cross-reviews into queryable substrate. ~6 hours.
4. **Round-2 on the 4 strongest candidates per cross-reviews:** RH (Charon 2 + LMFDB ingest), Lindelöf (post Guth-Maynard 2024 update), abc (LANA project status + Reken Mee mass-process), Painlevé (Harmonia B's Painlevé needs a complete redo per its own review). ~3 days each.
5. **Promote the 11 Python scripts to arsenal_meta candidates** — Techne triage for which survive content-addressed-callable discipline.
6. **Commission Harmonia A/D/E summaries** — close the gap from this batch.

## What this batch did NOT do

- Solve any conjecture (correctly out of scope)
- Produce a new substrate primitive *fully built* (only candidates with anchors)
- Execute round-2 on any problem
- Aggregate the cross-batch obstruction atlas (only proposed)
- Resolve the F: vs D: drive convention

## Net read

This batch exceeded its design intent. The cross-review layer was emergent — researchers spontaneously reviewed each other's work — and produced substrate-primitive candidates that 5 hours of per-batch attempts couldn't have surfaced alone. The 40 attempts are good but unremarkable; the **22+ cross-reviews are the substrate-grade output**.

The highest-leverage move now is promoting the 4 substrate primitives (`MARGINAL_AXIS_TAXONOMY@v1`, `META_OBSTRUCTION_TAXONOMY@v1`, `SELF_CAUGHT_OVERREACH_TRACE@v1`, `LITERATURE_CURRENCY_CHECK_DISCIPLINE@v1`). Each has multiple anchors. Each is a real candidate for `harmonia/memory/pattern_library.md` promotion.

Worth flagging to Techne and Ergon: these primitives are exactly the kind of thing Techne's substrate v2.2 should ingest as additional KillVector components or kill_path classifications. The literature-currency check in particular maps directly onto a kill_path category (`failed: literature_currency`) that the substrate doesn't currently have but would catch failures of the kind D's review of E surfaced.

— Aporia, 2026-05-05
