# Pythia Dispatch Contract — Schema v1

**Filed:** 2026-05-30
**Status:** Live from 2026-05-31. Mandatory at dispatch time.
**Authority:** `pivot/aporia_ecosystem_status_and_next_steps_v0.2_2026-05-30.md` Stand A2.
**Storage:** `aporia/meta/pythia_dispatch_log.jsonl` (append-only)

## Purpose

Every DR query Pythia sends MUST declare its consumer + expected delta + falsification criteria BEFORE dispatch. Retrospective yield audits cannot distinguish "bad report" from "no consumer" from "spec missing" — the dispatch contract makes attribution forward-attributable.

## Required fields (every dispatch)

```
{
  "query_id":              string  (ULID or "<utc-timestamp>-<nonce>"),
  "query_text":            string  (the actual DR prompt sent, full text),
  "dispatched_at":         string  (ISO 8601 UTC),
  "dispatched_by":         string  (agent name: "pythia-in-session" |
                                    "stygian-auto" | "lethe-auto" | ...),
  "intended_consumer":     enum    (see Consumers list below),
  "expected_behavior_delta": string (free text: what observation = success),
  "expiry_condition":      string  ("after_N_days:14" |
                                    "after_event:<event_id>"),
  "success_evidence":      string  (what artifact confirms the delta),
  "failure_evidence":      string  (what artifact confirms NO delta)
}
```

## Optional fields

```
{
  "parent_query_id":       string  (if this is a follow-up dispatch),
  "blocking_other_queries": array  (other query_ids this gates),
  "notes":                 string  (free-text rationale)
}
```

## Consumers (enum values for `intended_consumer`)

Exactly one of:

```
stygian             — battery executor; consumes claims for falsification
lethe               — anchor mining; consumes false-anchor candidates
acheron             — coordinate registry; consumes term collisions
moros               — adversarial critique; consumes substrate artifacts
hecate              — cross-gen MI audit; consumes kill_ledger summaries
pollux              — Spearman survival; consumes cross-database pair data
erebos              — generator cluster; consumes conjecture seeds
ergon               — Learner training; consumes curated corpus inputs
techne              — substrate mining; consumes primitive proposals
hypatia             — proof-decomposition; consumes theorem statements
doctrine            — Aporia doctrine corpus; consumes synthesis/framings
human               — direct James review; consumes high-stakes decisions
none                — explicitly speculative dispatch; no consumer claimed
```

`none` is allowed but flagged: dispatches with `intended_consumer: "none"`
count against a separate budget (proposed: 1/week) so speculative dispatch
cannot crowd out contract-bearing dispatch.

## Expiry condition formats

```
after_N_days:N             N = positive integer
after_event:<event_id>     event_id refers to a substrate artifact
                           (commit hash, ticket id, milestone)
never_expires              reserved for doctrine-foundational queries
                           (use sparingly; rate-limited to 1/month)
```

When an expiry condition fires and `actual_delta` has not been recorded,
the dispatch is automatically marked as `delta=expired_no_consumer` in
the audit log. The dispatch counts as a failed contract.

## Success evidence formats

Free text but should be operationally checkable. Good examples:

- "Stygian battery emits a new kill_ledger entry referencing this query"
- "Hecate registers c1_mut_equal as a confirmed retraction pattern in
   aporia/doctrine/substrate_vocabulary/"
- "Erebos G19 generator gains a new sub-claim decomposition primitive"
- "Doctrine commit lands in aporia/doctrine/ citing report_id"

Bad examples (rejected at validation):

- "The report is useful"             (not operationally checkable)
- "Eventually informs research"      (no checkable artifact)
- "Could lead to a kill"             (subjunctive)

## Failure evidence formats

Same operational-checkability constraint. Examples:

- "After 14 days, no kill_ledger entry references this query_id"
- "Stygian's consume_pythia_report() pulls but returns no_kills_extractable"
- "Moros critique produces no quotes from this report in its weekly digest"

## Validation at dispatch

Pythia's send function refuses dispatch if:

- Any required field is missing or empty
- `intended_consumer` is not in the enum
- `expiry_condition` doesn't match an allowed format
- `success_evidence` or `failure_evidence` is shorter than 20 chars (heuristic
  catch on "yes" / "no" / "ok" placeholders)

Validation failures are logged to `aporia/meta/pythia_dispatch_rejected.jsonl`
with the proposed payload so the dispatcher can fix and retry.

## Audit pass (weekly, Friday)

`scripts/aporia_triage_report.py` walks `pythia_dispatch_log.jsonl` and:

1. For each entry with expiry_condition fired, checks if `actual_delta`
   has been recorded.
2. Emits a Friday digest row per dispatch: query_id | consumer |
   expected_delta | actual_delta_or_expired_no_consumer.
3. Aggregates by `intended_consumer` to produce per-consumer yield ratios.

The Friday digest is human-read; no auto-close happens. The dispatcher
or consumer manually annotates `actual_delta` and `delta_evidence_pointer`
on the dispatch row by appending an UPDATE row with the same query_id.

## Recording actual delta (post-dispatch)

Append a new row to `pythia_dispatch_log.jsonl` with the same `query_id`
and `update: true` flag, providing:

```
{
  "query_id":              same as dispatch,
  "update":                true,
  "updated_at":            ISO 8601 UTC,
  "actual_delta":          enum (see below),
  "delta_evidence_pointer": string  (file path | commit hash | ticket id),
  "notes":                 string
}
```

`actual_delta` enum:

```
doctrine_commit          — landed in aporia/doctrine/
kill_ledger_entry        — Stygian or other emitted a kill citing the report
anchor_demotion          — an anchor was demoted citing the report
ticket_resolution        — an inbox ticket closed citing the report
generator_change         — Techne/Erebos generator updated citing the report
charter_update           — agent CHARTER.md changed citing the report
none                     — read by humans, no substrate artifact changed
expired_no_consumer      — expiry fired, no delta recorded (auto-marked)
unknown                  — audited but evidence inconclusive
```

The audit log stays append-only. Latest UPDATE row wins per query_id
when computing yield statistics.

## Deletion / retirement clause

If after 60 days the contract has been violated more than honored
(>50% of dispatches missing required fields or recording
`actual_delta=expired_no_consumer`), the contract discipline is too
heavy for the actual dispatch cadence. Retire the mandatory fields
and replace with a sampled-audit pattern.

This deletion candidate is mandatory per `Stand F` of the v0.2 doc.

---

**Schema version:** 1
**Next revision trigger:** after 30 days of operation, or after first
deletion-clause check at day 60.
