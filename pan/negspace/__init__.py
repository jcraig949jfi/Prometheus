"""PAN-43: negative-space evaluation (operator Sagacity Foundation directive s3; protocol in
roles/Pan/docs/sagacity/NEGATIVE_SPACE_EVALUATION.md; frozen rules in pan/tests/negspace_prereg.json).

  domain.py       the executable domain: a delay-recall contract, mechanisms as small Python classes, a frozen
                  intervention suite (input streams + environment wipes), a sandboxed subprocess runner with coverage
  calibration.py  known-answer pairs: EQUIVALENT under representation change, DISTINCT though similar, novelty
                  CHEATs, and genuinely UNRESOLVED pairs
  evaluators.py   cheap baselines (text, AST-normalized, embedding, constants) and the behavioral evaluator
                  (differential testing with a coverage gate that answers UNKNOWN when its evidence is incomplete)
  harness.py      the A-D generation arms (+ counterfeit-exclusion control) at matched budgets, smallest functional form
"""
