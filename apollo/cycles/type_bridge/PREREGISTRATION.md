# Preregistration — Apollo type-bridge metabolic cycle (T0 → T1)

> **Author:** Apollo (M2) · **Written:** 2026-08-19, BEFORE any arm executed
> **Cycle:** dossier Part Four ruling 3 (the heredity rule), first-cycle candidate #2
> **Mode:** deterministic only. `--mode llm` fired its own kill condition (2,152 Granite
> mutations, zero lift, 2026-06-28) and is NOT revived.
> **Constraint:** no new architecture. Every ablation rebinds module globals on an imported
> `blackboard_evolve`; the substrate is not edited on disk.

---

## 0. A factual correction the brief predates — read this first

**The bridging op already exists, and has since 2026-06-10.** This cycle's intervention step
was executed two months ago, by Apollo, and its falsification passed the same day.

- `relations_from_facts` (`reads=["derived_facts"] → writes=["relations"]`) is live at
  `apollo/src/blackboard_ops_r2.py:169` and registered at `blackboard_evolve.py:65`.
- `apollo/pivot/cross_tier_falsification_result_2026-06-10.json`: the cross-tier pipeline
  scores **accuracy 1.0, comp_lift 0.70**, with `derived_facts` *and* `relations` both
  load-bearing **through the bridge** under the existing data-flow test.
- Production runs since then produce cross-tier organisms in quantity — 217–224 de-novo
  events per 150-generation control run in the 2026-08-15 wall corpus.

So "forge the bridge, rerun, measure" is **already discharged**. What was never done is the
step the heredity rule actually cares about: **REPRODUCE, and archive the lineage.** An
improvement that cannot be replayed is not inheritance. That is what this cycle does.

**What remains genuinely open:** the T0 diagnosis named the gap as "no op reads
`derived_facts` and writes `relations`/`counts`." Only the `relations` branch was closed. No
op writes `counts` from `derived_facts` — the sole counts-writer is `parse_box_items`, which
reads `problem_text`. And `apollo/src/hephaestus_ops.py` — repaired 2026-08-12, 9 ops,
importing for the first time — contains **no bridge op of either kind**, so the forge's debt
is still open on the forge's side. §5 states the type signature, and why Apollo does not
want it built yet.

## 1. What is being tested

The T0 diagnosis makes two separable claims:

- **C1 — expressivity.** Without a `derived_facts → relations` bridge the cross-tier organism
  *is not in the search space*, so no search can find it.
- **C2 — search operator.** With the bridge, mutation alone still cannot assemble it;
  crossover can (2026-06-16 A/B: 4/5 vs 0/5).

Both were asserted from separate experiments run seven weeks apart under different configs.
**Neither has been tested against the other, and neither has been replayed.**

## 2. Design — 2×2, five seeds, deterministic

Factors: `BRIDGE ∈ {present, absent}` × `XOVER ∈ {0.3, 0.0}`.

| arm | bridge | crossover | what it is |
|---|---|---|---|
| **A0** | absent | off | the reproduced **T0** state (June's 481-generation flat run) |
| **A1** | absent | on | **falsifier of C1** — can crossover bridge tiers with no bridge op? |
| **A2** | present | off | **the classification call** — does mutation alone suffice once expressible? |
| **A3** | present | on | **T1**, and the replay of the 2026-06-16 treatment arm |

Config matches the archived A/B exactly, so A2/A3 are a true replay:
`gens=400, pop=24, mode=deterministic, seed_variant="ingredients", dispatch=False`,
seeds `[20260616, 1, 7, 42, 101]`.

`ingredients` is mandatory: it seeds the two splice parents but **not** the assembled solver,
so a discovery cannot be a one-edit copy of a seed.

`BRIDGE=absent` removes `relations_from_facts` from the registry and purges it from seed
pipelines — the same ablation as wall-corpus EX-02.

## 3. Outcomes — existing instruments only, no new meter

**Primary:** `novel_multitier` — the substrate's own de-novo discovery signal, defined before
this cycle at `blackboard_evolve.py:629`: an archive occupant containing `forward_chain` AND
`op_build_ordering`, **not** a seed pipeline, with `cross_tier_acc ≥ 0.9`. Per arm we report
**discovery rate = seeds with ≥1 such organism / 5**.

**Secondary:** first discovery generation; best `comp_lift`; best `n_load_bearing`; `max_acc`;
cross-tier subset coverage.

**Graduation threshold (pre-existing, from `n_distinct_real_shapes`):** `comp_lift > 0.05`
AND `n_load_bearing ≥ 1`. Not invented here.

## 4. Pre-committed decision rules

**SUCCESS** (cycle closes; the capability improvement is real *and* reproducible):
A3 discovers in **≥3/5** seeds, with ≥1 discovered organism meeting the graduation threshold,
AND A0 discovers in **0/5**. That replays the archived 4/5-vs-0/5 and reproduces T0→T1 under
one harness, on one day, on one machine.

**FAILURE — the honest one, and a real result:** bridge present, crossover on, and A3 still
discovers **0/5**. That falsifies the type-bridge account as sufficient and says the June
result does not survive replay. It will be reported as prominently as a success.

**FAILURE — C1 falsified:** A1 (no bridge, crossover on) discovers **≥3/5**. Cross-tier
organisms would then be reachable without the bridge, and the expressivity claim — the "deep
cause" of the T0 document and the specific finding the dossier elevates — is wrong.

**INCONCLUSIVE:** any arm landing 1–2/5 is reported as such. At n=5 the resolution is coarse
by construction; no arm separation below 3/5 is claimed as a result.

**The classification call** (Harmonia C's open question — `search_operator` vs part of
`evolutionary_search`), decided by A2, committed to before seeing data:

| A2 (bridge present, crossover OFF) | ruling |
|---|---|
| **0/5** while A3 ≥3/5 | crossover is **necessary**, not merely faster. A capability that appears only when one operator is added, and never otherwise, is *supplied by that operator* → classify **`search_operator`**. Apollo's `evolutionary_search` kill count stays at **5**, the exhaustion threshold holds, and the lane **redirects**. |
| **≥3/5** | mutation alone suffices; crossover is an accelerant inside the existing regime → classify **part of `evolutionary_search`**. That class has a June success, the count **resets**, and the lane **continues**. |
| **1–2/5** | INCONCLUSIVE. Report both sensitivities; make no ruling. |

Under ruling R3 (do not narrow), **both outcomes keep the lane** — EXHAUSTION is a redirect
signal, not a kill.

## 5. Request to Hephaestus (supplier-only) — specified, and deliberately not yet wanted

The still-open branch of the T0 gap, should the forge want to discharge it:

```
name:   counts_from_facts
reads:  ["derived_facts"]
writes: ["counts"]
precondition: bool(s.derived_facts)
contract: project cardinality atoms from the forward-chain closure into the typed
          counts mapping that op_aggregate_quantities consumes. Single canonical
          output. Declared reads must be actual reads (no recompute-bypass).
```

**Apollo does not want this built yet, and the reason is the T0 document's own Cause 2:**
nothing in the current battery rewards it. No task requires deriving a count by inference
rather than parsing it. Shipping the op first would repeat exactly the mistake Cause 2 names
— an expressible composition with no fitness gradient to select it. **The task must precede
the operator.** If the forge wants the debt closed, the cheaper half is a cross-tier
*counting* canary; the op is worth forging only once such tasks exist.

## 6. What this cycle cannot show

Deterministic search only, one substrate, n=5 seeds, one battery. It reproduces a specific
June finding and settles one classification call. It says nothing about whether a *model*
could have proposed the bridge — that is the widening question, and per dossier ruling 5 it
is heredity's third stage, not this one.
