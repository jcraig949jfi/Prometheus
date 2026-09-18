# Campaign 3 improvement ledger -- schema

LEDGER.jsonl: one JSON object per line, append-only. Entries are EMITTED by
archaeon/campaign2/accounting.py (shared) from receipts and typed states
(auto: true) or written by Archaeon (auto: false). Ids are L3-###. Fields
as campaign 2's LEDGER_SCHEMA.md (category, severity, auto, symptom,
evidence, workaround, proposed_fix, proposed_telemetry, blocks_future_runs,
safe_to_defer, recurrence, recurred_in, mitigation_helped, links,
recorded_at) with two campaign-3 categories added:

  REPLACEMENT   a planned slot replaced before execution (rules, section 15)
  RETIRED       a line reopened by mistake (must be 0) or explicitly retired
