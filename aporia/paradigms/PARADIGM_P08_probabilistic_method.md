# PARADIGM P08 — Probabilistic Method (worked example + decision tree + code skeleton)

Aporia P84, 2026-08-21. Source: taxonomy P08; no DR grounding in BACKCORPUS
(checked, not re-fired). Consumer: Learner corpus type C. Emitted to
paradigm_trees.jsonl.

**The move**: prove existence by showing a random construction succeeds with
positive probability (verb: RANDOMIZE-AND-COUNT; payoff verb:
PROVE-EXISTENCE-WITHOUT-CONSTRUCTING — though the example shows sampling often
constructs anyway).

## 1. Worked example — EXECUTED (`paradigm_p08_worked_example.py`)

Three legs, raw beside derived throughout:

- **A. Derived expectation.** E[# monochromatic K4 in a uniform 2-colored K10]
  = C(10,4)·2^(1−6) = **6.5625**, from linearity, exact integer arithmetic.
- **B. Monte Carlo match.** 20,000 sampled colorings: empirical mean **6.5947**
  (SE 0.0325, z = 0.99) with the full raw count distribution printed — the
  derived and sampled instruments agree.
- **C. Existence made constructive.** For (K8, K6-freeness) the derived
  expectation is 28/2¹⁵ ≈ 0.00085 < 1, so the union bound proves colorings
  with no monochromatic K6 EXIST; sampling found one on **draw 1** and it was
  verified exhaustively over all 28 six-subsets (0 monochromatic). The witness
  coloring is committed in the results file — the "non-constructive" method,
  run on a machine, constructs.

Verdict: **METHOD-DEMONSTRATED**.

## 2. Decision tree

- Q1: Is the goal an EXISTENCE statement (an object with property P exists)?
  — NO: the method proves existence; for counting/optimality see its second-
  moment refinements or exit.
- Q1 YES — Q2: Can you compute or bound E[# violations] (or P(success)) under
  a NATURAL random construction? — NO: without a computable first moment there
  is nothing to argue from; redesign the random model first.
- Q2 YES — Q3: Is E[# violations] < 1 (or P(success) > 0 via LLL when
  dependencies are local)? — NO: the first moment fails; escalate to second
  moment / alteration / LLL before abandoning.
- Q3 YES — EXECUTE: existence is proven; THEN attempt to sample a witness —
  if found, verify it EXHAUSTIVELY and commit it (a verified witness upgrades
  the proof to a certificate); if sampling fails despite E < 1, the model and
  the sampler disagree — instrument-first.
- Cross-gate (always): Monte Carlo the derived expectation; a z > 3 mismatch
  means the derivation or the sampler is wrong BEFORE any existence claim.

## 3. Code skeleton

```python
def probabilistic_attack(sample, count_violations, E_derived, trials=20_000):
    """P08 template. The derived moment and the sampler must agree BEFORE
    the existence conclusion is trusted; a found witness is verified
    exhaustively, never trusted from the sampler."""
    counts = [count_violations(sample()) for _ in range(trials)]
    mc, se = np.mean(counts), np.std(counts, ddof=1) / np.sqrt(trials)
    assert abs(mc - E_derived) < 3 * se, f"derivation vs sampler: {mc} vs {E_derived}"
    if E_derived < 1:                      # union bound: existence proven
        for _ in range(1000):
            w = sample()
            if count_violations(w) == 0:
                assert count_violations(w) == 0   # independent re-verification
                return ("EXISTS", w)
        return ("EXISTS", None)            # proven but unsampled — report both
    return ("FIRST-MOMENT-INSUFFICIENT", None)
```

## 4. Catalog assignment

Primary: the channel's own NULL BATTERY (permutation nulls ARE this paradigm
defensively — feedback_permutation_null); CAT-MATH-0057/0058 (circle-method
heuristics are expectation arguments), 0479/0483 (race densities are
probabilistic statements). Secondary: 0062/0175 (ensemble statistics), 0165
(moment methods). Anti-assignment: 0137 (deterministic congruence battery),
0129/0154 (finite exact recursions — nothing random).

## Provenance and honesty

All three legs are settled combinatorics; the transferable content is the
mandatory derivation-vs-sampler cross-gate (leg B) and the witness-upgrade
discipline (leg C: sample, then verify exhaustively, then commit). The
committed witness makes the classically "non-constructive" method reproducible
here: anyone can re-verify the coloring without re-sampling.
