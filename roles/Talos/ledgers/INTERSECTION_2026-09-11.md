# WHAT IS SEMANTICALLY REAL x WHAT A LIVE CONSUMER ACTUALLY DEMANDS

Currency: 2026-09-11 16:50 UTC. PROVISIONAL: the consumer search (#50) is
OPEN by its own protocol (Hephaestus and Kairos, online at asking, have
no receipt for #50; Arachne one sync without reply). This file is
rewritten, not appended, when TALOS-22 closes it. Operator directive:
"Only that intersection earns a re-premise."

## Left side: what is semantically real (TALOS-24, declared count)

    family                     sampled  semantically real   shape of what is real
    prometheus_math_tests        100          86            executable checks that PASS on today's tree
                                                            (85), property/edge/regression statements
    prometheus_math_modules      100          43            25 docstrings whose checkable claims hold;
                                                            23 embedded tests that PASS; 48 of 76
                                                            implementations named by some test
    theseus_scripts              100          18            1.0 calibration/audit functions, faithful docs
    charon_diagnostics           100          15            1.0 kill-path/cost functions, faithful docs
    hephaestus_* (4 families)    346           3            nothing measurable: no checkable claims

Population estimate from the sample (point estimates only, no gate):
~2,500 executable passing tests in prometheus_math_tests; ~1,200
semantically-real rows in prometheus_math_modules; ~50 in the two script
families; ~150 in the 18,671 forge rows.

## Right side: what live consumers actually demand (TALOS-10, answers so far)

    seat        answer   demanded representation
    Nyx         NONE     none. Conditional READ of hephaestus_* rows as
                         T1-LOCAL provenance when NYX-21 opens and only if
                         Hephaestus agrees. Not a contract; stays NONE
                         unless those conditions occur (operator directive).
    Eos         NONE     none
    Hermes      NONE     none
    Archaeon    NONE     none today. The door: (executable checker,
                         program over a DECLARED SMALL boolean/bit-vector
                         GRAMMAR, both hashable), later tasks sharing parts
                         of earlier solutions; H0 four-cell with the library
                         cheat; baseline = same tasks with shared parts
                         removed; falsifier = library-on == library-off on
                         the eligibility count; extra production none.
    Coeus, Polyhymnia, Arachne, Pheme   NO_REPLY (seen)
    Hephaestus, Kairos                  UNSEEN (online at asking)
    all others                          UNSEEN

Contracts: 0 of 4 answers.

## The intersection

    demanded                              real in the corpus            intersection
    a consumption contract                none received                 EMPTY
    Archaeon's door, condition 1:         YES: ~2,500 passing tests;    present
      spec as an executable checker       48/76 module rows with a test
    Archaeon's door, condition 2:         NO: every row is Python bound  ABSENT
      program over a declared small       to its module (21% closed
      boolean/bit-vector grammar          under builtins); no row is a
                                          program in a declared grammar
    Archaeon's door, condition 3:         YES in the library family:     present
      later tasks share parts of          1,668/2,841 rows call another
      earlier solutions                   family function (generic names
                                          excluded); 595 helpers used by
                                          >= 2 rows
    Nyx's conditional read                hephaestus_* rows as they sit  NOT A CONTRACT
                                          (no production needed)         (conditions not met)

Result: the intersection is EMPTY today. The only named door has one of
its three conditions measurably absent -- the declared small grammar --
and that is the condition the whole contract turns on (an H0 library cell
needs programs whose parts can be shared under a grammar the library
learner sees). Two-thirds of a contract shape is not a contract.

What would change it, on whose side (recorded, not acted on):
- Archaeon's side: if H1 beta declared a grammar into which a subset of
  prometheus_math functions could be compiled, the (test -> function)
  triples in prometheus_math_modules would become candidate tasks. That is
  Archaeon's design decision and a transformation Talos does not perform
  without a contract (operator: do not optimise the corpus for a
  hypothetical consumer).
- Talos's side: nothing. The semantically real residue is characterised,
  preserved byte-identical, and addressable by fingerprint.

## What earns a re-premise

Nothing, as of this currency. No May item is re-premised. The six items
stay CONSUMER-CONTINGENT DORMANT.

## The negative result, if #50 closes at zero (preserved per directive)

A producer created 24,847 artifacts in May 2026; of those, an estimated
~3,800 are semantically real by a declared, controlled, deterministic
count (~2,500 executable passing tests, ~1,200 faithful or oracle-bearing
library functions, ~100 faithful script functions); 4 of 4 answering
seats, including the coordinator of H0-H5, report no mechanism that
consumes any of it. The nearest demand (Archaeon #60) is a grammar the
corpus does not have. "Zero consumers" is therefore not a statement that
the residue lacks structure -- it measurably has some -- but that the
ecosystem has no instrument whose input type is "Python function with a
passing test". Whether that is a gap in the ecosystem or a correct
refusal is the operator's reading, not Talos's.
