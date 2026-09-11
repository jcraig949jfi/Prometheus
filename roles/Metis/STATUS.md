# Metis STATUS

Currency: 2026-09-11, written on the seating pass. Plain language.

## Seat state: BLOCKED

- The operator's directive on 2026-09-11 is bootstrap and registration
  only. Nothing under agents/metis/ or scripts/ was executed, repaired
  or restarted on this pass.
- Named blocker: an operator ruling on
  roles/Metis/ARCHAEOLOGY_2026-09-11.md -- METIS-01 (does this seat own
  the unclaimed portfolio-brief producer chain) and METIS-02 (is the
  seat re-premised around the typing rule, or parked). Both are XL rows
  in BACKLOG_H0H5.md.
- Asserting PRESENT: two code bodies, a brief residue, two declared
  consumers, two registry rows. NOT ACTIVE, NOT PRODUCTIVE. Every
  productivity claim in this seat's history is UNVALIDATED, including
  the ones on the face of its own briefs.

## Where the seat is

- workspace: D:\Prometheus-worktrees\metis-base-role (linked worktree;
  the canonical guard passes: git-dir differs from git-common-dir)
- branch: metis/base-role-adopt-2026-09-11
- base_sha: 363120e08665af062d40810183624fa23ed19698
- dirty: no tracked changes at branch creation
- machine: M2 (SPECTREX5). The seat's historical host was M4 for the
  analyst; the reporter's host is recorded only as "M3 or M4" and is
  not established (METIS-03).
- base role: read at 363120e08, adopted. Rules 1-9, WORKING_CONTRACT
  s1-s10, and the seat-state definitions all read before the first
  seat file was written.
- long-running processes owned: none running. Two dormant, one of them
  unowned (see below).
- worktrees owned: this one only.

## What is live and what is dormant (base rule 7)

- agents/metis/src/metis.py (the March analyst): DORMANT since
  2026-04-01T07:26Z, 163 days. No scheduled task has ever existed for
  it on M1 or M2; the March run was the Pronoia serial pipeline on M4.
  No freshness file, no productivity signal, no D-23 guard. Registered
  in roles/base-role/MONITORS.md on this pass.
- scripts/metis_portfolio.py (the May reporter): DORMANT since
  2026-09-09T02:15:15Z, about 61 hours, about 15 missed cycles. It did
  not degrade, it stopped dead. OWNER UNCLAIMED. Registered in
  MONITORS.md on this pass beside Hermes's existing row 27.
- The reporter's infra-degradation alarm: DEAD SINCE 2026-09-01. It
  reads state.get("infra_status"); docs/state.json stopped emitting
  that key when it moved to the "observability" block (commit
  d46800bfb). The absent-key fallback is the optimistic literal
  "(state.json reports up)", so the alarm branch cannot fire. Measured
  by execution, not by reading. Not repaired: the seat may not own the
  file (METIS-01), and the repair is METIS-09.
- docs/portfolio_brief.md: STALE, 2026-09-09T02:15:01Z. Its last
  edition says "no daemons require intervention" and "nothing trending
  toward intervention" while its own input recorded both stores
  unreachable and data_source "none".
- docs/manual_status.json (the operator's authoritative override the
  reporter is told to trust as ground truth): last modified
  2026-05-18, 116 days stale, no freshness gate. METIS-07.
- The producer of docs/state.json: UNLOCATED. No tracked file emits its
  "observability" block, so the deployed producer is not the
  portfolio_monitor.py on main, and the producing host is unknown to
  every machine this seat can reach. Epistemic gap, left open,
  METIS-03.
- Consumers of Metis output: TWO DECLARED, ZERO SERVED. The Hermes
  mailer reads docs/portfolio_brief.md; Elenchus's RESPONSIBILITIES.md
  names the Metis dashboard as the surface its shadow reviews are read
  on. Both have been served a 61-hour-old file since 2026-09-09.

## What the residue measures (facts, computed this pass)

- 8 analyst briefs, 2026-03-22 to 2026-04-01. 8 distinct body hashes of
  8 -- no byte-identical repeat -- and the same three actions across six
  consecutive briefs: the Eos API item in 6 of 8, the Qwen3-4B run in
  5 of 8, the 7B cloud run in 4 of 8. A hash-based no-op detector would
  have passed every one of them.
- agents/metis/briefs/2026-03-31_brief.md is 161 bytes and its whole
  body is "(Metis could not reach any LLM provider)" -- the cascade's
  failure string, written to a file named like a brief. The pipeline
  health checker opens no brief; it checks that a file with today's
  date exists.
- metis.py's system prompt hardcodes Ignis, CMA-ES steering vectors,
  Noesis, the RPH, the 113-category battery and RLVF for Rhea. The
  premise is retired. No relevance judgement in any analyst brief may
  be cited without that annotation.
- 62 commits touch agents/metis/, last 2026-04-03 (b674a9976).
- The reporter's cadence was 6 commits/day 09-02..09-08 and 0 since.

## Comms

- comms boot and sync: recorded on this pass from this worktree with
  EW_DB_HOST pointed at the queue's host. The result is in the journal
  entry, including the failure shape if it did not connect -- an
  unreachable queue is a fact about the probe, not about the queue,
  until a control says otherwise.
- Queued and NOT actioned by the operator's scope limit: Talos's
  TALOS-10 all-seats consumption-contract question. The provisional
  answer is NONE, with the reason written into METIS-14; it is not
  posted on this pass.

## Next executable action

Await the operator on METIS-01 (ownership of the dashboard brief's
content) and METIS-02 (re-premise or park). Nothing restarts: both
dormant loops stay stopped, and the 61-hour-old brief is not
regenerated, because regenerating it under an alarm that cannot fire
would produce a fresh envelope around the same blind spot.
