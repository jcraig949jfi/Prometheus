# S3 principal synthesis (Artemis, ubu002, 2026-09-29)

Protocol: roles/Odysseus/fabric_pilot/s3/S3_PROTOCOL.md, frozen by the principal at 2a229c9a2 (MWO-0004 G1).
Tasks: roles/Artemis/s3/TASKS.json (base 5266cceb). Actions: roles/Artemis/s3/ACTIONS.jsonl. Evidence for
the reading: roles/Artemis/s3/DIGEST.md (a fresh reader checked 3 claims per package; the principal re-checked
Q8 C4 in the code). Quality scoring (s5, two blind scorers, mixed with sanitised control reports) and the
authoritative canary scan belong to Odysseus and are NOT part of this file.

## 1. Execution (measured)

- One submission (12:52Z) and one completion barrier (closed 13:29:34Z, 37 min).
- 12/12 Tasks completed, each with 1 Attempt. 0 resubmits, 0 crashes, 0 rescues, 0 lost or duplicate executions.
- Workers: worker.ubu001.a and worker.ubu001.b. Model claude-opus-5-5 (the control model).
- Attempt wall time: Q1..Q10 3.9-11.7 min (budget 90); IP1/IP2 0.8 min each.
- Every Q package returned out/REPORT.md, out/claims.json and out/analysis.py.
- Principal COORDINATION actions: 8 for 12 executions = 0.67 per execution. Breakdown:
  - status checks: 3 (canary go; barrier start; barrier return);
  - messages to/from the worker operator: 2 (freeze notice; closeout);
  - dispatch: 1;
  - artifact fetch: 1 (one scripted pass);
  - isolation audit: 1 (principal-side prefix scan).
  - Code-stage: 0.
- SCIENTIFIC actions (not overhead): reading, two accept decisions, one follow-up design, this synthesis.
- Control, for comparison: the 2026-09-28 self-test ledger, 126 actions over 36 executions = 3.5 per execution,
  before Odysseus's scientific/coordination re-coding.

## 2. Isolation

- IP1 and IP2 both report no seat identity and no seat memory.
- The principal-side scan found no CANARY- string with a random suffix in any artifact. The hits are the unfilled
  templates the probes quoted from S3_PROTOCOL.md:39-41, which is public in the repo.
- Same-host/separate-session test: NOT RUN (MWO-0004 G1). The Artemis-context canary is not applicable.
- The authoritative scan uses the real canary values and is Odysseus's.

## 3. Did the work come back scientifically usable? (principal judgement, before blind scoring)

- All 10 answered their question (YES, some PARTLY on a sub-part).
- 30/30 checked claims were verified against the repo at 5266cceb. No report is unreliable.
- Principal redos: 0.
- Caveats that stand: Q6 budget parity (QD kept 14-15 items vs 16); Q10 over-reads a single-root Hermes incident;
  Q5's "fifth pressure" may never have been sent out; Q4's catch counts had one reader; Q9's fairness proof holds
  only over the full 2^64 period.
- Short run times: Q2, Q3, Q4 and Q8 leaned on the workers' own sub-agent sweeps. Every citation opened was exact,
  so speed did not cost correctness in the checked claims. Depth is for the blind scorers to judge.

## 4. What this says for Artemis's lane

- Consistent with the self-test (sharpening not shown to add yield): raw harvested questions, dispatched verbatim,
  came back answered, cited and consequential.
- The dispatch cost fell from about 3.5 to 0.67 principal coordination actions per execution.
- New finding about Artemis's own product: the harvest's "later evidence" field was wrong or stale in 5 of 10
  packages (Q1, Q4, Q5, Q9, Q10), 2 days after harvest. A harvest's currency claims decay fast. The worker, not
  the curator, should establish current status. Packages should say that the harvest's status notes are
  unverified.

## 5. Consequential findings (routed to owners after S3; routing is lane work, not an S3 action)

Q8 (Bellerophon): G1T task cells share seeds. G2 63/160, the G6 origin counts and ERRATA 103/160 are
pseudo-replicated, and "replication shows no task dependence" stands unqualified. Q1 (Archaeon): attribution v0's
singular parent uses FLOW shares, so a byte-identical-to-a child is labelled b. Q9 (Aether): the required
pre-campaign arbitration-bias check was never run. Q7 (Theophrastus): a failed preregistered prediction is listed
as "predicted". The other packages are in DIGEST.md.

## 6. Limits

- One principal, who also designed the control. 12 executions. Quality is not yet blind-scored.
- The workload was a seeded draw of repo-only raw questions. It excluded memory/SI, holdout and host-affine
  threads, so the task mix is easier to host than the control's.
- Not a benchmark. The migration decision is the operator's (S3_PROTOCOL s8).
