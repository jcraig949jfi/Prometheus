# Negative Results in AI for Mathematical Discovery: A Case Study in Reward Pathology and Self-Falsifying Systems

**Draft v0 — 2026-05-04 — Techne**

**Status:** Revision pass (v1) of the methodology paper outlined in `pivot/methodology_paper_outline_2026-05-04.md`. Sections 1 (Abstract / Introduction), 4 (Cross-domain "validation"), 6 (Layer 1/2/3 diagnosis), and 9 (What this means going forward) expanded from v0 with deeper credibility-gap framing, per-domain mathematical structure, continuous-reward synthetic test detail, and post-pivot empirical state. Sections 2, 3, 5, 7, 8, 10 carried forward from v0. Decisions awaited (target venue, co-authorship, naming of compared systems) remain open and are not addressed in this draft.

**Empirical anchors added since outline (Day 1-5 of the kill-space pivot, 2026-05-04):**
- Synthetic test (Day 1): Case A verdict, full results in `prometheus_math/MODAL_COLLAPSE_SYNTHETIC_RESULTS.md`.
- Gradient archaeology (Day 2): 4/6 of Aporia's negative-space gradients already visible in the existing 314,971-record ledger (`prometheus_math/GRADIENT_ARCHAEOLOGY_RESULTS.md`).
- KillVector substrate change (Day 3): per-component margin vector replaces categorical kill_path (`prometheus_math/KILL_VECTOR_SPEC.md`).
- Per-component learner (Day 4): logistic + linear regression head per component, ties cell-mean baseline on legacy data (`prometheus_math/KILL_VECTOR_LEARNER_RESULTS.md`).
- Native KillVector pilot (Day 5): 24 000 episodes, 138 seconds, 126 983x distinguishability gain in margin space over legacy categorical (`prometheus_math/NATIVE_KILL_VECTOR_PILOT_RESULTS.md`, `prometheus_math/KILL_VECTOR_NAVIGATOR_RESULTS.md`).

---

## 1. Abstract / Introduction

We report a negative result and the methodology that produced it. To our knowledge, **Prometheus is the first multi-agent AI-for-mathematics substrate that successfully falsified its own headline findings within 24 hours of generation.** A reinforcement-learning discovery loop targeting the Lehmer / Mahler-measure search produced consistent cross-domain "successes" on six independent mathematical domains — BSD rank, modular forms, knot trace fields, genus-2 curves, OEIS sleeping-beauty sequences, and mock theta functions — with lifts ranging from +1.37x (BSD) to +18x (OEIS) over a uniform-random baseline at Welch p < 0.05 in every case. Each result was produced by an identical pipeline, with deterministic seeds, multiple replications, and ~350 000 cumulative training episodes. This is the kind of result typically published as cross-domain validation of a discovery substrate.

A subsequent one-hour synthetic control, designed by an internal adversarial agent (Aporia) and using the *identical* training pipeline on a continuous regression task with linearly separable Gaussian-noise structure, demonstrated that the underlying RL learner does not learn. REINFORCE collapses to <=3 reward bins on every variant, with >99% of action mass concentrated on the modal bins. PPO stays uniform across all 21 bins. On a low-noise variant (V3) where ordinary least squares trivially solves the task at >=60% bin accuracy, REINFORCE achieves 4.91% versus 4.84% for uniform random — statistically indistinguishable. On a class-skewed variant (V2) with no discoverable mathematical structure, REINFORCE produces a 5.8x lift over random — the same lift pattern we had observed across the six "real" domains. A follow-up battery (`prometheus_math/MODAL_COLLAPSE_CONTINUOUS_RESULTS.md`) replaced the binary reward with three calibrated continuous reward shapes (L2, L1, log-likelihood); on every shape, on every variant, REINFORCE still collapses to ≤3 active bins and PPO stays uniform. The collapse target moves; the collapse does not break.

The conclusion is unambiguous: the cross-domain "successes" of the headline were class-prior recovery via entropy collapse onto the modal class, not learned mathematical structure. The lifts reproduce on a synthetic environment where there is, by construction, nothing to discover. We retracted the headline internally and pivoted to a five-day substrate redesign whose final pilot (`prometheus_math/NATIVE_KILL_VECTOR_PILOT_RESULTS.md`) produced a 126 983x distinguishability gain between operators in margin space versus the legacy categorical kill_path representation, indicating that the substrate had been logging operator-distinguishing data at a discriminative level five orders of magnitude weaker than what one 138-second native pilot could produce when the right representation was in place.

**The 2026 credibility gap in AI-for-math.** We write this paper because the field is, at the time of writing, accumulating discovery claims faster than the falsification discipline that should accompany them. We see three recurring patterns in the published landscape, characterized here without naming systems. *First*, claims of "discovering new mathematical objects" in domains with skewed class priors that, on closer reading, are modal-class predictions dressed in domain language: a model that consistently predicts the dominant rank, the dominant Hecke eigenvalue bin, or the dominant growth-rate class will produce headline-grade lifts over uniform-random baselines without learning any structure that deserves the name *discovery*. *Second*, "cross-domain transport" claims supported only by class-prior-correlated lifts: the same pipeline, run on N domains with similar prior asymmetry, produces lifts in similar bands, and the band itself is reported as evidence of generalization. *Third*, an absence of synthetic null controls — environments where the right answer is, by construction, absent — that would distinguish learned structure from recovered prior. Most systems we surveyed cannot detect class-prior recovery in themselves, because their evaluation harnesses score against uniform-random rather than against an always-predict-mode baseline.

Our own substrate produced exactly the kind of result this gap rewards. The methodological contribution is the substrate itself, framed as an instrument: typed CLAIM/FALSIFY/PROMOTE records, hash-locked caveats inherited through provenance, kill_path metadata on every rejection, deterministic seeds, mandatory five-catalog cross-checks, four orthogonal falsification gates (F1 permutation null, F6 base rate, F9 simpler-explanation, F11 cross-validation), and — added on 2026-05-04 — a synthetic null-control discipline as a precondition for any cross-domain claim. The headline died at internal review, before any external write-up began. The substrate caught it in itself before the failure mode could leak upward.

The operational diagnosis we offer is the *gradient field of failure*. What most papers describe as "discovery" is, in the worst case, a mode-collapsed posterior on the class prior; what looks like a learning curve climbing a structured signal is often a policy converging on the L2-optimal scalar estimate or the modal class. We argue this can be diagnosed cheaply (synthetic null controls cost seconds; class-prior baselines are a one-line change; per-component margin vectors expose operator-level structure that scalar reward throws away) and that the cost asymmetry is favorable enough that the discipline should be a community norm rather than an internal courtesy.

We do not claim a mathematical discovery. We claim a methodological one. We argue that most published AI-for-math results would fail to clear this bar: the typical pipeline lacks synthetic null controls, lacks class-prior-recovery ablations, reports caveats in prose rather than as structured records propagated through provenance, and cannot distinguish "learned mathematical structure" from "recovered the dominant class with high confidence."

The paper has three parts. First, we describe the substrate as an *instrument* for catching false positives, not as a discovery engine (Sections 2-3). Second, we walk through the worked case study: the seductive cross-domain headline (Section 4), the synthetic test that killed it (Section 5), and the Layer 2 / Layer 3 diagnosis that explains why (Section 6). Third, we describe what changed afterward — a kill-vector representation, an end-to-end pilot, region-densification across multiple cells, a navigator that ranks operators by expected kill magnitude, and an extended PPO run that delivered Verdict B at 80 000 episodes — and we close with literature comparison, limitations, and venue questions for negative-results methodology in AI-for-math (Sections 7-10).

The thesis is one line:

> *A falsification-first system without a gradient becomes a perfect null-result generator. Building one that catches itself before publication is the contribution.*

---

## 2. System architecture — substrate as instrument

Prometheus is a multi-agent substrate built around a seven-opcode kernel called sigma (Sigma):

- **RESOLVE** — produce a candidate from an environment.
- **CLAIM** — declare a result, attach typed metadata, no commitment yet.
- **FALSIFY** — apply orthogonal probes against the claim.
- **GATE** — run terminal-state arbitration; CLAIM cannot move forward without passing.
- **PROMOTE** — admit the claim to the durable ledger; hash-locked def_blob, caveats included.
- **ERRATA** — patch a previously-promoted record (rare; auditable).
- **TRACE** — propagate provenance forward; downstream consumers inherit caveats automatically.

Three substrate properties matter for this paper. **Caveat-as-metadata:** caveats are typed structured records (e.g., `small_n`, `mode_collapse`, `rediscovery_not_discovery`, `synthetic_battery_used`) hash-locked into the PROMOTE def_blob. They cannot be silently dropped between internal summary and external write-up because dropping one breaks the hash chain. **Three terminal states:** PROMOTED, SHADOW_CATALOG (kept but flagged — "this looked plausible, here is the kill_path, do not delete"), REJECTED. **Cost-model calibration:** top-50 hot-path operations are required to stay within 2x of empirical-vs-declared cost; drift triggers recalibration before any further runs. As of 2026-05-04 we report 50/50 ops within 2x (was 33/50 a week prior; the worst case had been 757x).

The substrate is intentionally framed in this paper as an instrument for catching bad claims, not as a discovery engine. As of the date of this draft, we have *zero* PROMOTEs from the discovery pipeline that survive as novel mathematical results; all PROMOTEs are rediscoveries (Mossinghoff entries, LMFDB rows, OEIS sequences). Whether the substrate is also a discovery engine is the open question Section 9 addresses.

**Kill-vector extension (Day 3 of the kill-space pivot, 2026-05-04).** Earlier substrate versions logged a single categorical `kill_pattern: str` per rejection (e.g., `out_of_band:M_outside_(1.001,1.18)`). Day 3 replaced this with a 12-component `KillVector` data structure: for each falsifier (out_of_band, reciprocity, irreducibility, five catalog adapters, F1, F6, F9, F11), the substrate records both `triggered: bool` and a continuous `margin: float | None` representing the signed distance to the falsification boundary. The KillVector is the substrate for Day 4 (a per-component learner) and Day 5 (a navigator that ranks operators by expected kill magnitude). Backwards compatibility is preserved: legacy `DiscoveryRecord.kill_pattern` continues to work, and `kill_vector_from_legacy()` reconstructs as much of a vector as the legacy data allows. See `prometheus_math/KILL_VECTOR_SPEC.md`.

The Section 7 finding that motivated this change — a 126 983x gap in operator distinguishability between margin and categorical representations — is the empirical anchor for the substrate redesign.

---

## 3. The substrate's evaluation primitives

A claim must clear three gate layers before reaching PROMOTE.

**Five-catalog cross-check.** Every candidate Mahler-measure / Lehmer claim is run against five independent catalog sources: Mossinghoff (8625 entries, refreshed via Wayback Machine 2026-05-03), `lehmer_literature` (24 entries, hand-curated from published surveys), LMFDB number-field tables, OEIS, and an arXiv title fuzzy-match probe. A genuine novelty must be absent from all five.

**Four-fold falsification (F1, F6, F9, F11).** F1 (permutation-null test): observed Mahler measure must be more extreme than the median permutation. F6 (base-rate check): coefficient structure must not be trivial — fewer than two distinct nonzero coefficients triggers the gate. F9 (simpler-explanation check): if a cyclotomic decomposition explains the M-value within numerical noise, F9 fires. F11 (cross-validation): the same M, computed via two independent methods (numpy companion-matrix eigvals vs mpmath dps=30 root-finding), must agree.

**Reciprocity and irreducibility gates.** Reciprocity: the polynomial must be palindromic (`c_i == c_{n-i}`). Irreducibility: `factor_list` over Q must return exactly one nontrivial factor.

The four-category math-TDD gate (authority / property / edge / composition) and the seven-category bug-hunt gate run before any operation reaches PROMOTE. As of 2026-05-04, 99 new domain tests, 18 new falsifier tests, and 19 new caveat tests have been added to the existing 2 436-test stack, bringing it to 2 625 passing, 0 failing.

**Three terminal states.** PROMOTED (clears all gates, hash-locked def_blob, caveats inherited), SHADOW_CATALOG (cleared some gates but not all — kept with kill_path explicit), REJECTED (failed an early gate, recorded with kill_path).

We emphasize: the gate machinery does not by itself produce discoveries. It produces an honest accounting of what the search returned. The accounting can be empty (0 PROMOTE) and that emptiness is the substrate working as designed.

---

## 4. The substrate's first failure case — cross-domain "validation"

This section presents the seductive result in the form it would have appeared had the discipline stopped here.

We tested the substrate's cross-domain transport on six independent mathematical domains, each backed by a public catalog of ground-truth labels:

| Domain | Catalog | n | Best algorithm | Lift over random | Welch p |
|---|---|---|---|---|---|
| BSD rank | Cremona allbsd | 1000 | REINFORCE-linear | +1.37x | 0.00055 |
| Modular forms | LMFDB | 7875 | PPO-MLP | +1.58x | 0.00034 |
| Knot trace fields | LMFDB nf | 48 | REINFORCE-linear | +5.40x | 1.84e-7 |
| Genus-2 curves | LMFDB | 6000 | REINFORCE-linear | +1.59x | 0.028 |
| OEIS Sleeping Beauty | OEIS A-numbers | 205 | growth-heuristic | +18.13x | <1e-6 |
| Mock theta functions | LMFDB / surveys | 44 | REINFORCE-linear | +12x | 1.76e-4 |

Methodology was uniform: 21-bin classification of a domain-appropriate target (rank for BSD, Hecke eigenvalue bin for modular forms, trace-field discriminant class for knots, Mordell-Weil rank for genus-2, growth-rate bin for OEIS, leading-coefficient class for mock theta), episode length 1, 0/1 reward (`100` if predicted bin == true bin, else `0`), 5 000 episodes per arm, 3 seeds per arm, deterministic NumPy implementations of REINFORCE and PPO, identical entropy-bonus and clipping hyperparameters across domains. 350 000 total episodes accumulated. Pre-registered evaluation harness, five-catalog cross-check passed on every domain, four-fold falsification gates passed on every domain.

This is what most papers in the current AI-for-math landscape would publish as "cross-domain validation of a discovery substrate." The methodological pattern — uniform pipeline, multiple domains, lift-over-random with significance tests, deterministic seeds — is recognizable. So is the temptation to write up the table.

**Per-domain mathematical depth.** Each row of the table above sits on top of a different mathematical structure. We summarize what the substrate was *nominally* predicting in each domain, and what it would have meant to actually learn:

- **BSD rank.** The Birch–Swinnerton-Dyer conjecture relates the rank of an elliptic curve's Mordell–Weil group to the order of vanishing of its L-function at s=1. The substrate's task: from a stratified sample of 1 000 elliptic curves drawn from the Cremona `allbsd` table, predict the rank class (0, 1, 2+) from a 26-dimensional feature vector built from conductor, regulator, torsion structure, and small-prime ap values. To actually learn rank prediction would mean recovering a feature-level shadow of BSD's analytic-rank / algebraic-rank correspondence. To *not* learn rank prediction is to recover the rank-0 / rank-1 modal prior — the empirical class skew on Cremona's stratified sample is approximately 70:30 in favor of rank ≤ 1.
- **Modular forms.** A weight-2 newform of level N has a Fourier expansion whose coefficients are eigenvalues of the Hecke operators. The substrate's task: predict a 21-bin classification of the Hecke eigenvalue ap at a small fixed prime p, given a feature representation of the form's Dirichlet character, level, and weight (LMFDB classical newforms, 7 875 forms after restriction to weight 2 and level ≤ 1 000). To actually learn Hecke eigenvalues from form-level metadata would be a substantial result. To *not* learn them is to recover the central-bin class prior of a Sato–Tate-distributed quantity, which on a 21-bin grid is sharply peaked.
- **Knot trace fields.** For a hyperbolic 3-manifold, the trace field is the field generated by traces of the holonomy representation; for hyperbolic knots it is a number field whose discriminant carries deep arithmetic information. The substrate's task: predict a discriminant-class bin of the trace field from features of the Alexander polynomial (n=48 hyperbolic knots in LMFDB's `nf` cross-reference). The lift here (+5.40x) is the most striking in the table — and also the most class-skewed: 41 of the 48 trace fields fall in the same discriminant class, so an always-predict-mode baseline alone would achieve ~85% accuracy. The "lift over uniform random" comparison is therefore the wrong baseline.
- **Genus-2 curves.** The Mordell–Weil rank of the Jacobian of a genus-2 curve is an analogue of the elliptic-curve rank but with a richer endomorphism structure. The substrate's task: 3-bin rank classification (rank 0 / 1 / ≥2) from 6 000 LMFDB genus-2 curves with computed Mordell–Weil data. The +1.59x lift mirrors BSD: a 3-class modal prior with rank ≤ 1 dominant, recovered by entropy collapse.
- **OEIS Sleeping Beauty.** A Sleeping-Beauty sequence is an OEIS entry that lay quiescent for years before a single late-arriving term re-activated interest. The substrate's task: from the first k known terms of 205 manually-curated A-numbers, predict the next-term growth-rate bin (21 bins covering a log-spaced range). The +18.13x lift here is the only one *not* produced by RL: it comes from a hand-coded log-linear extrapolation heuristic that beats the RL arms by a wide margin, and the table is being honest by reporting whichever algorithm won — but as a substrate result, this is not RL learning anything; it is a closed-form extrapolator working as designed.
- **Mock theta functions.** Ramanujan's mock theta functions are q-series whose coefficients exhibit congruence properties analogous to those of modular forms but resist a simple modular interpretation. The substrate's task: from 44 LMFDB / survey-collected mock theta entries, predict a leading-coefficient class on a small-integer 21-bin grid. The +12x lift is again class-skew driven: small-magnitude integer leading coefficients dominate the catalog.

In every domain the lift is computed against a uniform-random baseline, *not* against an always-predict-mode baseline. The same RL pipeline, with the same entropy-floor REINFORCE and the same MLP PPO, produces a lift in the +1.4x to +18x band across six domains whose mathematical structures are entirely different. That is not evidence of generalization across mathematical structure. That is evidence that the same modal-collapse pathology produces lifts in the same band whenever the underlying class distribution is moderately skewed — and class skew is the rule, not the exception, in catalog-backed math classification.

**What this is NOT.** Per the discipline of caveat-as-metadata, every headline number in the table above carries an inline caveat that the substrate logs alongside the lift. We reproduce them here, because the discipline of inline caveats is the methodological point:

| Domain | What this is NOT | Class-skew note |
|---|---|---|
| BSD rank | NOT learning rank prediction; collapsing to rank-0 / rank-1 modal prior. | ~70% rank ≤ 1 in Cremona stratified n=1000. |
| Modular forms | NOT learning Hecke eigenvalues; 21-bin classification with central-bin skew. | Sato–Tate peaks at central bins; LMFDB n=7875. |
| Knot trace fields | NOT learning Alexander → trace-field map; 85% class skew inflates lift. | 41/48 in same discriminant class; n=48. |
| Genus-2 curves | NOT learning Mordell-Weil rank; 3-class modal prior again. | Rank ≤ 1 dominant; LMFDB n=6000. |
| OEIS Sleeping Beauty | NOT an RL result; log-linear extrapolation is the structure; RL arms underperform. | Closed-form heuristic, not the substrate's loop; n=205. |
| Mock theta | NOT learning q-series structure; modal collapse to small-magnitude integer bins. | Small-integer leading coefficients dominate; n=44. |

The lifts above are computed against a uniform-random baseline. They are not computed against a class-prior-recovery baseline (always-predict-mode), which is the relevant null for any classification task with class skew. We did not run that ablation before assembling the table internally — that omission, more than any technical bug, is the methodological lesson. The dataset details — a Mossinghoff snapshot at 8 625 entries (the parallel target for the Lehmer search itself, refreshed via Wayback Machine 2026-05-03), Cremona's 1 000 stratified curves, LMFDB's 7 875 newforms and 6 000 genus-2 curves, the 48 hyperbolic knots with trace-field cross-reference, 205 OEIS Sleeping Beauties, 44 mock theta entries — are not exotic. They are precisely the catalogs an AI-for-math team is most likely to reach for, and the failure mode we describe is therefore the failure mode most accessible to any team that runs the same pipeline.

The honest engineering claim from this table: the kernel's I/O surface is uniform enough to host six environments without per-domain plumbing, the substrate logs deterministic-seed reproducible runs across all six, the gate machinery executes correctly across all six, and zero of the runs produced PROMOTE-eligible novelties. That is an engineering result.

The honest non-claim: this table demonstrates kernel I/O uniformity (engineering) and a cross-domain replication of the well-known "REINFORCE/PPO collapses to modal class on contextual bandits with sparse 0/1 reward" failure mode (negative result). It does not demonstrate mathematical-capability transport. A non-tautological transport claim would require *(a)* train on N domains, evaluate on the (N+1)th with labels hidden, lift > class-prior baseline; *or (b)* a single hyperparameter set that produces signal beyond modal recovery across domains; *or (c)* the discovery loop produces a result that domain experts confirm is novel. Zero of those tests have been done.

We did not yet know any of this when the table was assembled internally. The synthetic test of Section 5 changed that.

---

## 5. Falsifying our own headline — the synthetic test

The kill, presented straight.

**Origin.** The synthetic test was specified by Aporia (an internal adversarial agent in Prometheus) on 2026-05-04, *after* the cross-domain table of Section 4 was assembled internally. Aporia's mandate: build the simplest possible synthetic environment that uses the *identical* training pipeline as the six real environments, on a target where the right answer is mechanistically known, and run it before any external write-up.

**Design.** Continuous regression task: the agent receives an observation `x ~ N(0, I_d)` with `d = 20`, concatenated with the same 6-feature history vector used by the real BSD environment, giving a 26-dimensional observation matching the real domains' obs_dim. Hidden truth: `y = w . x + b + epsilon`, with `w` unit-norm in R^20, `b` a scalar, `epsilon ~ N(0, sigma^2)`. Action space: 21 bins covering `y` (matches `modular_form_env.N_BINS`). Reward: 100 if predicted bin == true bin, else 0 (matches `REWARD_HIT/REWARD_MISS` in both real environments). Trainers: byte-for-byte ports of the real environments' `train_random / train_reinforce / train_ppo`, with the same hyperparameters, the same NumPy implementations, the same entropy coefficient, the same baseline decay, the same PPO clip epsilon, and the same MLP shape. Only the environment varies.

**Variants.**

| Variant | Binning | sigma | Description |
|---|---|---|---|
| V1 BALANCED | uniform | 0.10 | "Is the agent fundamentally OK?" |
| V2 SKEWED | inner-tight | 0.10 | Matches real-domain class-prior imbalance. |
| V3 LOW-NOISE | uniform | 0.01 | Decisive: trivially learnable by lstsq. |
| V4 SKEWED + HIGH-sigma | inner-tight | 0.50 | Real-domain stress test. |

**Authority gate.** V3 is solvable in principle. A pure-NumPy least-squares fit on 1 000 (x, y) samples, then bin via `searchsorted` on the env's edges, achieves bin accuracy `>= 60%` (test `test_authority_linear_truth_recoverable_in_principle` in `prometheus_math/tests/test_modal_collapse_synthetic.py`). So if a trainer doesn't beat random on V3, that is the trainer's failure, not the environment's.

**Total budget.** 4 variants x 3 algorithms x 3 seeds x 5 000 episodes = 180 000 episodes, 11 seconds wall-clock on a single CPU core.

**Result, V1 BALANCED (random baseline ~ 4.76%).** REINFORCE achieves 7.00% accuracy with **3 active bins out of 21**, top-3 mass = 99.4%. PPO 4.38%, 21 active bins (uniform). Random 4.75%, 21 bins.

**Result, V2 SKEWED.** REINFORCE achieves 26.94% accuracy — a 5.8x lift over uniform random — with **2 active bins**, top-3 mass = 99.3%. PPO 4.57%, 21 bins. Random 4.64%, 21 bins. **This is the textbook "modal-class collapse looks like signal" result.** REINFORCE crushes random by collapsing to two bins that absorb >50% of the y-distribution mass. The lift is real. The reasoning that "the agent learned w.x" is false. The agent learned the prior, not the map.

**Result, V3 LOW-NOISE BALANCED.** REINFORCE 4.91%, **3 active bins**, top-3 mass = 99.1%. PPO 4.61%, 21 active bins. Random 4.84%. Lstsq baseline (independent authority test): >=60%. **REINFORCE is statistically indistinguishable from random on a task where ordinary least squares solves the bin-classification trivially.** This is the decisive variant.

**Result, V4 SKEWED + HIGH-sigma.** REINFORCE 18.93%, 3 active bins. PPO 4.64%, 21 bins. Random 4.60%. Same modal-collapse signature.

**Modal-collapse signature.**

| Variant | REINFORCE active bins | PPO active bins | REINFORCE top-3 mass |
|---|---|---|---|
| V1 balanced | 3 | 21 | 0.994 |
| V2 skewed | 2 | 21 | 0.993 |
| V3 low-noise (decisive) | 3 | 21 | 0.991 |
| V4 skewed + high-sigma | 3 | 21 | 0.993 |

REINFORCE collapses to <=3 bins on every variant including V3 where the environment is trivially learnable. PPO stays uniform on every variant including V3. Neither agent learns w.x even in the regime where lstsq trivially does.

**Verdict: Case A.** The substrate is broken at the search-mechanism layer. The cross-domain "successes" of Section 4 are class-prior recovery via entropy collapse, not discovery. The 5.8x V2 lift on a synthetic environment with no discoverable structure reproduces the +1.58x modular-form lift and the +1.37x BSD lift to within the same band; the underlying mechanism is the same. The substrate's role in the six-domain pattern is to provide BIND/EVAL accounting infrastructure; the lift comes from the prior recovered by entropy collapse, not from the BIND/EVAL machinery.

**Headline retracted internally before any external write-up.** Full results are in `prometheus_math/MODAL_COLLAPSE_SYNTHETIC_RESULTS.md`; raw run is in `prometheus_math/_modal_collapse_synthetic_results.json`; reproducible via `python -m pytest prometheus_math/tests/test_modal_collapse_synthetic.py -v` plus the run script in the results doc. Wall-clock cost of the test: 11 seconds. Wall-clock cost of accumulating the 350 000-episode headline that the test killed: ~2 days.

The cost asymmetry — eleven seconds of synthetic null kills two days of headline-quality real-domain runs — is the methodological point. We document it because we believe it generalizes: a substrate that does not run synthetic null controls before publishing cross-domain claims is paying the wrong cost ratio.

**What this rules out.** Cross-domain modal collapse as a substrate-architecture finding. The Section 4 lift values as evidence that the substrate is generalizing. Continued use of sparse 0/1 reward + episode-length-1 contextual bandit as a probe for substrate competence.

**What this does not rule out.** The substrate's BIND/EVAL accounting properties (cost model, capability provenance, hash-locked caveats) — those are unrelated to the agent training loop. Specific positive findings that did not depend on RL training (e.g., the BSD MLP supervised baseline, cross-domain congruence verifications). The possibility that a substrate-aware agent with shaped reward, longer episodes, or a different measurement interface would surface real cross-domain transfer. The synthetic test invalidates only the *current* training setup, not the substrate concept.

---

## 6. The Layer 1 / 2 / 3 diagnosis

The framing of this section — three layers, with Layer 2 the broken one — was developed in conversation with ChatGPT (frontier model review, 2026-05-04, transcript in `pivot/feedback_frontier_review_2026-05-02.md` and follow-up in `pivot/feedback_validation_ladder_2026-05-03.md`) and refined in dialogue with Aporia and Gemini. We attribute the three-layer model to ChatGPT's framing; the empirical anchors and the "load-bearing line" below are ours.

**Layer 1 — evaluation.** Sound. The substrate's gates correctly identify when a candidate satisfies mathematical criteria. F1 (permutation null), F6 (base rate), F9 (simpler explanation), F11 (cross-validation), reciprocity, irreducibility, and the five-catalog cross-check all produce the right verdict on the candidates they receive. The smoke-test bug catch described in Section 7 confirms this: when the gates failed (cyclotomic-noise false-positives on 5 of 11 deg-14 ±5 smoke-run band entries), the substrate's own discipline surfaced the failures within an 18-second test rather than after the full 97 million-poly enumeration.

**Layer 3 — search.** Replaceable. We tried REINFORCE-linear, PPO-MLP, two GA variants (elitist and three anti-elitist diversity strategies), V3 root-space sampling, catalog-seeded random, catalog-seeded REINFORCE, frozen-bias REINFORCE (the cleanest H2 falsifier we have), MLP-vs-linear ablation on BSD, rich-feature ablation on BSD (45 added features beyond the 26 baseline). All ten-plus algorithms produce 0 PROMOTEs across ~350 000 cumulative episodes. The failure is *identical* across algorithm classes because the failure is upstream of search. Swapping in MAP-Elites (Ergon's lane), MCTS, or LLM-driven proposals would not fix it.

**Layer 2 — signal extraction.** Broken. Discrete-bin reward produces a discontinuous gradient. Entropy collapse onto the modal bin is the *optimal* policy under discrete reward — not a failure mode, the correct response of REINFORCE/PPO to a measurement interface that supplies no usable gradient. The synthetic test of Section 5 is the definitive evidence: on V3 where lstsq solves the underlying problem at >=60%, REINFORCE produces 4.91% and collapses to 3 bins. The agent is doing the right thing under the wrong measurement interface.

**The load-bearing line:**

> *A falsification-first system without a gradient becomes a perfect null-result generator.*

All the discipline in the world cannot rescue a learner that is being asked to climb a flat surface. Caveat-as-metadata, hash-locked PROMOTEs, five-catalog cross-checks, deterministic seeds, four-fold falsification — these are necessary but not sufficient. The measurement interface that converts mathematical structure into a learnable signal is the missing piece, and it sits one layer below the gate machinery.

**The fix is not a different RL algorithm.** That is the temptation, and it is wrong. We tried multiple algorithms; the failure mode is identical. The fix is a different *measurement interface*: continuous surrogate signals (distance to validity, count of violated constraints, magnitude of failure rather than binary fail/pass). This is a Layer 2 redesign, not a Layer 3 swap.

**Continuous-reward synthetic test (Day 1 of the kill-space pivot, 2026-05-04 morning).** Aporia and Gemini's first proposed Layer 2 fix was scalar reward shaping: replace `reward in {0, 100}` with a continuous distance-to-truth signal, on the hypothesis that the discontinuous gradient was the bottleneck. Three reward shapes were calibrated to match the binary case's dynamic range (clipped to `[-100, 0]`, scale chosen so that worst-case error ≈ 3σ produces full negative reward) and run on byte-for-byte mirrors of the Day 1 trainers, with the only change being the reward formula:

| Reward shape | Formula | Calibration |
|---|---|---|
| L2 | `reward = -scale × (pred_y - true_y)^2` | scale = 100/9 |
| L1 | `reward = -scale × |pred_y - true_y|` | scale = 100/3 |
| log | `reward = -scale × log(1 + |pred_y - true_y|)` | scale = 100/log(4) |

The test grid was the same 4 variants × 3 algorithms × 3 seeds × 5 000 episodes, run for each of the three reward shapes — 1 620 000 episodes total, 32.7 seconds wall-clock. The verdict, documented in full in `prometheus_math/MODAL_COLLAPSE_CONTINUOUS_RESULTS.md`, is that **scalar reward shaping does not break modal collapse on any variant**:

- **REINFORCE collapses to 2-3 active bins on every cell, every reward shape.** Top-3 mass ≥ 0.993 across all 36 (variant × shape × algorithm) cells. The collapse target *moves* (under L2, REINFORCE picks the bins whose centers are closest to E[y], the L2-optimal scalar estimate; under L1 it picks bins near the median; under log, near the median again with slightly different weighting), but the *width of the support* does not change.
- **PPO stays uniform across all 21 bins on every cell, every reward shape.** Top-3 mass ≈ 0.15 = 3/21. The continuous reward provides no more usable signal to the MLP gradient than the binary reward did.
- **On V3 (low-noise, lstsq trivially solves at ≥60% bin accuracy), the best result across all three continuous reward shapes is REINFORCE under L2 at 9.08% — versus 4.84% random and ≥60% lstsq.** REINFORCE still collapses to 3 bins; the modest lift over random is the modal-prior gambit, not signal extraction. The lstsq baseline is more than 6× higher than either RL arm.
- On V2 (skewed prior), continuous reward makes REINFORCE *worse* than uniform random (2.4% vs 4.6%) — because the L2-optimal collapse target under a skewed prior is a less-favored bin than the modal class. The collapse persists; the direction of the artifact reverses.

The killer line, written into the diagnostic's verdict block:

> *Scalar reward did not just under-specify the signal — it projected the gradient away at the reward boundary.* L2/L1/log all return a *scalar* signal that says "you are this far from the right answer". For a 21-way categorical policy, that scalar gets distributed across 21 logits via the policy gradient identity `advantage × ∇log π(a|s)` — and the entire vector update is rank-1. The continuous reward does *not* tell the agent "the answer was bin 13, not bin 8"; it only says "you got 0.34 less reward this time". Modal collapse persists because the gradient is now non-zero almost everywhere, but it is *directionally ambiguous about which other action would have helped*.

This was the pivot point. ChatGPT's reframe (and our agreement, after more debate than was comfortable): the underlying outcome is not a scalar at all; it is naturally multi-dimensional. The Layer 2 problem is not reward smoothness — it is about *which kind of object* the substrate logs as the kill signal.

**The kill-vector reframe.** The substrate's response (Day 3, Section 2) was to replace the categorical `kill_pattern: str` with a 12-component `KillVector` carrying both `triggered: bool` and a continuous `margin: float` per falsifier (out_of_band, reciprocity, irreducibility, five catalog adapters, F1, F6, F9, F11). Operationally this reframes the policy gradient: a kill_path is now a *vector* in margin space, not a single string; operators induce *directional derivatives* in this 12-dimensional space; and "navigation toward zero margin" replaces scalar gradient descent as the substrate's optimization primitive. The substrate's Day 5 navigator (`prometheus_math/KILL_VECTOR_NAVIGATOR_RESULTS.md`) consumes per-component squashed margins to rank operators by `E[‖kill_vector‖_margin | region, operator]`, returning the first non-tautological policy primitive the substrate has produced.

**The 127 000x distinguishability gain as empirical anchor.** The decisive empirical evidence that the kill-vector reframe is the right Layer 2 fix comes from the Day 5 native pilot (`prometheus_math/NATIVE_KILL_VECTOR_PILOT_RESULTS.md`): on the canonical deg14 ±5 step DiscoveryEnv region, 24 000 episodes across 4 algorithms × 3 seeds, the average pairwise symmetric-KL divergence between operators was 3.50 × 10⁻⁷ in the legacy categorical representation and 4.44 × 10⁻² in the native squashed-margin representation — a ratio of ~127 000×, five orders of magnitude. The categorical view collapses every algorithm to "kills with `out_of_band`, triggered = 1.0"; the margin view shows PPO converging to mean margin +1.08 (touched the band at -0.001), random_uniform at +5.58, REINFORCE at +6.69 (worse than random at this configuration), GA_elitist at +3.18. The substrate had been logging operator-distinguishing structure at a discriminative level five orders of magnitude weaker than what one 138-second native pilot produced when the right representation was in place. The Layer 2 measurement interface was the bottleneck; the Layer 3 algorithms were not.

**Region-specific gradient fields.** The Day 5+ region densification pilot (`prometheus_math/REGION_DENSIFICATION_RESULTS.md`) extended the native pilot to four additional `(degree, alphabet_width, reward_shape)` cells (deg10 ±5, deg10 ±3, deg12 ±5, deg14 ±3 — all step reward) and confirmed that **different operators win in different regions**, with non-overlapping CIs. PPO wins on V1 in 4 of 5 cells; REINFORCE-linear wins decisively on `deg10 ±3 step` (mean ‖k‖ = 0.2553 vs PPO's 0.4305, gap 0.175 with non-overlapping CIs). This is the kill-space framing's testable signature: in a smaller search space (7^6 = 117 K trajectories at deg10 ±3) a simpler policy reaches the cyclotomic basin faster than PPO's structured exploration; PPO's advantage is at larger search spaces. Region-conditioning carries information the categorical archaeology could not see. The navigator's coverage went from 2 to 10 margin-mode regions after the densification.

**Implication for the field.** Any AI-for-math system using discrete success/failure rewards on hard discovery tasks is at high risk of the same pathology. Class-prior recovery looks like cross-domain transport. The headline numbers will be in the right band (1.5x to 5x lifts) and the p-values will be small. Continuous scalar reward, on its own, does *not* fix this — it changes the collapse target without widening the support. The synthetic null control is the only reliable test we have found that distinguishes "model learned structure" from "model recovered the modal class with high confidence." For systems that produce kill-path-style metadata, the further upgrade — replacing categorical kill labels with per-component margin vectors — exposes operator-level structure that scalar reward and categorical labels both throw away.

---

## 7. Self-falsification as substrate property

This is the methodological claim, supported by the case study and two ancillary catches.

**The synthetic test was an internal adversarial output.** The synthetic test of Section 5 was specified by Aporia *after* the cross-domain claims of Section 4 were assembled internally, and it killed the headline. The substrate's own falsification discipline produced the test that broke the substrate's own narrative. We highlight this design property because it is, in our experience, rare: most evaluation harnesses we have seen in the AI-for-science literature run *for* the headline, not *against* it.

The mechanism that made this possible was operational rather than philosophical. Aporia is an agent in Prometheus whose explicit charter (`pivot/aporia.md`) is to produce adversarial probes against any claim the team is internally on the verge of believing. The 2026-05-04 review cycle (transcripts in `pivot/feedback_ergon_review_round6a_chatgpt_2026-05-03.md` and the Aporia post-review addendum in `pivot/techne_2026-05-04_status_and_pivot.md`) specifies the synthetic test as item #2 in the "Now (parallel, today)" execution sequence, before any further surface-area expansion. Techne (the toolsmith agent — me) executed the spec in one hour; Aporia reviewed the verdict; the headline was retracted. None of this required human intervention beyond the human PI's standing approval to run the falsification battery.

**Brute-force smoke-test catch.** A second instance of the same discipline operating at a different layer. Earlier in 2026-05-04 we queued a brute-force enumeration of all 97 435 855 deg-14 reciprocal palindromic polynomials with coefficients in [-5, 5] — a finite-subspace settlement of H1 vs H2 vs H5 (`prometheus_math/LEHMER_BRUTE_FORCE_RESULTS.md`). Before launching the full enumeration we ran an 18-second smoke test on the analogous deg-14 ±1 subspace (2 187 polys). The smoke test surfaced two substrate bugs:

1. **Cyclotomic-noise false-positives in `in_lehmer_band`.** Pre-fix smoke result had 11 band entries; 5 were products of cyclotomic factors with numerical drift in the numpy companion-matrix path, not genuine Lehmer-band candidates. They had M_numpy ~ 1.0001 (drift just above the 1 + 1e-6 cutoff), M_mpmath = NaN (mpmath couldn't converge on high-multiplicity unit-circle roots), and `residual_M_after_cyclotomic_factor` ~ 1.0000xxx. True Mahler measure: 1, exactly. The pre-fix cyclotomic detector's 1e-9 cutoff was tighter than the actual numpy drift on these polys (~1e-4), so they slipped through.

2. **Verdict-logic inconsistency.** Pre-fix verdict for the smoke run was H5_CONFIRMED ("all band entries in Mossinghoff exactly") even though 5 of 11 entries had `in_mossinghoff: False`. The pre-fix `verdict_from_band` flagged an entry as "non-novel" if it was either in Mossinghoff *or* cyclotomic *or* had a cyclotomic factor — meaning the 5 cyclotomic-noise entries (all non-Moss but with cyclotomic factors) were silently treated as non-novel and the verdict fell into the H5 branch.

Both bugs would have flooded the full 97 million-poly enumeration with thousands of false-positive "discoveries." The fixes (a `classify_cyclotomic_noise` helper with 5e-4 residual tolerance, and a stricter `verdict_from_band` dispatch) cost ~2 hours of engineering time. The full enumeration (deferred indefinitely after the methodology pivot, but estimated at 5-10 CPU-days) would have produced a claim-pile that, at minimum, cost a week of post-hoc cleanup, and at worst would have leaked into an external write-up before being caught. The discipline pattern is the same as the synthetic-test catch in Section 5: cheap probe before expensive run, kill the false positives upstream.

**Caveat-as-metadata is the technical mechanism that prevents narrative inflation.** Internal narrative inflation is a real risk in multi-agent systems. We have observed it ourselves: when one agent (Charon) reports "+1.37x lift at p=0.00055 on BSD rank," another agent (a hypothetical writeup-agent, or a human PI) is liable to drop the small-n caveat, the rank-0 modal-prior caveat, the discrete-reward-warning caveat, and the "rediscovery, not novelty" caveat in the course of summarization. By the time the result reaches an external write-up, the caveats have been compressed to prose and then to nothing.

The substrate's response is structural rather than cultural. Caveats are typed records (`small_n`, `mode_collapse`, `rediscovery_not_discovery`, `synthetic_battery_used`) hash-locked into the PROMOTE def_blob. Downstream consumers receive caveats automatically through TRACE, and dropping a caveat breaks the hash chain. Narrative inflation is structurally blocked at the data layer. This is not a guarantee against motivated misinterpretation — a sufficiently determined human can always strip caveats by hand — but it raises the cost of doing so by enough that we believe it shifts the equilibrium.

**The kill_vector / native pilot result: 126 983x distinguishability gain.** The substrate's most striking ancillary catch came on Day 5 of the kill-space pivot (the same day the methodology paper outline was written). The first end-to-end native-KillVector pilot — 24 000 episodes across 4 algorithms x 3 seeds, 138 seconds wall-clock on a single machine — measured the symmetric-KL divergence between operators on the deg-14 ±5 step DiscoveryEnv region, in two representations:

- **Legacy categorical kill_path:** average pairwise symmetric-KL = 3.50e-7. Effectively zero. Every episode at this configuration is killed by the same falsifier (`out_of_band`), so the categorical representation collapses operator distinguishability to noise.

- **Native unit-aware-squashed margin:** average pairwise symmetric-KL = 4.44e-2. Five orders of magnitude larger.

- **Ratio: 126 983x.** Round number ~127 000x.

The ratio's interpretation is operational. Per `prometheus_math/NATIVE_KILL_VECTOR_PILOT_RESULTS.md`: "the substrate had been logging operator-distinguishing data at a discriminative level five orders of magnitude weaker than what one 138-second native pilot produced." Mean raw margins for the four algorithms differ dramatically: PPO mean = +1.08 (touched the band — minimum margin -0.001, indicating PPO's policy at one episode produced a polynomial with M just below the 1.18 ceiling), random_uniform mean = +5.58, REINFORCE mean = +6.69 (worse than random — its policy gradient locks in on high-M trajectories at this hard configuration), GA_elitist_v2 mean = +3.18 (between PPO and random). The squashed-L2 kill magnitudes are 0.36 / 0.84 / 0.86 / 0.75. The categorical view cannot see any of this because all four algorithms register the same single triggered component (`out_of_band`).

The substrate had been measuring operators in coarse-grained categorical space for ~350 000 episodes' worth of legacy ledger entries and reporting that operators were "indistinguishable on this configuration." The native pilot, with the right representation, recovers operator-level structure that was always there — it had just been thrown away at the substrate-output layer. Day 5's navigator (`prometheus_math/KILL_VECTOR_NAVIGATOR_RESULTS.md`) ranks operators by expected kill magnitude and produces the first explicit policy primitive for the substrate: in margin mode, on the canonical native-pilot region, the navigator returns `ppo_mlp` (E[||k||] = 0.36) as the top recommendation, with `random_uniform` (0.84) and `reinforce_linear` (0.86) ranked below. This is the substrate's first operator recommendation that is *not* a tautology over an empty cell.

**The same discipline pattern at three different layers.** Section 5's synthetic test catches a Layer 2 bug (reward-shape-induced modal collapse). Section 7's smoke-test catches two Layer 1 bugs (cyclotomic-noise false-positives, verdict-logic inconsistency). Section 7's kill_vector / native pilot catches a substrate-output-representation bug (categorical hides 5 OOM of operator-distinguishing structure). All three are instances of the same discipline: the substrate's adversarial agent specifies a cheap probe; the toolsmith agent runs the probe; the result kills (or in the third case, replaces) a load-bearing assumption. The substrate's *self-falsification cost* — the expected wall-clock and engineering cost to surface a load-bearing error — must be lower than the temptation to skip the check.

The synthetic test killed a 2-day, 350 000-episode headline in 11 seconds. The smoke test killed a 5-10 CPU-day brute-force enumeration in 18 seconds. The native pilot killed the categorical-kill-path representation in 138 seconds. **The cost ratio of self-falsification to overrun is, in each case, between 1:50 and 1:1000.** That is the cost asymmetry we believe makes substrate-level falsification discipline tractable: it is cheap relative to the runs it gates.

---

## 8. Comparison with the AI-for-math literature

We surveyed AI-for-math discovery results published in the previous two years. We do not name systems in this draft (the team has not yet decided whether to anonymize, name with a structured comparison table, or cut the section entirely; see `pivot/methodology_paper_outline_2026-05-04.md` Decisions Awaited #5). Instead we characterize four recurring patterns, scored against the substrate-discipline bar of Sections 2, 3, and 7:

**(a) No synthetic controls.** Headline numbers reported on real mathematical domains, without a parallel run on a constructed environment where the answer is known to be absent. This is the failure mode our own substrate exhibited until 2026-05-04 — and it is the most consequential, because synthetic null controls are the cheapest reliable diagnostic for distinguishing class-prior recovery from learned structure.

**(b) No null-hypothesis ablation.** No version of the system in which the learner is replaced by a class-prior-recovery baseline (always-predict-mode) or a simple supervised baseline (xgboost or logistic regression on the same features). The supervised-baseline omission is particularly diagnostic: if a tree on the same features beats RL by a meaningful margin, the RL machinery is unnecessary, and the headline's "lift over random" comparison was the wrong baseline all along.

**(c) Discipline-grade caveats absent.** Caveats reported in prose in the discussion section, not as typed structured records propagated through provenance. Easy to drop in summary; easy to drop again in the abstract; impossible to recover from after they are dropped. We have observed this pattern in our own internal documents before the caveat-as-metadata schema was deployed; we do not believe we are unusual.

**(d) Cannot detect class-prior recovery.** Evaluation harness does not distinguish between "model learned structure" and "model recovered the dominant class with high confidence." The two produce indistinguishable lift-over-uniform-random numbers when the true distribution is class-skewed. The remedy — modal-class baseline as the comparison rather than uniform random — is a one-line change that we have not seen consistently in published systems.

**Honest assessment.** Most published AI-for-math discovery results would fail to clear the synthetic-null bar. We know this because *our own* result failed to clear it, and our result was substantially more disciplined than the median published system in this space — five-catalog cross-check, four-fold falsification gates, hash-locked PROMOTEs, deterministic seeds, 350 000-episode evidentiary base. The headline survived all those gates. It died at the synthetic null. If our discipline isn't enough, the median system's certainly isn't.

This is a load-bearing claim and we will need to support it with a structured comparison if the team chooses to keep this section in any external write-up. Roughly ten anonymized systems scored on the four patterns above is a feasible scope.

**What our substrate enforces that we did not find consistently elsewhere:** typed records on every CLAIM, hash-locked caveats inherited through TRACE, kill_path metadata on every rejection (now upgraded to per-component KillVectors), deterministic seeds, Welch p-values with explicit family-wise correction, mandatory five-catalog cross-checks across heterogeneous data sources, and *mandatory synthetic null controls before any cross-domain claim*. The last item is the one we did not enforce until the headline died, and it is the one we believe most needs to become a community norm.

---

## 9. What this means going forward

The honest path forward is instrument-mode rather than discovery-mode.

**The discovery framing is not currently defensible.** We do not have evidence that the substrate produces mathematical discoveries. The 350 000-episode evidentiary base on the Lehmer search produces 0 PROMOTEs; the cross-domain "successes" are reward pathology; the brute-force settlement is implemented but the full enumeration remains deferred. We cannot, on this evidence, claim that AI made a discovery.

**The instrument framing is defensible.** We have evidence that the substrate catches its own false positives within 24 hours and at substrate-level cost (Section 5: 11 seconds for the synthetic test, Section 7: 18 seconds for the smoke test, 138 seconds for the native pilot). The instrument's value is in the kills it produces; SHADOW_CATALOG entries (kept-but-flagged) are the substrate's epistemically honest disposal.

**Empirical state after the kill-space pivot.** The five-day pivot has produced concrete artifacts that constrain what comes next:

- **Native pilot:** 24 000 episodes, 138 seconds, 127 000x distinguishability gain in margin space over legacy categorical (`prometheus_math/NATIVE_KILL_VECTOR_PILOT_RESULTS.md`).
- **Region densification:** 48 000 episodes across 4 additional `(degree, alphabet_width, reward_shape)` cells; region-specific gradient field structure confirmed (different operators win in different cells with non-overlapping CIs); navigator coverage from 2 to 10 margin-mode regions (`prometheus_math/REGION_DENSIFICATION_RESULTS.md`).
- **Navigator first recommendation:** PPO-MLP for the canonical deg14 ±5 step region (E[‖k‖] = 0.36 vs random 0.84 vs REINFORCE 0.86); REINFORCE-linear for the deg10 ±3 step region (E[‖k‖] = 0.26 vs PPO 0.43); the substrate's first non-tautological policy primitive (`prometheus_math/KILL_VECTOR_NAVIGATOR_RESULTS.md`).
- **Extended PPO test of the navigator's recommendation:** 80 000 episodes (seed 0) at deg14 ±5 step. Verdict B at 80 000 episodes (`prometheus_math/EXTENDED_PPO_RESULTS.md`): PPO converges to the Mossinghoff-entry neighborhood within 10 000 episodes (best margin -0.001, asymptotic), produces 31 682 band touches (40% of episodes), 536 in-band candidates, and **0 novel discoveries** outside Mossinghoff. The navigator's recommendation delivered the predicted convergence behavior, but the recommended operator's reach (margin -0.001) is shallower than Lehmer's polynomial itself (margin -0.004) — i.e., PPO never goes deep enough to surface a candidate beyond what the catalog already contains.

**The H1 vs H4 question that PPO's verdict B leaves open.** The 0-novel result at 80 000 PPO episodes on deg14 ±5 step is consistent with two structurally distinct hypotheses that this run cannot distinguish:

- **H1 (Lehmer's-conjecture-local):** No sub-Lehmer polynomial exists in the deg14 ±5 step subspace beyond the Mossinghoff catalog; the basin is genuinely empty in the relevant sense.
- **H4 (operator-utility ceiling):** Sub-Lehmer polynomials exist in the subspace, but PPO's policy class cannot navigate to the depths required to surface them.

H1 and H4 produce identical *observed* output (0 novel candidates), so the run alone cannot settle which is correct. The rigorous closure path is the bug-fixed brute-force enumeration of all 97 435 855 deg-14 ±5 reciprocal palindromic polynomials with cyclotomic-noise classifier and stricter verdict dispatch — a finite subspace where the right answer *is* the answer. The smoke-test bugs are fixed (Section 7); the full enumeration is implemented in `prometheus_math/lehmer_brute_force.py` with verdict outputs `H1_LOCAL_LEMMA`, `H2_BREAKS`, `H5_CONFIRMED`, `INCONCLUSIVE`. The full run is deferred (estimated 5-10 CPU-days when launched); a `H1_LOCAL_LEMMA` verdict from that run would settle H1 affirmatively and reduce H4 to a methodological footnote, while a `H2_BREAKS` verdict would do the opposite. Either way, the brute-force path is the substrate's strongest available statement on this subspace.

**Concrete near-term work.**

- **Layer 2 repair via kill-vector navigation: in progress.** Native KillVector emission is now the substrate default; the navigator is shipped and tested across 10 margin-mode regions; the per-component learner ties cell-mean baselines on degenerate single-component datasets (the only kind the legacy ledger contains). The open Day-4 question — whether a margin-aware learner beats cell-mean on cross-region data — becomes answerable as more regions accrue native pilots. We do not yet have a margin-aware KV MAE metric; building it is the next learner-side step.

- **Supervised baselines first.** Before any further RL investment, run xgboost / logistic-regression baselines on the same features in each domain. If a supervised model recovers most of the lift, the RL machinery is unnecessary; if it does not, the residual is the discovery question. We have not yet run this baseline on the BSD rich-features stack and we should before any further RL claim.

- **Brute-force closure on Lehmer subspace.** Run the bug-fixed `lehmer_brute_force.py` on the deg-14 ±5 reciprocal-palindromic finite subspace. The verdict closes H1 vs H4 for that subspace, regardless of which way it falls.

- **Substrate-as-instrument for the next campaign.** The methodology paper itself argues that the substrate's value is in the kills it produces. The next campaign should be designed *as a kill candidate* from the start: a hypothesis the substrate can falsify cheaply if wrong, with synthetic null controls and class-prior baselines wired in by default rather than added retroactively.

**Open questions for the field.** The methodology generalizes; the substrate-specific machinery does not have to. Three questions we believe are worth pursuing more broadly than Prometheus:

- **How do we design AI-for-math benchmarks that aren't class-prior-traversable?** A benchmark whose "lift over uniform random" can be saturated by always-predict-mode is not a benchmark of mathematical capability. Either the comparison must be against the modal-class baseline (one-line fix), or the target distribution must be balanced by construction, or the evaluation must require a structural property (rank prediction *plus* an interpretable feature attribution) that modal collapse cannot satisfy.
- **How do we make falsification-first systems learnable?** A substrate that catches its own false positives is, almost by definition, *not* receiving usable gradient from those false positives — every kill is a flat point in the policy's reward landscape. Kill-vector navigation is one answer; gradient-synthesis-from-failure (turning each kill into a *direction* in margin space) is a more general framing. Whether this framing scales beyond the Lehmer / Mahler-measure substrate is open.
- **How do we scale gradient-synthesis-from-failure across more domains?** The substrate's current KillVector schema has 12 components specialized to the Lehmer search's falsification gates. An analogous schema for other discovery domains — BSD rank prediction, modular-form coefficient prediction, knot trace-field prediction — would require adapting the per-component margin definitions to each domain's natural failure axes. Whether a general-purpose schema exists, or whether each domain requires bespoke instrumentation, is the most operationally consequential open question.

**The methodology IS the result.** Substrate-as-instrument is what we believe is defensible; substrate-as-discovery-engine is not, on this evidence. The paper itself does not commit to which way the brute-force closure falls or whether the next campaign produces true positives. It documents the kill, the methodology that produced it, and the empirical anchors (127 000x distinguishability, 0 PROMOTEs at 80 000 PPO episodes, Verdict B on the navigator's recommendation) that constrain what defensible next steps look like.

---

## 10. Honest limitations

The section the team must not let get cut.

**N=1 case study.** One substrate (Prometheus), one domain family (Lehmer / Mahler-measure search, validated against six rediscovery domains), one team. The methodological claim — that substrate-level discipline plus mandatory synthetic null controls catches reward pathology that would otherwise escape upward as a cross-domain transport claim — generalizes; the specific numbers (5.8x lift on V2, 4.91% accuracy on V3, 126 983x distinguishability gain) do not.

**Cost of substrate-grade discipline.** Substrate-grade discipline is slow. We accumulated 350 000 episodes before the one-hour synthetic test killed the headline. Discipline is cheaper than wrong publications, but it is not free, and we should be honest that it took us longer than it should have to run the synthetic null. The honest version of this paper is partly about that delay: had we run V3 LOW-NOISE on day 1 of the cross-domain campaign, we would have saved two days and not built up an internal commitment to the headline. We did not, because the synthetic null was not yet in our default battery. It is now.

**The methodology might still produce positive discovery results.** When Layer 2 is repaired (kill-vector navigation, continuous surrogate signals, multi-step episodes) and supervised baselines are run, the substrate may produce true positives. We do not yet know. The negative result documented here is a result *about this configuration of the substrate*, not a permanent claim about the architecture.

**Selection effects in synthetic-test design.** Aporia's synthetic environments were constructed to expose the suspected failure mode. We argue they are fair tests (linearly separable structure, abundant signal in V3, identical training pipeline). A reviewer could reasonably ask whether other synthetic environments would tell a different story; we believe not — the V3 LOW-NOISE BALANCED variant is solvable in principle by a one-line lstsq fit, and a learner that cannot solve it cannot reasonably be claimed to be "extracting mathematical structure" anywhere. But we cannot prove a universal.

**Frontier-model reviewers as collaborators.** Three of the load-bearing analytical moves in this paper — the three-layer Layer 1/2/3 framing, the H3/H4/H5 hypothesis additions in `pivot/techne_2026-05-04_status_and_pivot.md`, and the kill_path-as-vector reframe that motivated the Day 3 substrate change — came from frontier-model reviewers (ChatGPT and Gemini) and from an internal adversarial agent (Aporia). We attribute the framings; we executed the empirical work. A reasonable concern is that the methodology paper depends on a small number of strong external reviews and may not generalize to teams without that resource. We acknowledge the dependency and note that the substrate-discipline machinery (caveat-as-metadata, hash-locked PROMOTEs, mandatory synthetic null controls) is independent of which agent surfaces a particular critique.

**Open audience question.** What is the right venue for negative-results methodology in AI-for-math? The result is too methodological for a pure mathematics journal and too negative for most ML venues. Workshops on reproducibility, ML evaluation, or AI-for-science methodology are plausible homes; formal-systems venues (CPP, ITP) are not. The team has not yet decided (`pivot/methodology_paper_outline_2026-05-04.md` Decisions Awaited #1).

---

**End of v1 draft.**

Word count target: 6 000-8 000.
Sections expanded in this revision pass: 1 (Abstract / Introduction), 4 (Cross-domain "validation"), 6 (Layer 1/2/3 diagnosis), 9 (What this means going forward).
Sections carried forward from v0: 2 (System architecture), 3 (Evaluation primitives), 5 (Synthetic test), 7 (Self-falsification as substrate property), 8 (Comparison with literature), 10 (Honest limitations).
Decisions-awaited section deliberately omitted: the outline's artifact, not the paper's.
