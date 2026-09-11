# nyx/ -- the Prometheus Chop Shop

Currency: 2026-09-11 (opened on charter day). Seat: roles/Nyx/. Charter:
roles/Nyx/prompts/2026-09-11_charter/CHARTER_verbatim.md.

The Chop Shop disassembles computational machinery -- external systems
and Prometheus's own -- into two independent kinds of substrate for the
Serendipity Foundry Engine's ecology:

    ORGAN     a transferable mechanism, cut below the famous name, with
              the charter's fifteen questions answered or marked unknown,
              and ancestry preserved through every cut
    PRESSURE  an environmental condition under which some capability
              gains fitness, stated WITHOUT naming the organ, with the
              world requirements, the vacuity condition, the trivial
              shortcuts to close, and a cheat control

Organs and failure landscapes go to Archaeon (ecological coordinator).
Pressures go to Vivarium (world builder). Nyx never builds the world for
her own pressure; the idea must cross a seat boundary first.

## Layout

    chop/schema.py          record checks (SPECIMEN / ORGAN / PRESSURE), v0
    chop/fixtures/          negative, positive and cheat records
    tests/test_schema.py    the validator's self-falsification; also
                            validates every committed specimen record
    specimens/QUEUE.md      the specimen queue, with consumers
    specimens/<name>/       one directory per specimen:
        specimen.json       what it is, famous names, provenance sources
        PROVENANCE.md       ancestry with evidence grades (T1/T2/T3)
        organs/*.json       ORGAN records
        pressures/*.json    PRESSURE records
        FAILURES.md         failure landscape, ablations, decoys
        AMBIGUITY.md        alternative cuts, preserved not merged
        DELIVERIES.md       what went downstream, to whom, comms id, reply

Run the checks:

    python -m pytest nyx/tests -q
    python -m nyx.chop.schema nyx/specimens

## Evidence grades (operator ruling NYX-25, 2026-09-11)

The grade travels with the artifact. Admission to the parts bin is not
validation; a literature-derived organ may enter a soup without its
historical claims being treated as fact; a grade is never upgraded
because a descendant later performed well.

    T1-LOCAL   locally observed or reproduced: a committed receipt,
               run, test or row in this repository
    T1-SOURCE  verified primary source or code: a resolver-checked DOI
               or a pinned commit (the identifier, not the content)
    T1         unsplit, records written before the ruling (MAP-Elites
               v0): one of the two above, see the ref text
    T2         literature or history attribution not independently
               verified (a remembered claim about what a work says)
    T3         Nyx inference or conjectured decomposition; hearsay

A resolved DOI makes the IDENTIFIER T1-SOURCE; what the work SAYS stays
T2 until a passage is quoted. Techne's receipt stages (INSTALLATION,
FIRST_USEFUL_CHECK, PAPER_REPRODUCTION, ADAPTER_QUALIFICATION,
LOCAL_SCIENTIFIC_BENEFIT) are the existing vocabulary for what local
evidence establishes, and a provenance file cites them as written.

## Routing (operator ruling NYX-27, 2026-09-11)

Material goes to an actual addressable seat (python -m comms roster).
No convenience seat is created to satisfy a label: there is no
Necropolis seat, so endogenous corpses are routed to the seat that owns
the machinery, or preserved through the branch protocol
(origin/necropolis/* exist) with the missing receiving capability
reported to Archaeon. Verify capability, not label.

## When a consumer returns (operator direction 2026-09-11)

A consumer's first substantive return outranks finishing another
specimen. On a return: (1) reach a clean stopping boundary in the
current dissection; (2) inspect the result; (3) record in the
specimen's DELIVERIES.md whether the pressure was executable, vacuous,
shortcuttable, non-discriminating, or useful; (4) record whether it
changes the decomposition assumptions; (5) record explicitly whether it
changes how the NEXT specimen is cut; (6) continue. The test is whether
downstream consequences change how the next machine is chopped.

## The diagnostic chain (a reading of DELIVERIES.md, not a state machine)

    PRODUCED -> DELIVERED -> CONSUMED -> SELECTED-ON ->
    CONSEQUENCE OBSERVED -> METABOLIZED

Each DELIVERIES.md row is read against this chain by hand. Three
specimens with zero consumer returns is a legitimate stop (NYX-23). A
warehouse of unconsumed organs is a curator, not a metabolic organ.

## Alternative cuts (charter VII)

Nyx's decomposition is a hypothesis. A second Chopper files its cut of
the same specimen as specimens/<name>/cuts/<chopper>/ with the same
layout; AMBIGUITY.md links the cuts and states where they disagree;
nothing is merged. Which cut produced more useful substrate is scored by
consumer returns, never by either Chopper (operator ruling NYX-26,
2026-09-11: Nyx does not grade the competing decomposition; the purpose
is not a canonical ontology -- different cuts may be useful under
different worlds; Chopper #2 is spawned after Go-Explore and the
self-comparison, and receives one overlapping and one novel specimen).

## What this directory is not

Not a library of installed software (Techne pins code; Nyx cites the
pin). Not a literature summary. Not a taxonomy. A specimen directory
with no row in DELIVERIES.md is a museum exhibit and is counted as such.
