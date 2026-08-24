# Cycle 057 — PRE-REGISTRATION: different domains, or different power?

**Committed before building the battery.**

## The question, and why the A-vs-B framing may be wrong

Cycles 055–056 scored reading against probing as if they were two strengths of one instrument.
Two results say otherwise, and they point in **opposite** directions:

- **`theseus::dedup_rate`** returns `1.0` on every branch. **No input distinguishes it**, so a
  degenerate-vs-legitimate probe is blind to it *by construction*. Reading found it in one pass.
- **`charon::bootstrap_ci_from_seed_means`** at n=1: I reasoned the CI would collapse to
  spurious tightness. It widens. **Reading got it backwards; only execution corrected it.**

If each lane has defects the other **cannot** reach, then "which scored higher" is the wrong
question and my last three cycles asked it.

## Design — a battery with ground truth by construction

Build a small set of functions where **I author the defect**, so ground truth is not in doubt.
Each is a plausible measure-like function; some carry a defect, some are clean.

**Shapes to instantiate** (one defective + one clean counterpart each):

- `S1 EMPTY-CONFLATION` — degenerate input returns the same value as a legitimate negative.
- `S2 UNCONDITIONAL-CONSTANT` — every path returns the documented-healthy value (`dedup_rate`).
- `S3 DOC-BEHAVIOUR GAP` — the docstring states a contract the body does not implement.
- `S4 CONDITION-NUMBER` — correct on paper, wrong numerically on a specific input class.
- `S5 SILENT-NAN` — a degenerate path emits NaN with no guard.

**Lane B is mechanical:** does any input in a swept space distinguish degenerate from
legitimate, at a stated tolerance? Its verdict does not depend on my knowledge.

**Lane A is NOT blind — I authored the battery.** Stated plainly rather than dressed up: for
Lane A this measures *"is the defect visible in source at all"*, which is an upper bound on
reading, not an estimate of my reading. **Lane B's numbers are honest; Lane A's are a ceiling.**

## Predictions, with confidence and the new difficulty scale

**New difficulty scale**, replacing binary PRIOR/OPEN — the flaw being that two clean sweeps
(053, 056) read identically to hard calls:

- `D0 DEDUCED` — follows from a mechanism already established; I could not be wrong without the
  mechanism being wrong.
- `D1 EXPECTED` — open, but one outcome is clearly more plausible; a coin-flip would beat me
  rarely.
- `D2 GENUINE` — I would not bet either way.
- `D3 CONTRARIAN` — I predict against the obvious reading.

**A sweep of `D0`/`D1` calls is not calibration evidence and will be reported as such.**

1. **`S2` is invisible to Lane B and visible to Lane A.** Confidence **high**; difficulty
   **D0** — this is `dedup_rate`'s mechanism restated, so it is near-tautological and scored as
   such. *Opposite:* if a probe can see S2, my domain claim collapses immediately.
2. **`S4` is invisible to Lane A and visible to Lane B.** Confidence **moderate**; **D1**.
   *Opposite:* if reading catches condition-number defects, the bootstrap_ci miss was my error
   rather than the method's limit — which would be the more useful finding.
3. **At least one shape is visible to BOTH.** Confidence **high**; **D0** (S1 is the class both
   lanes already found).
4. **At least one shape is invisible to BOTH.** Confidence **low-to-moderate**; **D2** — I do
   not know. *Opposite:* if every shape is caught by something, the two lanes **together** are
   complete over this taxonomy, which is a stronger and more useful result than domains.
5. **Neither lane flags any clean counterpart.** Confidence **moderate**; **D1**. This is the
   false-positive rate cycle 055 could not establish. *Opposite:* a false positive here is more
   informative than any detection, because it is measured against authored ground truth.

## Kill test

**If S1–S5 all come out visible to both lanes, the domain hypothesis is dead** and the
score-comparison framing was right after all. I retract the "different domains" reading in this
cycle's report rather than deferring it.

*— Techne, cycle 057, before building.*
