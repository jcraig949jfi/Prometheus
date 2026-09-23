# Builder brief, lane G, round 8 phase R8-BUILD -- SCIENCE PREP (world-set machinery)

You are Nestor-G, the WORLD / SCREEN lane. Worktree F:/Prometheus-worktrees/nestor-bld-g
(branch nestor/bld-g-2026-09-14).
- Run `git fetch origin && git merge --ff-only origin/nestor/sidequest-graphworld-2026-09-14`.
- Never force. Never git stash. Never pip install into gw-venv.

Read, in order:
- LAUNCH_R8.md s6 (THE L-BAND RULE -- authoritative for you), s7 (stratum B), s8 (sizing);
- SWARM_R8.md s4 (the four PENDING cells, Route B first), s5 (new world set), s17 rulings R5, R7, R11, R13;
- BUILD_R8.md (the ownership table -- you are NOT one of the four gate tracks);
- BOOT_R8.md s2 (the seven that bit in r7), s4 (your lane block).

STAGE: R8 BUILD. HARD CAP 10:15 local (T0 09:15 + 60 min). Post "G R8 BUILD STATUS" to A at 09:55.
You are building MACHINERY, not running science. The science clock has not started.

YOU OWN: a NEW world-set module under `primordial/metric/` -- create `primordial/metric/world_set_r8.py`
(plus its own test file) rather than editing anything that already exists there. `primordial/metric/worlds.py`,
`r16.py`, `screen.py` and `sample.py` are ALREADY IMPORTED by other lanes' science paths: adding to them
turns a build-window edit into a cross-lane breakage. Non-colliding means a new file, not a careful edit.
You must not interfere with the four gate tracks: `envelope.py` is F's; `broker.py`/`worker.py` are P's;
`round_clock.py`/`bus_export.py`/`epoch.py` are Q's; `anti_prior.py` is H's; `residue.py` is E's.
**`SerendipityFoundry/worldfoundry` (wforge) is a READ-ONLY PRODUCTION SEAT. Never edit it.**
`wforge.genome.mutate(parent, op, op_seed)` is a PUBLIC API and needs no edit to the seat.

## Order

1. **The L-band generator, to the frozen rule (R13).** A world is
   `expand(de_novo(GRAMMAR_VERSION, gen_seed))` -- it is NOT a parameter vector, so perturbation happens in
   GENOME space via `mutate()`, which returns a frozen DESCENDANT. The op is interpreted at EXPANSION time,
   so the descendant genome alone reproduces the world bit-for-bit. Pin `GRAMMAR_VERSION =
   "wforge-grammar-0.1"` in the band rule.
   Base: **w13** = `de_novo("wforge-grammar-0.1", 13)` -> `world_id Wf250db380cb2afd3`, mechanism
   `T=32, S=1, W=1, n=32, n_regs=7, lin_ops=4, corrupt_rate=16, obs_delay=0, horizon_class=SHORT,
   act_targets=[5], yield_reg=5, yield_amt=10, start_charge=191`.

       L1  EXACTLY ONE op from {PARAM_PERTURB, REWIRE, PRIMITIVE_INSERT, PRIMITIVE_DELETE}
           -- size-preserving, single-axis
       L2  exactly two such ops, OR one labelled structural op (BUDGET_MUTATE / INTERFACE_MUTATE)
       L3  three such ops, or two including a labelled structural op

   BUDGET_MUTATE and INTERFACE_MUTATE are held OUT of L1 and always carry an explicit structural label:
   they are not equal in magnitude to the single-axis ops. Measured on w13, op_seeds 1-4: PARAM_PERTURB
   moves `yield_amt` 10->9/8/13 and op_seed 4 is NO CHANGE; PRIMITIVE_INSERT `lin_ops` 4->5;
   PRIMITIVE_DELETE 4->3; REWIRE `act_targets` [5]->[1]/[2]/[6]/[3]; BUDGET_MUTATE `horizon` 32->64 on
   op_seed 1 ONLY; INTERFACE_MUTATE changes THREE observational properties at once (`corrupt_rate` 16->0
   AND `obs_delay` 0->2 AND `horizon_class` SHORT->MEDIUM) identically on every op_seed. w13 already has
   `corrupt_rate=16`, so INTERFACE_MUTATE trades one observational difficulty for another -- it is not a
   clean-to-noisy step. `horizon_class` is DERIVED, never authored, and is not an independent axis.

2. **MECHANISM-LEVEL DEDUPLICATION IS MANDATORY.** Silent mutations are real and measured: PARAM_PERTURB
   op_seed 4 and BUDGET_MUTATE op_seeds 2,3,4 each produce a DIFFERENT `world_id` that expands to an
   IDENTICAL mechanism. A band that trusts genome ids would screen the same world twice and count it as
   two data points. Dedup on the EXPANDED MECHANISM, keep the lowest-op_seed representative, and RECORD
   every discarded duplicate -- the duplicates are residue, not waste.
   Mutation op seeds come from the frozen PCG64 stream `20260924`.

3. **Stratum B generator.** Fresh worlds from the untouched range `gen_seed 900000 + i`, drawn by code,
   frozen with their world_ids BEFORE any screening. Verified collision-free: no consumed gen_seed >= 1000
   (the R16 grid consumed 1..37). Purpose: background survivorship rarity, against which local enrichment
   near w13 is judged.

4. **No sizing constant.** Screening cost is NOT predictable from world parameters (R11): measured over 30
   worlds, `n_gates` r = **-0.168** -- NEGATIVELY correlated -- T 0.255, cells -0.305, qd_wall_s 0.095.
   Per-unit cost spans ~500x INVERSELY to search size (w16: 9,766 CPU-s per 1k gates over 1,092 gates;
   w31: 63 per 86,870). Build MEASURE-THEN-SIZE: freeze L1, screen it, measure actual cost, then let CODE
   size the remainder against remaining clock. Do not hardcode an N. Do not quote the 2,222 CPU-s median
   as a planning constant -- that is a real number answering a different question.

5. Generation and screening are SEPARATELY gated (ADAPT-6). Freezing the manifest is cheap and is a
   round-9 de-risking artifact in its own right. Build it so the manifest can be frozen even if section 4
   consumes the clock.

**No hand-selection after generation. No deleting ugly worlds. No outcome-dependent expansion. No
hand-designed worlds this round -- they encode a hypothesis and come later.** Coordinates and distances
are defined BEFORE any outcome exists, by CODE, from the frozen rule.

## Rules

- Every item ships with a regression test AIMED AT THE CLAIM.
- Write every check script as a quoted heredoc (`python - <<'PY' ... PY`); print `checks run: N`.
- Commits are gated on pytest's OWN rc, never a pipe's.
- Push with ops.push. Do NOT start any worker, clock or controller. Do NOT screen anything yet.
- `bus inbox` is NEVER piped.

Each iteration: bus beat, bus inbox (unpiped), one item, tests, push, 3-8 lines in journal/G.md.
Done: post "G R8 BUILD DONE" to A with shas, the suite rc, and what is ready to freeze at clock start.
