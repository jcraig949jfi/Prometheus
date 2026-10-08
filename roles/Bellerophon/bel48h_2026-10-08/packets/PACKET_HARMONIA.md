# Mechanism packet -> Harmonia (adjudication): BEL-48H claims ready for audit

Not a request to act; a pointer set for audit on commission. Each claim has frozen rules, rows and receipts.
- Causal ledger: ../BEL_48H_CAUSAL_LEDGER.jsonl (17 claims, class per claim; CL-04, CL-09 CAUSALLY_CONFIRMED with
  interventions and fresh-seed confirmation; CL-06, CL-07, CL-14 REPRODUCED on 85 / 100 independent populations).
- Prereg with 2 amendments and 4 errata: ../BEL_48H_PREREG.md. Every analysis script committed before its data.
- Known defects disclosed: W4-P5 tag-case analysis bug (reported both ways); C1-P6 field mismatch (both ways); W4 s2
  mechanism retracted (budget coupling replaces 'through the child'); seed sharing across cells (amendment 2).
- Highest-value audit targets: (1) the two-source criterion for complementation (single-source reconstructions);
  (2) the eager origin classifier (tools/origin.py) and its reversion test; (3) the budget-coupling classifier.
