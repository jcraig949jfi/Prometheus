# Review Questions for `descriptor_collapse_audit.md` v3.3 / v3.4

### 2026-04-26 (questions A–J), updated 2026-04-26 evening with K and M1–M4 after first reviewer round

**Author of paper:** Harmonia_M2_auditor
**Author of these questions:** the same — this is a self-prepared scrutiny document submitted alongside the paper for external review.
**Paper:** `D:\Prometheus\whitepapers\descriptor_collapse_audit.md`
**Repository root:** `D:\Prometheus\exploratory\zoo\`

---

## What this document is

The paper's headline finding shifted twice in three days:
- v3.0: partial Branch-A pass, residual coupling unexplained.
- v3.1: residual coupling diagnosed as search starvation.
- v3.2: search-starvation interpretation hedged after self-review.
- v3.3: search starvation **falsified** by Phase 5b; coupling re-attributed to TT geometry.

Two unanticipated surprises were caught mid-session: a config-forwarding bug in `D:\Prometheus\exploratory\zoo\map_elites\multi_seed.py` (which silently disabled DMRG in Phase 4) and a refinement-induced collapse mechanism (DMRG-as-truncation pulling peaked profiles toward effective rank). Both surfaced only when explicitly searched for.

The base rate for a third unanticipated surprise in v3.3 is non-trivial. The next planned move is §8.2 — porting the audit framework to `D:\Prometheus\exploratory\tensor_decomp_qd\` to test the methodology contribution claim. Porting is harder to reverse than a paper edit, so v3.3 deserves a beat of external scrutiny first.

This document lists what I would attack if I were reviewing v3.3 cold, and the specific questions I want a frontier model (and James) to assess. Each section names a concrete experiment that would resolve it.

---

## A. Is the Outcome-B claim — "real TT-geometry signal, not search artifact" — bulletproof?

The Phase 5b headline (`D:\Prometheus\exploratory\zoo\results\phase5b_no_dmrg_20260425T033645.json`):
- Entropy axis filled to 84% of achievable [0.778, 1.609].
- Within-band MI on `(log_params, rank_entropy)` stayed at 25–61× the within-band shuffled null.
- Conclusion: residual coupling is structural, not search starvation.

Three rival hypotheses I have NOT formally ruled out:

### A1. Mutation-bias residue

The hybrid mutation at `shift_magnitude = 4` may induce structure between `log_params` and `rank_entropy` even if the underlying achievable region is otherwise clean. Specifically: a rank-shift transfer of magnitude 4 from bond $i$ to bond $j$ changes both `n_params` and `rank_entropy` simultaneously, and the joint update may correlate them.

**Question A1.** Does a uniform random sample of valid rank profiles (no MAP-Elites, no mutation) show the same KSG MI on `(log_params, rank_entropy)` that Phase 5b shows? If yes, geometry. If no, mutation-bias.

### A2. Placement-pressure structure

MAP-Elites cell replacement uses "lower `rel_error` wins within cell." This selects, at each (log_params, rank_entropy) cell, the rank profile with the lowest error among all profiles that landed in that cell during the run. The selected profiles may lie on a specific curve in shape-space because lower-error profiles at fixed total params tend toward more-uniform rank distributions for many functions.

**Question A2.** Repeat the audit on the **history** of evaluations (every probe), not just the **archive** (the cell-elite subset). If MI is lower on history than on archive, placement pressure is structuring the result.

A2 is testable on the existing dump — `D:\Prometheus\exploratory\zoo\results\phase5b_no_dmrg_20260425T033645.json` already stores `pooled_history` separately.

### A3. Combinatorial-discreteness artifact

With `max_bond = 16` and `d = 6`, the achievable rank profiles form a discrete lattice of at most $16^5 = 1{,}048{,}576$ tuples (smaller because each bond is bounded by `min(left_size, right_size)`). KSG MI on quantities derived from a discrete lattice has known biases — the estimator measures lattice structure, not continuous information.

**Question A3.** What is the KSG MI between `log_params` and `rank_entropy` over a uniform random sample of all valid rank profiles? This is the "lattice baseline." If it's of the same order as Phase 5b's measurement, the audit's verdict on Phase 5b is detecting the lattice itself, not a TT-specific geometric coupling.

A1, A2, A3 collapse into one experiment: enumerate or random-sample the valid rank profiles, audit them with the same Layer 1–5 pipeline, compare. Any deviation between Phase 5b's ratios and the lattice baseline is what we'd want to call "TT geometry."

---

## B. Is the within-band null methodology actually defensible at small n?

Phase 5b within-band cells have n = 59–130. The KSG estimator with k = 3 has small-n upward bias documented at order $1/n$ for low-dim continuous distributions. The within-band shuffled null is built at the same n, so first-order bias cancels. But:

- **B1.** Does the bias have higher-order n-dependence that does not cancel under shuffling? (Specifically: bias may depend on the joint distribution's support shape, which the shuffle changes.)
- **B2.** When the underlying data has lattice structure (per A3), KSG's bias may not match its continuous-distribution scaling. A shuffled null on lattice data may not bound the bias correctly.
- **B3.** A more conservative null would use a permutation test stratified by some observable feature (e.g., shuffle within `avg_rank` strata so the null preserves more structure). Should the within-band null be MORE constrained?

**Question B.** Is there a known small-n bias correction for KSG MI (e.g., Kraskov-Stögbauer-Grassberger 2004 §III.B has a bias term; later work by Gao et al. 2017 proposes corrections) that should be applied here? The paper currently doesn't mention any.

---

## C. Have I actually adopted the reviewer's reframe?

The previous external reviewer wrote (paraphrased): "Contribution = audit framework, TT = worked example. Structurally emphasize the framework; treat TT as illustration."

v3.3's abstract claims this reframe. But:
- §2 spends 6 subsections on TT machinery vs 1 on the audit (§2.6).
- §3 reports TT-specific Phase 4 outcomes.
- §4 has 7 subsections, all about the TT diagnostic chain.
- §5 has 5 lessons; only §5.4 and §5.5 generalize beyond TT.

**Question C.** Does the structural balance match the abstract's framing claim? A genuine reframe would have §2.6 expanded to a full section on the audit's general formulation, §4 split into two sections (audit-on-TT and TT-specific results), and the TT machinery in §2 contracted to a one-page summary. The current paper still reads more "TT result" than "audit framework with TT as illustration."

---

## D. Is the audit framework actually portable?

§8.2 proposes porting the audit to `D:\Prometheus\exploratory\tensor_decomp_qd\`. The audit module at `D:\Prometheus\exploratory\zoo\diagnostics\nonlinear.py` is documented as "reusable" but:

- **D1.** Imports take a `dict[str, np.ndarray]` of descriptor columns. The tensor-decomp project's data structures are different. Untested.
- **D2.** The within-band null logic in `D:\Prometheus\exploratory\zoo\experiments\analyze_conditional_mi.py` and `D:\Prometheus\exploratory\zoo\experiments\run_phase5b_no_dmrg.py` is duplicated; a clean reusable version doesn't exist as a single function.
- **D3.** The shuffled-null function assumes the "shuffle one column" pattern; some QD problems may need stratified shuffles or block shuffles, and the current code doesn't expose that.

**Question D.** Before §8.2 commits, what does a minimal "audit-as-package" interface look like? Specifically: which audit functions should accept generic descriptor records, what's the minimum set of dependencies, and where is the unit-test surface?

---

## E. Are there hidden assumptions about what counts as a "function" in the catalog?

The six functions are evaluated on a $(12,)^6$ grid. The function class implicitly assumed by the audit:
- Smooth or smooth-with-known-roughness (calibration anchors are exact algebraic; frontier are smooth).
- Real-valued (no complex tensors).
- Bounded (no near-singular behavior).
- Cartesian-grid-evaluable (no mesh-free or adaptive).

**Question E.** If a future user applies this audit to a tensor-decomposition QD problem (§8.2 target), do these assumptions transfer? Specifically: tensor decomposition over $\mathbb{F}_2$ or $\mathbb{F}_3$ is integer-valued and has different MI estimator behavior than real-valued continuous data. KSG MI is not directly applicable to discrete data; a different estimator (e.g., MI based on plug-in entropy estimates with Bayesian smoothing) would be needed.

---

## F. The "DMRG-as-truncation" finding (Phase 5 §4.5)

Phase 5 with DMRG actually on showed peaked rank profiles get pulled toward the function's effective rank. This was identified as a third coupling source.

- **F1.** Is this universally true for all rank-adaptive refinement operators, or specific to two-site DMRG with our particular `rel_tol` and rollback guard?
- **F2.** If the operator's effect on descriptor distribution is itself audit-detectable, should the audit framework include a "post-evaluation descriptor distribution check" as a default Layer 6?
- **F3.** The finding is presented as a side note in the TT paper. Is it stronger as a standalone? (The reviewer mentioned this could ship as a short companion paper.)

**Question F.** Should the DMRG-mask finding be the contribution of a separate methodology paper (audit-detects-operator-side-effects), with the geometry signal as the headline of THIS paper?

---

## G. Calibration anchors — sufficiency

Three anchors: rank 1, rank 2, incompressible. They span the corners but leave the middle empty.

- **G1.** A rank-4 separable function (e.g., $\sum_{i,j} x_i x_j$ on disjoint pairs) would be a mid-rank known anchor.
- **G2.** A function with known closed-form effective rank (e.g., a tensor-product polynomial of degree $p$ has effective rank ≤ $\binom{d+p}{p}$) would be a mid-rank quantitative anchor.

**Question G.** Should the calibration contract be tightened with a fourth anchor before §8.1's "audit other descriptor pairs" experiment runs? The current contract has no near-misses, which means we don't know how the audit behaves at the boundary between calibration and frontier.

---

## H. The proposed Phase 6 experiments — are they the right ones?

§8.1 lists three sharpening experiments. §8.2 lists cross-domain validation. Other priorities not explicitly listed:

- **H1.** A formal information-theoretic lower bound on MI between `log_params` and `rank_entropy` derived from the rank-profile lattice. If the lattice itself bounds MI from below at, say, 1.2 nats, the Phase 5b measurement of 1.6–1.9 nats is "lattice + 0.4 nats of TT-specific structure." Cleanly separates the structural from the geometric.
- **H2.** Comparison between TT-SVD-only and TT-cross-decomposed approximations on the same catalog. The current paper's findings are TT-SVD-specific.
- **H3.** Test whether the audit framework, as designed, can distinguish between an Outcome-B function (geometric coupling) and an Outcome-A function. Does Phase 5b's audit produce different verdicts on a hand-constructed function with known-orthogonal descriptors?

**Question H.** Among A1–G2, which experiments would most strengthen v3.3 if executed before §8.2 commits to porting?

---

## I. Are there bugs analogous to the `multi_seed.py` issue still in the codebase?

The `multi_seed.py` bug forwarded only a subset of `LoopConfig` fields per seed. Similar patterns elsewhere:
- **I1.** `D:\Prometheus\exploratory\zoo\experiments\run_phase4.py` and other drivers construct `LoopConfig` and pass to `run_multi_seed`. The constructor pattern is identical across drivers; if one driver passes something the multi-seed harness ignores, the bug surfaces silently.
- **I2.** The `Elite` class has an `extras: dict | None = None`. Various downstream code does `(e.extras or {}).get("rank_entropy", 0.0)`. If a future descriptor isn't logged, it silently defaults to 0.

**Question I.** Should v3.4 include a code audit pass for "silent-default" patterns analogous to the multi-seed bug? A lint rule or assertion-based contract would catch these.

---

## J. The decision: is §8.2 (cross-domain audit) the right next move?

Reviewer's recommendation was "§8.2 is the publishable methodology path." But:
- v3.3 finds Outcome B (negative result), not Outcome A. The paper's main claim is now "TT axes don't decouple," not "audit framework demonstrates decoupling on TT."
- §8.2 ports a framework that has been tested on a worked example with a negative result. That's still useful (the framework caught the negative result), but framing changes.

**Question J.** Given Outcome B, should §8.2 (port framework) precede or follow §8.1 (sharpen geometry-signal claim)? An argument for §8.1 first: if the geometry-signal claim is the main contribution, sharpening it is the highest-leverage move and gives §8.2 a stronger paper to port from. An argument for §8.2 first: framework portability is the methodology contribution; if the framework doesn't port cleanly, that's load-bearing for any reviewer.

---

---

## Questions added 2026-04-26 evening (K, M1–M4) after first reviewer round

The first external reviewer (anonymous frontier model, 2026-04-26 morning) returned a sharp critique. They affirmed A and A3 as the existential threats; elevated A2 (archive-selection pressure) from "one rival among three" to co-primary; and named a missing question that I have now numbered K. They also surfaced four further questions M1–M4 that are foundational to whether this work composes with the rest of Prometheus.

The fulcrum experiment in §4.7 of v3.4 addresses A1+A2+A3 and K (specifically Sub 3 implements the identifiability test below). M1–M4 remain open.

### Question K — Identifiability of the audit itself

Can the audit framework distinguish, in controlled synthetic worlds with known ground truth:
- INDEPENDENT (no coupling)
- LINEAR coupling
- NONLINEAR coupling
- DISCRETIZATION-only coupling (lattice + noise; no continuous structure)
- SELECTION-COUPLED (apparent coupling from elite-selection on independent data)

The audit must classify each correctly. Failing to distinguish these is a methodology gap, not a TT-specific concern.

**v3.4 partial answer (§4.7 Sub 3):** the audit correctly classifies INDEPENDENT, LINEAR, NONLINEAR, and SELECTION_COUPLED. It FAILS on DISCRETIZATION — reporting MI = 1.65 nats on a synthetic where there is no continuous coupling, only lattice structure plus noise. Disclosed in Limitation 8 of v3.4. The audit cannot distinguish "lattice + noise" from "continuous nonlinear coupling." This is a real limitation, not just a caveat.

### Question M1 — Is MAP-Elites the wrong microscope?

The current paper asks: are MAP-Elites placement descriptors independent? It does not ask: is gridded archive occupancy the right object for discovering descriptor-geometry properties at all? Maybe descriptor-collapse audits should run on sampled rank-profile manifolds independent of MAP-Elites — in which case the methodology generalizes more strongly, but the framing changes from "audit MAP-Elites archives" to "audit descriptor maps in their natural domain."

This question is Prometheus-relevant because Prometheus's mantra ("compressing coordinate systems of legibility, not laws") suggests the right substrate object may be the descriptor map itself, not its image under one search procedure.

### Question M2 — Coordinate pathology vs structural law

The paper blurs two layers. Is the audit:
- detecting BAD COORDINATES (descriptor design pathology — different layer of analysis from the underlying mathematics)
- or REVEALING INVARIANT STRUCTURE (something a future Prometheus could promote to substrate)

These are not the same. The current paper acts as if the audit's verdict is read from the geometry, but in v3.4's three-tier discipline (§5.1), only Tier 3 supports that reading. The honest M2 answer for v3.4: the audit detects **descriptor design pathology that interacts with TT evaluation** — Tier 2 — and a Tier-3 invariant-structure claim is not yet earned.

### Question M3 — Does the audit compose with substrate/reasoning architecture?

The paper asks whether the audit ports to other QD codebases (§8.2). It does not ask whether audit OUTPUTS become first-class substrate objects. Concrete possibilities:
- A descriptor-dependence GRAPH per problem domain (nodes = descriptors, edges = MI flagged at threshold).
- COLLAPSE CERTIFICATES — versioned, hash-pinned records that a given (descriptor pair, function class, search procedure) failed the audit at a specific tier.
- A COORDINATE-PATHOLOGY REGISTRY — analogous to Prometheus's symbol registry but for known-bad descriptor combinations, with provenance.

If audit results stay as one-off experiment dumps, the methodology stranded. If they become substrate objects with the same versioning discipline as F-IDs and P-IDs, the methodology composes with Prometheus's actual architecture. M3 is the question of whether to invest in that composition.

### Question M4 — Is MI even the right object?

KSG MI is one choice among many information-theoretic dependence measures. The reviewer suggests:
- Persistent homology of the descriptor-image point cloud.
- Manifold-dimension estimates (e.g., correlation dimension, intrinsic-dimension estimators on the descriptor scatter).
- Jacobian rank of the descriptor map (when the map is differentiable).

These would give DIFFERENT signals than MI. A descriptor pair could have low MI but constrain to a low-dimensional manifold; or have high MI but with manifold dimension equal to the ambient dimension. The audit currently reads only one of these signals.

The DISCRETIZATION false-positive in K is an instance of this: MI is high, but a manifold-dimension probe would correctly identify the lattice structure as 1-dimensional in a way MI does not.

---

## What I want from external review

A frontier model with no skin in the game should:

1. Pick the 2–3 questions above that most threaten v3.3's defensibility.
2. Propose what a stronger version of those questions would be (the questions I haven't thought to ask).
3. Recommend a specific ordering: which experiment runs first, what should change in the paper before that experiment, and what evidence would make the recommendation falsifiable.
4. Identify any claim in v3.3 that should be retracted or hedged before review-2.

I am specifically NOT asking for: a copy-edit pass, a reformatting suggestion, or a reframe of the abstract. The paper is a working draft; the question is whether the science is defensible.

---

## Artifacts the reviewer needs

| Artifact | Full path |
|---|---|
| Paper v3.3 | `D:\Prometheus\whitepapers\descriptor_collapse_audit.md` |
| Phase 5b dump (decisive Branch-A) | `D:\Prometheus\exploratory\zoo\results\phase5b_no_dmrg_20260425T033645.json` |
| Phase 5 dump (DMRG-mask finding) | `D:\Prometheus\exploratory\zoo\results\phase5_20260425T032712.json` |
| DMRG unit test | `D:\Prometheus\exploratory\zoo\results\dmrg_unit_test.json` |
| Within-band null (matched-n fix) | `D:\Prometheus\exploratory\zoo\results\phase4_within_band_null.json` |
| Audit module (the methodology contribution) | `D:\Prometheus\exploratory\zoo\diagnostics\nonlinear.py` |
| Phase 5b driver | `D:\Prometheus\exploratory\zoo\experiments\run_phase5b_no_dmrg.py` |
| Loop with diversified seeding | `D:\Prometheus\exploratory\zoo\map_elites\loop.py` |
| Multi-seed (post bug-fix) | `D:\Prometheus\exploratory\zoo\map_elites\multi_seed.py` |
| Three-phase entropy distributions | `D:\Prometheus\exploratory\zoo\docs\figures\fig_j_entropy_three_phases.png` |
| Phase 5b decisive scatter | `D:\Prometheus\exploratory\zoo\docs\figures\fig_k_phase5b_scatter.png` |

---

## Self-assessment of my own scrutiny

I have NOT executed any of the experiments proposed above. I have NOT generated additional figures. I have NOT changed the paper's claims. This document is questions only — what I would want a sharper-than-me reviewer to attack.

If the reviewer answers the questions and most of v3.3 holds, §8.2 commits with confidence. If the reviewer finds load-bearing problems, v3.3 needs revision before any cross-domain port.

The single highest-leverage experiment, by my estimation: A1+A2+A3 collapsed into the "audit on uniform random rank profiles" baseline. ~30 minutes compute on the existing infrastructure. Resolves whether Outcome B is real geometry or audit-measures-its-own-search.

---

*Review questions v1.1 — 2026-04-26 evening. Companion to `D:\Prometheus\whitepapers\descriptor_collapse_audit.md` v3.4. K added with §4.7 Sub 3 partial answer; M1–M4 added unaddressed for next review round.*

*v1.0 — 2026-04-26 morning. A–J only.*
