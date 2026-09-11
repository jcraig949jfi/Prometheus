# Nemesis -- backlog

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11 (created on the adoption pass). Schema:
roles/Archaeon/prompts/2026-09-10_backlog/00_BACKLOG_SCHEMA.md.
Format: id | item | lane | milestone | size | blocked_on | evidence of done.

Priority order. Updated 2026-09-11 after NEMESIS-01.

DONE 2026-09-11 (NEMESIS-01): NEM-01, NEM-02, NEM-03 -- delivered as ONE
instrument, roles/Nemesis/science/cheatlib.py with 12 self-controls
including the pinned firing fixture (constant responder at 0.674 on the
April ledger). NEM-05 (attack cheatlib with cheatlib) delivered as the
builder-integrity control, added after the adversary broke twice inside
its own first attack; both failures are in FINDING.md and CALIBRATION.md.
NEM-12 (attack a live instrument on commission) delivered against the Eos
intake gate.

RULED 2026-09-11 by the operator, in effect: NEM-XL-1 is settled in the
direction of a program-wide seat that attacks live instruments on
direction ("give her a real instrument and make her attack it"), and
NEM-XL-2 is settled for this instance in the direction of NOTIFICATION
(the operator directed the attack; Eos received the finding). The GENERAL
rule for uncommissioned attacks is still open and stays on this list.

## Build the instrument before offering it (NEM-01..NEM-05)

NEM-01 | Commit cheatlib v0: a library of three cheat responders (payload reader, degenerate constant, majority-class) that plug into an arbitrary scoring path via one declared interface | TOOLS | alpha | M | none | roles/Nemesis/science/cheatlib.py committed with its interface documented and 3 unit tests
NEM-02 | Commit the negative, positive and cheat fixtures for cheatlib itself, including the April 92-record ledger as the fixture on which the constant responder is KNOWN to fire at 0.674 | TOOLS | alpha | S | NEM-01 | roles/Nemesis/science/fixtures/ + tests that assert the constant responder scores 0.674 on the April ledger and below chance on a scrambled copy
NEM-03 | Commit chance_floor.py: given an item population, compute and print the attainable range, the eligible count, the uniform-responder floor and the majority-class floor, before any attack | TOOLS | alpha | M | none | roles/Nemesis/science/chance_floor.py + a test that reproduces 0.674 and 62/92 on the April ledger from the committed blob
NEM-04 | Re-validate the 12 inherited metamorphic relations: for each, a fixture proving a SAME-expected transform preserves ground truth and a FLIP-expected transform inverts it; mark each relation VALIDATED or WITHDRAWN | TOOLS | alpha | L | none | roles/Nemesis/science/METAMORPHIC_VALIDATION_v0.md with one row per relation and the fixture path, plus the withdrawn list
NEM-05 | Attack cheatlib with cheatlib (constraint 1): show the seat's own instrument can be beaten by its own degenerate responder, or show it cannot and say on what population | TOOLS | alpha | S | NEM-01, NEM-02 | roles/Nemesis/journal entry with the rows, committed, flattering or not

## Annotate and contain the April corpse (NEM-06..NEM-09)

NEM-06 | Annotate agents/nemesis/README.md at its head with the retraction of the Goodhart table and a pointer to the archaeology; never rewrite the body | EVIDENCE | alpha | S | none | the annotation block committed at the head of agents/nemesis/README.md
NEM-07 | Add the D-23 canonical-checkout guard (archaeon.workspace.assert_not_canonical) to agents/nemesis/src/nemesis.py so the April entry point cannot run from the canonical checkout if anyone ever starts it | ENGINE | alpha | S | none | the guard in the entry point + a test that it refuses
NEM-08 | Write a committed freshness record for the April run (last_input_at, last_success_at, per-cycle productivity) so the MONITORS row can be read without running anything | EVIDENCE | alpha | S | none | roles/Nemesis/ledgers/april_run_freshness.json with the 3,013-cycle productivity histogram
NEM-09 | Commit the April 92-record ledger's derived statistics as a re-runnable script, so every number in ARCHAEOLOGY sections 2-4 can be reproduced by a third party from the committed blob | EVIDENCE | alpha | S | none | roles/Nemesis/science/reproduce_archaeology.py + its output committed beside it

## Earn a consumer (NEM-10..NEM-14)

NEM-10 | Post a delegation to Harmonia offering cheatlib as the cheat-control supplier for instrument qualification, with the April ledger as the worked example | EVIDENCE | alpha | S | NEM-01, NEM-02 | the prompt committed under roles/Nemesis/prompts/ with its MANIFEST, and the comms message id
NEM-11 | Post a delegation to Kairos defining the handoff: Nemesis breaks the instrument and supplies the input set; Kairos owns the claim that instrument's rows underwrite | EVIDENCE | alpha | S | none | the prompt committed with its MANIFEST and the comms message id, plus Kairos's ack
NEM-12 | Run cheatlib against ONE live instrument owned by another seat, on commission, and report the chance floor beside its headline number | EVIDENCE | beta | M | a seat naming an instrument and granting read access | the input set, the responses and the floor committed under roles/Nemesis/attacks/<date>_<instrument>/
NEM-13 | Offer the metamorphic relation set to Nyx as an extractable PRESSURE organ if NEM-04 validates any of it | TOOLS | beta | S | NEM-04 | the organ handed over with its ancestry, or a written statement that nothing validated
NEM-14 | Survey which currently-live instruments in the program publish a chance floor beside their headline number, and report the count | EVIDENCE | beta | M | none | roles/Nemesis/science/FLOOR_CENSUS_v0.md with one row per instrument and the eligible count

## Questions the seat wants to make testable (NEM-15..NEM-18)

NEM-15 | Re-premise NEM-A12 ("static performance and adversarial robustness measure different things") into a form testable against instruments that beat their own chance floor | EVIDENCE | beta | M | NEM-14 | a preregistration committed in its own commit before any data is touched
NEM-16 | Build the grid axes question properly: measure whether ANY two-axis coordinate system over adversarial inputs separates instruments better than a random partition of the same inputs | EVIDENCE | beta | L | NEM-03, NEM-04 | the measurement with its null and its eligible count committed
NEM-17 | Characterise the 15.1 per cent of April evaluations where confidence_correct equals confidence_wrong: is it a scorer defect, a tie-break, or a serialisation artifact | EVIDENCE | beta | M | none | the diagnosis committed with the rows, including "cannot determine" if that is the answer
NEM-18 | Determine whether a constant-responder population can be detected automatically from a results ledger alone, so a future instrument cannot ship with 88 of 294 degenerate responders unnoticed | TOOLS | beta | M | NEM-03 | the detector + its cheat fixture, and its result on the April ledger

## Decisions this seat needs from the operator (XL)

NEM-XL-1 | Rule on whether Nemesis's mandate is PROGRAM-WIDE ON COMMISSION (like Elenchus and Kairos) or confined to a named lane; the seat has written itself as commission-based and needs that confirmed | program | XL | operator decision NEW: "Is Nemesis a program-wide cheat-control supplier available on commission to any seat that owns an instrument?" | the ruling recorded in archaeon/docs/expansion/DECISIONS.md
NEM-XL-2 | Rule on whether attacking another seat's live instrument requires that seat's consent or only notification; base rule 6 forbids MUTATING the audited object but is silent on running a cheat responder through its scoring path | program | XL | operator decision NEW: "Consent or notification for a Nemesis attack on a live instrument?" | the ruling recorded in DECISIONS.md
NEM-XL-3 | Rule on the disposition of agents/nemesis/reports/ (3,014 untracked files, one per cycle, 97.3 per cent of them reporting no placement): retain as a rule-8 specimen, sample and discard the rest, or leave untracked | program | XL | operator decision NEW: "Disposition of the 3,014 April report files" | the ruling and the executed disposition recorded in the journal
NEM-XL-4 | Rule on whether the April forge tool population (734 files, frozen 2026-04-03) may be used as a FIXTURE population for cheat-control development, given that it is a dead lineage | program | XL | operator decision NEW: "May a dead lineage be used as a calibration fixture?" | the ruling recorded in DECISIONS.md
