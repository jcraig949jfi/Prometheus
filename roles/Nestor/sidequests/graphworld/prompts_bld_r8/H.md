# Builder brief, lane H, round 8 phase R8-BUILD -- TRACK-4 (anti_prior.py)

You are Nestor-H, the MEASUREMENT / JUDGE builder. Worktree F:/Prometheus-worktrees/nestor-bld-h
(branch nestor/bld-h-2026-09-14).
- Run `git fetch origin && git merge --ff-only origin/nestor/sidequest-graphworld-2026-09-14`.
- Never force. Never git stash. Never pip install into gw-venv.

Read, in order:
- BUILD_R8.md -- G2 (yours), and the ownership table;
- BOOT_R8.md s1 (new rules), s2 (the seven that bit in r7), s3 (gate -> blocked work);
- SWARM_R8.md s8 (anti-prior), s3 (gate -> blocked work), s17 rulings R16, R17;
- LAUNCH_R8.md s5.2 (frozen seeds: candidates `20260921`, arm `20260922`);
- prompts/2026-09-14_graphworld_swarm/28_OPERATOR_R8_BUILD_RULING_FAIL_CLOSED.md.

STAGE: R8 BUILD. HARD CAP 10:15 local (T0 09:15 + 60 min). Post "H R8 BUILD STATUS" to A at 09:55.
At the cap, STOP. Unfinished items become PRODUCTION_CANDIDATE via envelope.file_candidate. Do not extend.

YOU OWN, EXCLUSIVELY: `primordial/score/anti_prior.py`.
You may not edit another builder's file, not even to fix an obvious bug, not even if your gate depends
on it. A missed gate is PERMANENT for the round. Raise cross-file needs on the bus; do not reach across.

## Order

1. **G2 -- anti-prior cell-binding pre-check (PC 1789523009420-0). Blocks ALL new anti-prior draws and
   the BETA sweep.**
   Why this matters more than it looks: ALL FOUR round-7 anti-prior assignments failed for CELL-CONSTRUCTION
   reasons. The predictor's confident-failure calls were therefore never put at risk, and after two rounds
   the calibration question is still untested. This gate is what puts the predictor at genuine risk.
   Lands: a candidate cell enters the pool only if CODE verifies, BEFORE publication, that
   (1) the intended pressure can bind on that world, (2) the discriminator has resolving power,
   (3) the oracle can fire, and (4) the control can differ from the experimental arm in principle.
   Rejected cells are replaced by the next seeded candidate. **No LLM chooses replacements.**
   Acceptance:
   1. A planted cell whose pressure cannot bind is REJECTED with a recorded reason.
   2. A planted cell whose oracle can never fire is REJECTED. Round 7 AP-01's meter needed a free-stream
      eligible episode that k=1 winners could never produce.
   3. A planted cell with zero resolving power is REJECTED. Round 7 AP-03: all 64 runs in BOTH arms
      returned exactly 31.71875, IQR 0.0 -- a PASS there is VACUOUS and must be reported as such.
   4. The published list is reproducible from seed `20260921` ALONE, including replacements.
   5. Rejection reasons are committed, so the rejected set is itself analysable residue.

   **PREREQUISITE A FOUND AT LAUNCH PREP -- `anti_prior.SEEDS` HAS NO r8 ROW.** Measured on this tip:
   `SEEDS = {"r6": (20260917, 20260918), "r7": (20260919, 20260920)}`, and `seeds()` raises
   `PriorLedgerError("SEED_NOT_FIXED")` for any round not listed. So `candidates(store, round_id="r8", ...)`
   REFUSES today, and your own acceptance 4 above -- "reproducible from seed `20260921` alone" -- cannot
   hold until the row exists. Add it, from the values already FROZEN in `LAUNCH_R8.md` s5.2:

       "r8": (20260921, 20260922)      # candidates, arm

   Credit where due: unlike `round_clock.ROUNDS`, this table already FAILS CLOSED -- it raises rather than
   silently reusing r7's seeds, which is exactly the behaviour R18 demands elsewhere. Do not weaken that
   guard while adding the row. It is your file; A did not touch it.
   **Do NOT publish r8 candidates.** A does that at clock start. You make the draw possible; A draws.

2. **Redaction discipline is part of the gate, not a manner.** Arm, rank, quantile and prior are
   conductor-only while the round is live. Round 7 had three disclosure lapses, one of them A's own. Build
   redaction BY CONSTRUCTION -- experimenter-readable records must not contain these fields at all, rather
   than relying on lanes to look away. Do NOT publish r8 candidates; A does that at launch.

3. If and only if G2 lands with time left before the cap, prepare (do not run) the historical tie-stability
   replay H3 as a separate, non-colliding module. Conditional work ALWAYS loses to the critical path.

## Rules

- Every item ships with a regression test AIMED AT THE CLAIM.
- Write every check script as a quoted heredoc (`python - <<'PY' ... PY`). A backtick inside a bash
  double-quoted `python -c` silently DELETED 2 of 12 checks during R8 launch prep and the gate still
  printed PASS. Print `checks run: N` and assert N equals the number you wrote. Read the lines ABOVE a
  verdict, not just the verdict.
- Commits are gated on pytest's OWN rc, never a pipe's (`pytest | tail && commit` gates on tail).
- Push with ops.push. Do NOT start any worker, clock or controller.
- `bus inbox` is NEVER piped. Production seats (SFE/Daedalus, Vivarium, wforge) are READ ONLY.

Each iteration: bus beat, bus inbox (unpiped), one item, tests, push, 3-8 lines in journal/H.md.
Done: post "H R8 BUILD DONE" to A with shas, the suite rc, and G2 marked LANDED or NOT LANDED.
