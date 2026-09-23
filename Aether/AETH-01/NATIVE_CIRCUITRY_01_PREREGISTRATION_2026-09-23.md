# AETH-02 Native Circuitry 01 -- PREREGISTRATION

Status: **PREREGISTERED. Committed before any run, in its own commit, so
the order is in git history** (base role s2). Nothing below may be
changed after data exists; if something here turns out to be wrong, the
correction is an annotation beside it with a date, and the original
stays visible.

Instance Aether[buckkeep-7a10ca4b]. Branch
`aether/aeth02-native-circuitry-2026-09-23`, base `ab7ac1631`.
Directive: `roles/Aether/prompts/2026-09-23_native_circuitry/DIRECTIVE.md`.

## 1. The instrument, and why it is causally downstream

`gpu_step` takes an optional `observer` list. Per field it appends
`(winner_slot, contenders)`:

- `winner_slot` uint8, index into `_NEIGHBOR_SLOTS` of the source whose
  proposal won, 255 where nothing won. The source coordinate follows
  exactly from (target, slot), so this costs 1 byte/site rather than 8.
- `contenders` uint8, how many of the four slots presented a valid
  proposal -- the arbitration outcome.

The observer is written to and never read from, so no value in it can
influence the transition. `semantics_id` is unchanged, the replay tuple
is unchanged, and `observer=None` allocates nothing.

Already verified (commit preceding this one): five output fields and
`counters` byte-identical with the observer on and off; frozen A40
digests 8/8 and 7/7; AST parity between the two kernel copies; the edge
set equal to the CPU oracle's independent `proposal_won` trace on fixed
dimensions and 120 randomized worlds; contender counts equal to the
oracle's `proposal_emitted` counts; a cheat control that corrupts one
recorded winner and requires the comparison to notice.

Measured cost: **113.01 bytes/site observer off, 123.01 on** (+10.00,
exactly the predicted 2 arrays x 5 fields x 1 byte).

## 2. A structural fact that changes what is worth measuring

A writer's direction and target field come from its own `arg0`/`arg1`,
so **it emits exactly one proposal per tick.** Measured out-degree is 1
for every source. The per-tick realized edge set is therefore a
**partial function on sites**, and that has consequences which are
mathematical, not empirical:

- every weakly connected component is exactly one cycle with in-trees
  hanging off it;
- strongly connected components larger than a single node are **exactly
  those cycles**, so SCC detection reduces to cycle detection and needs
  no general SCC algorithm;
- out-degree distribution is degenerate (all 1). Fan-in, which is
  `contenders`, carries all the degree information;
- "bottleneck" and betweenness reduce to how many tree nodes feed a
  given cycle;
- path length from a node is the number of steps to reach its cycle.

**These will be reported as structurally determined, not as findings.**
Reporting an all-ones fan-out distribution as a measurement would be
dressing a definition up as evidence.

The genuinely empirical questions that survive are: which cycles exist,
how long they persist, whether the realized map changes while the
proposed map does not (arbitration re-randomizes per tick because the
priority hash includes the tick), and whether anything about a cycle's
history affects its future.

## 3. Sparsity: the observer must not become the experiment

At 4096^2 with First Light's activity of 0.19-0.42, a tick produces
roughly 3-7 million edges. Fifty thousand ticks is on the order of
**10^11 edges**. Logging them is not an option, so:

RETAINED EVERY SAMPLED TICK, as aggregates computed on device without
materializing any edge list:
- edge count per field; total edge count
- `contenders` histogram (bins 0..4) per field -- the fan-in distribution
- winning-slot histogram (4 bins) per field -- directional flow
- count of edges that changed target state vs did not, per field
- number of realized cycles, and the cycle-length histogram, by pointer
  doubling on the realized map
- number of sites on a cycle; number in trees; mean steps-to-cycle
- edge-persistence run lengths, carried as a per-(site,field) uint16
  counter incremented when the winner is the same slot as last tick and
  reset otherwise. This gives recurring-edge statistics **without
  storing edges**, at 10 bytes/site.

RETAINED EXACTLY, as edge-level traces, only inside:
- the two preregistered windows of section 4;
- the detector-selected window of section 5, labelled separately;
- candidate subgraphs identified under section 6.

## 4. Preregistered window selection -- fixed now, no cherry-picking

Two 256x256 full-resolution windows per world, both fixed before the run:

- **WINDOW_A, fixed origin.** Top-left at (0, 0). No selection freedom
  whatsoever.
- **WINDOW_B, seeded origin.** Top-left at
  `(mix64_scalar(seed ^ 0xA02) % (H - 256), mix64_scalar(seed ^ 0xB02) % (W - 256))`
  using the world's own physics seed and `mix64_scalar` from the kernel.
  Determined by the run configuration, computable before the run starts,
  and not choosable after seeing data.

Both are captured at the same tick schedule for every world, whether or
not anything interesting is in them. A window that turns out empty is
reported as empty.

## 5. Detector-selected window -- separate, and labelled

One additional 256x256 window may be selected by the anomaly rule:

> the window containing the 64x64 block with the greatest number of
> (site, field) pairs whose edge-persistence run length is at least 16
> consecutive ticks, evaluated at the mid-run sample.

Threshold 16 and "mid-run" are fixed here. This window is recorded as
`DETECTOR_SELECTED` and **never pooled** with WINDOW_A/WINDOW_B in any
statistic, because it was chosen by looking.

## 6. Candidate definitions, under neutral labels only

A candidate is a measurement, not a claim. Nothing below is called
memory, communication, control or computation.

- `PERSISTENT_SUBGRAPH_CANDIDATE` -- a realized cycle whose full edge
  set is unchanged for at least 64 consecutive sampled ticks.
- `LONG_RANGE_PROPAGATION_CANDIDATE` -- a chain of realized edges,
  consecutive in time, whose endpoints are at least 32 lattice sites
  apart, i.e. state that travelled 32 hops rather than a value merely
  appearing far away.
- `RESOURCE_ROUTING_CANDIDATE` -- a field-4 subgraph moving a net
  positive energy flow along the same edge set for at least 64 sampled
  ticks.
- `STATE_DEPENDENCE_CANDIDATE` -- reserved for section 7's outcome and
  **cannot be assigned by observation at all**: it requires two replays
  from the same checkpoint that differ only in the candidate's prior
  state and then diverge in the candidate's later output.

## 7. Counterfactual assay, with the causality limit stated

For each of the strongest candidates:

1. checkpoint the world (the recipe plus tick is already an exact
   replay pointer);
2. replay identically -- confirm bit-identical, or the assay is void;
3. replay with ONE site inside the candidate perturbed by a single bit
   flip in its opcode;
4. run `delta` = 256 further ticks;
5. measure Hamming divergence from the unperturbed replay, split by
   distance from the perturbed site.

**MATCHED CONTROL, and it is the whole filter.** The same single-bit
perturbation is applied to a site NOT in any candidate, matched on:
neighbourhood WRITE density (+/-10%), own energy (+/-8), and target
field. Five matched controls per candidate.

**THE CAUSALITY LIMIT, stated before any result.** The physics is local
with propagation speed of one site per tick, so at `delta` ticks all
divergence lies inside a radius-`delta` light cone. "Nonlocal
consequence" therefore CANNOT mean divergence outside the cone -- that
is impossible and finding it would mean the instrument is broken. It can
only mean **divergence much larger than a matched perturbation elsewhere
produces**. Any claim phrased as "the effect reached further than
mechanics allow" is wrong by construction and will not be made.

A candidate passes only if its divergence exceeds every one of its five
matched controls. Weak effects are acceptable; effects within the control
spread are not.

## 8. What would falsify what

- Persistent cycles exist but perturbing them gives divergence inside
  the matched-control spread -> **no functional circuitry**, and that is
  the round's answer. It is a real result and will be stated plainly.
- The side-channel disagrees with the oracle trace at any point ->
  engineering blocker, scientific interpretation stops.
- Long-horizon CPU/GPU digests diverge -> engineering blocker,
  interpretation stops.
- B reaches a fixed point early -> Track 1 answered, and the certified
  freeze condition from First Light section I1 applies.
- Edge-persistence run lengths never exceed the arbitration
  re-randomization timescale -> there is nothing for a candidate to be
  made of, and the cycle statistics are describing tick-to-tick noise.

## 9. Budget, and stop conditions

Up to **$3**, one pod at a time, the already-qualified A40 path.
Priority: Track 1's 50,000-tick B trajectory first, because it is the
one thing First Light left right-censored. Stop on semantic mismatch,
OOM, >60 s/tick, unexpected failure, or the controller's dollar ceiling.
Terminate and verify `ACTIVE_POD_COUNT 0`.

No reward, no selection pressure, no graph-complexity objective, no
kernel redesign. The measurements of this round are observational, and
`FUTURE LIGHT PRESSURES` in the output document will name candidate
pressures without implementing any of them.
