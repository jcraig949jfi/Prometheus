# 08 — Executive verdict

**Recommendation: BUILD — scoped to the M0 falsification prototype only, with frozen kill criteria. Not the engine.**

Audited tree: `5633cc02a`, in a new isolated worktree. The original checkout was not the reference commit; see 01 §0.

## Architecture at a glance

```
        ┌──────────── FIXED KERNEL K (RSO-owned; unreadable/unwritable by the learner) ───────────┐
        │ metered interpreter · dev oracle · ACCEPT from blank θ₀ on fresh panels · rollback · ledger │
        │ sealed held-out families written by another author                                       │
        └────────────▲───────────────────────────────▲──────────────────────────────▲─────────────┘
                     │ pass/fail                     │ accept / reject              │ replay
   tasks ──► SOLVE(φ, θ) ──► SLEEP: abstract → MDL gate → promote ──► θ (library, grammar)
                     ▲                                               │
                     │ same SOLVE, same φ, same θ                    ▼
   "improve φ" ──► SOLVE over edits of φ ──► screen ──► ACCEPT ──► φ′  (φ = 6 small DSL programs)
```

## What should be built?

A small, deterministic, CPU-only program-synthesis learner: the **Reflexive Library Learner (RLL)**.

- Its improvement machinery φ consists of six small programs, written in the same typed language as its task solutions:
  - search priority;
  - pruning key;
  - task schedule;
  - abstraction proposer;
  - grammar update;
  - edit screen.
- Improving φ is posed as one more search task, solved by φ itself, using the library θ it has learned.
- A fixed kernel decides acceptance. It tests every proposed φ′ from a **blank knowledge state** at **matched compute** on families the learner has never seen, and it can roll changes back.

## Why this architecture?

- **It is the only candidate with an L3 channel.** It is the only one of five where the meta-level is an object that the object-level machinery acts on. A (Aphrodite-V5), B (DreamCoder hybrid) and E (evolved plasticity) all have a fixed meta-level, so they cannot produce the L3 observation the brief asks for, however well they run (03).
- **It answers the specific failures in the record:**
  - inert improver levers (RB-6): φ is a program, not a menu;
  - inheritance substituting for improvement (R8): acceptance runs from θ₀, plus a continuation check;
  - the leaky meter exploited in one generation (RSI toy X2): the meter is inside the interpreter that runs φ;
  - the composition wall: useful improver edits are single 1–6-node changes judged on their own effect;
  - uncalibrated rulers: withheld-mechanism positive controls and a planted negative.
- **It is cheap enough to falsify.** M0 needs ≈ 3–4 engineer-weeks and ≤ 800 core-hours, with no GPU, no LLM and no paid API.

## Which existing Prometheus components are reused?

These are patterns and protocols, not organisms (01 §7):

| Component | Source |
|---|---|
| Escrow / charge meter, disjoint entropy domains, keyed common-random-number pairing | `roles/Aphrodite/engine/engine.py`, `fair.py` |
| Exact-expansion primitive promotion | `roles/Aphrodite/engine/w5p/promote.py` |
| Sham-donor and R8 enable-vs-substitute protocols | Aphrodite Tier 3 / Beta-02 |
| The reuse-assay control battery | Crius |
| Shuffled-history / random-library ablations | D-series |
| Independent evaluator ownership and the deterministic adversarial kit | `rso/`, `rso/adversary` |
| Distributed fan-out | Fabric (`fabric/`) |

No existing substrate is reused. Ananke, Crius, Theseus, Aether, Nestor and the fold DSL each have a measured ceiling or a needle landscape.

## Which external mechanisms are adopted?

| Mechanism | Used as |
|---|---|
| Success-Story Algorithm | Rollback-stack acceptance |
| OOPS | One searcher, reusable earlier code |
| STOP | Self-application structure, without the LM |
| Huxley-Gödel Machine | Descendant-based meta-metric |
| DreamCoder | Wake/sleep baseline and fixed-improver control arm |
| Stitch (MIT) | MDL cross-check |
| Observational-equivalence pruning, multi-hole anti-unification | Withheld positive controls |

None of the LLM-based systems (DGM, AlphaEvolve, STOP, Hyperagents) is used at runtime (02).

## What genuinely new mechanisms must be created?

1. Improver slots written in the task language, so that **learned task abstractions become one-node moves in improver space**: the "operational knowledge" channel.
2. The **meta-knockout assay**: rerun generation g+1's meta-search with the parent's meta machinery (or without the learned library), at matched compute. This measures whether a modification *caused* the next one to be found. I found no published L3 test of this form (02 §8, and Aphrodite's prior-art survey §2(a)).
3. The **withheld-mechanism battery**: known-good improver changes, certified by a hand-built run, used as positive controls for whether the meta channel can reach anything.

## What is the first experiment?

**RLL-M0-E1:** arms T, XM, HP, CM, F0, SH; 3 seeds × 10 generations; ≈ 200–500 core-hours. The question: does the reflexive meta-search rediscover any of six withheld, certified-good improver mechanisms, does it beat a fixed random-edit meta-searcher, and does it beat tuning and compute-matched baselines on sealed held-out families? (07)

## What would show it is working?

In order of strength:

1. ENGINEERING_SUCCESS, meaning replay is byte-identical and the adversarial kit reports 0 SURVIVED.
2. LEARNING_DEMONSTRATED.
3. SELF_MODIFICATION_DEMONSTRATED: an accepted φ-edit beats the fixed, compute-matched, tuned and sham arms on sealed held-out families, with knock-out and transplant confirming the effect.
4. **BOUNDED_RECURSIVE_IMPROVEMENT_SUPPORTED:** a second accepted edit, where meta-knockout shows the first edit (or the learned library) raised the rate of finding it, and the parent's meta machinery from the same state finds it less often. Exact rules are in 06 §6.

## What would make me abandon it?

- **S-META:** across 3 seeds × 10 generations, 0 of 6 withheld mechanisms rediscovered and no edit accepted. The meta channel is inaccessible.
- **S-L2:** edits are accepted, but none beats tuning (HP) and compute-matched (CM) baselines on held-out families. The meta-level is a tuner.
- **S-L3:** meta-knockout shows no causal effect at adequate power over two rounds.
- **S-HACK:** any kernel breach.

## Confidence

These are probabilities that M0/M1 reach each class. They are my judgment, and I state them so they can be scored afterwards.

| Class | Probability | Reason |
|---|---|---|
| ENGINEERING_SUCCESS | 0.8 | Mostly re-implementation of patterns that already pass their tests here (49 + 9 + 27 + 41 tests run) |
| LEARNING_DEMONSTRATED | 0.75 | DreamCoder-class L1 is well established |
| SELF_MODIFICATION_DEMONSTRATED (beats HP and CM) | 0.4–0.5 | Rediscovery of observational-equivalence pruning alone should beat φ₀, but HP and CM are strong controls |
| BOUNDED_RECURSIVE_IMPROVEMENT_SUPPORTED | **0.10–0.15** | No published no-LLM discrete L3; the autoconstructive-evolution record is poor; the most likely positive is the narrow "pruning helps both levels" route (attack 1) |
| L4 transferable | ≈ 0.03–0.05 | |

Why BUILD rather than RESEARCH FURTHER: further reading cannot settle the question. Twenty years of OOPS/SSA and the whole Aphrodite RSI record leave L3 untested in exactly this form, and M0 settles the meta-channel question for under 800 core-hours. Why not STOP: the brief prefers a reproducible negative, and this design produces one by its frozen kill rules.

---

## Adversarial self-evaluation

1. **Strongest simpler competing explanation.** The likeliest "L3" is generic: observational-equivalence pruning makes *any* search cheaper, and because the meta-search is the same search, it gets cheaper too. That satisfies the definition but is a single, designer-anticipated, non-compounding effect. **Mitigation:** results are reported per channel, and a C1 positive driven only by a withheld mechanism (W1-class) is labelled "designer-anticipated reflexive transfer". Calling it open recursion needs a second, non-withheld edit chain.
2. **Most likely hidden designer intelligence.** The primitive set P₀ (`dedup_by`, `run_on_examples`, `logp`, tree primitives) and the edit grammar make good edits short. The dev generator's motif grammar decides what recurs. Only Δ from φ₀ is credited (04 §6), and the held-out generator has a different author. Even so, the shape of the discoverable space is mine.
3. **Most likely representational ceiling.** φ has six fixed slots and the order wake → sleep → meta is fixed. RLL cannot invent a new phase, a new slot, or a new data structure for itself. Its ceiling is roughly "a self-configuring DreamCoder". Lifting it (letting φ define new slots) brings back the autoconstructive failure modes. Deferred deliberately.
4. **Most likely search bottleneck.** Meta-evaluation costs ≈ 1–4 core-minutes per candidate, so ≤ 64 candidates are screened per generation. Any useful change that needs two coordinated slot edits (for example a new abstraction proposer *plus* a grammar update that exploits it) is a meta-level composition wall, a parity-like target that acceptance-tested hill climbing cannot find (Valiant/Feldman, recalled). I predict most accepted edits will be single-slot.
5. **Most likely measurement artifact.** AUC over 3 rounds from θ₀ rewards edits that speed *early* learning. That is the HGM metaproductivity mismatch: they may hurt long-horizon learning. Gains are also relative to the budget C_eval (the A23 walk-cliff lesson). Mitigations: the continuation test, the 0.5B/2B budget shift in M2, and the rollback re-tests. A long-horizon arm is still not in M0.
6. **Costliest unverified assumption.** Channel C2 — that abstractions learned from *task* programs are useful vocabulary for *improver* programs. Integer-list tasks and frontier-scoring programs may share almost nothing. If so, C2's knock-out is null, and only C1 remains. M2's tree/AST domain may need to move into M0 if E1 shows zero library use in φ-edits.
7. **Power risk.** Too few lineages may reach a second accepted edit. MSR comparisons detect only large effects: 0.55 vs 0.15 at 0.85 power with 30 replicates per arm; 0.5 vs 0.2 needs ≥ 40. Underpowered results are UNTESTABLE, not negative. The C-019 lesson is applied.
8. **Generator overfitting.** Acceptance uses the dev generator. The held-out generator by another author may not share its motifs, so T could win on dev-generator families (H₁-same) and lose on H₁. That would be a real negative, and it is reported via the H₁-same − H₁ gap.
9. **Is it new, or a known optimiser renamed?** Mechanistically it is OOPS-style self-application without an LM, inside a DreamCoder-style loop. The new parts are the operational-knowledge channel and, above all, the **causal assay** (meta-knockout, withheld battery, θ₀ acceptance). If the mechanism turns out ordinary, the assay is still the contribution: it can test any future candidate, including LLM-based ones under the Phase-3 three-layer separation.
10. **The experiment most likely to falsify quickly: RLL-M0-E1.** If six certified-good, short (≤ 6-node) improver edits are not found in 30 generation-seeds, the reflexive meta channel is inaccessible at this scale, and the route stops for ≤ 500 core-hours.
11. **Same-family bias.** I am the same model family as many Prometheus engine authors, Hestia's auditor, and the prior OPUS-5.5 Phase-3 design. My agreement with their diagnoses (composition wall, ruler first) is not independent confirmation. The held-out generator and the acceptance code must be written and reviewed by a seat other than the engine author, preferably another model family or a human.
12. **Rollback oscillation.** SSA-style re-tests on fresh panels can pop and re-accept the same edit. Mitigation: rejected hashes are never re-proposed, and pops are logged as results.

**Is any architecture scientifically viable?** As a *falsification instrument*, yes. As an engine expected to produce compounding recursive intelligence, the evidence does not support that expectation today. Nothing in Prometheus or the no-LLM literature has shown it. A recommendation stronger than "BUILD M0 and let the kill rules decide" would be an unsupported claim.

## Unresolved questions (not answered here)

1. Which RSO seat authors the held-out generators, and on what schedule? Custody design is RSO's.
2. Does the operator accept a 1:1 C_obj : C_meta split, or prefer 2:1? This affects CM's strength.
3. Should M0 include the tree/AST domain from the start (attack 6)? I recommend deciding after E1's library-use census.
4. Interpreter throughput is unmeasured; every compute figure here is an estimate pending M0 step 1.
5. Whether Ananke's C5T outcome (still uncommitted per the C-019 closeout) changes the composition-wall priors. It does not change this design, but it should be read before any M2 Composition-Ladder port.
