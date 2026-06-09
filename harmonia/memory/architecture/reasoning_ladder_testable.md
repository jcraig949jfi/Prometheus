# The Testable Prometheus Reasoning Ladder

## ⚗️ EXPERIMENTAL — reasoning-side KillVector basis

> **Design by James Craig (2026-05-27)**, captured and operationalized by Harmonia_M2_B. This is the
> reasoning-landscape analogue of the math kill-space: it makes the R0–R12 ladder *empirical* by defining
> each tier through behavioral probes and a structured failure artifact, not prose.
>
> **Companions:** [`tool_genome_meta_evolution_spec.md`](tool_genome_meta_evolution_spec.md) §5.5 (the
> empirical-ladder move), [`topological_falsification_engine.md`](topological_falsification_engine.md)
> (doctrine), [`reasoning_tool_candidates.md`](reasoning_tool_candidates.md) #27 (reasoning-side basis).

## The core move

> Stop defining tiers by how sophisticated the explanation *sounds*. Define them by what the system can
> reliably do **under perturbation, failure, transfer, and adversarial pressure**, and by the **failure
> artifact** it emits.

Operational rung definition: **`capability = operation + perturbation + failure_mode + evidence_artifact`.**
A system is at tier R_k only if it passes tier-specific probes under surface perturbation, adversarial
variation, and transfer, *while producing the expected reasoning artifact*. "Harder problem ≠ higher tier."

## The tiers (operation · kill test · evidence artifact)

| Tier | Operation | Kill test | Evidence artifact |
|---|---|---|---|
| R0 | answer recall / pattern match | isomorphic rewrite (same structure, new surface) | survives-isomorphism flag |
| R1 | local rule application | swap domain assumptions (ℤ/ℚ/ℝ/ℂ/𝔽_p) | applied rule + legality unchecked |
| R2 | constraint tracking | op usually safe but here invalid (square, ÷, log, reciprocal) | domain-constraints-detected; extraneous rejected |
| R3 | multi-step composition | change one subcondition so the plan almost works | subgoal plan + verification |
| R4 | representation shift | "solve it a second way, avoiding the first" | ≥2 representations + equivalence |
| R5 | invariant detection | similar problem where the obvious invariant is insufficient | conserved quantity named |
| R6 | counterexample / falsification | true & false conjectures mixed | counterexample ledger; boundary cases |
| R7 | proof repair | locate exact failing step; weakest fix | failing-step id + corrected theorem |
| R8 | strategy selection | tempting-but-inefficient method available | strategy justification |
| R9 | lemma invention | proof-dependency graph | invented lemma + load-bearing flag |
| R10 | analogy / transfer | near-analogy where one assumption fails | role mapping table |
| R11 | meta-reasoning / uncertainty | claim with a long misleading streak (e.g. n²+n+41) | calibration state {solved/probable/under-constrained} |
| R12 | generative conjecture / research | small universe (graphs ≤8, sequences, curves) | failed conjectures that carve the space |

## The 4-version benchmark design

For each probe, build four versions: **(1) clean**, **(2) isomorphic** (same structure, new surface),
**(3) adversarial** (a tempting invalid shortcut), **(4) transfer** (same reasoning, another domain).
Score robustness across all four — a single clean pass is not evidence of the tier.

## The Reasoning Trace Vector (= the reasoning-side KillVector)

Every attempt emits a structured record, never a single scalar. Failures become structured training
material. Example fields: `problem_id, claim_type, tier_probe, answer_correct, domain_constraints_detected,
operations_used, invalid_operations_attempted, counterexamples_tested, lemma_invented, lemma_load_bearing,
representation_shifts, proof_gap_locations, transfer_attempted, confidence_calibration, kill_pattern,
failure_type, repair_available, minimal_counterexample`.

## The central falsifiable claim

The ladder is testable iff: *a system is at tier R_k only if it passes the tier-k probes under
perturbation + adversarial + transfer AND emits the tier-k artifact.* "Sounds like R8" is replaced by
"selected among strategies, justified it, avoided the inferior method, and transferred it."

## Suites to build (each emits kill vectors)

constraint-tracking · invariant-discovery · counterexample · proof-repair · representation-shift ·
lemma-invention · analogy-transfer · conjecture-generation. The ladder becomes a falsification battery
for reasoning behaviors, not a taxonomy of intelligence.

## Falsifier critiques (Harmonia, before building)

1. **Ladder vs basis (ordering not assumed).** Presented as ordered R0→R12, but "harder ≠ higher" and the
   orthogonal operation-suites suggest several tiers are *orthogonal axes*, not rungs (R4 vs R5, R8 vs R9).
   Treat it as a **basis first**; promote a pair to a ladder edge only where the **rung-reality test**
   (are adjacent tiers' failure-gradient distributions distinguishable AND ordered?) measures a
   prerequisite relation. Don't impose order — measure it.
2. **Upper tiers re-import the LLM judge (doctrine C9).** R0–R6 have deterministic graders
   (isomorphism-survival, extraneous-root rejection, counterexample-found). R8/R9/R11/R12 risk collapsing
   to "sounds like R8" if an LLM scores them. Each needs a non-LLM artifact extractor: lemma-load-bearing
   = proof-dependency-graph (wants a verifier, e.g. Lean); info-gain = counterexamples-per-test;
   calibration = Brier vs ground truth. **Lower tiers buildable offline now; upper tiers wait on a verifier.**
3. **Goodhart on a frozen probe set (extremal/adversarial).** A fixed battery gets trained-to. Requires
   **procedural generation** of isomorphic/adversarial variants + held-out families. Algebra/number-theory
   probes generate programmatically — tractable.

## Build status

- **Reasoning Phase 0** (`harmonia/experiments/reasoning_phase0.py`): procedural R0–R3 + R6 probe
  generators, capability-capped baseline reasoners, deterministic trace-vector emitter. Measures
  (a) reasoner×tier calibration staircase, (b) per-cell dominant failure shape, (c) effective
  dimensionality + cross-tier distinguishability (the rung-reality test). Offline.
- **Hardened + extended (2026-05-29):** R0 variable-rename artifact fixed (variable-agnostic solve);
  R1/R3 trace signatures thickened; **R5 (invariant/parity) and R7 (proof-repair) tiers added** with
  deterministic ground truth. 7-tier run: clean staircase R0→R3, R5/R7 floor at 0.00 for all baselines
  (the frontier above the algebra reasoners), reasoning kill-space effective dim **5.36 / 11 fields**.
- **Verifier lens shipped** (`harmonia/experiments/verifier_lens.py` + `test_verifier_lens.py`, 19 tests):
  deterministic, non-LLM selector — `verify(probe, claimed) → {valid, checks, kill_pattern}`, fails
  closed, verifies by substitution/eval (catches `extraneous_root_admitted`, `missed_root`,
  `bogus_counterexample`, `excluded_value_missed`). Cross-validated 0 disagreements with the harness
  grader on R0–R3 and reproduces the careful/procedural split. Returns `valid=None` for true universals
  (no rubber-stamp). This is the incorruptible selection side (doctrine: LLM on mutation only).
- **Still needs a real backend:** z3/cvc5 (decidable arithmetic) and Lean/Coq (inductive universals like
  "n²+n even") are NOT installed — universals are honestly reported unverifiable, not guessed. Upper tiers
  R8–R12 await this.
- **LLM reasoner + first real plateau (2026-05-29)** (`reasoners_llm.py` + `run_llm_plateau.py`,
  `_llm_plateau_run_20260529.txt`): NVIDIA Nemotron-120B (Groq cheap-head was 429-throttled), 100 calls,
  ~38 min. Per-tier acc: **R0 1.00, R1 1.00, R2 0.30, R3 0.50, R6 1.00.** **Plateau = R2**
  (constraint-tracking / extraneous-root rejection) — the model squares `sqrt(x+a)=x-b` and keeps
  domain-violating roots (`extraneous_root_not_rejected`, the SAME shape the `procedural` baseline shows
  and the verifier lens independently certifies). **KEY FINDING: the ladder is a BASIS, not an ordered
  ladder** — R3 and R6 *recover above* the R2 trough (non-monotonic), so the "tiers" behave as orthogonal
  capability axes for this model. Empirical support for ladder-vs-basis critique #1; triangulates with the
  R2/R3 signature overlap and the R5/R7 floor. Trace-vector eff-dim 3.65/8.
  **CONFOUNDS (honest):** 24% JSON parse failures on the forced Nemotron path entangle parse-misses with
  reasoning-misses; result is a 120B model not the intended cheap head; n=5/(tier,version) small.
  Next: JSON-mode/retry to disentangle, pin a cheap reliable model, re-grade in the verifier-lens
  selection seat, extend to R5/R7.
- **Opus 4.8 clean run (2026-05-29)** (`run_opus_plateau.py`, Anthropic SDK + STRUCTURED OUTPUTS, 72
  calls, **0 parse failures**, ~$0.72): R0=1.00 R1=0.83 R2=0.83 R3=1.00 R5=1.00 R6=1.00 — **no plateau
  on the lower ladder.** The Nemotron R2=0.30 plateau was a weak-model + 24%-parse-failure artifact;
  with a frontier model + API-enforced JSON it's 0.83 (the 4 residual failures are `missed_root` /
  `extraneous_root`). **Two findings:** (1) the **R0–R6 suite is SATURATED** against a frontier model —
  it no longer discriminates, the failure landscape there is near-empty, and signal has moved to R7–R12
  (which need the verifier backend for non-LLM grading); (2) **ladder-vs-basis non-monotonicity is a
  frontier-RELATIVE property** — visible when a model operates near its capability edge (Nemotron's
  R3/R6 recovered above its R2 trough), flat when the model is well above the suite (Opus 4.8). The
  suite's discriminating power is relative to the model's frontier. **Verifier-lens cross-check
  (deterministic, no LLM): 55 agree / 0 disagree**, independently flagged the 4 failures as `missed_root`
  and declined 5 true universals as `unverifiable_universal`. Caching wrote 30705 tok / read 0 → no
  benefit at this prompt size; drop the breakpoint. Structured outputs eliminated the parse-failure
  class (24% → 0).
- **3-model comparison (2026-05-29)** (`run_model_comparison.py` + z3-extended verifier, R0–R7,
  identical probes, n=8/tier, **0 failures / 168 calls**, ~$0.93). Model × tier accuracy:
  ```
  model        R0   R1   R2   R3   R5   R6   R7    plateau
  opus-4-8    1.0  1.0 0.75 1.0  0.50 1.0  1.0    none<0.5
  sonnet-4-6  1.0  1.0  1.0  1.0  1.0  1.0  1.0    none<0.5
  haiku-4-5   1.0  1.0  0.0  1.0  1.0  1.0 0.38    R2
  ```
  **Findings:** (1) **Haiku is the only model that plateaus inside the suite — at R2** (constraint
  tracking: 0/8, squares the sqrt-equation and keeps extraneous roots every time) and also fails **R7**
  proof-repair (0.38). (2) **R2 is the sharpest discriminator:** clean capability gradient Haiku 0.0 →
  Opus 0.75 → Sonnet 1.0. (3) **Neither Opus nor Sonnet plateaus on R0–R7** → suite still too easy for
  frontier models; their real plateau needs R8–R12 / novel problems. (4) **Surprising inversion: Opus
  4.8 < Sonnet 4.6 on R2 (0.75 vs 1.0) and R5 (0.50 vs 1.0)** — but n=8/tier is small; this is within
  noise and needs a higher-N confirmation before it's a claim, not a conclusion. (5) **Verifier
  cross-check (z3+sympy, no LLM): 39 agree / 0 disagree for ALL THREE models** — measurement sound.
  Sonnet's trace eff-dim is low (1.80) precisely because it had zero failures (degenerate kill-space);
  Opus 4.15, Haiku 3.60.
- **PROMOTED FINDING — "Strength is not ladder-monotone" (capability ≠ control), Experiment A
  2026-05-29** (`run_inversion_exp.py` + `morphology.py`, n=40/tier, Opus 4.8 vs Sonnet 4.6, R2+R5,
  0 failures, verifier 40/0). The n=8 inversion **confirmed and widened**: Sonnet 1.00/1.00 (R2/R5);
  Opus **0.82 / 0.85**. The morphology is the artifact, and it differs:
  - **R2:** Opus fails by **`over_refuses` (7/40 — drops valid roots)**, NOT `keeps_extraneous`. Worst
    under the explicit legality-scaffold phrasing (ph0 0.71) and best under the plain phrasing (ph2 0.92)
    → the "discard extraneous" instruction makes Opus **over-prune** (over-literal instruction-following,
    a documented Opus-4.x trait, surfacing as a reasoning failure). Sonnet 40/40, scaffold-invariant.
  - **R5:** Opus fails by **`invariant_app_failure` (5/40 — names the right invariant, mis-applies it)**;
    Sonnet 0.
  - **Mechanism:** Opus has the machinery (right invariant; knows the domain check) but worse LOCAL
    EXECUTION CONTROL; scaffolding amplifies rather than fixes. This confirms "basis not ladder" on the
    Opus<Sonnet axis (now stands on Haiku AND this). **Scope:** one model-pair, two probe-families
    (sqrt, mutilated-chessboard) — existence proof + mechanism, not a universal law. **Informs R8–R12:**
    build traps that separate *intelligence* from *reasoning-state control* (e.g. a tempting over-general
    lemma; a minimal-edit proof repair that conflicts with a literal reading).
- **R8 lemma-selection result — finding REFINED (2026-05-29, `run_r8.py`, n=30, 0 failures):**
  Opus 4.8 **1.00**, Sonnet 4.6 0.87, Haiku 4.5 0.90. The R2/R5 inversion does **not** generalize to
  lemma *selection* — it flips (Opus best), and the over-reach hypothesis is unsupported (Opus 0 errors
  → 0 over-general-trap grabs). The failure-to-generalize is the signal: aligning the morphologies —
  R5 Opus *named* the right invariant (recognition ✓) but *mis-applied* it (execution ✗); R2 Opus *knew*
  the domain check (recognition ✓) but *over-pruned* (execution ✗); R8 pure selection/recognition → Opus
  flawless. So **Opus 4.8's non-monotonic deficit vs Sonnet is in EXECUTION/APPLICATION discipline, not
  recognition/selection** — "capability ≠ control" tightens to "recognition intact; execution control is
  the gap." Caveat: n=30, one 4-problem lemma family; Haiku's 3 errors are `no_lemma_selected` (format).
  **Sharp next test:** an *application-isolation* probe (give the correct invariant/lemma, ask only to
  apply it) — Opus<Sonnet there would confirm the execution-control hypothesis directly; cleaner than
  R9 invention (which mixes recognition + invention + application).
