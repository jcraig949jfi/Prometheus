# cw01-e02 — ANCESTRAL EFFICIENCY RATCHET

campaign_id: cw01-2026-09-17
experiment_id: cw01-e02
attempt_id: cw01-e02-a01
written: 2026-09-17, PREFLIGHT phase, **before** any implementation exists.

## Why this is written first (again)

In e01 the pre-registration is what stopped four separate false positives from
being reported: it fixed the interventions in advance, so when the instrument
turned out to be broken the fix was forced to serve the question rather than the
other way round. The same discipline applies here, and it matters more, because
the ratchet claim is much easier to fake.

## The pressure

> DO USEFUL COMPUTATION BETTER THAN YOUR ANCESTOR DID.

Selection is on **useful information transformed per unit resource, relative to
ancestor**, under matched worlds and budgets. Never raw fitness. Never "be
complicated". Never "implement a named algorithm".

## Minimal scientific question

> Do successive ancestor-relative gains **compose into a ratchet** — that is, is a
> later gain *conditional on an earlier gain having landed* — or do gains merely
> accumulate independently?

This is the whole experiment. "Two improvements happened in one lineage" is nearly
free and proves nothing: independent improvements also co-occur. The claim only
survives if removing the earlier gain **disproportionately** destroys the later one.

## Operational definition of a ratchet (fixed now, not after seeing data)

A ratchet between gains A (earlier) and B (later) requires **all three**:

1. **Temporal ordering.** A reaches fixation in the lineage strictly before B
   appears. Recorded from the lineage, not inferred afterwards.
2. **Superadditive knockout.** Take a descendant carrying both. Revert A's genes to
   their pre-A ancestral values, leaving B's genes untouched. The loss must
   **exceed A's own original contribution** — i.e.
   `loss(revert A from A+B) > gain(A alone, measured when it arrived)`.
   If B stands on its own, the loss is merely additive and this fails.
3. **Order-dependence.** B's genes installed into the *pre-A* ancestor must yield
   less than B's genes in the post-A background. B must be worth more on the
   foundation than without it.

Condition 2 is the one that distinguishes a ratchet from ordinary epistasis plus
luck, and condition 3 is the one that stops me from calling any positive epistasis
a ratchet. Both are named here so neither can be quietly dropped if inconvenient.

## What is NOT built

No "capability" objects, no skill tree, no unlockable upgrades, no explicit
composition operator, no reward for using two mechanisms together. The world prices
physical consequences; whether anything composes is measured, not designed.

## Neutral affordances (priced, none privileged)

Work items arrive as structured payloads that must be transformed into useful
output. The organism may apply transformations drawn from a small neutral set. Each
has a price, and prices interact **through the state of the payload**, not through
any rule about ordering:

- **T1 normalise** — reduces payload dispersion. Costs `c1`.
- **T2 factor** — extracts shared structure. Costs `c2`, and its cost scales with
  payload dispersion, so it is *cheaper on a normalised payload*. Nothing states this.
- **T3 reduce** — produces output. Cost scales with payload size and with residual
  structure, so it is cheaper after T2.
- **T4 cache-bind** — retains a transformed payload for reuse (priced occupancy,
  reusing e01's economics).

The ratchet substrate is therefore purely economic: T2 is cheaper after T1, T3 is
cheaper after T2. No rule rewards the sequence. If a lineage discovers the ordering,
that is a finding; if it does not, that is also a finding.

## Pre-registered interventions

Applied post-hoc to evolved lineages, each against a cost-matched sham:

- **K1 revert-A** — restore the earlier gain's genes to pre-A ancestral values.
  Sham: revert an equal number of *neutral* genes (no measured contribution).
- **K2 transplant-B** — install the later gain's genes into the pre-A ancestor.
  Sham: install them into the post-A background (should be ~neutral).
- **K3 ancestor-restoration** — run the original ancestor in the descendant's world.
- **K4 price-shift** — re-run evolved lineages under altered `c1..c4`.
- **K5 harder-workload** — increase demand; do gains survive?
- **K6 frozen-transfer** — unseen world, frozen at evaluation time.

K1 and K2 are the ratchet test. K3–K6 are the survival tests the campaign order
requires (harder workloads, altered prices, altered geometry, frozen transfer,
ancestor restoration).

## Measurement

Primary: `useful_information_transformed / total_resource_cost`, ancestor-relative.

Resource accounting (all recorded, per the campaign order): compute, retained
state (cell-steps), object accesses, world interactions, transformations applied,
communication, latency-to-completion, and external transformations.

Gain detection: a **gain** is a generation-over-generation improvement in the
lineage mean that (a) exceeds a pre-set effect size, and (b) persists for at least
`P` subsequent generations. Both thresholds are fixed in WORLD.json before running,
so "gain" cannot be defined post-hoc to fit whatever the curve did.

## Disposition rules, fixed in advance

- **COMPLETE** — ≥2 ordered gains, superadditive knockout (K1), order-dependence
  (K2), and the result replicates across independent seeds.
- **NEGATIVE** — descendants do not beat ancestors under matched budgets.
- **NULL** — gains occur but are additive: removing the earlier gain costs no more
  than that gain was worth. Accumulation without a ratchet. **This is a real and
  likely outcome and will be reported with equal weight.**
- **INCONCLUSIVE** — a ratchet signature appears but does not replicate, or the
  backend counterfactual is not exercised within the timebox.

## Known threats to validity

1. **Epistasis ≠ ratchet.** Positive gene interaction is common and is not a
   ratchet unless ordered in time and superadditive on knockout. Conditions 1–3 exist
   for this reason.
2. **Gain detection on noise.** A "gain" fitted to a wiggle in the curve will
   manufacture ratchets. Effect size and persistence thresholds are pre-set.
3. **Reversion must be free.** Reverting genes must cost no resources, or the
   knockout measures the reversion rather than the dependency.
4. **Drift masquerading as a foundation.** If A is neutral-but-fixed, reverting it
   should cost ~0; a ratchet requires A to have had a measured contribution *when it
   arrived*. That contribution is recorded at the time, not reconstructed.
5. **Free lunch.** As in e01, the prices must make the ordering a real trade. A
   reachability probe (best-case vs worst-case hand-built organism) runs before any
   budget is spent — this is now a standing gate, not a judgement call.

## Smallest scientifically meaningful version

One world, one price vector, one population, enough generations to observe ≥2
ordered gains, plus **K1 and its sham only**. If ≥2 ordered gains do not appear
within the timebox, the disposition is NEGATIVE or NULL on the evidence available —
not an extension of the search until something appears.
