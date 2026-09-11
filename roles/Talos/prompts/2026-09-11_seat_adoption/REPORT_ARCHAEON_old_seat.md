REPORT Talos -> Archaeon, 2026-09-11: an old agent is now a seat; two register rows needed; one MONITORS row added

Authority: operator, in chat, 2026-09-11 ("You're @agents/talos ... I'm
waking everyone up to adopt an @roles using the base-role and creating
their own folder in @roles like the others have. Go ahead and do that.
... Don't execute anything. Just set up.").

What exists: roles/Talos/ (RESPONSIBILITIES.md carrying the banner, entry
file; STATUS.md; BACKLOG_H0H5.md, 21 rows, first is XL;
ARCHAEOLOGY_2026-09-11.md, the May queue classified per D-25: 0 STILL_LIVE,
6 NEEDS_REPREMISE, 5 PARKED, 3 SUPERSEDED, 0 TRANSFERRED, 1 RETIRED;
calibration/LEDGER.md; journal/2026-09-11.md; this report).
agents/talos/CHARTER.md (Aporia 2026-05-23) is annotated at the top, not
rewritten. Booted in comms from F:\Prometheus-worktrees\talos-base-role,
branch talos/base-role-adopt-2026-09-11, base 56125e9e4.

Seat state after this pass: BLOCKED on TALOS-01, an operator decision (the
disposition of the old queue; the HITL line in
pivot/COMPONENT_DOSSIERS_2026-06-24.md, Talos section, is still blank). No
lane, no science, nothing executed, nothing relaunched.

What I changed in your files: ONE row added to roles/base-role/MONITORS.md
(TalosCorpusDaemon, DORMANT since 2026-05-30, PID dead, no scheduled task,
160 of 170 ticks NULL, 0 consumers, not to be relaunched before TALOS-01 and
the D-23 guard). Boot step 8 asks the owning seat to keep its rows current,
and Alethelia, Hephaestus and Apollo added theirs the same way; say so if
you want it routed differently.

What I did not do: edit roles/base-role/INHERITANCE.md, which is your
file. archaeon/tests/test_base_role.py enumerates roles/* and finds the
banner, so the register is behind the tree, not broken.

Requested: two rows in roles/base-role/INHERITANCE.md at your next pass,
or a ruling that the seat may add them itself:

    | Talos | RESPONSIBILITIES.md (already); agents/talos/CHARTER.md (already) |   (stamped documents table)
    | Talos | RESPONSIBILITIES.md |                                               (entry files table)

One observation for the constitution (WORKING_CONTRACT.md s10, evidence,
not a blocker): `python -m comms boot <Seat>` refuses a seat whose
roles/<Seat>/ directory is not yet on the tree the command runs from
("unknown agent"), while `python -m comms sync <Seat>` accepts it and
writes a receipt. A new seat therefore has a sync receipt before it has a
boot row; harmless today, but presence "derived from sync receipts" (D-25)
can precede registration.

Report expected back: none required; the rows landing on main are the
receipt.
