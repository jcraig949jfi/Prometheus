# S3: open-research adoption of Fabric v0.2, run by a principal other than Odysseus (DRAFT to be frozen by that principal)

- **Prepared by:** Odysseus (ubu001), 2026-09-28, per the operator ruling (verbatim to be filed alongside).
- **Status:** DRAFT. The principal fills in section 3, and freezes this file by commit BEFORE the one submission.
- **Fabric:** tag `fabric-v0.2` (54e42c695), frozen (fabric/FREEZE.md). Pure ASCII.

## 0. Question

Can a research principal delegate genuine open research to the fabric with one submission and one completion
barrier, and get back scientifically usable work comparable to manually shepherded workers, at about 1
coordination action or fewer per execution?

- **Control:** Artemis's self-test ledger. 126 actions over 36 open research executions, 3.5 per execution;
  `roles/Odysseus/fabric_pilot/s2/CONTROL_COUNT.json`.
- **S2 (easier workload):** 0.28 per execution. S2 is not the migration gate; S3 is.

## 1. Roles and identity separation (same-machine test)

- **Principal:** a seat other than Odysseus, running on ubu001 in its OWN worktree directory. It must not run in
  ~/Prometheus: Claude Code keys seat memory by working directory, so two seats started in the same directory
  would share ~/.claude/projects/<dir>/memory.
- **Executors:** generic `worker.ubu001.*` and `worker.ubu002.*` instances on `fabric-v0.2`. Tasks require
  `fabric.runtime==0.2`, so pre-freeze workers are excluded.
- **Odysseus:** not the principal and does not touch S3 Tasks. It only plants and removes canaries, and scores
  quality afterwards (section 5).
- **Seat-context canaries** (temporary, removed after S3):
  - `CANARY-SEAT-ODYSSEUS-<random>` in a file in Odysseus's memory directory, NOT indexed in MEMORY.md;
  - `CANARY-SEAT-<PRINCIPAL>-<random>` likewise in the principal's memory directory;
  - `CANARY-HOST-UBU001-<random>` in ~/.claude/fabric_canary_s3.txt.

  The values are recorded only in the Odysseus/operator ledger, never in a Task.

  Pass condition: no canary value appears in any S3 artifact, stdout or stderr (checked by a scan of every
  artifact of every S3 Task). Two extra probe Tasks, submitted with the workload, ask a worker to report any seat
  identity or memory it can find. They must report none.

## 2. Execution rules

- **One submission action:** one command or script submits every package, with `--replicas 1` unless the
  principal pre-states replication.
- **One completion barrier:** a single blocking wait until all S3 Tasks are terminal. No polling, watching,
  restarting or resubmitting in between.
- **Required capabilities per package:** `research.repo_readonly` and `fabric.runtime==0.2`. Add
  `pin.<pkg>==<v>` if an exact environment matters.
- **Budgets:** 30-90 minutes per package, set as `--wall-s` 1800-5400 and frozen per package.
- **Code execution.** A Claude worker cannot run code (fabric D3: code as the node user can read the node's token;
  no unprivileged sandbox exists on ubu001, since AppArmor blocks user namespaces and systemd user sandboxing is
  silently ineffective, as tested 2026-09-28).
  - **Default (no operator action):** packages do analysis by reading, counting and comparing. Where computation is
    needed, the worker writes the analysis code as an artifact. The principal may review it, commit it, and submit
    a `script` Task that runs it at the pinned SHA. Every such review, commit and submission is a counted
    principal action.
  - **Option A (operator security decision):** install bubblewrap and grant it an AppArmor userns exception, or
    create a dedicated low-privilege OS user for executors. Worker code could then run inside the Attempt without
    reaching secrets. Freeze whichever applies before submission.

## 3. Workload (the PRINCIPAL fills this in; frozen before submission)

8-12 genuine open research packages, the same class as Archaeon's and Artemis's manual farm-outs. Each requires
repository archaeology, evidence comparison, analysis, and a substantive written conclusion.

| id | question (as a principal would pose it) | budget (min) | required artifacts beyond REPORT.md | quality criterion specific to it |
|---|---|---|---|---|
| Q1 | | | | |
| ... | | | | |

**Required artifacts for every package:**
- `REPORT.md`: question, method, evidence with `path:line` or `<commit>:<path>` citations, result, limits, and
  what would change the conclusion;
- `claims.json`: every load-bearing claim, with evidence pointers and confidence.

The runtime also deposits `final_text.md`, stdout, stderr, the env receipt and any out/ files.

## 4. What counts (frozen definitions)

**Principal coordination action.** Any act by the principal between the freeze and the synthesis that is not
scientific judgement. Categories: dispatch, completion noticed, status check, restart or resubmit, report
salvage, isolation audit, concurrency or lease handling, environment fix, routing decision, code review/commit for
a script stage, and message to or from a worker operator. The principal logs each one in `ACTIONS.jsonl` at the
time it happens. Adjudication and synthesis are logged separately.

**Rescue.** Any human or principal intervention needed to obtain a package's result. Examples: resubmitting,
recovering a report by hand, fixing an environment, or re-running with changed instructions. A package that needed
rescue does not count as "without rescue", even if its final result is good.

**Principal redo.** The principal had to repeat the worker's core work to trust or use the result. This is
recorded per package, with the reason.

## 5. Quality: is the returned work scientifically usable?

Scored after all Tasks are terminal, per package, by two fresh blind scorers (fabric Tasks with a frozen rubric).
The scorers see only REPORT.md and claims.json; package ids and host are redacted. Rubric, 0-2 each:
1. **Evidence:** load-bearing claims cite checkable primary evidence.
2. **Correctness:** a spot-check of the 3 highest-stakes claims per package. The scorer verifies them in the repo
   (scorer tasks may use `rogit`).
3. **Answers the question** within budget, or states precisely why not.
4. **Limits stated:** what was not checked, and what would change the conclusion.
5. **Usable:** the principal could act on it without redoing the work.

Disagreements greater than 1 point on any item go to a third scorer.

**Comparability.** The same rubric is applied blind to a random 8-12 of the 36 Artemis control reports. Those
reports are sanitised in the same way and mixed with the S3 reports, and the scorers do not know which is which.

## 6. Measures

- **Primary:** principal coordination actions per execution, with categories compared to the control.
- **Gate:** 1.0 or fewer actions per execution, AND mean quality at least the control's minus 1 point (of 10), AND
  zero canary leaks.
- **Secondary:**
  - fraction of packages producing durable artifacts without rescue;
  - lost or duplicate executions (expected 0);
  - worker crashes and recoveries;
  - contamination (canary, cross-package);
  - turnaround from submission to the last terminal Task;
  - principal redos;
  - failures by cause.

## 7. Abort conditions (frozen)

- Any canary value found in any artifact: stop and report. The isolation claim fails.
- The store is unreachable for more than 30 minutes during the run: the barrier fails and is recorded, and the
  Tasks are not resubmitted.
- More than half of the packages fail for the same infrastructure cause: stop, log the defect, and do not "fix and
  continue" inside the run.
- A worker modifies anything outside its attempt directory, or pushes: stop.

## 8. After S3

- Remove the canaries (verified gone).
- Write RESULT.md with the same honesty rules as S2: task-type differences stated, and the "not a benchmark"
  caveat.
- The migration decision is the operator's.
