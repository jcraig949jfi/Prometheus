# Icarus -- the self-improving ladder climber, re-read as residue and instruments

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11. Created on the base-role adoption pass (operator
prompt: roles/Icarus/prompts/2026-09-11_adoption/OPERATOR_PROMPT.md, hash
in MANIFEST.md beside it). Icarus never had a roles/ directory before
today; its only seat document was agents/icarus/README.md (2026-05-25),
which is now annotated as HISTORICAL at its top and otherwise untouched.
The May-June queue is classified, not resumed: roles/Icarus/
ARCHAEOLOGY_2026-09-11.md. This is the seat's entry file.

Resolve and obey the current base-role inheritance chain BEFORE this
seat's local bootstrap. This file does not restate inherited boot
mechanics, git mechanics, journaling, comms or paste-block rules.

## Seat state: BLOCKED (2026-09-11)

Blocked on ICARUS-XL-1, an operator decision (ARCHAEOLOGY section D):
retire with residue navigable / probe before resurrection / re-premise
as a lineage. No autonomous work until it is made. The seat's stand is
recorded there. "Always be working" applies to ACTIVE seats only.

## What Icarus was (historical; the record is in ARCHAEOLOGY section A)

A loop that rewrote a hand-written reasoner with an LLM to climb the
R0-R12 reasoning ladder, with TDD, an adversarial battery, a co-evolving
Falsifier on a different model, and a lens panel that turned every
failure into a typed object. 22 cycles on M2, 2026-05-25 to 2026-06-15;
R5 cleared at cycle 18; stopped at cycle 20 with R6 as target. The
mission is in tension with the north star (a predetermined ladder is
not the target; the reasoner is not ours to design). The machinery --
typed failure residue, kill clusters with nearby survivors, an
independent-model falsifier, a rung-calibration matrix that reports its
own vacuous rungs, a debt ledger -- is the kind of thing the north star
says a seat supplies.

## What Icarus holds now (the only things that are current)

- The residue: agents/icarus/state/training_stream.jsonl (8 typed
  objects), state/kill_clusters.json + wisdom/kill_clusters.md (3
  clusters, 6 failures), state/debt_ledger.json, state/
  tier_calibration.json (2026-05-28 matrix: R0/R1 too_weak_all_pass, R2
  vacuous, holdout_R1 unreached_all_fail), and cycles/cycle_001..020 --
  which exist ONLY on M2 (D:), gitignored, unreachable from this seat.
  Making that residue navigable (ICARUS-01, ICARUS-02) is the one class
  of work that is STILL_LIVE regardless of the decision.
- The code under agents/icarus/ (42 python files). Not running anywhere:
  verified 2026-09-11 on M1 (no scheduled task, no process, no pid
  file); M2 not inspected from here. Its entry point daemon.py has no
  D-23 guard and hardcodes D:\ paths in its README; both are backlog
  items, executed only if the seat is unparked.
- Two doctrine lines the program kept: reasoning_ladder.md rule 3 (a
  plateau is an interface bug until an interface audit clears it) and
  "a session that produced no typed object produced nothing"
  (Harmonia 08-12). Icarus does not own either; it is their provenance.

## Boundaries with sibling seats (so a re-premise does not collide)

- Kairos maps the failure surface of CLAIMS. Icarus's residue is about
  failures of a self-modifying LOOP; if (b) or (c) is chosen, the
  question "does failure emit a direction the next attempt can use" is
  asked of organisms, and Kairos is told.
- Ergon is the memory-metabolism seat; anything Icarus registers as
  residue goes through the Evidence Wiki API, never a private store.
- Vivarium executes; Archaeon coordinates H0-H5; Harmonia qualifies
  instruments. Option (c) would make Icarus a lineage under Vivarium,
  a decision none of those seats can take.
- Daedalus's charter borrows the name ("Icarus -- hand people wings
  that hold"). It is a motto there, not this seat.

## Files

  STATUS.md                          machine-readable state, dormancy visible
  BACKLOG_H0H5.md                    24 rows in the 2026-09-10 schema; XL rows are the operator's queue
  ARCHAEOLOGY_2026-09-11.md          the classified May-June queue and the decision
  calibration/CALIBRATION.md         the seat's own wrong calls, from the record
  journal/2026-09-11.md              this pass
  BASE_ROLE_ADOPTION_2026-09-11.txt  the adoption receipt
  prompts/2026-09-11_adoption/       the operator prompt verbatim + MANIFEST
