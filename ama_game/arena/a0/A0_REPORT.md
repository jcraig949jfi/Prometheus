# A0 baseline — result

**Run:** 2026-08-25 · protocol v0.1-alpha · condition A · n = 30
**Freeze:** `FREEZE_A0.json`, re-verified after the run — no drift, `graph.jsonl`
still the empty-file hash. 24 tracked files, all four role prompts' invariant
blocks, budget config, and both eval-set trees hashed before the first seat ran.
**Seats:** 30 fresh-context Opus 5 assessors, one per claim, homogeneous.
**Eval set:** `A0_EVAL`, seed 88041199, 30 distinct propositions, disjoint by
proposition from the MDE pilot set.

---

## 1. Primary, exactly as preregistered

| | |
|---|---|
| **EVC** (expected verifier cost to correct disposition) | **6.37** (SE 1.74) |
| accuracy | **80%** (24/30) |
| cost rule | correct → verifier calls; incorrect → budget cap (25) |
| unit of analysis | the claim, n = 30 |

This number stands as the A0 baseline. Nothing below revises it.

## 2. Where the errors are

Every one of the six errors is in a single class.

```
FALSE_BUT_HARD_WITHIN_BUDGET   6/6   -> FALSE
FALSE_WITH_WITNESS             6/6   -> FALSE
TRUE_BUT_INVALID_ARGUMENT      6/6   -> TRUE_BUT_INVALID_ARGUMENT
TRUE_VALID_ARGUMENT            6/6   -> TRUE
UNRESOLVED_WITHIN_BUDGET       0/6   -> FALSE x4, TRUE_BUT_INVALID_ARGUMENT x2
```

Post-hoc, and labelled as such: on the 24 items from the four well-posed
classes, **accuracy is 100% and EVC is 1.71** (SE 0.16). Verifier calls on those
24: eleven 1s, ten 2s, two 3s, one 4.

## 3. The baseline is at ceiling, and that is the headline

The user's own criterion: a near-perfect baseline is a problem, because it
leaves no headroom for D.

That is the situation. On every class that measures what it was built to
measure, thirty fresh assessors were **unanimously correct at a median of two
verifier calls**. There is no room for graph state to improve a disposition that
is already right and already costs two calls.

And the 20% error is not difficulty — it is a broken class. In all six
`UNRESOLVED` failures the assessor got the mathematics right:

```
A0_EVAL-0004  truth TRUE   said TRUE_BUT_INVALID_ARGUMENT   2 calls
A0_EVAL-0009  truth FALSE  said FALSE                       2 calls
A0_EVAL-0014  truth FALSE  said FALSE                       4 calls
A0_EVAL-0019  truth FALSE  said FALSE                       1 call
A0_EVAL-0024  truth TRUE   said TRUE_BUT_INVALID_ARGUMENT   2 calls
A0_EVAL-0029  truth FALSE  said FALSE                       3 calls
```

Four said FALSE and the sealed truth was FALSE. Two said
`TRUE_BUT_INVALID_ARGUMENT` on items that are in fact TRUE with an INCOMPLETE
argument — the more informative answer, scored as an error.

The scorer's own guard fired: *every overclaim was right*, 4/4. That is the
signature of a mislabelled class, not a lucky assessor. The cause is documented
in `FINDING_budget_not_enforced.md`: the 200,000 search budget lives in a prompt
and nothing enforces it. Seats swept to 372,001, 504,120, 579,714 — and said so
in their own records. The generator's supposed enumeration advantage was
requested, never held.

So the honest reading of A0 is: **substantively 30/30**. The preregistered 80%
reflects one class that cannot be scored as designed.

## 4. What did not go wrong

Worth stating, because these were the failure modes the design most feared:

- **False accusations: 0/14.** Not one true claim was killed.
- **Invalid falsifiers: 0/16.** Every submitted witness survived independent
  re-execution against the claim's own domain and predicate.
- **`TRUE_BUT_INVALID_ARGUMENT` is not hard: 6/6.** Nobody spotted a planted
  defect and then used it to kill the true conclusion (0), and nobody missed the
  defect and waved the claim through (0). The compositional mutations were found
  and correctly localised — several seats named the exact step, including the
  CRT-abuse plant at s4 and the converse-abuse plant at s5.

## 5. MDE, computed and archived before scoring

From an independent 10-item pilot run, resampled with a permutation test (the
cost distribution is a point mass on the cap plus a small cluster of cheap
correct answers; normal theory does not apply):

```
  n/arm    lever                       dEVC   power
     30    D fixes 100% of A's errors   4.70    79%
     30    D fixes  75% of A's errors   3.72    44%
     60    D fixes 100% of A's errors   4.80   100%
     60    D fixes  75% of A's errors   3.46    68%
    120    D fixes  75% of A's errors   3.55    97%
```

**At n = 30 per arm, no simulated effect reaches 80% power.** The A0-vs-D
comparison at this size is UNPOWERED. n = 60 detects only a near-total error
fix; n = 120 detects a 75% fix.

A structural note that matters more than the numbers: cost reduction alone is
nearly undetectable. Cutting verifier cost 60% on already-correct answers moves
EVC by 0.28 and reaches 5% power. Under the preregistered cost rule, **D can only
win by being right more often, not by being cheaper** — because a wrong answer
costs 25 and a right one costs about 2. That follows from the rule chosen before
data existed, and it is better known now than discovered during the D analysis.

## 6. Consequences for the navigation experiment

Three blockers, all measured rather than argued:

1. **No headroom.** A0 is at ceiling on every well-posed class. D cannot beat
   100% accuracy at 1.71 calls. The item pool must be made harder before
   B/C/D are worth running.
2. **Underpowered at the planned n.** Even with headroom, 30/arm detects
   nothing. 60 is the floor, 120 is honest.
3. **One class of five is unscoreable.** `UNRESOLVED_WITHIN_BUDGET` needs an
   enforced verifier before it measures calibration rather than compliance.

## 7. What was deliberately not done

- The `UNRESOLVED` class was **not** patched, and those six items were **not**
  rescored. A0 was frozen before the run; adjusting a scoring rule after seeing
  which items it punishes is the exact manoeuvre the preregistration exists to
  prevent. The defect is reported, not corrected retroactively.
- The transfer-set MI confound remains **UNPOWERED** and was not "fixed" by
  enlarging those sets, per the instruction not to optimise the alpha around
  satisfying every diagnostic.
- No epoch runner, no graph, no navigation machinery was built.

## 8. Known weakness in the instrument itself

Verifier-call counts are self-reported and the seats visibly disagreed about
what counts. Several reported re-running an identical script purely to persist
a log; several counted a JSON-parse check, several disclosed it separately and
declined to count it. The reported EVC therefore carries an unmeasured
counting-convention variance on top of its sampling error. A metered verifier
fixes the budget-enforcement problem and this one in the same stroke.
