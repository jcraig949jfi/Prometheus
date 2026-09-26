# RunPod Engineering Ladder — Iterations 3 and 4: long-run reliability, failure injection, fan-out

Date: 2026-09-26. Directive: `roles/Aether/prompts/2026-09-26_next_round/DIRECTIVE.md`
(manifest verified). Branch `aether/runpod-iter3-2026-09-26`, base `39887c4ef`.

**Iteration 3 spend: $0.5821. Iteration 4 spend: $0.0570. Campaign total:
$0.8446 of $5.00.** Caps were $1.50 and $1.00.
Pods leaked: **none.** After every real flight, a separate
`python -m prometheus_gpu.cli inventory` read (not the controller's own
check) returned `active: 0`. The one exception was deliberate: during the
controller-kill test it returned exactly the one pod that the killed
controller had left running, and that pod was later terminated by the
resumed controller.
Billing reconciliation: **not claimed.** Every dollar figure is measured wall
time multiplied by a quoted hourly rate.

This is an infrastructure report. Nothing in it is a scientific result.

---

## 1. VERDICTS

| gate item | Iteration 3 | how it was established |
|:--|:--|:--|
| exact ownership | **held** | Adoption is by NAME only. Unnamed listings are treated as AMBIGUOUS. Resume refuses a pod whose name has changed. In the fan-out, three concurrent creates collided on the same card and none adopted a sibling's pod |
| recoverable state | **held** | Ledger per run. The controller was hard-killed on real hardware (`os._exit`) and resumed from the ledger 123 s later with no second create |
| durable evidence | **held after repair** | Two defects found and fixed: ledger writes could abort a run, and an error path skipped retrieval. Artifacts are verified against a digest computed on the pod. Platform samples are snapshotted during the run |
| honest disposition | **held** | Every receipt carries a derived `disposition` answering the six questions. Absence requires LIST and GET to agree. Capacity is labelled INFERRED because 400 bodies are not read |
| safe cleanup | **held** | 0 active after every flight, checked independently. Absence was confirmed by LIST+GET on every pod that existed |
| bounded spend | **held** | $0.58 of $1.50. No flight exceeded its ceiling except F2, which stopped AT its $0.05 ceiling by design |

**Iteration 3 PASSES its gate, after repairing the real reliability
defects it found** (§4). The directive allowed continuing to Iteration 4
after repairing a real defect. Iteration 4 **PASSES** (§6).

Iteration 3 real flying stopped under the 4-failed-flights rule: F2, F2b,
L1a, and A1's pinned campaign that was refused for capacity. Every flight
the gate depends on had flown by then.

---

## 2. WHAT WAS FLOWN

| # | flight | card (how chosen) | result / cause | wall | $ |
|--:|:--|:--|:--|--:|--:|
| F1 | soak 300 s, **exit** fault at 60 s | A4000 (declared first) | FAILED / MODULE_EXITED_WITHOUT_END | 123 s | 0.0058 |
| F2 | soak 300 s, **killserver** at 60 s | A4000 | ABORTED / BUDGET_CEILING, **fault-injector defect** (§4.1) | 1,074 s | 0.0507 |
| F2b | same, fixed bundle | all five SECURE cards refused | NOT_RUN / NO_CAPACITY (§4.3) | 0 | 0.0000 |
| F2c | same | RTX 4000 Ada (**stock order**) | UNKNOWN / ARTIFACT_SERVER_UNREACHABLE | 265 s | 0.0206 |
| F3 | soak 300 s, **hang** at 60 s | L4 (stock order) | ABORTED / TELEMETRY_STALLED | 209 s | 0.0249 |
| L1a | soak **3,900 s**, planned kill at +1,500 s | L4 | UNKNOWN / CONTROLLER_ERROR at +1,470 s, **durability defects** (§4.2) | 1,470 s | 0.1756 |
| L1b | same, repaired | A5000 (stock order) | **OK**; controller killed, then resumed | 3,927 s | 0.2830 |
| A1 | `--auto`: scout → plan → campaign, 3,000 matmuls | 4090 → *refused* → A5000 | **OK**, one automatic re-scout | 4 flights | 0.0215 |
| I4 | 3 concurrent soak shards, 240 s, c exits at 60 s | A5000 / 4090 / L4 | **PARTIAL** as designed | ~275 s | 0.0570 |

Evidence for every flight: `Aether/runpod/receipts/<run_id>.json`,
`receipts/<run_id>/` (platform samples, telemetry, series, controller
health, API calls, ledger events), plus the console logs `receipts/i3_*.log`
and `receipts/i4_*.log`. The predictions are in
`receipts/i3_preregistration.json`, committed at `f369c6855` before any
flight.

---

## 3. THE LONG FLIGHT (L1b): 65 minutes, with a controller kill in the middle

A 3,900 s soak ran on an RTX A5000: 4096² matmul windows, device and host
memory, a steadily growing `series.jsonl`, and a 4 MiB checkpoint every
600 s. At +1,500 s after the first telemetry, the controller was killed with
`os._exit(137)`, which skips every `finally`, leaving the pod running. 123 s
later a new process ran `flight.py --resume .ledger/<run>.json`. It confirmed
by GET that the pod still existed and still carried this run's name, created
nothing, watched until the module ended, retrieved and verified every
artifact, terminated the pod, and established absence by LIST and GET.

Every drift prediction below was computed by `soak_drift.py` from the raw
rows, not from the receipt's summaries (`receipts/i3_L1b_drift.json`):

| | prediction | observed | |
|:--|:--|:--|:--|
| P1 | module 3,900 ± 2 s | 3,900.009 s | PASS |
| P2 | ≤ $0.22 on A4000, ≤ $0.62 worst card | $0.2830 on A5000 | PASS |
| P3 | no device-memory creep | CuPy pool held **identical** from window 30 to the end; driver free bytes **identical** | PASS |
| P4 | module RSS, last 10 windows within 5% of windows 30–39 | **+16.7%** | **FAIL as written** |
| P5 | p50 step latency within 5% (windows 30–59 vs last 30) | +0.06% | PASS |
| P6 | p99/p50 < 1.5 in ≥ 95% of windows | 100% of windows; max 1.02 | PASS |
| P7 | no progress gap > 30 s, **including across the controller gap**; sampler cost flat | max gap 10.3 s; sampler cost p50 0.033 → 0.035 s | PASS |
| P8 | 390 ± 2 series rows, 6 checkpoints, every artifact verified | 390, 6, 4/4 VERIFIED against `/_manifest` | PASS |
| P9 | provider latency second-half p50 within 2× of first half | fetch 0.221 → 0.221 s over 685 calls, **0 failures**; GET 0.40 → 0.32 s | PASS |
| P10 | pod-clock offset start/end within 0.5 s | +0.159 → +0.186 s (drift 0.027 s over 65 min) | PASS |
| P11 | resume: no second create, absence by LIST+GET | 0 creates on resume, `controller_absent_s` 122.5, LIST and GET agree | PASS |
| P12 | controller spend vs receipt within 2% | $0.2828 vs $0.2830 (0.08%) | PASS |

**P4 is recorded as failed.** The rows show a bounded step rather than a
creep: 431 MB, then 495 MB at the first checkpoint (610 s), then 503 MB at the
second (1,210 s), then flat for the remaining 2,690 s. The module keeps a
64 MiB host copy of its matrix after each checkpoint. The prediction compared
windows that straddle the module's own checkpoint schedule, so it was
mis-specified. It is not rewritten after the fact. This is not a platform
defect.

Other long-flight observations: GPU utilisation mean 99.2%, power mean 223 W
(A5000), temperature peak 56 °C, 392 platform samples, artifact directory
peak 29.8 MB.

---

## 4. DEFECTS FOUND, AND WHAT EACH FAILURE BOUGHT

Hardware found five defects the fake could not, and one labelling error.
Each fix has a test that fails on the old code.

### 4.1 F2: the fault injector killed the container, and the container restarted into a loop

The soak module's `killserver` fault matched `_serve.py` anywhere in a
process command line. The pod's bootstrap runs as `bash -c <script>`, and
that script text mentions the server, so the injector killed the container's
main process. **RunPod restarted the container**, and the bootstrap re-ran
from the top on the same disk. The module started again and appended a second
run to the same telemetry, in a loop: the stage file held 80 lines, ten boots.
The controller saw an ordinary, progressing run until the $0.05 ceiling
stopped it. I diagnosed this live, by reading the pod's own stage file
through the proxy while it billed.

- **Fixed:** the injector now matches argv, not substrings (FAILURE_PLAYBOOK 24).
- **Fixed (platform):** a restart guard now runs before `stage boot`. A
  restarted container serves what the first run wrote and never re-runs the
  module. The controller reports `CONTAINER_RESTARTED` (playbook 25). This
  guard covers any main-process death, not only the injector.
- **Fixed:** the pod clock is now re-measured when `/_clock` was not ready at
  first contact. F2 lost its clock sync that way (playbook 27).

### 4.2 L1a: the durability layer ended a healthy run

At +1,470 s, `os.replace` onto the ledger raised `WinError 5`, a transient
Windows sharing lock. The ledger write was allowed to raise, so a best-effort
durability record ended a healthy run. The exception path then went straight
to teardown **without retrieving**, so 1,450 s of evidence on the pod came
back MISSING with zero platform samples. Cleanup was still correct.

- **Fixed:** ledger writes retry with backoff and never raise into the run.
  Failures are recorded in `ledger_errors`, and the previous ledger stays
  valid because the replace is atomic.
- **Fixed:** the error path retrieves before teardown, in both `run` and
  `resume`.
- **Cause of the lock:** not established. Candidates are this session's own
  Git Bash watcher that `stat`ed the ledger, or a Windows indexer or scanner.
  The fix does not depend on which.

### 4.3 F2b: "no capacity" that nobody had read

All five declared SECURE cards returned 400. The receipt said NO_CAPACITY
because every create had failed cleanly. But the qualified client discards
400 bodies, and a malformed request would look identical, which mattered
because F2b followed a change to the bootstrap. A one-off direct POST of the
identical body read the provider's own words: *"There are no longer any
instances available with the requested specifications."*

A read-only GraphQL stock query then showed exactly one SECURE card in stock,
the RTX 4000 Ada, which the spec did not declare.

- **Fixed:** NO_CAPACITY receipts now state that capacity is INFERRED, not
  read (playbook 23).
- **New:** `RunPodProvider.stock_status`. The controller tries in-stock cards
  first; it reorders and never drops a card. F2c, F3, L1b, A1 and all three
  Iteration 4 shards landed on the first or second card they tried.

### 4.4 F2c: evidence that lived only on the pod

Once the server died, telemetry up to the fault was already in the receipt,
but the platform samples were zero. `platform.jsonl` and the stage file had
been fetched only at retrieval.

- **Fixed:** both are now snapshotted every 6 watch polls, and a snapshot is
  only ever replaced by a longer one (playbook 26).

### 4.5 A resume that refused a pod, then terminated it

This was caught in the fake, before hardware. The first `resume()` decided a
pod was not ours inside a `try` whose `finally` runs teardown.
`test_resume_leaves_alone_a_pod_that_is_no_longer_ours` failed, and ownership
is now settled before anything can reach teardown.

---

## 5. FAILURE INJECTION: THE SIX QUESTIONS

Every receipt now carries `disposition`, derived from its own facts. The
fake-provider suite (`test_prometheus_gpu_iteration3.py`, 52 tests) injects
every failure the directive lists. The pod-side faults were then qualified on
hardware.

| failure | where | 1 controller believes | 2 provider believes | 3 evidence retained | 4 resume | 5 cleanup safe | 6 uncertainty vs absence |
|:--|:--|:--|:--|:--|:--|:--|:--|
| process exits non-zero | fake + **F1** | FAILED / MODULE_EXITED_WITHOUT_END, from the stage file within a poll | pod gone (LIST+GET) | telemetry, series, platform: VERIFIED | not needed | yes | result/ckpt MISSING (absent: never written) |
| process hangs | fake + **F3** | ABORTED / TELEMETRY_STALLED at 127 s unchanged | pod gone | telemetry, series VERIFIED; 20 platform samples | not needed | yes | result/ckpt MISSING |
| timeout | fake | TIMEOUT / MAX_RUNTIME | pod gone | telemetry to the cap | not needed | yes | — |
| artifact server disappears | fake + **F2c** | UNKNOWN / ARTIFACT_SERVER_UNREACHABLE after 131 s of silence, GET still true | pod existed until terminated | telemetry read before the fault; platform snapshots (after §4.4) | not needed | yes | all artifacts MISSING, not mismatched |
| artifact corruption | fake | `integrity: mismatch`, re-fetched 3×, kept as `<path>.mismatch` | — | the corrupt bytes as evidence, never as the artifact | — | yes | MISMATCH ≠ VERIFIED ≠ MISSING |
| partial retrieval | fake | mismatch by size (5 of 14 bytes) | — | as above | — | yes | same |
| telemetry stalls | fake + F3 | TELEMETRY_STALLED; a 240 s pause under a 300 s threshold is NOT a hang (tested) | — | — | — | yes | — |
| controller interruption / restart | fake + **L1b** | the killed controller leaves the pod and a ledger; resume continues | pod running until the resumed controller ends it | ledger events, all telemetry, all artifacts | **yes**, from the ledger, 0 creates | yes | cost counted from the original create |
| create response lost after acceptance | fake | adopted BY NAME, 1 create | pod exists | — | — | yes | `creation_outcome: adopted` |
| … and omitted from every LIST | fake | NOT_RUN, with a note that absence rests on LIST alone | pod exists (**the residual risk**) | — | no id | **not provable** | named as uncertainty in the receipt |
| status-less ambiguous create | fake | reconciled by name, 1 create | — | — | — | yes | — |
| LIST omission (after ACK) | fake | `UNCERTAIN: LIST omits it but GET still returns it` | pod exists | — | — | **no** | Iteration 2 would have called this clean |
| GET/LIST disagreement | fake | re-read up to 4×; if it persists: `UNCERTAIN: GET says gone but LIST still shows it` | — | — | — | no | recorded, never resolved by preference |
| transient DELETE failure | fake | retried, ACK | gone | — | — | yes | — |
| inventory unreadable at teardown | fake | UNCERTAIN; cleanup not claimed | unknown | — | — | no | `inventory_read_ok: false` |
| ambiguous GET errors during watch | fake | not a verdict; run completes | — | — | — | yes | — |
| container restart | fake + **F2** | CONTAINER_RESTARTED (after §4.1) | pod exists | what the first run wrote | — | yes | — |
| someone else's pod after a failed create | fake | FAILED_CLEAN; the foreign pod is untouched | foreign pod exists | — | — | yes | — |
| concurrent creates colliding on one card | **I4** (real) | each 500 reconciled by name (two LIST reads), then the next card | none of ours created | — | — | yes | — |

**Nothing blindly retries a create.** A retry happens only after two LIST
reads, 5 s apart, both show none of ours. An unreadable listing, or one with
no names, stops the walk.

**The one residual this platform cannot close is named in every receipt
it could affect.** If a create succeeded, its response was lost, and every
LIST omits the pod, then there is no id to GET. The receipt says its
"nothing was created" rests on LIST reads alone.

---

## 6. ITERATION 4: THREE CONCURRENT PODS

`flight.py examples/soak --go --fanout receipts/i4_shards.json`, using
`prometheus_gpu/fanout.py`. One campaign preflight checked that the account
held nothing but this campaign's pods. Then three controllers ran in
parallel, each with its own run id, ledger, receipt and cleanup.

All three raced for the same "Low" stock A5000. One got it. The other two
received **real HTTP 500s**, reconciled each by name, and moved on, to an L4
and (after a second 500) a 4090. None adopted a sibling's pod.

| shard | card | result | module | artifacts | cleanup | $ |
|:--|:--|:--|--:|:--|:--|--:|
| a | A5000 | OK | 240.8 s | 4/4 verified | ACK + LIST + GET absent | 0.0197 |
| b | 4090 | OK | 240.5 s | 4/4 verified | ACK + LIST + GET absent | 0.0257 |
| c | L4 | FAILED / MODULE_EXITED_WITHOUT_END (designed) | 60.8 s | telemetry, series verified; result, ckpt missing | ACK + LIST + GET absent | 0.0116 |

Campaign receipt `i4-164557.campaign.json`: **PARTIAL** (never OK while
a shard failed); 3 distinct pods and run ids; `operational_cleanup` true
because every shard's own receipt claims it; $0.0570 against ≤ $0.12
preregistered. Shards a and b were unaffected by c (both within 0.4% of
240 s). Fail-fast is opt-in (`--fail-fast`), tested on the fake, and records
the stopped siblings as `CAMPAIGN_FAIL_FAST`, not as their own failure.

---

## 7. THE FEEDBACK LOOP: SCOUT → CALIBRATE → CAMPAIGN AS THE DEFAULT

`flight.py mod --go --auto --units N --preregistered $X` is now one command,
using `prometheus_gpu/campaign.py`. A1 flew it and hit the exact failure that
Iteration 2 had recovered from by hand:

1. The scout landed on an RTX 4090 via the stock order and calibrated to
   PROCEED.
2. The campaign, pinned to the 4090, was **refused for capacity 7 s later**:
   NOT_RUN, $0, and the provider confirmed nothing was created.
3. The chain **re-scouted automatically** without a pin, landed on an A5000,
   recalibrated, and flew the pinned campaign: OK.

The campaign receipt's canonical `estimates` block:

| | Iteration 2 (L4) | Iteration 3 A1 (A5000) |
|:--|--:|--:|
| spec sheet | $0.0259 (**−36.5%**) | $0.0148 (**−4.3%**) |
| scout-calibrated | $0.0432 (**+5.9%**) | $0.0157 (**+1.5%**) |
| actual | $0.0408 | $0.0155 |

The Iteration 2 row is a regression test
(`test_iteration_two_estimates_are_the_regression_case`). A1's spec-sheet
figure was preregistered for an A4000. It landed close on the A5000 by
coincidence of the two cards' price-to-throughput ratios, and it is reported
as preregistered, not recomputed.

**The stock order introduced a cost-estimate failure mode:** a
preregistration priced on the declared first card misses by the rate ratio
when the run lands elsewhere. F2c ($0.0206, Ada) and F3 ($0.0249, L4) each
exceeded a $0.02 bound written for an A4000. Both are recorded as misses.

---

## 8. TELEMETRY AND CONTROLLER HEALTH

- **Provider API latency** is recorded per operation, overall and first half
  vs second half. Over 65 minutes: fetch p50 0.221 s both halves, p99 0.34 s,
  0 failures in 685 calls. No polling degradation.
- **Controller health:** one record per watch poll (loop time, poll gap,
  running spend, telemetry size). Last-poll spend agreed with the receipt to
  0.08%.
- **Observer cost:** the platform sampler's cost is 0.033–0.035 s per sample,
  flat over the hour.
- **Clock:** the offset was measured at both ends of every flight, with a
  maximum drift of 0.027 s over 65 minutes.
- **Log growth:** telemetry reached 398 records and series 121 kB in 65
  minutes, growing linearly. Nothing surprising.

---

## 9. CAPABILITIES ADDED (reusable by any seat)

- **Ledger and resume:** `flight.py --resume`, `Controller.resume`, and
  `.ledger/` (gitignored).
- **Watch exits:** module exit without `end`, hang, unreachable server,
  vanished pod, container restart, and campaign fail-fast.
- **Absence:** requires LIST and GET together, with per-pod `absence_evidence`.
- **Artifact integrity:** checked against the pod-side `/_manifest`, with
  verified / unverified / mismatch / missing kept apart.
- **Receipt fields:** `disposition`, `api_latency`, `controller_health`,
  `stock_at_launch`, `resumed`, `estimates`.
- **Stock-ordered GPU walk:** `RunPodProvider.stock_status`.
- **Workflows:** `--auto` (`campaign.py`), `--fanout` (`fanout.py`), and
  `--env` overrides that leave the bundle unchanged.
- **Soak module:** `examples/soak`, with controlled `exit` / `hang` /
  `killserver` faults.
- **Drift analysis:** `soak_drift.py` for long-flight checks.
- **Watch poll** tightens to 3 s near the expected module end.
- **Documentation:** FAILURE_PLAYBOOK 23–28, `RUN_RECEIPT_SCHEMA.md`
  (Iteration 3 fields), guide (one command, fan-out, controller death),
  and `COST_MODEL.md`.

Gates, each run as its own command and read:

    test_prometheus_gpu.py              60 passed
    test_prometheus_gpu_launch.py       40 passed
    test_prometheus_gpu_examples.py     24 passed
    test_prometheus_gpu_scout.py        19 passed
    test_prometheus_gpu_iteration2.py   29 passed
    test_prometheus_gpu_iteration3.py   52 passed
    test_aeth01_terminology_audit.py     3 passed

---

## 10. STILL OPEN

- **A pod that every LIST omits after a lost create response.** This is named
  in the receipt and cannot be closed without provider-side idempotency keys
  or a name-filtered query that is independent of LIST.
- **A restart that also loses the disk.** The restart guard sees no stage
  file and the module runs again. Only a reset in the telemetry sequence
  would show it.
- **400 bodies.** The qualified client still discards them. The probe in §4.3
  was a one-off. Reading the body safely inside the client would let the
  controller say "capacity" rather than infer it.
- **The 305 s install** from Iteration 1 has not reproduced in 13 samples
  (4.4–14.7 s).
- **A cost estimate for a card the run may land on.** Preregistrations should
  price every declared alternative, not only the first.
- **Iteration 5** (a foreign seat's module) is next on the ladder.
