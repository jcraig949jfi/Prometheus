# Cost model

Authority: `prometheus_gpu/cost.py`. Checked by:

```bash
python -m prometheus_gpu.cli estimate module_spec.json --workload-seconds 300
```

## The model

```
cost = (accept + provision + bootstrap + canary + compute + teardown)
       / 3600 * hourly_rate * gpu_count
```

The hourly GPU price is the least interesting number in that line. What
you actually pay for a short experiment is dominated by the fixed part.

## Overhead, measured

Defaults in `cost.OVERHEAD_S`, **measured through the platform's own launch
path**: Iteration 1 on an RTX 4090 (`hello-gpu-20260924T212427Z`) and
Iteration 2 on an RTX A4000 (`gpu-load-scout-20260926T065221Z`,
`gpu-load-20260926T065409Z`):

| phase | seconds | provenance |
|:--|--:|:--|
| `accept` | 1.5 | **measured** — create call 1.1–2.9 s over four flights |
| `provision` | 2.3 | **measured, clock-synchronised** — 2.1, 2.3, 2.8 and **22.1** s (± 0.25 s); a property of the host |
| `bootstrap` | 8.0 | **measured** on the pod's clock; observed up to 305 s |
| `canary` | 1.2 | **measured**; a property of your canary |
| `module_setup` | 1.5 | **measured**; a property of your module |
| `end_detection` | 5.0 | ≈ watch poll / 2; measured 8.8 s at a 10 s poll, 0.4 s at 3 s |
| `retrieval` | 5.3 | **measured** for 8.4 MB; scales with bytes (5.4 MB/s) |
| `teardown` | 2.2 | **measured** — terminate ACK to absence confirmed |
| **total** | **27.0** | measured 30.1 s (A4000 scout), 30.2 s (A4000 campaign, 10 s poll), 18.0 s (L4 campaign, 3 s poll) |

**Provisioning is 2 seconds, not 24.** Iteration 1 could only bound it,
because it subtracted a controller instant from a pod instant as though the
two machines shared a clock. Iteration 2 measures the offset: the artifact
server answers `/_clock`, and the controller takes five round trips and
keeps the shortest (offset = pod time − midpoint, uncertainty = RTT/2,
≈ 0.23 s). With that, the pod's shell is running **2.1–2.3 s** after the
create is accepted -- on three of four hosts. The fourth, an L4 scout,
took **22.1 s**; the L4 campaign minutes later landed on a host that took
2.8 s. Provisioning is a property of the host a pod lands on, which the
platform does not choose, so a projection carries the median and the
observed range carries the tail.

The rest of what Iteration 1 called provisioning is the provider's **proxy**:
it answers 404 for ~25 s after the pod is already up
(`accepted_to_first_contact_s`). That delay overlaps the bootstrap, so it is
not billed on top of it — but it is why a controller cannot see a module
finish for up to ~25 s on a very short job. FAILURE_PLAYBOOK entry 21.

**Overhead is now 4.9% of a 10-minute run**, against 97% for Iteration 1's
0.67-second workload: 30.2 s of 590.9 s on the Iteration 2 campaign.

**Scouts see a cold card.** The A4000 ran at its 140 W power cap and
reached 75 °C within two minutes; throughput settled ~2% below the value a
27-second scout measured, and the calibrated compute estimate was 1.8%
short. The L4 did the same at its 72 W cap, by ~5% (10.72 → 10.19 TFLOP/s),
and its compute estimate was 5.1% short. A scout shorter than the card's thermal settling time
over-predicts throughput by about that much; the 20% planning margin
covers it, and a scout of a few minutes would remove it.

**The variance matters more than the median.** The same bootstrap measured
**6.0 s and over 305 s** on consecutive flights with the same image,
wheels and GPU class — `cupy-cuda12x` and its `nvidia-*` dependencies are
about a gigabyte, and how long that takes is not a property of the
workload. `cost.OVERHEAD_OBSERVED_RANGE_S` records the spread:

| phase | observed range |
|:--|:--|
| `accept` | 1.7 – 2.9 s |
| `bootstrap` | 6 – 305 s |
| `teardown` | 1.1 – 4.1 s |

This is why the controller waits on bootstrap PROGRESS rather than on a
deadline: a fixed timeout cannot tell a slow install from a dead pod, so
it calls both dead.

**Two clocks.** Pod-side stage intervals and controller-side instants are
reported separately in every receipt. The one interval that spans both —
provisioning — is reported twice: raw under `cross_clock`, and corrected
by the MEASURED offset under `synchronised`, with its uncertainty. When the
pod's `/_clock` cannot be read, only the raw figure appears.

**Spec sheets are not throughput.** The preregistration assumed 60% of
spec-sheet FP32 peak for every card. The A4000 delivered 62%; the L4
delivered **35%**, and the preregistered L4 campaign estimate was 37% low.
The scout caught it: the calibrated estimate was within 5.4% of the
measured cost. This is the whole case for scouting, on one card.

## What overhead does to a short job

27 seconds is fixed, so cost per unit of work falls hyperbolically with
workload length. On an A40 at $0.49/h:

| workload | total | cost | overhead share |
|--:|--:|--:|--:|
| 10 s | 37 s | $0.0050 | **73%** |
| 60 s | 87 s | $0.0118 | 31% |
| 300 s | 327 s | $0.0445 | 8% |
| 1,800 s | 1,827 s | $0.2487 | 1% |
| 14,400 s | 14,427 s | $1.9637 | <1% |

The operational consequence is unchanged and now cheaper to state:
**batch small experiments.** Ten 10-second probes as separate pods cost
$0.050 and spend $0.037 of it on overhead. The same ten inside one pod cost
$0.0173 and spend $0.0037 on overhead.

## The cheaper GPU often wins

A quoted hourly rate is not the economics. On a short job, a slower
cheaper card can finish for less money even though it takes longer:

| | A40 @ $0.49/h | RTX A4000 @ $0.17/h |
|:--|--:|--:|
| workload | 30 s | 60 s (2× slower) |
| total with overhead | 65 s | 95 s |
| **cost** | **$0.0089** | **$0.0045** |

A caveat Iteration 1 supplied the hard way: the cheapest card is also the
one most likely to have no capacity. Declare `gpu.alternatives` in the
order you would rather have them, because a projection for a GPU you
cannot obtain is not a projection.

That is a test, not an anecdote:
`test_cheaper_gpu_can_win_on_a_short_job`. Pick the cheapest GPU that
fits the memory requirement, and let `estimate` arbitrate.

Quoted rates in `cost.HOURLY_USD` are A40 $0.49, RTX A4000 $0.17,
RTX A5000 $0.26, RTX 4090 $0.34, L4 $0.43, default $0.49. **The provider
is authoritative, not this table.**

## Measured throughput, in Aether's own denominator

| campaign | lattice | site-ticks/s | $/1e9 site-ticks |
|:--|:--|--:|--:|
| AETH-01 First Light | 4096² | — | 0.0039 |
| AETH-02 trajectories (in flight) | 2048² | 3.24e7 | 0.0042 |

The AETH-02 figure is from 3,918 s of the run in progress: 121 samples
at 250 ticks each, on a 2048² lattice, with the causal-edge observer and
periodic graph analysis active. Provisional until the receipt lands.

The ~8% gap between the two is **not** a clean measurement of the
observer's cost: the lattice size differs, so observer overhead and
scale effects are confounded. It bounds the instrumentation at "less
than about 8% at this size", which is enough to know the observer is not
a significant tax, and not enough to say what it actually costs.

A useful conversion: **$1 buys roughly 240e9 site-ticks** at the
instrumented rate.

Observed billing rate over the same window: **$0.4897/h** against an
A40 list price of $0.49/h. The controller's spend counter tracks the
list rate to within 0.1%. That makes it a good *estimator* and still not
reconciliation — see below.

## Your own denominator

Declare `work_units` and every projection reports cost in your
vocabulary:

```json
"work_units": {"name": "candidates", "estimate": 50000}
```

gives `usd_per_unit` and `units_per_usd` alongside the dollar figures.
Aether counts site-ticks; that is Aether's business and the platform
does not impose it on anyone.

## Estimate versus reconciliation

`cost.actual()` reports `usd_estimated` from measured wall time at a
quoted rate, and always sets `billing_reconciled: false`. Its `basis`
field says so in words.

This holds even though the rate tracked list price to 0.1% above. An
accurate estimate is still an estimate: it cannot see a minimum billing
increment, a storage charge, a partial-hour rounding rule, a credit, or
a pod that kept billing after we stopped watching. Only provider billing
data, recorded in `cleanup.billing_evidence` with its source and
retrieval time, may set that flag true. `receipt.validate()` refuses any
receipt that claims otherwise, including one that tries to smuggle the
claim in through the cost block.

## Budgeting a campaign

1. `estimate` with a realistic `--workload-seconds`, not `max_runtime_s`.
2. Add the overhead **per pod**, not per campaign — three pods pay 234 s.
3. Hold back a reserve. AETH-02 held ~$0.33 of $3, unspent unless a
   specific discriminating counterfactual appeared.
4. Set `max_runtime_s` as a real bound. It is the mechanism that stops a
   hung workload from becoming an unbounded bill.
