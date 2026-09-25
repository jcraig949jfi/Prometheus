# AETH-02 NATIVE CIRCUITRY 01 — three long trajectories

Date: 2026-09-24
Semantics: `aeth01.v1`, unchanged. No new semantics id.
Preregistration: `NATIVE_CIRCUITRY_01_PREREGISTRATION_2026-09-23.md`
Calibration: `AETH02_CALIBRATION_2026-09-23.md`
Run: `aeth02-20260924T070408Z-efe7be17`, pinned to `f4fb349b849e`

> **AMENDED 2026-09-24, and closed.** Two changes were directed after this
> report was written, and both narrow it. (1) The four-part statement in
> §7 is a list of useful evidentiary dimensions, **not** a definition of
> circuitry and **not** jointly necessary. (2) The negative conclusion is
> narrow: no evidence was found that the measured persistent-edge and
> cycle structures perform a demonstrated nontrivial function **under the
> assays run**. It does not say Aether contains no possible circuitry.
> The preregistered falsifiers H1–H4 were then run at zero dollars; see
> `AETH-02_CLOSE_2026-09-24.md`, which supersedes §4 and §7 where they
> differ.

The question this round was set to answer: **does `aeth01.v1` spontaneously
produce persistent functional circuitry?**

The short answer, **for the structures measured and the assays run**, is
**no**, and the interesting part is what it produces instead. Persistent structure exists, is reproducible across seeds to
four decimal places, and is quantitatively well described — but what
makes an edge persist is the absence of anything opposing it, not any
function it performs.

---

## 1. RUN INTEGRITY

| | |
|:--|:--|
| worlds | 3 independent B-balanced trajectories, 2048 × 2048 |
| ticks planned | 50,000 each |
| ticks completed | 50,000 / 50,000 / ~47,000 (truncated) |
| stop reason | controller dollar ceiling, $2.608 ≥ $2.60 after 19,159 s |
| GPU canary | PASS |
| backend | CuPy on one A40 48 GB, SECURE |
| pod | `ns96dzh9bq7ynx`, terminate `ACK_204`, absence confirmed, `ACTIVE_POD_COUNT 0` |
| independent recheck | a fresh inventory read after the run reported `active: 0` |
| billing reconciliation | **NOT performed.** $2.608 is wall time at a quoted rate. |

Seeds and initial-state digests, all `instrument_class: SPONTANEOUS`
(regimes 1–2 only, so no seeded instrument can be present):

| phase | lattice seed | init digest | realised write density | final digest |
|:--|:--|:--|--:|:--|
| 0 | 1543575297 | `8a319e852f8a3337…` | 0.499842 | `50c6662cbce2d818…` |
| 1 | 1543575298 | `9a8d74256b09003d…` | 0.500103 | `1b3a354f327a8c38…` |
| 2 | 1543575299 | `fb38a5e4e0f2e0a9…` | 0.500052 | (truncated at 45,001: `87b39e0ecaa228fa…`) |

**Structural invariant held everywhere.** Maximum out-degree of the
realised write graph was **1** at every one of 296 measurements and at
every phase end. Each (site, field) receives at most one winning write
per tick, which is what makes the graph a partial function and makes
"every component is one cycle with in-trees" a theorem rather than a
finding. Nothing below treats it as a discovery.

**Observer consistency check, and this one is a real check.** For every
template field at every sample, the number of sites whose stored value
differed from the previous tick equals exactly the number of edges the
observer classified `STATE_CHANGING` — ratio 1.0000 at every tick of
every phase. The observer's edge set therefore accounts for every
template-field change in the lattice, no more and no less. The observer
is causally downstream: it reads the kernel's own winner arrays and
changes no state.

### Cost

| | phase 0 | phase 1 |
|:--|--:|--:|
| wall | 6,525.3 s | 6,517.7 s |
| spend | $0.88816 | $0.88713 |
| throughput | 3.3697e7 site-ticks/s | 3.3697e7 site-ticks/s |
| per 1e9 site-ticks | $0.004039 | $0.004039 |
| median tick | 0.124473 s | 0.124472 s |

Preregistered $0.83 per trajectory; measured $0.888. **My projection was
7.2% low**, which is why the third trajectory met the ceiling instead of
finishing. Recorded in the calibration ledger; the cause was a
throughput figure carried from an uninstrumented 4096² run into an
instrumented 2048² one without re-measuring.

---

## 2. OBSERVED

### 2.1 The system stops changing after about a thousand ticks

Every bulk quantity reaches a stationary value by roughly tick 1,000 and
then moves by less than one part in a thousand over the following 49,000
ticks. Phase 0:

| tick | write density | active | starved | change rate | H(opcode) | zlib ratio | energy Gini |
|--:|--:|--:|--:|--:|--:|--:|--:|
| 1 | 0.451564 | 0.412055 | 0.039508 | 0.275606 | 5.3776 | 0.9495 | 0.364220 |
| 251 | 0.428187 | 0.205110 | 0.223077 | 0.245474 | 5.5563 | — | 0.578870 |
| 1,001 | 0.425546 | 0.193158 | 0.232388 | 0.185534 | 5.5763 | — | 0.586713 |
| 5,001 | 0.424069 | 0.191792 | 0.232278 | 0.184792 | 5.5874 | 0.9284 | 0.588166 |
| 25,001 | 0.422833 | 0.191266 | 0.231567 | 0.184726 | 5.5968 | 0.9287 | 0.587172 |
| 50,000 | 0.422507 | 0.191052 | 0.231455 | 0.184610 | 5.5992 | 0.9288 | 0.587116 |

Write density is still declining at tick 50,000, at about 1e-7 per tick.
Extrapolating that rate is not justified by the data; what the data
support is that the state is stationary to four decimal places over the
last 45,000 ticks.

**The three seeds are the same system.** At matched ticks the three
trajectories agree to four decimal places on every bulk quantity. At tick
50,000 (46,751 for phase 2):

| | phase 0 | phase 1 | phase 2 |
|:--|--:|--:|--:|
| write density | 0.422507 | 0.422848 | 0.422729 |
| change rate | 0.184610 | 0.184616 | 0.184682 |
| edges | 788,606 | 789,241 | 789,635 |
| energy Gini | 0.587116 | 0.587403 | 0.587181 |
| H(opcode) bits | 5.5992 | 5.5966 | 5.5975 |

This is the round's strongest single result. Three independent initial
states, 50,000 ticks, no shared randomness beyond the semantics, and the
stationary state is reproducible to four decimal places.

### 2.2 Energy concentrates and then holds

Total energy falls from 5.238e8 to 3.518e8 in the first ~500 ticks and
then holds. Gini rises 0.364 → 0.587. The fraction of sites at zero
energy rises 0.047 → 0.2384; saturated sites stay at 0.0077. Mean site
energy settles at 83.87 of 255.

23.1% of sites hold a write opcode but cannot afford `write_cost`. That
starved fraction is stable and is the larger part of the drop in activity
density (0.412 → 0.191).

### 2.3 No spatial structure develops

Nearest-neighbour autocorrelation is small and **negative** at every
sample and grows slightly more negative over the trajectory:

| tick | opcode | payload | energy |
|--:|--:|--:|--:|
| 1 | −0.023956 | — | −0.039206 |
| 50,000 | −0.039206 | — | −0.078203 |

Neighbouring sites are very slightly anti-correlated. Nothing resembling
domain formation, clustering or pattern growth appears at any point.

Compressibility moves the wrong way for structure: the zlib ratio falls
from 0.9495 to 0.9288, i.e. the lattice becomes marginally *more*
compressible, and stays at 0.9288 for 45,000 ticks. Payload entropy is
7.9999 of 8 bits throughout. All 256 opcode values remain present at
every sample; the modal opcode holds 42.25% of sites.

### 2.4 The write graph: 790,000 edges, and most of them write what is already there

At stationarity, ~788,600 winning writes land per tick out of 20,971,520
(site, field) slots — 3.76% occupancy. Per field:

| field | edges | share |
|:--|--:|--:|
| opcode | 198,562 | 25.2% |
| arg0 | 171,944 | 21.8% |
| arg1 | 174,218 | 22.1% |
| payload | 189,666 | 24.1% |
| energy | 54,216 | 6.9% |

**The four-way classification, all fields pooled, phase 0:**

| tick | edges | STATE_CHANGING | SAME_VALUE_UNCONTESTED | SAME_CONTESTED_ALT_CHANGE | SAME_CONTESTED_NO_ALT_CHANGE |
|--:|--:|--:|--:|--:|--:|
| 1 | 2,011,842 | 99.488% | 0.493% | 0.019% | 0.000% |
| 251 | 846,807 | 45.794% | 53.612% | 0.584% | 0.010% |
| 501 | 802,067 | 27.777% | 71.537% | 0.649% | 0.038% |
| 5,001 | 791,877 | 27.184% | 72.146% | 0.633% | 0.038% |
| 25,001 | 789,244 | 27.253% | 72.071% | 0.637% | 0.039% |
| 50,000 | 788,606 | 27.079% | 72.251% | 0.627% | 0.043% |

Phases 1 and 2 agree to within 0.1 percentage point at every tick.

The composition is set within 500 ticks and then does not move. Note the
first row: from a uniformly random start almost every write changes
something, and within 500 ticks three quarters of writes are writing a
value that is already present.

**Per field at the last sample of each phase** — the energy field behaves
completely differently from the four template fields:

| field | STATE_CHANGING | SAME_UNCON | SAME_CON_ALT | SAME_CON_NO_ALT |
|:--|--:|--:|--:|--:|
| opcode | 21.90% | 77.42% | 0.678% | 0.011% |
| arg0 | 22.37% | 76.85% | 0.679% | 0.109% |
| arg1 | 21.94% | 77.42% | 0.621% | 0.014% |
| payload | 23.94% | 75.32% | 0.678% | 0.057% |
| **energy** | **88.49%** | **11.40%** | 0.111% | 0.000% |

Energy writes are transfers of a computed amount, so they almost always
change the target. Template writes are copies, and by stationarity most
copies are redundant.

### 2.5 Contests are rare, and when they happen they matter

Same-value contested edges are 0.67% of all edges (5,284 of 788,606 in
phase 0; 0.664% and 0.680% in phases 1 and 2). Of those, in **93.5%** the
losing alternative would have changed the target's state, and in 6.5% it
would not.

So arbitration is almost never called upon, and when it is, it is almost
always excluding a state change. Slot usage is close to uniform — the
spread between the most- and least-used of the four neighbour slots is
0.22%–1.91% of the mean, per field. Fan-in is 0 or 1 at 98.4% of
(site, field) slots, 2 at 1.6%, 3 at ~20 per million, and 4 at one
measured instance in the whole run.

### 2.6 Persistent structure exists, and has two distinct components

Edge run-lengths at the last sample of each phase (phase 0):

| field | edges present | ever repeating | max run | mean run | ≥16 ticks | ≥64 ticks |
|:--|--:|--:|--:|--:|--:|--:|
| opcode | 198,562 | 173,446 | **50,000** | 469.10 | 19.9% | 6.96% |
| arg0 | 171,944 | 150,524 | **50,000** | 704.50 | 22.3% | 9.19% |
| arg1 | 174,218 | 152,861 | **50,000** | 666.41 | 22.1% | 8.91% |
| payload | 189,666 | 165,937 | **50,000** | 667.18 | 22.3% | 9.12% |
| energy | 54,216 | 10,872 | 50,000 | 7.47 | 0.48% | 0.11% |

`max run = 50,000` means at least one edge was continuously present from
tick 1 to tick 50,000 in every template field.

**The persistent cohort is a fixed size, not a growing one.** The count of
edges with run ≥ 64 is flat from tick 2,500 onward (opcode: 14,449 at
2,501; 13,952 at 5,001; 13,934 at 25,001; 13,828 at 50,000), while mean
run grows linearly with tick. That combination separates two components.
Fitting `run_mean(T) = f·T + (1−f)·m` over T ≥ 5,000:

| field | f (unbroken since tick 1) | count | m (turnover mean run) |
|:--|--:|--:|--:|
| opcode | 0.00851 / 0.00885 / 0.00877 | ~1,690–1,750 | 44.7 / 44.6 / 45.0 |
| arg0 | 0.01312 / 0.01331 / 0.01304 | ~2,240–2,290 | 50.7 / 50.4 / 49.9 |
| arg1 | 0.01232 / 0.01226 / 0.01218 | ~2,120–2,150 | 50.8 / 49.9 / 49.9 |
| payload | 0.01226 / 0.01217 / 0.01278 | ~2,325–2,445 | 53.6 / 53.5 / 53.4 |
| energy | 0.000113 / 0.000058 / 0.000073 | **3–6** | 2.0 / 2.0 / 2.1 |

(three values per row = the three phases)

So about **1.2% of template-write edges — roughly 8,400 per trajectory —
have been continuously present since tick 1**, and the remaining 98.8%
turn over with a mean run of 45–54 ticks. The energy field has
essentially no persistent component at all: three to six unbroken edges
out of 54,000, and a mean run of two ticks.

**Composition of the persistent cohort** (run ≥ 64), at the last sample:

| | phase 0 | phase 1 | phase 2 |
|:--|--:|--:|--:|
| persistent edges | 62,516 (7.93%) | 62,620 (7.93%) | 62,535 (7.92%) |
| STATE_CHANGING | 20.61% | 20.29% | 20.34% |
| SAME_VALUE_UNCONTESTED | 79.39% | 79.71% | 79.66% |
| SAME_CONTESTED_ALT_CHANGE | 1 edge | 2 edges | 2 edges |
| SAME_CONTESTED_NO_ALT | 0 | 0 | 0 |

Persistent edges are *more* same-value than the lattice as a whole
(79.4% vs 72.3%), but one in five persistent edges changes its target's
value every tick — a stable channel carrying changing data.

### 2.7 Persistence requires the absence of a contest — with no exceptions

From the 256 × 256 window samples (2,500 edges each, opcode field only):
across **ten windows and 1,754 sampled persistent edges, the number with
two or more contenders was exactly zero**, against a contested rate of
1.24%–2.28% among all sampled edges in the same windows.

| window | persistent edges | contested among them | contested rate, whole window |
|:--|--:|--:|--:|
| ph0 t25001 A | 159 | 0 | 0.0156 |
| ph0 t25001 B | 177 | 0 | 0.0168 |
| ph0 t50000 A | 142 | 0 | 0.0156 |
| ph0 t50000 B | 182 | 0 | 0.0164 |
| ph1 t25001 A | 189 | 0 | 0.0172 |
| ph1 t25001 B | 199 | 0 | 0.0168 |
| ph1 t50000 A | 177 | 0 | 0.0152 |
| ph1 t50000 B | 176 | 0 | 0.0124 |
| ph2 t25001 A | 167 | 0 | 0.0172 |
| ph2 t25001 B | 186 | 0 | 0.0228 |
| **pooled** | **1,754** | **0** | ~0.0166 |

If persistence and contest were independent, the expected number of
contested persistent edges would be about 29, and the chance of seeing
zero is of order 1e-13. This is not a marginal effect.

A size-matched random-subset control, drawn instead of using the whole
window, gives the same answer with a wider spread (0.55%–4.19%); the
whole-window rate is quoted because it is what the committed reduction
computes and is the less arbitrary comparison.

### 2.8 Persistent edges are not spatially organised

Mean nearest-neighbour Chebyshev distance among persistent targets,
against a size-matched random control from the same window:

ratios 1.012, 1.039, 0.894, 1.010, 1.000, 0.998, 1.040, 1.038, 1.033,
0.934 — mean 0.999, no ratio outside [0.89, 1.04].

The persistent set is spatially indistinguishable from a random subset of
the same size. There are no localised assemblies, no clusters, no
neighbourhoods of persistent structure. Slot usage among persistent edges
is also near-uniform, so they do not share a preferred direction.

### 2.9 Cycles

Cycle membership was measured every 500 ticks by pointer doubling
(22 doublings, ⌈log₂ 4,194,304⌉).

| tick | mapped nodes | cycle nodes | share | retention over 500 ticks |
|--:|--:|--:|--:|--:|
| 1 | 2,011,842 | 248,344 | 12.344% | — |
| 501 | 802,067 | 12,836 | 1.600% | 0.5644 |
| 1,001 | 797,001 | 12,534 | 1.573% | 0.2176 |
| 5,001 | 791,877 | 12,060 | 1.523% | 0.2234 |
| 25,001 | 789,244 | 11,548 | 1.463% | 0.2105 |
| 50,000 | 788,606 | 11,410 | 1.447% | 0.2195 |

Across 100 measurements per phase, cycle-node count ranged 11,218–11,692
after the transient and retention held at 0.219 ± 0.006, never once zero.
Phases 1 and 2 match (retention means 0.2185, 0.2178).

So roughly 1.45% of write-graph nodes lie on a cycle, the aggregate is
stable, and about 22% of cycle membership carries across a 500-tick gap.

**On-cycle edges are structurally different from the rest.** Where
measured, on-cycle edges are 63–65% `STATE_CHANGING` against 27% in the
lattice as a whole — a 2.4× enrichment, consistent across all three
phases at every measured tick.

### 2.10 Where state change actually comes from

The classifier scores an edge by its realised outcome: `STATE_CHANGING`
means the target's value after the tick differs from before, so a
same-value proposal that the perturbation operator then flipped is
counted as changing. `aeth01.v1` applies a single-bit perturbation to the
stored value at every site where a write landed, with probability
`mut_numer / 2^32 = 0.100000`, and that draw is independent of whether
the proposal differed.

Writing `p_s` for the fraction of landed writes proposing a value
identical to the target's current one:

    observed SAME_VALUE = p_s (1 − q)
    observed CHANGING   = (1 − p_s) + p_s q

Solving, over the four template fields at the last sample:

| phase | template edges | p_s (redundant proposal) | perturbation share of all change |
|--:|--:|--:|--:|
| 0 | 734,390 | 0.8606 | 38.17% |
| 1 | 735,061 | 0.8593 | 37.91% |
| 2 | 735,885 | 0.8599 | 38.04% |

**86% of landed template writes propose a value the target already holds,
and roughly 38% of all template-field state change is the perturbation
operator acting through a redundant copy channel rather than any transfer
of information.**

This is arithmetic on the measured classification plus the known
perturbation rate, not an independent measurement. Its one assumption —
that the perturbation draw is independent of whether the proposal
differed — is true by construction in the kernel.

---

## 3. INTERVENTION RESULTS

**None. No intervention was performed this round.**

Track 4 was conditional on a discriminating counterfactual appearing, and
the budget reserve was to be held otherwise. A counterfactual was
identified (§6) but not run, and the $2.608 spent bought observation
only. Nothing in §2 rests on an intervention, and nothing in §4 should be
read as if it did.

---

## 4. INTERPRETATION

**There is persistent structure. It is not circuitry.**

Structure that persists is real and measurable: ~1.2% of template-write
edges hold unbroken for 50,000 ticks, a stable cohort of ~62,500 edges
holds for at least 64 ticks, and ~11,400 nodes sit on cycles with 22%
membership retention across 500 ticks. None of that is noise, and it
reproduces across three independent seeds.

What it is not is functional. The decisive observation is §2.7: of ~1,750
sampled persistent edges, **not one had a competitor**. Persistence in
`aeth01.v1` is what happens to a write channel that nothing contests.
The mechanism is visible in the semantics — arbitration priority is
hashed with the tick, so it rerolls every tick, and a contested channel
therefore changes winner pseudorandomly and cannot accumulate a run. An
edge persists exactly when it is unopposed, and being unopposed is a
property of the neighbourhood's opcode layout, not of anything the edge
does.

**Same-value writes are not functionless, and the reason is specific.**
The preregistered rule was not to equate a same-value write with no
function, and the semantics say why that rule was right. A landed write
has one consequence beyond its value: it makes the target eligible for
perturbation, because the perturbed value is stored only where a write
landed. The energy cost is paid for *being active*, independent of
whether the write landed or changed anything, so the cost is not
attributable to the write. That leaves perturbation eligibility as the
sole consequence channel of a same-value uncontested write — and it is a
real one. The 72% same-value majority is precisely what allows
perturbation to reach ~8.6% of landed writes and supply 38% of all state
change. The redundant copy channel is the noise channel.

**The system is stationary, not developing.** By tick 1,000 every bulk
measure is fixed to four decimal places and stays fixed for 49,000 more
ticks. Compressibility falls slightly and then holds; spatial
autocorrelation is small, negative, and drifts further negative; opcode
entropy rises by 0.02 bits over 49,000 ticks and flattens. The persistent
cohort does not grow: its size is set by tick 2,500 and constant
thereafter. A 50,000-tick trajectory and a 2,500-tick trajectory would
have supported the same conclusions about the stationary state — which is
itself worth knowing before the next round is costed.

**Energy is not routed.** The energy field has 3–6 unbroken edges out of
54,000 and a mean run of two ticks. If anything in this system were
maintaining a resource pathway, this is where it would show, and it does
not. Energy concentrates (Gini 0.364 → 0.587) by ordinary accumulation,
not by transport structure.

**The cycle enrichment is the one result that resists a flat reading.**
On-cycle edges are 2.4× more likely to change their target's state than
edges at large, consistently, in all three phases. Something distinguishes
cycle-resident edges. What that something is cannot be settled from
observation alone: the plainest candidate is selection, in the arithmetic
sense that an edge whose writes never change anything gives its target no
way to point back, so a stable same-value edge is less likely to close a
loop. That is a structural constraint, not a function.

**Verdict.** On the preregistered question, the answer is negative, and
the scope of that negative matters. `aeth01.v1` under B-balanced
parameters produces a stationary state containing durable, spatially
unorganised, uncontested write channels and a small stable set of cycles.
**No evidence was found that these structures perform a demonstrated
nontrivial function under the assays run**: no localisation above a
matched-random null, no growth, no persistent resource routing, no
persisting contested gating.

> **AMENDMENT (operator directive, 2026-09-24).** That is a statement
> about these structures and these assays. It is not a statement that
> `aeth01.v1` contains no possible circuitry, and it must not be quoted as
> one. These assays can see localisation, contest, persistence and
> resource routing. They cannot see a structure that is spatially
> distributed, informational rather than resource-routing, uncontested in
> normal operation, stateful without being self-repairing, or dynamically
> reconfigurable rather than topologically persistent — and any of those
> would be circuitry this round was not built to detect.

---

## 5. REJECTED INTERPRETATIONS

**"Cycles are circuitry."** Prohibited in the preregistration, and the
data show why the prohibition was needed. Out-degree is 1 by
construction, so every component of the write graph is exactly one cycle
with in-trees — cycles are not a finding, they are a theorem. 11,410
cycle nodes is a number to be explained, not evidence of computation.

**"A same-value write is a no-op, so 72% of edges do nothing."** Rejected
on the semantics, not on taste. A landed write makes its target eligible
for perturbation, and that channel supplies 38% of all state change. The
redundant majority is load-bearing for the system's only source of
novelty.

**"~62,500 persistent edges is a persistent functional structure."**
Rejected. Every sampled persistent edge was uncontested, the set is
spatially indistinguishable from random, it has no directional
preference, and its size is fixed from tick 2,500. It is a residue, not
an achievement.

**"Write density is still falling, so the system is still developing."**
Rejected as unsupported. The rate is ~1e-7 per tick at tick 50,000 and
every other measure is flat to four decimal places. Extrapolating that
slope over unobserved time is not something this data licenses in either
direction.

**"Energy Gini of 0.587 shows resource competition."** Rejected.
Concentration arises from independent per-site replenishment against a
uniform maintenance decay, with 23% of sites too poor to act. No
persistent energy edges exist to carry competition.

**"The seeds agreeing to four decimal places shows convergence to an
attractor."** Overreach as stated. What is shown is that three initial
states drawn from the same distribution reach the same *statistics*.
Their state digests differ and their cycle memberships differ. The
attractor claim would need trajectories from genuinely different initial
distributions.

**"The third trajectory was truncated, so the three-seed agreement is
weaker."** Rejected as a concern. Phase 2 ran 47,000 of 50,000 ticks and
agreed with the others to four decimal places from tick 500 onward. The
truncation cost the terminal window sample, not the comparison.

---

## 6. HYPOTHESES

Each is stated so that it could be wrong, with the cheapest test that
would show it.

**H1 — Persistence is exactly non-contest, and nothing repairs it.**
Prediction: perturb the opcode of a persistent edge's source so it stops
writing; the edge does not reappear, and no other edge takes its place at
that target beyond the background rate. Test: a CPU intervention run on a
512² lattice, matched controls, **$0.00** — this needs no GPU and should
not consume the reserve.

**H2 — The persistent count is set by the stationary opcode/direction
statistics alone.** Prediction: the fraction of (site, field) slots with
exactly one active aimed neighbour, computed from the stationary write
density and direction distribution under an independence assumption,
predicts the ≥64-tick cohort size to within a factor of two. Test:
arithmetic on data already in hand, **$0.00**. A clean match would mean
no structure-forming process needs to be posited at all.

**H3 — Cycle enrichment for state-changing edges is a closure constraint,
not selection.** Prediction: the enrichment is reproduced by a null model
that rewires the observed edge set at random while preserving per-field
edge counts and the same-value fraction. Test: offline null model on the
recorded window data, **$0.00**.

**H4 — Perturbation is the rate-limiting source of change, and removing
it freezes the template fields.** Prediction: at `mut_numer = 0` the
template change rate falls by ~38% immediately and then decays toward
zero as redundant channels stop being re-randomised, while energy
dynamics are unaffected. Test: CPU run, **$0.00**. This is the sharpest
available test of the §4 claim that the redundant channel is the noise
channel.

**H5 — 2,500 ticks is sufficient for every stationary measure reported
here.** Prediction: statistics at tick 2,500 predict those at 50,000 to
within the cross-seed spread. Test: already answered affirmatively by
this data for every bulk measure; it fails only for `run_max` and mean
run, which are definitionally time-dependent. Consequence: future rounds
should buy *more seeds*, not longer trajectories. At $0.044 per 2,500-tick
2048² trajectory, the $2.608 spent here would have bought ~59 seeds.

> **AMENDMENT (operator directive, 2026-09-24) — H5 is a campaign-design
> lesson, and it is REGIME-SPECIFIC.** What was established is narrow:
> *for B-balanced `aeth01.v1` and the observables measured here, the
> stationary statistics were already settled by approximately tick 2,500.*
> Nothing establishes that 2,500 ticks suffices for another parameter
> regime, other semantics, other observables or a future substrate, and
> assuming it would be the same class of error as carrying a throughput
> figure across workloads. The transferable lesson is the procedure, not
> the number: **measure time-to-information with cheap scouts before
> buying long trajectories.**

**H6 — B-balanced is a degenerate corner.** The stationary state is so
reproducible, so spatially featureless and so quickly reached that the
parameter point may simply be uninteresting. Prediction: varying
`write_cost`, `maintenance_cost` and `mut_numer` produces qualitatively
different stationary states, including at least one where the persistent
cohort grows rather than saturating. Test: a seed-and-parameter sweep at
2,500 ticks; the `param_sweep` module shape already exists.

---

## 7. FUTURE LIGHT PRESSURES

Stated as what would have to be true, not as things to go and build.

**No steering was applied and none is recommended yet.** Nothing in this
round rewarded loops, cycles, modularity, persistence, resource routing,
state retention, communication or graph complexity, and the negative
result is only informative because of that. A round that introduced a
reward now would be unable to distinguish what the reward produced from
what the substrate does.

**The next pressure should come from the substrate, not from a score.**
The one mechanism this round identified as decisive is tick-rerolled
arbitration, which makes contested channels unable to accumulate runs.
A substrate in which arbitration had *any* memory — priority carrying
even weakly across ticks — would allow a contested channel to persist,
and that is the smallest change that could make persistence something
other than the absence of opposition. Whether that is still `aeth01.v1`
is a semantics question, and it would need a new id.

**Four evidentiary dimensions, NOT a definition.** This round measured
whether a persistent structure (a) contains persisting CONTESTED edges,
(b) is spatially localised above a matched-random null, (c) is repaired
after targeted disruption above background, (d) routes energy through
edges that themselves persist. It found (a) ZERO, (b)
null-indistinguishable, (d) 3–6 edges of 54,000, and (c) was answered
afterwards by H1 — see `AETH-02_CLOSE_2026-09-24.md`.

> **AMENDMENT (operator directive, 2026-09-24).** These four are useful
> evidentiary dimensions. They are **not jointly necessary**, and freezing
> them as the definition of circuitry would make this round's instruments
> into the criterion — which is the error of verifying the label instead
> of the property. Circuitry in a future round may legitimately be
> spatially distributed rather than localised; informational rather than
> resource-routing; uncontested under normal operation; stateful without
> being self-repairing; or dynamically reconfigurable rather than
> topologically persistent. A positive claim should be stated against
> whatever dimensions its own mechanism implies, declared in advance, each
> carrying a matched null.

**Budget discipline.** H5 says the expensive axis was the wrong one.
Future rounds should buy seeds and parameter points at 2,500 ticks, keep
the ceiling well above the projection rather than near it, and measure
throughput on the configuration that will actually run.

---

## 8. LIMITATIONS

1. **No intervention.** Every claim about function rests on observation
   plus semantics. H1–H4 are untested.
2. **Third trajectory truncated** at ~47,000 of 50,000 ticks by the
   dollar ceiling, costing its terminal 50,000-tick window sample.
3. **Window samples are opcode-field only.** The 2,500-edge cap was
   filled before the sampler reached `arg0`, `arg1`, `payload` or
   `energy`, so §2.7 and §2.8 are established for the opcode field alone
   and assumed, not shown, for the others. This is an instrument defect,
   not a finding, and the cap should be made per-field.
4. **Reciprocity untested.** Zero reciprocal pairs were found among
   sampled persistent edges, but with ~2,500 of ~12,300 window edges
   sampled, only ~4% of pairs could have both endpoints present. The
   observation is consistent with no reciprocity and does not establish
   it.
5. **One parameter point.** B-balanced only. See H6.
6. **Cross-seed agreement is within-distribution.** All three initial
   states were drawn from the same sparse-soup recipe at write density
   0.5.
7. **No billing reconciliation.** $2.608 is wall time at a quoted rate.
8. **Three seeds is not an error bar.** Cross-phase spreads are quoted as
   observed ranges, not as confidence intervals.

---

## 9. REGENERATING THESE NUMBERS

Every figure above comes from the committed reduction run against the
committed evidence:

```bash
python Aether/observatory/aeth02_reduce.py \
    Aether/AETH-01/evidence/2026-09-24_aeth02_trajectories/circuitry.log
```

`--json` gives the same content as a machine-readable object.
`Aether/test/test_aeth02_reduce.py` asserts that the reduction still
reproduces the headline figures quoted here, so a change that would
silently alter them fails a test rather than leaving a stale report.

---

## 10. WHAT THE RECEIPTS SAY

| claim | status |
|:--|:--|
| pod terminate acknowledged | yes, `ACK_204` |
| pod observed absent | yes, twice — by the orchestrator and by an independent later inventory read |
| operational cleanup | yes, `ACTIVE_POD_COUNT 0` |
| **billing reconciled** | **no** |
| semantics unchanged | yes, `aeth01.v1`, no new id |
| observer causally downstream | yes; reads the kernel's winner arrays, writes no state |
| out-degree invariant | 1 at all 296 measurements and both phase ends |
| observer accounts for all change | yes, exactly, at every sample |
| instrument class | SPONTANEOUS for all three worlds |
| steering applied | none |
