# Hephaestus calibration ledger (kept because it is unflattering)

Currency: 2026-09-11. One line per wrong call this seat made, with the
correction and where the evidence is. Base role s2: "keep a calibration
ledger of your own past wrong calls".

Conflicts of interest declared: this seat authored the closure gauntlet
(hephaestus/src/closure_test.py), the frozen basis A2-GENERIC-v1, the dev
harness for MINT-0001, and the specimen 3 preregistration and runner. Any
reading of the gauntlet's own output by this seat is a same-author reading.

- 2026-04 to 2026-06: "the forge produces ~1,960 novel reasoning tools".
  Wrong: ~5 mechanisms in costumes (ROLE.md s2). Evidence: behavioural NCD
  and mechanism knockout.
- 2026-05: "causal_trace is R5". Wrong: keyword match, honest tier R1,
  actively -6pp on R5 (ROLE.md s4, s6).
- 2026-06-24: ROLE.md s0 quoted "0.725 bits MI" as a forge-ledger number.
  Wrong: computed over 314,971 substrate kills in prometheus_math, unrelated
  (ROLE.md ERRATA 2026-09-01, item 1).
- 2026-06-24: ROLE.md s6 tier profile "R5 0 / R6 ~7". Wrong: the instrument
  reads R5 18.75 / R6 38.1 (agents/hephaestus/ablation/knockout_2026-08-20.json).
- 2026-06-24: "12 models converge". Overstated: 12 attempted, 5 produced
  usable tools (ERRATA item 4).
- 2026-09-01: MINT-0001 marked READY-FOR-DEEP-MINT on executed evidence and
  a Master Smith session was run. Operator ruling (Addendum 1) reclassified
  it a Level-1 composition plus a representation adapter problem: the
  semantic-injection question ("if perfect semantic state were injected,
  what is still missing?") had not been asked. Now mandatory before TRIAGE
  exit.
- 2026-09-01: specimen 3 runner committed UNRUN with a comparator that
  raises TypeError on the first sort (S and V signatures compared). Found
  at first execution 2026-09-11; corrected as a filter that leaves the
  preregistered canonical order unchanged (journal 2026-09-11). Lesson: a
  runner committed unrun has not been smoke-tested on a shape it will meet;
  run it on a one-target budget before freezing.
- 2026-06-24 to 2026-09-11: ROLE.md carried "running on M3 / GANDALF" as a
  seat property. The seat is host-independent; the host is a receipt
  field (annotation in ROLE.md s1).
- 2026-09-01 (found 2026-09-11): the closure gauntlet, FROZEN at 1f4c5ca72
  as "the standard Forge test", hard-wired its coerced comparison to
  bool(). Correct for the two boolean-valued specimens it had been run
  on; degenerate for any vector-valued target, where every non-empty
  output casts to True: every vector program would have matched the
  target on the six probes AND on the 1,290-point exhaustive domain, so
  the gauntlet would have reported thousands of "mechanism-bearing"
  witnesses in A0 for every LOST target and classified all of specimen 3
  SEARCH_ROUTING. A green instrument for the wrong reason, on the very
  specimen chosen as the OPERATOR positive control. Caught only because
  the run was slow enough to read the code before reading a number.
  Correction: spec-declared COERCE, default unchanged (boolean specs
  re-checked byte-identical). Lessons: (1) an instrument frozen after two
  specimens of one value type has not been shown to work on a second
  value type; freezing is not validation; (2) the positive control must
  be run BEFORE the instrument is declared standard, not as specimen 3;
  (3) base rule "verify the property, never the label": "verify_exhaustive
  = True" was a label.
- 2026-09-01 (found 2026-09-11): the same enumerator's "at least one
  argument from the previous layer" test was a linear scan over a list of
  closures inside a product over pool x pool, uncounted by the budget; on
  TINYPROG pools one target ran more than 20 minutes (907 s CPU) without
  finishing. Corrected with a depth tag (O(1), identical enumeration).
  The "300,000 evaluation budget" bounded evaluations, never runtime; a
  budget that does not bound the thing you wait for is not the bound you
  think it is.
