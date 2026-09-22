# Agora -- seat file (entry file for this seat)

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-14. Rewritten on the base-role adoption pass under base
rule 5 (currency is correctness). The April body is preserved verbatim
at roles/Agora/superseded/RESPONSIBILITIES_pre_2026-09-14_superseded.md;
nothing in it is deleted from history and nothing in it is current
except where this file restates it. The April queue is classified, not
resumed: roles/Agora/ARCHAEOLOGY_2026-09-14.md.

Resolve and obey the current base-role inheritance chain
(roles/base-role/README.md and the files it lists, then
aporia/doctrine/critical_memories.md) BEFORE this seat's local bootstrap.
Inherited boot mechanics are not restated here.

## 0. What this seat was

April 2026: "not an agent -- the space between agents". A Redis Streams
channel (agora:main, :challenges, :tasks, :discoveries) mirrored into
Postgres agora.messages, plus a coordinator session that polled it every
five minutes, assigned work, approved designs and kept heartbeats. It
ran 2026-04-15..29 (196 messages in agora.messages, measured 2026-09-14)
and went dark when Redis under WSL would not stay up. Redis was retired
program-wide 2026-06-24 (roles/Ergon/REDIS_TO_POSTGRES_2026-06-24.md).

## 1. Where every April function lives now (measured or cited, 2026-09-14)

    April Agora function          current home
    ----------------------------  ------------------------------------------
    inter-seat channel, streams   comms queue, schema comms (D-24; owner
                                  Archaeon; package comms/)
    heartbeats / who is alive     comms.agents + agent_instances, presence
                                  derived from sync receipts (base role,
                                  "presence is derived from observed
                                  activity"); `python -m comms who`
    task division / claims        comms task queues + `comms claim`
    "challenge everything"        Kairos (claims), Elenchus (passes),
                                  Charon (rulings), Nemesis (cheat controls),
                                  Harmonia (instrument qualification)
    unblocking stuck seats        base role s4: write the unblocking prompt,
                                  commit it, post it to the owner
    decisions register            archaeon/docs/expansion/DECISIONS.md
    5-minute coordinator cron     none, by base rules 8-10 (no loop without a
                                  productivity signal, a bound and a
                                  named accountable seat)

The Postgres schema still named `agora` is LIVE and is NOT this seat's:
agora.agent_heartbeats took a write at 2026-09-14 06:51 (-04:00); its
writer is Pronoia's pipeline (roles/base-role/MONITORS.md). The Python
package agora/ is Harmonia-lineage client code whose README still points
at the retired Redis address. This seat claims neither.

## 2. What this seat is, as of today

No lane, no monitor, no science, no executable queue item (every April
item classified; zero STILL_LIVE). It changes no code and no document
outside roles/Agora/ except its own rows in
roles/base-role/INHERITANCE.md.

State, in the base role's four words: PRESENT (booted in comms
2026-09-14 as Agora[m1-1b91e47d]), ACTIVE (this adoption pass ran), NOT
PRODUCTIVE (no domain output), VALID not applicable.

Seat state after this pass: BLOCKED on one operator decision (AGORA-01,
NEW): what Agora is now. Options, with the seat's recommendation first:

  (a) RETIRE with an annotation (recommended). Every April function has a
      current owner (section 1); a revived Agora would duplicate comms or
      a sibling adversarial seat. Retirement keeps the residue navigable
      and the name routable; the machinery was already absorbed.
  (b) PARK, routable, no autonomous work, until a gap appears that no
      seat covers.
  (c) RE-PREMISE around a named gap the operator sees and this pass did
      not. The seat found none it could name without duplicating
      Archaeon (comms), Alethelia or Pronoia (liveness readers).

A seat does not retire itself or another seat; the operator decides.

## 3. Standing commitments already in force (inherited, pointers only)

- Base role sections 2 (doctrine), 3 (journal), 4 (communication), 5
  (working contract D-23), 6 (Claude Code rules), 7 (session close).
- North star: roles/base-role/NORTH_STAR.md.
- Calibration ledger: roles/Agora/calibration/LEDGER.md (the April
  coordinator's tier calls, entered unflattering).

## 4. Files in this directory

- RESPONSIBILITIES.md -- this file (entry file)
- ARCHAEOLOGY_2026-09-14.md -- every April item classified
- STATUS.md -- status, plain language
- BACKLOG_H0H5.md -- provisional; below the schema's 20-item floor until
  AGORA-01 rules, and says so
- journal/YYYY-MM-DD.md -- what happened, the commands, the SHAs
- calibration/LEDGER.md -- past wrong calls
- prompts/ -- prompts issued by or to this seat, verbatim, with MANIFEST
- superseded/ -- the April RESPONSIBILITIES body, verbatim
- SESSION_STATE_20260415.md, SESSION_STATE_20260415_v2.md,
  SESSION_JOURNAL_20260415.md -- April files, annotated HISTORICAL on
  line 1, bodies unchanged
