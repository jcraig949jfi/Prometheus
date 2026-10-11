# Live demo against C-016 (tree = origin/main state 5bc5d84b0 for ops/campaigns/C-016)

$ queue
C-016-T011       0 min  C-016  2026-10-11T10:13:55Z  by Eupalamus[harry1-33a3708a]  sha 239a0de6d395  notified=False

$ scan (first)
posted [('C-016-T011@239a0de6d39592fb9d75a865b0d45a311a38a8e4', 2116)] already [] dispositions []

$ scan (retry)
posted [] already ['C-016-T011@239a0de6d39592fb9d75a865b0d45a311a38a8e4'] dispositions []

$ two scanners at once
posted [] already ['C-016-T011@239a0de6d39592fb9d75a865b0d45a311a38a8e4'] dispositions []
posted [] already ['C-016-T011@239a0de6d39592fb9d75a865b0d45a311a38a8e4'] dispositions []

$ queue
C-016-T011       0 min  C-016  2026-10-11T10:13:55Z  by Eupalamus[harry1-33a3708a]  sha 239a0de6d395  notified=True

Result: comms id 2116 (sender Eupalamus -> Palamedes, task_ref C-016-T011) is the single notice; retry and two
concurrent scanners posted nothing. Honest limit: the concurrent pair ran AFTER the notice existed, so it shows
dedupe across scanners, not a won first-post race; the advisory lock around find+post is by construction, not
race-tested. Disposition path is covered by unit tests (MemSink) and fires on the next scan after Palamedes
INTEGRATED/sends back C-016-T011. Proposal to Achilles: comms 2115.
