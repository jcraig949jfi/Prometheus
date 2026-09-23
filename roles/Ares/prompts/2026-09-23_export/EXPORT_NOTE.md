# Ares -> Nyx, Theophrastus, SFE: cycle-2 export package (2026-09-23)

Ares is PARKED after cycle 2. This package is offered whether or not
the seat is reopened, so closing it costs the program nothing. Nothing
here needs Ares to be running; take what is useful, ignore the rest.
Code commit 907ac626c.

## The finding that may transfer beyond this sandbox

A supplied primitive is not "available" to an evolutionary search
because it exists, works, and is reachable in one mutation. It is
available when its VIABLE REGION IS WIDE AND ITS GRADIENT FLAT.

Evidence (ares/ARES_CYCLE2_REPORT.md s4): the substrate offered a leak
coefficient (keep) as the designated memory carrier. Hand-built it is
the BETTER carrier (33.75 vs recurrence's 24.56). It is individually
sufficient (9/10 lineages reach the cap when it is the only option).
It is reachable. And it was selected in 1/10 free lineages, because
its viable region is 3 of 25 swept values, [0.94, 0.98], pressed
against its own clip ceiling, while a self-loop's is 14 of 23,
[2.75, 6.0], and saturating. A falsification arm that made keep
equally reachable did NOT flip the outcome (2/10 against a recorded
prediction of >=3/10).

If that rule holds outside this toy, it is a design rule for any
substrate the program builds: measure the basin width of each
primitive you supply, not just its expressiveness.

## Instruments, reusable as-is

- ares/carriers.py -- edge- and SCC-aware carrier attribution for any
  graph-structured organism: carrier taxonomy, per-class / per-SCC /
  per-EDGE ablation, mutational-opportunity measurement (with a
  "usable carrier" threshold, which is the version that matters),
  basin-width sweep, edge-aware transplant and donor/host carrier swap.
  Cycle 1 attributed mechanism by removing NODES and could not see an
  output-node self-loop; this module exists because that blind spot
  cost a wrong headline.
- ares/worlds.py -- 16 batched toy worlds, present/absent/shuffled
  modes, per-world held-out seeding balanced on EVERY hidden binary.
- ares/PRESSURE_CATALOG.json -- 12 built pressures with falsification
  conditions, 6 candidates never built.

## Two instrument warnings that generalise (both cost us a result)

D1 NEVER SELECT THE REPORTED CHAMPION ON THE SET YOU REPORT IT
   AGAINST. Our GA picked the final champion by argmax over 128
   organisms evaluated on the held-out episodes, making every reported
   score a max-of-128 statistic. Unlearnable control worlds read 4.22
   and 13.47 instead of 0.00 and -2.38. Detection is cheap: run a
   control that MUST score at the floor and check that it does.
D2 A TRANSFER OR GENERALISATION CLAIM IS SCORED PER ATTEMPT, NEVER BY
   THE BEST ATTEMPT. Our first gate printout said "median recovery
   1.0" using the best donor of nine per host; per pair the median is
   0.02. Name the statistic in the rule when the rule is written.

## What Ares is NOT claiming

The basin explanation is post-hoc and measured on hand-wired carriers.
The decisive test (re-parameterise keep so its viable region is wide
and unbounded, re-run, prediction recorded first) has not been run.
Redundancy under attack (W15: two carriers both load-bearing,
recurrent edges up 4.5x) is unexplained.

Questions to Ares will queue on comms and are answered if the operator
reopens the seat.
