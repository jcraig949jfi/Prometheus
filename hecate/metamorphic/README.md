# hecate/metamorphic -- metamorphic tests for world evaluators

A good evaluator must react correctly when its input rows are corrupted in
known ways. An evaluator whose verdict does not move when it must is a ruler
that cannot see what it claims to measure. This harness applies fixed
corruptions to an evaluator's rows, re-runs it, and judges the reaction.

## Run

```
python hecate/metamorphic/harness.py --scratch <tmp dir> \
    [--only HT-321a] [--workers 6] [--timeout 60] [--json out.json] [--md out.md]
```

- Discovery covers `hecate/programs/HT-*/worlds/*/evaluate.py` (with
  `rows.jsonl` beside it), `worlds/*/probe/evaluate.py`,
  `worlds/*/pass4/evaluate.py`, and the pilot-only worlds listed in
  `PILOTS`, which have `pilot_eval.py` + `PILOT.json`. That is 42
  evaluators today.
- For every evaluator x mutation, the world directory is copied to
  `<scratch>/<tid>/<mutation>/`, with the parent world dir for probe and
  pass4, because those read `../spec.json`. The rows file is rewritten, the
  output file is deleted, and the evaluator runs with that directory as cwd.
- The output is the evaluator's own JSON: `OUTCOME.json`,
  `PASS4_OUTCOME.json` or `PILOT.json`. Nothing under hecate/programs is
  written, and the harness refuses a scratch dir inside it.
- No git, no network, no model calls. The run is deterministic: M7 uses a
  seeded RNG, keyed by evaluator and mutation.
- If the baseline (unmutated) run exceeds `--timeout`, the evaluator is
  reported as SKIPPED. The table also flags any baseline verdict that
  differs from the committed one.

## Mutations

| id  | corruption | expected reaction |
|-----|------------|-------------------|
| M1  | swap TREATMENT <-> NULL_TWIN data | positive -> not positive (CONFOUNDED expected); NULL stays NULL |
| M2  | NULL_TWIN := copy of TREATMENT | never positive; positive -> CONFOUNDED |
| M3a | TREATMENT := copy of CONTROL | never positive |
| M3b | TREATMENT := copy of NULL_TWIN | never positive |
| M4  | drop *POSITIVE_CONTROL* rows | INSTRUMENT_FAIL / NOT_BUILT / crash; never a clean verdict, never pc=True |
| M4c | drop *CHEAT* rows | same, for the cheat control |
| M5  | CHEAT := copy of TREATMENT | cheat undetected must not give a clean verdict; cheat must not be "detected" on failing treatment data |
| M6  | all seeds := seed s0's rows (labels kept) | pseudo-replication flagged |
| M7  | measurement values permuted across arms within seed | positive verdict must move |

For pilot worlds there is no TREATMENT arm:
- M2 becomes NULL_TWIN := POSITIVE_CONTROL, and the PC must no longer be
  detected.
- M5 becomes CHEAT := NULL_TWIN, and the cheat must not be detected.
- M1 and M3 are N/A.

Arm aliases for worlds that name roles differently live in `ALIASES`. For
example, ae38/W5/probe uses TREATMENT=V and NULL_TWIN=NULL_TWIN_V.

## Copy semantics

`copy_arm(rows, src, dst)` keeps every destination row's seed, design cell
(`attack`, `variant`, `attempt`, `k`, `level`, `delta`, `tau`, ...) and
provenance labels (`source`, `role`, ...). It fills the rest from the
matching source row, matched on seed + design cell, then coarser keys, then
index. Destination-only payload fields are dropped, so the destination
really is a copy.

If the evaluator then dies with KeyError on a row field (CRASH_SCHEMA), the
harness re-runs once in lenient mode, which keeps the stale destination-only
fields. A lenient result that would claim INSENSITIVE, SILENT or WRONG is
downgraded to UNTESTABLE when the evaluator source names one of the stale
fields. In that case the corruption never reached the deciding statistic.

M1 is two simultaneous copies.

M7 permutes, within each (seed, attack, variant, attempt, phase, tag, run)
group, every payload field across the rows that carry it. It prefers
permutations in which each row gets another arm's value. Fields carried by
one arm only cannot move; they are recorded in `info.unmoved_keys`.

## Labels

| label | meaning |
|-------|---------|
| OK | expected reaction |
| REACTED_OTHER (ok*) | moved, but to a different non-positive class than expected |
| UNINF (u) | baseline already in the forced class; no information |
| INSENSITIVE | verdict or flag unchanged where it must change: the ruler cannot see the corruption |
| SILENT | cheat undetected yet a clean verdict was issued |
| WRONG | moved in a direction no correct rule allows (e.g. NULL -> SIGNAL) |
| ASYM | twin rule != success rule: treatment data "meets success" in the twin slot but not in the treatment slot |
| UNTESTABLE | lenient re-run only; decision rests on fields the mutation could not replace |
| CRASH / CRASH_SCHEMA | evaluator raised; crash is NOT detection |
| BLIND / SHIFTED / DETECTED | M6 only: silent / verdict moved without a flag / flagged or forced to instrument class |
| NA (-) | arm absent |

## Extending

- To add a mutation, add a branch to `mutate()`, an entry to `MUTATIONS`
  and `ORDER`, and a rule in `judge()`.
- For a new evaluator layout, add it in `discover()`. Use `PILOTS` for
  argv / rows file / output file, and `ALIASES` for role names.
- `extract()` normalises any output into `verdict`, `cls`
  (POS/NEG/CONF/INSTR), `pc`, `ch`, `nt` and `anomalies`.

## Latest results

See roles/Hecate/harvest_w2/INV_F_metamorphic_results.md (table + findings)
and INV_F_metamorphic_results.json (raw).
