# COUPLING FAILURE LEDGER

Every implementation, scientific, exploit or detector failure of the coupling campaign, in the order found.
Pre-freeze entries (F1-F3) were found during Phase 0 on off-plan pilot seeds (7e12..7.5e12) and changed the design
BEFORE any scientific run. Post-launch entries are appended by the analysis and never edited away.

| id | when | class | what failed | evidence | disposition |
|---|---|---|---|---|---|
| F1 | Phase 0 pilot | implementation-design | charge-as-you-write copy budget (VM halts at the first unpaid window write): an organism cannot see R, so every copier spent each income on a partial copy and never accumulated a full copy's price; 12/12 pilot worlds extinct with 0-1 SR births, seeded replicators included | pilot output (journal 2026-09-24) | replaced BEFORE freeze by charge-at-construction (a viable offspring costs COST x bytes written; unpaid constructions refused, free). The VM change was reverted; v1/v2 untouched |
| F2 | Phase 0 test | test premise | "no reproduction by the evaluator" test assumed zero births in a SEEDED_WITNESS world; 14 births came from the world's random majority copying by its own code | test run | test corrected to the real invariant: births == paid births and no rich non-copier ever breeds |
| F3 | Phase 0 probe | tooling | a stdin-fed multiprocessing probe cannot spawn on Windows and looped (64 MB of tracebacks); 3 orphaned workers could not be terminated | tool output | probe rerun from a file; no campaign code involved |
