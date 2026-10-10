# THESEUS-41 verdict: SYN injection WITHOUT task selection (prereg roles/Theseus/prereg/2026-10-09_syn_inject_rep/, 166c6c93e)

Runs: PYTHONHASHSEED=0, master seed 20261009, --quality rep, flags as 38 S2-REP plus
--inject, --workers 2 each:
- REP-S v0_2tr_s2_injS_2026-10-09 (inject_S)
- REP-M v0_2tr_s2_injM_2026-10-09 (inject_M)

Eval: python -m theseus.synth.task_comp --tag comp_task_syn_rep_2026-10-09
--a v0_2tr_s2_injS_2026-10-09 --b v0_2tr_s2_injM_2026-10-09 --workers 2.

GATE: 1-part controls .195-.2025; 2-part controls 1.0. PASSES.

## Primary: H-SYN-REP
D solvers (J >= .6), 100 viable DEEP+VERY_DEEP children per run:

| run | solvers | mean J |
|---|---|---|
| REP-S | 79/100 | .832 |
| REP-M | 81/100 | .840 |

One-sided Fisher p .70; RD -.02 [-.131, .091].
VERDICT: NOT SUPPORTED. Under reproducibility selection, re-injected SYN concepts do not raise
deep solver share over matched non-solving deep matter.

## Descriptive

Attribution:

| | REP-S | REP-M |
|---|---|---|
| solvers with every essential part a verbatim injected rule | 15 | 7 |
| solvers with any copied essential part | 20/53 | 18/53 |
| copied essential rules | 23/77 (20 laws) | 22/79 (15 laws) |
| essential-rule provenance | law 49, mutation edit 27, G0 1 | law 55, mutation edit 18, G0 3, lens 3 |

Redundant solvers (no single essential rule): REP-S 26/79, REP-M 28/81.

Beside 39 (task0, same base seed): the task0 RD was .13. Under rep, RD -.02.

Against the un-injected rep run of the same base seed (38 S2-REP v0_2tr_s2_2026-10-08:
63/100), both injected rep arms are far higher (79, 81). This is not preregistered and is
confounded by lane timing (injected genomes open the deep lanes from gen 1; see the 39
prereg). It is descriptive only: any deep, law-bearing injected matter appears to raise
deep solver share under rep selection, whether or not its source solved the task.

## Reading
The SYN-specific advantage seen under task selection (39 and 42 pooled: RD .09 [.007, .173])
does not appear without task selection.
- SYN rules are inherited more often as whole solutions (15 vs 7), but the rate does not rise.
- The deep matter itself, solving or not, carries laws that become working parts.
Compressed concepts are not useful matter on their own. Their small benefit shows only when
selection also favours the task.

## Predictions

| id | prediction | outcome |
|---|---|---|
| U1 | direction S > M (p .65) | WRONG (79 vs 81): ledger |
| U2 | SUPPORTED (p .4) | did not occur, in line with the stated probability |
| U3 | REP RD < task0 RD .13 | -.02, RIGHT |
| U4 | more all-copied solvers in REP-S | 15 vs 7, RIGHT |
