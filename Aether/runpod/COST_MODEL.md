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

## Overhead, with provenance

Defaults in `cost.OVERHEAD_S`, each labelled measured or inferred so a
later reader can tell an observation from an estimate:

| phase | seconds | provenance |
|:--|--:|:--|
| `accept` | 1 | **measured** — create → 201 on AETH-02 launches |
| `provision` | 20 | *inferred* from canary-ready latency; not isolated |
| `bootstrap` | 40 | *inferred* from the same interval; not yet decomposed |
| `canary` | 12 | **measured** — receipt `gpu_kernel_seconds` 10.95–12.94 |
| `teardown` | 5 | **measured** — terminate ACK → absence confirmed |
| **total** | **78** | |

`provision` and `bootstrap` are inferred from a single interval that has
not been decomposed, so they are 60 of the 78 seconds and the least
trustworthy part of the model. Iteration 3 of the engineering ladder
separates them. They are updated **only from real runs**; nobody tunes
them to make a projection look better.

## What overhead does to a short job

78 seconds is fixed, so cost per unit of work falls hyperbolically with
workload length. On an A40 at $0.49/h:

| workload | total | cost | overhead share |
|--:|--:|--:|--:|
| 20 s | 98 s | $0.0133 | **80%** |
| 60 s | 138 s | $0.0188 | 57% |
| 300 s | 378 s | $0.0515 | 21% |
| 1,800 s | 1,878 s | $0.2556 | 4% |
| 14,400 s | 14,478 s | $1.9706 | 0.5% |

The operational consequence: **batch small experiments.** Ten 60-second
probes as separate pods cost $0.19 and spend $0.11 of it on nothing. The
same ten inside one pod cost $0.092 and spend $0.011 on overhead.

## The cheaper GPU often wins

A quoted hourly rate is not the economics. On a short job, a slower
cheaper card can finish for less money even though it takes longer:

| | A40 @ $0.49/h | RTX A4000 @ $0.17/h |
|:--|--:|--:|
| workload | 30 s | 60 s (2× slower) |
| total with overhead | 108 s | 138 s |
| **cost** | **$0.0147** | **$0.0065** |

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
