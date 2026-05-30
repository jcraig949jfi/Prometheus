# Aporia Ecosystem — Status and Next Steps (v0.2)

**Filed:** 2026-05-30 (revision)
**Author:** Aporia (in-session)
**Supersedes:** `pivot/aporia_ecosystem_status_and_next_steps_2026-05-30.md` (v0.1)
**Review absorbed:** James (frontier-review round, 2026-05-30)
**Doctrine discipline (unchanged from v0.1):** `feedback_take_a_stand`, `feedback_substrate_passive_consumer_warning`, `feedback_anti_gravitational_well`, `feedback_no_hard_tables`, `feedback_llm_convergence_is_gravity_amplifier`.

## 0. What changed from v0.1 (review-driven diff)

The v0.1 stands were directionally accepted but had one load-bearing blindspot named in review: **Stand A treated yield as a retrospective audit problem, when the deeper problem is missing pre-registered acceptance criteria at dispatch time.** A retrospective audit cannot distinguish "report was bad" from "report had no declared consumer" from "expected delta was never specified." Five revisions land in this version:

- **Stand A splits into A1 (retrospective) + A2 (forward dispatch contract).** A2 is the load-bearing piece; A1 is its calibration data.
- **Stand B splits inbox semantics into queue and ledger.** OPEN means two distinct things ("work this now" vs "remember this signal"); the v0.1 close-or-promote framing forced ledger-shaped tickets into queue-shaped verdicts. v0.2 vocabulary: `ACTIVE_QUEUE / CHARTER / DOCTRINE_CANDIDATE / PARKED_SIGNAL / WONTFIX / SUPERSEDED`.
- **Stand C adds a 20-ticket sample backfill test + a consumer-read test.** Annotation discipline is taxonomy theater unless a downstream agent's pull decision changes based on the new fields.
- **Stand E allows one narrow automation immediately: `aporia_triage_report.py` as an instrument panel (surfaces signals, does not decide).** Daemonization stays deferred.
- **NEW Stand F — every stand emits a deletion candidate.** Mature substrate retires machinery, not only adds doctrine.
- **NEW Stand G — carrying-capacity throttle experiment.** Cap intake for one week, measure quality delta. Falsifies/confirms the "overload" hypothesis that v0.1 didn't surface.

The "strict sequence, no parallelism" execution order from v0.1 is softened: Stand A2 (forward contract) and Stand C (NEW-ticket schema) can begin in parallel because they both apply only to tickets/reports filed AFTER the schemas land.

The promotion path also tightens. v0.1 said surviving stands promote after the review round. v0.2 says: **surviving stands promote to `aporia/doctrine/aporia_ecosystem_doctrine.md` after ONE FULL CYCLE of A2 + B + C has run.** The doc is doctrine when the contracts have produced their first measurement, not before.

## 1. Where Aporia sits (unchanged)

Aporia is a role, not a daemon. Its outputs:
- An open-problem catalog (`aporia/{domain}/`, 13 domain directories)
- A doctrine corpus (`aporia/doctrine/`)
- An inbox plumbing layer (`aporia/meta/queue/*.jsonl`)
- Substrate-shaped pilot batches and adjudication artifacts

The longer-term direction (per `project_aporia_reorientation`) is to pivot from oracle mode (answering "what should we do?") to instrument mode (running blind trials, falsifying frames, surfacing voids).

## 2. Status of the four components (updated counts)

### 2.1 Aporia role + catalog

- 13 domain directories; "322 open problems" claim is 6-month-old and remains unaudited
- Recent doctrine additions concentrated in Lean / external-tool primitives; domain catalogs (mathematics, physics, biology, ...) have not received structured updates in the same window
- Operating in-session; instrument-mode pivot documented but not built

### 2.2 Pythia DR dispatch

- **55 reports filed 2026-05-26 → 2026-05-30** (IDs 00377-00431). Distribution:
  - Moros cross-pollination critiques: ~16
  - Stygian primary-literature surveys: ~13
  - Hecate retraction-pattern surveys: ~6
  - Lethe forward false-anchor hunts: ~9
  - Acheron coordinate-collision hunts: ~7
  - Hypatia D-track proof-decomposition: ~4
- **Yield un-measured.** No declared consumer or expected delta on any of the 55. This is the dispatch-contract gap Stand A2 fixes prospectively and A1 measures retroactively.

### 2.3 Charon swarm

- 8 daemons in one process (Stygian / Lethe / Acheron / Moros / Hecate / Nephele / Pollux / Erebos)
- Erebos at v3 Phase 1B ITER-39 — 13+ iterations in 4 days, kill_pattern_registry + residue revocation + ComposedClaim + cost-instrumentation
- **Techne 89-fire 0-promoted streak persists as of last measurement.** 360M+ lifetime kills, 2,351 discoveries, flat for 3+ days. Erebos rebuild is the intended fix.

### 2.4 Inbox plumbing

- 196 OPEN in aporia_inbox.jsonl (oldest ~3 weeks)
- 51 OPEN in techne_inbox.jsonl
- 6 OPEN in ergon_inbox (60 BLOCKED-DEFERRED-V1.0)
- 2 OPEN in charon_inbox
- ~22 tickets with `status=?` across queues (schema drift)
- Heterogeneous schema is itself a finding (each agent encodes distinct stagnation modes)

## 3. What is operationally broken (numbered, mostly carried from v0.1)

1. **Pythia dispatch lacks a contract.** Reports are filed without declared consumer or expected delta. Retrospective yield audit alone cannot distinguish "bad report" from "no consumer" from "spec missing."
2. **Inbox conflates queue and ledger.** OPEN means both "work this" and "remember this." 196 OPEN tickets are not all actionable WIP; some are valid substrate residue mislabeled.
3. **Techne 89-fire 0-promoted streak.** Diagnosis ranking (per Q1 review): routing/promotion-interface problem highest prior; promotion-criteria second; generation-rate third.
4. **Catalog audit is overdue** (6-month-old number).
5. **Reasoning-ladder annotation discipline is not implemented.**
6. **Aporia role is not running as machinery.** Stand E says: keep it human-driven for 4 weeks, allow `aporia_triage_report.py` as instrument panel.
7. **Substrate carrying capacity is unmeasured.** v0.1 missed this frame entirely. Stand G is the falsifier.

## 4. Stands (v0.2 revisions)

### Stand A1 — Retrospective Pythia yield audit (calibration data)

**Action:** One pass over the 55 reports IDs 00377-00431 in `aporia/docs/deep_research_reports/2026-05-{26..30}/`. Output: `aporia/meta/pythia_yield_audit_2026-05-30.jsonl`, one row per report. Schema (per review):

```
report_id              : "00377"
date                   : "2026-05-26"
report_class           : "literature_survey" | "false_anchor_hunt" |
                         "coordinate_collision" | "critique" |
                         "proof_decomposition" | "other"
inferred_consumer      : "stygian" | "lethe" | ... | "doctrine" | "human" | "none"
actual_consumer        : same vocabulary, or null until audited
expected_delta_inferred: free text from title/header
actual_delta           : "doctrine_commit" | "kill_ledger_entry" |
                         "anchor_demotion" | "ticket_resolution" |
                         "generator_change" | "none" | "unknown"
reason_for_no_delta    : free text or null
audited_at             : ISO timestamp or null
audited_by             : "aporia-in-session" | null
```

**Behaviour delta:** Yield-per-token ratio. Per review thresholds:
- <10%: emergency (decorative dispatch)
- 10-25%: weak (only acceptable for frontier exploration)
- 25-50%: tolerable if reports are cheap and diverse
- \>50%: healthy

**Falsifiable:** If <10%, Pythia query construction is decorative; the DR token budget rotates to a different consumption pattern.

**Deletion candidate (per Stand F):** If the audit finds 90%+ of reports trace to Moros cross-pollination critiques and Moros critiques have <10% actual delta, propose retiring Moros's auto-dispatch cadence.

### Stand A2 — Forward Pythia dispatch contract (load-bearing piece)

**Action:** Every NEW DR query dispatched from 2026-05-31 onward MUST declare, before dispatch, the following fields:

```
query_id            : ULID or timestamp+nonce
query_text          : the actual DR prompt sent
dispatched_at       : ISO timestamp
dispatched_by       : agent name
intended_consumer   : exactly one of {stygian, lethe, acheron, moros,
                      hecate, pollux, erebos, ergon, techne, hypatia,
                      doctrine, human}
expected_behavior_delta: free text describing what observation =
                      success
expiry_condition    : "after_N_days: N=14" | "after_event: <event_id>"
success_evidence    : what artifact / observation confirms the delta
failure_evidence    : what artifact / observation confirms no-delta
```

Storage: `aporia/meta/pythia_dispatch_log.jsonl`, append-only, one row per dispatch. The contract is mandatory at dispatch time; Pythia refuses to send queries without all required fields.

**Behaviour delta:** Forward attribution. Every future report has a pre-registered consumer and success criterion. Retrospective audits (A1-style) become structurally cheaper.

**Falsifiable:** If after 30 days of contract operation the actual-delta column still shows <10% match to expected_behavior_delta, contract discipline is not the bottleneck — either Pythia query construction OR consumer absorption is. Either way the result is informative.

**Deletion candidate:** If after 60 days the contract has been violated more than honored (>50% of dispatches missing required fields), the contract discipline is too heavy for the actual dispatch cadence; retire the mandatory fields and replace with a sampled-audit pattern.

### Stand B — Inbox queue/ledger split

**Action:** Replace OPEN with the following status vocabulary in `aporia/meta/queue/*_inbox.jsonl`:

```
ACTIVE_QUEUE        : bounded actionable WIP, expected to close within
                      14 days; cap per-queue (proposed: 20)
CHARTER             : promoted to an agent's charter / mission file;
                      ticket archived but not "closed"
DOCTRINE_CANDIDATE  : ticket has reached "this should be doctrine"
                      maturity; pending doctrine commit
PARKED_SIGNAL       : valid substrate residue worth remembering but no
                      actionable owner; ledger mode
WONTFIX             : decided not worth doing
SUPERSEDED          : replaced by a later ticket or pivot
```

**Behaviour delta:** Once a week, every OPEN ticket older than 14 days gets converted to one of the six above. Inbox depth in ACTIVE_QUEUE is bounded; PARKED_SIGNAL grows freely.

**The conceptual fix (per review):** "The current problem is not that old tickets exist. The problem is that OPEN means both 'work this' and 'remember this.'" PARKED_SIGNAL is the load-bearing addition — it gives the ledger semantics a name.

**Falsifiable:** If after 3 weekly passes ACTIVE_QUEUE grows beyond cap consistently, the substrate is producing actionable tickets faster than the role can adjudicate; that's a Pythia-equivalent over-production signal at the meta layer.

**Deletion candidate:** If after 6 weeks PARKED_SIGNAL contains >300 entries and zero of them have been promoted back to ACTIVE_QUEUE or DOCTRINE_CANDIDATE, the ledger is decorative; PARKED_SIGNAL becomes an alias for WONTFIX-archive.

### Stand C — Reasoning-ladder annotation on NEW tickets only + sample test + consumer-read test

**Action:**
1. From 2026-06-01, every NEW ticket landing in `aporia/meta/queue/*_inbox.jsonl` MUST carry `required_reasoning_tier` (R0-R12) AND `failure_axis` (F0-F8).
2. **Sample backfill test (per review):** Backfill exactly 20 randomly-selected OLD tickets with tier + axis labels. Use the sample to test inter-rater stability and downstream consumer readability. Do NOT backfill the queue.
3. **Consumer-read test:** Within 4 weeks, at least one agent's pull-decision logic must change based on the tier/axis fields (e.g., Techne pulls higher-tier tickets first; Erebos prioritizes high-F-axis voids). If no consumer reads the fields, the annotation discipline is taxonomy theater.

**Behaviour delta:** A measurable consumer-read rate. The 20-ticket sample produces an inter-rater-reliability number. New-ticket annotation rate produces a discipline-adherence number.

**Falsifiable:** If at week 6, (a) the inter-rater agreement on the 20-sample is <50%, OR (b) no agent has changed any pull decision based on the new fields, the annotation discipline is decorative and gets retired entirely. Position (c) from review Q5 — drop the ladder annotation — is the live falsifier.

**Deletion candidate:** The annotation discipline itself, if either falsifier fires.

### Stand D — Per-domain catalog audit, one domain per week (unchanged from v0.1)

Order: `mathematics/` first (highest substrate-coupling), then `physics/`, then descending. Each domain audit produces a fresh count + staleness distribution + demote/retain/promote disposition per problem.

**Deletion candidate:** Domains where >40% of problems demote in one audit pass get a "catalog deletion review" — propose merging or archiving the whole domain directory if its problem density falls below 5 active.

### Stand E — Defer Aporia-as-daemon for 4 weeks, BUT allow one instrument-panel automation

**Action:**
- Aporia-as-daemon stays deferred until Stands A1+A2+B+C+D have run at least once.
- **Allowed immediately:** `scripts/aporia_triage_report.py`. Runs weekly. Does NOT decide. Surfaces:
  - OPEN tickets older than 14 days (per Stand B)
  - tickets missing `required_reasoning_tier` / `failure_axis` (per Stand C, scoped to post-2026-06-01)
  - tickets with no inferable consumer
  - Pythia reports with no declared delta (per Stand A2, scoped to post-2026-05-31)
  - repeated unresolved failure axes
- Output: `aporia/meta/triage_report_<date>.md`. Human reads it Friday morning; decisions stay human.

**Behaviour delta:** No new agent. One Friday-morning script. The instrument-panel automation is the falsification surface that distinguishes "human cadence is workable" from "human cadence is unsustainable."

**Falsifiable:** If after 4 weeks the human-driven Friday cadence has been skipped 2+ times even with the triage_report.py panel surfacing the signals, the role is under-served by human-only operation and partial automation (NOT a full daemon) is the right next step.

**Deletion candidate:** `aporia_triage_report.py` itself, if its output is never read for 3 consecutive weeks.

### NEW Stand F — Every stand emits a deletion candidate

**Doctrine claim:** A mature substrate retires machinery, not only adds doctrine. Every stand in this doc carries a `Deletion candidate` line (above). Every FUTURE stand added to Aporia's stands list must do the same.

**Behaviour delta:** A culture norm. Mechanically enforced by review during stand promotion to doctrine.

**Falsifiable:** If after 90 days the substrate has added 5+ stands but retired 0 machinery, Stand F is decorative; either the deletion candidates are too soft to fire or the doctrine is reluctance-biased toward additions.

**Deletion candidate (for F itself):** If F fires no actual deletions over 90 days but stands keep being added, F is retired and replaced with a quarterly "what should we kill?" doctrine-review pass.

### NEW Stand G — Carrying-capacity throttle experiment

**Action:** For one week (proposed: 2026-06-08 → 2026-06-14):
- Cap new Pythia dispatches at 5/day (down from current ~15)
- Cap new aporia_inbox tickets at 10 for the week (vs. current ~50)
- Cap new pivot/ docs at 2 for the week (vs. current 5+)
- Process backlog only; no new architectural buildout

Measure during the week and 1 week post:
- Discovery rate (Techne promotions)
- Behaviour-delta rate (commits that change agent behaviour, not just generate)
- Doctrine commits
- Inbox triage rate (Stand B status transitions)

**Behaviour delta:** A causal signal on whether the substrate is overloaded or whether it depends on high-throughput turbulence. Per review Q7: "If output quality rises under intake throttling, the ecosystem is overloaded. If it falls, the substrate depends on high-throughput turbulence."

**Falsifiable (both ways):**
- If quality rises during the throttle: the substrate IS overloaded; intake caps should become permanent
- If quality falls during the throttle: the substrate depends on turbulence; throttling discipline is wrong; remove caps and accept the unmeasured-throughput cost

**Deletion candidate:** If quality rises but the team won't accept the cap as permanent (engineering-culture rejection), the throttle experiment itself is retired and replaced with a softer measurement (e.g., audit-while-running rather than cap-and-measure).

## 5. Order of execution (softened from v0.1)

Parallelism is now allowed where stands operate on disjoint timestamps:

```
Day 0 (2026-05-30, today)
  - File this v0.2 doc                                                [done]
  - Write aporia/meta/pythia_dispatch_contract_schema.md              [today]
  - Write aporia/meta/pythia_yield_audit_2026-05-30.jsonl skeleton    [today]

Day 1-2 (2026-05-31 onward)
  - Stand A2 contract goes live (mandatory at dispatch)
  - Stand C schema goes live for NEW tickets
  - Stand A1 retrospective audit runs (human-driven session)

Day 3-7
  - First Stand B inbox triage pass
  - First Stand D catalog audit (mathematics/)
  - aporia_triage_report.py written + first Friday run

Day 8-14
  - Stand G carrying-capacity throttle experiment (one week)

Day 15-28
  - Second iteration of B/D/E
  - First measurement of A2 contract data
  - Stand C consumer-read test deadline

Day 28+
  - If A1+A2+B+C+D have all produced their first measurement,
    promote surviving stands to aporia/doctrine/aporia_ecosystem_doctrine.md
```

## 6. What this section explicitly is NOT proposing (unchanged from v0.1)

- No new agent
- No new doctrine doc beyond this v0.2 and the dispatch contract schema
- No replacement of the inbox schema with a new framework (split semantics, don't replace)
- No retroactive tier-annotation of 196 old aporia_inbox tickets (20-sample only)
- No promotion of any in-flight pivot doc to doctrine until A2+B+C have produced one cycle of data

## 7. Posture (v0.2)

v0.2 is filed at `pivot/` per the discipline that doctrine promotion requires data from one full cycle. After A2 + B + C produce their first measurement (estimated Day 28, ~2026-06-27), the surviving Stand-section gets promoted to `aporia/doctrine/aporia_ecosystem_doctrine.md` and the dispatch contract becomes `aporia/doctrine/dr_dispatch_contract.md`.

The 6-week behaviour-delta deadline from v0.1 stands: if by 2026-07-11 the audit hasn't run, the contract isn't live, or the triage cadence has been skipped, the doc was wrong and gets retired.

— Aporia, 2026-05-30 (v0.2)
