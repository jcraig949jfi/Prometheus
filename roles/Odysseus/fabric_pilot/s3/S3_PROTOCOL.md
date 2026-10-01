# S3: open-research adoption of Fabric v0.2, principal ARTEMIS (DRAFT to be frozen by Artemis)

- **Prepared by:** Odysseus (ubu001), 2026-09-28, per the operator ruling (verbatim to be filed alongside).
- **Status:** DRAFT, READY FOR THE PRINCIPAL (2026-09-29). The principal fills in section 3, and freezes this file by
  commit BEFORE the one submission.
- **MWO-0004 G1 (2026-09-29), supersedes the placement below:** Artemis runs S3 from her EXISTING instance on
  ubu002. The same-host/separate-session test on ubu001 is dropped for this run and recorded as **NOT RUN** (not
  passed). No operator-managed session is started.
  - Canaries for this run: the Odysseus-seat canary and the host fixture on ubu001, where the generic workers
    execute.
  - An Artemis-context canary on ubu001 is not applicable, because her seat memory lives on ubu002 and no Fabric
    worker runs there.
- **Rulings folded in:**
  - operator 2026-09-29 (prompts/2026-09-28_fabric/06_*): Artemis is the principal, after her self-test's blinded
    scoring and unsealing (done); the same principal as the control gives the strongest comparison;
  - MWO-0001: v0.2 only; promexec NOT used.
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
- **Code execution (MWO-0001: promexec is NOT ENABLED and NOT used in S3).**
  - Claude workers cannot run code.
  - Where computation is needed, the worker writes the analysis code as an artifact. The principal may review it,
    commit it, and submit a pinned `script` Task that runs it (on a worker whose probed environment fits, e.g.
    `python.numpy`).
  - Each review, commit and script submission is a counted COORDINATION action (category "code-stage"). This is
    the known cost of running without promexec, and S3 measures it (DEF-ODY-007).

## 3. Workload (the PRINCIPAL fills this in; frozen before submission)

8-12 genuine open research packages, the same class as Archaeon's and Artemis's manual farm-outs. Each requires
repository archaeology, evidence comparison, analysis, and a substantive written conclusion.

| id | question (as a principal would pose it) | budget (min) | required artifacts beyond REPORT.md | quality criterion specific to it |
|---|---|---|---|---|
| Q1 | roles/Artemis/s3/draft/Q1.package.md, verbatim (harvested thread FR-028, cluster C; question and sources not rewritten, MWO-0001 s10) | 90 | out/analysis.py only if a computation is needed | answers the harvested question from cited primary evidence, or states precisely why it cannot within budget |
| Q2 | roles/Artemis/s3/draft/Q2.package.md, verbatim (harvested thread FR-075, cluster K; question and sources not rewritten, MWO-0001 s10) | 90 | out/analysis.py only if a computation is needed | answers the harvested question from cited primary evidence, or states precisely why it cannot within budget |
| Q3 | roles/Artemis/s3/draft/Q3.package.md, verbatim (harvested thread FR-053, cluster F; question and sources not rewritten, MWO-0001 s10) | 90 | out/analysis.py only if a computation is needed | answers the harvested question from cited primary evidence, or states precisely why it cannot within budget |
| Q4 | roles/Artemis/s3/draft/Q4.package.md, verbatim (harvested thread FR-099, cluster N; question and sources not rewritten, MWO-0001 s10) | 90 | out/analysis.py only if a computation is needed | answers the harvested question from cited primary evidence, or states precisely why it cannot within budget |
| Q5 | roles/Artemis/s3/draft/Q5.package.md, verbatim (harvested thread FR-115, cluster M; question and sources not rewritten, MWO-0001 s10) | 90 | out/analysis.py only if a computation is needed | answers the harvested question from cited primary evidence, or states precisely why it cannot within budget |
| Q6 | roles/Artemis/s3/draft/Q6.package.md, verbatim (harvested thread FR-102, cluster M; question and sources not rewritten, MWO-0001 s10) | 90 | out/analysis.py only if a computation is needed | answers the harvested question from cited primary evidence, or states precisely why it cannot within budget |
| Q7 | roles/Artemis/s3/draft/Q7.package.md, verbatim (harvested thread FR-119, cluster L; question and sources not rewritten, MWO-0001 s10) | 90 | out/analysis.py only if a computation is needed | answers the harvested question from cited primary evidence, or states precisely why it cannot within budget |
| Q8 | roles/Artemis/s3/draft/Q8.package.md, verbatim (harvested thread FR-022, cluster B; question and sources not rewritten, MWO-0001 s10) | 90 | out/analysis.py only if a computation is needed | answers the harvested question from cited primary evidence, or states precisely why it cannot within budget |
| Q9 | roles/Artemis/s3/draft/Q9.package.md, verbatim (harvested thread FR-077, cluster K; question and sources not rewritten, MWO-0001 s10) | 90 | out/analysis.py only if a computation is needed | answers the harvested question from cited primary evidence, or states precisely why it cannot within budget |
| Q10 | roles/Artemis/s3/draft/Q10.package.md, verbatim (harvested thread FR-055, cluster F; question and sources not rewritten, MWO-0001 s10) | 90 | out/analysis.py only if a computation is needed | answers the harvested question from cited primary evidence, or states precisely why it cannot within budget |
| IP1 | identity probe (s1): roles/Artemis/s3/draft/IP1.package.md | 90 | none | reports NO SEAT IDENTITY OR MEMORY FOUND, or quotes what it found |
| IP2 | identity probe (s1): roles/Artemis/s3/draft/IP2.package.md | 90 | none | as IP1 |

**FROZEN by the principal (Artemis, ubu002, MWO-0004 G1) at the commit that adds this paragraph.**
- Packages: a seeded draw of 10 from 56 eligible raw backlog threads. Rule and seed:
  roles/Artemis/s3/DRAFT_WORKLOAD.md and build_s3_draft.py, drawn at 742243972 (fda8cbc28). The seed is sha256 of
  this file as it stood then. The draw is kept, not re-drawn after this file's later edits.
- Submission: roles/Artemis/s3/submit_s3.sh <base = origin/main at submission>, one command. All 12 tasks run with
  executor claude, --model claude-opus-5-5 (the control model), --wall-s 5400, --replicas 1,
  --cap research.repo_readonly --cap fabric.runtime==0.2, and --thread thr-s3.
- Actions log: roles/Artemis/s3/ACTIONS.jsonl, from this freeze onward.
- Same-host separation test (s1): NOT RUN (MWO-0004 G1).

**Required artifacts for every package:**
- `REPORT.md`: question, method, evidence with `path:line` or `<commit>:<path>` citations, result, limits, and
  what would change the conclusion;
- `claims.json`: every load-bearing claim, with evidence pointers and confidence.

The runtime also deposits `final_text.md`, stdout, stderr, the env receipt and any out/ files.

## 4. What counts (frozen definitions)

**Scientific vs coordination actions** (operator 2026-09-29; the principal is also the control principal).

SCIENTIFIC actions are NOT overhead. They are logged separately, for the record only:
- reading returned research;
- adjudicating disagreement;
- designing a follow-up;
- rejecting or accepting a worker conclusion;
- integrating evidence;
- the synthesis.

COORDINATION actions are the measured overhead. Categories:
- dispatch;
- polling or status checks;
- finding a worker;
- recovering a crash;
- restart or resubmit;
- salvaging a report;
- isolation audit;
- managing a lease or concurrency;
- moving or archiving an artifact;
- fixing an environment;
- routing decisions;
- code-stage review/commit/submit (above);
- messages to or from a worker operator.

Every action is logged in `ACTIONS.jsonl` when it happens, with `"kind": "scientific"|"coordination"` and a
category. The control (Artemis's self-test ledger) is re-coded with the same split before comparison: its
CONTROL_COUNT categories dispatch, completion, isolation audit, salvage, incident, rule, concurrency and routing
are coordination; its scoring shepherding is coordination; any adjudication is scientific.

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
- **Gate:** 1.0 or fewer COORDINATION actions per execution, AND mean quality at least the control's minus 1 point (of 10), AND
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
