# Reasoning-Steering & the Non-Conservativity Instrument — Internal White Paper

**Date:** 2026-06-09
**Author:** Aporia (in-session, with James)
**Status:** Internal technical report. Documentation of a single multi-day working
session. Calibrated; no external-publication framing (per `feedback_exploration_not_papers`).
**Scope:** what we built, why, how (process), what we found, how we tested it, the data,
and next steps — for this work and for the wider Prometheus ecosystem.
**Code:** `aporia/experiments/reasoning_steering/` (Stage 0a + Stage 0b), 97 tests.
**Protocol docs:** `reasoning_steering_protocol_v0.2.md`, `…v0.3_relational_correction.md`,
`reasoning_quality_emit_spec_v0.1.md`. **Running log:** `reasoning_steering_progress_log.md`.

---

## Executive summary

We set out to test one of Prometheus's load-bearing hypotheses — that the difficulty of
mathematical reasoning is **not a single scalar** ("the ladder is a basis, not a scalar").
We made it falsifiable by reformulating it as a question in combinatorial Hodge theory:
*is the failure/evaluation flow over reasoning states **conservative** (reducible to a
single potential = scalar difficulty) or **non-conservative** (irreducible cyclic
structure = genuinely multi-dimensional)?*

We built a validated instrument to answer that, ran it on real mathematical data, and got
a sequence of clean, falsifiable results:

1. **A combinatorial Hodge decomposition instrument** (Stage 0a), proven on synthetic
   controls and a famous real positive (Efron's intransitive dice → 98.6% curl). 47 tests.
2. **A fundamental correction caught by building, not by argument:** the natural way to
   define the flow (`Δdamage` between states) is **conservative by construction** — a
   gradient by definition — so the original test was *vacuous*. The fix is a **relational**
   (pairwise, possibly non-transitive) flow à la HodgeRank.
3. **Two trustworthy NULLs on mathematical objects:** in-band Mahler/Lehmer polynomials
   and genus-2 curves both came up **gradient-dominated** (scalar-reducible). The genus-2
   test was *fair* (13 heterogeneous, trading-off invariants) and still NULL — math
   objects are theorem-coupled, hence scalar-reconcilable.
4. **A sharp methodological correction:** pairwise **anti-correlation does NOT predict
   non-transitivity** (genus-2 had a −0.80 correlated pair and 34 anti-correlated pairs,
   still NULL). The lever is **non-weightable cyclic disagreement**, detectable only by
   the curl itself. We built a fast curl **pre-screen** that gates expensive runs.
5. **A validated positive control:** at the exact scale where the NULLs occurred (n=30),
   planted cyclic structure is detected decisively (BEATS_NULL, p=0.005). So the NULLs are
   **true negatives**, not instrument blindness.
6. **A mechanistic law with a behavior delta:** curl **explains** "a combined reward
   scores worse than random while a single head works." When evaluators are non-weightably
   related, linear combination collapses below the best single head and below random — a
   provable reason the substrate's reward signal may need to be **vector-valued**.
7. **A precise, minimal substrate change** (`reasoning_quality_emit_spec_v0.1`): the
   reason the real reasoning test can't run yet is that the substrate computes per-head
   reasoning scores, combines them, and **persists only the combined value** — discarding
   the per-evaluator vector the instrument needs. The fix is a logging change.

The headline: we converted a philosophical claim into a falsifiable, validated
measurement, found that *mathematical objects* are scalar-reducible, and produced a
concrete, validated argument that the open question — *is reasoning quality
non-weightable?* — is now one logging change (or one inference batch) away from a real
answer.

---

## 1. Motivation — why this question, why now

Prometheus's deepest bet (`project_convergence_theory`, the "ladder as a basis") is that
reasoning is a *dynamic, multi-dimensional* process that transformers suppress into a
"sounds-good" scalar. The reasoning-steering protocol (`…v0.1`/`…v0.2`) proposed that the
failure landscape's structure could be read as a **basis** of independent reasoning
directions rather than a single difficulty scalar — and, if so, used to *steer* a model.

That claim was a metaphor until we asked: **what would make it false?** The answer turned
out to be precise. In combinatorial Hodge theory, any flow on a graph decomposes
orthogonally:

```
f  =  grad(φ)   ⊕   curl(ψ)   ⊕   harmonic(h)
      scalar         local           global
      potential      cyclic          topological
      (difficulty)   (non-transitive) (voids / H¹)
```

"Difficulty is a scalar" is *exactly* the statement that the flow is a pure gradient
(`grad(φ)` only). "The ladder is a basis" is *exactly* the statement that the flow has
non-zero curl/harmonic mass that survives null controls. The metaphor became a measurable,
falsifiable quantity: `non_gradient_mass = (‖curl‖² + ‖harmonic‖²) / ‖f‖²`.

This also connects three standing threads: the failure-landscape "voids ARE the
mathematics" doctrine (`feedback_failure_signal_vector_field`) is literally the *harmonic*
component; the ejection/convergence finding is the "sounds-good scalar attractor"; and the
tensor program is served because curl/harmonic structure is a coordinate-free invariant of
a domain.

---

## 2. Process — how we worked (and why it mattered)

The process is part of the result. Five disciplines, each of which materially changed the
outcome:

- **Test-driven, authority-anchored (math-tdd).** Every mathematical operation got
  authority/property/edge/composition tests *first*. This is what caught the most important
  finding (below): a test premise we wrote ("transitive ⇒ pure gradient") failed, exposing
  the saturation baseline; another ("flow = Δdamage") was *provably vacuous* before we spent
  a minute on the expensive run.
- **Document-as-you-go (`feedback_document_as_you_go`).** A running log + per-step commits.
  We had lost an earlier build to a network drop; nothing in this session lived only in
  chat. 50+ commits, each a checkpoint.
- **Preregistration + ratification gates.** Every load-bearing degree of freedom (the
  damage metric, the corpus, the operator set, the localization radius) was frozen in a
  written spec and ratified *before* the run, so a NULL couldn't be p-hacked into a PASS.
- **Stop-and-report on surprise.** When the build surfaced something the spec didn't
  anticipate (a 55s/score cost; a cycle-free graph; a conservative-by-construction flow),
  the loop **stopped** and brought the decision back rather than forcing through.
- **Calibrated honesty (`feedback_calibration`, `feedback_anti_gravitational_well`).** No
  "novel/publishable/literature-grade" framing. NULLs reported as wins. Every claim scoped.

The build ran largely as a self-paced TDD loop (the `/loop` mechanism): pick the next unit,
red → green → refactor → log → commit, report each cycle. Stage 0a was 7 iterations; Stage
0b several more, with three explicit stop-and-report design checkpoints.

---

## 3. What we built

### 3.1 Stage 0a — the instrument (`stage0/`, 47 tests)

A self-contained combinatorial Hodge decomposition over an edge-flow on a graph:

- **`hodge.py`** — `hodge_decompose(G, flow)` → gradient/curl/harmonic components, masses,
  `non_gradient_mass`, and the subspace ranks (curl_rank, harmonic_rank = first Betti
  number). Validated against hand computation and networkx. (Later: a dense-graph OOM in
  triangle enumeration was found at K30 and fixed with direct edge-common-neighbour
  enumeration — behaviour-preserving.)
- **`controls.py`** — four synthetic controls with *known* Hodge structure: no-cycle/no-void
  (must read ~0), planted-cycle (curl), planted-hole (harmonic), operator-artifact (the
  false-positive floor).
- **`nulls.py`** — the anti-artifact null battery: degree-preserving rewire, operator-label
  shuffle, endpoint-permutation, emitter-family-holdout, with a smoothed permutation p-value.
- **`localization.py`** — H-R2 with a preregistered "localization freeze" (fixed
  graph-distance balls r∈{1,2,3}, two-of-three-radii stability, `UNSTABLE_LOCALIZATION`
  label) — closing the neighbourhood-radius researcher degree of freedom.
- **`runner.py`** — the 0a gate: validates the instrument against all controls and emits
  `stage0_hodge_controls_report.json` (`all_passed=True`). This is the
  "instrument-proven-before-real-data" gate.

The load-bearing test is the **operator-vs-state discriminator**: planted real structure
beats the null battery; the operator-artifact floor does not. This is the guard against
"discovering our own operator menu" (the H5-OEIS artifact failure mode).

### 3.2 Stage 0b — the relational pipeline (`stage0b/`, 50 tests)

After the conservative-by-construction finding (§4.1), the flow was reformulated as a
**relational** (HodgeRank) comparison:

- **`damage.py`** — the Axis-2 battery-survival-depth scorer (the originally-ratified
  metric) + `margins_from_kill_vector` (the per-falsifier margin vector).
- **`corpus.py` / `g2c_corpus.py`** — in-band Mahler/Lehmer polynomials; genus-2 curves.
- **`flow.py`** — the relational flow:
  `flow(i,j) = Σ_k sign(margin_k(j) − margin_k(i))` over the complete comparison graph.
  The **`sign` non-linearity is essential** — it is what lets the flow be non-conservative;
  linear aggregation collapses back to a gradient.
- **`relational_nulls.py`** — the adapted null battery (falsifier-column-shuffle,
  sign-permutation, falsifier-family-holdout).
- **`prescreen.py`** — the fast curl **signal screen** (observed curl + a small null,
  ~10× cheaper than the full run) that gates expensive runs.
- **`calibration.py`** — the relational **positive control**: a planted maximal Condorcet
  cycle at scale + Efron's intransitive dice.
- **`reward_curl_demo.py`** — the path-B demonstration that curl explains
  combined-reward-below-random.
- **`runner.py`** — the H-R1 verdict runner (BEATS_NULL | NULL | INVALID), with degeneracy
  and criteria-adequacy guards.

---

## 4. Findings

### 4.1 The flow was conservative by construction (the deepest finding)

The Stage-0b emit schema defined `flow(before→after) = damage(after) − damage(before)`.
For any deterministic per-state scalar `D`, this is exactly the discrete gradient
(coboundary) of `D`: curl ≡ 0, harmonic ≡ 0, `non_gradient_mass ≡ 0` **identically**, for
any graph/operators/metric. The hypothesis was *unfalsifiable-toward-positive*. Worse, the
fixed-seed determinism we adopted for reproducibility is exactly what *guarantees* the
gradient. This was caught by building the emitter, before any compute was spent.

**The fix** (protocol v0.3): the edge measurement must be **relational** — a pairwise
comparison `g(a,b)` not reducible to `φ(b) − φ(a)`, i.e. one that can be **non-transitive**.
This is HodgeRank's founding setting; the curl of pairwise-comparison data measures its
inconsistency with any global ranking.

### 4.2 Two trustworthy NULLs on mathematical objects

- **In-band Mahler/Lehmer polynomials** (21 states, battery falsifiers as criteria):
  gradient 0.799, curl 0.201, harmonic ~0; observed curl *below* the column-shuffle null
  (0.251, p=0.818). A free diagnostic on the cache reclassified this as **corpus-limited**
  (only 3 of 8 falsifiers varied across the near-identical polynomials — homogeneous corpus,
  not a substrate statement).
- **Genus-2 curves** (30 curves, 13 heterogeneous arithmetic invariants): gradient 0.829,
  curl 0.171, harmonic 0; column-shuffle null 0.164, p=0.355. This was a **fair**,
  well-powered test (criteria-adequacy guard passed, 13 varying criteria) and still NULL.

**Interpretation (calibrated):** mathematical objects, compared across their invariants,
admit a consistent scalar ordering. A plausible deep reason: arithmetic invariants are
**coupled by theorems** (BSD ties rank/Sha/regulator), so they cannot disagree
non-transitively. This is *not* a universal refutation of H-R1 — it is a NULL on the
worst-case substrate (theorem-coupled objects) for the hypothesis.

### 4.3 Anti-correlation is not non-cyclicity (the methodological correction)

When asked "what increases P(signal)?", the intuitive answer is "decorrelate the
evaluators." We built a pre-screen on pairwise correlation — and **the data falsified the
strategy**: genus-2 had a min pairwise Spearman of **−0.80 and 34 anti-correlated pairs**,
yet was NULL. Two evaluators trading off pairwise are still **weightable** — a scalar
combination orders the states. Curl requires **cyclic, non-weightable** inconsistency
(a≻b≻c≻a) among ≥3 evaluators, which pairwise statistics cannot see. The corrected screen
measures the curl itself at low sample count; it correctly predicts both NULLs.

### 4.4 The positive control — the NULLs are true negatives

The relational pipeline had been missing a positive control at H-R1 scale. We built it:

- **Efron's intransitive dice** (famous, independent; flow from computed win-probabilities):
  curl_mass **0.986** — the instrument recovers a real non-transitive system as ~99% curl.
- **Planted maximal Condorcet cycle at n=30** (the genus-2 scale): screen PASS, H-R1
  **BEATS_NULL**, `non_gradient_mass = 1.0`, both nulls p=**0.005**.

So at the exact scale where math objects were NULL, genuine curl is detected decisively.
**The instrument fires on real curl ⇒ the NULLs are true negatives.**

### 4.5 Curl explains reward-combination failure (the behavior delta)

The substrate's own record (`feedback_no_naive_score_combination`) notes a *combined*
reward that scored *worse than random* while a single head (PRM v0) worked. We reproduced
the mechanism with the validated instrument: adding non-weightable (cyclic) heads crashes
the linear combination from 0.99 → ~0 (random) → negative, while the best single head stays
at 1.0, and the Hodge curl jumps from the 0.32 saturation floor to 0.77.

```
cyc_wt   curl   best_single  combined   (combined vs ground truth)
  0.0   0.317     0.992       0.992     combining is fine
  0.1   0.765     1.000       0.002     collapses to RANDOM
  0.25  0.765     1.000      -0.154     WORSE than random
```

This is *not* a units/scale problem (the original diagnosis) — the heads are commensurable
and combination still collapses; normalization cannot fix it. **Diagnostic:** when a
combined reward underperforms the best single head, measure the curl; high curl ⇒ heads are
non-weightable ⇒ **scalar reward combination is provably lossy ⇒ use a vector-valued reward
or the best-aligned head, do not average.**

### 4.6 The recurring data wall → the substrate-emit finding

Five times this session, a real finding lived in memory but its multi-evaluator numeric
data was **not on disk** (Mahler done; kill-ledgers thin; learner corpus categorical;
quality-dimension fields unpopulated; Walk-Z/PRM head scores never persisted). The root
cause is precise: **the substrate computes per-head scores, combines them, and persists only
the combined value.** The per-evaluator vector — the only thing the instrument can read —
is discarded at write time. This is why the *reasoning* test cannot run yet, and it is the
strongest case for the minimal emit change.

---

## 5. Testing & validation

- **97 automated tests** across Stage 0a (47) and Stage 0b (50); all green at session end.
  math-tdd discipline (authority/property/edge/composition) on every operation.
- **Instrument validation:** the 0a runner gate (`all_passed=True`) on planted controls;
  the operator-vs-state discriminator; the localization freeze rejecting a single-radius
  hole that the global decomposition accepts.
- **Positive control:** Efron dice (0.986 curl) + planted n=30 cycle (BEATS_NULL, p=0.005).
- **Negative-control faithfulness:** synthetic no-cycle/no-void reads ~0 (2.4e-31);
  operator-artifact sits at the floor and does not beat its null.
- **Self-correction record:** five TDD-caught corrections (saturation baseline; all-zero vs
  constant-flow guard; complete-graph rewire inapplicability; conservative-by-construction
  flow; anti-correlation ≠ curl) — each sharpened the protocol rather than being patched
  over.
- **Report artifacts** (committed JSON): `stage0_hodge_controls_report.json`,
  `stage0b_relational_hodge_report.json`, `stage0b_g2c_relational_report.json`,
  `stage0b_calibration_report.json`, `stage0b_reward_curl_report.json`.

---

## 6. Data

- **In-band Mahler/Lehmer polynomials** — `prometheus_math.databases.mahler.MAHLER_TABLE`
  (8625 entries; 21 in-band). Scored via the live falsifier battery
  (`DiscoveryPipeline.process_candidate`); ~55s/in-band score; reproducible (local
  catalogs, fixed seed). Cached in `stage0b_margin_cache.json`.
- **Genus-2 curves** — `cartography/lmfdb_dump/g2c_curves.json` (66,158 records, 13 numeric
  invariants); deterministic stratified sample of 30; no scoring needed (invariants read
  directly).
- **Calibration** — Efron's dice (first-principles) and a generated maximal Condorcet cycle.
- **Reward-curl** — a synthetic informative+cyclic head mixture (no external data).
- **What was absent** (the data wall): multi-head reasoning-quality scores; multi-agent
  shared-state verdicts (only 2 agents overlap, < 3 needed for non-transitivity);
  populated quality-dimension fields. None persisted.

---

## 7. Limitations & honest scope

- The two NULLs are on **mathematical objects compared via invariants**, not on **reasoning
  traces compared via independent judges**. The reasoning claim itself is *untested* — the
  data does not exist on disk.
- The relational flow uses the `sign` (Condorcet) aggregation, which carries a **saturation
  baseline**; all verdicts are therefore BEATS-NULL, never `non_gradient_mass > 0`.
- Sample sizes were modest (n=21, n=30); the positive control confirms power at n=30, but
  larger corpora would tighten the negatives.
- "Curl explains reward failure" establishes the **mechanism and a diagnostic**; it does not
  prove the substrate's *specific* historical failure was curl (that needs the unpersisted
  head data).

---

## 8. Next steps — this work

1. **Persist the per-evaluator vector** wherever ≥2 heads/judges score a reasoning candidate
   (`reasoning_quality_emit_spec_v0.1`). A logging change, not a modelling change. This is
   the single highest-leverage move; it unblocks everything below.
2. **Run H-R1 on real reasoning data** (arm A: independent model judges over *contested*
   candidates; or arm D: the actual heads), gated by the fast screen. The first genuine test
   of whether reasoning quality is non-weightable.
3. **The harmonic probe (path C).** We only ever measured *curl* on *complete* graphs. The
   **harmonic** component (global topological holes = the "voids") only appears on **sparse**
   (k-NN) comparison graphs. No-inference, existing data, unexplored — a direct test of the
   "voids ARE the mathematics" doctrine.
4. **The scalarity spectrum (path D).** `gradient_mass` is a number characterising a domain
   (g2c = 83% scalar). Sweep domains (knots, OEIS, lattices, modular forms) and rank them by
   non-scalarity — a map of which territories are genuinely multi-dimensional.

---

## 9. Next steps — the ecosystem

The instrument is general: it answers "does this reduce to a scalar, or is there irreducible
multi-dimensional structure?" for any *states × evaluators*. That has ecosystem-wide reach:

- **Reward modelling / RLVF (Ergon, Noesis, Rhea).** The clearest behavior delta: the
  curl→combination-failure law says scalar reward over non-weightable heads is provably
  lossy. The ecosystem should (a) persist per-head vectors, (b) run the curl screen whenever
  a combined reward underperforms a single head, (c) adopt vector-valued / multi-objective
  reward where curl is high. This is a concrete, validated argument against naive reward
  blending across the whole training stack.
- **Cross-agent evaluation (Charon, Erebos/Pollux/Stygian).** When ≥3 agents evaluate shared
  claims, the curl of their disagreement is a first-class signal: high curl means the claim's
  "quality" is genuinely multi-dimensional and no single verdict suffices — exactly the
  agent-differentiation thesis (`feedback_agent_differentiation`) made measurable.
- **The failure landscape (Aporia doctrine).** The harmonic component *is* the "voids ARE the
  mathematics" object. Folding the Hodge instrument into the failure-signal pipeline gives
  the substrate a native operator: decompose any failure-flow into scalar / cyclic /
  topological parts, and treat the harmonic (void) structure as navigable coordinates.
- **The tensor program (`feedback_tensors_near_and_dear`).** Curl/harmonic masses and ranks
  are coordinate-free invariants of a domain — natural fibres of the unified signature-keyed
  tensor. The "scalarity spectrum" is a tensor slice.
- **Arachne (the crawler swarm).** The relational/HodgeRank machinery is precisely what an
  Arachne "failure crawler" needs: crawl → emit typed+provenanced edge-flow → decompose →
  surface curl (non-transitive structure) and harmonic (voids). The instrument is the missing
  analysis layer for the fabric. (`agents/arachne/crawler.py` now exists on disk.)
- **The convergence thesis.** If the reasoning test (step 2) ever returns BEATS_NULL, it is
  direct measured evidence that reasoning quality is non-scalar — the "ladder is a basis"
  claim with a number on it, and a concrete argument that single-scalar reward/verification
  is structurally insufficient for reasoning.

**The one-sentence ecosystem takeaway:** we now have a cheap, validated test for *"is this
signal genuinely multi-dimensional, or are we compressing it into a lossy scalar?"* — and
that question recurs everywhere the substrate scores, rewards, ranks, or verifies.

---

## Appendix A — commit map (selected, this session, on `main`)

- `a90cb4d6` protocol v0.2 (Hodge scalar-collapse falsifier)
- `a5619bac … e532d37a` Stage 0a iters 1–7 (instrument, 47 tests, gate PROVEN)
- `c2623df5 / 72765050` Stage 0b emit-schema freeze (draft → ratified)
- `dca44d22 / e4f2155d` Stage 0b iter-1 scorer + performance stop-and-report
- `89925644` corpus design checkpoint (cycle-free graph)
- `eaf95864` FUNDAMENTAL: flow = Δ(node scalar) is conservative by construction
- `6eef2b83` protocol v0.3 relational correction
- `d6c625ce / 3d17220b / 4d09c5d2` Stage 0b relational pipeline (margin/corpus/flow/nulls/runner)
- `bfa29ee9` Mahler H-R1 NULL; `b020ac9c` reclassified corpus-limited
- `34446a19 / e57f1fb1 / 2fdeea1f` genus-2 loader + OOM fix + fair NULL
- `f37ef5d4` signal pre-screen + anti-correlation correction
- `cf9f8685 / c61944f1` calibration positive control PASSES
- `e0ceb839` path B: curl explains combined-reward failure
- `bef3fdfa` reasoning-quality emit spec v0.1

## Appendix B — file & artifact map

Code: `aporia/experiments/reasoning_steering/{stage0,stage0b}/` (12 modules, 97 tests).
Docs: `aporia/docs/reasoning_steering_protocol_v0.{1,2,3}*.md`,
`reasoning_quality_emit_spec_v0.1.md`, `reasoning_steering_progress_log.md`, this paper.
Reports: `stage0b/stage0b_*_report.json`, `stage0_hodge_controls_report.json`,
`stage0b_margin_cache.json`.
Memories banked: `feedback_flow_conservative_by_construction`,
`feedback_anticorrelation_is_not_noncyclicity`, `feedback_document_as_you_go`; updated
`feedback_no_naive_score_combination`.

— Aporia, 2026-06-09
