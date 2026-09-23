+=====================================================================+
|  C5-10 -- HELD-OUT TRIAL: READOUT                                     |
|  Archaeon[m2-49ee5a4d]   2026-09-18 15:07Z   attempt of record a02   |
|  NO_CONDITION_SELECTED (the rule's success)                          |
+=====================================================================+

RULE.md (committed 14:36Z, before C5-04 and C5-05 ran) selects a
condition iff its net won-minus-lost cells against OLD_v04 in C5-09 is
>= +4 with the grammar-only arm below +4. C5-09 a02: OLD_B 0, B_FAIL
+1, B_FIZZLE +1. No condition is selectable. The held-out worlds
(W3_K3d1, W2_K2d4; never used by any slot -- checked against the C5-02
and C5-09 preregistrations in code) and held-out seeds 11-16 were not
run. a01 read the same on C5-09 a01 (INSTRUMENT_INVALID by its control
defect) and is preserved; a02 reads C5-09 a02. The harness's decl
label INCONCLUSIVE ("an arm of the primary comparison has no rows") is
the mechanical reading of a slot that, by rule, ran nothing.

For the final disposition: the directive names NO_CONDITION_SELECTED a
success; combined with C5-06's real recovery and C5-09's NO_GAIN the
campaign closes BOUNDARY_CREATED_NO_DISCOVERY_GAIN (D5-014).
+=====================================================================+
