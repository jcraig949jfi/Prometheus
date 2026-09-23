+=====================================================================+
|  C5-10 -- HELD-OUT TRIAL: PREREGISTRATION                             |
|  Archaeon[m2-49ee5a4d]   2026-09-18   Status: DRAFT, NO ROW RUN      |
|  Campaign 5, Phase B -- the rule is C5-10/RULE.md (committed earlier) |
+=====================================================================+

This slot has no discretion. It reads C5-09's attempt of record
(REACH.json), applies RULE.md's selection rule verbatim, and either
  - records NO_CONDITION_SELECTED and stops (a success of the rule), or
  - runs the selected condition against OLD_v04 on the two held-out
    worlds (W3_K3d1, W2_K2d4) x held-out seeds 11-16, N=50, G=100,
    E=16 (equal total compute by construction), with the same starting
    subsample rule as C5-09 keyed by the held-out seed, and reads
    REPLICATED / FAILED_TO_REPLICATE by RULE.md's numbers.
CONTROLS: the two held-out worlds were never used by C5-02, C5-09 or any
other slot (checked against the receipts' world lists in code); the
starting best per world is <= the screen receipt's best; determinism of
one cell.
