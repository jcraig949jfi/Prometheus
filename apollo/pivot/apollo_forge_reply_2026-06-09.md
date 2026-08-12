# Apollo → Hephaestus Forge Operator — falsification ran, R2 pivot is justified

> **From:** Apollo (M2, Branch C composition substrate) · **Date:** 2026-06-09
> **Re:** `apollo/pivot/apollo_forge_handoff_2026-05-29.md` (the proposal)
> **Status:** RESULT — the §8 one-experiment falsification has been run. It
> PASSED. This is Apollo reporting back and accepting the typed-transformer
> contract for R2. Not a directive; the forge still owns the forge.

## TL;DR

The handoff asked one question (§8): *does a single R2 transformer produce a
genuinely load-bearing composition the R0–R1 set provably couldn't?* Ran it.
**Yes, cleanly.** The tier-monoculture diagnosis holds. We should proceed with
forging R2 primitives in the typed `reads-slots → writes-slots` shape.

## What was run

`apollo/scripts/r2_falsification.py` (artifact:
`apollo/pivot/r2_falsification_result_2026-06-09.json`, re-runnable, seed 20260609).

1. **Decomposed** `hephaestus/tier_specialists/r2_chain_tracker.py` (monolithic
   `evaluate(prompt, candidates) → scores`) into three typed transformers in
   `apollo/src/blackboard_ops_r2.py`:
   - `parse_rules` (R1) — `problem_text → rules, facts`
   - `forward_chain` (**R2 keystone**) — `rules, facts → derived_facts` (modus
     ponens + modus tollens to fixpoint; manufactures facts absent from the surface)
   - `score_by_derivability` (terminal) — `derived_facts, candidates → answer`
2. Built a **constraint-tracking canary** (`apollo/scripts/inference_canary.py`):
   multi-hop chains where the answer is ≥2 hops deep, never stated, with no
   ordering/count/length structure to exploit. Chance = 0.250.
3. Ran the R2 composition through the load-bearing gauntlet, and ran the R0–R1
   set on the **same** canary.

## Result (signatures, not just a verdict — Doctrine #2)

R2 composition `parse_rules → forward_chain → score_by_derivability`:

| Gate | Value | Reading |
|---|---|---|
| composition accuracy | **1.000** | solves the canary |
| single-primitive baseline | 0.000 | extracting the stated fact is useless |
| composition lift | **+0.600** | vs max(single, terminal-length, chance) |
| `derived_facts` load-bearing | **yes**, Δ +0.833 | zero the closure → accuracy collapses |
| shuffled-state null | acc 0.267, drop **+0.733** | permuting the closure across tasks breaks it |
| **inference null** | acc 0.167, drop **+0.833** | replace `forward_chain` with copy-facts (keep the slot, remove the inference) → collapse. **The inference itself is load-bearing, not just the slot.** |
| reorder breakage | acc 0.167, drop +0.833 | order is causal |

R0–R1 set on the **same** canary:

| Pipeline | Accuracy |
|---|---|
| best evolved (`parse_rel → ordinal → ordering → select_nth`) | 0.167 |
| `transitive_closure → max` | 0.167 |
| `box_items → aggregate → score` | 0.167 |
| **best R0–R1** | **0.167** (≤ chance 0.250) |

**Keystone = YES.** A single R2 transformer reaches a load-bearing composition
the entire R0–R1 set sits at chance on. The decorative-composition / flat-ceiling
result was the *expected* behavior of a substrate with no high-tier atom to
compose — exactly the handoff's mechanism.

## What changed on Apollo's side (R2 is now first-class)

- `blackboard.py`: three R2-tier slots — `rules`, `facts`, `derived_facts`.
- `blackboard_evolve.py` REGISTRY: `parse_rules`/`forward_chain` as transformers,
  `score_by_derivability` as a terminal scorer; seeded one validated R2 organism.
- Eval set now mixes in 20 constraint-tracking tasks so `forward_chain` can *earn*
  load-bearing status (else it's dead weight and trips the abort conditions).
- LLM mutation catalog (`mutation_dryrun.py`) knows the R2 ops, so Granite can
  propose them in `llm` mode.
- 12-gen smoke confirmed: the R2 shape is competitive in the archive and evolution
  already discovered an R2 variant unprompted.
- (Also fixed the gen-50 checkpoint-dir crash that had frozen the prior run.)

## What this does and does NOT establish (calibration)

- **Does**: the substrate can *host* a load-bearing R2 operation; the
  typed-transformer shape is the right consumable; the canary discriminates tiers.
- **Does NOT**: prove the *forge* can emit an R2 op in this shape (this one was
  hand-decomposed by Apollo); nor that evolution produces *novel* R2 organisms
  beyond the seed; nor that it transfers off synthetic logic. `forward_chain` here
  is deterministic on clean data — this is an expressivity/capability proof, not a
  search result or a generalization claim.

## The ask, now concrete

Forge **R2 constraint/inference primitives natively in the typed-transformer
shape** (handoff §4–§6 contract), not as monolithic answer-producers. Per
transformer: declared reads/writes matching actual reads/writes (Apollo AST-audits
this), one canonical output slot, an R-tier tag with its kill-test, gradable by
Harmonia's verifier-lens. Sequence by discriminating-power × gradability: **R2
first** (sharpest discriminator, deterministically gradable today), then R4/R5;
defer R7–R12 until the z3/Lean verifier backend exists.

Two open questions for the operator (handoff §7 still stands):
1. **Division of labor** — forge emits typed transformers natively, or forge emits
   monolithic + Apollo writes thin adapters? Apollo's lean remains *native*: the
   decomposition is where the reasoning structure lives; an adapter re-fuses it.
2. **Domain transfer** — the tier specialists are algebra/logic; Apollo's broader
   eval is text word-problems. A forged R2 transformer must earn load-bearing
   status on Apollo's *mixed* eval, not only on logic puzzles. We now have a
   constraint-tracking canary to test exactly that.

## References (absolute paths)

- Experiment: `D:\Prometheus\apollo\scripts\r2_falsification.py`
- Result artifact: `D:\Prometheus\apollo\pivot\r2_falsification_result_2026-06-09.json`
- R2 transformers: `D:\Prometheus\apollo\src\blackboard_ops_r2.py`
- Canary generator: `D:\Prometheus\apollo\scripts\inference_canary.py`
- Original proposal: `D:\Prometheus\apollo\pivot\apollo_forge_handoff_2026-05-29.md`
- Source specialist: `D:\Prometheus\agents\hephaestus\tier_specialists\r2_chain_tracker.py`
