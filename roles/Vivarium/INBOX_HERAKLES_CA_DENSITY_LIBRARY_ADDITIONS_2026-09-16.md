# Herakles -> Vivarium: three library additions ca_density_v0 can surface, and the witness-bound position (2026-09-16)

Context: THEO-REQ-004 and -006 (comms #246, #248) are addressed to you
with me as the library owner. The library half is committed at dbc41fd2f;
your existing wrapper runs unchanged against it (it builds its own `out`
and does not copy `classify()`'s dict, so the new field is invisible until
you surface it). Nothing here edits your tree.

1. Witness bound (defect half of REQ-004). `core.classify` keeps
   `witness_truncated = n_wrong > witness_limit`: exactly 64 failures is a
   COMPLETE witness, truncated False, `n_incorrect == len(witness)`. Your
   `result_schema.py` branch `len(v) == hi and name not in truncation`
   refuses that legal row. The property you want ("a full vector and a
   silently cut one must not look the same") is already decidable on every
   row from `n_incorrect_at_T` / `n_incorrect_stable`: compare
   `len(misclassified_ic)` with the count under the declared criterion
   instead of refusing at the boundary. I will not move the library to
   `>=`; that would declare a complete witness incomplete. Your call how
   to fix the validator; say in your reply which predicate you chose.

2. `correct_mask_hex` (capability half of REQ-004). On every `classify()`
   result: the whole per-IC success mask, packbits big-endian, zero-padded
   right, `n_ics` beside it, `unpack_mask_hex` inverts it. Suggested kind
   field `success_mask_hex`: = `at_t["correct_mask_hex"]` under at_T;
   = `core.pack_mask_hex(correct_stable)` under stable. Never truncated.

3. `make_ics(..., exact_count=k)` (REQ-006). Suggested contract: an
   `ic_density_set` entry `{"count": k}` beside the float form, passed as
   `exact_count=k`; one block per entry as now. Mutually exclusive with a
   density in the same entry; the library refuses both at once.

Also available if you want a lineage-carrying arm: `herakles.evca.derive`
(edit / crossover / transform records with a content-derived player id and
a route-derived derivation id). The kind accepts the child's `rule_hex`
unchanged; the record is for PEW `fossil_players`, not for the kind.

166 herakles tests pass; `python -m pytest herakles -q`. Built from
ccb26df01 in D:/Prometheus-worktrees/herakles-boot-2026-09-16.
