# cw01-e01 — WORKSPACE EMERGENCE UNDER NECESSITY

campaign_id: cw01-2026-09-17
experiment_id: cw01-e01
attempt_id: cw01-e01-a01
written: 2026-09-17, PREFLIGHT phase, **before** surveying the existing codebase.

## Why this is written first

The campaign order forbids inspecting an organism, recognising a familiar algorithm, and
then redesigning the world to encourage it. The subtler version of that error is designing
the *pressures* after learning which affordances the existing machinery makes cheap. This
document therefore fixes the question, the affordances, the interventions and the
disposition rules **before** the reuse survey returns. If implementation cost later forces
a change, the change is recorded as an amendment with a reason — never by silent edit.

## Minimal scientific question

> Under economics where useful computation cannot always be completed within one step, do
> populations evolve to **pay a holding cost to retain unfinished computation** rather than
> recompute it — and does their advantage **causally depend** on that retained state?

The second clause is the experiment. Correlation between "has persistent state" and "scores
well" is nearly free and nearly worthless. The claim only survives if removing, corrupting
or mis-addressing the retained state **destroys the advantage**.

## What is NOT built

No workspace architecture. No scratchpad object, no memory controller, no "save/restore"
API, no named slots, no attention over stored items. Nothing in the world is called a
workspace, buffer, cache, or memory. Organisms are given neutral affordances with prices;
whether any of them is used to hold unfinished work is the thing being measured.

## Neutral affordances (each priced, none privileged)

A1. **Addressable region.** A finite set of cells that survives between steps. Writing costs
    `w`, reading costs `r`, and *occupancy costs `h` per cell per step* whether or not it is
    read. Holding is never free.
A2. **Partial emission.** A computation may terminate before completion and emit whatever it
    has. Partial output is not rewarded directly; it is simply permitted to exist.
A3. **Re-entry.** A computation may begin from a supplied value rather than from the world's
    initial condition. Nothing enforces that the supplied value is its own earlier output.
A4. **Retrieval by content.** A value may be looked up by a key the organism computes.
    Collisions are possible. Lookup costs `r` whether or not it hits.
A5. **Transfer channel.** Where the world permits, a value may pass to a descendant or a
    contemporary. Transfer has its own price and a failure probability.

Costs `(w, r, h, transfer)` are world parameters and are varied across worlds. If retention
only pays under one arbitrary price vector, that is weak evidence and will be reported as
such.

## Pressure

Work arrives whose completion demand exceeds a single step's budget, drawn so that:
- some items are *resumable* (partial progress is worth more than nothing),
- some items *recur* (the same subcomputation is demanded again later),
- some items are *novel* (retention cannot help).
The recurrence rate is a world parameter. At recurrence 0 retention should be pure cost —
that is the built-in negative control, not an afterthought.

## Pre-registered causal interventions

Applied **after** evolution, to evolved populations, against matched controls. Each is a
separate arm; each has a matched sham that pays the same cost without the causal effect.

- **I1 ERASE** — zero the addressable region between steps.
- **I2 SCRAMBLE** — permute the address map between write and read. Content survives;
  addressing does not. Separates *having* state from *finding* it.
- **I3 SEVER** — disable A4 retrieval only. Writing and reading own cells still work.
- **I4 DESTROY-SELECTED** — delete the k partials with highest retrieval frequency, and, as
  a control, k random partials. If only the targeted deletion hurts, the organism was using
  those specific items.
- **I5 SWAP** — exchange preserved state between matched organisms. If performance follows
  the *state* rather than the *organism*, the state carries the work.

I2 and I4-control are the interventions that distinguish a real result from a story; they
are named here so they cannot be quietly dropped if they are inconvenient.

## Measurement (ancestor-relative, per II)

Primary: **useful information transformed per unit resource, relative to ancestor**, under
matched worlds and budgets. Never raw fitness.

Recorded per organism/lineage: compute, cell-steps held, reads, writes, retrievals
(hit/miss), transfers attempted/succeeded, partial emissions, re-entries, recompute events,
latency to completion, and completion fraction.

Dependence statistic: Δ(performance) under each intervention minus Δ under its sham,
ancestor-adjusted. A positive advantage with **zero** intervention sensitivity is reported
as NULL for the causal claim even if the raw advantage is large.

Transfer: evolved populations are moved to worlds with (a) different price vectors,
(b) different recurrence rates, (c) frozen/unseen task streams.

## Disposition rules, fixed in advance

- **COMPLETE** — a retention-dependent advantage replicates and is intervention-sensitive
  in the pre-registered direction.
- **NEGATIVE** — retention-capable lineages do not beat matched non-retaining controls.
- **NULL** — advantage exists but is intervention-insensitive (it was not the machinery).
- **INCONCLUSIVE** — effect present, replication or controls not achieved within timebox.
- **BLOCKED / INSTRUMENT-FAILURE / SKIPPED-TIMEBOX** — per campaign lifecycle.

A NEGATIVE or NULL result here is a real finding about the pressure and will be reported
with the same weight as a positive one. The experiment is not permitted to "succeed" by
redefinition.

## Known threats to validity

1. **Backend leakage** — retention advantage that is really an artefact of one store's
   behaviour. Mitigation: the organism-visible physics must be reproducible on a second
   backend (IX). If that is not achieved within timebox, the claim is capped at
   INCONCLUSIVE, not COMPLETE.
2. **Free lunch** — if holding cost `h` is effectively zero, retention trivially wins and
   the result is about the price, not the biology. `h > 0` is asserted at QUALIFY.
3. **Leakage via recurrence** — if recurrence is too high the task degenerates to lookup.
   Recurrence is swept, not fixed.
4. **Sham asymmetry** — an intervention that also removes compute would confound. Each sham
   is cost-matched and verified at QUALIFY.

## Smallest scientifically meaningful version

One world, one price vector with `h > 0`, one non-zero recurrence rate, retention-capable
vs. matched non-retaining ancestors, plus **I1 and its sham only**. If that cannot be
exercised within the timebox, disposition is SKIPPED-TIMEBOX with the blocker named.
Everything else (I2–I5, price sweeps, transfer) is expansion, attempted only after the
minimal form produces a durable row.
