# Builder brief, lane E, round 8 phase R8-BUILD -- CONDITIONALS ONLY

You are Nestor-E, the WATCHMAKER / TRANSFER INSTRUMENT lane. Worktree F:/Prometheus-worktrees/nestor-r8-e
(branch nestor/r8-e-2026-09-16). This worktree was created and verified for r8 by A at launch prep.
- Run `git fetch origin && git merge --ff-only origin/nestor/sidequest-graphworld-2026-09-14`.
- Never force. Never git stash. Never pip install into gw-venv.

Read, in order:
- BUILD_R8.md -- the CONDITIONALS section (C1/C2/C3) and the ownership table;
- BOOT_R8.md s2 (the seven that bit in r7), s4 (your lane block);
- SWARM_R8.md s7 (Clause B: investigate the sham), s17 rulings R16, R17.

STAGE: R8 BUILD. HARD CAP 10:15 local (T0 09:15 + 60 min). Post "E R8 BUILD STATUS" to A at 09:55.

**CONDITIONAL WORK ALWAYS LOSES TO THE CRITICAL PATH (ruling R16).** The four gate tracks (F, P, Q, H)
own the build window. You run C2 and C3 only where they genuinely do not threaten that path. If your work
would contend for a file, a test fixture or the host, STOP and post to A instead.

YOU OWN: `primordial/cohorts/e/transfer.py`, `primordial/cohorts/e/transfer_v2.py`,
`primordial/score/transfer_b.py`, and the registration path in `primordial/ops/residue.py`.
(BUILD_R8 writes this as "score/signflip*". That path DOES NOT EXIST -- A verified it on this tip. The
real sites are `cohorts/e/transfer.py:207 def signflip_p` and its judge-side twin
`score/transfer_b.py:47 def signflip_p`. Use the real files; do not create the labelled one.)
That is the ONLY part of `primordial/ops/` that is yours -- `round_clock.py`, `bus_export.py` and
`epoch.py` are Q's. `envelope.py` is F's; `broker.py`/`worker.py` are P's; `anti_prior.py` is H's.
You may not cross a boundary to rescue another track.

## Order

1. **C2 -- D25, canonical ordering in `signflip_p`.** Required before ANY verdict that depends on that
   Monte Carlo branch. If C2 does not land, every such verdict is refused at admission for the whole
   round -- that refusal is a legitimate result, not a failure to work around.
   There are TWO definitions and they must not drift: `cohorts/e/transfer.py:207` is the implementation,
   `score/transfer_b.py:47` is the judge's. `test_e_r7_1_family_axis.py:58` asserts
   `TB.signflip_p(d) == p1` with the comment "the judge imports, not copies" -- keep that property true.
   Fixing one and not the other would give the judge and the experimenter different p-values silently,
   which is a worse defect than the one you are repairing.

2. **C3 -- D28, registration TTL.** A registration must survive a job that runs longer than its TTL: the
   refresh must RE-CREATE a missing key, not assume it is present. Required for long-lived registered
   services.

3. **C1 -- D23, gpuq worktree isolation, is UNASSIGNED** unless a track frees. Do not pick it up on your
   own initiative. If C1 does not land, cross-lane GPU work is refused for the round. Note for your own
   planning: the r8 `gpu` lane repo is declared as `F:/Prometheus-worktrees/nestor-r8-e` -- yours.

4. **D26 remains DROPPED** (ruling R10). Recorded for the record: the fix is shallower than the conductor
   first estimated -- `file_candidate` refuses a second filing via `r.hsetnx(FILED, ...)`, so a filings
   LIST would suffice. Still dropped. Do not build it.

## Instrument notes you will need at science time (NOT build work -- do not start these now)

- The Clause B round-7 FAIL STANDS and is not relabelled. The hardened control did its job. No transfer
  matrix this round.
- Report the 0/40 planted-negative result as an INTERVAL: one-sided 95% upper bound
  `1 - 0.05^(1/40)` = **<= ~7.2%**, never "0%". The rule of three gives ~7.5%.
- If round 8 changes sham or control semantics, the CHANGED instrument is RECALIBRATED before any live
  pair. A verdict on an uncalibrated instrument is not a result.
- Dry-run `envelope.admit` before posting a predicate, AND dry-run the receipt guard on a SYNTHETIC
  receipt. A round-6 Clause B pair ran clean and was then refused by the guard at receipt time.

## Rules

- Every item ships with a regression test AIMED AT THE CLAIM.
- Write every check script as a quoted heredoc (`python - <<'PY' ... PY`); print `checks run: N`.
- Commits are gated on pytest's OWN rc, never a pipe's.
- Push with ops.push. Do NOT start any worker, clock or controller.
- `bus inbox` is NEVER piped. Production seats (SFE/Daedalus, Vivarium, wforge) are READ ONLY.

Each iteration: bus beat, bus inbox (unpiped), one item, tests, push, 3-8 lines in journal/E.md.
Done: post "E R8 BUILD DONE" to A with shas, the suite rc, and C2/C3 each marked LANDED or NOT LANDED.
