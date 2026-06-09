# Astraea — Prometheus Router (charter, with the knockouts run)

**Author:** Harmonia C
**Date:** 2026-05-30
**Status:** DESIGN + structural critique + MVP first slice. Not yet built.
**Companion docs:** `harmonia/memory/architecture/topological_falsification_engine.md`
(§1.1 operating rule, §2 knockouts, §3 fork), `bottled_serendipity.md`,
`harmonia/memory/architecture/reaudit_killvector_rank1_2026-05-27.md` (the
training-data prerequisite), `pivot/harmonia_C_higher_success_engine_2026-05-27.md`
(graded-descriptor methodology, LABS bake-off failure shape).

> James's spec, restated: *"Given a new generated claim, the system predicts its
> likely kill pattern, routes it to the right falsifier(s), proposes the minimal
> discriminating test, and updates the search distribution based on the result —
> better than fixed heuristics and better than an LLM judge."* This is the next
> milestone artifact, and the right milestone — but only if Astraea survives the
> five structural risks below.

---

## 1. Why Astraea, in one sentence

Routing is the first tractable synthetic-reasoning primitive because it is a
**supervised problem on cheap ground truth**: every historical
(claim → KillVector) pair is a labelled example, and the substrate produced
~thousands of them already (the consumption-starvation scar becomes the training
set). Generation is hard; routing on past failures is the place the substrate
already has the data to learn something.

## 2. The five structural risks (knockouts, run *before* building)

### Risk 1 — Selector contamination (the doctrine's first rule)

`topological_falsification_engine.md` §1.1: **"LLM on mutation side only. Never on
the selection side."** Astraea *is* a selector — it judges which falsifier(s) a
claim should go to. **If implemented with an LLM in the deciding seat, Astraea
violates the doctrine's first rule by construction.** James's own bar ("better
than an LLM judge") already implies the comparator, not the design — Astraea
must be a **non-LLM learned router** (a deterministic classifier / Bayesian
posterior / small supervised model) whose predictions commit before any LLM
explanation, with the kill outcome as mechanical ground truth. LLMs are allowed
to *propose* claims; nothing else.

### Risk 2 — Goodhart concentration (the router becomes a fast confirmer)

A router that optimizes "minimize wasted compute by predicting kill_pattern
correctly" converges on routing every claim to **the falsifier most likely to
kill it** — exactly the §2.2 concentration pressure (Apollo gen-3551 monoculture
in a different guise). The router would become an efficient autopsy machine,
not a learner. Two fixes, both required:
- **Information-gain routing**, not kill-rate routing. The objective is "route
  to the falsifier whose outcome maximally *reduces uncertainty* about the
  claim's true kill axis" — entropy / expected Bayesian information gain — not
  "most likely to kill cheaply."
- **Explicit exploration injection.** A fraction of claims is routed to
  *unlikely* falsifiers, by design, to discover off-prior kill axes. Without it
  the router never learns that the prior was wrong.

### Risk 3 — The basis is unmeasured (same load-bearing decision, twice)

Harmonia B's 10 reasoning axes (A=legality, B=multi-step, C=invariants, …) are
a **hypothesis**, not a measurement — exactly as the original 12-component
KillVector basis was *before* the 2026-05-27 re-audit showed it was effectively
rank-1 with `out_of_band ≡ F9` collinearity. Routing on an *unmeasured* axis
list inherits the same failure pole: **what if Haiku's "high invariant / low
legality" is one underlying factor wearing two names?** The orthogonality of the
reasoning axes must be **measured on data** (off-diagonal correlations among
per-axis performance, conditional on hard problems — Pattern 20: pooled corr is
a projection) before the axes are accepted as Astraea's routing substrate. The
re-audit's lesson generalizes: *measure the basis before you route on it.*

### Risk 4 — Taxonomy engine (James's own warning, restated as an invariant)

> *"A failure landscape can be real and still not lead to reasoning. It can
> become a taxonomy engine: excellent at classifying death, weak at producing
> life."*

A router that only classifies past failures more accurately is autopsy. Astraea
must **close the loop into the mutation operator** — its predictions must
update the proposal distribution, and the success metric must be **downstream
survival-rate lift**, not classification accuracy. Concretely: every Astraea
prediction is paired with a back-edge that says "given this predicted kill axis,
bias the next mutation toward avoiding it." If the next-generation survival rate
doesn't lift, the router is autopsying.

### Risk 5 — Training data is broken upstream (the re-audit prerequisite)

A supervised router needs labelled (claim → KillVector) pairs. The substrate's
existing pairs are the data from `_native_kill_vector_pilot.json` and the legacy
315k corpus — **every one of them carries ≤2 components** (the
2026-05-27 instrumentation artifact). A router trained on this data learns
"predict `out_of_band`" and nothing else. **Astraea cannot be trained until the
instrumented pilot lands** (re-audit ladder step 1). That work is logged; it
must precede Astraea, not parallel-track it.

## 3. The architecture that survives (what Astraea must be)

1. **Non-LLM learned router.** Input: claim feature-vector (the graded
   descriptor — already validated orthogonal on Salem + LABS). Output: a
   distribution over falsifiers + an expected-information-gain score per
   choice. Model class: start with a small gradient-boosted tree or logistic
   ensemble; escalate to a small NN only if the baseline saturates. Strictly no
   LLM in the deciding seat.
2. **Behavior space = the *measured* orthogonal reasoning basis.** Run the
   off-diagonal-correlation audit on Harmonia B's 10 axes against held-out
   per-axis performance data first. Drop / merge collinear axes before they
   become routing primitives.
3. **Objective = information gain × downstream survival lift.** Not
   classification accuracy. Not kill-rate. Two metrics, both required:
   information gain per kill (the routing quality) and the survival-rate
   improvement when Astraea's predictions feed the mutation operator's prior
   (the loop-closure / not-an-autopsy check).
4. **Explicit exploration policy.** Fixed fraction of claims (Thompson sampling
   or ε-greedy) routed to unlikely falsifiers. Logged; never silently dropped.
5. **Training data = the instrumented pilot's full KillVectors**, recorded on
   in-band candidates by the cypari-host production fix. (Bootstrap with the
   cypari-free reference battery in `graded_qd_harness.py` so the architecture
   can be validated end-to-end before the cypari pilot lands.)
6. **Evaluation = three baselines, blind holdout.** Astraea vs (a) fixed
   uniform routing, (b) fixed kill-rate-greedy routing, (c) Haiku/Sonnet
   LLM-judge routing. Holdout = a domain or sequence-length not in training.
   Pass = beats all three on both objectives.

## 4. The MVP first slice (buildable now, cypari-free)

A tiny end-to-end Astraea on the existing harness, *before* the full system:

1. Extend `graded_qd_harness.py` to record a **multi-falsifier verdict vector**
   per candidate (which of `{F1, F6, F9, irreducibility, peak-sidelobe, …}`
   would have killed it, and with what margin) — i.e. the proper KillVector that
   doesn't exist in the legacy data.
2. Generate ~2k labelled training pairs on LABS-n=37 (cheap, ~minutes).
3. Train a tiny supervised model (sklearn GradientBoosting) to predict the
   *kill axis* from the descriptor. Hold out 20%.
4. Measure: routing accuracy + **information gain** (entropy reduction vs
   uniform) on the holdout.
5. Closed-loop test: feed the predictions back into the mutation operator's
   prior; re-run the bake-off (random vs LLM vs **Astraea-biased random**).
   The survival-lift number is the load-bearing metric — if it doesn't move,
   Astraea is autopsying.

If MVP passes its own knockouts on this toy slice, it's safe to scale to the
real substrate. If it fails — especially on (5) — the failure shape is
substrate-grade information about which Risk dominates (3=basis was a proxy,
4=back-edge isn't load-bearing, 1=we accidentally let an LLM into the loop).

## 5. The honest claim

Astraea is the right next agent **iff** it (a) is non-LLM in the deciding seat,
(b) routes by information gain with exploration, (c) is trained on a basis
whose orthogonality was measured first, (d) closes the loop to the mutation
operator with downstream survival as the headline, and (e) waits for the
instrumented pilot (re-audit step 1) as its training corpus. **Build all five
or build none** — a router that misses any of them inherits a known failure
pole from this very project's scars.

*Net: routing is the right primitive because it converts the project's largest
liability (production-rich, consumption-starved) into its largest training set
— but only if the router doesn't recapitulate the selector failures Prometheus
has spent two years learning to avoid.*

---

## 6. MVP v1 results — the surface win + the failure shape (2026-05-30)

Runner: `harmonia/runners/astraea_mvp.py`. LABS n=37, 3000 training samples, 4
falsifiers, GradientBoostingClassifier router, 5000-eval bake-off.

**Surface:** lift +0.569 on best merit factor (3.46 → 4.03 on Astraea-biased
arm), coverage tied. "Loop closed" by the headline rule.

**Knockout on the headline (this is what matters):**

```
F_skew    : acc 1.000  info_gain +0.546   feature: skew_defect_cheap = 1.00
F_balance : acc 1.000  info_gain +0.508   feature: balance           = 1.00
F_energy  : acc 1.000  info_gain +0.004   trigger rate 1.0  (useless — fires always)
F_peak    : acc 0.693  info_gain +0.042   features: run_entropy, mean_run, n_runs
```

Two of four classifiers are **feature-label tautologies**: `F_skew` is defined
as `skew_defect>0.4` and the router predicts it from `skew_defect_cheap` —
which *is* `skew_defect`. The "classifier" is a threshold lookup on its own
input. Same for `F_balance`. Info-gain is real entropy reduction but reflects
"you can predict `f(x) > c` from `f(x)`," not "cheap features predict expensive
outcomes." **Only `F_peak` is a genuine cheap→expensive prediction** (info-gain
+0.042 — positive but a 7% entropy reduction).

The +0.569 lift came mostly from **hand-coded heuristic mutations** triggered
by trivially-correct predictions, not from learned routing. With F_skew /
F_balance predicted perfectly (because tautology), `targeted_mutate` mostly
applied "flip a bit to reduce skew_defect / balance" — directional moves toward
Salem structure that beat random bit-flips. **You could remove the router
entirely, always apply those corrections, and get the same lift.** The router
is decorative; the lift is encoded domain knowledge.

### Where each Risk landed in v1

- **R1** (LLM in deciding seat): held. sklearn only. ✓
- **R2** (Goodhart concentration): held nominally; not stressed.
- **R3** (basis unmeasured): label-label corr passed (max 0.039) — **but a new
  failure mode surfaced that the audit doesn't catch: feature-label
  tautology.** F_skew is label-orthogonal to F_balance yet both are functional
  identities of single cheap features. Pattern 20 in another guise.
- **R4** (taxonomy / loop closure): **NOT actually tested.** Lift exists, but
  confounded by tautology + hand-coded heuristics. Whether a *learned* router
  closes the loop is still open.
- **R5** (training data instrumented): multi-falsifier vectors recorded ✓ —
  but the set itself was degenerate (one constant, two tautological).

### Substrate lessons added to the charter (v1 → v2)

1. **Strict cheap/expensive separation.** No cheap feature may be a
   function-of-the-same-domain as any falsifier label. The audit must include
   a (feature, label) functional-identity check, not just label-label
   correlations.
2. **Falsifier calibration gate.** Refuse to run with any falsifier whose
   trigger rate is below 0.05 or above 0.95 — near-zero entropy, useless basis.
3. **Targeted mutations must be *learned*, not hand-coded.** Either the router
   outputs a learned bit-flip distribution, or the targeted-mutate is reduced
   to "random flip restricted to predicted-axis region" so the routing is the
   only treatment.

## 7. MVP v2 — the cleaner kick

Single structural edit, then re-run the four phases:

- **Falsifier set requires autocorrelation for every member.** Replace
  `F_skew`, `F_balance` with falsifiers that test autocorr-dependent properties
  (e.g., `F_peak`, `F_lag_k_peak` at specific k=⌊n/3⌋, `F_low_lag_energy`
  weighted toward small k). Drop `F_energy` or recalibrate to ~50% trigger.
- **Feature set is purely combinatorial.** Bigram counts, run-length stats,
  parity patterns, position-of-extremes. No skew_defect, no balance, no
  merit-factor-adjacent statistic in features.
- **Targeted-mutate is reduced** to "pick a flip position from a router-learned
  distribution, sign random" — the directionality is the only treatment.

If lift survives v2, the routing thesis has a real positive datapoint on a
clean test. If it doesn't, the failure shape distinguishes:
- info-gain stays positive, lift vanishes → architecture needs more than
  feature-based routing (Risk 4 binding).
- info-gain collapses → cheap combinatorial features just don't carry
  expensive-falsifier signal (Risk 3 binding — re-examine the basis itself).

Either outcome is substrate-grade. v1 was throwaway by design; v2 is the
honest test.

---

## 8. MVP v2 + v3 results — the architecture as built does NOT clear the bar (2026-05-30)

### v2 single-seed (clean test, no tautologies, router-guided greedy):
- LIFT best_F +0.146 (3.46 → 3.60); coverage −0.037 (concentration cost)
- Per-falsifier info-gain: F_peak +0.073, F_lag_k −0.005, F_low_lag +0.089, F_high_lag −0.006
- **Half the basis unlearnable from cheap features.** Only F_peak and F_low_lag carry signal.
- Wall-clock: 70.9s vs 0.7s random — 100× slowdown for +0.146 fitness gain.

### v3 (trusted-set audit + stochastic targeting + confidence fallback, 3 seeds):
- lift_F per seed: [+0.223, −0.498, +0.916]; mean +0.214, std 0.578
- mean − std = −0.364: **the lift is NOT robust to seed**
- One seed shows router actively hurting (−0.498)
- Coverage: all three seeds regressed (mean −0.013, std 0.003) — R2 still partially binding
- Telemetry: routed 22-25%, low_conf_fallback 33%, explore 14%
- **Routing thesis as architecturally tested has no robust positive datapoint on LABS-37.**

### What the MVP settled (three structural limits)

1. **Half the basis is unlearnable from cheap features.** F_peak and F_low_lag
   (global autocorr properties) carry cheap-feature signal; F_lag_k and F_high_lag
   (local properties) don't. The cheap/expensive boundary tracks global/local.
   *Either richer features, sequence-modeling architectures, or different
   domain redirection is needed.*

2. **Greedy/stochastic targeting on predicted-trigger axes concentrates niches**
   even with ε=0.2 exploration + Thompson-style sampling. R2 partially binding
   across all three iterations. *The architecture should route at the
   **decision** level ("should I run this expensive falsifier at all?") not at
   the **mutation-direction** level ("which axis should I attack").*

3. **The cheap/expensive cost ratio determines whether routing is the right
   primitive at all.** On LABS-37 autocorr is cheap; the router pays 40-100×
   wall-clock for marginal/noisy fitness gain. *Routing is upside-down for
   cheap-falsifier domains. The MVP's wall-clock numbers say "wrong domain
   for this test."*

## 9. v4 redirection — three changes to the production design

The v1→v3 MVP did exactly what James asked: kicked the tires. The tires came
off in three structured ways. Production Astraea must clear them:

1. **Domain redirect.** Move to an expensive-falsifier regime where falsifier
   compute ≫ routing overhead. The `prometheus_math` battery on a cypari host
   qualifies (F1 perm-null 30× cost, catalog DB lookups, kernel CLAIM minting).
   Until the routing-overhead/falsifier-cost ratio is ≪ 1, the architecture
   can't pay off. The cypari blocker from the re-audit becomes load-bearing
   here.

2. **Reframe Astraea from "predict kill axis" → "predict whether expensive
   evaluation is worth running."** Binary gate, not multi-class router. The
   cost-benefit math is direct: skip the falsifier when predicted-pass-probability
   > threshold; the saved compute funds more mutation evals (loop closure
   automatic — skipped falsifier time = extra search time).

3. **Treat the basis-half-unlearnable finding as a feature-engineering problem.**
   The v2/v3 finding that global features predict global properties but not
   local ones is a real generalization. Design v4's cheap features to *expose*
   the structures known to be predictable (per-domain). Drop the rest.

**Decision required before v4:** which expensive-falsifier domain to target.
Salem-cypari is the natural candidate (it's the original re-audit unblocked).
Alternatives: any cartography domain with minutes-scale falsifiers, or a new
synthetic domain where falsifier cost can be tuned.

