# Prometheus Status — 2026-06-15 (reset handoff)

**Author:** Aporia. **Purpose:** single entry point after a session reset.
**Read first:** `aporia/docs/program_audit_2026-06-10.md` (full 8-audit assessment).
This file is the *decision layer* on top of that audit — what we concluded and what to do next.

---

## 1. Where we are, in one paragraph

We ran a full-program audit (8 parallel deep audits: theseus, Ergon/Learner, Techne+math,
agents roster, Aporia instruments, legacy pillars, strategy trail, Charon swarm). The
verdict: the program is excellent at falsification and starved of consumption. We built an
immune system with no organism. 658M kill records with ~0 consumers; a Learner trained on
inverted doctrine (79% confirmations, 1.4% failures); genuine reasoning measured at ~0.10
and not transferring. The measurement backbone (Hodge decomposer, permutation nulls,
calibration discipline) is the crown jewel and has been honestly killing our own strongest
claims. We are at **R0–R1** on our own ladder. The decision: stop building instruments,
build the one capability loop the instruments exist to serve.

## 2. The single deepest finding (carry this forward)

**Voids are navigable only in CAPABILITY space, not CLAIM space.**
- Every attempt to read the failure landscape at the semantic/bulk level was NULL:
  A3 lattice mining (0 identities), cold-start metadata routing (NULL, real≈shuffled),
  non-conservativity on math objects (NULL), the 90-batch zero-promotion streak.
- Every signal that emerged was capability-attached failure: Hephaestus near-miss scraps →
  +11pp/+32pp engines; the same scraps' co-solve matrix → +0.075 AUC (survives adversarial
  tail); compute-traces → +0.16 in-op transfer; D1 kill-neighborhoods (96% have neighbors).
- Restated doctrine (this was always in `feedback_residue_must_be_navigable_not_logged` —
  we just never enforced it): **the failure of a reasoner attempting something is residue;
  the failure of a random claim is exhaust.** We spent 99% of cycles mapping exhaust.

## 3. The decision: one spine, everything else off

Icarus / Apollo / Forge / Learner are not four bets. Wired correctly they are ONE loop.
Build it in this order:

1. **Learner = the spine.** It generates capability-attached failures (the only kind that
   has ever produced signal). Only run it with the fixed pipeline (§4), never on the old corpus.
2. **Forge = the metabolizer.** Point Hephaestus at the Learner's failure clusters directly.
   This BYPASSES the Nous zombie gate (Nous becomes optional). The +11pp/+32pp result is the
   proof this works by hand; automating it is the claim under test.
3. **Router = the binder.** Uncap the Hephaestus solve matrix, add probe features, train
   router v0. This is the compounding mechanism — each iteration's failures target the next.
4. **Icarus = the harness, WITH a blind oracle or not at all.** Icarus already proved
   self-graded ladder climbs Goodhart (its own R1/R2 climb was false; Apollo gen-3551 same
   disease). It earns its place only once the frozen eval battery exists.
5. **Apollo = deferred.** Shelved with cause (R8 organism collapsed under perturbation).
   Its lineage is eval feedstock / Atalanta ore, not part of the loop yet.

## 4. Immediate next actions (the loop, concretely)

- **A. Fix the handoff mapper.** Port `ergon/learner/greedy/serializers.py` into
  `theseus/handoff/ergon_handoff.py:116` so ALL claim_kinds render (not just
  invariant_equality). Recalibrate training_weight (`:185-197`) so kills clear the 0.5 bar.
  (~100 lines. Unblocks ~40% of generated data + >100M stranded failure records.)
- **B. Build the compute-trace corpus.** From prometheus_math test suites + databases +
  cartography battery cascades. Shape: prompt = "compute X", completion = worked derivation.
  Property-based tests give unlimited fresh instances; gold computed by verified code; balance T/F.
- **C. Freeze the transfer eval battery.** `eval_greedy.py` already supports entity-disjoint
  + domain-transfer + computation-required slices. Make all three mandatory; this is the
  blind oracle that lets Icarus automate without Goodharting.
- **D. Train LoRA v0.5 on 7B (cloud GPU).** Local 17GB card caps at 3–4B; modexp ceilings at
  ~0.52 on 1.5B regardless of traces — do not interpret capacity bounds as data failures.
- **E. Router v0.** Regenerate solve matrix without top-10 cap, add probe/problem features,
  train scrap+probe → solved/unsolved, eval against preregistered H_A/H_B.
- **F. Wire `reasoning_quality_emit`** into every site where ≥2 evaluators score the same
  candidate. Unblocks H-R1 on real reasoning data + gives the contested-sampling lever.

## 5. Preregistered kill criteria (state the stakes BEFORE running)

- If LoRA v0.5 (diverse traces, all kinds, 7B) still shows **zero cross-op transfer** →
  "wrong data" hypothesis dies → pivot to router+tools (route around model limits, don't
  train through them).
- If router can't beat popularity baseline **cold-start even with probe features + uncapped
  solve sets** → behavioral residue doesn't generalize past warm-start → navigable-residue
  doctrine narrows from navigation to recommendation.
- If Forge tools built from Learner failure clusters **don't move the eval the cluster came
  from** → metabolize-failure thesis fails its first automated closed-loop test.
- Open from last session: the ~0.10 "genuine reasoning" number needs 4 kills before it's
  load-bearing — per-relation decomposition (is it all `equal` string-matching?),
  base-model-with-format control, magnitude scaling on `divides`, and it already failed
  transfer. Treat as "nonzero floor," not "extraordinary," until those run.

## 6. Rung gates (the ladder, operationalized)

- **R2 gate:** in-op transfer ≥ +0.15 over verdict-only across ≥6 ops (already shown for 8;
  make it the floor, not the headline).
- **R3 gate (THE WALL):** cross-op transfer > 0, p<0.05, on never-trained ops. Currently 0.
  This is what the whole loop is throwing diverse worked-traces + 7B capacity at.
- **R4 gate:** router-assisted cold-start tool selection beats popularity (the H_A test,
  currently NULL — the router prong exists to flip it).
- R6 self-monitoring enters only after R3, trained on contested/disagreement data the emit
  vectors surface.

## 7. What keeps running / what goes off

- **KEEP:** daily Gemini burn (use-or-lose), Hypatia (1/day), reduced Charon rotation
  (Hecate, Pollux, Moros, Stygian as loaders land), Talos corpus build, Icarus pilot +
  Polyhymnia (named operators).
- **OFF until they have a consumer:** Theseus continuous loop (keep as on-demand harness:
  A1 null, D1, A3, H2), Erebos composition (paused; reframe Phase-3 docs honestly —
  0 signal passes survive nulls, 1 infra pass stands).
- **ARCHIVE:** Eos→Aletheia→Skopos→Metis→Clymene→Hermes pipeline, Nemesis, Coeus, kairos,
  koios, zoo, papers, reproductions. **DELETE:** Auditor.
- **EXTRACT to shared falsification library** (`harmonia/lib/falsification_primitives/` or
  `prometheus_math/discipline/`): permutation_null, kill_tensor, stratified_ledger_sample,
  scale_artifact_detector, cold_llm_anti_anchor, coordinate_collision, Hodge bindings,
  14-test battery, canonical kill-ledger schema. Discipline rule: any "beats baseline X"
  claim emits its own permutation-null p-value or refuses PASS.

## 8. The one-sentence north star check

The compounding mechanism is NOT corpus volume — it is navigability of failure: the router
redirects generation toward what the Learner fails at, emit vectors make disagreement
sampleable, the falsification library makes every claim cheap to kill. This is the first
configuration where the falsification machinery and the capability machinery point at each
other instead of past each other. Everything off the spine waits until the spine produces
its first verdict.

---
*Provenance: program audit 2026-06-10 (committed 070a9096) + decision session 2026-06-15.*
