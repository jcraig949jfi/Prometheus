# Prometheus Genesis Ecology — working organization

**Issued by:** James (operator), 2026-08-30. **Status:** RATIFIED, supersedes the proposal
assessed in `GENESIS_ECOLOGY_ASSESSMENT_2026-08-30.md`. **Recorded by:** Aporia.

This file is the record of the chart as issued, plus Aporia's ratification notes. The chart is
the operator's; the notes below it are mine and carry no authority over it.

---

## The chart, as issued

    JAMES + LLM CHIMERA
        Direction / north star / major resource decisions
        |
        +-- APORIA      portfolio scientist / synthesis; finds prior work, compares
        |               benches, recommends next bets. Does not need permission to
        |               think across boundaries.
        +-- TECHNE      tools / donor stacks / capability acquisition. RAID -> WRAP -> TEST
        +-- LUDUS       worlds / environments / discrimination. Existing charter intact.
        +-- ERGON+LEXIS machine memory / abstraction / transfer. Lexis G0-G4 evidence
        |               and gates INHERITED, not restarted. Ergon pushes toward the
        |               long-term Learner.
        +-- HARMONIA A-E parallel science benches. Hypotheses, representations, lenses,
        |               compression, experiments, replication. May cross domains.
        |               Do not over-specialize yet.
        +-- CHARON      adversary. Attack important results when there is something
                        to attack.
                             |
                             v
                    SERENDIPITY FOUNDRY (physical M1)
                    measurement / execution / provenance / replay
                             |
                             v
                    SERENDIPITY EXPERIMENTER (physical M2)
                    frozen experiment / analysis / verdict
                             |
                             v
                    KNOWLEDGE / FOSSILS -> feeds next generation

    RULE ZERO:
        ROLES ARE SPECIALIZATIONS, NOT PROPERTY RIGHTS.
        Any seat may notice anything. Any seat may challenge anything.
        Existing work should be consumed before duplicated.
        Authority matters only where changing something could contaminate an
        experiment or its evidence.

## Ratification notes

### The three corrections landed

- **Naming collision CLOSED.** Verified 2026-08-30: no file in the tree claims "Serendipity" as
  a seat name. Giving the two spine roles their own names lets `M1`/`M2` revert to meaning only
  the physical stations, which is their established sense (`stations/M1_STATUS.md`,
  `M2_STATUS.md`, `roles/Ludus/ROLE.md:8` — "Machine: M1 (Skullport)"). This REDUCES referents
  rather than adding a third. D-5's constitutional `M0`/`M1` experiment arms
  (`agent_d5_blind/MANIFEST.md:45`, "§49: M1 is built LAST") are untouched.
- **Ludus intact.** The authorised 12-month Worlds charter (granted 2026-08-26) stands and is
  not duplicated into Harmonia.
- **Lexis inherited, not restarted.** G0 and G1 keep their FIRED status from 2026-08-25; G2
  (compute-matched) and G3 (transfer, not compression) remain the binding conditions.

### Harmonia A-E left unspecialized — correct, and worth stating why

The earlier draft assigned A-E fixed specialisms (assay designer, world designer, compression,
lensing, replication). Leaving them general is the better call: five seats pre-partitioned into
five topics cannot produce independent formulations of the SAME question, which is the only
thing that makes five of them worth more than one. Replication diversity requires overlap.

### RULE ZERO is the load-bearing clause, and it needs one operational definition

"Authority matters only where changing something could contaminate an experiment or its
evidence" is the correct boundary. To be actionable rather than aspirational, **contaminate**
should mean a specific, checkable list. Proposed from this programme's own scars:

    1. editing a FROZEN instrument after any binding measurement exists
    2. editing a PREREGISTERED predicate, threshold, or branch table after reading data
    3. editing or deleting COMMITTED ROWS beneath a verdict
    4. editing another seat's verdict string, as opposed to commissioning a successor
    5. changing the meter, budget, or scoring channel mid-arm

Everything else — noticing, challenging, proposing, reinterpreting, re-analysing with a new
instrument — is open to every seat under Rule Zero. Note that (1) and (2) are already enforced
in code in places (`result_schema.emit` refuses non-adjudicable artifacts; D-4/D-5 freeze
hashes), and (3) is only partly enforced: `atk015` asserts rows EXIST beneath a verdict but not
that they were not EDITED to match it.

### "Consume before duplicate" is accidentally the right anti-concealment mitigation

`report_SELECTION_DISCOVERED_CONCEALMENT.md` established that a separable evaluation episode is
an attack surface, and that the mitigation which HELD was moving selection off the episode and
making it continuous and in-population. Rule Zero's "existing work should be consumed before
duplicated" points the same way: it makes CONSUMPTION the selection signal rather than a
periodic round in which Aporia picks winners from a slate. That is the structurally safer form
and it should be kept that way deliberately, not by accident.

### Flag: M3 and Hephaestus are outside the chart

`stations/M3_STATUS.md` — M3 (Gandalf), point agent **Hephaestus**, the fleet's one non-Opus
seat (Fable 5), running the forge plus meta-assessment loop. **Last updated 2026-08-12, 18 days
stale.**

The chart names M1 and M2. Under Rule Zero this is not a territorial problem, but there is a
live seam worth naming: Techne acquires capability from OUTSIDE (donor stacks), Hephaestus mints
primitives from INSIDE (the forge), and Ergon owns what persists. Those are three different
layers touching the same object — the primitive pool. The donor inventory (2026-08-30) also
found the forge's cheapest actionable item still open: documentation plus usage exemplars on the
primitive pool, against a measured 0%-usage failure.

Not a request for a decision. Recorded so that a successor does not read the chart as a complete
roster of live seats — `roles/` holds 22.

### Standing constraint on my own seat, unchanged

Aporia recommends promotion; it does not rewrite evidence or modify another seat's frozen
experiment. If a frozen predicate says PASS, Aporia may commission a successor experiment
attacking the meaning of that PASS, and may not change the verdict. This held under test on
2026-08-27 and is now doubly binding under Rule Zero item (4).

The out-of-band append-only ledger belongs under **Serendipity Foundry** ("provenance / replay"),
and remains unbuilt. It is the precondition for enforcing contamination items (3) and (4) rather
than trusting them.
