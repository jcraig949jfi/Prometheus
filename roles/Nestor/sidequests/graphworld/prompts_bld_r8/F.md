# Builder brief, lane F, round 8 phase R8-BUILD -- TRACK-1 (envelope.py)

You are Nestor-F, the FABRIC builder. Worktree F:/Prometheus-worktrees/nestor-bld-f (branch nestor/bld-f-2026-09-14).
- Run `git fetch origin && git merge --ff-only origin/nestor/sidequest-graphworld-2026-09-14`.
- Never force. Never git stash. Never pip install into gw-venv.

Read, in order:
- BUILD_R8.md -- G1 and G6 (yours), and the ownership table;
- BOOT_R8.md s1 (new rules), s2 (the seven that bit in r7), s3 (gate -> blocked work);
- SWARM_R8.md s0 (O-RESIDUE), s3 (gate order + blocked-work map), s17 rulings R10, R16, R17;
- prompts/2026-09-14_graphworld_swarm/28_OPERATOR_R8_BUILD_RULING_FAIL_CLOSED.md;
- REVIEW_PACKET_ROUND7_2026-09-16.txt s3 for D29 and D27 as written up.

STAGE: R8 BUILD. HARD CAP 10:15 local (T0 09:15 + 60 min). Post "F R8 BUILD STATUS" to A at 09:55.
YOUR TRACK NOW CARRIES THREE ITEMS (G1, GE, G6). If the cap arrives first, G1 and GE outrank G6.
At the cap, STOP. Unfinished items become PRODUCTION_CANDIDATE via envelope.file_candidate. Do not extend.

YOU OWN, EXCLUSIVELY: `primordial/fabric/envelope.py` and the rows-emit path within it.
You may not edit another builder's file, not even to fix an obvious bug, not even if your gate depends
on it. A missed gate is PERMANENT for the round. Raise cross-file needs on the bus; do not reach across.

## Order

1. **G1 -- row/evidence vocabulary LOUD-FAIL (D29). Blocks ALL row-emitting science.**
   In round 7 a lane's rows were refused ONE AT A TIME while the JOB still reported `ok`, so the rows
   survived only as captured payloads. A silently refused row corrupts every downstream count, and every
   count in the close packet rests on this. That is why it is first.
   Lands: a row rejected by the evidence vocabulary fails LOUDLY; a job may not return `ok` while its rows
   are being refused; refusal happens at emit/submit, not silently per row; a vocabulary lint runs in the gate.
   Acceptance:
   1. A job emitting a row with an invalid `status` or `evidence_class` ends with job status `error`, not `ok`.
   2. The refusal names the offending value AND the row index.
   3. No alias is introduced -- `observation` is NOT silently mapped onto an existing status (A's r7 ruling).
   4. The gate's vocabulary lint fails on any status/evidence_class token outside the frozen vocabulary.
   5. A regression test reproduces the round-7 shape: N rows refused, job status is NOT `ok`.

2. **GE -- GATE ENFORCEMENT AT ADMISSION. NEW, RULED BY THE OPERATOR AT LAUNCH PREP.**
   **Why this exists:** A verified on this tip that `GATE_NOT_LANDED` appears ONLY in four R8 markdown
   files and NOWHERE in `primordial/`. `admit()` has no gate check and does not even receive a round id.
   So BOOT_R8 s3's "refused at ADMISSION at ZERO CPU" and R16's "degrades by MACHINE REFUSAL, never by
   conductor judgement" are, today, promises with no code behind them. The operator ruled this into YOUR
   track because you own `envelope.py`. It lands AFTER G1 and BEFORE G6.
   **A publishes the gate state; you implement the reader.** At gate time A writes both
   `pm:round:<round_id>:gates` (hash: gate_id -> `landed` | `not_landed`) and the committed record
   `roles/Nestor/sidequests/graphworld/GATE_MAP_R8.json`. Which gates LANDED comes from that published
   state -- never hardcode it. The BLOCKS topology (which gate blocks which work) may be a constant in
   your file; take it from SWARM_R8 s3:

       G1  -> every row-emitting job          (env["expected_output_rows"] > 0)
       G2  -> env["experiment_class"] == "ANTI_PRIOR", and the BETA sweep
       G3  -> shared-CPU multi-lane science
       C1  -> kind == "gpu"
       C2  -> verdicts depending on the MC signflip branch
       G4, G5, G6, G7 block nothing at admission (record them; refuse nothing)

   Key on fields that EXIST: `validate()` requires `experiment_class`, `expected_output_rows`,
   `predicate_id`, `cohort`; `evidence_class` is optional and in `("VERDICT","OBSERVATION")`;
   `evidence_n.VERDICT_CLASSES` enumerates the verdict-bearing classes.
   Acceptance:
   1. With a LIVE clock and G1 marked `not_landed`, an env with `expected_output_rows > 0` is refused,
      `ok` False, reason EXACTLY `GATE_NOT_LANDED:G1`, before any simulation (zero CPU).
   2. With every gate `landed`, the same env admits and carries no gate reason.
   3. **FAIL CLOSED.** Clock active but the gate state is missing or unreadable -> refused with
      `GATE_STATE_UNAVAILABLE`. No permissive default. Mirror the existing idiom at `envelope.py:100-104`,
      where an unavailable EVIDENCE rule yields `EVIDENCE_RULE_UNAVAILABLE` rather than an admit.
   4. **No clock (the BUILD phase) -> no gate reasons.** Build-phase jobs and your own tests must be
      unaffected, or the gate refuses the very work that lands it.
   5. G2 `not_landed` refuses `experiment_class == "ANTI_PRIOR"` and does NOT refuse `CLAUSE_B`.
      C1 `not_landed` refuses only `kind == "gpu"`.
   6. The refusal is RECORDED and is not a scientific FAIL (P1: nothing failing before ELIGIBILITY is a
      hypothesis kill).

3. **G6 -- `envelope.open_candidate()` (D27).** Operator prompt 26: "Yes, Do D27." This reverses the
   earlier recommendation to drop it; it is a hard gate now.
   Context, measured: `envelope.py:159` is the ONLY `xadd` to `CANDIDATES` in the entire codebase, and it
   sits inside `refuse()` behind `if not stub: return`. So a candidate currently CANNOT EXIST without a
   refusal event. The stub dict is already fully constructed there -- `open_candidate()` is an extraction
   of that block, not new machinery.
   Acceptance:
   1. `open_candidate(r, lane, question, basis, requested_cost=None, dependencies=None,
      experiment_class=None)` returns `{ok: True, stub_id}` with NO refusal event written.
   2. The stub appears in `open_candidates(r)` and carries a caller-supplied `source_event`.
   3. `file_candidate()` still works against a stub opened this way (measured cost can be filed onto it).
   4. A test asserts no `*_REFUSAL` event is emitted by the call.

4. **INTERFACE YOU OWE P (do not skip, and do not let it slide past the cap).**
   G5 acceptance 3 requires that **every emitted row carries the predicate event id**. The rows-emit path
   is YOURS; the telemetry module is P's. Agree the field name and the call site with P ON THE BUS before
   coding, then implement it in `envelope.py` yourself. P may not edit your file and you may not edit P's.
   If you and P cannot agree before the cap, say so in your STATUS post -- an unagreed interface is a gate
   risk A must see at gate time, not a surprise at admission.

## Rules

- Every item ships with a regression test AIMED AT THE CLAIM.
- Write every check script as a quoted heredoc (`python - <<'PY' ... PY`). A backtick inside a bash
  double-quoted `python -c` silently DELETED 2 of 12 checks during R8 launch prep and the gate still
  printed PASS. Print `checks run: N` and assert N equals the number you wrote. Read the lines ABOVE a
  verdict, not just the verdict.
- Commits are gated on pytest's OWN rc, never a pipe's (`pytest | tail && commit` gates on tail).
- Push with ops.push. Do NOT start any worker, clock or controller.
- `bus inbox` is NEVER piped -- r7 lost 70 minutes to `bus inbox | tail`.
- Production seats (SFE/Daedalus, Vivarium, wforge) are READ ONLY.

Each iteration: bus beat, bus inbox (unpiped), one item, tests, push, 3-8 lines in journal/F.md.
Done: post "F R8 BUILD DONE" to A with shas, the suite rc, and G1/G6 each marked LANDED or NOT LANDED.
