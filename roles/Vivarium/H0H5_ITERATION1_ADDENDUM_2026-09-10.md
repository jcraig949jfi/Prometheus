# Addendum to the iteration-1 receipt — what changed underneath it

**Vivarium, 2026-09-10.** The receipt of 2026-09-09 is unamended; this records
what moved after it, in the same file tree, so the status file's three carried
limitations can be corrected against evidence rather than memory.

## The slice was merged onto a moved main and re-verified

`origin/main` had advanced by ~20 commits, including Daedalus's
`ef05397f2 H0-H5 iteration 1: authorized artifact resolution, cost events on
the existing mechanism, schema v8`. Merged clean (no conflicts) at `e0d30e38d`.

The dev engine was rebuilt from the merged tree — **schema_version 8**,
instance `eng_9be475ef477301443b3ac76f`, source commit `e0d30e38d` — and the
entire suite re-run against it. **364 passed, 1 skipped, unchanged.** The
loader needed no modification to work on v8; `consume_budget` still enforces,
and every boundary case still refuses for the same reason it refused on v7.

## Two of the three carried limitations are now FALSE

* **`sfclient` cannot pass `expected_blob_hash`** — CLOSED. It now can, and
  `artifact_content` additionally takes `expected_digest`, `expected_bytes` and
  `max_bytes`, checked engine-side **after** authorization, so a caller who
  knows only a hash still gets 404. That is strictly better than my local
  post-download check and I should adopt it (see below).
* **Engine-side cost events are absent (Daedalus C4-3)** — CLOSED. v8 has
  `reserve_budget(stage=, attempt_id=)`, `cost_event(...)`, `get_cost_event`
  and `cost-report`, with reservations settled exactly once and no caller-
  declared enforcement field.
* **`register()` discards the engine-issued `client_id`** — STILL OPEN.
  Unchanged at `sfclient/client.py:98`. My load receipt therefore still records
  `principal.engine_issued: false`.

## What I changed today, and why it was not optional

The status file says producer and executor receipts "cannot reconcile yet". The
blocker named was C4-3. It was not the only one: **my vector could not have
reconciled with Archaeon's even after C4-3 landed**, because it carried no
`attempt_id` at all, and `archaeon/producer/costs.py::reconcile` matches on
`v.get("attempt_id")`. Three smaller mismatches sat behind it — my field was
`enforcement`, theirs `enforcement_class`; my byte unit was `"B"`, theirs
`"bytes"`; I had no `stage`.

I adopted their vocabulary rather than proposing mine. One seat changing a
private field beats two seats disagreeing permanently, and their names were
already published and already consumed by committed code.

Four tests now assert this against **their actual module**, imported from the
repo rather than reimplemented — a reconciliation test written against my own
idea of the counterpart's shape proves that my idea is self-consistent and
nothing else.

    test_the_executor_vector_reconciles_with_a_producer_receipt
    test_a_refused_attempt_still_carries_the_reconciliation_key
    test_the_retrieval_stage_is_a_subset_and_says_so
    test_the_two_seats_agree_on_units_and_the_enforcement_field

## Not done, deliberately

The engine's reservation/cost-event path is **not wired in**. The loader still
debits with `consume_budget`, and `artifact_content` is still called without
the engine-side `expected_digest` / `expected_bytes` gates. Both are
improvements and neither is this order: the next permitted action is
`cegis_boolean_v1`, and re-plumbing the accounting underneath a slice that was
just accepted would put an unreviewed change under a recorded gate.

They are the obvious first item after it, and they are small:

* `reserve_budget(stage="retrieval", attempt_id=...)` before the fetch,
  settled by `cost_event(...)` after — a real reservation instead of a debit,
  and the engine then holds the same `(attempt_id, stage)` key the other two
  seats already agree on, closing the three-way reconciliation.
* `artifact_content(expected_digest=..., expected_bytes=...)` so the engine
  refuses before sending bytes, with my local verification kept as the
  defence-in-depth it now is rather than the guarantee it currently is.
