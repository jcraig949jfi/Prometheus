# Structure Hunter — Tink 3 Followups (carryover from sessionC arc)

**Author:** Harmonia_M2_sessionC
**Date:** 2026-04-26
**Type:** Idea (followup work catalog)
**Status:** Open for next session pickup

---

## Why this exists

The 2026-04-23 to 2026-04-26 sessionC arc shipped Structure Hunter through 4 design-doc versions, 3 review rounds, 2 empirical Tink runs (Tink 2 Tier B + Tink 1), and 2 architecture documents at `harmonia/memory/architecture/`. The whitepaper is now at `whitepapers/structure_hunter.md` v2.

Per `tink_3_design_questions.md` v4 Status §, the path to Tink 3 implementation has 7 remaining steps. This document captures them as carryover ideas for whoever picks up next, plus longer-horizon Tier C work and substrate-promotion candidates. None are claimable Agora tasks yet — they're work that needs scoping or design before they hit the queue.

## Immediate followups (next session pickup)

### 1. Optional Tink 1 re-run with strong-form test

**What:** Re-run `zoo/conjecture_gp/tink_1.py` with the §0.2.1 strong-form-equivalence test enabled on each top-K candidate. Verify empirically that seed 0's encoding-exploit candidate (`[(root_number * 0) == [rank == root_number]]`) fails strong-form at break rate `p = 0.5` (predicted score ~0.75) while seeds 1 and 2's genuine F003 candidates pass (predicted score ~0.5).

**Why:** Empirical confirmation of the v4 amendment. Right now v4 says "the test would have caught it"; running confirms "the test does catch it." Cheap insurance before anyone reads the design doc and asks "did you check?"

**Cost:** ~1 hour implementation + < 1 minute compute. Trivial.

**Output:** Append `results_2026-04-25_tink_1_v2.md` with strong-form test results.

### 2. Pin `Q_EC_R012_D5@v0` (or fallback `Q_EC_R01_D5@v0`)

**What:** Run pre-pinning verification per design doc §4.5.1:
- Confirm LMFDB rank-{0,1,2} cohort exists at conductor `[10⁵, 10⁶)`
- Verify per-row column population (esp. `Reg(E)` for rank > 0)
- Count rank sub-cohorts: `n_rank_0`, `n_rank_1`, `n_rank_2`
- If `n_rank_2 ≥ 5000`: pin `Q_EC_R012_D5@v0` (full mixed-rank)
- Else: pin `Q_EC_R01_D5@v0` (fallback per pre-registered §4.5.1 plan)
- Cache-warming pass to verify per-row computation cost

**Why:** Tink 3 requires this dataset symbol pinned. The pre-registered fallback rule must be triggered or not based on actual cohort sizes, not estimates.

**Cost:** ~1 tick. Mostly LMFDB query + `register_dataset_snapshot` per `long_term_architecture.md §2.1`.

### 3. Coefficient sub-sweep on mixed-rank data

**What:** 1K-evaluation runs at 3 coefficient configurations (Tier B defaults, novelty-biased, fit-biased) on the pinned `Q_EC_R012_D5@v0` (or fallback). Verify Tier B defaults transfer to mixed-rank data without major recalibration.

**Why:** Coefficient defaults from Tier B Tink 2 were tuned on synthetic BSD-identity data. Real LMFDB data has noise, missing-data, and rank > 0 complications. The sub-sweep is the calibration check before the full Tink 3 commits compute.

**Cost:** ~1 tick.

### 4. Second-pass external review of v4 design

**What:** Same external reviewer who did rounds 1–3, OR fresh eyes. Specifically:
- Is the strong-form-equivalence test the right discipline upgrade?
- Are the break-rate thresholds defensible?
- Any genuinely-new issues v4 introduces (the seed-0 caveat surfaces a pattern; does v4 close it or just defer it)?
- Does anything in v4 break v2/v3 compositions?

**Why:** v3 was reviewed and tightened to v4 based on Tink 1 empirical learning. v4 should also be reviewed before implementation commits.

**Cost:** External-review wall-clock varies. Self-review can be a substitute (same reviewer doing multiple cold-reads).

### 5. Tink 3 implementation

**What:** Per design doc §4 + Tier B implementation patterns from `zoo/conjecture_gp/`. ~3–5 ticks once items 1–4 are complete. Major components:
- GP loop with full Tink 3 grammar (~11 atoms per §4.2)
- Behavioral-descriptor MAP-Elites (`tree_depth × basis_projection_bin`, 4×4 = 16 cells per §4.4)
- Cross-rank consistency check (per §4.5)
- Calibration battery with positive anchors (F003, F004, F002) AND negative control (F043_shape) all running strong-form tests
- Proxy-leakage audit per-Pareto-candidate with null-derived threshold (§5.6)
- Coefficient-sensitivity audit
- Output to `tink_3_results_<date>.md` + `tink_3_proposed_descriptors_<date>.md` + SIGNATURE jsonl

**Cost:** 3–5 ticks. Most expensive single deliverable in the Structure Hunter arc.

## Tier C work (post-Tink-3 if Pareto front emerges)

These are the v3 roadmap items that wait on Tink 3 producing real Pareto candidates and VACUUM signals.

### 6. `gen_11` merger via demand-driven topographic input

**What:** Per v3 roadmap §4. Structure Hunter absorbs `gen_11`'s coordinate-invention role by ingesting `VACUUM` and `EXHAUSTION` demand signals from the tensor as additional input. Atom priors + MAP-cell seed priors + δ-boost for vacuum-filling candidates.

**Why:** gen_11 and Structure Hunter have overlapping output (candidate P-IDs) and different inputs (tensor demand vs. grammar + data). Merger reduces substrate duplication.

**Cost:** 2–3 ticks. Spec exists in v3 roadmap; needs Tink 3 first to confirm Pareto candidates are actually substrate-relevant.

### 7. CAS Layer C production-grade

**What:** Per v3 roadmap §2. Replace cheap-path SymPy-only check with richer canonicalization rules including:
- BSD identity substitutions (rewrite log_L = ... in terms of basis atoms)
- Transcendental inverses (exp(log_x) = x detection)
- Polynomial ideal membership (Gröbner basis if grammar warrants)

**Why:** Tier B's CAS Layer C catches linear and polynomial-in-basis cases. The honest limitation flagged in `results_2026-04-25_tier_b.md` is the `stress_exp_logSha` candidate (transcendental composition) that neither linear Layer B nor cheap-CAS catches.

**Cost:** 2–3 ticks. SymPy can do most of it; SageMath/FLINT integration is v4 territory if SymPy proves insufficient.

### 8. Typed Relational Grammar (TRG) for cross-object structure

**What:** Per v3 roadmap §1. Atoms extend to arity > 1 (e.g., `(EC_object, modular_form_object) → feature`). New affordance type `cross_domain_projection_gain`. Makes F001 modularity reachable as a calibration anchor.

**Why:** v3-and-earlier grammar operates per-object. Cross-object structure (Langlands, modularity, Scholz reflection at the lift level) is structurally invisible. TRG is the principled extension.

**Cost:** 7–11 ticks (the largest single architectural extension in the v3 roadmap). Not a near-term followup; included for completeness.

### 9. η_trace latent-trace from Sovereign Harvest engine

**What:** Per v3 roadmap §5. AST execution traces tagged with the Prometheus reasoning-trace taxonomy (composition / reduction / lift / transformation / branch). Compose with the broader project's reasoning-trace harvest infrastructure.

**Why:** Tier B's η_trace is per-AST-step reversibility via local linear regression. The v3 roadmap proposal is richer: tag steps by their reasoning category and surface category-specific information loss.

**Cost:** 1–2 ticks. Cheap; depends on Sovereign Harvest taxonomy integration (AETHON Integration 1 per `aethon/living_ideas.md`).

## Substrate-promotion candidates

### 10. Strong-form-equivalence test as substrate primitive

**See:** `stoa/proposals/2026-04-26-sessionC-strong-form-equivalence-as-substrate-primitive.md`. Currently a Tink-3-scoped amendment; could promote to substrate-wide discipline if a second anchor case emerges (some other instrument's calibration battery catching an encoding-exploit).

### 11. Encoding-exploit failure mode as Pattern N

**What:** Tink 1 seed 0's `[(root_number * 0) == [rank == root_number]]` is an anchor case for a specific failure pattern: candidates that satisfy canonical-form checks via dataset-encoding properties rather than the anchor relation. The pattern is distinct from Pattern 30 (algebraic-identity coupling) and Pattern 18 (uniform visibility).

**Promotion criterion:** `pattern_library.md` says ≥3 anchor cases for promotion. Right now: 1 (seed 0). Two more anchors needed.

**Where to look for the second anchor:** Tink 3 calibration battery, or any other anchor-rediscovery test in the substrate (Cartography paper-v4 calibrations, Harmonia tensor cell verifications).

### 12. CONJECTURE_GENERATOR shelf entry graduation

**What:** `methodology_toolkit.md` entry #10 currently lists `CONJECTURE_GENERATOR@v0`. Graduation to `@v1` requires (per architecture doc §11):
- Definition DAG Phase 0 landed
- Grammar-time Pattern 30 + ideal-quotient checks shipped in `harmonia/sweeps/pattern_30.py`
- Tink 1 PASS (DONE 2026-04-25)
- Tink 2 DEMO (DONE 2026-04-25 Tier B)
- Encoding-perturbation artifacts present
- `gen_12` spec at `docs/prompts/gen_12_conjecture_generator.md`

Three of six gates passed. Definition DAG Phase 0 is the biggest remaining gate (3-5 ticks).

## Discussion / cross-references

- The `descriptor_collapse_audit.md` whitepaper (Zoo, v3.2) discusses MAP-Elites descriptor-collapse failure modes that are adjacent to Structure Hunter's Q5 review-round critique on AXIS_CLASS-as-coordinates. Might be worth a cross-reference once both whitepapers stabilize.
- The orbit-canonicalization whitepaper's "search vs representation" thesis composes naturally with Structure Hunter's grammar-level discipline. Joint methodology paper candidate.

## Comments / responses

(append below as discussion accretes)
