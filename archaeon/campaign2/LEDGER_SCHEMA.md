# Campaign 2 improvement ledger -- schema

LEDGER.jsonl: one JSON object per line, append-only. Entries are EMITTED by
archaeon/campaign2/accounting.py from receipts and typed states (auto: true)
or written by Archaeon (auto: false). Fields:

  id                  "L2-###"
  experiment          "C2-SFE-NN" or "PHASE-A" (first seen)
  category            BUG | FRICTION | MISSING_TELEMETRY | AUTOMATION |
                      TO_MACHINERY | KEEP_POLICY | MISSING_FAILURE_STATE |
                      MISSING_RECOVERY | PORTABILITY | OBSERVABILITY |
                      LANDSCAPE | ASSAY_STATE (a typed state that fired;
                      informational) | RECOVERY (attempts > 1: resumed or
                      re-created) | MACHINE_FIX (a shared-machine change
                      made during the campaign)
  severity            blocker | major | minor | note
  auto                true if generated from a receipt
  symptom             one sentence
  evidence            paths / commands / numbers
  workaround          what the campaign did instead
  proposed_fix        the deterministic fix
  proposed_telemetry  what to measure so it is visible next time
  blocks_future_runs  true | false
  safe_to_defer       true | false
  recurrence          integer (incremented on each later experiment that
                      hits it; never a new entry for the same defect)
  recurred_in         ["C2-SFE-NN", ...]
  mitigation_helped   null | true | false
  links               ["L-###" (campaign-1 ledger), "D2-###", ...]
  recorded_at         ISO-8601 UTC
