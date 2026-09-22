# cw01-e04 — QUEUE / TTL ECOLOGY

campaign_id: cw01-2026-09-17
experiment_id: cw01-e04
attempt_id: cw01-e04-a01
written: 2026-09-17, before any implementation exists.

## Why this is written first (fourth time; it has earned its place)

e01: fixed the interventions in advance, so when the instrument turned out broken the
repairs had to serve the question. e02: the limit written beforehand — *"the ordering
is an enhancement, not a precondition"* — predicted the NULL exactly. e03: the
distinction written beforehand — *"sparsity is not a coalition"* — turned out to be
the entire experiment. The pattern is consistent: whatever is not fixed in writing
beforehand gets fitted to whatever the machinery makes convenient.

## The pressure

Items arrive. Useful output requires combining information that becomes available at
*different times*. The channel that carries information between those times is
**bounded, ordered, forgetful and slow**: it holds finitely much, delivers in a
discipline the organism does not choose, expires its contents, delays them, and
sometimes drops them.

Nothing is called a queue, cache, scheduler, buffer or retry. The organism does not
learn that a TTL fired. **The object vanished.** It pays the consequence.

## Minimal scientific question

> Under a bounded, forgetful, delaying channel, does evolution discover
> **differential handling conditional on item properties** — triage — or merely a
> **uniform policy** that happens to score well?

## THE DISTINCTION THAT DECIDES THIS EXPERIMENT

**Uniform handling is not triage.** An organism that enqueues everything identically,
or enqueues a fixed fraction, can score respectably while having learned *nothing about
which items matter*. Triage means **what the organism does with an item depends on that
item's properties**.

Measured as two independent quantities, exactly as e03 separated sparsity from
conditionality:

- **Selectivity** = fraction of arriving items given channel treatment. Low is cheap.
- **Triage** = `I(item_properties ; handling_decision)`, against a shuffled-label null.
  Zero means the organism ignores what the item is, however selective it looks.
- **Triage competence** = does the conditional policy favour items that are *actually*
  worth carrying, or merely a consistent arbitrary subset?

A result with high selectivity and **zero triage** is a NEGATIVE for the triage claim
and will be reported as such.

## Second axis, required by the campaign order

> *"Vary the weather after evolution to test whether the mechanism is general or merely
> fitted to one damage schedule."*

So generality is a separate verdict from existence: a policy tuned to one TTL is a
weaker result than one that survives nearby physics. Both are reported.

## What is NOT built

No queue object exposed as a queue. No scheduler, priority field, retry loop, cache,
eviction policy, or backpressure signal. No reward for enqueueing less, for ordering, or
for recovering dropped items. The channel has physics and prices; what the organism does
with them is the measurement.

## Neutral affordances (priced)

- **Channel placement** — put a value into the channel. Costs `c_put`. Capacity is
  finite; placement into a full channel fails silently and still costs.
- **Channel retrieval** — take from the channel under a fixed discipline (FIFO by
  default). Costs `c_get` whether or not anything is returned.
- **Expiry** — placed values vanish after `ttl` steps. No notification.
- **Latency** — a placed value is not retrievable for `d` steps after placement.
- **Loss** — placement fails with probability `p_drop`, silently.
- **Direct recompute** — the always-available fallback: reconstruct the needed
  information at full cost, no channel involved.

The organism observes item properties before deciding. It never observes TTL, queue
depth, or whether a specific object still exists.

## Pre-registered interventions

Each against a cost-matched sham, applied post-hoc to evolved populations:

- **J1 SCRAMBLE-VALUE** — permute which item properties predict an item's worth, leaving
  all costs and physics identical. Sham: identity permutation. *A triage policy matched
  to real structure must collapse; uniform handling should not care.* **Decisive.**
- **J2 TTL-SHOCK** — halve and double the TTL after evolution. Sham: same number of
  world-parameter writes, TTL unchanged. *Generality vs fitting.*
- **J3 DISCIPLINE-SWAP** — FIFO → LIFO. Sham: FIFO → FIFO.
- **J4 DROP-SHOCK** — raise `p_drop`. Sham: unchanged `p_drop` at the same cost.

J1 and the identity shams are named here so they cannot be dropped if inconvenient.

## Measurement

Primary: **useful information transformed per unit resource, ancestor-relative** (II).
Never raw fitness, never a selectivity score.

Recorded per organism: items seen, placements attempted/succeeded, retrievals
attempted/hit/miss, expiries suffered, recomputes, channel occupancy, latency to
completion, selectivity, `I(properties ; handling)`, triage competence, compute, cost.

Dependence statistic: Δ(performance | intervention) − Δ(performance | matched sham),
ancestor-adjusted.

## Disposition rules, fixed in advance

- **COMPLETE** — selectivity **and** triage above its shuffled null **and** J1 collapses
  performance beyond its sham, replicated across independent seeds.
- **NEGATIVE** — channel users do not beat matched always-recompute controls.
- **NULL** — selectivity evolves but triage is ~zero, or J1 does not hurt: a policy that
  is cheap without being informed. **Likely and fully reportable.**
- **INCONCLUSIVE** — effect present but not replicated, or IX not discharged in timebox.

Generality (J2/J3/J4) is reported as a **separate** verdict and never upgrades the
primary disposition.

## Known threats to validity

1. **Uniform policy mistaken for triage.** The central threat; addressed by measuring
   triage separately and by J1.
2. **Free lunch.** If the channel is too reliable, everything is enqueued and there is no
   pressure; too hostile and nothing is. **Learnability gate** (`lib/learnability.py`)
   runs before any budget: a hand-built triager must beat hand-built uniform-enqueue and
   always-recompute, and a badly-configured triager must lose.
3. **MI bias.** Triage is measured with `lib/infometrics.mi_with_null`; raw MI reads
   ≈0.14 bits on independent data at these sample sizes (CW01-D022).
4. **Latent facts redrawn per episode.** The property→worth mapping and the channel
   physics are attempt-stable, not episode-stable (CW01-D029).
5. **Arms diverging by construction.** Arms are genome/world transformations applied up
   front; no capability flag may short-circuit a draw (CW01-D019/D021).
6. **Recording a check that did not run.** No `ran=True` without a performed comparison
   (CW01-D031).

## Smallest scientifically meaningful version

One world, one channel physics (`ttl`, `delay`, `p_drop`, capacity), one population;
selectivity, triage and ancestor-relative score measured; plus **J1 and its sham only**.
If triage never rises above its shuffled null within the timebox, the disposition is NULL
on the evidence available — not an extension of the search until something appears.
