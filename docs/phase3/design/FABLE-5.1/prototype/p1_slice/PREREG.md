# P1 calibration slice prototype -- preregistration

Architect: FABLE-5.1 (seat Dionysus). Written 2026-10-01, before qualify.py or
reach.py had been run. This file and the code are committed together in one
commit; the receipts are committed afterwards. The order is in git history.

## What this prototype is

A small working version of experiment P1 from RSE_ARCHITECTURE.md: one world
that demands BUILD (RETAIN), one tiny organism machine (WM-mini), a calibration
set of designed organisms, the rulers, and the qualification gate. It exists
to find out whether the design's central instrument works mechanically, and to
replace an assumed throughput with a measured one.

It is not a Prometheus engine. Nothing it produces is a scientific claim about
reasoning. In the design's own terms its results are C0 observations about an
instrument. The organisms are designed, so there is nothing here to discover.

## Run before this commit (disclosed)

- differential_test.py: compiled kernel against the pure-Python oracle,
  3,672 comparisons, 0 mismatches; its fire test caught a wrong oracle.
- A check of the exact binomial tail code against a brute-force definition
  (0 mismatches on n up to 40).
- builder_min on the 16 training lives: 126 of 126 probes correct. This is
  the designed target of reach.py scored on training lives; it told me the
  target works and how many probes the training block holds.
- The toy-machine throughput benchmark in ../../process/.

Nothing else was run. In particular no calibration verdict, no intervention
and no search had been computed when this file was written.

## Part 1: qualify.py

Fixed in advance (see the constants at the top of qualify.py):

- world: K = 8 stimuli, R = 4 responses, E = 8 episodes, T = 6 trials;
  store 16 cells, fast memory 16 cells; seed 20261001
- sealed lives for reported numbers: 1,200 from life 1,000,000
- significance: alpha = 1e-6, exact binomial; FAIL means "within 0.05 of the
  class bound", also at 1e-6; fewer than 200 eligible trials is INDETERMINATE
- the expected verdict table: the dict EXPECTED in qualify.py

The gate passes only if every section matches EXPECTED and every fire test
fires. There is no partial credit and no post-hoc reading. If a section fails,
the receipt says which, and the prototype is reported as having failed there.

Why the null is exact. For a policy that carries nothing across an episode
boundary, the first probe of each stimulus in a life is correct with
probability exactly 1/R, independently across stimuli and lives, because the
hidden answer is uniform and independent of everything such a policy can know.
Counting one probe per stimulus per life makes the count exactly binomial even
for a deterministic guesser.

## Part 2: reach.py

Fixed in advance (constants at the top of reach.py): target builder_min (8
instructions); knock-out distances 0, 1, 2, 3, 8; three acceptance rules; 24
lineages per cell; 200,000 proposals per lineage; 16 training lives, 64
selection lives, 64 sealed lives; 2,000,000 random programs.

Forecasts, with my probability that each is true (also in reach.py, where they
are scored):

    0.85  F1 margin rule, d=1: recovery rate >= 0.9
    0.80  F2 margin rule, d=2: recovery rate <= 0.2
    0.97  F3 every rule, d=8 (from an empty program): zero recoveries
    0.75  F4 neutral and strict rules, d=1: recovery rate lower than the margin rule's
    0.90  F5 margin rule: recovery rate does not rise as d goes 1, 2, 3, 8
    0.97  F6 random programs: zero of 2,000,000 score >= 0.9 on the training block

Reasoning behind them, so that a miss is informative. The builder is all or
nothing: with any one instruction missing it scores at chance. So a single
missing instruction can be put back by one lucky proposal (about 1 in 10,000),
which a rule that waits for a large jump will find and keep. Two missing
instructions need two specific proposals with no reward in between. A rule
that accepts ties or small gains will meanwhile accept changes to the
instructions that were still right, because at chance level nothing protects
them. I therefore expect a cliff between d = 1 and d = 2 under every rule, and
I expect the tie-accepting rules to do worse than the margin rule even at
d = 1. If F4 fails, my picture of drift at chance level is wrong.

What would count as the measurement itself being broken: any rule failing to
"recover" the intact builder at d = 0 (the positive control of the search
harness). In that case the receipt is void.

## What will be reported

Both receipts as written by the programs, whatever they say. The Brier score
of the six forecasts against an always-0.5 baseline. The measured throughput
of WM-mini with the world in the loop.
