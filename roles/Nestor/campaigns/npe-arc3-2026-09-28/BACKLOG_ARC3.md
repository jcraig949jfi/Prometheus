# ARC3 backlog -- endogenous heredity, reproductive machinery, environmental scaffolding (opened 2026-09-28)

This file extends the P2 backlog (`../npe-p2-endogenous-heredity-2026-09-27/BACKLOG.md`, 40+ Threads) and does not
replace it.

Each Thread records: Q question, W why it matters, E current evidence, X external evidence, U uncertainty,
D cheapest discriminator, R resource, M maturity.

Maturity scale: IDEA -> DESIGNED -> READY (a work package exists) -> RUNNING -> ANSWERED / KILLED.

Resource classes:
- **REPO**: repo/literature only, runs anywhere.
- **LIGHT**: at most 2 processes.
- **LEASED-M1**: world runs on M1 under a cpu8 lease.
- **PORTABLE**: CPU-only, can run on any node with the repo.
- **LENS**: instrument or substrate work.

## Status changes to P2 Threads (Block Q)

| Thread | Change | Evidence |
|---|---|---|
| T-ACQ-2 (presence vs encoding) | MERGED into T-ACQ-9 | acquisition is predicted by carrier exposure (frequency x persistence) |
| T-ACQ-4 (random-walk baseline) | DESIGNED -> READY (WP-9) | neutral-walk pilot: soup/neutral ratio 1.75, p = 0.20 |
| T-ACQ-5 (mutational reachability) | ANSWERED (partly) | OPERAND operator, no indels; 7ae3 opcodes never mutate; the P2 "frame shift" description was wrong (erratum) |
| T-CTX-1 (SELF-free copiers are the norm) | ANSWERED | transplant: 280/280 SELF-free copiers are tape-anchored |
| T-CTX-5 (shorter path) | SPLIT into T-LOC-1 / T-LOC-2 | |
| T-EST-2 / WP-1 (entry-state circularity) | RUNNING | X-A3-FAIR |
| T-DC-1 / WP-2 (child autopsy) | RUNNING | X-A3-AUTOPSY |
| T-END-1 / WP-4 (candidate transition) | RUNNING | forensic delegate on 7ae3 16000006 |
| T-INS-STEP | CLOSED | LDIR is charged per byte; the alias uses the same code path |

## New Threads

**T-ACQ-9 Carrier exposure as the acquisition variable.**
- Q: Is the acquisition hazard proportional to copy-carrier exposure (carriers screened x time)?
- W: This unifies DENSE, PLANT, PLAIN and SHAM with a single parameter.
- E: The hazard fitted on DENSE predicts PLANT 28.6 (32 observed); the reverse fit predicts 54.8 (49 observed).
- U: Only two informative arms.
- D: A new arm that holds frequency fixed and varies persistence, e.g. a planted copy protected from mutation vs
  unprotected. It predicts a 2-5x gap from persistence alone.
- R: LEASED-M1 (~1 h). M: DESIGNED.

**T-ACQ-10 Why does the planted copy disappear?**
- Q: What removes the planted 2-byte copy from the population (0.76 -> 0.16 of genomes)? Candidates are overwriting
  by non-carriers, or the planted copy being deleterious in the wrong place.
- W: If carrying a misplaced copy instruction is costly, accessibility itself has a fitness cost.
- D: Carrier survival vs position of the planted copy (existing X-P2-PLANT checkpoints plus a replay with carrier
  tracking).
- R: LIGHT. M: IDEA.

**T-LOC-1 Tape-rotation world (withdrawing the self-location scaffold).**
- Q: If absolute placement varies per interaction, do tape-anchored copiers fail, and can true locators (SELF plus
  relative destination) arise and establish?
- W: This is the self-location analogue of X-A3-WITHDRAW, and the direct test of "can self-location be
  internalized".
- E: 280/280 SELF-free copiers are tape-anchored; the 2 true locators work at any offset.
- X: Every published soup supplies self-location through its resets (EXTERNAL_RESEARCH); Tierra's cheaters exploit
  registers set by neighbours.
- D: A world axis "placement offset" that is random per interaction. The whole tape is rotated by r before execution
  and back afterwards, which is equivalent for relative code and breaks absolute code. It needs a fail/pass
  self-test with a known tape-anchored copier and a known locator.
- R: LENS + LEASED-M1. M: DESIGNED (WP-7).

**T-LOC-2 The true-locator motif (seed 16000026).**
- Q: How did SELF + LD D,L; LD E,D + LDDR arise? Is it more robust or more evolvable, and does it spread when
  geometry varies?
- D: Lineage replay of X-DD-DENSE-COPY 7ae3 16000026; transplant tests; competition against tape-anchored copiers
  in the T-LOC-1 world.
- R: LIGHT then LEASED-M1. M: IDEA.

**T-STATE-1 State-freedom as the internalized-initialization class.**
- Q: 182/332 copiers set every register they use. Is state-freedom acquired within lineages over time, or present
  from the first donor?
- E: State-freedom predicts robustness (p = 1.5e-28).
- D: Longitudinal census on existing checkpoint genomes (X-DD-DENSE-COPY) using the transplant delegate's
  random-register test.
- R: LIGHT. M: DESIGNED.

**T-SCAF-1 Scaffold ablation matrix (external raid, experiment 1).**
- Q: For each supplied function, what happens if it is removed or varied? The functions: register init, placement,
  wrap geometry, execution order, the copy primitive.
- D: One arm per scaffold, over the same donor panel.
- R: LEASED-M1 / PORTABLE. M: IDEA.

**T-SCAF-2 Coupling arm (Bourrat).**
- Q: Make self-location and copy success one trait (e.g. copy only succeeds if the destination is derived from
  SELF). Does internalization then occur when the scaffold is withdrawn?
- X: Bourrat 2022.
- R: LENS. M: IDEA.

**T-SCAF-3 Collapse probe.**
- Q: Seed a hand-built address-computing (true-locator) donor into the ZERO-reset world vs the CARRIED world. Does
  the world's scaffold make the lineage lose its self-location machinery (Tierra; Baugh 2015)?
- R: LEASED-M1 (~1 h). M: DESIGNED.

**T-SCAF-4 Parent-written prologue.**
- Q: Can a donor write a prologue into the child that sets up the child's next execution (developmental
  initialization)?
- D: Search the existing autopsy records for children whose first bytes differ from the parent in a way that sets
  registers.
- R: LIGHT. M: IDEA.

**T-SCAF-5 Harness audit.**
- Q: List every register, flag, offset and constant that differs between the certification harness and normal world
  execution.
- W: The ruler must not construct the phenomenon.
- R: REPO. M: IDEA.

**T-BASE-1 Full neutral-baseline comparison.**
- Q: Does soup variation-selection reach competence faster than a matched neutral walk?
- D: The preregistered comparison (accessibility/BASELINE_DESIGN.md).
- R: PORTABLE (~9 CPU-h, 2 processes). M: READY (WP-9).

**T-XE-APH-1 Aphrodite comparative Thread.**
- Q: Do NPE and Aphrodite share a law in which "reachable" depends on carrier exposure (persistence of partial
  structure) rather than representation?
- D: Compute Aphrodite's analogue of carrier exposure for its macro vs scratch arms.
- R: REPO + LIGHT. M: IDEA.

## Change log
- 2026-09-28: opened. 11 new Threads. 3 P2 Threads answered or closed, 1 split, 1 merged.
- 2026-09-28 T-STATE-1 ANSWERED: within-lineage internalization of register initialization CONFIRMED (C-A3-INTERNALIZE 8/144).
  Follow-ups: T-STATE-2 (route: which byte changes, how many steps; the lineages from C-A3-INTERNALIZE are now a corpus), T-STATE-3
  (why ffa6 7 vs 7ae3 1: operand mutation of slot offsets 1-3 in ffa6 vs fixed opcodes in 7ae3 -- a mutation-topology hypothesis).
- 2026-09-28 T-END-1 KILLED in single-change form (X-A3-FORENSIC-16000006); superseded by T-STATE-1.
- 2026-09-28 NEW T-DC-5 Copy fidelity: only 6-11% of certified copies are exact and child material is the dominant post-copy loss
  (X-A3-AUTOPSY); do lineages evolve more exact copying (e.g. BC count matched to genome length)? D: exact-copy share over time in
  C-A3-INTERNALIZE / X-DD-DENSE-COPY lineages. R: LIGHT. M: DESIGNED.
- 2026-09-28 NEW T-RULER-1 Heredity certification: P-11 certifies construction (Artemis #793, Odysseus #803); CVT-R on Nestor corpora
  requested (#802). Every future heredity claim needs CVT-R or byte provenance. M: RUNNING (external).
- 2026-09-28 NEW T-RULER-2 Cycle-aware self-state ruler: single-k ruler snapshots cycling state (forensic); X-P2 conclusions survive
  repair (X-A3-ENDOSTATE-R 326/341 agreement). M: ANSWERED.
- 2026-09-28 X-A3-WITHDRAW closed CLEAN_NULL on withdrawal speed; robustness rises within the lineage after withdrawal (0.22 -> 0.94 vs
  control 0.15 -> 0.10). NEW C-A3-WITHDRAW-ROBUST (frozen CONFIRM). M: DESIGNED. R: LEASED-M1 (~2.7 h at 10 procs).
- 2026-09-28 T-SCAF-2 (Bourrat coupling) downgraded: the gradual-withdrawal premise did not hold for register initialization.
