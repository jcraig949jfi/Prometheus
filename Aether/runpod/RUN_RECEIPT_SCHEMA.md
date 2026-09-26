# Run receipt schema

`prometheus-gpu/run-receipt/1`

Authority: `prometheus_gpu/receipt.py`. Enforced by
`Aether/test/test_prometheus_gpu.py`. Checked by:

```bash
python -m prometheus_gpu.cli validate-receipt receipt.json
```

A receipt is not a log. It is the record a later reader trusts when
nobody is left who remembers the run. Its job is to keep apart the
things that are easy to conflate and expensive to conflate wrongly.

## The four cleanup claims

This is the part worth reading twice. These four are **not**
interchangeable, and the difference between them is money.

| claim | means | does NOT mean |
|:--|:--|:--|
| `terminate_acknowledged` | the provider accepted a terminate request | the pod stopped |
| `observed_absent` | the pod is not in an inventory listing | the pod is not billing |
| `operational_cleanup` | nothing we know of is still running | the bill is settled |
| `billing_reconciled` | **provider billing data was obtained** | anything we computed ourselves |

The ladder is enforced in `cleanup_block()`, not left to the caller's
discipline. A caller cannot assert a claim; it supplies per-pod evidence
and the claims are derived from it.

**A failed inventory read cannot testify to absence.** A LIST that
errored, or that was filtered, omits every pod — exactly like a LIST of
a genuinely empty account. So `observed_absent` is forced false whenever
`inventory_read_ok` is false, and the block carries a note saying
reconciliation must happen before any further create.

**Absence alone cannot report clean.** `operational_cleanup` requires
*both* an acknowledged terminate and an observed absence, for every pod.
Absence alone is a listing's opinion; an acknowledgement alone is a
promise about the future.

**Reconciliation requires evidence.** `billing_reconciled: true` is
refused unless `billing_evidence` is present with `source`,
`retrieved_utc` and `amount_usd`. Wall-clock time multiplied by a quoted
hourly rate is an *estimate*. Calling that reconciliation is the specific
false claim this module exists to prevent, so `cost.actual()` always
emits `billing_reconciled: false` and `validate()` refuses a receipt
that flips it true anywhere.

## Per-pod fields

```json
{"id": "ns96dzh9bq7ynx",
 "creation_outcome": "confirmed",
 "created_utc": "2026-09-24T07:04:08Z",
 "terminate_acknowledged": true,
 "observed_absent": true}
```

`creation_outcome` is a three-value field because the middle value is
real and gets lost otherwise:

| value | meaning |
|:--|:--|
| `confirmed` | the create call returned an id |
| `adopted` | the create outcome was **ambiguous**, and the pod was found by reconciling inventory rather than by a second create |
| `unknown` | the create outcome was ambiguous **and** reconciliation also failed |

An `adopted` pod must not be recorded as `confirmed`. A later reader
needs to see that the run was one blind retry away from a double bill;
flattening it to "confirmed" erases the near miss. An `unknown` outcome
blocks `operational_cleanup` outright.

## Result

| value | meaning |
|:--|:--|
| `OK` | ran to completion and reported success |
| `PARTIAL` | produced usable output but did not finish the plan |
| `FAILED` | ran and failed |
| `TIMEOUT` | hit `max_runtime_s` |
| `ABORTED` | the controller stopped it (budget, guardrail, operator) |
| `NOT_RUN` | never launched; a dry run's skeleton stays here |
| `UNKNOWN` | launched, and we genuinely cannot say |

`UNKNOWN` is not a polite synonym for `FAILED`. A pod whose outcome
cannot be determined is a different operational situation from one that
crashed: it may still be running, and it demands reconciliation rather
than a post-mortem. A vocabulary that cannot say "unknown" will round it
to the nearest familiar word and lose the distinction that mattered.

## Full shape

| field | notes |
|:--|:--|
| `schema` | `prometheus-gpu/run-receipt/1` |
| `run_id`, `seat`, `module` | identity; `module` is `name@version` |
| `entrypoint`, `args` | what was executed |
| `bundle_sha256` | **required once the run happened.** Without it the bytes that ran cannot be identified later. |
| `spec_sha256`, `git` | provenance from the bundle manifest |
| `transport` | how the module reached the pod |
| `guardrails` | `max_runtime_s`, `disk_gb`, telemetry interval |
| `plan_cost_projection` | what the dry run predicted, kept for calibration against the actual |
| `created_utc`, `started_utc`, `ended_utc` | three distinct moments |
| `result` | from the table above |
| `pods` | list of per-pod records |
| `cleanup` | the four claims, derived |
| `cost` | from `cost.actual()`; always an estimate |
| `artifacts`, `artifacts_missing` | retrieved, and declared-but-absent |
| `telemetry_summary` | from `telemetry.summarise()` |
| `notes` | free text |

## Measurement blocks (Iteration 2)

Informational; `validate()` does not require them, so older receipts still
load.

| field | what it holds |
|:--|:--|
| `lifecycle.pod_clock` | intervals between the pod's own stage markers |
| `lifecycle.controller_clock` | intervals between controller instants, incl. `accepted_to_first_contact_s` (pod reachable through the proxy) |
| `lifecycle.cross_clock` | the raw pod-minus-controller subtraction, labelled as such |
| `lifecycle.synchronised` | the same intervals corrected by a MEASURED clock offset, with `uncertainty_s`; absent if `/_clock` was unreadable |
| `clock_sync.start` / `.end` | offset, uncertainty, min RTT and sample count, measured at first contact and again at retrieval |
| `ready_poll_s` | the controller's poll interval during the ready wait |
| `platform_summary` | peaks and means of `platform.jsonl`: GPU memory/util/temp/power, host load and RAM (the host's, not the process's), disk, artifact bytes, and the sampler's own cost per sample |
| `artifact_transfer` | total bytes, fetch seconds, rate, and the largest artifact with its own rate |
| `artifacts[].fetch_s` | per-artifact fetch time |

## The receipt begins as the plan

`receipt.from_plan(plan)` builds the skeleton from the dry-run plan, so
what was validated is what is reported. Nothing is re-derived by hand
after the fact, which is how a receipt drifts from the run it describes.

## Validation reads other people's receipts too

`validate()` is written to be run against a receipt produced by anyone —
another seat, an older version of this platform, a future version of us
that got it wrong. It refuses a forged `operational_cleanup`, an
`observed_absent` without a successful listing, a `billing_reconciled`
without evidence, a reconciliation claim smuggled into the `cost` block,
an unrecognised result or creation outcome, and a completed run with no
bundle hash.

## Reproducing a run from its receipt

Take `git.commit`, check it out, rebuild the bundle, compare
`bundle_sha256`. Bundling is deterministic, so an identical hash means
identical bytes ran. If the receipt records the module as git-dirty, the
commit is not sufficient and the bundle hash is the only identity there
is.
