# D1 RESULT -- archive-arm ladder on p1_slice T5 (C-013-T012)

Argus[harry1-90a937a5], claude-sonnet-5-5 (Q2), 2026-10-10. Executed under FREEZE_D1 v1.0.1 / PREREGISTRATION v1.0.1
(s9 amendment A1 governs s4, s5, s7). Base origin/main 7f77d5c53, branch argus/c013-t012. No file pinned in
FROZEN_D1.json was changed; the runner's check_frozen passed on every call (rso/reach/run_d1.py:49-54, 109).
Raw material: rso/reach/runs/D1/{LEDGER.jsonl (270 rows), CONTROLS.json, RUN.json, RESULT.json}.

## 1. Result class

**NOTHING SEPARATES.** All five contrasts: "NOT SEPARATED at this budget and n" (Holm-adjusted p >= 0.56).
Run status STOPPED_AT_CPU_CAP (RUN.json); analysis status ANALYZED (not UNDERPOWERED, not VOID).
Under s7 the permitted reading is: *no ingredient detectably changed the rate at B = 200,000 and n = 15 per (arm, d)*;
each arm's upper bound is reported (section 4); NOT "archives do not help" and NOT "the target is unreachable".
Separately, 9 lineages certified (section 5): a certified builder is reachable from those starts by those searches at
this budget.

## 2. Run facts

- Completed rounds N = 15 of 24; **N >= 12: yes** (so contrasts were read). n = 15 lineages per (arm, d), 45 per arm.
- CPU: 11,673.1 core-seconds = **3.243 core-hours** (RUN.json cpu_s; ledger row sum 3.243 h). The cap (3.2 h = 11,520 s)
  was first reached after round 15 (10,698 s after round 14), so the runner stopped; I did not choose the stop and did
  not inspect per-arm outcomes to decide whether to continue. Total stays within the 4 core-hour authorization.
- Wall: 12:34Z-14:30Z, 2 workers, NUMBA_NUM_THREADS=1, one round per call (about 6-9 min wall each). No call timed
  out; the ANOMALY 1 NUMBA RuntimeError did not occur. Per-round cost rose from ~630 to ~980 CPU-s over the run (trend recorded; no cause claimed).
- Controls (CONTROLS.json, ok = true): all six arms seeded at the target certify with a seeded hit at evaluation 0 and
  counted_as_discovery = false; holder, constant, lookup and empty do not certify. Seeded controls appear nowhere in
  the counts below (ledger seeded_hit = true on 0 of the 270 d >= 1 rows).
- Instrument: no VOID (no oracle disagreement). Training-perfect hits that failed certification: 0 (every hit certified).

## 3. Contrasts C1-C5 (stratified exact test, two-sided; Holm over 5)

Counts are certified discoveries / 15 per distance; "pooled" is over d = 1, 3, 8 (n = 45 each).

| id | contrast (A vs B) | A counts d1,d3,d8 | B counts d1,d3,d8 | pooled A vs B | raw p | Holm p | verdict |
|---|---|---|---|---|---|---|---|
| C1 | chain_neutral vs chain_strict | 0, 1, 0 | 4, 0, 0 | 1 vs 4 | 0.3487 | 1.0000 | NOT SEPARATED |
| C2 | X1 vs chain_neutral | 0, 0, 0 | 0, 1, 0 | 0 vs 1 | 1.0000 | 1.0000 | NOT SEPARATED |
| C3 | X2 vs X1 | 3, 1, 0 | 0, 0, 0 | 4 vs 0 | 0.1121 | 0.5603 | NOT SEPARATED |
| C4 | X3 vs X2 | 0, 0, 0 | 3, 1, 0 | 0 vs 4 | 0.1121 | 0.5603 | NOT SEPARATED |
| C5 | X3 vs X3G | 0, 0, 0 | 0, 0, 0 | 0 vs 0 | 1.0000 | 1.0000 | NOT SEPARATED |

Direction flag (A1.3): no contrast separates, so no s7 verdict row is invoked. For information, the stratum whose
direction opposes the pooled sign: C1 at d = 3 (chain_neutral 1 vs chain_strict 0, against a pooled sign of strict >
neutral). The other strata are tied or agree with the pooled sign. This is descriptive only.

## 4. Per-(arm, d) certified counts (RESULT.json `cells`; the A1.3 table)

| arm | d = 1 | d = 3 | d = 8 | pooled /45 | 95% upper bound (pooled) |
|---|---|---|---|---|---|
| chain_strict | 4/15 | 0/15 | 0/15 | 4 | 0.192 |
| chain_neutral | 0/15 | 1/15 | 0/15 | 1 | 0.101 |
| X1 | 0/15 | 0/15 | 0/15 | 0 | 0.064 |
| X2 | 3/15 | 1/15 | 0/15 | 4 | 0.192 |
| X3 | 0/15 | 0/15 | 0/15 | 0 | 0.064 |
| X3G | 0/15 | 0/15 | 0/15 | 0 | 0.064 |

Per-cell 95% upper bounds: 0/15 -> 0.181; 1/15 -> 0.279; 3/15 -> 0.440; 4/15 -> 0.511.

Secondary descriptives (no test, no claim): median realised cells at end -- X1 18-19, X2 1,288-1,458, X3 11,925-12,636,
X3G 12,226-12,762 (matches the B_d it was built with); chain arms hold no cells. Training-perfect-but-uncertified: 0 in
every cell. Hit times: section 5. Budget checkpoints: certified by 2,000
evals -- X2 d=1: 1, chain_strict d=1: 2 (42 and 1,812); by 20,000 -- X2 d=1: 3 (all its d=1 hits), chain_strict d=1:
4; by 200,000 -- all 9.

Stepping-stone counts (REPORTED ONLY; the inferential row is WITHDRAWN, A1.4): lineages that evaluated a shortest-path
stone: chain_strict d=8: 11 of 15, all other cells 0; lineages retaining one at the end: 0 in every cell; most rows
restored: 1 (chain_strict d=8), 0 elsewhere. **Stone counts cannot support or refute path preservation at this budget
and operator.** No conclusion about off-path routes or parent diversity is drawn from them.

## 5. Discovered certified solutions (seeded controls excluded)

9 certified discoveries, all CERTIFIED by certify.py (>= 90% on selection lives 2000..2063, sealed PASS or as the
certifier decided, oracle agreeing). arm, d, lineage, evaluations to hit:
chain_strict d=1 L10 @42; chain_strict d=1 L7 @1,812; X2 d=1 L14 @1,967; chain_strict d=1 L1 @2,105;
X2 d=1 L0 @2,320; chain_strict d=1 L3 @2,990; X2 d=1 L2 @7,721; chain_neutral d=3 L8 @36,387;
X2 d=3 L7 @138,824. Genomes are in LEDGER.jsonl (`final_prog` for hits). Per A1.4 last row and A1.2, each certifies
*a* builder (>= 90% on the 64 selection lives, oracle-agreeing), not necessarily builder_min or a synonym of it; the
reading is "reachable from that start by that search at that budget", not "built by design". Hits occur only at d = 1
and d = 3; none at d = 8 in any arm.

## 6. Interpretation (s7 / A1.4 words only)

- C1, C2, C3, C4, C5 do not separate, so none of their separating rows applies. "No ingredient detectably changed the
  rate at B = 200,000 and n = 15 per (arm, d)."
- This is NOT "archives do not help" and NOT "the target is unreachable". Observed pooled differences (e.g. X2 4 vs X1
  0, chain_strict 4 vs chain_neutral 1, X2 4 vs X3 0) are not separated at the Holm level and are not read as effects.
- Reachability: a certified builder is reachable from the d = 1 and d = 3 starts in chain_strict, chain_neutral and X2
  at this budget. No hit in X1, X3, X3G, or at d = 8 in any arm.
- Exploratory (labelled, NOT confirmatory, not in the Holm family): the raw pooled counts are 4/4/1/0/0/0 for
  chain_strict / X2 / chain_neutral / X1 / X3 / X3G. I ran no post-hoc contrast test and none should be read from this
  note.

## 7. What D1 does NOT establish

- Anything about the stepping-stone hypothesis (instrument withdrawn at A1.4); path or route preservation.
- That any ingredient (neutral acceptance, retention, count-weighted selection, worse-genome admission) helps or does
  not help; the power table (s6) detects ~+0.2 per lineage at N = 24, and here N = 15 (power lower than the N = 20
  row, between the printed N = 12 and N = 20 rows); smaller effects read NOT SEPARATED.
- That the behaviour-cell structure matters or does not matter beyond archive size (C5: 0 vs 0, no information beyond
  upper bound 0.064 pooled); the X3G control is matched at end-of-budget only.
- Anything about d > 8, other targets, other engines, Go-Explore, state restoration, or substrates in general.
- That the cap-truncated N = 15 would match N = 24 (rounds 16-24 never ran; they are not imputed).

## 8. Observations for the integrator (ambiguity written down, not resolved)

1. RUN.json `frozen` is null (rso/reach/run_d1.py:132 writes `spec.get("freeze_commit")`, which FROZEN_D1.json does not
   carry). check_frozen passed (48/48) at every start; the null is a metadata gap, not a skipped check.
2. The s6 power paragraph quotes N = 24, 20, 12; N = 15 falls between; I have not recomputed power.

Receipts and provenance: ops/campaigns/C-013/tasks/C-013-T012/attempts/A-001/RECEIPT.json; analysis command
`python -B -m rso.reach.analyze --run-dir rso/reach/runs/D1`.
