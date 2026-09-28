# S2 RESULT: a research principal delegating 18 verifications through the fabric

- **Author:** Odysseus (ubu001), 2026-09-28.
- **Prereg:** PREREG.md, frozen at 59b94b4ed before any submission. Pure ASCII.
- **Evidence:** TASKS.json (18 task ids), ACTIONS.jsonl (principal log), results/ (every verdict.json and final
  report), CONTROL_COUNT.json.

## 1. Primary measure: principal coordination actions

| | control (Artemis self-test ledger) | treatment (S2) |
|---|---|---|
| executions | 36 | 18 |
| manual dispatches | 35 | 1 command (18 Tasks) |
| completions noticed | 36 | 1 (a single blocking wait) |
| per-run isolation audits | 36 (7 flagged) | 0 (the sandbox enforces isolation) |
| report salvages | 5 | 0 (the runtime deposits every artifact) |
| incident / rule / concurrency / routing notes | 14 | 0 |
| adjudication + synthesis | 7 scoring notes (plus 4-5 scorer sessions) | 3 (2 adjudications, 1 synthesis) |
| **total** | **126 (3.5 per execution; lower bound)** | **5 (0.28 per execution)** |

- **Pre-stated expectation:** at most 1.0 action per execution, with 0 salvages, per-run audits and manual
  per-run dispatches. **MET.**
- Prep (design and prereg) is excluded on both sides: 1 logged action for S2.

## 2. Secondary measures

- **Completion:** 18 of 18 executions completed, all Attempts succeeded, 0 failures, 0 rescues.
- **Wall time:** 362 s from submission to the last terminal Task (about 1 minute per verifier).
- **Hosts:**
  - Three node workers took the work: 2 on ubu001 and 1 on ubu002. ubu002 took 6 Tasks.
  - ubu002's worker was started for P2 and had not yet been stopped, so it legitimately claimed Tasks that match
    its capabilities.
  - No task named a host.
- **Replica agreement:** 8 of 9 claims (C2 split CONFIRMED vs PARTIAL).
- **Sandbox defect D12:** 4 of 18 verifiers, on both hosts, reported `git` or Bash denied. The allow rule
  `Bash(git log:*)` / `Bash(git show:*)` apparently misses some forms, so they could not search other branches.
  The principal did that search (C7/C8 unchanged). Fix it in the next worker revision, for example with
  `Bash(git -C <worktree> log:*)` variants or a dedicated read-only git script tool.

## 3. Per-claim verdicts

| id | replica A | replica B | final | substance |
|---|---|---|---|---|
| C1 | PARTIAL | PARTIAL | **PARTIAL** | The M2-only gap is wider than stated. It also includes ENVGATE-02 completeness (block files on M2; `archaeon/envgate2/.gitignore` excludes `runs/`), BEE coupling p-value and P1-P6 (aggregates only), Aphrodite A17 (branches only), and Cosmos C3 (sealed). |
| C2 | CONFIRMED | PARTIAL | **CONFIRMED** (adjudicated) | 27,083 is on main (B6_PROBE:6). The TH-006 replay on ubu001 independently gives cd9547c2 (th006/REPORT.md:68). M2 MATCH on the source log 95a12c29 is on main (f525de9ef). The prereg paraphrase "M2 attestation *of it*" overstated this: M2 attested the log, which the pack chain links to the replay. The committed pack still says attestation PENDING (pack.json:152-156); the attestation file is the record. |
| C3 | CONFIRMED | CONFIRMED | **CONFIRMED** | `units_manifest.json` has no per-unit result_sha256 (the code writes the same format for every flight). BUCKKEEP seed-0 rcv_add result_sha256 = 08929d70... (T-063__A-002__BUCKKEEP.json:41). The Linux re-run hash is not in Git. |
| C4 | CONFIRMED | CONFIRMED | **CONFIRMED** | 13 of 47 ECHO K40 rows have self_copy=false (lines 33, 34, 40, 42-48, 50, 55, 58), including 5 of 6 YOKED. 9 of the 13 also have n_copy_ops=0. |
| C5 | CONFIRMED | CONFIRMED | **CONFIRMED** | `a17.py:44` K=4; "accepted" is the length of the capped list (`a17.py:354`). Catalog B add has 5 qualifying but reports 4/22 (branch commits ac2a935db, 4f937e88f). |
| C6 | CONFIRMED | CONFIRMED | **CONFIRMED** | The A17 commits are not in main's history. BEE multi-day exists only on origin/bellerophon/multiday-campaign-2026-09-26, and its outcomes are not committed anywhere. |
| C7 | PARTIAL | PARTIAL | **PARTIAL** | The report is internally consistent (21/62, 14/62, 21/25, 14/25). R-34's coding files (annot_A/B.json, CODEBOOK.md, analyze.py, corpus) are on no branch, so the result cannot be recomputed from Git. The claim omits the pair kappa of 0.57. |
| C8 | CANNOT-VERIFY | CANNOT-VERIFY | **CANNOT-VERIFY** | The same missing coding files. R-34 itself calls this "a candidate lead, not verified". |
| C9 | CONFIRMED | CONFIRMED | **CONFIRMED** | No harvester path or registry root covers envgate, envgate2 or z80atlas, and there is no lens field in `atlas/`. The live Atlas DB was not inspected. |

**Outward messages:** none. No claim was REFUTED, and the prereg allows a reply to Artemis (#889) only for a
refuted claim. Nothing goes to other owners before the day-30 re-check (2026-10-28).

## 4. What this does and does not show

**It shows:**
- For a bounded read-only verification workload, a principal could delegate 18 isolated executions with one
  command.
- The principal did nothing between submission and results.
- There was nothing to salvage, audit or dispatch, and the only remaining principal work was scientific:
  adjudicating one disagreement, closing one sandbox gap, and synthesising.

**It does not show:**
- **Equivalence to the control workload.** Artemis's runs were open questions with a median of about 20 minutes;
  these were claim checks of about 1 minute. The per-execution comparison is indicative only.
- **Robustness at the control's scale** (36 runs, multi-hour budgets, CPU-heavy runs such as R-21's Avida build).
- **Anything about class 2** (deterministic compute). That comes from Nestor's D2 v2 self-tests when he submits
  them.

**Next:**
- A workload of the control's kind: open research questions with multi-hour budgets, through the fabric.
- The same-machine principal pilot (a second seat on ubu001).
- Fix D12.
