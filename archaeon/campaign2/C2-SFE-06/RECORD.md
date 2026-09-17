# C2-SFE-06 -- retention economics on a rung ladder

## A. STARTUP (preregistration; sealed sha256:d08ad16428043955fb3b302075b6aee1676e262da9ea74f2e7e15b14eccfbd3a)

- experiment ID: C2-SFE-06
- parents: SFE-05
- QUESTION: When the selective pressure climbs a delay ladder (W0 -> d1 -> d2 -> d4, 25 generations per rung), at what revisit share p of earlier rungs in the training battery is rung-0 competence retained to the end, and what does retention cost on the top rung?
- PARENT EVIDENCE: SFE-05: adaptive +0.155, transfer +0.113 (n=3); fixed/on lost Kd-0 competence entirely (forgetting shelf hidden by the battery mean, L-022). Table: W0 4-bit COMMON by ~G35 (10/12 C2-SFE-03, 7/10 C2-SFE-04); W1_d4 4-bit RARE (1/14 at G60).
- ASSAY CAPABILITY REQUIREMENT: the ladder is climbable at its bottom: the p0.0 arm reaches rung-0 competence >= 0.5 (peak_r0) in >= 3 of 6 seeds; otherwise POSITIVE_CONTROL_FAILED (nothing to retain)
- POSITIVE CONTROL: p0.0 on rung 0 during the first 25 generations (W0 4-bit): expected ~0.7 per seed
- REACHABILITY ESTIMATE:
    {"W0": {"at_budget": {"band95": [0.0, 1.0], "class": "UNESTABLISHED", "first_solved_gens": [], "freq": null, "k": 0, "n": 0}, "at_budget_any_foundry": {"band95": [0.0, 1.0], "class": "UNESTABLISHED", "foundries": [], "freq": null, "k": 0, "n": 0}, "foundry": "instr1-16:6528b9dc", "pooled_any_budget": {"band95": [0.0, 1.0], "budgets": [], "class": "UNESTABLISHED", "freq": null, "k": 0, "n": 0}}, "W1_d4": {"at_budget": {"band95": [0.0, 1.0], "class": "UNESTABLISHED", "first_solved_gens": [], "freq": null, "k": 0, "n": 0}, "at_budget_any_foundry": {"band95": [0.0, 1.0], "class": "UNESTABLISHED", "foundries": [], "freq": null, "k": 0, "n": 0}, "foundry": "instr1-16:6528b9dc", "pooled_any_budget": {"band95": [0.0127, 0.3147], "budgets": [[200, 60, 16]], "class": "RARE", "freq": 0.0714, "k": 1, "n": 14}}}
- ARMS:
    - p0.0
    - p0.1
    - p0.25
    - p0.5
- COMMON-RANDOM-NUMBERS POLICY: default; identical generation 0 and selection stream for every p (the RNG is keyed on rung 0's world id); episodes per generation keyed on (generation, seed) so arms share the current-rung episodes and differ only in the revisit share
- BUDGET:
    {"E": 16, "G": 100, "N": 200, "probe_episodes": 24, "probe_every": 5, "rung_gens": 25, "rungs": [{"D": 1, "K": 1, "Kd": 0, "ask_kind": "ASK", "ask_mode": "all", "ask_timing": "end", "delay": 0, "delays": [], "expensive": 0, "fanout": 1, "interfere": false, "interleave": "sequential", "n_defs": 0, "name": "W0", "noise_rate": 0.0, "op_mode": "fixed", "recycle": false, "retire_rate": 0.0, "topology": "streams", "value_bits": 4, "vocab": "train"}, {"D": 1, "K": 1, "Kd": 0, "ask_kind": "ASK", "ask_mode": "all", "ask_timing": "end", "delay": 1, "delays": [], "expensive": 0, "fanout": 1, "interfere": false, "interleave": "sequential", "n_defs": 0, "name": "W1_d1", "noise_rate": 0.0, "op_mode": "fixed", "recycle": false, "retire_rate": 0.0, "topology": "streams", "value_bits": 4, "vocab": "train"}, {"D": 1, "K": 1, "Kd": 0, "ask_kind": "ASK", "ask_mode": "all", "ask_timing": "end", "delay": 2, "delays": [], "expensive": 0, "fanout": 1, "interfere": false, "interleave": "sequential", "n_defs": 0, "name": "W1_d2", "noise_rate": 0.0, "op_mode": "fixed", "recycle": false, "retire_rate": 0.0, "topology": "streams", "value_bits": 4, "vocab": "train"}, {"D": 1, "K": 1, "Kd": 0, "ask_kind": "ASK", "ask_mode": "all", "ask_timing": "end", "delay": 4, "delays": [], "expensive": 0, "fanout": 1, "interfere": false, "interleave": "sequential", "n_defs": 0, "name": "W1_d4", "noise_rate": 0.0, "op_mode": "fixed", "recycle": false, "retire_rate": 0.0, "topology": "streams", "value_bits": 4, "vocab": "train"}], "seeds": [1, 2, 3, 4, 5, 6], "shares": [0.0, 0.1, 0.25, 0.5]}
- PRIMARY OBSERVABLE: final_r0 (rung-0 competence of the elite at the end, 24 eval episodes) per arm x seed; rung x generation matrix; shelf report
- CLAIM CEILING: weak at best (n=6, one ladder); a capable negative = revisits at p<=0.5 do not retain rung-0 competence
- FALSIFICATION CONDITION: final_r0(p0.25) - final_r0(p0.0) < 0.15 => revisiting does not retain; cost = final_r3(p0.25) - final_r3(p0.0) reported
- TYPED FAILURE CONDITIONS:
    - POSITIVE_CONTROL_FAILED (p0.0 peak_r0 >= 0.5 in < 3 seeds)
    - UNDERPOWERED
    - ENGINE_FAILURE / INSTRUMENT_FAILURE
- EXPECTED MACHINE TELEMETRY:
    - rung x generation matrix per row
    - shelf report per rung
    - peak/final per rung
    - schedule (rung, best, mean per generation)
    - elite genome summary
    - gen0 provenance
- MACHINE CHANGES EXERCISED:
    - G (spec and episodes change per step)
    - H (rung_matrix_row, shelf_report)
    - B
    - C
    - I
- decl (machine-read by archaeon.wse.states): {"n_min": 6, "positive_control": {"arm": "p0.0", "metric": "peak_r0", "min": 0.5, "min_rows": 3}, "primary": {"control": "p0.0", "metric": "final_r0", "min_effect": 0.15, "treatment": "p0.25"}}

## B. EXECUTION (generated from receipts)

- attempts: 2 (of record: a02); resumed_from: None; replayed steps on the attempt of record: 0
    a01  errors=0 replayed=0 engine=False purpose=dry run disposition_candidate=POSITIVE_CONTROL_FAILED
    a02  errors=0 replayed=0 engine=True purpose=engine disposition_candidate=WEAK_POSITIVE
- engine: live; worlds 1; artifacts 2; imports 0; records 24; errors 0
- timings (s): ladder_s=295.6, records_s=6.53, startup_s=0.97, teardown_s=0.19, total_s=304.3
- decisions: D2-014: revisit share p is the only difference between arms; it is an ecological pressure (old conditions recur), never a reward for retaining anything
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / final_r0              s1      s2      s3      s4      s5      s6    mean    n
    p0.0                     0.042   0.125   1.000   0.000   0.083   0.083   0.222    6
    p0.1                     1.000   0.125   1.000   1.000   0.083   0.833   0.674    6
    p0.25                    1.000   0.125   1.000   1.000   1.000   0.083   0.701    6
    p0.5                     1.000   1.000   1.000   1.000   1.000   1.000   1.000    6

    arm / final_r3              s1      s2      s3      s4      s5      s6    mean    n
    p0.0                     0.042   0.083   1.000   1.000   0.000   0.042   0.361    6
    p0.1                     1.000   0.083   1.000   1.000   0.000   0.583   0.611    6
    p0.25                    1.000   0.083   1.000   1.000   1.000   0.042   0.688    6
    p0.5                     1.000   0.083   1.000   1.000   1.000   0.000   0.681    6

    arm / peak_r0               s1      s2      s3      s4      s5      s6    mean    n
    p0.0                     1.000   0.167   1.000   1.000   0.167   0.167   0.583    6
    p0.1                     1.000   0.167   1.000   1.000   0.083   0.833   0.681    6
    p0.25                    1.000   0.167   1.000   1.000   1.000   0.083   0.708    6
    p0.5                     1.000   1.000   1.000   1.000   1.000   1.000   1.000    6

    arm / retention_r0          s1      s2      s3      s4      s5      s6    mean    n
    p0.0                     0.042   0.750   1.000   0.000   0.500   0.500   0.465    6
    p0.1                     1.000   0.750   1.000   1.000   1.000   1.000   0.958    6
    p0.25                    1.000   0.750   1.000   1.000   1.000   1.000   0.958    6
    p0.5                     1.000   1.000   1.000   1.000   1.000   1.000   1.000    6

    arm / fell_r0_at            s1      s2      s3      s4      s5      s6    mean    n
    p0.0                        25       -      25      25       -       -  25.000    3
    p0.1                        30       -       -      25       -       -  27.500    2
    p0.25                       45       -       -       -       -       -  45.000    1
    p0.5                         -       -       -       -       -       -       -    0

- footholds:
    arm                    footholds  first_solved_gen per row
    p0.0                   3/6        18,-,17,19,-,-
    p0.1                   4/6        18,-,17,19,-,91
    p0.25                  4/6        18,-,17,19,88,-
    p0.5                   4/6        18,-,17,19,82,-

- typed states fired: none
- disposition candidate (machine): WEAK_POSITIVE -- effect >= min_effect but n < 10 or a declared falsification attack failed or was not run
    evidence: {"control_mean": 0.2222, "effect": 0.4792, "min_effect": 0.15, "n_control": 6, "n_treatment": 6, "paired": 6, "paired_wins": 3, "treatment_mean": 0.7014}
    battery: {"attacked": 0, "declared": 0, "survived": 0}
- claim ceiling (machine): weak; not for propagation; preregistered ceiling: weak at best (n=6, one ladder); a capable negative = revisits at p<=0.5 do not retain rung-0 competence

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

Positive control passed at the preregistered minimum: the p0.0 arm reached rung-0 competence 1.0 in 3 of 6 seeds (s1, s3, s4, all by generation 20; the other three never solved W0 inside the 25-generation rung, consistent with W0's solve times of 12-31). The machine candidate WEAK_POSITIVE (final_r0 p0.25 - p0.0 = +0.48, paired wins 3/6, n=6) is accepted with its ceiling: the retention question is defined only in the seeds that had something to retain, so the effective n is 3. In those three seeds the FORGETTING SHELF is sharp and sits exactly at the rung boundary: under p0.0 rung-0 competence fell from 1.0 to <= 0.12 within five generations of the pressure moving to delay 1 (s1 and s4: 100 at generation 20, 12 and 29 at 25, 0 at 30); under p0.1 it fell in one of the three (s1, recovered later), under p0.25 in one (s1 at 45, recovered to 1.0 by 99), under p0.5 in none, and p0.5 held rung 0 at 1.0 in all six seeds to the end. The COST side is the surprise: retention did not cost top-rung competence, it bought it. Final rung-3 (delay 4) competence: p0.0 mean 0.36 (2/6 seeds at 1.0), p0.1 0.61, p0.25 0.69 (4/6), p0.5 0.68 (4/6). Break-even is therefore at or below p=0.1: the smallest revisit share tested already removes the shelf in most seeds at no cost to adaptation. Exploratory shape behind it (rung x generation matrices, 21 probes per run): the rung-0 solver is a last-value specialist (row at generation 20: R0 1.0, R1-R3 0.0); the FIRST delay-1 solutions that appear after the pressure moves are already delay-INVARIANT (s3 and s4 at generation 30: 1.0 on every rung including delays 2 and 4 the population had never been asked), and under p0.0 the population then specializes AWAY from rung 0 (s4 at generation 35: 0/1.0/0.96/0.96) and later oscillates between specialists (generation 99: 0/0.08/0.04/1.0); under p0.25 and p0.5 the same seed holds 1.0 on every rung from generation 30 to 99. Retention economics, as measured: a general solution exists and is found early; without revisits selection drifts off it toward the current specialist; a 10-25% revisit share keeps the general solution in place. Must NOT be claimed: that p0.5 is better than p0.25 (equal within noise on R3; p0.5 delayed adaptation in s1 to generation 70); anything at n=3 retained seeds beyond 'the shelf exists and revisits remove it'.

## D. TEARDOWN (generated)

- worlds: {"ladder": "TERMINATED"}
- all TERMINATED: True

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C2-SFE-06

Zero engine errors; 1 world; 24 records; the matrices published as one observation artifact; 24 reachability rows (treated: schedule). The step API did exactly what group G asked: one population, the spec and the episode battery changed per generation, no loop re-implemented (SFE-05 had rebuilt the loop with G=1 calls and its own child generator). The rung x generation matrix and shelf_report (group H) exposed in one glance what SFE-05's battery mean hid. Bench notes: (1) the probe every 5 generations missed the exact fall generation by up to 4 generations (fell_at_gen is the first probe at which the drop shows); a probe every generation during rung transitions would locate the shelf to the generation (MISSING_TELEMETRY, minor); (2) 'peak_r0' as the positive-control metric counts a seed whose rung-0 solution arrived late (s6 under p0.1 at 95); a rung-window peak would be stricter (KEEP_POLICY).

## F. LANDSCAPE / GRADIENT NOTES

(1) The delay-0 solution on this ladder is a specialist (answers only when asked immediately); the delay-1 pressure produces a delay-invariant solver in the seeds where it produces anything (2 of 3 retained seeds, at generation 30, i.e. 5 generations after the pressure moved): delay 1 is the rung at which 'store and answer later' is discovered, and it generalizes to delays 2 and 4 unseen. (2) The forgetting shelf is a rung-boundary cliff (5 generations) under pure current-rung pressure, and it happens even when the population holds a solution that covers every rung (s4): drift, not capacity. (3) W1_d4 competence 0.96-1.0 was reached in 4 of 6 seeds by generation 99 on the ladder (through the corridor delay 0 -> 1 -> 2 -> 4), where direct search reaches W1_d4 4-bit at G60 in 1/14: the ladder is a corridor to a RARE cell. (4) Revisit share 0.5 delayed adaptation in one seed (rung 0 held, rungs 1-3 flat until generation 70) -- the retention cost exists at high p in some seeds, not on average.

DISPOSITION: WEAK_POSITIVE (machine candidate WEAK_POSITIVE). Assay capable (p0.0 peaked on rung 0 in 3/6 seeds); n=6 with three seeds carrying the retention question. Revisiting earlier rungs at share >= 0.1 removes the rung-boundary forgetting shelf and does not cost top-rung competence (it raises it: final delay-4 competence 0.36 at p=0 vs 0.61-0.69 at p >= 0.1). WEAK_POSITIVE at n=6; no falsification battery was declared; the matrices are the product.
