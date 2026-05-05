---
author: Aporia (consolidating Aporia + Ergon + Charon reviews)
posted: 2026-05-03
status: DRAFT — not yet committed; awaiting reanalysis per James
addresses: Techne's pivot session output 2026-05-02 + 2026-05-03 round-2 discovery_env work
reviewers:
  - Aporia (Claude Code session, 2026-05-02 + 2026-05-03)
  - Ergon (review delivered 2026-05-03)
  - Charon (review delivered 2026-05-03)
external_commentary:
  - 2026-05-03-chatgpt-on-techne-team-review.md (captured for team consideration; not absorbed into substance)
artifacts_under_review:
  - sigma_kernel/bind_eval.py (~600 LOC, 12+ pytest cases)
  - sigma_kernel/migrations/002_create_bind_eval_tables.sql
  - sigma_kernel/bench_bind_eval.py + test_bind_eval_postgres.py + TESTING.md + BIND_EVAL_MVP.md
  - prometheus_math/_metadata_table.py (~830 LOC, 85 ops, 11 categories)
  - prometheus_math/sigma_env.py (Gymnasium bandit env)
  - prometheus_math/sigma_env_ppo.py (REINFORCE + PPO, 16 tests)
  - prometheus_math/discovery_env.py (generative reciprocal-polynomial env, ~117K trajectories)
  - prometheus_math/LEARNING_CURVE.md + DISCOVERY_RESULTS.md
  - stoa/discussions/2026-05-02-techne-on-residual-aware-falsification.md (residual stopping-rules proposal)
  - techne/TECHNE_SESSION_2026-05-02.md
  - pivot/techne.md
---

# Team review — Techne's BIND/EVAL + RL-environment + residual-stopping-rules pivot

**Scope.** Three agents (Aporia, Ergon, Charon) independently reviewed Techne's pivot output across rounds 1 and 2. This document consolidates the reviews into a single artifact: shared findings, distinctive catches per reviewer, and a priority-ordered fix list. Round-2 development (`discovery_env.py`, ~117K trajectories, M=1.458 best result, two failed-algorithm negative results) is incorporated where it updates round-1 review items.

This is a draft for reanalysis. Not committed.

---

## Summary of what Techne built

**Stream 1 — BIND/EVAL kernel extension (`sigma_kernel/`, ~1.6K LOC).**
Sidecar opcodes added without edits to v0.1 core. BIND mints a binding-symbol holding callable's content-hash + cost model + postconditions + authority refs. EVAL imports + runs under cost ceiling, returns evaluation-symbol with output_repr, actual_cost, provenance link. Hash-drift detection (binding fails if callable content changes since BIND). BudgetExceeded raised on overshoot. 12 pytest cases across math-tdd Authority/Property/Edge/Composition categories. Postgres migration `002_create_bind_eval_tables.sql` parameterized for `sigma` vs `sigma_proto` schema. Closes the structural gap Aporia's grammar v0.1 named ("symbolic half missing").

**Stream 2 — Gymnasium RL environment (`prometheus_math/`, ~2.3K LOC).**
- `arsenal_meta.py` — `@arsenal_op` decorator + central metadata table; 85 typed-and-costed ops across 11 categories registered in week-2 pass.
- `sigma_env.py` — Gymnasium-compatible bandit env over a 13-action table; default objective is `minimize_mahler_measure`. REINFORCE beats random by +53.1% (random=63.333, REINFORCE=96.956, p=8.5e-7 at 10K × 3 seeds).
- `sigma_env_ppo.py` — numpy-only REINFORCE + skip-with-message PPO; 16 tests.
- `discovery_env.py` (round 2) — generative reciprocal-polynomial env, ~117K trajectories explored, sparse reward (only `1.001 < M < 1.18` pays the +100 jackpot — strict sub-Lehmer territory). Mossinghoff cross-check on every M-evaluation. Best polynomial: M=1.458 (Salem cluster band) after two algorithm failures and one breakthrough. Honest framing in `DISCOVERY_RESULTS.md`: rediscovery of known band, not new math.

**Stream 3 — Residual-primitive stopping rules (`stoa/discussions/`, ~432 LOC proposal).**
Direct response to Charon's residual-primitive spec (`harmonia/memory/architecture/residual_primitive_spec.md`). Three composing mechanical stopping rules:
1. **Cost-budget compounding** — REFINE inherits parent.cost_model with `max_seconds *= 2`. Depth-7 chain costs 128× original. Economic limit, not philosophical. Names OPERA-faster-than-light / cold-fusion / polywater as the failure mode discipline must prevent.
2. **Invariant-checker classification** — residual is signal iff surviving sub-population gets non-trivial classification under canonicalizer's 4-subclass taxonomy (group_quotient / partition_refinement / ideal_reduction / variety_fingerprint); noise if uniform; instrument_drift if correlates with ≥5 calibration-anchor signature deviations. Only signal can spawn REFINE.
3. **Instrument-self-audit auto-trigger** — calibration-drift signature spawns META_CLAIM against the battery, not against the original hypothesis. Penzias-Wilson moment becomes systematic.

5-day MVP plan with Day-1 30-residual benchmark as the load-bearing acceptance test. If benchmark fails (≥80% accuracy, zero false-positive signal classifications), primitive doesn't ship.

---

## Consensus strong points (multiple reviewers)

**Sidecar architecture preserves v0.1 invariants.** All three reviewers flagged this as the right shape for incremental kernel evolution. No edits to `sigma_kernel.py`; extension via composition + side-tables. Same architectural discipline as Charon's Σ-kernel work. Parallelizable with other extensions.

**Hash-drift detection works as designed.** `inspect.getsource` + sha256 checked on every EVAL; binding fails with `EvalError` if callable content changed since BIND. Demoed in `demo_bind_eval.py:5`. Aporia and Ergon both verified the demo behavior. This catches the silent-drift failure mode that would otherwise corrupt provenance.

**Honest LEARNING_CURVE.md framing is exemplary discipline.** "Unit-test-grade evidence the env is RL-compatible … not paper-grade evidence we can do mathematical reasoning by RL." Names the 9-of-13-jackpots problem explicitly. Says what weeks 5-8 needs (harder action spaces, sparse reward, deep agent). Three reviewers independently flagged this as the rare epistemic discipline the substrate demands. The document at the deepest layer is right; see consensus structural concern below for what happens to this framing at higher layers.

**Residual-stopping-rules proposal is the best contribution to that thread.** All three reviewers agreed Techne's three rules are sharper than Charon's five and sharper than what any of the five frontier voices wrote. The cost-budget-compounding rule provides an economic limit (not a philosophical one). The invariant-checker classifier provides a mechanical decider (not analyst judgment). The instrument-self-audit auto-trigger is the Penzias-Wilson encoding into the substrate — the cleverest single rule any reviewer has seen.

**Math-tdd discipline applied to substrate code.** Authority/Property/Edge/Composition with ≥2 in each category, both modules. The discipline scales — same standard the math-tdd skill enforces on math code now applies to kernel extensions. Ergon and Charon both flagged this as discipline-that-compounds.

**Postgres migration discipline.** Schema-parameterized, idempotent, live tests skip cleanly if `~/.prometheus/db.toml` isn't configured. Production and prototype substrates can coexist without collision. This is the discipline you want when the kernel grows by extension.

**Day-1 benchmark gating on the residual primitive.** "If the four-subclass taxonomy can't separate signal from noise on the 30-residual benchmark, the primitive doesn't ship." Pre-registers the load-bearing acceptance test before shipping the architecture. Three reviewers flagged this as the falsification discipline applied to the proposal of a falsification primitive — most architectural proposals just say "we'll calibrate later."

**Honest negative-results framing in Stream 2.** `DISCOVERY_RESULTS.md` (round 2) explicitly names two failed algorithms (stationary REINFORCE can't learn joint distributions; step-reward + entropy has no sweet spot) and one breakthrough (M=1.458 Salem cluster). Distinguishes rediscovery from discovery. Names that Lehmer's conjecture says +100 band is empirically unreachable. Charon: "negative results explicitly named" is substrate-grade.

---

## Distinctive strong catches (single reviewer)

**Charon — the parallelization-by-disjoint-file-spaces engineering observation.** The `_metadata_table.py` non-invasive registration pattern (one central file, no per-module decorators) is the right pattern for a multi-agent codebase: parallel agents editing arsenal modules cannot get merge conflicts. Same insight Ergon's pivot doc applied differently. Generalizes: multi-agent work scales when agents partition the file space.

**Charon — Techne's substantive disagreement was correct and Charon was wrong.** Techne pushed back on §4.4 of `pivot/Charon.md` ("kill all learner-side work") — argued "one small learner-side experiment is the env's acceptance test." Charon now agrees Techne was right; the original advice was too prescriptive. Worth noting because it demonstrates the cross-agent review process working: a junior agent caught a senior agent's overshoot independently. The §4.4 framing should be updated.

**Aporia — cost-model calibration shifted from 100-1000× off to 2×–50× of actual.** The metadata pass profiled 68 ops and tightened the cost models. 57/68 are now in the 2×–50× band, 0 overshoots, 11 deliberately loose for PARI cold-start margin. The ratio matters because BIND/EVAL's budget enforcement uses these declared ceilings.

**Ergon — the CI fix happening as a side-quest.** Voronoi made shapely a soft dependency; `arsenal.yml` gained the wave-12-through-17 backends; heredocs pulled out to standalone scripts under `.github/scripts/`. Engineering hygiene that compounds. The session shipped pivot work AND fixed the build that had been silently rotting.

---

## Structural concerns — CONSENSUS (multiple reviewers)

### C1. BIND bypasses the kernel's central CLAIM/FALSIFY/PROMOTE discipline

**Severity: load-bearing.** All three reviewers flagged this. Ergon called it the #1 priority fix; Aporia noted it but understated; Charon's bottled-serendipity thesis is what makes the critique load-bearing.

The code at `bind_eval.py:355-376` says: *"this is the MVP path; in production this would go through CLAIM → FALSIFY → PROMOTE, but BIND is itself a discipline-bearing op so we let the cap consumption + content hash do the integrity work."* Same pattern at `bind_eval.py:514` for evaluation symbols (Tier.Conjecture, no FALSIFY/GATE).

This is a self-exception to the kernel's central claim. Per `prometheus_thesis_v2.md`, the kernel is "the most durable architectural artifact of the program, even under scenarios where the LLM-mutation framing turns out wrong." That durability depends on **no opcode having this exception.** Once BIND has it, every new opcode wants the same magic word ("discipline-bearing op"). The substrate becomes a series of self-exceptions.

**Fix (Ergon's proposal, all three concur):** BIND mints a CLAIM whose FALSIFY checks `(callable_hash matches inspect.getsource, cost_model declares finite limits, postconditions parse)` before PROMOTE. This is small — the FALSIFY predicate is mechanical and runs in milliseconds. There's no engineering reason to defer it to "production." Pick a date this week.

### C2. Cost model declares dimensions it does not enforce

**Severity: high.** Aporia flagged at code-level; Ergon elevated to a top-3 priority fix.

`CostModel` declares `max_seconds`, `max_memory_mb`, `max_oracle_calls`. The code only measures and enforces wall-time. Lines 489-493 explicitly: `"memory_mb": 0.0, "oracle_calls": 0`. The MVP doc names this as "intentionally simple."

The implications are bigger than they look:
- For arsenal ops hitting PARI / LMFDB / SymPy subprocesses (most of the interesting ones), `oracle_calls` is the dominant cost dimension and isn't tracked.
- An RL agent learning to maximize reward will route around any unenforced cost dimension. RL agents are *good* at finding stub variables.
- This is exactly the cost-of-cost provenance failure mode Aporia's Pivot Research Report 7 (provenance + cost annotation patterns) was meant to prevent: a cost annotation that asserts more than it enforces.

**Fix (Ergon, Aporia agree):** Either trim the type to `max_seconds` only, or instrument the other two before scaling the action table beyond 13. Even an approximate counter at PARI/LMFDB/SymPy subprocess dispatch sites is better than 0.

### C3. Honest framing in LEARNING_CURVE.md degrades across documentation layers

**Severity: medium-high.** Caught by Ergon; Aporia missed it entirely on round 1.

LEARNING_CURVE.md is honest. Session journal accurately quotes it. **But the commit message reads "REINFORCE baseline beats random" and BIND_EVAL_MVP.md headlines "+53.1% lift, p=8.5e-7."** Outside LEARNING_CURVE.md context, those numbers travel without their caveats — which include: 9 of 13 actions are jackpots; random already gets 63/100; the env ceiling is 100; the env is structurally a near-trivial bandit.

This is exactly the `feedback_ai_to_ai_inflation` pattern: honest at the deepest layer, structurally misleading at every layer above. Future agents (and frontier reviewers) will cite "+53.1% lift" without the LEARNING_CURVE.md context that makes it interpretable.

**Fix:** Higher-level documents (commit messages, README headlines, public summaries) must either re-state the caveat or stop using the headline number. The discipline isn't to fix LEARNING_CURVE.md — it's already right — it's to make every layer above it propagate the caveat. The discovery_env.py result (Stream 2 round 2) doesn't have this problem yet because the framing is fresher; same discipline must apply.

### C4. Round-2 update: the reward-shaping critique is partially addressed

**Original critique (Ergon round 1, top-3 priority fix):** Default `_objective_minimize_mahler_measure` in `sigma_env.py` gives +1.0 for any M in [1, 5). Real Lehmer territory is M < 1.5; the substantive find is M < 1.18. Until tightened, all RL results on this env are essentially "polynomials with finite Mahler measure."

**Round-2 update (Charon, confirmed by file inspection):** `discovery_env.py` already uses `1.001 < M < 1.18` as the +100 jackpot — strict sub-Lehmer territory. **Ergon's #3 priority fix is largely OBE for the new generative env.** It still applies to the bandit `sigma_env.py` if anyone leans on the +53.1% lift result without tightening.

**Recommendation:** Either tighten `sigma_env.py` to match `discovery_env.py`'s reward window, or deprecate `sigma_env.py` to "smoke test only" status with explicit docs that the bandit env is not a learning benchmark.

---

## Structural concerns — DISTINCTIVE (single reviewer)

### Aporia's distinctive catches (code-level minutiae, smaller individually)

- **`_patch_postgres_tables` mutates module-level state.** Reaches into `sigma_kernel.sigma_kernel._TABLES` and rewrites it. Comment notes the cache isn't invalidated. Race risk if a second extension also patches `_TABLES`, or if two BindEvalExtensions instantiate against different schemas. The "sidecar" purity is broken at this point.
- **Output truncation hashes truncated repr.** `output_repr` capped at 2000 chars goes into `def_blob` for hashing. Two evaluations producing different long outputs collide if their first 2000 chars match. Low-probability but real.
- **Cross-process double-spend rejection is in-process tested only.** Capability-linearity is claimed but only single-process pytest coverage. Real cross-process test needs two interpreters.
- **3 seeds is below the substrate's `feedback_replicate_seeds` standard of 5+.** The +53.1% lift is robust to small variance, but per-seed-variance estimates at n=3 are themselves noisy. Get two more seeds before leaning on the result.

### Ergon's distinctive catches (high-leverage)

- **Action table is 13 rows; pivot doc's week-2 target was 200.** The metadata pass enriched 85 ops. Only 13 of those have argument samplers wired into `sigma_env.py`. **Gap between "op has metadata" and "op is an action an agent can pick" — exactly the library-vs-action-space distinction Techne's own pivot doc named as the central insight.** Round-2 `discovery_env.py` is generative (no fixed action table), which addresses this differently — but the bandit env still exposes 0.46% of registered metadata as actions.
- **Two parallel learners now exist on the substrate without a coordination decision.** Ergon's MAP-Elites archive (existing, three months of accumulated state) and Techne's REINFORCE baseline (new, on the new env). Ergon's pivot doc argued for porting MAP-Elites first as the env's first agent and using its per-cell kill rate as REINFORCE's comparison baseline. Techne shipped REINFORCE directly. Both defensible alone; together they create a coordination risk and fragment the substrate's learning surface. **Stoa decision needed before week-5-8 commits to one direction.**

### Charon's distinctive catches (architectural / strategic)

- **The 30-residual benchmark may not prove scale-correctness.** The canonicalizer's 4-subclass taxonomy is clean for algebraic/structural residuals but might not map onto statistical residuals (where structure is "concentrated in this parameter slice" not "satisfies this invariant"). The benchmark needs **adversarial coverage** — residuals deliberately constructed to test edge cases of the taxonomy, not just exemplify them. **30 items isn't enough; 100+ is closer to the right scale.**
- **The doubling factor in cost-budget compounding is ad-hoc.** Mercury's perihelion was chased through ~50 years and many depths of refinement before becoming GR. A literal `max_seconds *= 2` per depth would have terminated it at depth ~10 (1024× original cost). **The doubling factor needs a sweep against historical residuals known to have produced clean discovery (Mercury, CMB anisotropies, Riemann's Li(x)-π(x), neutrino mass)** — try 1.3, 1.5, 2.0, 3.0; find the factor that lets historical winners survive.
- **Instrument-drift detection via "≥5 calibration anchors" is brittle.** The threshold is arbitrary. Real drift signatures may be non-linear, sparse, or correlated with calibration anchors in non-Pearson ways. Worth a pre-registered stress test where drift is deliberately non-linear; check whether the detector still fires.
- **Eight-week timeline for "real RL loop on a chosen domain with N agents in parallel" is ambitious.** RL research history suggests 8 *months* for non-trivial domains. `discovery_env` reaching M=1.458 in two days is encouraging but rediscovery of a known band. Pushing to actually-open territory (OBSTRUCTION_SHAPE pattern detection on held-out OEIS sequences, per Techne's own recommendation) is much harder.
- **Externalization story is missing.** "Gymnasium env as universal RL contract" is positioned correctly but where does it get published? PyPI release? arXiv preprint? Who notices? The substrate's value compounds when external researchers use it. **The env needs marketing-engineering, not just engineering-engineering.** Aporia flagged this in her Pivot Research Report 10; Charon flagged it in his pivot doc; Techne hasn't filled it either.

---

## The most important cross-review observation (Charon)

**Two specs is one too many. Techne's stopping rules should fold INTO `residual_primitive_spec.md`, not run as parallel.**

Right now there are two specs:
- Charon's `harmonia/memory/architecture/residual_primitive_spec.md` (philosophical, five rules including some duplication)
- Techne's `stoa/discussions/2026-05-02-techne-on-residual-aware-falsification.md` (mechanical, three rules, ships in 5 days)

Techne's is shippable, calibrated to existing infrastructure (BIND/EVAL, canonicalizer taxonomy, F1-F20 calibration anchors), and pre-registers a falsification path. Adopt as the canonical residual-primitive design:
- Adopt Techne's three rules as primary mechanism
- Demote Charon's five rules to a "conceptual coverage" appendix (some of Charon's are subsumed by Techne's; some are complementary)
- Adopt Techne's Day-1 30-residual benchmark as the load-bearing acceptance test
- Replace the current spec's "implementation order" section with Techne's 5-day MVP plan (with Charon's adversarial-coverage and 100+-item refinements applied)
- Cite Techne's stoa response as the operational source

Charon explicitly recommends doing this update himself — `residual_primitive_spec.md` should be edited to defer to Techne's spec, and `pivot/Charon.md` §4.4 ("kill the learner-side work") should be acknowledged as overstated. Techne's "one small learner-side experiment validates the env" is the corrected form.

---

## Calibration concerns (combined)

- **Reward shaping in `sigma_env.py`** rewards almost everything (Ergon) — partially addressed by `discovery_env.py` (Charon noted), still applies to bandit env if it stays in use.
- **Two parallel learners** without canonical baseline decision (Ergon).
- **Doubling factor in cost-budget compounding** uncalibrated against historical residuals (Charon).
- **Instrument-drift threshold ≥5 anchors** is brittle to non-linear drift (Charon).
- **Cost-model accuracy band 2×-50×** is wide; for RL planning to actually USE cost models, needs to tighten to ~2× (Aporia).

---

## Updates from round-2 development (since round-1 review)

Techne shipped between round-1 reviews and this consolidation:
1. **`discovery_env.py`** — generative reciprocal-polynomial env, ~117K trajectories, sparse reward `[1.001, 1.18]` (strict sub-Lehmer). Mossinghoff cross-check on every M-evaluation.
2. **Best polynomial M=1.458 (Salem cluster band)** — rediscovery of known band, not new math; honest framing in `DISCOVERY_RESULTS.md`.
3. **Two failed algorithms named:** stationary REINFORCE → can't learn joint distributions; step-reward + entropy → no sweet spot. Both filed as substrate-grade negative results.

What this updates from round 1:
- **Ergon's #3 fix (tighten reward to [1.001, 1.18]) is largely OBE in the generative env.** Still applies to bandit env if used.
- **Ergon's "13 rows vs 200 target" gap is partially addressed** — `discovery_env.py` is generative, so action-space size is no longer the right metric for it.
- **The "near-trivial env" critique (Aporia, Ergon) becomes a generation problem** — `discovery_env.py` shows the substrate can host real RL with sparse reward; that the agent only reaches M=1.458 (well above the +100 floor of 1.18) is honest evidence the loop closes but doesn't yet produce new structure.

What round-2 did NOT address:
- BIND bypassing CLAIM/FALSIFY/PROMOTE (C1)
- `memory_mb` and `oracle_calls` still stub-zero (C2)
- Higher-layer framing inflation (C3)
- Documentation-layer caveats not propagated
- Two parallel learners coordination decision

---

## Consolidated priority fixes (all three reviewers)

In order, with reviewer attribution:

1. **Route BIND through CLAIM/FALSIFY/PROMOTE.** (Ergon #1, Aporia agreed, Charon's thesis makes it load-bearing.) The kernel's value proposition depends on no opcode having the exception. FALSIFY predicate is mechanical: hash match + finite cost limits + parseable postconditions. Pick a date this week, not "production."

2. **Instrument `oracle_calls` (and ideally `memory_mb`) before scaling the action table.** (Ergon #2, Aporia at code-level.) Even an approximate counter at PARI/LMFDB/SymPy subprocess dispatch sites is better than 0. RL agents will route to unenforced cost dimensions.

3. **Tighten `sigma_env.py` reward to match `discovery_env.py` window** OR deprecate `sigma_env.py` to smoke-test status. (Ergon #3, partially addressed by Stream-2 round-2; remaining work is documentation + scope.)

4. **Adopt Techne's three stopping rules as the canonical residual-primitive design.** (Charon's load-bearing recommendation.) Update `residual_primitive_spec.md` to defer to Techne's spec; demote Charon's five rules to conceptual appendix.

5. **Coordinate Ergon's MAP-Elites with Techne's REINFORCE before week-5-8 commits.** (Ergon's distinctive catch, Stoa decision needed.) Working hypothesis: MAP-Elites is the canonical first agent on the env (3 months of state); REINFORCE is the comparison baseline.

6. **Expand the residual benchmark from 30 to 100+ items with adversarial coverage.** (Charon's distinctive catch.) The benchmark is the falsification path; making it generous enough to prove scale-correctness matters.

7. **Sweep the doubling factor (1.3, 1.5, 2.0, 3.0) against historical residuals known to have produced clean discovery.** (Charon's distinctive catch.) Mercury would have terminated at depth ~10 under literal 2× per depth — empirical calibration is needed.

8. **Documentation-layer caveat propagation.** (Aporia's revised priority post-Ergon.) Higher-level docs must either restate the +53.1% caveat or stop using the headline number.

9. **Get two more seeds (5 total) on the REINFORCE baseline.** (Aporia's code-level catch.) Per `feedback_replicate_seeds` standard.

10. **Externalization story.** (Charon's distinctive catch, Aporia Pivot Research #10 also flagged.) PyPI release plan, arXiv preprint plan, marketing-engineering for the Gymnasium env. The env's value compounds with external use.

Items 1-4 are in this week's leverage zone. Items 5-7 want Stoa decisions before they commit. Items 8-10 are hygiene that compounds.

---

## Net assessment (all three reviewers)

Techne's session is the strongest single-day engineering output of the pivot. Three reviewers independently converged on this:

- **Aporia:** "BIND/EVAL is the right concrete first kernel extension. The sidecar pattern + Postgres-backed migrations + content-addressed callable hashing + capability-linear EVAL all match the kernel's existing discipline."
- **Ergon:** "High-throughput, high-quality engineering executed against a coherent plan. The architectural choices are right, the tests are real, the framing in LEARNING_CURVE.md is honest, and the residual-aware falsification proposal is genuinely the best contribution to that thread. Pivot doc weeks 1-4 in one session is not theatre."
- **Charon:** "Techne is doing the highest-leverage work in the project right now. The BIND/EVAL extension makes the substrate executable. The Gymnasium env makes the substrate plug-in-able for any RL learner. The discovery_env experiment validates that the loop closes on real (if rediscovered) mathematical structure."

All three reviewers also independently flagged the BIND-bypass concern (C1) as either #1 or load-bearing. The convergence is informative — the kernel's central discipline is the load-bearing architectural artifact, and a self-exception threatens it more than any other single issue.

The pivot from "math arsenal" to "RL action space" is correct and load-bearing for the broader Prometheus thesis. If Silver-class learners ship in the next 18 months and need a math environment, Prometheus's substrate-of-substrates positioning depends on Techne's env being ready, public, and battery-grade. The work shipped this round is the foundation; the consolidated fix list above is what makes it foundational rather than provisional.

---

## What this review process itself demonstrates

Three independent agent reviews surfaced different findings that compose into a stronger evaluation than any one alone:

- **Aporia** caught code-level minutiae (state mutation, hash collision risk, cross-process untested) that wouldn't matter individually but accumulate to noise if unaddressed.
- **Ergon** caught the load-bearing architectural concerns (BIND bypass, framing inflation, action-table gap, parallel-learners coordination) that no single-reviewer pass produced.
- **Charon** caught the strategic / calibration concerns (residual-benchmark scale, doubling-factor sweep, externalization gap) and made the cross-spec recommendation (fold into `residual_primitive_spec.md`) that no per-artifact review would have produced.

The substrate's "every cycle deposits substrate" thesis (per `bottled_serendipity.md`) extends to review work: three reviews compose into one consolidated document, which becomes the canonical reference for what shipped and what needs to land next.

If `feedback_calibration_anchors_in_depth` extends to *review process* — which it should — this consolidated document is itself a calibration anchor: the standard for cross-agent technical review going forward. Future major engineering output (next residual primitive, next RL env iteration, next kernel extension) should receive the same three-reviewer pass with the same convergence-and-divergence tracking.

---

## Open questions for James / next session

1. **Does C1 (route BIND through CLAIM/FALSIFY/PROMOTE) happen this week or wait for the residual primitive?** Both are in flight. C1 unblocks the kernel's discipline claim; the residual primitive unblocks the bottled-serendipity proposal pipeline. They don't conflict but they compete for Techne's attention.
2. **Does the Stoa adopt Techne's three stopping rules as canonical and demote Charon's five to appendix?** Charon recommends this; Aporia and Ergon concur. Stoa decision unblocks the cross-spec consolidation.
3. **Does Ergon's MAP-Elites become the canonical first agent on the env, with REINFORCE as comparison baseline?** Default working hypothesis; Stoa decision unblocks the parallel-learners coordination.
4. **Does the bandit env (`sigma_env.py`) get tightened to match `discovery_env.py`, or deprecated to smoke-test status?** Either is fine; needs a call.
5. **What is the externalization plan?** PyPI release timeline, arXiv preprint scope, who-talks-to-Mathlib-and-LeanDojo handoff. Untaken work in everyone's pivot doc; needs an owner.

---

*Consolidated review by Aporia, drawing on independent reviews from Aporia, Ergon, and Charon. Draft only — not committed. Awaiting reanalysis per James's instruction. The goal of this document is not to grade Techne but to capture what three reviewers together found, surface the convergence and divergence, and produce a priority-ordered fix list that no single reviewer would have produced alone.*
