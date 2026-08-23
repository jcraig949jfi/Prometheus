# Cognitive Ceiling v0 — Executable Experimental Spec (Build 1)

> **RECONSTRUCTED 2026-08-22.** The original was pre-registered 2026-08-21 and
> hashed into every run manifest. It was destroyed in the working-tree loss (see
> `RECOVERY.md`) and **no hash of it survives** — the manifests carrying
> `spec_md_sha256_16` lived in the deleted run directories.
>
> This file is reconstructed from the session transcript. Its falsifiers were
> quoted verbatim in progress reports at the time they were set and before the
> corresponding results existed, which is the only attestation available. That is
> weaker than a hash and I will not describe it as equivalent. **Build 1 and
> Build 2 results should be reported as exploratory-with-attestation, not as
> cryptographically pre-registered.**
>
> Nothing here has been edited to fit results. Where a later iteration overturned
> something, the original text stands and the change is recorded in
> `SPEC_BUILD2.md` or `ITERATION_LOG.md`, never by rewriting this file.

## 0. Question

Can a bounded, FROZEN reasoner acquire usable structure it did not initially
have, by interacting with an external environment and accumulating
machine-readable artifacts — and does that competence survive destruction of the
model's context?

## 1. Alien Universe v0 — "Word/Sensor universe"

Hidden ground truth, evaluator only:

- Hidden state space `S = Z_m^k`. Shipped configuration: m=3, k=3, so |S| = 27.
- n = 4 primitive actions. Family `F_T`: each action is a translation
  `x -> (x + b_a) mod m`, with the shifts resampled until they generate the whole
  space. Consequence, never disclosed: the action monoid is a 27-element
  commutative group, so every action word equals one of 27 elements, actions
  commute, each has order dividing m, and relations `A_i A_j == A_k` are common.
  These relations are the discoverable structure and are never named.
- r = 4 entry tags `K0..K3` mapping to fixed hidden states.
- Sensor `sigma : S -> Q`, |Q| = 4, a near-balanced random surjection. LOSSY:
  ~7 states share a symbol, so one readout never determines the state and
  distinguishing suffixes are required.

Reasoner-facing API, the only channel:

```
RUN <tag> <a1 ... aL>      L <= 6
  -> trace of L+1 symbols
  cost: 1 interaction
```

Identifiers are `A#`, `K#`, `q#`. No word naming the hidden family may appear in
any rendered prompt; a leakage test enforces this against a banned vocabulary and
against the universe's own hidden parameters.

## 2. Scored task

A fixed held-out pool of 40 queries per universe, `(tag, word)` with
`|word|` in [8, 12] — strictly longer than the exploration cap of 6, so no query
can ever have been executed. Answer: the final sensor symbol. Chance 25%.
Evaluation is interaction-free; the eval view raises if anything tries to probe.
No feedback on eval answers is ever returned to any arm.

## 3. Arms

Every arm gets the SAME interaction budget per round and the SAME number of
rounds. Every LLM arm gets the same number of LLM calls per round and the same
max_tokens. The model is identical and frozen in all LLM arms.

- **P0** fresh frozen reasoner; nothing persists between rounds.
- **P1** frozen reasoner + RAW HISTORY; the verbatim interaction log persists.
- **P2** frozen reasoner + SUBSTRATE: tested rewrite rules (REL), derived
  operators (OP), memoised outcomes (OBS), one bounded note. The raw log does not
  persist. Rule tests cost interactions from the same budget.
- **P3a** random / majority-class reference.
- **P3b** algorithmic baseline given the same interaction count.
- **P3c** the substrate machinery driven by a NON-MODEL proposer at equal budget.
  The critical control for "does the reasoner contribute anything, or is the
  substrate just an algorithm?"

## 4. Readouts

P2 has two, both logged: **P2-llm** (the model answers with artifacts in context,
apples-to-apples with P0/P1) and **P2-sub** (the deterministic substrate predictor
answers, no model involved — the artifact-only ceiling).

## 5. Model amnesia

Every round begins with a FRESH model instance and an empty conversation.
A round is `EVAL_PRE -> explore -> persist -> EVAL_POST`, so `EVAL_PRE(r)` versus
`EVAL_POST(r-1)` measures exactly what survived the wipe.

## 6. Verification: stupid verifiers only

A proposed rule `lhs == rhs` is tested by the environment: for several
`(tag, suffix)` contexts, compare `sigma(run(tag, lhs+suffix))` against
`sigma(run(tag, rhs+suffix))`. All equal -> provisional PASS; any mismatch ->
permanent REJECT. This is a Myhill-Nerode style probe and requires no
understanding of the claim. Surviving rules are re-probed with fresh contexts on
later rounds; a rule that later fails is demoted. Environmental selection, never
model self-grading.

## 7. Metrics

Accuracy on held-out queries; accuracy by word length; interactions consumed; LLM
calls; tokens; cost; artifact counts and bytes; rule proposal count and pass
rate; normalisation coverage; amnesia deltas.

Epistemic-gain instance, computable, all four links required: (a) an interaction
whose observed trace contradicted the store's own prediction; (b) a rule proposed
that round which passed environmental test and persisted; (c) that rule changing
the normaliser's output on at least one held-out query; (d) that query going
wrong->right against a counterfactual store with the rule removed AND its
dependent memo purged.

## 8. Ablations

A1 no-persistence (= P0). A2 memo-only. A3 rules-only. A4 artifact shuffle
(universe X's store against universe Y's queries). A5 top-k deletion, compared
against deleting the same number of random and least-used rules, plus restore.
A6 fresh-model transfer (every round boundary). A7 wrong artifacts injected
untested. A8 random search.

## 9. PRE-REGISTERED FALSIFIERS

Declare NO EVIDENCE for cumulative system-level epistemic gain if ANY of:

- **F1** P2-llm final accuracy does not exceed P1 by >= 10 points, paired over seeds.
- **F2** P2 accuracy at EVAL_PRE of the final round is not >= its EVAL_POST of the
  previous round minus 5 points — competence does not survive amnesia.
- **F3** P3c matches P2-sub within 10 points at equal interaction budget. Then the
  substrate is an algorithm and the reasoner is decorative. This falsifies "the
  frozen reasoner contributes", not "the system accumulates"; both verdicts are
  reported separately.
- **F4** Top-k deletion does not reduce accuracy, or restoration does not recover it.
- **F5** Artifact shuffle does NOT hurt — artifacts carry no universe-specific content.
- **F6** Gains vanish under compute-matched comparison.
- **F7** The algorithmic baseline at equal budget >= P2-sub.
  *(Superseded in Build 2: demoted from falsifier to branch condition. Original
  text retained.)*
- **F8** Any leakage test fails.

No post-hoc redefinition of success. A clean negative is the deliverable.

## 10. Expected readings, recorded before running

P0 ~30-40%; P1 ~35-50%; P2-llm unknown, and I predict the model is bad at
hand-applying rewrite rules over long words; P2-sub 50-90% if the rule set
covers, else ~majority; P3b high, 60-100%; P3c the crux, genuinely unknown.
I expect F7 to fire and F3 to be close. Running anyway, because the P2-sub
amnesia result and the A5 causal test are worth having even then.
