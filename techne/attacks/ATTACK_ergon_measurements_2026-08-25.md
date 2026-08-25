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
