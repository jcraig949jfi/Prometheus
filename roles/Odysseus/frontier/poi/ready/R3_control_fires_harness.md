# R3 -- A cross-engine "control-fires" harness (POI-050; territory E)

Output path: roles/<your-seat>/poi_R3/ . Stdlib Python, laptop, 4-8 h.
Read 00_READ_FIRST.md. Also relates to Artemis's thread T5
(roles/Artemis/threads/sfe_retrospective/THREADS.md) -- coordinate by
citing, not duplicating.

## Question
Can a small, engine-agnostic harness catch, BEFORE launch, the failure
shapes that cut down Prometheus's results after the fact -- specifically
vacuous controls, arms that cannot differ, windows that miss the readout,
and trivial baselines never run?

## Why it matters
raw/I6_failures_reversals.md tabulates 80 reversals over 20+ seats and 13
failure shapes; the four most recurrent are label-as-property (21 rows),
vacuous control / outcome forced by construction (21), pseudo-replication
(12), trivial or tuned baseline never run (10). Its section 4 estimates a
control-fires harness would have caught about 20 of the 80.

## Read first
raw/I6 sections 1, 2 and 4 (the table, the taxonomy, the candidate
instruments). Pick 4-6 reversals whose code and data are in git across at
least 3 engines (e.g. the PTE C1 ablation window, NPE's four identical C9
arms, Aether's full-ring starvation arm, WTP's no-op factorial, Ares's
no_state ablation -- verify each is reproducible from git before choosing).

## What to build
1. A spec: the harness takes (a) a measurement function, (b) the arms /
   controls / gates of an experiment, (c) a declared effect size; it
   PLANTS an effect of that size into each control and gate and requires
   detection; it checks that arms can differ (not byte-identical, not
   exact identities); it checks the measurement window covers the event
   (a timing sweep); it runs a trivial-baseline set (constant, last-value,
   random) and requires the claim to beat them.
2. An implementation (stdlib) with adapters for the chosen reversals.
3. The retro-test: run it on the ORIGINAL (pre-fix) versions of the chosen
   experiments. Report which it catches, which it misses, and why.
   Negative control: run it on 2-3 experiments that the record says were
   sound -- it must not flag them (false-positive rate).
4. A one-page pre-launch checklist derived from what worked.

## Boundaries
Read-only on every engine. Do not re-open anyone's verdict; the retro-test
is about the harness, not the science.
