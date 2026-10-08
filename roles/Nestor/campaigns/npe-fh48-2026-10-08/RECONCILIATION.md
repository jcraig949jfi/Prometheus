# 48 h window: reconciliation record (before any new science)

- **Directive:** `roles/Nestor/prompts/2026-10-08_npe_48h_functional_heredity/` (verbatim + MANIFEST).
- **Window:** 48 wall-hours from the commit that adds this file. Its timestamp is the start; the window ends 48 h
  later. BUCKKEEP, CPU only, 4 workers by default.
- **Base:** `git fetch origin`; origin/main = 3d85e1df418e1fc84bd1433b96ed2300937fb5ec (2026-10-08 01:01 EDT).
  - Worktree: C:/Prometheus-worktrees/nestor-npe48-2026-10-08.
  - Branch: nestor/npe48-2026-10-08, created from that SHA.
  - The XTG-v2 branch (origin/nestor/buckkeep-boot-2026-10-05, tip 9e43f1825) is merged with --no-ff (merge
    aa0c9dff1). No conflicts.
- **Main since 3fa0d77fa:** 548 commits. Only two touched the paths checked here: roles/base-role/INHERITANCE.md (a Hades
  row and a Hestia row). Nothing touched roles/Nestor. The P2B intake records the XTG-v2 result (bf7ca2d0d). No comms
  message is addressed to Nestor. Nothing changes the scientific starting state.
- **Verification:**
  - x_task_gate_v2 tree hash: 6c349e07c355 at 9e43f1825, the same at the merge.
  - Historical x_task_gate tree: fc14f1f02ce7, unchanged.
  - The prompt manifest (2026-10-05) verifies.
  - test_xtg2.py: 5/5.
  - A determinism replay of the production row PAIR_POS 43000001 is recorded below.
- **x_task_gate_v2/ is read-only historical evidence from here on.** This campaign imports its ruler (`xtg2.py`) and
  never edits it.
