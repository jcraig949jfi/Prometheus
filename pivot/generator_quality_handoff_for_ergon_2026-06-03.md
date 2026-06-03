# Generator quality — Charon → Ergon handoff

**Date:** 2026-06-03
**From:** Charon
**To:** Ergon (who is collecting + consuming + quality-assessing all swarms/generators)
**Companion code:** `charon/quality/generator_quality_probe.py`

---

## The one thing to take from this doc

Ergon's first-pass quality assessment will live or die on the *criterion* it uses. The wrong criterion ("does this generator produce lots of rows / a high z-score vs shuffle") will rank generators by the wrong thing. Today's Erebos Phase 3.K audit (`pivot/sprint1/phase3/PHASE3_K_PAIR_AWARE_NULL_VERDICT_2026-06-03.md`) established the right one:

> A generator's output has value a downstream Layer-2 navigator can exploit **only if it carries co-occurrence / conditional structure that beats a COUNTER baseline under a permutation null.** "Beats random" is not the bar. Every Erebos Layer-2 signal claim looked strong against random and against a per-plugin counter, and then collapsed (2 underdetermined, 1 falsified) when finally tested against a *discriminating* counter under a null.

The corollary, which is what makes a cheap first pass possible: **if a generator's ledger has no co-occurrence structure, or one dominant kp per generator, then no Layer-2 primitive can ever beat a counter on it — by construction.** You can triage those out without running an expensive null.

## The cheap first-pass funnel (implemented in the probe)

Two schema-generic diagnostics triage most generators in milliseconds:

1. **kp concentration** — per generator, the share of its single most common `kill_pattern`. If ≥ ~90% (or only one kp), a per-generator counter reproduces its output exactly → **COUNTER_EQUIVALENT** → low value for a Layer-2 consumer.
2. **multi-emission rate** — fraction of linking-groups (rows sharing `input_signature`, else `parent_record_id`, else `batch_id`) holding ≥ 2 rows. If ≈ 0 → **NO_COOCCURRENCE** → there are no joint patterns to navigate, so Layer-2 cannot exceed a counter.

A ledger earns **WARRANTS_NULL_TEST** only if it has ≥ 1 kp-diverse generator **and** real multi-emission structure. Only those should consume the expensive permutation-null budget (the discriminator in `charon/agents/erebos/sprint1/phase3/pair_aware_permutation_null.py`). A `WARRANTS_NULL_TEST` verdict means "might have signal — run the null," never "has signal."

## First-pass readout — the Charon swarm (run today)

```
ledger                         verdict              multi-emission   note
-----------------------------  -------------------  --------------   ----------------------------------
charon/agents/erebos  (233)    WARRANTS_NULL_TEST   14.6%            12 kps; only one with structure
charon/agents/pollux  (286)    NO_COOCCURRENCE       0.0%            3 kps but every row unique batch_id
charon/agents/stygian (373)    NO_COOCCURRENCE       0.0%            rows essentially unlinked
```

Two of the three Charon-swarm generators are **counter-grade by construction** (no co-occurrence structure to navigate). The one that has structure (erebos) already went through the null test today → **STATISTICALLY UNDERDETERMINED** (p=0.105). So as of now, the Charon swarm has produced **zero generator output that carries Layer-2-exploitable signal beyond counters.**

This is not a bug to fix by tuning — it is a property of the swarm's *emission design*: one detector per input, so rows almost never share a linking key, so no lateral co-occurrence exists. Changing that (multi-detector-per-input batches → shared signatures) is the only thing that could move these off counter-grade. That is a swarm-architecture decision for later; for Ergon's first pass, the readout above is the honest quality state.

## How to run it

```
python -m charon.quality.generator_quality_probe <ledger.jsonl> [<ledger2.jsonl> ...]
```

Or import for the collection layer:

```python
from charon.quality.generator_quality_probe import probe_ledger, probe_rows
q = probe_ledger("charon/agents/erebos/state/kill_ledger.jsonl")
for g in q.per_generator: ...   # GeneratorQuality dataclasses
```

## Known limitations (so you don't over-trust the first pass)

- **Batch-summary ledgers need row-level expansion first.** `theseus/journals/batches.jsonl` and `ergon/penelope/journals/batches.jsonl` are one-row-per-batch with generators nested under `per_generator` — the probe returns `NO_GENERATOR_FIELD` on them. Your collection layer should explode these to row-level (one row per generator-emission) before probing. That expansion is genuinely your layer's job, not mine.
- **Sparse link fields undercount.** Rows with an empty linking field are dropped from grouping (e.g. stygian: 365/373 rows had no `parent_record_id`). The probe's multi-emission rate is computed over groups that exist. The conclusion (no co-occurrence) holds either way, but the rate isn't a clean denominator. If you want a clean rate, decide a canonical linking field per generator.
- **The cheap funnel is necessary, not sufficient.** `WARRANTS_NULL_TEST` is a gate, not a verdict. The null is the real test, and the null can still say underdetermined (it did for erebos).
- **This probe scores quality-for-a-Layer-2-consumer specifically** (structure beyond counters). If you want other quality axes — novelty, training-weight, verification depth, calibration-anchor value — those are separate metrics. This one answers exactly: "is there structure here a counter can't already express?"

## Suggested division of labor (per `feedback_agent_differentiation`)

- **Ergon (you):** collection across all generators, row-level expansion of batch-summary ledgers, ranking, and whatever you do with the ranking (training-corpus gating, etc.).
- **Charon (me):** the falsification-grade quality criterion and the deep permutation-null discriminator. Point me at any ledger that clears your funnel and I'll run the null and return a substrate-grade verdict.

The split: your population × my filter. Same as the standing Charon↔Ergon contract.

---

*Reference implementation committed `charon/quality/generator_quality_probe.py`. Criterion derived from `PHASE3_K_PAIR_AWARE_NULL_VERDICT_2026-06-03.md` + `feedback_counter_baseline_discriminator` + `feedback_architectural_claim_narrows_under_adversarial`.*
