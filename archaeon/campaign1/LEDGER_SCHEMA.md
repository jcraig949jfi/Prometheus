# Campaign 1 improvement ledger -- schema (directive V)

LEDGER.jsonl: one JSON object per line, append-only. Fields:

  id                  "L-###"
  experiment          "SFE-NN" (first seen)
  category            BUG | FRICTION | MISSING_TELEMETRY | AUTOMATION |
                      TO_MACHINERY (a decision that should become
                      deterministic) | KEEP_POLICY (should remain a
                      scientific/policy decision) | MISSING_FAILURE_STATE |
                      MISSING_RECOVERY | PORTABILITY | OBSERVABILITY |
                      LANDSCAPE (a binary that should be a landscape)
  severity            blocker | major | minor | note
  symptom             one sentence
  evidence            paths / commands / numbers
  workaround          what the campaign did instead
  proposed_fix        the deterministic fix
  proposed_telemetry  what to measure so it is visible next time
  blocks_future_runs  true | false
  safe_to_defer       true | false
  recurrence          integer (incremented on each later experiment that
                      hits it; never a new entry for the same defect)
  recurred_in         ["SFE-NN", ...]
  mitigation_helped   null | true | false
