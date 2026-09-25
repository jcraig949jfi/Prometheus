# S1-B -- H4 extinction autopsy: `64dea50f417efb02-s1203-tL-a0`

Currency 2026-09-23. Machine record: `H4_AUTOPSY.json` (per-epoch series for every run),
produced by `h4_autopsy.py` on the forensic substrate. The frozen record is untouched.
These are forensic replays. They are not retroactive 72-hour evidence.

## Verdict

**The 4x runtime difference is not early extinction, not population size and not
validation frequency.** The endogenous arm **never reproduces**. There are zero ALLOC
calls, zero births, zero deaths and zero mutations in 4,000 epochs, so the population is
the 384 seeded reader ancestors, unchanged. Each halts after 11 instructions per slice.
The external arm reproduces 5% of its population every epoch; its mutated genomes run
longer and miss the validation cache. The cost difference is execution plus
cache-missing validation of a population that changes, against one that never does.

**A-4 is not endogenous accessibility.** The endogenous run's held-out score moves only
because `COEVO_ENV` keeps changing the task under a population that never changes. Its
first crossing, at epoch 636, happened with no genome having changed since epoch 0. And
**the exact matched control also crossed**, at epoch 48, before the endogenous run did.
It then lost the crossing to undirected mutation (pressure `NONE_IMPLICIT`).

## Runs

| id | run | kind | tier / seed | epochs | births | deaths | pop min-max | ops | wall | first cross | held >= 0.90 epochs | final held |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T | `64dea50f417efb02-s1203-tL-a0` | frozen replay, REPLAY_MATCH | L / 1203 | 4000 | **0** | **0** | 384-384 | 16.9 M | 33 s | 636 | 1,072 | 1.0 |
| EXACT | partner cell `d0f78df5558316cb` at s1203 L | **new forensic run** | L / 1203 | 4000 | 76,000 ext | 76,000 reaped | 384-384 | 451.7 M | 453 s | **48** | 60 (48-179) | 0.0 |
| USED | `d0f78df5558316cb-s1816-tM-a0` | frozen replay, REPLAY_MATCH | **M / 1816** | 2000 | 24,000 ext | 24,000 reaped | 256-256 | 105.5 M | 106 s | never | 0 | 0.0 |
| SIB | `64dea50f417efb02-s1816-tM-a0` | frozen replay, REPLAY_MATCH | M / 1816 | 2000 | **0** | **0** | 256-256 | 5.6 M | 10 s | 50 | 330 | 0.625 |

Validation epochs are identical within a tier: 334 at L and 200 at M. Extinction time
is none in every run. Genome diversity in T is 384 unique at epoch 0 and 384 unique at
epoch 4,000, all distinct only in their random padding.

Cost decomposition for T against EXACT, with the same epochs, the same population and
the same validation schedule:

- execution: 11 against 294 ops per organism per epoch, 26.7x;
- validation wall: 16.4 s against 184.3 s, 11x, because T's genomes never change and
  validation is cached by genome, except that `COEVO_ENV` clears the cache every 25
  epochs;
- non-validation wall: 16.8 s against 268.5 s.

The Cycle-9 smoke pair, re-run on the Cycle-9 substrate at the smoke's 120 epochs,
reproduces the 4x on its own seed (9,400,000): endogenous 0.80 s, 0 births, 11.0 ops
per slice; external 3.17 s, 2,280 births, 51.6 ops per slice; 384 organisms in both;
held_max_ever 1.0 in both.

## Two defects this exposed

**Z80A-D04 -- the "matched control" was not matched.** The flag compared the tier-L,
seed-1203 endogenous run with `d0f78df5558316cb-s1816-tM-a0`, which is tier **M**, seed
**1816**: the control of the M-tier sibling T was promoted from. The scheduler stores
`control_summary` per **family** and fills it from any control whose `control_of` is
any run in that family (`scheduler.py` `on_complete`), so a promoted run inherits a
sibling's control. The frozen record holds **no** control at T's seed and tier. Measured
across all 65 `REACHED_ONLY_UNDER_ENDOGENOUS_REPRODUCTION` verdicts: **64 were adjudicated
against a control not run for the flagged run** (50 WEAK, 13 INADMISSIBLE, 1 ADMISSIBLE);
the single flag with its own control adjudicated INADMISSIBLE. A-4's "matched external
control at 0.0" is withdrawn as unmatched. Recorded, not patched: the
frozen record stays as it is.

**C9-D07 -- H4's endogenous arm cannot reproduce, so H4 cannot test accessibility.**
`SEEDED_READER` seeds a task reader with no ALLOC/BIRTH code. With no births there is
no mutation, because this substrate mutates only at birth, so the arm is a frozen
population. Block B (`RANDOM` seeding) does not escape this: S1-A finds that FREE-policy
random populations produce zero births. Block C (`STATIC` environment) would freeze the
held score too. H4's decision rule reads final held >= 0.90, and for a frozen reader in
`COEVO_ENV` that is set by where the environment happens to be at the last epoch.

## Consequence for S4

Enlarging H4 from 16 to 32 seed-pairs buys a sharper estimate of an environmental coin
flip. **H4 is therefore not enlarged in the candidate manifest; it needs redesign
first**, which is the directive's stated exception. Redesign options are in
`S4_CANDIDATE.md` for operator decision. None is implemented.
