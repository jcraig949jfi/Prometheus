# ATTACK — Ergon's four measurement implementations, 2026-08-25

**Techne.** Read-only constraint lifted (HITL #221). Four measurement implementations landed the
same day, authored by the party they certify, alongside a same-day record of three prior checks
passing over a 400/400 arm label and a repair carrying three further defects. Everything here is
treated as guilty until a constructed world makes it speak.

**Method, per the mandate and my own standing rule (HITL #129/#133):** *before trusting an
instrument, construct the input on which it MUST report the answer you do not want.* A check I
cannot make fail is itself a finding.

**Baseline verified before attacking, not assumed:**
- `python -m pytest ergon/probe/tests/ -q` → **220 passed** in 21.15 s.
- Ledger `ergon/probe/ledgers/adversarial_leakage/leakage_gate.json` reads `verdict: PASS`,
  `positive_controls_pass: true`, `n_tasks: 200`.

---

## 0. A correction to the brief, before anything else

The brief states that observed balanced accuracy sits below the permutation-null mean *"on all
twelve live pairs."* **It is 9 of 12.** The three `H` pairs sit marginally ABOVE the null mean
(+0.0005, +0.0120, +0.0222). This matters, because the shape of the residual is the evidence:

- targets involving **R** (`arm6`, `cell4`, `R`) are below null by **−0.011 to −0.066**
- targets on **H** alone sit at the null to within ±0.022

So whatever produces the offset is **specific to the retrieval slot and absent from the hint
slot**. A hypothesis that predicts a uniform offset is already falsified by the committed ledger.

---

## 1. PRE-REGISTRATION (committed before any attack was run)

### Attack 1+2 merged — the null offset and the exchangeability, which are one question

Ergon's hypothesis for the below-null offset is task structure reaching the classifier through the
sparsity slot under grouped CV. **My competing hypothesis is that the offset is a symptom and not
the disease.** Two structural properties of the gate, both readable from source before running
anything:

**(a) THE VERDICT IS ONE-SIDED.** `run_gate` computes
`FAIL-LEAK if obs > p95 else UNDECIDED if obs > p90 else PASS`. There is no branch testing the
lower tail. But balanced accuracy *below* chance carries the same information as balanced accuracy
above it — an adversary simply inverts the prediction. For a gate whose stated question is whether
assignment is *recoverable*, `|obs − null|` is the quantity, not `obs − null`. **A systematically
below-null observation is scored PASS with no examination**, and 9 of 12 live pairs are exactly
that.

**(b) `GroupKFold` BY TASK ANSWERS A DIFFERENT QUESTION THAN THE THREAT MODEL.** Grouping by task
was introduced for a good reason — a row-level split let 14 memorised constants produce a positive
that was later retracted. But it changes the estimand. Grouped CV measures *"is arm recoverable
from a packet belonging to a task never seen in training?"* **The solver always knows its own
task.** The threat is *"is arm recoverable GIVEN the task?"* — and a leak that is task-conditional
is invisible to this design **by construction**, not by bad luck.

### Predictions

1. **A perfect task-conditional leak is reported PASS by the unmodified gate.** Confidence
   **high**; **D0**. Mechanism stated before running: plant a marker whose arm→token map ROTATES
   by task index. Given the task the marker determines the arm exactly; task-blind training across
   held-out tasks learns nothing consistent. *Opposite:* if the gate flags it, grouped CV leaks
   task identity into the classifier and the design is different from what I read.
2. **A task-aware adversary recovers arm at ≥ 0.95 balanced accuracy on that same world.**
   Confidence **high**; **D1**. This is what makes prediction 1 a defect rather than a curiosity:
   the leak must be demonstrably real, not merely undetected noise. *Opposite:* if it cannot be
   recovered, I have planted nothing and the whole attack collapses.
3. **On LIVE packets, within-task-normalised features recover arm ABOVE the within-task
   permutation null.** Confidence **moderate**; **D2**. This is the load-bearing one: it asks
   whether the live data actually has something in the blind spot, not merely whether a blind spot
   exists. *Opposite:* a null result here means the gate's blind spot is empty on this manifest,
   the PASS survives on its merits, and the finding narrows to the scope statement only.
4. **The one-sidedness is a pure code fact: no branch in `run_gate` tests the lower tail.**
   Confidence **high**; **D1**. Decidable by reading, confirmed by executing a below-null world.
5. **`blocks.merge_reading` returns `n_pooled=None` under FORBIDDEN, and no path in `campaign.py`
   can clear the R13 floor on a forbidden merge.** Confidence **moderate**; **D2**. *Opposite:* a
   path that treats `None` as 0, or that reads `pooled_point_estimate` without checking
   `pooling`, is a live defect.

### Committed in advance

- Every adversary is **imported from Ergon's module**, never reimplemented — reimplementing them
  would fork the estimator and is the ATK-014 shape I am here to attack.
- If prediction 3 comes back null, **I report the gate's scope defect and explicitly say the live
  PASS survives**, rather than letting a structural criticism imply a substantive one.

*— pre-registration ends. Everything below was written after running.*

---

## 2. RESULT — three defects, one clean pass, and one of my own predictions falsified

**Reproduce:** `PYTHONPATH=. python techne/attacks/probe_ergon_leakage_gate_2026-08-25.py`
(exit 1 = defect present). Rows: `techne/attacks/ledgers/`.

### F1 — THE COMMITTED LEDGER DOES NOT REPRODUCE, AND ITS PROVENANCE STAMP STILL MATCHES

`ergon/probe/ledgers/adversarial_leakage/leakage_gate.json` carries `verdict: PASS` and
`manifest_sha16: e6b1e001bf79e3ef`. The current manifest hashes to **the same value**. Not one of
its six LIVE observed figures reproduces:

```
pair                        committed  recomputed
lexical|arm6                   0.1275      0.1667
structural|arm6                0.1542      0.1667
distributional|arm6            0.1550      0.1667
lexical|R                      0.2667      0.3333
structural|R                   0.3125      0.3333
distributional|R               0.3133      0.3333
```

INVARIANT 7 re-keyed the slug on the task between the ledger being written and now. That changed
the gate's inputs completely — and **`manifest_sha16` covers the task manifest, not the packet
renderer, so it is invariant to exactly the change that invalidated the artifact.** A committed
verdict describes packets that no longer exist, and every provenance field on it still checks out.

This is a new defect class: **ATK-016, provenance stamp blind to the transform.** It is the
mirror of ATK-015 — there the rows were destroyed and the verdict survived; here the rows are
intact and the *transform between them and the verdict* changed silently.

**Patched:** the report now carries `renderer_sha16`, a hash of `ergon/probe/packet_render.py`.

### F2 — THE GATE IS NOW EXACTLY VACUOUS AND WOULD STILL HAVE WRITTEN `PASS`

Measured on the current packets, all 200 tasks:

```
tasks                       200
tasks_with_constant_input   200      (fraction 1.0)
distinct_texts              138  of  1200
verdict_tally               {"PASS": 12}
example pair lexical|arm6:  observed 0.1667   null_mean 0.1667
                            null_p05 0.1667   null_p95 0.1667   null_max 0.1667
```

Every task yields **one** distinct blanked payload across all six arms. The classifier is handed
six identical feature rows with six different labels; observed balanced accuracy is exactly
`1/n_classes`; **the permutation null has zero variance — p05, p90, p95 and max are all the same
number.** Twelve `PASS` verdicts from a null that cannot vary.

Ergon *names* this in `packet_invariants.check_invariant_7`'s docstring — *"the adversarial gate
is now VACUOUS on these packets ... a vacuous reading reported as a passing one is its own defect
class"* — which is exactly right, and **nothing enforced it.** The prose knew; the code did not.
That is the same shape as my own finding #21 two cycles ago, in someone else's file.

This is the generalization already written into ATK-013: *a gate whose input field is absent must
RAISE, never return a passing value.* Here the field is present and **constant**, which is the
same defect wearing different clothes. Registered as **ATK-017**.

**Patched:** `input_vacuity()` measures it, and `main()` now returns a `VACUOUS` verdict **before**
the pass/fail ladder, stating that this is the correct consequence of INV 7 closing the channel
and that the gate survives only as a regression detector.

### F3 — THE VERDICT WAS ONE-SIDED, AND THE LIVE WORLD'S SIGNATURE MATCHED A KNOWN PLANTED LEAK

`FAIL-LEAK if obs > p95 else UNDECIDED if obs > p90 else PASS`. No branch tested the lower tail.
But balanced accuracy **below** chance carries the same information as above it — an adversary
inverts the prediction — so for a gate asking whether assignment is *recoverable*, the quantity is
`|obs − null|`.

This is not hypothetical, and it answers the question the brief actually asked. Compare the
committed LIVE world against this file's **own planted-leak control**:

```
                          observed   null_mean   delta     verdict
LIVE lexical|arm6           0.1275     0.1677   -0.0402     PASS
SENSITIVITY_band_plus3      0.1292     0.1647   -0.0355     PASS      <- a KNOWN planted leak
```

They are quantitatively indistinguishable. The `+3` band is the leak Ergon's own sensitivity sweep
documents the gate as **unable to detect**, and the live world sat at the same magnitude, on the
same side, and was scored `PASS`.

**So the below-null offset was never a curiosity to be explained away — it was the leak.** The
arm-varying slug was real, INVARIANT 7 later removed it by a decidable byte comparison, and the
evidence had been sitting inside the gate's own numbers the whole time, on exactly the R-involving
targets, discarded by a one-sided verdict. Ergon's sparsity-slot hypothesis is unnecessary: the
offset is concentrated in R and absent from H, and it vanished to **exactly zero** the moment the
slug was re-keyed.

Registered as **ATK-018, one-sided gate on a two-sided question.**

**Patched, additively:** a new `FAIL-LEAK-INVERTED` verdict fires when `obs < p05`. It carries its
own name rather than reinterpreting the preregistered upper-tail thresholds, so Ergon's original
semantics are untouched and the change is reviewable on its own.

### F4 — THE MERGE RULE HOLDS. NO DEFECT.

Attack 4 found nothing, and I could not construct a world where it failed:

```
non-overlapping -> FORBIDDEN   n_pooled: None   pooled_point_estimate absent
missing leg     -> UNAVAILABLE n_pooled: None
overlapping     -> PERMITTED   n_pooled: 404    point 0.496
campaign.py: guard at line 819, its return at 836, the only read of merged["n_pooled"] at 837
```

The guard tests the **verdict**, not the number, and returns before `n_pooled` is ever read — so
the `TypeError` safety net is never even reached. The ordering is asserted on the source rather
than eyeballed. **This one is well built and I am saying so.**

### F5 — MY OWN D0 PREDICTION WAS FALSIFIED

I predicted a perfect **task-conditional** leak would be invisible to the gate, on the reasoning
that `GroupKFold` holds out whole tasks and a per-task rotating marker cannot generalise. I built
it: `LEAK_k` with `k = (arm_index + task_index) mod 6`, so the arm is a deterministic function of
(marker, task) and the map is a different permutation in every task. A task-aware decoder recovers
the arm at **1.0000** on 360 packets, so the leak is unambiguously real.

**The gate caught it.** `any_fail: true`, with H reaching 1.000 against a p95 of 0.548, and 0 of
12 pairs below null. The mechanism I missed: the blanked payloads are heavily duplicated across
tasks (138 distinct of 1,200), so held-out tasks share text with training tasks and the grouping
does not isolate them the way I assumed. **Scored FALSIFIED. The gate is stronger on this axis
than I predicted, and the design criticism I intended does not stand.**

### F6 — MY PATCH INTRODUCED A DEFECT, AND ERGON'S TESTS CAUGHT IT IN SECONDS

The first version of the vacuity patch left an unterminated string literal at line 445. Three
tests in `ergon/probe/tests/test_packet_leak_gate_fire.py` went red immediately with a
`SyntaxError` surfaced through an import. Fixed; **220 passed** again. Recorded because it is the
cleanest possible restatement of the standing lesson: mechanical errors announce themselves,
inferential ones do not. My F5 inference survived a cycle; my syntax error survived twenty
seconds.

---

## 3. PREDICTIONS SCORED

- **1 — FALSIFIED (D0).** See F5. The gate detected the task-conditional leak.
- **2 — CONFIRMED (D1).** Task-aware recovery 1.0000 on 360 packets; the planted leak was real.
- **3 — CONFIRMED-NULL, and reported as pre-committed.** Within-task-normalised features on live
  packets recover nothing: observed 0.1667 against a null of 0.1667 with zero variance. As
  written in the pre-registration, **I say plainly that the live PASS survives on its merits** —
  there is nothing in the blind spot because, post-INV-7, there is nothing at all. The finding
  is the artifact's staleness and the gate's silence about its own vacuity, not a hidden leak.
- **4 — CONFIRMED (D1).** One-sided, as a code fact and as an executed world.
- **5 — CONFIRMED (D2).** No path clears R13 on a forbidden merge.

## 4. WHAT I CHANGED IN ERGON'S CODE

All under HITL #221 (cross-role FIXES permitted; cross-role SCIENCE is not). Each is additive and
none reinterprets a preregistered threshold:

1. `renderer_sha16` in the report — provenance that can see the transform.
2. `input_vacuity()` + a `VACUOUS` verdict returned **before** the pass/fail ladder.
3. `FAIL-LEAK-INVERTED` on `obs < p05`, plus `signed_delta` and `abs_delta` on every pair.

**220 tests pass** after the change; `python ergon/probe/packet_invariants.py` still reports
`PASS — decidable invariants hold on every task`.

## 5. FOR ERGON — one thing I did not do, and one ruling I need

- **I did not regenerate your ledger.** `leakage_gate.json` on disk still reports the stale
  `PASS`. Overwriting a committed verdict of yours is science, not a fix, and #221 does not cover
  it. Re-run `python ergon/probe/adversarial_leakage.py` and it will now write `VACUOUS`.
- **The `FAIL-LEAK-INVERTED` threshold is preregistration-adjacent.** I gave it a distinct name
  precisely so it cannot silently change a `PASS` into a `FAIL` under your existing rule, but
  whether a below-null excursion should HALT P2 is your call, not mine.
