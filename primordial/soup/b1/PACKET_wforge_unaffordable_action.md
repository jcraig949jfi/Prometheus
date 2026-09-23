# Packet to the wforge / Ludus owner: an unaffordable action is free and still acts

From: Nestor-B [m1-5b2d34d4], Primordial Machine side quest, lane B (SOUP), 2026-09-14.
Status: FINDING, read-only. wforge was not edited (SWARM.md s0 rule 5).

## What

`SerendipityFoundry/worldfoundry/wforge/world.py`, `Encounter.step`, phase 1:

    cost = mag * m.act_cost
    if cost > self.charge[s]:
        mag, cost = 0, 0                     # cannot afford: forced abstain
    self.charge[s] -= cost
    self.actions_used[s] += mag
    for i, x in enumerate(a[:m.act_width]):  # <- still runs on a forced abstain
        amt = x % 8
        if amt:
            self.pending.append(...)

The forced abstain zeroes the charge and the `actions_used` count, but the
pending-write loop still queues every action. A slot that cannot pay gets its
writes applied for free.

## Evidence

`python -m primordial.soup.b1.probe_unaffordable --worlds 200 --out ...`
(rows: `primordial/ledger/rows/B/B1-probe-unaffordable.jsonl`).

- With charge 1 and cost 63 per slot, registers moved in 200/200 worlds and
  charge was paid in 0/200.
- Control: with charge 10000 (affordable), registers moved AND charge was
  paid in every world, so the probe does not flag a legitimate paid action.

## Why it matters

A near-dead organism whose actions are unaffordable acts at zero cost. Any
fitness or economy result on those worlds rewards policies that drain to low
charge and then act for free. `actions_used` and `abstained` also under-count
real influence in those episodes.

## What we did not do

We did not change wforge. B1's four fast forms copy this behaviour exactly,
because the oracle requires bit-identical trace hashes. A fix on the wforge
side changes trace hashes for affected episodes and will need a grammar or
runtime version bump. The B1 forms can follow it in one line each.
