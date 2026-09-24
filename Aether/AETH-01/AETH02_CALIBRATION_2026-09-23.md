# AETH-02 calibration -- the cost curve, and a budget problem

Instance Aether[buckkeep-7a10ca4b]. Run
`aeth02-20260924T011512Z-7e729e54`, pod `qtyu4j6p6dgozr`, one A40 SECURE
at $0.49/hr, pinned to commit `20b69fc30`. Pod wall **1,300 s**, cost
**$0.177**. Canary PASS 300/300 backend cupy before any science.
Terminated `ACK_204`, absence confirmed. 4 of 4 phases completed.

Raw rows: `evidence/2026-09-23_aeth02_calibration/calibration.jsonl`.

This run existed to learn the economics before committing to the long
trajectory. It did that, and the answer changes the plan.

## 1. The cost curve, measured

| phase | size | ticks | s/tick | sites/sec | USD/1e9 site-ticks | phase $ |
|:--|--:|--:|--:|--:|--:|--:|
| econ_1024 | 1024 | 300 | 0.0333 | 31,485,573 | 0.0043 | $0.0030 |
| econ_2048 | 2048 | 300 | 0.1221 | 34,359,738 | 0.0040 | $0.0058 |
| econ_4096 | 4096 | 300 | 0.4755 | 35,286,827 | 0.0039 | $0.0221 |
| probe_4096 | 4096 | 2000 | 0.4755 | 35,285,748 | 0.0039 | $0.1385 |

Throughput saturates by 2048^2 and the marginal cost flattens at
**$0.0039 per billion site-ticks**, i.e. **$1 buys about 259 billion
site-ticks**. Causal-graph observation costs **2.5% of throughput**
(35.3 M vs First Light's 36.2 M sites/sec) and +10.00 bytes/site.

Reproducibility check: `econ_4096` and `probe_4096` are the same
configuration at 300 and 2000 ticks and agree to 0.0001 s/tick.

## 2. THE BUDGET PROBLEM the calibration was for

Track 1 as the directive literally specifies it -- B_balanced at 4096^2
for 50,000 ticks -- costs:

    50,000 x 0.4755 s = 23,775 s = 6.60 h x $0.49 = **$3.24**

**That does not fit in $3.** Nothing was wrong with the estimate in the
directive; 0.47 s/tick was the pre-observation figure and the arithmetic
simply lands just over the line.

What $3 does buy, measured:

| option | cost | site-ticks | notes |
|:--|--:|--:|:--|
| 4096^2 x 50,000 | $3.24 | 839e9 | **over budget** |
| 4096^2 x 46,000 | $2.98 | 772e9 | fits, truncates Track 1 by 8% |
| 2048^2 x 50,000 | $0.83 | 210e9 | fits, and **3 replicates fit in $2.49** |
| 1024^2 x 50,000 | $0.23 | 52e9 | 12 replicates fit |

The directive's own priority settles it: *"Prioritize time and
replicated trajectories over maximum lattice size. 4096^2 is likely
sufficient for the main long-duration work unless measurement shows
otherwise."* Measurement has shown otherwise, and the stated priority is
time and replication. **Three 2048^2 trajectories at the full 50,000
ticks for $2.49 is the directive-conformant read**, and it buys the
cross-seat replication First Light showed to be near-exact rather than
one truncated trajectory with no replicate at all.

## 3. GPU memory over lifetime -- the First Light gap, closed

| phase | device used | pool used | pool total |
|:--|--:|--:|--:|
| econ_1024 | 432.2 MiB | 25.0 | 158.0 |
| econ_2048 | 906.2 MiB | 100.0 | 632.1 |
| econ_4096 | 2,802.2 MiB | 400.0 | 2,528.1 |
| probe_4096 | 2,802.2 MiB | 400.0 | 2,528.1 |

Within the 2,000-tick probe: 2,674.2 MiB at tick 1, 2,802.2 MiB from
tick 101, and then **exactly flat to tick 2,000**. The +128 MiB is
one-time pool growth, not creep. **No memory creep.**

2,802 MiB at 4096^2 is consistent with the memory-wall pool model
(2,318 MiB) plus observation (+160 MiB) plus graph state (+294 MiB for
run-length counters and the realized map).

## 4. OBSERVED -- the causal graph at 4096^2

Direct measurements from `probe_4096`. No interpretation in this section.

    tick     edges   cycle_nodes    activity  template_chg  run>=64
       1   8,049,939    995,716      0.4122     0.38271          0
     101   4,668,775    102,918      0.2847     0.07228  2,969,795
     501   3,208,470     51,858      0.1943     0.06209    352,695
    1001   3,189,208     49,562      0.1933     0.06170    305,145
    2000   3,173,389     48,624      0.1924     0.06000    260,585

- **`partial_function_max_outdegree` was 1 at every sample.** The
  out-degree-1 property the graph layer rests on held on real hardware
  at 16.7 M sites, not only in tests.
- **Cycles exist and stabilize.** Cycle nodes fall from 995,716 to
  ~48,600 and flatten -- about **0.29% of the lattice sits on a cycle**
  of the realized map at steady state.
- **`run_max` equals the tick number at every single sample** (1, 101,
  ..., 2000). Some edge has held the same winner since tick 1, so
  **persistence is censored by the run length** and the true timescale
  is not visible in 2,000 ticks.
- 260,585 edges had held for >= 64 consecutive ticks at tick 2,000,
  declining from 2,969,795 at tick 101: persistent edges erode slowly
  rather than either vanishing or locking.
- Activity 0.1924 and template change 0.0600 at tick 2,000 reproduce
  First Light's B_balanced (0.1919, 0.0597 at tick 5,000) -- an
  independent cross-run agreement, on a different run, with the
  observer attached.

### Contests are rare

| field | targets with 1 contender | with >=2 | share contested |
|:--|--:|--:|--:|
| opcode | 775,157 | 13,754 | 1.74% |
| arg0 | 685,856 | 12,552 | 1.80% |
| arg1 | 692,705 | 11,589 | 1.65% |
| payload | 750,204 | 13,757 | 1.80% |
| energy | 216,595 | 1,220 | 0.56% |

### Most causal edges move no information

| field | edges | changed target state | share |
|:--|--:|--:|--:|
| opcode | 788,911 | 169,850 | 21.5% |
| arg0 | 698,408 | 152,377 | 21.8% |
| arg1 | 704,294 | 152,644 | 21.7% |
| payload | 763,961 | 169,086 | 22.1% |
| **energy** | 217,815 | 192,685 | **88.5%** |

## 5. INTERPRETATION

Weaker than section 4 and to be attacked separately.

**I was wrong about arbitration.** In the preregistration I wrote that
the realized map changes tick to tick "because arbitration
re-randomizes each tick since the priority hash includes the tick". The
measurement says contests touch only **1.7%** of edges. For the other
98.3% there is a single contender and the winner is forced, so the
realized map is essentially the proposed map and its changes come from
template bytes being overwritten, not from arbitration churn. The
preregistration's section 2 is annotated accordingly; the original text
stays visible.

**The persistent structure looks static, not stateful.** Roughly 78% of
template edges rewrite a value that is already there. A cycle made of
same-value rewrites is a fixed pattern being redundantly refreshed, not
a circuit carrying state. Energy edges are the opposite (88.5% change
something), which is consistent with energy being the one field with a
live conserved quantity flowing through it.

That gives Track 3 its sharp form, and it is cheap to ask: **are the
~48,600 cycle nodes carrying CHANGED edges, or same-value rewrites?**
A persistent cycle of same-value rewrites would be a
`PERSISTENT_SUBGRAPH_CANDIDATE` by the preregistered definition and
still not be circuitry in any useful sense. Nothing in this run
distinguishes the two yet.

## 6. What this run does NOT establish

- Nothing about state dependence: no counterfactual was run.
- No candidate was assigned any label. 48,600 cycle nodes is a count,
  not a set of identified subgraphs.
- Persistence is right-censored at 2,000 ticks.
- Long-horizon CPU/GPU determinism is still open; only the 300-case
  canary and the frozen digest gate have run.
- The windows were captured but not analyzed here.

## 7. Two reporting bugs in my own output, fixed

1. The per-phase cost field was named `usd_per_1k_world_ticks` while
   computing USD per 1e9 site-ticks -- a millionfold misread waiting to
   happen. Renamed `usd_per_1e9_site_ticks`, with `usd_per_tick` added
   beside it. The committed rows carry the old name; this document is
   the correction.
2. The orchestrator, generated from the First Light one, kept its
   `aeth01_fl_` artifact prefix, so AETH-02 artifacts were written under
   First Light's names. Now `aeth02_`.

## 8. Next

Operator decision on section 2. My recommendation is three 2048^2
trajectories at 50,000 ticks for $2.49, because it satisfies the
directive's stated priority (time and replication over size), it leaves
Track 1 un-truncated, and First Light showed replication at these scales
to be near-exact so a single trajectory has no way to expose a seed
artifact.

Spent to date on AETH-02: **$0.177 of $3.**
