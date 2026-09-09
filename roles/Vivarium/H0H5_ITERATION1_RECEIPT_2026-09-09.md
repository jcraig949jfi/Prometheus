# H0–H5 iteration 1 — the loader vertical slice

**Vivarium, integrating owner. 2026-09-09.** Design v0.1, contracts C1/C3/C5,
brief §"First iteration" B and C. Development schema `viv_dev_h0h5`,
development engine `http://127.0.0.1:8899`, PEW namespace `test`. Production
was not written.

## What now runs

An experiment can consume bytes it did not carry. A producer creates a typed
immutable artifact in an authorized SFE world; a sealed spec names those bytes
by digest; a queue row says where a copy of them lives; preflight resolves them
through the engine's own authorized read, verifies size, digest, codec,
declared type, declared interface and dependency closure against declared
limits, retains the verified bytes and hands the kind a frozen structure and no
client at all; the kind returns a deterministic result validated against its
own declared schema; the whole thing commits through the existing work
lifecycle, publishes through Mnemosyne's idempotent path, and reports
`recorded_in_sfe` and `indexed_in_pew` as the two separate facts they are.

Every boundary case in the order runs as a real execution against a real
engine. Twenty-four of them.

## The receipt

```json
{
  "iteration_id": "vivarium/h0h5-iteration-1/2026-09-09",
  "design_version": "0.1",
  "work_items": ["C1 immutable artifact input and preflight hydration",
                 "C3 kind isolation (no data-service client to the executor)",
                 "C4 resource vector with per-resource enforcement class",
                 "C5 result, load receipt, idempotent publication"],
  "baseline_commits": {
    "vivarium": "e43a6c7f2 (worktree-vivarium-campaign-e1-e6-e16)",
    "sfe_runtime_and_client": "unchanged; no engine-side change was needed",
    "design_packet": "origin/archaeon/v0 roles/Archaeon/prompts/2026-09-08_h0h5",
    "design_sha256": "3b1dbec106cc77cb6885d5bba36a12b40d3aee0677f8b05d46d6887b3b1260b5"
  },
  "result_commits": ["959d35043 -- the loader slice (25 files, 4167 insertions), on worktree-vivarium-campaign-e1-e6-e16",
                     "this line is a FOLLOW-UP commit: a receipt cannot name the commit that contains it, and the first attempt stamped a SHA that an amend then orphaned"],
  "components_changed": [
    "vivarium/viv/artifacts.py       NEW  slot contract, codecs, interfaces, limits, cache",
    "vivarium/viv/preflight.py       NEW  the ten steps, SfeResolver, load receipt",
    "vivarium/viv/resources.py       NEW  resource vector + enforcement classes",
    "vivarium/viv/artifact_probe.py  NEW  the instrument kind's executor",
    "vivarium/migrations/004_artifact_locators.sql NEW  address book + freeze",
    "vivarium/viv/kinds.py           artifact_slots; registers artifact_probe_v1",
    "vivarium/viv/request.py         4th field: artifact_locators",
    "vivarium/viv/queue.py           admission checks for the address book",
    "vivarium/viv/runner.py          world shape, preflight, meter, receipt",
    "vivarium/viv/executors.py       inputs=, refused in both directions",
    "vivarium/viv/pew.py             write_outcome, recorded_in_sfe/indexed_in_pew",
    "vivarium/viv/loop.py            client_id, dev-engine config, failure receipt",
    "vivarium/viv/db.py              VIV_SFE_BASE_URL / _CACERT / _INSECURE",
    "vivarium/viv/identity.py        client_id_for(role)",
    "vivarium/viv/cli.py             `limits`"
  ],
  "commands_run": [
    "python SerendipityFoundry/SerendipityFoundryEngine/serve.py --db <scratch>/dev.sqlite --host 127.0.0.1 --port 8899 --science-profile warn --registration open",
    "python -m pytest tests -q --ignore=tests/test_live_sfe.py --ignore=tests/test_live_pew.py",
    "VIV_DEV_SFE_URL=http://127.0.0.1:8899 python -m pytest tests/test_h0h5_slice.py -q",
    "python -m pytest tests/test_live_sfe.py tests/test_live_pew.py -q",
    "VIV_SCHEMA=viv_dev_h0h5 VIV_PEW_NAMESPACE=test VIV_IDENTITY_ROLE=test python tools/h0h5_receipt_run.py --sfe http://127.0.0.1:8899",
    "python -m viv.cli limits"
  ],
  "tests_and_controls": [
    {"suite": "tests/test_h0h5_artifacts.py", "n": 61, "result": "passed",
     "scope": "contract algebra: exact keys, canonical codec, digest binding, closure, limits, sealed identity, admission, immutability, resource classes"},
    {"suite": "tests/test_h0h5_slice.py", "n": 24, "result": "passed",
     "scope": "REAL engine + REAL Postgres + REAL PEW test namespace; every boundary case"},
    {"suite": "vivarium offline suite (all)", "n": 362, "result": "passed"},
    {"suite": "tests/test_live_sfe.py (PRODUCTION engine regression)",
     "n": 1, "result": "passed", "note": "1 skipped: live PEW module"},
    {"positive_control": "a declared dependency that IS published and addressed resolves, and its rows are consumed (closure_size 2, items_consumed 5)"},
    {"negative_control": "the same dependency unpublished -> MISSING_DEPENDENCY, no observation"},
    {"instrument_control": "artifact_probe_v1 is an INSTRUMENT; `folded` is a checksum-like fold and carries no scientific meaning"}
  ],
  "artifact_and_observation_refs": {
    "producer_world": "wld_2019beb3d1093ca420918eb2",
    "producer_artifact": "sha256:22e9058725dd56f8f7f4bb87214b65a16c89357287eae050400539c5aab2778f",
    "artifact_blob_hash": "sha256:bb2e0ec9ba0d478db904d98180cd11a562e89b504c6070d0dbd449c50ddc60d6",
    "artifact_bytes": 146,
    "queue_experiment_id": "9b26657f-9156-4c46-ac43-b45d5a78c094",
    "spec_hash": "sha256:de0327adfb2caaeb69d207626c509c5075b85a27f8b72605a4a1b32967341582",
    "execution_world": "wld_5fd37921f14985a775029aa4",
    "world_name": "viv-de0327adfb2caaeb",
    "execution_artifact_id": "sha256:f74db21e23b9281937e75d2382836b041f0ed763409909713c53aa28c46b9821",
    "import_seq": 1477,
    "exp_id": "exp_1782656fcb994333dee958d0",
    "work_id": "wrk_1bc531c8536bdcfe69ead25b",
    "obs_id": "obs_5234e6d9b487935feafa25c8",
    "anchor_event": "evt_9457249607fd6bb1949c586c (OBSERVATION_RECORDED, seq 1486)",
    "anchor_entry_hash": "sha256:c3e570278033c8a920a59d4cd779c9d5feebc8958423ad30dbd7e450468193c4",
    "closure_manifest_hash": "sha256:ed5f1a31cc50154e17ca3d633a12190eebb0372d81f415811589508647760b06",
    "pew_reference": "pew:encounter/h0h5-receipt-9500109c6d87:exp_1782656fcb994333dee958d0:wrk_1bc531c8536bdcfe69ead25b",
    "engine": {"instance": "eng_0c5b1e98d9764d93834aaa7f",
               "schema_version": 7,
               "engine_source_hash": "sha256:4d2d4da30a5ed78d0bb322ee35cee88a0cd84a263dc819d501268a4a655e3ab0"}
  },
  "resource_receipt_refs": {
    "carried_in": "the SFE work result AND the queue row's result_summary",
    "artifact_bytes": {"quantity": 146, "enforcement": "enforceable",
                       "note": "debited on the execution world BEFORE the fetch"},
    "wall_seconds": {"enforcement": "enforceable",
                     "note": "checked between repeats; cannot interrupt one"},
    "cpu_seconds": {"enforcement": "measured"},
    "peak_memory_bytes": {"quantity": 33165312, "enforcement": "measured",
                          "scope": "process", "additive": false},
    "gpu_seconds": {"quantity": null, "enforcement": "unavailable",
                    "note": "unavailable is not zero"},
    "engine_side_cost_events": "ABSENT -- Daedalus's C4 deliverable 3 does not exist at this revision; filed"
  },
  "source_set_ref": null,
  "software_stage_changes": [
    {"component": "vivarium artifact loader", "from": "planned", "to": "alpha",
     "gate": "one real bounded execution through the relevant data path, with artifact/cost/result receipts and known controls"}
  ],
  "evidence_state_changes": [
    {"connection_evidence": "runnable",
     "basis": "typed end-to-end execution with endpoint pins and a complete resource receipt",
     "explicitly_not": "demonstrated-transfer -- no controlled held-out effect was measured and none was attempted"}
  ],
  "scientific_outcomes": [
    {"hypothesis": "none", "outcome": "not-run",
     "note": "this iteration produced NO scientific result and was not supposed to. artifact_probe_v1 is an instrument."}
  ],
  "unrun_or_blocked": [
    "cegis_boolean_v1 -- explicitly AFTER iteration 1; Proteus's Boolean library not yet wrapped",
    "engine-side cost events -- Daedalus's lane, absent, filed",
    "sfclient expected_blob_hash and client_id -- Daedalus's lane, filed",
    "the loader has NOT been run on the production engine or the production queue",
    "external process execution -- needs its own named contract; deliberately not smuggled through the in-process wrapper"
  ],
  "design_deviations": [
    "The address book is keyed by DIGEST, not by slot name (C1 sketches a per-slot locator). Reason: a dependency deep in a closure must address the same way a root does, and a digest-keyed book cannot carry a key the sealed spec never mentions.",
    "ExecutionRequest widened from three fields to four. Argued and tested rather than asserted; see below.",
    "The cycle guard is defence in depth, not a live check: a content-addressed cycle is unconstructible. Stated rather than implied."
  ],
  "next_unblocked_action": "Wrap Proteus's bounded Boolean library as cegis_boolean_v1 with the adaptive loop (policy, seeds, caps, ordering, termination) sealed INSIDE the kind, consuming a failure_input_set through this loader; the generic runner stays policy-blind."
}
```

## What it teaches us

**The engine already had the hard half.** The design guessed this — "the missing
work is wiring, complete accounting and qualification, not a second artifact
store or budget engine" — and it was right. F1's world-scoped content read, the
explicit import with its sharing policy and topology-group rules, the
content-identity gate and `_debit_budget`'s commit-then-raise are the entire
authorization and enforcement story. Nothing was added engine-side. The loader
maps the engine's typed refusals onto rejection classes; it never decides
authorization itself.

**Widening a deliberately three-field object was the real decision.** The
argument that it does not reopen the blinding hole is not "we checked that the
executor does not look" — that is a review which must be repeated forever. It is
that preflight verifies every resolved artifact against the digest inside
`spec_hash`, so a locator can only decide *whether* an experiment runs, never
*what* it computes. `test_two_different_locators_over_identical_bytes_execute_identically`
runs that claim.

**Two things I assumed and had to correct.** The obvious `digest -> bytes` cache
is a permission bypass, and no amount of checking around it helps — the cache
had to be keyed by who was authorized. And a content-addressed dependency cycle
turned out to be unconstructible; the test that claimed to build one was
asserting nothing, and now says what is actually true instead.

**A limit that fires after the allocation is a description.** Oversize is
refused on the *declaration*, before a byte crosses the network, and the test
asserts the resolver was never called. The budget is debited before the fetch
for the same reason.

**One measurement nearly went in as `unavailable`.** Peak memory read as
unobtainable on this host until the ctypes signature was declared — an untyped
`GetCurrentProcess` truncates the pseudo-handle and the call fails silently.
`unavailable` is the honest reading of a failed call, which is exactly why it
must not be allowed to stand for a counter that does work.

## What remains uncertain

* **Nothing scientific was measured, and nothing here supports any H0–H5
  hypothesis.** `artifact_probe_v1` is an instrument; `folded` is a fold chosen
  because it changes when any consumed byte changes and for no other reason.
* **This ran on a development engine.** The production path is unchanged and its
  regression test still passes, but the loader has never claimed a production
  row.
* **The resource vector is Vivarium's, not the engine's.** Without cost events
  it cannot be reconciled against a producer's accounting, so campaign-level
  cost claims are not yet supportable.
* **The client principal is not engine-issued.** `sfclient.register()` discards
  the `client_id` the engine sends; the receipt records
  `engine_issued: false` rather than letting a locally invented id read as
  authoritative. Sound today because the cache is per-attempt; load-bearing the
  day a cache spans attempts.
* **`interface_id` is checked, not proved.** The content declares which
  interface it implements and the shape checker agrees; that is a consistency
  check between two declarations plus a structural test, not a semantic proof
  that the bytes mean what the interface says.

## Which consumer this enables

`cegis_boolean_v1`. H1's alpha needs exactly one thing this slice did not have
yesterday: a way for a bounded CEGIS kind to receive a *source failure pack* as
a sealed, verified, immutable input while the generic runner stays blind to what
is in it. `failure_input_set` / `boolean-inputs-v1` is that pack's transport,
ordered because first-witness semantics are defined by case order. H0's four
cells then consume the same transport with the frozen component library, and
"off" means an explicitly absent slot under the kind's declared contract rather
than a hidden alternative.
