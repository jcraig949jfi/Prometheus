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

Defaults in `cost.OVERHEAD_S`, **measured by Iteration 1 through the
platform's own launch path** on an RTX 4090 (receipt
`hello-gpu-20260924T212427Z`):

| phase | seconds | provenance |
|:--|--:|:--|
| `accept` | 1.8 | **measured** — create call 1.745–2.947 s |
| `provision` | 24.0 | **UPPER BOUND** — not isolated; see below |
| `bootstrap` | 6.0 | **measured** on the pod's clock; observed up to 305 s |
| `canary` | 1.0 | **measured** for `import cupy`; a property of your canary |
| `teardown` | 2.2 | **measured** — terminate ACK to absence confirmed |
| **total** | **35.0** | |

The previous values totalled 78 s and were inferred from orchestrator
timings rather than measured. **They were 2.3× too high**, and the error
sat almost entirely in the two terms that had been marked *inferred*.
Marking them was right; it was not enough, because nothing forced them to
be measured.

**`provision` is a bound, not a measurement.** 31.4 s elapsed from
create-accepted to first telemetry, of which 7.0 s is accounted for on the
pod's own clock. Up to 15 s of the remainder is the controller's poll
interval, so the true value is between about 9 s and 24 s. A shorter poll
interval would tighten it.

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
provisioning — is labelled `cross_clock`, because the two machines' clocks
are not synchronised and that offset is not measured here.

## What overhead does to a short job

35 seconds is fixed, so cost per unit of work falls hyperbolically with
workload length. On an A40 at $0.49/h:

| workload | total | cost | overhead share |
|--:|--:|--:|--:|
| 10 s | 45 s | $0.0062 | **78%** |
| 60 s | 95 s | $0.0130 | 37% |
| 300 s | 335 s | $0.0456 | 10% |
| 1,800 s | 1,835 s | $0.2498 | 2% |
| 14,400 s | 14,435 s | $1.9648 | <1% |

The operational consequence is unchanged and now cheaper to state:
**batch small experiments.** Ten 10-second probes as separate pods cost
$0.061 and spend $0.048 of it on nothing. The same ten inside one pod cost
$0.0182 and spend $0.0048 on overhead.

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
