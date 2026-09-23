# S1-A -- replication failure funnel, non-PAIR_EXECUTION random starts

Currency 2026-09-23. Machine records: `FROZEN_FUNNEL.json` and `FROZEN_FUNNEL_RUNS.jsonl`
(the frozen record), `REPLAY_FUNNEL.json` (the forensic replays), `REPLAY_SELECTION.json`
and `replay_ids.txt` (the 256 selected runs and the rule that selected them).

The replays are a **new forensic assay, not retroactive 72-hour evidence**. Each one
re-executed its frozen run with telemetry added and was checked field for field against
the frozen summary: **256 of 256 REPLAY_MATCH**.

## 1. Frozen-record funnel (1,255 runs, run-level)

Status labels: NOT_MEASURED means the frozen counters cannot establish the step.
NOT_APPLICABLE means the cell's self_location is NONE, so there is no self-location
operation. A LOWER_BOUND count is proven by the record but may be too small.

| step | ENDOGENOUS_COPY (323) | ENDOGENOUS_PARTIAL (306) | CONSTRUCTIVE (278) | OVERWRITE (348) |
|---|---|---|---|---|
| self-location executed | NOT_MEASURED (201), N/A (122) | NOT_MEASURED (205), N/A (101) | NOT_MEASURED (187), N/A (91) | NOT_MEASURED (246), N/A (102) |
| ALLOC attempted | 41 (p .127, loss 282) | 37 (.121, 269) | 33 (.119, 245) | 321 (.922, 27) |
| ALLOC succeeded | 36 (.878, 5) | 34 (.919, 3) | 29 (.879, 4) | 290 (.903, 31) |
| target writes | 14 (.389, 22) | 12 (.353, 22) | 13 (.448, 16) | >= 218 LOWER_BOUND (130 NOT_MEASURED) |
| BIRTH attempted | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | >= 227 LOWER_BOUND |
| birth accepted | **0** | **0** | **0** | 227 (.783 of alloc-succeeded) |
| fidelity >= 0.90 | 0 | 0 | 0 | **0** (loss 227) |
| offspring evidence-backed child | 0 | 0 | 0 | 0 |

Event totals, FREE-policy physics combined: 362k successful ALLOCs and **zero births of
any kind**. In all 907 FREE runs every surviving genome is unique and the population
only shrinks. This substrate mutates only at a birth, so **these populations never
varied**. OVERWRITE: 3,075 births, 2,451 of which wrote bytes, and none at fidelity >= 0.90.

## 2. Forensic-replay funnel (256 runs, 64 per physics, per organism)

Sequential means an organism did step k after it had done steps 1 to k-1 itself.
Under NONE, step 1 does not apply, and those organisms enter at step 2. The
self-location row counts NONE organisms (`organisms_self_location_NONE`) as passing by
definition; the column on the right shows how many locating organisms actually executed
a self-location op.

| step | ENDOGENOUS_COPY | ENDOGENOUS_PARTIAL | CONSTRUCTIVE | OVERWRITE |
|---|---|---|---|---|
| organisms (of which NONE) | 16,384 (5,632) | 17,024 (5,888) | 17,024 (5,632) | 18,832 (6,469) |
| locating organisms that executed self-location | **6** of 10,752 | **13** of 11,136 | **5** of 11,392 | 1,612 of 12,363 |
| ALLOC attempted | 16 (p .0028) | 3 (p .0005) | 7 (p .0012) | 1,418 (p .175) |
| ALLOC succeeded | 15 (.94) | 1 (.33) | 7 (1.0) | 1,060 (.75) |
| target writes | 3 (.20) | 0 (.0) | 3 (.43) | 734 (.69) |
| BIRTH attempted | **0** | 0 | **0** | 130 (.18) |
| birth accepted | 0 | 0 | 0 | 128 (.98) |
| fidelity >= 0.90 | 0 | 0 | 0 | **0** (loss 128) |
| offspring evidence child | 0 | 0 | 0 | 0 |

Marginal (ever, any order): ALLOC attempted 29 / 18 / 9 / 3,731 organisms; BIRTH
attempted 10 / 24 / 8 / 3,618; birth accepted 0 / 0 / 0 / 543.

**The decisive event count.** Across the 192 FREE-policy replays there were 114,485
BIRTH/SPLIT executions, and **every one of them had no pending allocation**. The
organisms that allocate never declare a birth, and the organisms that declare never
allocate. The per-stratum counts sit at multiples of the epoch count (2,000 at tier M),
so each is one or two organisms looping the same instruction every epoch. OVERWRITE:
108,018 of 108,674 BIRTH calls had no pending allocation; 656 were accepted.

Per self_location x copy_primitive, see `REPLAY_FUNNEL.json`. No stratum of a FREE
physics produced a birth. OVERWRITE births occur in every stratum, between 68 and 140
per 10 or 11 runs.

## 3. What this says about the five hypotheses

| hypothesis | FREE physics | OVERWRITE |
|---|---|---|
| random programs never find the reproduction API | **mostly true**: 0.05-0.3% of organisms ever call ALLOC | false: 20% call ALLOC |
| they allocate but cannot copy | too few allocators to say; 3 of 29 write the target | 69% of successful allocators write the target |
| they copy but cannot declare birth | **true in the strong form**: no allocator ever declares, no declarer ever allocated | 18% of writers declare, 98% accepted |
| a first faithful child immediately dies | never reached | never reached: **0 of 656 births at fidelity >= 0.90** |
| the detector treats the physics asymmetrically | **yes, but through the physics before the detector** (below) | same |

**The asymmetry that decides it is in the physics, not the private-slot detector.**
`PAIR_EXECUTION` mutates **every paired organism every epoch** (`_pair_epoch` calls
`_mutate` on both halves unconditionally), so a pair-tape population is always
searching. The four non-pair physics mutate **only at a birth**. A FREE-policy random
population that produces no birth therefore runs the same 256 or 384 random programs
unchanged for the whole run, which is no search at all. OVERWRITE escapes partly,
because ARENA writes let organisms rewrite one another. Comparing replication rates
across the two families compares a search against no search.

S1-C adds a second asymmetry on the pair side. The pair detector reads fidelity after
`_mutate`, and under the RECOMBINATION axis `_mutate` splices in a random living
organism.

## 4. What the next exploratory campaign should deform (for S8, not decided here)

1. **Give the non-pair physics a search.** Mutate each organism in place at a declared
   rate per epoch, not only at a birth. Without this, "no spontaneous replicator"
   under FREE physics is a statement about zero variation.
2. For FREE physics, **the protocol is the barrier**: ALLOC and BIRTH never co-occur in
   one organism. The deformation to test is a compressed protocol, such as a
   single-operation "birth from this span" or an ALLOC that declares automatically.
3. For OVERWRITE, **fidelity is the barrier**: births happen, faithful ones do not.
   The deformation to test is the copy primitive and the cost of a loop.
