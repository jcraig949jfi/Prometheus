# INV-F -- metamorphic test of the Hecate world evaluators

Date: 2026-09-30. Harness: hecate/metamorphic/harness.py (see hecate/metamorphic/README.md).
Raw per-cell results (verdicts, flags, errors, mutation info): INV_F_metamorphic_results.json.
Command: `python hecate/metamorphic/harness.py --scratch <tmp> --json ... --md ...`
(6 workers, 60 s per run, 486 s wall).

Scope: 42 evaluators. These are 23 round-1/2 `evaluate.py`, 6 pilot-only
`pilot_eval.py` (worlds with no evaluate.py), 8 `probe/evaluate.py` and 5
`pass4/evaluate.py`. Each run used a fresh scratch copy of the world directory,
and nothing under hecate/programs was written.

Every baseline (unmutated) re-run reproduced the committed verdict: 42/42.
No evaluator needed more than 60 s, so none was skipped. The slowest single
run took 42.6 s.

## Mutations and the expected reaction

| id  | corruption | a correct evaluator must ... |
|-----|------------|------------------------------|
| M1  | swap TREATMENT <-> NULL_TWIN data | leave SIGNAL (expect CONFOUNDED); keep NULL as NULL |
| M2  | NULL_TWIN := copy of TREATMENT (pilot: := POSITIVE_CONTROL) | never say SIGNAL; twin flag must equal treatment success |
| M3a | TREATMENT := copy of CONTROL | never say SIGNAL |
| M3b | TREATMENT := copy of NULL_TWIN | never say SIGNAL |
| M4  | drop all *POSITIVE_CONTROL* rows | say INSTRUMENT_FAIL/NOT_BUILT (or crash); never a clean verdict, never "PC detected" |
| M4c | drop all *CHEAT* rows (extension) | same, for the cheat control |
| M5  | CHEAT := copy of TREATMENT (pilot: := NULL_TWIN) | a cheat that is undetected must not pass silently; must not "detect" failing treatment data as the cheat |
| M6  | every seed's rows := seed s0's rows (seed label kept) | notice pseudo-replication |
| M7  | measurement values permuted across arms within each seed | leave a positive verdict |

A copy (M1-M3, M5) keeps the destination's seeds, design cells and provenance
labels, and drops the destination-only payload fields. When that crashes on a
missing row field (crash-s), the harness re-runs once in lenient mode, which
keeps the stale destination-only fields. That result is shown after " / " with
a "~" suffix. A lenient result that would claim insensitivity is downgraded to
"untest" if the evaluator reads one of the stale fields.

## Results table

Legend:
- `ok`: the expected reaction.
- `ok*`: the evaluator reacted, but to a different non-positive class than expected.
- `u`: uninformative, because the baseline already sits in the forced class.
- `-`: not applicable, because the arm is absent.
- `INSENS`: INSENSITIVE, meaning the verdict did not change where it must.
- `asym`: the twin rule is not the success rule.
- `untest`: the mutation cannot reach the deciding field.
- `CRASH`: the evaluator raised an exception.
- `crash-s`: the evaluator raised KeyError on a row field the mutated arm does not carry.
- `blind`: M6 was accepted silently.
- `det`: M6 changed the verdict to an instrument class.
- `shift`: M6 changed the verdict with no flag.

Crash is never counted as detection.

| evaluator | kind | baseline | M1 | M2 | M3a | M3b | M4 | M4c | M5 | M6 | M7 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| HT-056d3ac561/worlds/W1 | main | INSTRUMENT_FAIL | crash-s / ok~ | crash-s / ok~ | ok | crash-s / ok~ | CRASH | CRASH | crash-s / untest~ | shift | u |
| HT-056d3ac561/worlds/W4 | main | NULL | ok* | ok | ok | ok | CRASH | CRASH | ok | blind | ok |
| HT-056d3ac561/worlds/W5/probe | probe | NULL | ok* | ok | - | ok | ok | ok | ok | det | ok |
| HT-2a8a3aedeb/worlds/W1 | main | NULL | ok | ok | CRASH | ok | CRASH | CRASH | ok | blind | CRASH |
| HT-2a8a3aedeb/worlds/W4 | main | NULL | ok | ok | ok | ok | CRASH | CRASH | ok | blind | ok |
| HT-321a8fd8e0/worlds/W1 | main | SIGNAL | ok | ok | ok | ok | CRASH | CRASH | ok | blind | ok |
| HT-321a8fd8e0/worlds/W1/pass4 | pass4 | ORIG_FOSSIL_ALT_PASS | ok | ok | ok | ok | CRASH | CRASH | ok | blind | CRASH |
| HT-37e311ce05/worlds/W1 | main | INSTRUMENT_FAIL | ok | ok | ok | ok | CRASH | CRASH | u | blind | CRASH |
| HT-37e311ce05/worlds/W4 | pilot | PILOT_FAIL | - | u | - | - | u | ok | ok | blind | CRASH |
| HT-37e311ce05/worlds/W5/probe | probe | NULL | ok* | ok | - | ok | CRASH | CRASH | ok | det | CRASH |
| HT-47f4c02be4/worlds/W1 | main | NULL | crash-s / asym~ | crash-s / asym~ | crash-s / ok~ | ok | INSENS | INSENS | crash-s / untest~ | blind | ok |
| HT-47f4c02be4/worlds/W4 | main | CONFOUNDED | crash-s / ok~ | crash-s / ok~ | crash-s / ok~ | ok | CRASH | CRASH | crash-s / ok~ | blind | ok |
| HT-55162c0ac0/worlds/W2 | pilot | PILOT_FAIL | - | CRASH | - | - | CRASH | CRASH | crash-s / ok~ | blind | CRASH |
| HT-55162c0ac0/worlds/W3 | main | INSTRUMENT_FAIL | crash-s / ok~ | crash-s / ok~ | ok | ok | CRASH | CRASH | ok | blind | crash-s |
| HT-55162c0ac0/worlds/W6/probe | probe | SIGNAL | ok* | ok* | crash-s / untest~ | ok | ok | ok | ok | blind | ok |
| HT-55162c0ac0/worlds/W6/pass4 | pass4 | PARK | ok | ok | - | ok | ok | ok | ok | det | ok |
| HT-5b0b3ebb8d/worlds/W4 | main | SIGNAL | ok | ok | CRASH | ok | CRASH | CRASH | ok | shift | CRASH |
| HT-5b0b3ebb8d/worlds/W4/pass4 | pass4 | PARK | ok | ok | - | ok | ok | CRASH | ok | blind | ok |
| HT-71b65251aa/worlds/W3 | main | SIGNAL | CRASH | ok | crash-s / untest~ | CRASH | CRASH | CRASH | crash-s / ok~ | blind | CRASH |
| HT-71b65251aa/worlds/W3/pass4 | pass4 | PARK | CRASH | ok | crash-s / ok~ | CRASH | CRASH | ok | crash-s / untest~ | blind | CRASH |
| HT-79e904e13a/worlds/W1 | main | NULL | crash-s / ok~ | ok | ok | crash-s / ok~ | CRASH | CRASH | ok | det | ok |
| HT-79e904e13a/worlds/W4 | main | NULL | crash-s / ok~ | ok | crash-s / ok~ | crash-s / ok~ | CRASH | CRASH | crash-s / ok~ | blind | ok |
| HT-8a87057933/worlds/W1 | main | NOT_BUILT | ok | ok | ok | ok | CRASH | CRASH | ok | blind | u |
| HT-8a87057933/worlds/W4 | pilot | PILOT_FAIL | - | u | - | - | CRASH | CRASH | ok | blind | ok |
| HT-8a87057933/worlds/W5/probe | probe | SIGNAL | crash-s / ok*~ | ok* | crash-s / ok~ | crash-s / ok~ | CRASH | CRASH | ok | det | ok |
| HT-8a87057933/worlds/W5/pass4 | pass4 | PARK | ok | ok | crash-s / ok~ | crash-s / ok~ | CRASH | CRASH | ok | blind | ok |
| HT-974471f045/worlds/W1 | pilot | PILOT_FAIL | - | crash-s / u~ | - | - | CRASH | CRASH | ok | blind | ok |
| HT-974471f045/worlds/W3 | main | NULL | ok* | ok | crash-s / ok~ | ok | ok | ok | ok | blind | ok |
| HT-974471f045/worlds/W6/probe | probe | NULL | ok* | ok | crash-s / ok~ | crash-s / ok~ | ok | CRASH | ok | blind | u |
| HT-a9e2ba7618/worlds/W3 | main | NULL | asym | asym | ok | ok | CRASH | CRASH | ok | blind | ok |
| HT-a9e2ba7618/worlds/W4 | main | NULL | ok | ok | ok | ok | CRASH | CRASH | crash-s / untest~ | blind | u |
| HT-ae38c641b1/worlds/W3 | main | NULL | CRASH | ok | CRASH | CRASH | CRASH | CRASH | ok | blind | ok |
| HT-ae38c641b1/worlds/W4 | pilot | PILOT_FAIL | - | CRASH | - | - | CRASH | CRASH | ok | blind | CRASH |
| HT-ae38c641b1/worlds/W5/probe | probe | NULL | crash-s / ok~ | crash-s / ok~ | - | ok | CRASH | CRASH | ok | det | ok |
| HT-e106e1603b/worlds/W1 | main | NULL | ok | ok | ok | ok | CRASH | CRASH | ok | blind | CRASH |
| HT-e106e1603b/worlds/W2 | main | INSTRUMENT_FAIL | ok | ok | ok | ok | u | ok | ok | shift | u |
| HT-e106e1603b/worlds/W5/probe | probe | NULL | ok | ok | - | ok | ok | ok | ok | blind | ok |
| HT-e743909f97/worlds/W1 | main | NULL | crash-s / ok~ | crash-s / ok~ | ok | ok | CRASH | CRASH | CRASH | blind | ok |
| HT-e743909f97/worlds/W3 | main | NULL | ok | ok | ok | ok | CRASH | CRASH | ok | blind | ok |
| HT-faa9277e02/worlds/W1 | pilot | PILOT_FAIL | - | u | - | - | CRASH | CRASH | u | blind | ok |
| HT-faa9277e02/worlds/W2 | main | INSTRUMENT_FAIL | ok | ok | ok | ok | CRASH | CRASH | ok | blind | CRASH |
| HT-faa9277e02/worlds/W6/probe | probe | NULL | crash-s / ok~ | ok | crash-s / ok~ | crash-s / ok~ | CRASH | CRASH | ok | det | ok |

Label counts by mutation (strict run):

| mutation | counts |
|---|---|
| M1 | ok 16, ok* 6, asym 1, crash-s 10, CRASH 3, - 6 |
| M2 | ok 27, ok* 2, asym 1, u 3, crash-s 7, CRASH 2 |
| M3a | ok 16, crash-s 11, CRASH 3, - 12 |
| M3b | ok 26, crash-s 7, CRASH 3, - 6 |
| M4 | ok 7, u 2, INSENS 1, CRASH 32 |
| M4c | ok 8, INSENS 1, CRASH 33 |
| M5 | ok 31, u 2, crash-s 8, CRASH 1 |
| M6 | blind 32, det 7, shift 3 |
| M7 | ok 24, u 5, CRASH 12, crash-s 1 |

Lenient re-runs:

| mutation | counts |
|---|---|
| M1~ | ok 8, ok* 1, asym 1 |
| M2~ | ok 5, asym 1, u 1 |
| M3a~ | ok 9, untest 2 |
| M3b~ | ok 7 |
| M5~ | ok 4, untest 4 |

## Findings

F1 -- INSENSITIVE: HT-47f4c02be4/W1 passes with no controls (M4, M4c).
The gates are `pc_ok = all(pc_success(r) for r in pc)` and
`cheat_ok = all(success(...) for r in ch)`, and `all()` of an empty list is
True. With every POSITIVE_CONTROL row deleted, the evaluator still reports
`positive_control_detected: true` and a clean NULL. The same happens with
every CHEAT row deleted. This is the only hard insensitivity found, and the
ruler cannot see missing controls. The fix is to require
`len(pc) == n_seeds` (and the same for CHEAT) before the `all()`.

F2 -- No positive verdict survived the treatment corruptions. The positive
baselines are 321a/W1 SIGNAL, 321a/W1/pass4, 55162/W6/probe SIGNAL,
5b0b/W4 SIGNAL and 8a87/W5/probe SIGNAL. M1, M2 and M3b each moved all of
them off positive, except 71b6/W3 SIGNAL, which crashed on M1 and M3b.
For 8a87/W5/probe, M1 and M3b needed the lenient re-run. M7 also moved
every positive baseline that ran; 321a/pass4, 5b0b/W4 and 71b6/W3 crashed
on M7.
- 55162/W6/probe and 8a87/W5/probe went to INSTRUMENT_FAIL rather than
  CONFOUNDED, because their frozen-control reproducibility check reads
  NULL_TWIN.
- M3a cannot be tested on 55162/W6/probe or 71b6/W3. The treatment verdict
  reads treatment-only fields (`ari_ftle`..., `by_theta`), and CONTROL is
  measured on a different schema. Copying CONTROL into TREATMENT therefore
  cannot reach the deciding statistic.

F3 -- ASYM: the twin rule is not the success rule (a9e2/W3, 47f4/W1). When
treatment data sits in the twin slot (M1, M2), it "meets success" even though
the same data fails the treatment success rule.
- a9e2/W3: the twin rule is median ARI >= 0.7 only. Success needs that, plus
  a gap >= 0.2 with p < 0.01, plus osc > comp.
- 47f4/W1: the twin rule is clause A only. Success is A and B, and B is
  computed from the twin rows.

The asymmetry is conservative (it calls CONFOUNDED more readily). Even so,
`null_twin_meets_success` does not mean what its name says. I checked by
hand that the 47f4 lenient result does not rest on the stale `ratio_20_0`
field.

F4 -- Removing a control is mostly caught by crashing, not by the instrument
class. Across M4 and M4c, 32/42 and 33/42 evaluators raise an exception:
KeyError, IndexError, ZeroDivisionError, StopIteration, AssertionError or
sklearn ValueError. Only these answer in-class, with INSTRUMENT_FAIL,
NOT_BUILT, PILOT_FAIL or a controls-failed PARK:
- M4: 056d/W5/probe, 37e3/W4 (pilot), 55162/W6/probe, 55162/W6/pass4,
  5b0b/W4/pass4, 974471/W3, 974471/W6/probe, e106/W2, e106/W5/probe
- M4c: 056d/W5/probe, 37e3/W4 (pilot), 55162/W6/probe, 55162/W6/pass4,
  71b6/W3/pass4, 974471/W3, e106/W2, e106/W5/probe

A crash is loud, but a pipeline that treats "no OUTCOME.json" as a retry or
skip would not record an instrument failure.

F5 -- Pseudo-replication is invisible (M6). No evaluator checks that seeds are
independent:
- 32/42 are blind.
- 7 "detected" M6 only because the frozen-control values in
  ATTAINABILITY.json no longer reproduced (056d/W5, 37e3/W5, 8a87/W5,
  ae38/W5, faa9/W6 probes, 55162/W6/pass4), or incidentally because the PC
  flag flipped (79e9/W1). Neither is a duplication test.
- 3 shifted with no flag. In 5b0b/W4, SIGNAL became CONFOUNDED once seed 0
  was cloned to every seed. In 056d/W1 and e106/W2, the cheat flag flipped.

A uniqueness check on per-seed payload hashes would catch all of these.

F6 -- Cheat detectors in 4 worlds read cheat-only fields, so M5 cannot reach
them (`untest~`):
- 056d/W1: `D_cheat`, `top1_cheat`
- 47f4/W1: `twin_ratio_injected`
- 71b6/W3/pass4: `injected`
- a9e2/W4: `acc_T_by_w`, `acc_C_by_w`, `acc_N_by_w`

In these worlds the cheat control is not scored by the same statistic as
treatment success, so "cheat detected" is a check on a different quantity.

No evaluator returned a clean verdict with the cheat undetected (SILENT = 0).
For example, 8a87/W5/probe has a cheat signature (an error floor) beyond
success. With CHEAT := TREATMENT it correctly loses cheat detection and
returns INSTRUMENT_FAIL.

F7 -- The control gate is coupled to the twin. For 056d/W4, 056d/W5/probe,
37e3/W5/probe, 974471/W3 and 974471/W6/probe, M1 on a NULL world gives
INSTRUMENT_FAIL. Their positive and cheat controls are scored against
NULL_TWIN, so corrupting the twin breaks the instrument verdict rather than
the treatment verdict. This is defensible, but it means a bad twin reads as
"instrument broken", not "confounded".

F8 -- Arm schemas are heterogeneous. Of the copy and permutation cells, 44
end in crash-s. Arms carry different fields: the treatment-only diagnostics,
the twin-only `ratio_20_0`, the cheat-only injection fields. That is why
many evaluators cannot be metamorphically tested by a plain arm copy. Arms
that are meant to be comparable should share one row schema.

## Caveats

- The expectations are the harness's reading of the round-1 class rules
  (INSTRUMENT_FAIL > CONFOUNDED > SIGNAL > NULL). For pass4, SURVIVES and
  ORIG_FOSSIL_ALT_PASS count as positive, and PARK counts as NEGATIVE or
  INSTR according to the controls flags. Pass4 has no CONFOUNDED class, so
  any non-positive answer to M1 or M2 counts as ok.
- Pilot worlds have no TREATMENT arm, so M1 and M3 do not apply. For pilots,
  M2 is NULL_TWIN := PC and M5 is CHEAT := NULL_TWIN. All 6 pilots
  committed PILOT_FAIL, so most pilot cells are uninformative.
- M7 can only move fields that at least two arms carry. Fields carried by
  one arm alone are listed in the JSON (`unmoved_keys`). On non-positive
  baselines, an unchanged verdict is marked `u`, not INSENS.
- M5 "treatment success" is taken as true for a positive baseline and false
  for NULL. Otherwise it is taken from the twin flag of the M1 run.
- The "u" cells under M4 (e106/W2, 37e3/W4) are worlds whose PC already
  failed at baseline, so the mutation cannot show a reaction.
