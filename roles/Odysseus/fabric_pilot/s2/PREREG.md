# Fabric adoption experiment, pilot S2: can a research principal stop shepherding workers?

- **Author:** Odysseus (ubu001). Frozen 2026-09-28, committed BEFORE any S2 task is submitted.
- **Operator ruling:** `roles/Odysseus/prompts/2026-09-28_fabric/04_OPERATOR_RULINGS_v01_verbatim.md`. Next phase
  is a measured adoption experiment; the metric is principal coordination actions, not throughput. Pure ASCII.

## 1. The adoption experiment (three work classes)

| class | what | this experiment's instance |
|---|---|---|
| 1 disposable research workers | literature, repo archaeology, adversarial review | S2 verifiers (below), plus the D2 v2 re-audit (`audit.security.adversarial`, submitted by Nestor) |
| 2 deterministic light compute | replay, analysis, verification jobs | the D2 v2 self-tests as script tasks (Nestor), and later TH-006-style attestations and Archaeon #813 recert |
| 3 multi-worker scientific workflow | the principal delegates several Tasks and synthesises the returned Artifacts | S2 (below) |

A later phase is a principal seat running on the same machine as the workers (ubu001), at the operator's request.
It is not part of S2.

## 2. Control (historical, not retrofitted)

- **Source:** Artemis's prospective self-test (36 bounded research executions by disposable workers, ubu002,
  2026-09-28). It is finished (RESULT.md), and its frozen scoring is not touched.
- **Control count:** coded from `roles/Artemis/selftest/LEDGER.md` by `control_count.py`, output in
  `CONTROL_COUNT.json`. It is a lower bound that counts only what the orchestrator wrote down:
  - 35 manual dispatches;
  - 36 completions noticed and recorded;
  - 36 per-run isolation audits (7 flagged);
  - 5 report salvages (a worker's Write was blocked and the report was recovered from its final reply);
  - 14 procedural or incident notes: quota incident, sealed-material move, audit-rule changes, template changes,
    concurrency and lease, containment, scoring.
  - Total: **126 actions for 36 executions (3.5 per execution).**

## 3. Treatment: S2, verifying the claims Artemis routed to Odysseus (#889)

Artemis's workers made claims about the program. Artemis marked them unverified and routed to Odysseus those that
concern its lane ("check against your own records before acting"). S2 verifies them through the fabric.

**Scope rule (protects Artemis's open endpoint).** Artemis's prereg A2.7 re-checks owner decisions (ED) at day 30.
S2 therefore verifies only the claims routed to Odysseus, which is owner behaviour, and posts nothing to other
seats' owners before 2026-10-28. The only outward message allowed is a reply to Artemis on #889 for claims found
wrong, which Artemis invited.

### Claims (atomic, from #889 and the cited report lines)

| id | claim | source |
|---|---|---|
| C1 | Of the 12 engine headlines, the not-recomputable-from-Git gap is exactly: BEE multi-day outcomes (seat branch plus M2 only), Z80xAtlas RUNS.jsonl, and the BEE coupling denominators. All other headline inputs are in Git. | R-13 table lines 55-70 |
| C2 | The B6 count W_by_location=NO and W_by_material=YES = 27,083 comes from main (`archaeon/causal_lens/out_v02/B6_PROBE_r038751.json`). Its replay result_sha256 cd9547c2... equals the committed recipe/pack, and an M2 attestation of it is on main. | R-13 l.37, 62, 73-78 |
| C3 | Aether rcv_add: `units_manifest.json` records artifact-file hashes but no per-unit result_sha256, and the committed BUCKKEEP (Windows) seed-0 unit's result_sha256 is 08929d70.... | R-13 l.93, 157-158, 198-199 |
| C4 | 13 of the 47 BEE ECHO K40 ledger rows (including 5 of the 6 YOKED rows) carry arch.self_copy = false. | R-13 l.104, 204 |
| C5 | Aphrodite "accepted" means capped admissions (K = 4). | #889 |
| C6 | Aphrodite A17 per-draw and per-replicate evidence exists only on aphrodite/* seat branches, not on main. BEE multi-day evidence is branch-only as well. | R-13 l.59, 67, 183 |
| C7 | A declared (varied, observed) lens pair recovers only 23-34% of the known Z80 cross-seat convergence, with 56-84% precision, and the per-field coding agreement is kappa 0.73-0.76. The numbers must be reproducible from R-34's committed coding files. | R-34 l.82 |
| C8 | Archaeon SFE campaign records and Aphrodite both code as improver x improvement-rate. SFE D8, Aphrodite and Odysseus natural-induction code as improver x task-skill. | R-34 l.74-75, 109-110 |
| C9 | The Atlas harvester does not index envgate, envgate2 or z80atlas, and no lens field exists in `atlas/`. | R-34 l.37, 114-115 |

### Execution

- **Tasks.** Each claim is one fabric Task with `--replicas 2`, giving 18 Tasks.
  - Executor: `claude` (claude-opus-5-5); wall limit 2400 s; capability `research.repo_readonly`.
  - Base: origin/main at freeze time.
  - Thread: `thr-fabric-s2`.
- **Prompt.** `VERIFY_TEMPLATE.md` plus the claim text.
- **Isolation.** The fabric sandbox provides it (the P7/P7b regime). There is no per-run transcript audit, and not
  doing one is part of what is measured.
- **Dispatch.** One command submits all 18 Tasks (`submit_s2.py`).
- **Principal conduct.** After submission the principal does NOT watch, poll, restart or rescue. One blocking wait
  runs until every S2 Task is terminal, then the principal reads the artifacts once.

### Per-claim decision rule (frozen)

- Each replica returns `verdict.json` with a verdict of CONFIRMED, REFUTED, PARTIAL or CANNOT-VERIFY, plus
  evidence.
- If both replicas agree, the claim's verdict is that verdict.
- If they disagree, Odysseus adjudicates by checking the cited evidence himself. Each adjudication is logged as a
  principal action.
- If a replica fails (no verdict), the claim is decided on the other replica, flagged "single replica". A failure
  is NOT resubmitted, so the failure counts as observed.

## 4. Measures

**Primary: principal coordination actions per execution.** They are logged in `ACTIONS.jsonl` at the time they
happen, in the control's categories:
- dispatch;
- completion noticed;
- isolation audit;
- report salvage;
- incident or mitigation;
- rule or template change;
- concurrency or lease;
- routing;
- adjudication or synthesis.

Design and preregistration actions are logged as `prep` and excluded. The control excludes them too, since they
are not in its ledger.

Secondary:
- executions completed without manual rescue;
- replica agreement (claims with both replicas agreeing, out of 9);
- wall time from submission to the last terminal Task;
- failed Attempts and their causes;
- per-claim verdicts.

**Pre-stated expectation (falsifiable).** Treatment actions per execution are <= 1.0, against 3.5 in the control.
Report salvages, per-run isolation audits and manual dispatches per run are all 0. If the treatment needs more
than 1.0 per execution, the claim that "the principal stops shepherding" is NOT supported at this scale, and the
report says so.

## 5. Threats (recorded now)

- The control and the treatment differ in task type (open research questions vs claim verification), in node
  (ubu002 vs ubu001), and in orchestrator (Artemis vs Odysseus).
- The control count is a lower bound from a ledger; its undercounting works against the treatment. The treatment
  log is written by the treated principal and could undercount in the treatment's favour. The comparison is
  indicative, not causal.
- The treatment offloads isolation to the sandbox. The residual risk of that sandbox (P7b scope) is not
  re-audited per run.
