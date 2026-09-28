# Cross-engine attribution assay, v2 after Review 1 (directive item 13) -- Archaeon, 2026-09-28

v1 (ASSAY_v1_SUPERSEDED.md) is kept unedited. Review 1 (review1/REVIEW_1.md, R1-5) showed that its BEE and NPE "material" columns
were not descent:
- BEE: copies whose SOURCE ADDRESS lay in the writer's region, stamped as taint (counter-example CX-5a, run on Bellerophon's own
  traced VM);
- NPE: positions whose final byte EQUALS the donor's, split by the executing code's location and provenance (CX-5e).

The validator certified both ("0 invalid"), because an adapter could write any `via` and count resolution switched off the tiling
check.

Fixes:
- A5 forbids source_address / value_match;
- A4 tiles count-resolution records;
- A16 ties infrastructure logs to infrastructure processes;
- the adapters now record what the preserved rows actually support.

Adapters: archaeon/attribution/assay.py. Output: assay/ASSAY.json (result_sha256 4b29dcc6ccb180f6...). Inputs are the same four
files as v1, fingerprinted in ASSAY.json.

## Result: descent is identifiable in ONE of the three engines' preserved records

| question | BEE r038751 | BEE r016299 | NPE T-003 (34) | Archaeon block 13 (53,185) |
|---|---|---|---|---|
| child material identified by descent | NO: written bytes carry no descent record (0% identified) | NO (99.5% of loci unidentified; only unwritten occupant bytes, by construction) | NO (T-003 records the executing code, and value equality at D positions) | YES (native per-byte taint) |
| producer != some material donor | not identifiable | not identifiable | not identifiable | 3.9% |
| majority donor != producer | not identifiable | not identifiable | not identifiable | 0.71% (375; host-written) |
| two or more donors | not identifiable | not identifiable | not identifiable | 3.3% |
| singular parent loses identified structure | not identifiable | not identifiable | not identifiable | 4.9% |
| someone other than the writer/donor EXECUTED (carrier, which IS recorded) | 176 births: partner-material code ran (codeprov foreign) | 10,454 births (12.5%) | victim code performed in 25/34; both contexts in 22/34 | neighbour code co-executed in 5,363 (10.1%) |
| resemblance label vs another reading | label "target" while the ADDRESS reading says writer-majority: 792; the reverse 2,114. **Not a descent test**: both are non-descent readings, and CX-5a shows the address reading can be the wrong one | 18,703 / 2,524 (same caveat) | -- | the parent chain names the executor; the executor is not the majority donor in 375 (0.71%) |
| capability shown later, in situ (among ADDRESS-writer-majority children seen writing) | is_sr later: 60% | 0.04% (18) | not recorded | not per event (block-13 probes) |

## What survives from v1
- Archaeon's column is unchanged: it reads native taint, and the reviewer confirmed it as a descent reading. New in v2: the
  co-executing neighbour is recorded (5,363 births), where v1 had omitted it.
- The carrier row (who executed) is recorded natively in all three engines. It shows substantial co-execution everywhere:
  * BEE r016299: 12.5% of births;
  * NPE: 22/34 births;
  * Archaeon: 10.1% of births.

## What v1 got wrong
- BEE "the resemblance label contradicts descent in 1.1% / 23%" is UNTESTABLE from the preserved rows. The reviewer's CX-5a is
  a real traced-VM case where the label is right and the address reading is wrong.
- NPE "50% two donors, 8.8% producer != donor, 23.5% lossy" measured code location and provenance, not material.
- The BEE producer was hard-coded to the writer; 10,454 r016299 births ran partner-material code.

## The finding that matters for the program
The directive's quantitative questions (producer != donor, resemblance mistaken for descent, singular-parent information loss) can
be answered from the preserved record of only one engine: Archaeon, whose VM carries per-byte material taint.

For BEE and NPE the answer requires a FULL replay with byte-level material provenance. Bellerophon's traced VM keeps a last-writer
map for the window only (traced_replay.py:83-84). NPE's z8taint tracks the executing code.

This is an instrumentation gap in the other engines' preserved records, not a property of BEE or NPE.
Recommendation: a material-taint replay (the Archaeon taint-VM pattern) for one BEE run and the T-003 NPE births. That is TH-016's
replay, extended to per-byte descent. Not launched: other seats' harnesses.
