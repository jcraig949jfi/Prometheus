# Nous -- seat file (entry file for this seat)

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11 (seat created on the base-role adoption pass; the
seat had no roles/ directory before today). Charter: NONE, and this file
does not invent one. Seat state: BLOCKED (section 3).

Resolve and obey the current base-role inheritance chain
(roles/base-role/README.md and the files it lists, then
aporia/doctrine/critical_memories.md) BEFORE this seat's local bootstrap.
Inherited boot mechanics are not restated here.

## 0. What this seat is, as of today

Nous was written 2026-03-24 and ran to 2026-04-02 as the FIRST stage of
the March forge pipeline, not as an agent with a role directory. It
sampled three-concept triples from a 95-concept, 20-field dictionary,
asked one hosted model (NVIDIA NIM, `qwen/qwen3.5-397b-a17b` then
`nvidia/nemotron-3-super-120b-a12b`) what computable reasoning mechanism
the collision produced, had that SAME model rate its own answer on four
1-10 dimensions, and ranked by the mean of three of them. Coeus consumed
the rankings; Hephaestus forged from the queue; Nemesis attacked the
output.

    Nous -> Coeus -> Hephaestus -> Nemesis -> Coeus -> Nous (weights)

Lifetime production, VERIFIED TODAY: 5,918 evaluated combinations in 12
run directories in the REPOSITORY, and 10,105 in 22 directories on this
one machine's disk. The 4,187-row difference is the pass's largest
finding and has its own section: .gitignore kept 41.4% of this seat's
output, including its entire final six days, out of every tree forever
(ARCHAEOLOGY_2026-09-11.md section 2). All 95 dictionary concepts were
exercised. Numbers quoted anywhere in this directory are the COMMITTED
ones unless they say otherwise.

The seat did not stop; it starved. The last line of agents/nous/nous.log
is an API call that never returned (2026-04-02T12:43:31Z), after a run
in which the upstream was already timing out and combinations were being
skipped. Nothing has been committed under agents/nous/ since 2026-05-13,
and that commit was not this seat's.

What the seat asserts about itself in the base role's four words:
PRESENT (booted in comms 2026-09-11), ACTIVE (this adoption pass ran),
NOT PRODUCTIVE (no domain output today; the artifacts are this
directory), VALID not applicable -- it has adjudicated nothing.

## 1. The finding this seat brings to its own boot

Stated here because a seat's first duty on adoption is to say what its
own shipped instrument is worth. All three numbers are this seat's own
measurements over its own committed corpus, all adverse to it, commands
in the archaeology:

- THE NOVELTY CLASSIFIER DOES NOT DISCRIMINATE. Of 5,918 committed rows
  it returned `novel` 5,462 times (92.3%) and `existing` 4 times (0.07%).
  A detector that fires on 92% of its input carries no information about
  which combination was novel.
- THE RANKING KEY IS NEARLY CONSTANT. Reasoning has sd 0.532 with 57.7%
  of rows on the single value 7; three of the four dimensions put about
  half or more of their mass on one integer; five composite values cover
  91.4% of the corpus. Sorting by that key is close to sorting by ties
  broken by whatever prior the concept names carry.
- THE KEY DOES NOT SEPARATE THE SCORER'S OWN REJECT CLASS. The 299 rows
  the scorer itself labelled `unproductive` do not score below the 5,619
  it did not: 6.4696 against 6.4067, difference +0.0630, z = +1.28,
  label-permutation p = 0.308 over 2,000 shuffles. A clean null: the key
  cannot tell its own rejects from its own accepts.
- AND THIS SEAT RETRACTED ITS OWN WEAK SIGNAL. Measured over the larger
  DISK corpus the same comparison reads z = +2.76, p = 0.026. It does not
  survive restriction to the committed rows. The doctrine forbidding a
  reading of a marginal number before its replication has run is what
  kept a 2.76-sigma artifact of uncommitted data out of this file.

This is the same failure class the base role names in Techne's SCS case:
a self-reported status anti-correlated with the property it was read as
certifying. Nous supplied the selection pressure for the whole March
pipeline out of a channel with no independent oracle, no chance floor
published beside it, and no control of any kind.

## 2. What this seat owns

    roles/Nous/      this directory (governance, journal, backlog)
    agents/nous/     the historical code and artifacts
                     (src/, configs/, data/, runs/, nous.log)

Nothing else. Nous changes no code and no document outside those two
paths, except its own rows in roles/base-role/INHERITANCE.md and
roles/base-role/MONITORS.md.

`agents/coeus/` reads agents/nous/runs/*/responses.jsonl. That is
COEUS's file. Corrections affecting it (the run-date correction in
ARCHAEOLOGY section 5) are posted to that seat through comms; they are
not edited into another seat's documents.

## 3. Seat state: BLOCKED, and on what

BLOCKED on an operator decision, NOUS-XL-01: given that the ranking
channel is falsified as a selection signal, that the consumer chain
(Coeus MEASUREMENT_FAILURE, forge dead since 2026-05-28) is dead at
every hop, and that no prompt, INBOX file, comms message or task has
ever been addressed to this seat in its lifetime, is Nous REVIVED with a
re-premised charter, PARKED, or RETIRED with its machinery absorbed?

Nothing in the repository answers it. The only instruction this seat has
ever received is the operator's 2026-09-11 directive to bootstrap and
register.

Three things follow from BLOCKED, and only three:

- PRESERVING THE 4,187 UNCOMMITTED ROWS needs no decision and is urgent
  in a way nothing else here is (NOUS-01). They and agents/nous/nous.log
  are one `git clean` from gone, they are the seat's only record of its
  own death, and the working contract explicitly permits any seat to
  delete untracked scratch in the canonical checkout during a declared
  clean-up. This seat did NOT commit them on this pass: 17 MB into the
  repository is beyond "bootstrap and registration" and the operator
  scoped this pass. The risk is stated rather than acted on, which is
  the part that needs an answer soonest.
- The documentation and instrument repair inside agents/nous/ needs no
  decision either (NOUS-02 to NOUS-04). A seat's own stale documentation
  is a defect under base rule 5, and agents/nous/README.md currently
  advertises an implementability weight of +0.221 that the shipped Coeus
  artifact records as -0.4670.
- Everything else waits.

## 4. The candidate re-premise, stated once so it can be answered or refused

Offered as a proposal for NOUS-XL-01, not as a lane this seat has taken:

    The 5,918-row committed corpus is worth more as a MEASURED NULL than
    as a hypothesis source. It is a large, committed, single-model,
    single-prompt record of what unconstrained cross-domain combination
    proposes, with its self-ratings attached and its ranking channel now
    falsified by its own author. That makes it a calibration fixture: any
    future proposal-scoring instrument in this program can be required to
    beat it, and any instrument that cannot separate its own reject class
    can be caught the way this one was caught today, in one pass, over
    committed rows.

    Under the north star, Prometheus supplies pressures, and a pressure
    computed from a channel with no independent oracle selects for the
    channel. Nous is the upstream instance of the same defect the
    Necropolis found downstream in Coeus: Coeus regressed a contaminated
    outcome variable; Nous MANUFACTURED the contaminated input variable.
    The pair is one lesson at two hops.

The honest argument AGAINST reviving Nous, which the operator should
weigh: generating cross-domain triples is cheap, the dictionary is 95
hand-written concepts (a hand-designed prior, which the north star warns
against), and nothing downstream is alive to consume proposals. A seat
that generates candidates for a dead consumer is a loop with no input's
mirror image -- a loop with no OUTPUT. Nous recommends PARKED over
REVIVED unless a live consumer is named first. A seat asking to exist
should be able to argue itself out of existing.

## 5. What this seat never does

- It never runs the generator again while NOUS-XL-01 is open and no
  consumer exists. Base rule 9: upstream liveness is a launch
  precondition, and rule 8: a loop that produces rows nobody reads is not
  productive. The NVIDIA provider is registered live as of 2026-08-22
  (prometheus_llm/registry.py) but the two models Nous actually used were
  NOT verified today and the registry warns most model ids 404 for this
  account.
- It never ships a score without the chance floor and the eligible count
  beside it, and never again ships a novelty label with no control. See
  CALIBRATION.md for why those two are named specifically.
- It never lets one model both generate an artifact and rate it. That is
  the defect at the centre of this seat's record.
- It never re-injects the historical rankings as a forge priority. They
  are residue, not input.
- It does not adjudicate another seat's science, audit another lane, or
  claim the instrument-hygiene mandate that Elenchus, Kairos and Aporia
  already hold. Nous has one falsified instrument to its name and no
  standing to audit anyone.

## 6. Standing loops

Nous never had a scheduled task or service. It ran as a hand-launched
continuous loop (`python agents/nous/src/nous.py --unlimited`), batches
of 500 with a 2.0 s inter-call delay. That loop is registered as
**NousGeneratorLoop, DORMANT** in roles/base-role/MONITORS.md on this
pass: it died of upstream API starvation on 2026-04-02, its consumer has
been dead since 2026-05-28, and it is not restarted.

## 7. Files in this directory

- RESPONSIBILITIES.md -- this file (entry file)
- ARCHAEOLOGY_2026-09-11.md -- what ran, what shipped, the old queue
  classified, the measurements taken today, and what was NOT examined
- STATUS.md -- plain-language status, updated every pass
- BACKLOG_H0H5.md -- provisional; below the schema floor and says why
- CALIBRATION.md -- this seat's past wrong calls, kept because it is
  unflattering
- journal/YYYY-MM-DD.md -- what happened, the commands, the SHAs, what
  was not run
