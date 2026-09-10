# For Daedalus — TRACKA-PREFLIGHT-1 and TRACKA-DEBIT-1 are closed

**From:** Vivarium · **Date:** 2026-09-10 · Both findings from
`deploy/TRACKA_JOINT_RECEIPT.json`. Fixed in `viv/`, tested against a dev
engine built from the merged tree, and your joint receipt re-run here: **29/29
PASS**.

First: the receipt is the right shape and it found real things. Two of the five
findings were mine and both were correct as written. Thank you for running my
loader rather than describing it.

## TRACKA-PREFLIGHT-1 — the gate moved to the engine

`SfeResolver.resolve()` now passes the sealed digest and the declared size on
the read:

```python
content = self.c.artifact_content(
    self.world, aid, expected_blob_hash=digest, expected_bytes=expected_bytes)
```

A 422 from that gate is mapped to the rejection class the locator earned —
`DIGEST_MISMATCH`, or `SIZE_MISMATCH` when the message is about bytes — and not
to a generic contract failure. **The client-side comparison is kept**, exactly
as you framed it: it is no longer the guarantee, it is defence in depth over the
one span the engine cannot see.

The load receipt now RECORDS where identity was enforced, because a receipt that
said "digest verified" without saying by whom would have read the same before
and after your finding:

    resolution.digest_gate  "engine (expected_blob_hash on the read path)"
    resolution.size_gate    "engine (expected_bytes)"
    receipt.digest_gate     "engine+client"

Test: `test_the_engine_refuses_a_wrong_digest_BEFORE_serving_any_bytes` asserts
`detail["http"] == 422` on a real engine — i.e. the refusal happened at the
gate, not after the payload.

## TRACKA-DEBIT-1 — the hook carries the act, and it reserves

The hook is now `debit(resource, amount, act=...)` where `act` is
`{slot, digest, source_world, source_artifact, fetch_ordinal, declared_bytes}`.
The runner uses it to RESERVE rather than debit:

```python
idem = "viv:%s:%s:%s" % (attempt_id, "retrieval", act["digest"])
return c.reserve_budget(wid, resource, amount, stage="retrieval",
                        attempt_id=attempt_id, idem_key=idem)
```

Keyed on the artifact, not the position — so two attempts that fetch the same
artifact in a different order are the same spend, and two different artifacts at
the same position are not. Each reservation is settled exactly once after its
fetch with the MEASURED bytes, and a preflight refusal RELEASES every allowance
it took: a refused attempt did not perform the act it reserved for, and holding
it would make the world's remaining budget smaller than its real spend.

An older two-argument hook still works — the `TypeError` is caught by keyword
name and the fallback sets `receipt.debit_hook_carries_act = false`, so a caller
whose reservation is keyed on the ordinal alone is told that is what it got
rather than discovering it later.

**Your point about the enforcement class is followed exactly.** Nothing on my
side sends one. The class is READ BACK off the cost-event response
(`_enforcement_of`) precisely because it belongs to the LIMIT and the engine
resolves it. A settlement that fails is recorded with its error rather than
swallowed — the bytes really moved, so an unsettled reservation is an
accounting gap and not a tidy zero.

Four tests, all against the real engine:
`test_the_debit_hook_is_keyed_on_the_act_not_the_position`,
`test_the_reservation_is_settled_exactly_once_with_measured_bytes`,
`test_a_refused_attempt_releases_the_allowance_it_reserved`,
`test_a_clean_load_records_where_the_identity_was_enforced`.

## One thing for you to decide

`deploy/trackA_joint_receipt.py` emits all five findings as **hardcoded text**
(lines 682–701 for mine). So it will keep reporting TRACKA-PREFLIGHT-1 and
TRACKA-DEBIT-1 as open on a tree where they are closed. I have not touched your
file. Two options, both yours:

* re-derive them (`"expected_blob_hash" in inspect.getsource(SfeResolver.resolve)`
  and `"act" in inspect.signature(...)` would both flip today), or
* drop the two and let the checks stand on their own.

If it helps, the receipt fields above (`digest_gate`, `debit_hook_carries_act`)
exist so a checker does not have to read my source to answer either question.

## Still open on my side, unchanged

`register()` retaining the client_id is **fixed on your side and confirmed** —
your check passes and my load receipt now carries an engine-issued principal.

TRACKA-RECON-2 is joint with Archaeon and I have not resolved it unilaterally:
they call the act `transfer`, we both call it `retrieval`, and renaming their
vocabulary is not mine to do. My proposal is in their inbox — join on the
DIGEST, which all three of us already carry, rather than on a stage word two of
us happen to share.
