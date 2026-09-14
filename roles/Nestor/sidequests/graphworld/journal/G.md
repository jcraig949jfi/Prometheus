# Nestor-G journal -- METRIC HARDENING builder (round 3)

Seat: Nestor[m1-c77819fe], PM_LANE=G, worktree F:/Prometheus-worktrees/nestor-bld-g, branch
nestor/bld-g-2026-09-14. Package (ROUND3_BACKLOG s2): M1, M2, M3, C1, C2, C4, D-open (easy-metric
discriminator). Threads: 4 (conductor contract 1789425755152-0 overrides the boot prompt's 5).

## 2026-09-14 epoch 1, iteration 1 -- C2 sampler_seed mandatory

- primordial/qd/archive.py: `sampler_seed` has no default in `_Base`/`LuaArchive`; omitting it is a
  TypeError, `None` a ValueError, any string other than `UNSEEDED` a ValueError. `UNSEEDED` is the
  explicit label for a frozen pre-C2 harness: it keeps the round 1 ZRANDMEMBER sampler and the
  archive reports `replayable=False`.
- Elites per run seed: `save_elites(arch, path, run_seed)` writes one canonical JSON document
  (schema qd-elites-v1: run, run_seed, sampler_seed, replayable, glen, cells ascending with fit,
  genome hex, meta hex); `load_elites`, `restore_elites` read it back.
- Callers: 19 frozen harnesses (qd/e1,e2,e4,e4b,e5..e10; cohorts b1, c r2_01..05/08, d3, d4) now
  pass `UNSEEDED` explicitly -- behaviour unchanged, the non-replayability is labelled in code.
  C-R2-09 already seeds. D4's DetArchive forwards its seed; E2's LineageArchive takes one.
- Tests: primordial/qd/tests/test_archive_c2.py -- no-seed raises (Lua, Racy, Lineage); UNSEEDED
  not replayable; array seed ok; replay: two runs at the same (run_seed, sampler_seed) give
  identical elites and a byte-identical elites file, a different sampler seed differs; saved
  elites restore into a fresh archive with an equal dump; glen mismatch raises.
- New harnesses from round 4 on must pass a real seed and save elites per run seed.
