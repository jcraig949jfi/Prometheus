# Cycle 049 — RETROSPECTIVE AUDIT of cycles 001-048: findings

Prereg: `CYCLE049_RETROSPECTIVE_PREREG.md`, committed `aac126e0` before any cycle file
was re-read for content. Three predictions and a null outcome were fixed in advance.

## Verdict on the pre-registered predictions

| # | prediction | outcome |
|---|---|---|
| 1 | `O-PROMISE` count >= 5 | **FALSIFIED — 4** |
| 2 | at least one NEW `E-INFER` | **HELD — and it is the loop's oldest finding** |
| 3 | arsenal red counts do not reconcile | *pending suite* |

Prediction 1 is falsified narrowly and I am reporting it as falsified rather than
reclassifying the `O-DANGLE` below to reach five. Two of the four also come from a single
charter clause; counted as one deviation it would be three.

## E-1 (`E-INFER`) — the loader claim was a wrong-population error

**Eighteen cycles said "the loader throws away every row." That is false.**

Measured across all seven prepass ledgers rather than the one that prompted it:

```
FLAT form  {"uid","rep",...}   5 files  1,852 rows   loader correct, accepts rep-1 exactly
KEY  form  {"key":[rep,uid]}   2 files  1,604 rows   loader accepts ZERO
```

The loader was broken for **one producer's wire format**, never in general. I took a
measurement on `campaign/p1_prepass.jsonl` and quoted it as a property of the consumer —
the fourth instance of `feedback_wrong_population_statistics`, committed by the role that
files that trap against everyone else.

**The mis-framing hid the hazard.** Two further defects sat behind the same 100% drop:
count-family prose routed by a **filename prefix**, and a gold screen sitting **downstream
of the rep filter** so it inspected none of the 1,604 KEY-form rows. The "obvious two-field
fix" I escalated for eighteen cycles would, applied alone, have shipped raw count-family
prose into a live arm. **The broken loader was accidentally acting as the firewall.**

Fixed this cycle (`c6736671`) now that #221 permits it: 0 -> 625 accepted, 0 shipping raw
prose, FLAT ledgers bit-for-bit unchanged, ergon suite 163 passed.

## O-1 — Band H was never built and never withdrawn

`LOOP_CHARTER.md` Track 2: *"R0→R12, then Band H (H1, H2), then restart at R0."*
R0-R12 completed at cycle 021 (`b08fa6db`). **Band H is never mentioned again in 48 cycles.**
Band H is not a minor tail: canon §6 calls it *"James's thesis, formalized and falsifiable"*
(H1 reflective modeling, H2 failure-landscape navigation). The charter explicitly allowed
theory to substitute for building in the upper bands, so non-measurability did not block it.

## O-2 — the second pass restarted at R3, not R0

Charter says restart at R0. Cycle 022 opened the second pass at **R3**. Silent deviation.

## O-3 — the R0 baseline lane was promised and never wired

HITL #2 (cycle 001): *"should the R0 retrieval circuit become a permanent baseline lane in
the grading oracle? My stand: yes ... will wire it in a later cycle unless you object."*
`harmonia/services/grading_oracle.py` contains no reference to `r0_pattern` or any retrieval
baseline. Never done, and — the actual fault — **never withdrawn** when the read-only
constraint made it impossible. Silence is not a withdrawal.

## O-4 — the Lane A/B reading experiment was pre-registered and never run

Pre-registered cycle 041 (`LANE_AB_READING_EXPERIMENT.md`), queued in the 20% at cycle 045,
never executed through 048. The note still contains no result section.

## O-DANGLE — egglog was installed on a leverage claim and never consumed

HITL #5: *"propose adding the `egglog` package ... real leverage on rule composition. Will
proceed unless you object."* `egglog` **is installed**. It is referenced by exactly one file
in the repo — `techne/loop/egglog_saturation_demo.py` — and by **no circuit, no test, no
module**. A dependency taken on a stated leverage claim that nothing ever consumed.

**This bears directly on HITL #242.** I asked James to approve installing four more
dependencies. My own record shows the last one I installed on a leverage argument was never
used. That weakens my #242 ask and should be stated alongside it, not buried.

## A near-miss inside the audit itself — the proxy trap, fourth instance

I nearly filed *"`tensor_train.py` violates Standing Order #1 — it imports only numpy"* from
a grep of **top-level imports**. It wraps quimb through a lazy import inside `_mps`. I had
used top-level imports as a **proxy** for "does this wrap the library".

That is the same trap as cycles 043 and 045 (guard-on-a-proxy), and the count is now four
including the `ledger_id`-prefix proxy found in ergon's code this cycle. The fourth instance
being in **another role's code** is the useful part: **this trap is not idiosyncratic to me.**
The prereg's self-guard — *every finding must diff against a checkable artifact* — is what
caught it, and it is the only reason this file does not contain a false finding.

## What did NOT reproduce as an error

- `quimb`/`tntorch`: cycle 001 planned both; the wrap uses quimb, tntorch was never needed.
  Plan narrowed by implementation, not an omission.
- Cycle 014's rung mislabelling was **self-caught and fully crosswalked** at the time
  (`RUNG_LABEL_CORRECTION.md`). The audit adds nothing to it.
- Cycle 048's 4.481e-10 catalog measurement: re-checked, stands.

## The omission the audit could not check

**No cycle records the command that produced its "arsenal red" number.** 48 cycles report
counts (28/29/30) with no reproduction line, so prediction 3 required re-deriving the scope
from scratch. Any number a later cycle diffs against is only as good as an unrecorded
invocation. **Standing fix: every reported count ships its command.**

*— Techne, cycle 049.*
