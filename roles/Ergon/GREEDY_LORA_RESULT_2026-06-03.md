# Greedy Substrate → LoRA — Needle-Movement Result (2026-06-03)

**Directive (James):** build a greedy consumer that scrapes all substrate it can
find as LoRA training data; see if ingesting it moves the needle toward mathematical
reasoning. Scope chosen: **full loop (build → train → eval)**, sources **tiered by trust**.

**Stand-down note:** this run overrides the Phase-3 training stand-down at James's
explicit direction. One-off experiment.

---

## Headline

**The needle moved, hard — and the gain survives the content control.**

| Condition | Gold accuracy (1,200 held-out, 600T/600F) | parse-fail | acc on True | acc on False |
|---|---|---|---|---|
| **Base** Qwen2.5-Math-1.5B-Instruct | **0.228** | 0.653 | 0.457 | **0.000** |
| **Greedy LoRA (real labels)** | **0.907** | 0.000 | 0.908 | 0.905 |
| Shuffled-label control | 0.681 | 0.000 | 0.962 | 0.400 |

Raw delta base → trained: **+0.678**. Training time: ~10.5 min/run on the RTX 5060 Ti.

---

## Honest decomposition (what the +0.68 actually is)

The raw jump is real but it's **two effects stacked**, and the experiment was designed
to separate them:

1. **Format effect (~format-following).** The base model *can't emit a parseable
   verdict 65% of the time* — it answers in its own format, not "True/False" (exactly
   the eval-protocol mismatch Aporia flagged in v0.5). Any LoRA fixes this: both the
   real and shuffled adapters have 0% parse-fail. The shuffled-label control isolates
   this effect: it learns the format and scores **0.681** with *no content signal*.

2. **Content effect (genuine discrimination).** Real LoRA **0.907** vs shuffled control
   **0.681** = **+0.226** that is *content, not format*. And the tell is in the
   balance:
   - The **real LoRA is balanced** — 0.908 on true claims, 0.905 on false. It learned
     to *discriminate*.
   - The **base has zero discrimination** — 0.000 on false claims; when it answers at
     all it essentially always says "True."
   - The **shuffled control is lopsided** — 0.962 true / 0.400 false: it learned format
     + a "True"-leaning prior, not what's actually true.

So: ingesting the substrate taught the model to *correctly judge whether these
mathematical claims hold*, well beyond just learning the answer format. That is the
thesis ("learn what doesn't work to reveal what does") showing up as measurable,
control-survived behavior.

Per-source on the real LoRA: hephaestus 1.00, pollux 1.00, theseus 0.86 — it learned
all three gold-labeled failure families, hardest on the cross-catalog knot×ec relations.

---

## Generalization probe — CounterMath (OOD, no gold labels in cache)

| | base | trained |
|---|---|---|
| unparsed | 50 / 120 | **0 / 120** |
| judged True | 56 | 19 |
| judged False | 14 | **101** |

The trained model **generalizes its judgement behavior out of distribution**: on
CounterMath (counterexample-reasoning statements it never trained on) it goes from
42% non-answers to 0%, and shifts decisively toward "False." CounterMath is built
around statements that are *false / have counterexamples*, so a False-lean is
directionally correct — **but I cannot claim accuracy** (this cached copy has no gold
labels). Read this as: the failure-data training produced a model that confidently
judges OOD math statements and leans toward falsification. Plausibly good, unverified.

---

## Caveats (do not over-read this)

1. **Held-out is claim-level disjoint, not object-level.** The gold set excludes
   trained `uid`s, but the same knot/EC objects may appear in train under a *different*
   relation. Part of the knot×ec gain could be **memorized invariant values** rather
   than reasoning. Next run: object-level (entity-disjoint) split.
2. **In-distribution, narrow.** The gold task is judging substrate-shaped claims
   (invariant relations, correlation-survival, will-it-forge). This is *narrow
   mathematical judgement*, not general MATH-benchmark reasoning. The CounterMath probe
   is the only OOD signal and it's unscored.
3. **Format-following is a large share of the raw number.** The honest "reasoning"
   gain is the trained-vs-shuffled +0.226 and the true/false balance, not the full
   +0.68.
4. **One seed, one epoch, rank 16.** No error bars yet.

---

## What this establishes

- The audit's core claim is now demonstrated end-to-end: the stranded failure data,
  once actually ingested, **changes model behavior in the target direction** — and the
  effect survives a label-shuffled control, so it's content, not artifact.
- The greedy consumer works: 18,464 examples, 60% failure data, ~12 domains, both
  monocultures broken — assembled from 6 substrate sources that previously reached the
  Learner corpus at 0%.
- A clean, falsifiable, reproducible rig now exists (`ergon/learner/greedy/`).

## Recommended next steps

1. **Entity-disjoint held-out** to separate reasoning from value-memorization (caveat 1).
2. **Score CounterMath properly** — obtain gold T/F labels (or LLM-judge) for a real OOD accuracy number.
3. **Ablate the tiers/sources** — does Tier-2 prose help or hurt? Does each source carry weight?
4. **Scale corpus** via the audit's ingestion unblocks (un-stall Theseus handoff to ship kills; Charon/Hephaestus adapters) and re-run to see if more varied failure data lifts OOD.

---

# Addendum 2026-06-04 — Entity-disjoint re-test (reasoning vs memorization)

Follow-up to caveat 1. v1 **hid the invariant values from the prompt**, so in-distribution
accuracy could be explained by *recalling memorized values*. This re-test holds out the
underlying objects entirely (no knot/EC appearing in eval was ever in training) and runs two
framings: **values withheld** (recall task) and **values given in the prompt** (pure reasoning).

| Framing | base | trained | what it isolates |
|---|---|---|---|
| v1 — in-distribution, values hidden (objects SEEN) | 0.228 | **0.86** (theseus) | recall + priors + format |
| **E-hidden** — entity-disjoint, values withheld | 0.233 | **0.744** | objects unseen → no value recall possible |
| **E-shown** — entity-disjoint, values GIVEN | 0.119 | **0.841** | reasoning from data, memorization impossible |
| relation base-rate oracle (no values, no objects) | — | **0.669** | floor reachable from priors alone |

All trained numbers are balanced across true/false (≈0.72–0.85 each side) and 0% parse-fail.

## Decomposition of the trained model's accuracy

1. **Format-following** — base emits no parseable verdict 64–81% of the time; trained 0%.
   A large share of every raw base→trained delta is just learning to answer True/False.
2. **Relation base-rate priors ≈ 0.669** — a predictor that knows only "which relation types
   usually hold" (equal → ~always false; divides → ~64% true; parity → skewed) reaches 0.669
   with **zero object or value knowledge**. E-hidden (0.744) is essentially this floor + ~0.07.
   This is shallow distributional learning, **not reasoning**.
3. **Value memorization ≈ +0.116** — v1 in-distribution (0.86) minus E-hidden (0.744). Real,
   but modest: memorizing seen objects' invariant values bought ~12 points. v1 was **not**
   mostly memorization, as I'd worried — most of v1 survives entity holdout.
4. **Genuine relational reasoning ≈ +0.097** — E-shown (0.841) minus E-hidden (0.744). When
   given the data on **never-seen objects**, the model correctly judges the relation 84% of the
   time, balanced, with memorization ruled out by construction. This is the clean reasoning
   signal. (It's diluted: ~37% of the eval is non-invariant_equality "other" claims that gain
   no clean values in the shown framing, so the per-relation reasoning lift is larger than the
   aggregate +0.10.)

## Honest verdict

- **The needle moved in every framing, robustly** — even with objects fully held out
  (0.23 → 0.74 hidden; 0.12 → 0.84 shown). Ingesting the substrate is not a memorization
  artifact.
- **But the "mathematical reasoning" share is the smallest component.** Ordered by size:
  format-following > relation base-rate priors (~0.67) > value memorization (~0.12) >
  genuine reasoning (~0.10). The eye-popping +0.68 from v1 was mostly format + priors.
- **The genuine reasoning is real and clean**: E-shown 0.84 on entity-disjoint objects with
  values given cannot be memorization or pure priors — the model learned to evaluate these
  relations from data and generalize to unseen objects. It's narrow (simple relations) but real.

## Implication for the program

The substrate-ingestion thesis holds at the level it can be cleanly demonstrated: failure-data
training teaches genuine (if narrow) relational reasoning that survives entity holdout. To grow
the *reasoning* share rather than the *prior* share, future corpora should (a) always show the
data in-prompt (judge-from-evidence, not recall), (b) balance labels within each relation type
to kill the base-rate shortcut, and (c) add multi-step claims where priors can't substitute for
reasoning.

## Addendum artifacts
- Corpora: `corpus/{train,gold_eval}_e_hidden.jsonl`, `corpus/{train,gold_eval}_e_shown.jsonl`
- Adapters: `runs/lora_e_hidden/`, `runs/lora_e_shown/`
- Evals: `runs/eval_e_hidden.json`, `runs/eval_e_shown.json`

---

## Artifacts
- Consumer + harness: `ergon/learner/greedy/{serializers,sources,build_corpus,train_greedy,eval_greedy}.py`
- Corpus: `ergon/learner/greedy/corpus/{train_v1,gold_eval_v1}.jsonl` + `manifest_v1.json`
- Adapters: `ergon/learner/greedy/runs/{lora_v1, lora_v1_shuf}/`
- Eval: `ergon/learner/greedy/runs/eval_results_v1.json`

— Ergon, 2026-06-03
