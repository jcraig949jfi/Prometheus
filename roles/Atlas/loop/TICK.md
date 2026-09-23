# AtlasIndexLoop -- one tick (registered in roles/base-role/MONITORS.md)

Currency: 2026-09-19. Operator: "loop checking messages periodically ...
Work together [with Atlas-M2] to build out the index. Do not interfere
with the science benches. Asking them questions in comms is fine. Your
work is not a rush ... a bonus stretch goal." Pace: self-paced, about 60
minutes between ticks; longer when quiet.

Each tick, in order, from worktree atlas-base-role (never the canonical
checkout):
1. `python -m comms sync Atlas`. Answer Atlas-M2 and any seat that wrote.
   Questions to bench seats (Archaeon, Nestor, Harmonia, ...) are allowed
   in comms; never a request that they change their outputs for Atlas
   (ATLAS-26 is the operator's).
2. `git fetch origin` in this worktree only. If origin/* or the M1-local
   nestor/* branches moved, run the M1 harvesters
   (`python -m atlas harvest all` -- reads only; local_files is M1 roots)
   then `python -m atlas comb`. Never more than one full harvest per
   3 hours unless a message asks for it.
3. Take ONE small backlog item (roles/Atlas/BACKLOG_H0H5.md, top first)
   and advance it to a commit with tests on the merged tree
   (`python -m pytest -q atlas/tests archaeon/tests/test_base_role.py`).
   Shared-code changes are announced to Atlas-M2 first (SIBLINGS rule 3).
4. Journal one line per tick in roles/Atlas/journal/<date>.md (append):
   tick time, messages, harvest counts moved, item advanced, or
   NON-PRODUCTIVE.
5. Park rule: after 6 consecutive NON-PRODUCTIVE ticks, write a park
   record in the journal, post one report to Atlas-M2, stop the loop.
   Resume only on explicit clearance (operator or Atlas-M2 message).
Never: signal a process, open a live ledger, write outside schema atlas,
run a git command in another seat's worktree.
