# POST-ROUND FINAL STEPS (standing procedure)

Adopted after round 7 (2026-09-16) at operator request. This is the procedure for EVERY round close from
r8 onward. It exists because the operator reads and rules from a phone: the deliverable is one pasteable
ASCII block, and every number in it must be derived by code from code-owned streams, never from prose.

Scope: the CONDUCTOR (lane A) runs this. It is logistics only. The conductor never scores, never changes a
success criterion, and never authorises compute. Anything that would do those things becomes a QUESTION in
section 10 of the packet, or a PRODUCTION CANDIDATE.

---

## 0. HARD PRECONDITION: the round must be closed BY CODE

Do not start until all of these are true. Check, do not assume.

    PM_LANE=A python -c "from primordial.bus import bus; r=bus.conn(); \
      print(r.hgetall('pm:epoch:state'), r.get('pm:round:current'), len(r.keys('pm:worker:reg:*')))"

- `pm:epoch:state` phase == `closed`
- `pm:round:current` is None (unset by the close)
- 0 registrations, 0 stop flags
- `now > end_ts` for `pm:round:<id>`
- the epoch controller process has EXITED 0

A wrapper script's exit code is NOT the controller's exit code. In r7 the launch wrapper printed
`controller rc 2` from an unrelated quoting bug in the wrapper while the controller itself ran all 9 epochs
and exited 0. Read the controller's own tail, not the wrapper's.

---

## 1. FAST-FORWARD THE CONDUCTOR WORKTREE **FIRST**

    git fetch origin --quiet && git merge --ff-only origin/<integration-branch>

`close_sweep` reads receipt MIRRORS from the WORKING TREE. A stale checkout reads mirrors dated before the
round and reports zero cited. In r7 this produced a false "zero cited" alarm that was broadcast to seven
lanes before the conductor discovered its own checkout was 205 commits behind. **ff before every sweep.**

Git writes are safe here ONLY because the round is closed and no RowWriter is live. Never make any git write
(commit, add, checkout, rebase, push, and NEVER stash) in a worktree with a live RowWriter.

---

## 2. RUN THE CLOSE SCRIPT (one invocation, pre-staged during the round)

Keep a `r7_close.sh`-equivalent written and REHEARSED before the close, so the close is execution, not
assembly under a deadline. Rehearse every step except `--emit` while the round is still live.

Steps, in order:

1. ff the worktree (section 1)
2. round-record probe (section 0)
3. close tally  -> `<round>_close_tally.py > tally_close.json`
4. `close_sweep --round <id> --emit`   <- THE receipt-integrity check
5. `residue scan --round <id>`
6. epoch log tail (for the epoch table and the O7 audit)
7. lane-A post split (see section 3)

`--emit` writes `UNRECEIPTED_OBSERVATION` events. It MUST NOT be run against a live round.

Expected healthy output: `rows_files N, cited N, unreceipted []`, `emitted []`, sweep rc 0.

**`residue scan` exiting rc 1 at close is EXPECTED, not a failure.** A round whose workers have all exited
leaves one DEAD_CONSUMER per lane group (plus any shared service) with `pending 0`. These persist until the
NEXT round's build clears them. Do not clear them at close: `clear()`'s consumer half is not round-gated, so
you *could*, but doing so spends the round's clean intervention count on cosmetics. Record, don't clear.

---

## 3. COUNTING TRAPS -- CHECK EVERY ONE BEFORE QUOTING A NUMBER

Each of these produced a wrong number in a real packet draft. They are not hypothetical.

| trap | wrong number | correct derivation |
|---|---|---|
| Controller posts as lane A | `A_bus_posts_by_kind {'note': 45}` read as conductor action | SPLIT: subtract `^EPOCH \d+ boundary` notes. r7 = 45 total, 9 controller, **36 conductor** |
| PC stream length is all-time | `xlen(pm:production_candidates)` = 149 | count only ids inside the round's id window |
| Hand-written vs filed PCs | "three hand-written" | `hand_written_D27` from the tally; a stub filed via `file_candidate` is NOT hand-written |
| Defect count in the headline | "10 new defects (D18-D27)" after D28-D31 landed | recount the defect table at close, every time |
| Receipt counts vs rows files | "15 receipts" read as 15 rows files | receipts and rows files are different denominators; state both |
| A lane's round-N receipt credited to round N+1 | B's r6 search-budget receipt credited to r7 | check the receipt's round, not the lane's presence |
| Hardware claims from memory | "4-core host" | query the host; r7's is 8 physical / 16 logical, RTX 5060 Ti 16 GB |
| Stale checkout sweep | "zero cited" | ff first (section 1) |

Rule of thumb: **any number that flatters the conductor or simplifies the story gets re-derived before it
ships.** In r7, five of the conductor's characterisations were corrected by lanes and two more by the tally.

### 3a. CHECKER-INTEGRITY TRAPS -- the gate can lie about itself

A counting trap gives a wrong number. These give a wrong VERDICT, which is worse, because the wrong verdict is
"everything is fine".

| trap | what happens | guard |
|---|---|---|
| Backtick / `$` / `!` inside a bash double-quoted `python -c` | the shell performs command substitution and DELETES part of the script; the rest runs and PASSES | write every check as a QUOTED heredoc: `python - <<'PY' ... PY` |
| A check set that can silently shrink | 2 of 12 checks vanish, 10 pass, gate prints PASS, commit proceeds | print `checks run: N` and assert N equals the number written |
| Reading only the verdict line | `command not found` scrolls past above a green PASS | read the lines ABOVE the verdict; an error there means the PASS describes a different script than the one you wrote |
| Gating on a pipe's exit code | `pytest \| tail && commit` gates on tail | capture the tool's own rc before committing |
| A matcher that matches itself | a psutil kill-by-cmdline matched its own source and its shell ancestors | exclude the whole ancestor chain; match interpreter + argv tokens |

**This happened during R8 launch prep**, not hypothetically: a markdown backtick in a gate script removed the
two checks verifying the launch preconditions, and the gate reported PASS anyway. The committed content was
correct by luck; the claim "it was verified" was not.

---

## 4. EVIDENCE DISCIPLINE -- NEVER CONFLATE

Every scientific item in the packet is written as four SEPARATE labelled parts. Do not merge them, do not
let one imply another:

- **OBSERVATION** -- what ran, how many runs, what was measured, with row/receipt ids and shas.
- **ELIGIBILITY** -- whether the sample rule (CANDIDATE_N / EVIDENCE_N_v1: 32 runs, 4 families, 8 per family,
  structurally balanced) was met, and which predicate was pinned BEFORE the run.
- **VERDICT** -- what CODE decided, with the receipt id and guard result. Never what the conductor thinks.
- **INTERPRETATION** -- explicitly labelled as inference, and explicitly bounded ("no mechanism is claimed").

A PASS whose arms cannot discriminate is VACUOUS and must be reported as such (r7 AP-03: all 64 runs in both
arms returned exactly 31.71875, IQR 0.0). A verdict on an uncalibrated instrument is not a result: measure
the control's own false-positive rate FIRST (r7 O8: 0/40 planted negatives before the live Clause B pair).

---

## 5. PACKET STRUCTURE (fixed section order)

0. ELI5 executive summary -- ONE paragraph, no jargon, no ids.
1. Operations -- clock, epochs, jobs, grants, interventions, receipt integrity.
2. Scientific findings -- one block per finding, in the section-4 format.
3. Null and negative results -- stated as results, not as gaps.
4. Instrumentation defects -- numbered, with status and PC id.
5. Production candidates -- table with measured or estimated basis.
6. Epistemic state -- what is known, what is unresolved, what is parked with cost.
7. Proposed next-round design -- PROPOSALS ONLY, each needing an operator ruling.
8. Performance / throughput options -- against measured hardware limits.
9. Telemetry and logging proposals -- what to capture NEXT round to answer this round's unanswerables.
10. Questions -- for OPERATOR, for HITL, and for EXTERNAL REVIEWERS, separately.
11. Reproduction pointers -- branch, shas, receipt ids, predicate refs, rows paths.
A. This procedure (so the packet is self-describing to an external reader).

---

## 6. DELIVERY RULES

- ONE fenced ASCII block. The operator copies from a phone; a packet split across blocks is unusable.
- Pure ASCII. Verify: 0 characters with `ord(c) > 126`.
- 0 unfilled placeholders. Verify by grep before commit.
- Long table rows are acceptable (they soft-wrap); a second fenced block is not.
- Put the DECISIONS the operator must make ABOVE the block, so they are visible without scrolling past it.
- Commit the packet to the round's sidequest directory and push, gated on git's own rc, never a pipe's.

---

## 7. TELEMETRY TO CAPTURE **DURING** THE ROUND

Each of these exists because a post-round question could not be answered from r7's record. Land them in the
BUILD phase of the next round; they are cheap and they compound.

1. **Per-job resource samples** -- RSS, CPU%, thread count sampled every 30 s into the job's done record.
   r7 can report CPU-s but cannot say whether a job was memory-bound, thread-starved, or idle-waiting.
2. **Token wait time** -- stamp queue-entry and grant time per job. D22 (broker not FIFO) was diagnosed from
   a lane's complaint, not from data; a wait histogram would have shown it on the first boundary.
3. **Queue depth timeseries** -- per lane, per epoch. D30 (continuations lose queue position) cost 4 cells
   and was invisible until a lane noticed.
4. **Per-generation timing for evolution jobs** -- not just per-job wall. GPU/CPU backend comparisons need
   per-generation cost to project, and r7 had to project `w13 train128` rather than measure it.
5. **Oracle outcome counts as structured fields**, not prose in a FINAL post.
6. **A machine-readable FINAL** -- every lane emits `FINAL.json` (receipts, rows, PCs, open claims, own
   errors) alongside its prose post. r7's packet was assembled by reading five prose finals, which is where
   several conductor misreadings came from.
7. **Watcher liveness beacons** -- every lane watcher emits a heartbeat with its own stop time. D31 (a lane
   goes deaf at close) and G's silently-dropped asks were both silent failures.
8. **Host-level sampler** -- total CPU/GPU/RAM every 60 s for the whole round, committed as rows. r7 can only
   compute average utilisation by dividing job CPU-s by wall time.
9. **Event id of the predicate in every row**, so rows are traceable without joining through receipts.
10. **A `WHY_NOT_RUN` record** for every drawn-but-unrun cell, with the lane's stated reason (r7 AP-05 was
    recorded only in prose).

---

## 8. STANDING RULES THAT APPLY AT CLOSE

- Significant operator prompts are committed VERBATIM with sha256 in MANIFEST at issuance.
- Production seats (SFE/Daedalus, Vivarium) are read-only to Nestor; never start or stop them.
- Never `pip install` into `gw-venv`.
- LLM lanes do not score themselves.
- Never `git stash/pop/drop` in a Prometheus worktree -- `refs/stash` is shared across worktrees.
- Count and report every conductor intervention, including ones that turned out to be correct.
- A lane's self-disclosed error is worth more than an audit finding: record it with the lane's own numbers,
  and if the lane disputes the conductor's framing, record the DISPUTE, not the conductor's version.

---

## 9. CHECKLIST (run in order)

    [ ] round closed by code, controller exited 0 (not the wrapper's rc)
    [ ] ff conductor worktree
    [ ] close tally rc 0
    [ ] close_sweep --emit: rows == cited, unreceipted [], rc 0
    [ ] residue scan recorded (rc 1 with pending-0 dead consumers is EXPECTED)
    [ ] every section-3 counting trap checked
    [ ] 0 placeholders, 0 non-ASCII, section order correct, no duplicate rule entries
    [ ] hardware/perf claims re-queried from the host, not recalled
    [ ] packet committed + pushed, sha recorded
    [ ] decisions listed ABOVE the paste block
    [ ] memory updated: round state, new traps, lane corrections
    [ ] background watches stopped; no orphan tasks
