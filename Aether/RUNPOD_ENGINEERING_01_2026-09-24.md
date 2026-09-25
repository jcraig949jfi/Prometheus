# RunPod Engineering Ladder — Iterations 0 and 1

Date: 2026-09-24
Campaign ceiling: $5.00. **Spent: $0.124.**
Iteration 1 ceiling: $0.30 per attempt. Highest single attempt: $0.044.

Iteration 1 **PASSED** on its sixth attempt, and the five that failed are
the reason this document is worth reading. Every one of them found
something the fake provider could not have, and every one is now covered
by a fake-provider test.

---

## 1. WHAT WAS FLOWN

`iteration1_flight.py --go` drives `prometheus_gpu.launch.Controller`
against the real provider, carrying `examples/hello_gpu` — a two-file
module that declares `cupy` and `numpy`, runs 200 GPU steps, and writes
one result file plus its telemetry.

The full generic path, in order, all of it exercised:

module spec → deterministic package → immutable bundle hash → dry run →
retrievability check → safe create (with reconciliation) → bootstrap →
dependency install → canary → credential scrub → module execution →
telemetry → artifact retrieval → termination → independent absence
confirmation → canonical receipt.

Passing receipt: `Aether/runpod/receipts/hello-gpu-20260924T212427Z.json`.

| | |
|:--|:--|
| result | `OK` |
| GPU used | NVIDIA GeForce RTX 4090 (third choice) |
| artifacts | 2 of 2 retrieved, 1,164 bytes |
| telemetry | 6 records, `units=200`, module reported `ok` |
| module exit code | 0, recorded as a pod stage |
| cleanup | terminate acknowledged, absence observed, operational |
| billing reconciled | **no** |
| cost | $0.0032 estimated over 33.8 s |
| independent recheck | inventory read after the run: `active: 0` |

---

## 2. PREDICTED VERSUS OBSERVED

The cost model before Iteration 1 predicted **78 s** of fixed overhead,
of which 60 s was explicitly marked *inferred* rather than measured.

| interval | predicted | observed | clock |
|:--|--:|--:|:--|
| create call (accept) | 1.0 s | **1.745 s** | controller |
| provision | 20.0 s | **≤ 24 s** (see below) | cross-clock |
| bootstrap: fetch + verify + unpack + install | 40.0 s | **6.0 s** | pod |
| canary | 12.0 s | **1.0 s** | pod |
| teardown: terminate → absence | 5.0 s | **2.2 s** | controller |
| **total fixed overhead** | **78.0 s** | **≈ 35 s** | |
| total wall | — | 35.444 s | controller |
| artifact transfer (1,164 B) | — | 0.560 s | controller |
| module execution | — | 0.67 s | module's own telemetry |

**The model was 2.3× too high**, and the error sat almost entirely in the
two terms it had flagged as inferred. `cost.OVERHEAD_S` is now measured,
with per-term provenance, and a one-second workload projects at 36 s total
against the 35.4 s observed.

**Provision is an upper bound, not a measurement.** 31.4 s elapsed from
create-accepted to first telemetry, of which 7.0 s is accounted for on the
pod's own clock. Up to 15 s of the remainder is the controller's own poll
interval, so the true provisioning time lies somewhere between about 9 s
and 24 s and is not yet isolated. A shorter poll interval would tighten
it; that is Iteration 2's to do, and the model says so rather than
quoting the bound as a fact.

**The variance matters more than the median.** The same bootstrap was
measured at **6.0 s and at over 305 s** on consecutive flights with the
same image, the same wheels and the same GPU class. `cupy-cuda12x` with
its `nvidia-*` dependencies is about a gigabyte, and how long that takes
is not a property of the workload. `cost.OVERHEAD_OBSERVED_RANGE_S`
records the spread, and the controller no longer uses a deadline to decide
whether a pod is alive.

**No billing reconciliation.** $0.0032 is measured wall time at a quoted
rate. The provider was never asked for billing data, so nothing here
claims it was.

---

## 3. WHAT THE FIVE FAILED ATTEMPTS FOUND

Ordered as they happened. Total cost of finding all of this: **$0.121**.

### Attempt 1 — no GPU capacity, and the request was fine

Three creates refused with HTTP 400. The controller reconciled inventory
after each, confirmed nothing existed, and reported `NOT_RUN`. **No pod,
$0.0003.**

Reading the provider's actual error body — a 400 creates nothing, so it is
free to ask — gave: *"There are no longer any instances available with the
requested specifications."* The request was valid; there was no RTX A4000
capacity in SECURE cloud.

**Earned:** `gpu.alternatives`, an ordered list of GPUs a workload can run
on. The controller walks it, and every attempt goes through
`create_with_reconcile`, so a failed create is confirmed to have created
nothing *before* the next id is tried. Walking a list without that would
be a loop of blind retries — the exact failure the reconciliation exists
to prevent. An unresolved outcome stops the walk immediately, because
trying another GPU there could put a second pod beside one that cannot be
named. Cost now follows the GPU that actually ran; billing the requested
card would misreport every run that fell back, and an A40 is 2.9× an
A4000.

### Attempt 2 — a pod, and ten minutes of silence

The fallback worked on hardware: A4000 refused, A5000 accepted. Then the
pod never became reachable and the run reported `FAILED` after 600 s with
no indication of why. **$0.0444.**

**Earned:** a failed fetch now leaves evidence — url, status and error —
and the controller reports the reason once per distinct cause. Silence was
the real defect; ten minutes of pod time bought one uninformative word.

### Attempt 3 — 404, immediately and for ten minutes

With diagnostics, the answer arrived in the first second: `status=404`. Not
a connection error. **The artifact server had been up the whole time and
the controller was asking for the wrong path.** $0.0435.

`MODULE_CONTRACT.md` says artifact paths are relative to
`$PROMETHEUS_ARTIFACT_DIR`. The artifact server's document root *is* that
directory, so a file at `/app/out/result.json` is served at
`/result.json` — and the controller, along with both example specs, was
asking for `/out/result.json`. The contract was right; the implementation
and the examples were not, and nothing tested the agreement between them.
The conformance test even *stripped* a leading `out/`, papering over
precisely this mismatch.

**Earned:** paths corrected, the conformance test now refuses any artifact
path containing a slash, and the contract states where paths are rooted
with the cost attached.

Two things were also fixed before this attempt, both found without
spending: **the bootstrap never started an artifact server at all**, so
every fetch would have failed; and a built bundle left inside the module
directory gets swept into the next bundle, so "same content, same hash"
quietly stops holding.

### Attempt 4 — PASS, with one file missing

`result.json` absent while `telemetry.jsonl` arrived. **$0.0032.**

**Earned:** a missing artifact is a question the pod can still answer
while it is alive, so the controller now fetches the server's document
index and records it. Guessing at this from the ground had already cost a
flight.

### Attempt 5 — the listing answered it in one request

```
<li><a href="stages.jsonl">stages.jsonl</a></li>

stages: boot, fetched, server_up, verified, unpacked — then nothing
        for the remaining 305 seconds.
```

The pod was healthy. It was installing a gigabyte of CUDA wheels, and the
controller had called it dead. **$0.0294.**

**Earned:** the controller waits on **progress, not on a clock**. It reads
the pod's stage markers each poll, logs each new stage, and gives up only
when nothing has advanced for `stall_timeout_s`, or at a hard ceiling. A
failure now names the stage — *"furthest bootstrap stage reached was
unpacked"* — instead of an elapsed time that says nothing about where it
stuck. A fixed deadline cannot tell a slow dependency install from a dead
pod, so it calls both dead and discards the one that was about to work.

### Attempt 6 — PASS, complete

Both artifacts, full telemetry, module exit code 0, clean teardown.

---

## 4. LEDGER ITEMS FROM THIS ITERATION

**The cost model's inferred terms were wrong by 2.3×, in the direction
that makes runs look more expensive than they are.** Marking them
`INFERRED` was right and was not enough; nothing forced them to be
measured. They are now measured, and the two that remain uncertain
(provision, and the bootstrap's variance) say so in their provenance.

**A test had baked an inferred number into a threshold.**
`test_cost_separates_overhead_from_compute` asserted that overhead exceeds
50% of a one-minute job. That was true only of the inflated estimate, so
the better measurement failed the test. The test now asserts the
*property* — fixed overhead dominates a short enough job — rather than a
figure. A test pinned to a number it did not derive will fail exactly when
the number improves.

**The cost breakdown did not add up.** `usd_overhead` and `usd_compute`
were each rounded independently of `usd_total`, leaving a residue. Small,
and still a defect in a money report. The reported total is now the sum of
the reported parts.

**Five of six flights failed, and that is the correct ratio for a first
rung.** Every failure was a condition the fake provider could not have
produced: real capacity limits, a real proxy's 404 semantics, a real
contract mismatch between two of my own files, and a real dependency
install two orders of magnitude slower than any deadline I would have
guessed. All five are now fake-provider tests, which is the point —
**real RunPod should discover conditions, not logic.**

---

## 5. WHAT A SEAT NO LONGER NEEDS TO KNOW

Iteration 1 removed four more items from the list of things a seat would
otherwise have to learn:

- which GPU has capacity right now (declare alternatives);
- that the artifact server exists, what port it uses, or that it needs a
  token (the platform writes, starts and authenticates it);
- that a pod's bootstrap can take six seconds or six minutes for the same
  work (the controller waits on progress);
- what the provider's 400 means in each of its several senses.

Still on the list, and Iteration 2's to remove: nothing about request
JSON, User-Agent, credential handling, reconciliation, cleanup semantics
or pod ownership — those were already gone after Iteration 0.

---

## 6. STATE AND NEXT RUNG

| | |
|:--|:--|
| Iteration 0 | complete, $0.00 — platform, docs, 40 tests |
| Iteration 1 | **complete, $0.124** — flown, measured, 6 attempts |
| tests | 148 passing across 6 files |
| campaign spend | $0.124 of $5.00 |
| pods leaked | none; inventory independently verified empty after each |

**Iteration 2** should increase at least one axis and leave reusable
machinery behind. The measurement this rung produced points at the axes
worth taking: a shorter poll interval to isolate provisioning, a longer
workload to move the overhead fraction off 97%, and a heavier artifact to
measure transfer against something larger than 1,164 bytes.

The scout/calibrate/campaign path built alongside this iteration
(`prometheus_gpu/scout.py`) has not yet been flown. Its regression test is
AETH-02: given a representative calibration, it refuses three trajectories
against a $2.60 ceiling and reports that the ceiling affords about 2.4 —
which is what actually completed. Flying it is Iteration 2's other half.
