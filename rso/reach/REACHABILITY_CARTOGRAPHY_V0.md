# REACHABILITY CARTOGRAPHY v0 -- a reusable protocol for characterising a search desert

C-013-T010 (Argus[harry1-6417c3ea], claude-opus-5-5), 2026-10-10. Authority: operator Strategic Expansion Directive
2026-10-10 s5 and Operator Ruling 2026-10-10 s2-s3 (roles/Palamedes/prompts/2026-10-10_strategic_expansion/01_*, 02_*).
Sources: Atlas G1-G6 (roles/Atlas/proposals/2026-10-02_reachability_go_explore/), Nyx's attack
(roles/Nyx/ATTACK_reachability_go_explore_2026-10-03.md) and corrected ladder (nyx/atlas/experiments/reach_archive/
@ 3318a2098), Hestia Audit 1 bottleneck vocabulary (digest: roles/Palamedes/notes/2026-10-10_strategic_sources/01_*).
Status: v0, a protocol. Its one worked example (s6) is filled only with measurements that exist; the D1 demonstration
that fills two more rows is preregistered in PREREGISTRATION.md and has NOT been run.

## 1. What a desert is, and what this protocol refuses to say

A DESERT is a pair (target mechanism, search process) where the target is known to exist -- a constructed solution
is in hand -- and the search, at its budget, does not produce it. The protocol characterises the pair, never the
target alone and never the substrate in general.

Three refusals, binding on every sheet:

1. NEVER IMPOSSIBILITY. "Not reached" is always written "0 of n lineages within B proposals; one-sided 95% upper bound
   u on the per-lineage rate", u = 1 - 0.05^(1/n) for 0/n. A desert is budget-relative. Hestia's own amendment M1
   softened the composition wall to "a strong prior for the tested representations; not a proof".
2. NEVER A SEEDED PATH AS A DISCOVERY. A hand-written stepping stone, plant, curriculum or breadcrumb that makes the
   target reachable demonstrates that a path EXISTS. It is reported in a separate CONTROLS section and is never
   pooled with, or counted as, a solution the search found (directive s5: "That demonstrates a possible path. It does
   not demonstrate that the evolving system can discover the path independently.").
3. NEVER TRAINING FITNESS AS SUCCESS. A hit is a candidate until certified by rulers on held-out (selection) and
   sealed data, with an independent recomputation (rso/reach/certify.py is the reference pattern). Training-perfect
   but uncertified hits are reported as such.

## 2. The five questions (Hestia M2 vocabulary: EXPRESS / REACH / REWARD / CREDIT / DETECT)

For a target T and search S, in this order -- each answer conditions the next:

| # | question | the measurement that answers it | typical failure label |
|---|---|---|---|
| Q1 EXPRESS | Can the substrate represent T at all? | a constructed genome that certifies (the positive control); its size | EXPRESS (no construction exists) |
| Q2 REACH | Can S's operators produce T from where S starts? | operator distance d(start, T); hitting-time distribution at matched budget; descent from the plant (d components removed) and ascent from random | REACH (constructible but rarely produced) |
| Q3 REWARD | Would T's behaviour earn an advantage over the incumbents if produced? | T's fitness vs the incumbent population's; the selection rule's acceptance of T | REWARD (T found but not kept) |
| Q4 CREDIT | Would useful partial constructions receive detectable reinforcement? | the fitness of every intermediate on shortest operator paths, against equal-score arbitrary genomes | CREDIT (no gradient toward T) |
| Q5 DETECT | Would our instrumentation recognise success, and see the intermediates? | certification of T (ruler can pass); a planted near-miss the ruler must fail; descriptor separation of intermediates | DETECT (a ruler that cannot fail, or cannot see) |

Only after these are separated is an intervention chosen; the interventions the directive lists (representation,
operators, reusable modules, neutral-intermediate preservation, structured partial credit, curriculum, lifetime
learning, preservation across generations) are competing explanations, each matched to a failure label, never pooled.

## 3. The measurement sheet (directive s5, the ten minimum measurements)

Each row: what is measured, the cheapest protocol that measures it, the reported form. Sparse and experimentally
meaningful; no exhaustive map of an astronomical space is required anywhere.

| M | measurement | minimal protocol | reported as |
|---|---|---|---|
| M1 | target density or bounded estimate | N uniform draws from the operator's own genome distribution, scored by the SAME certification as search hits | k/N and the one-sided 95% upper bound; plus needle bits (exact-match description length under the operator's distribution, an upper bound because equivalents exist) |
| M2 | smallest known construction | the shortest certified genome in hand; knock-out test that every part is needed | size, listing, per-part knock-out result |
| M3 | distance under the actual operators | edit distance in the operator's own move set (not Hamming on an unrelated encoding) from each start used | d per start; the number of shortest paths |
| M4 | known viable intermediates | enumerate genomes on shortest operator paths (for d <= ~10 rows this is 2^d - 2, cheap); score each | count; score of each; which certify any partial ruler |
| M5 | hitting-time distribution | n independent lineages per (arm, d) at a frozen budget B; record proposals-to-certified-hit | rate with upper bound; rate by budget checkpoints (e.g. B/100, B/10, B); median hit time; never a mean over censored lineages |
| M6 | loss or preservation of stepping stones | per lineage: path intermediates EVALUATED, path intermediates RETAINED at the end (population / archive / chain parent), most restored | counts per lineage (lower bounds if equivalence classes are not enumerated) |
| M7 | sensitivity to representation | the same target under a second genotype encoding or operator set, same budget, same certification | paired rates; d under each encoding |
| M8 | sensitivity to credit structure | the same search with (a) the native fitness, (b) a structured partial-credit fitness, (c) a shuffled/yoked-credit control | paired rates; the control must not help |
| M9 | behaviour under archive / novelty search | the separated ladder of s4 (never a bundled "Go-Explore-like" arm) with a matched structure-free archive control | per-contrast exact test, multiplicity-corrected |
| M10 | behaviour under modularity / developmental promotion | the search with a module library or promotion operator vs (a) none, (b) a random library of matched size, (c) a shuffled-history library (Hestia M5) | paired rates with the controls; archive-off final evaluation |

Order of cost: M1-M4 are cheap (minutes) and come first; they often explain the desert before any search arm is run
(s6 shows this). M5 is the reference search. M6 is free once M5 runs (it is instrumentation in the same lineages).
M7-M10 are the expensive interventions and are only run when M1-M6 point at the failure label they address.

## 4. Five mechanisms that must not be collapsed into "exploration" (directive s5)

| mechanism | what it is | the arm or measurement that isolates it | what it is NOT |
|---|---|---|---|
| retaining promising genomes | a population or archive keeps genomes the current lineage has left | X1 (archive, greedy parent) vs the neutral chain, same acceptance (Nyx ladder) | environment-state restoration |
| preserving neutral stepping stones | equal-score variants are accepted and can be built on | strict chain vs neutral chain (S2 vs S3); M6 counts; X3 vs X2 only where the stone is BEHAVIOURALLY distinguishable (s5) | admission of worse candidates |
| restoring previously reached environment states | returning the WORLD (not the genome) to a state reached before, then exploring from it, without re-traversal (Go-Explore's mechanism) | only in worlds whose state is not the genome (Hestia names Crius; Tyche T4 unchecked). NOT testable on any genome-is-state target | genotype copying. On p1_slice the program IS the state: copying an archived program is genome retention, never "state restoration" (Nyx B2) |
| discovering useful paths through genotype space | the search finds a route of viable intermediates under its own operators | M3/M4 enumeration of shortest operator paths + M6 in the lineages; G2-C5/G4 once rebuilt on shortest operator paths (Nyx M2) | a hand-written breadcrumb trail (that is a seeded control) |
| maintaining populations around incomplete mechanisms | many lineages near a partial mechanism, kept despite no current advantage | a population arm (S1-like, many parents, no archive) vs chain; no isolating arm exists yet in G1-G6 (digest 02) | retention of single elites |

Vocabulary rule: an archive of genomes with count-weighted parent choice and new-cell acceptance is MAP-Elites with
count selection (Nyx A3), not Go-Explore. "Detachment" may be used only in the population-genetic sense and only if
the retention contrast (X1 > chain) separates (Nyx DESIGN s5).

## 5. Instrument rules (each one a test, not prose)

- The cell / behaviour descriptor is a RULER and must be qualified before any archive arm is read: (R1) it separates
  shortest-path intermediates from equal-score arbitrary genomes; (R2) it does not over-split behaviourally identical
  genomes; and two planted must-fail controls show the qualification CAN fail (a fitness-only descriptor must fail R1,
  a genotype hash must fail R2). Report the realised cell count against distinct genomes visited (Nyx A4.1).
  Reference: rso/reach/descriptor.py.
- A structure-free archive control (genotype-hash cells) with bucket count MATCHED to the behaviour descriptor's realised
  cell count, calibrated outcome-blind (rso/reach/calibrate.py), accompanies every behaviour-cell archive arm.
- Stochastic fitness: re-evaluate a cell's incumbent on fresh lives before replacement (Nyx A2). (p1_slice fitness is
  deterministic on a fixed training block, so this does not arise there.)
- Power is computed against the OBSERVED baseline, not zero: on p1_slice the chain baseline is 1/24, so 6/24 is p = 0.097
  two-sided Fisher, not 0.022 (digest 02; checked by rso/reach/tests/test_stats.py).
- Any implementation port (e.g. numba) is differential-tested against the reference implementation exactly.

## 6. Worked example: the FABLE-5.1 p1_slice reach world (T5), as far as it is measured today

Target builder_min (8 instructions, docs/phase3/design/FABLE-5.1/prototype/p1_slice/organisms.py:96-111); operator:
one whole instruction row replaced by a uniform draw (reach.py:105-111); fitness: correct BUILD probes on 16 fixed
training lives (126 probes); certification: selection lives + sealed class-exclusion ruler.

| M | value | source |
|---|---|---|
| Q1 EXPRESS | YES: builder_min certifies (training 126/126; sealed class-exclusion PASS) | reach.py receipt d=0 controls 24/24 each regime; rso/reach tests (certify) |
| M1 density | 0 of 2,000,000 uniform programs reach 0.9 of the training probes; 95% upper bound 1.5e-6; best random 42/126; needle <= 65.0 bits | RECEIPT_reach.json "random" |
| M2 smallest construction | 8 instructions, each needed (knock-out of any one drops to chance) | organisms.py:96-111; s6 M4 row |
| M3 distance | d = number of knocked rows (row-replacement operator); one shortest path per order of restoration (d! orders) | rso/reach/arms.py _path_restored |
| M4 viable intermediates | 254 shortest-path intermediates (any proper row-subset of the target, rest NOP). EVERY one scores at the always-answer-0 level (32/126) or below (one scores 20). NO partial credit exists along any shortest path | rso/reach/DESCRIPTOR_QUALIFICATION.json (intermediate_scores [20, 32]) |
| Q4 CREDIT | NONE on shortest paths under the native fitness: the desert is a credit desert first | M4 |
| Q5 DETECT (target) | ruler passes on the target, fails on four impostors, VOIDs on an oracle disagreement (fire test) | rso/reach/tests/test_certify.py |
| Q5 DETECT (intermediates) | C-BEH (per-type correct counts) separates intermediates from equal-score arbitrary genomes in 0.6% of pairs (R1 FAIL); the FULL action trace separates them equally rarely: 99.4% of equal-score others have an IDENTICAL trace. Where traces differ, C-BEH separates 100% (R1c PASS); no over-splitting (R2 1.0); both planted must-fail controls fail as required | rso/reach/DESCRIPTOR_QUALIFICATION.json |
| M5 hitting time (chain) | at B = 200,000: neutral chain 1/24 (d=1), 0/24 (d=2), 1/24 (d=3), 1/24 (d=8); strict 9/24, 1/24, 0/24, 0/24; margin 24/24 at d=1, 0/24 at d >= 2 | RECEIPT_reach.json "cells" |
| M6 stepping stones | not yet measured; instrumented in D1 (stones evaluated / retained per lineage) | PREREGISTRATION.md s6 |
| M7 representation | not measured (out of D1's scope) | -- |
| M8 credit structure | not measured; M4 says it is the first lever to test | -- |
| M9 archive / novelty | D1, preregistered, not run | PREREGISTRATION.md |
| M10 modularity / promotion | not measured | -- |

What the measured rows already say, before any archive arm runs: on this target the intermediates are invisible to
reward AND to any training-behaviour descriptor. A behaviour archive therefore cannot keep shortest-path stepping
stones apart from arbitrary genomes; any archive advantage D1 finds must come from somewhere else (off-path routes,
diversity of parents, admission of worse genomes), and D1's interpretation rules (PREREGISTRATION.md s7) say so in
advance. The next cheapest informative measurement after D1 is M8 (structured partial credit vs a yoked control),
because M4 locates the barrier at CREDIT.

## 7. The sheet a future desert fills (machine-readable form)

    {"schema": "prometheus.reach.cartography_sheet.v0",
     "target": {"name", "construction_ref", "size", "certifier_ref"},
     "search": {"operator_ref", "fitness_ref", "budget", "acceptance"},
     "Q": {"EXPRESS", "REACH", "REWARD", "CREDIT", "DETECT"}: each {"answer": YES|NO|UNMEASURED, "evidence_ref"},
     "M1".."M10": each {"value", "upper_bound_95" (for zeros), "n", "budget", "evidence_ref", "status": MEASURED|UNMEASURED},
     "controls": {"seeded": [...], "must_fail": [...]},      # never pooled with discoveries
     "failure_label": one of EXPRESS|REACH|REWARD|CREDIT|DETECT|UNRESOLVED,
     "next_measurement": "the cheapest unmeasured row that could change the failure label"}

Rows are filled from receipts by file:line; a value without a committed source is UNMEASURED.

## 8. Limits of v0

- One worked example, on a genome-is-state world; environment-state restoration has no test bed here (s4).
- Path enumeration (M4) is exact only for small d; beyond ~20 differing units it must be sampled, and the sheet says so.
- Equivalence classes (synonymous genomes) make M6 counts lower bounds unless enumerated.
- Nothing here compares engines; the directive forbids turning this into a cross-engine campaign.
