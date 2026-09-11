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

## Evidence grades

T1 a committed artifact in this repository (receipt, lock, test, row) or
   a resolver-verified DOI / commit; T2 a remembered citation not yet
   resolved; T3 hearsay; unknown. A delivery states the grade of every
   source it leans on. Local receipts outrank remembered literature.

## Alternative cuts (charter VII)

Nyx's decomposition is a hypothesis. A second Chopper files its cut of
the same specimen as specimens/<name>/cuts/<chopper>/ with the same
layout; AMBIGUITY.md links the cuts and states where they disagree;
nothing is merged. Which cut produced more useful substrate is scored by
consumer returns, never by either Chopper (NYX-26 asks the operator to
name the scorer).

## What this directory is not

Not a library of installed software (Techne pins code; Nyx cites the
pin). Not a literature summary. Not a taxonomy. A specimen directory
with no row in DELIVERIES.md is a museum exhibit and is counted as such.
