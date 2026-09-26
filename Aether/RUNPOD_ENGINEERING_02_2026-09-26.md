# RunPod Engineering Ladder — Iteration 2: scale up, and the scout path

Date: 2026-09-26
Campaign ceiling: $5.00. Iteration 2 cap: $1.00.
**Iteration 2 spend: $0.0815 (estimated). Campaign total: $0.2055.**
Pods leaked: none. Inventory independently read `active: 0` after every
flight, as a separate command from the controller's own absence check.
Billing reconciliation: **not claimed.** Every dollar figure here is measured
wall time at a quoted hourly rate.

This is an infrastructure report. Nothing in it is a scientific result.

---

## 1. WHAT WAS FLOWN

Six real flights through `flight.py` (new: generic over any module
directory) and `prometheus_gpu.launch.Controller`, carrying
`examples/gpu_load` (new): a sustained FP32 matmul load at n = 8192 with a
6 GB device-memory ballast and an 8 MiB binary artifact. Work units are
matmuls, read from `PROMETHEUS_WORK_UNITS`.

| # | flight | GPU | result | wall | est. cost | receipt |
|--:|:--|:--|:--|--:|--:|:--|
| 1 | scout, 300 matmuls | RTX A4000 | **OK** | 57.7 s | $0.0027 | `gpu-load-scout-20260926T065221Z` |
| 2 | campaign, 6000, pinned | RTX A4000 | **OK** | 590.9 s | $0.0279 | `gpu-load-20260926T065409Z` |
| 3 | campaign, 3000, pinned, plan attached | RTX A4000 | NOT_RUN — no capacity | 0.5 s | $0.0000 | `gpu-load-20260926T071205Z` |
| 4 | same, one retry | RTX A4000 | NOT_RUN — no capacity | 0.5 s | $0.0000 | `gpu-load-20260926T071218Z` |
| 5 | scout, 300, unpinned | **L4** (4th choice) | **OK** | 84.4 s | $0.0101 | `gpu-load-scout-20260926T071229Z` |
| 6 | campaign, 3000, pinned, plan attached | L4 | **OK** | 341.8 s | $0.0408 | `gpu-load-20260926T071408Z` |

Flights 3 and 4 created nothing; the provider confirmed it after each
refusal, by inventory read, before anything else was tried. They are counted
against the four-failure stop rule anyway (2 of 4 used). Their receipts
priced 0.5 s of controller time as $0.00002 of spend; that is a defect,
fixed (s6), and the table shows the corrected $0.

Evidence for every flight: `Aether/runpod/receipts/<run_id>.json` plus
`receipts/<run_id>/` holding `platform.jsonl`, `telemetry.jsonl` and
`result.json`, and the controller console as `receipts/i2_flight*.log`. The
8 MiB `state.bin` artifacts are recorded by size and sha256 only; on all
four passing flights the controller's digest equals the digest the module
computed on the pod.

---

## 2. PREREGISTERED VERSUS OBSERVED

Written and committed before the first flight:
`receipts/i2_preregistration.json` (commit `3b22826cf`).

| prediction | falsified if | observed | verdict |
|:--|:--|:--|:--|
| provision 9–24 s (Iteration 1's bound) | outside [5, 60] s | **2.14, 2.29, 22.13, 2.82 s** (± 0.19–0.25) | **FALSIFIED** on three of four |
| 8 MiB artifact ≥ 1 MB/s through the proxy | < 1 MB/s | 4.7–5.4 MB/s | holds |
| campaign overhead < 25% of wall | ≥ 25% | 5.1% (A4000, 6000), 5.3% (L4, 3000) | holds |
| clock offset \|x\| < 5 s, uncertainty < 0.5 s | uncertainty ≥ 0.5 s | +0.33 to +0.39 s, ± 0.17–0.25 s | holds |
| A4000 at 60% of FP32 peak: 0.0954 s/matmul | — | 0.0920 (scout), 0.0934 (campaign) | 3.6% / 2.1% pessimistic |
| L4 at 60% of FP32 peak: 0.0605 s/matmul | — | 0.1026 (scout), 0.1079 (campaign) | **L4 delivered 35% of peak** |

Overhead here is wall time minus the module's own loop time.

---

## 3. THE THREE AXES

### 3.1 Provisioning is now measured, and it was not what Iteration 1 thought

The pod's artifact server answers `/_clock` with its own time. The
controller takes five round trips at first contact, keeps the shortest
(offset = pod time − round-trip midpoint, uncertainty = half the round trip),
and repeats at retrieval to bound drift. Start/end offsets agreed within
0.04 s on every flight.

| flight | offset | ± | **provision** (pod running) | first contact via proxy | pod bootstrap |
|:--|--:|--:|--:|--:|--:|
| 1 A4000 | +0.368 | 0.230 | **2.14 s** | — (field added after) | 9.23 s |
| 2 A4000 | +0.389 | 0.247 | **2.29 s** | — | 8.90 s |
| 5 L4 | +0.349 | 0.201 | **22.13 s** | 33.35 s | 13.65 s |
| 6 L4 | +0.337 | 0.185 | **2.82 s** | 24.36 s | 6.31 s |

Iteration 1's "≤ 24 s provisioning" was two mechanisms in one interval. The
pod's shell usually runs **~2–3 s** after the create is accepted. The
provider's **proxy** then answers 404 for ~20–25 s more before it routes to
the pod at all. The proxy delay overlaps the bootstrap, so it is not billed on
top of it, but it is invisible without a synchronised clock. One host in four
took 22 s to provision: this is a property of where the pod lands, not of
the card. FAILURE_PLAYBOOK 21.

Ready-wait polling was 3 s on every flight (default is now
`min(poll, 5 s)`).

### 3.2 Longer workload: overhead from 97% to 5%

| | Iteration 1 | flight 2 (A4000) | flight 6 (L4) |
|:--|--:|--:|--:|
| module loop | 0.67 s | 560.7 s | 323.8 s |
| wall | 35.4 s | 590.9 s | 341.8 s |
| overhead share | 97% | **5.1%** | **5.3%** |
| GPU utilisation, mean | — | 96.2% | 96.4% |
| device memory peak | — | 7.6 GB of 16 GB | 7.6 GB of 23 GB |
| power, peak | — | 140 W (the cap) | 77 W (cap 72 W) |
| temperature, peak | — | 75 °C | 71 °C |
| throughput | — | 11.77 TFLOP/s | 10.19 TFLOP/s |

**Scouts see a cold card.** Both cards run at their power cap, and both
settled below the throughput a 30-second scout measured: A4000 by 1.5%
(11.95 → 11.77), L4 by 5% (10.72 → 10.19). The calibrated compute estimate
was short by 1.6% and 5.1% respectively for that reason. The 20% planning
margin absorbs it; a scout of a few minutes would remove it.

### 3.3 Heavier artifact

8,388,608 bytes per flight. The largest file moved at **4.7–5.4 MB/s**
through the RunPod proxy; total retrieval (three files, including the
per-file handshakes) took 4.3–5.3 s. Digests matched end to end on all four.
The guide's old "8 MB limit" belonged to the retired AETH bench server, not
to the platform's artifact server, and has been removed.

---

## 4. THE SCOUT PATH, ON HARDWARE

The sequence the ladder asked for — scout → measure → estimate →
refuse-or-proceed, with both estimates in the receipt — flew twice.

| | A4000, 6000 matmuls | L4, 3000 matmuls |
|:--|--:|--:|
| preregistered (spec sheet × 60%) | $0.0287 | $0.0259 |
| calibrated from the scout | $0.0332* / $0.0145 (3000) | **$0.0432** |
| actual | **$0.0279** | **$0.0408** |
| calibrated vs actual | +19%* | **+5.9%** |
| preregistered vs actual | +2.9% | **−37%** |
| both estimates in the receipt | no (plan in `i2_campaign_plan.json`) | **yes, validated** |

\* The first calibration included the 120 s teardown RESERVE in its
expectation, although the scout's measured overhead already contained a
real teardown. That double count was the whole of its 19% error. Fixed:
the reserve now sits only in `usd_with_margin`, which is what the ceiling
and the decision use. Recalibrated for 3000 matmuls under the fixed model,
the A4000 plan came to $0.0145 against a $0.0152 preregistration; that
campaign was refused for capacity before it could fly (flights 3–4).

**The L4 is the case for scouting in one line.** The spec sheet says
30.3 TFLOP/s; this workload got 10.2–10.7. A preregistration at 60% of peak
was 37% low. The scout found it for $0.010 and the calibrated plan landed
within 6%. Of that 6%, the cold-card effect made compute 5.1% short, and a
22-second provisioning on the scout's host made the overhead term generous;
the two partly cancelled, and the report says so rather than taking credit
for the agreement.

**Pinning costs availability.** A calibration is valid only on the card it
was measured on, so the campaign is pinned and drops its alternatives, which
leaves it one card to be refused on. Twelve minutes after the A4000 scout,
there was no A4000 capacity, twice. The recovery was the whole path again,
quickly: an unpinned scout walked the alternatives to an L4, and scout,
plan and campaign completed inside seven minutes. FAILURE_PLAYBOOK 22.

---

## 5. TELEMETRY AND OBSERVER OVERHEAD

Platform telemetry is now the platform's job. A sampler written into the
bootstrap starts after the artifact server and before the bundle fetch, so
the dependency install is on the record, and every `platform_interval_s`
seconds writes GPU memory, utilisation, temperature and power, host load and
RAM, disk, artifact bytes, and **its own cost per sample**. Every record has
UTC and monotonic time. It never raises; a failure becomes a field.
194 samples on the 10-minute campaign, 112 on the L4 campaign.

**Observer overhead, measured:**
- CPU: 0.029–0.057 s per sample (`nvidia-smi` plus `/proc`), i.e. 1–2% of
  one host core at a 3 s interval.
- GPU throughput: the sampler fires about once every 32 steps. The total
  excess of all steps over the median is (mean − p50) × steps = 0.13 ms ×
  6000 = 0.79 s of 560.7 s, **≤ 0.14%**, and that bound also absorbs the
  0.31 s warm-up step and the thermal drift. There is nothing left for
  adaptive sampling to recover at this rate.

Caveat recorded in the guide and schema: host RAM is the HOST's, which the
container sees whole (69–134 GB "used"); it is not the module's footprint.

---

## 6. DEFECTS FOUND AND REPAIRED

Every one has a fake-provider or unit test. Four were found at $0.

| | found | defect | fix |
|:--|:--|:--|:--|
| 1 | dry run, $0 | A scout shrank `work_units.estimate`, which never reached the module; the "scout" would have run the full campaign | `PROMETHEUS_WORK_UNITS` in the module env (playbook 19) |
| 2 | reading, $0 | `max_runtime_s` counted from the create, so a 305 s wheel install could time out a scout before it ran | runtime bound starts at first telemetry; money still bounded from create by the budget (playbook 20; test verified RED on the old code) |
| 3 | flight 1 | "provisioning" was mostly proxy reachability | measured clock offset; `synchronised.provision_s` and `accepted_to_first_contact_s` (playbook 21) |
| 4 | flight 2 | calibrated expectation double-counted teardown (+19%) | reserve moved to `usd_with_margin` only; two tests that pinned the old arithmetic now assert the property |
| 5 | flight 2 | a campaign plan's estimates had no way into the receipt | `flight.py --plan`, validated; refuses a plan for another module, unit count, a REFUSE, or one lacking its preregistered estimate |
| 6 | flights 3–4 | a confirmed non-event priced controller time as spend | $0 when the provider confirmed nothing exists; an UNRESOLVED create keeps its estimate |
| 7 | reading, $0 | a calibration did not record which GPU it came from | `calibrate(gpu_used=)`; `plan_campaign` refuses to price a different card unless accepted in words |

---

## 7. CAPABILITIES ADDED (reusable machinery)

- `flight.py`: build / dry / rehearse / go for ANY module; `--scout`,
  `--pin-gpu`, `--units`, `--platform-interval` (all in-memory: the bundle
  hash is unchanged, tested); `--calibrate` (scout receipt → campaign plan);
  `--plan` (both estimates into the receipt); evidence directory per run.
- Pod `/_clock`; controller clock-offset estimate at start and end.
- Platform sampler and `platform_summary` in every receipt.
- Per-artifact fetch timing and transfer rate.
- `examples/gpu_load`, executed by the conformance suite.
- `cost.OVERHEAD_S` re-measured with new terms (`module_setup`,
  `end_detection`, `retrieval`) and per-term provenance; the model totals
  27.0 s against 18.0 s measured (L4 campaign, 3 s watch poll) and 30.2 s
  (A4000 campaign, 10 s watch poll).
- End detection is a controller-poll property: 8.8 s at a 10 s watch poll,
  **0.39 s at 3 s**.

Gates, each run as its own command and read:

    test_prometheus_gpu.py            60 passed
    test_prometheus_gpu_launch.py     40 passed
    test_prometheus_gpu_examples.py   17 passed
    test_prometheus_gpu_scout.py      19 passed
    test_prometheus_gpu_iteration2.py 29 passed
    test_aeth01_terminology_audit.py   3 passed

---

## 8. REMAINING SINGLE POINTS OF FAILURE

- **Scout → plan → campaign is three commands.** Between them, capacity can
  vanish. `flight.py` should chain them, with a fresh unpinned scout as the
  fallback when the pinned card is refused. Iteration 3.
- **The proxy.** All telemetry, artifacts and the clock go through it; it
  took 20–33 s to route on every flight. A pod that runs but never routes is
  indistinguishable from one that never started until `stall_timeout_s`.
- **Bootstrap install variance** (6–305 s) is still unexplained; four more
  samples this round (5.2–12.2 s) did not reproduce the tail.
- **One card class per calibration.** A campaign that needs capacity
  elasticity has to accept an uncalibrated card in words or re-scout.

## 9. NEXT RUNG

Iteration 3 per the directive: a longer run with failure injection. What
this rung's measurements point at, in order:

1. Chain scout → plan → campaign in one command, with re-scout on refusal.
2. Failure injection on a cheap real pod: module exits non-zero, artifact
   over size, telemetry stream interrupted, controller killed mid-run and
   resumed from its ledger. The fake already covers the provider-side
   faults; these are the pod-side ones it cannot.
3. A scout long enough to reach thermal steady state, and a measurement of
   how long that is per card.
4. A watch poll that tightens near the module's expected end, since end
   detection is now the largest poll-dependent overhead term.

Spend so far: $0.2055 of $5.00.
