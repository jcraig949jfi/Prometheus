# Metered verifier — build log and findings

Milestone 1 of `NEXT_MILESTONES.md`. Built iteratively; every design change
below was forced by a test failing, not chosen in advance.

## What it is

The harness owns every chargeable evaluation. A seat can call `evaluate(point)`,
`evaluate_range(lo, hi)`, `symbolic_check(relation)`, and the free
`remaining()` / `statement()` / `report()`. Nothing else reaches the claim.

**Chargeability is defined at the interface**: a call costs because it requests
information about the target claim, not because it executed code. Parsing JSON
is free. Asking whether the proposition holds at n = 4 is not. This removes the
judgement call the v0.1 seats were forced to make and openly disagreed on —
several charged themselves for re-running a script to persist a log, several ran
a JSON parse check and did not.

Past the cap the API refuses and the call does not run. That is what makes
`UNRESOLVED_WITHIN_BUDGET` a class about calibration rather than about whether a
seat chose to obey an unenforced limit.

## The precondition, stated rather than assumed

Metering binds only if a seat cannot obtain the same information locally. A
fully public, cheaply reimplementable claim leaves the cap decorative — the
exact v0.1 failure. So a metered claim must carry a **sealed component** the
seat can only reach through this API. Sessions record `binding=True/False`, and
a non-binding claim's meter reading is honest about being unenforceable rather
than quietly analysed as if it weren't.

## Finding 1 — the refund policy destroyed the experiment

`evaluate_range` originally refunded points beyond an early failure, reasoning
that cost should track work done rather than how a question was phrased.

The selftest exposed the consequence: **with a refund, requesting the entire
affordable domain costs only up to the first failure, so "scan everything" is
never worse than any targeted strategy.** There is then no incentive to navigate
at all, and the arena's central question becomes unaskable.

Reversed: the width you ask for is the width you pay for. Choosing a range
becomes a decision with a price, which is the thing being measured. Adaptive
seats step with `evaluate` at one credit per probe and stop when they like —
that route remains available and costs exactly the number of probes taken.

I had written a comment defending the refund on the grounds that charging for
unrun work "would make cost a function of how the seat phrased its question
rather than what it learned." That reasoning was wrong: how you phrase the
question *is* the decision under study.

## Finding 2 — the first cost spread was accuracy in disguise

The strategy landscape initially showed a 3.6x spread between a naive sweep and
an informed probe, and informed separating from a boundary heuristic at
p = 0.017.

Applying `PREREG_A0.md` Amendment 1 — the collider correction I had just
registered — killed it. On the **intersection** of claims every strategy
dispositioned correctly, `informed` vs `boundary_first` came out at **p = 0.450**.
The full-sample separation was an accuracy effect: informed solved more claims
(88% vs 72%), and solving more claims lowers a cap-charged mean.

My verdict logic had used the full-sample p-value and reported a separation that
did not survive. Fixed to use the intersection p, which is what the amendment
requires.

The design lesson underneath: **coverage advantages and cost advantages are
different things.** The original `informed` probed boundaries first, exactly as
`boundary_first` did, then added residues. On claims both solved, they took the
same route and cost the same; informed's advantage lived entirely in claims
`boundary_first` failed outright. That is a coverage win, and the navigation
experiment needs a cost win.

## Finding 3 — navigation has to be claim-conditioned

Fixed by giving each claim a **public** shape tag and making the informed
strategy choose its probe order from it, while the generic heuristic ignores it.
The shape is visible to everyone; what the graph is supposed to supply is the
mapping from shape to the probe order that reaches the witness soonest.

That is the structure the navigation experiment actually posits, and it produces
a cost win rather than a coverage win.

Result on 200 claims, domain [1, 5000], budget 1500:

```
  strategy          accuracy  mean cost   median
  naive_sweep           30%     1500.0     1500
  left_step             30%     1188.2     1500
  boundary_first        64%      706.5      536
  informed              87%      347.7       79

INTERSECTION (52/200 claims every strategy got right)
  naive_sweep      mean   1500.0   median  1500
  left_step        mean    442.7   median    36
  boundary_first   mean    508.8   median    82
  informed         mean     72.4   median    35

  naive / informed on the intersection : 20.7x   perm p 0.000
  informed vs boundary_first           :         perm p 0.000
```

**20.7x cost separation on shared items**, so it is not an accuracy effect, and
informed beats a generically careful strategy on the claims both solve.

That is the headroom the v0.1 A0 run lacked — obtained by hardening the search
geometry rather than the mathematics, as the review advised.

## What the selftest hunts

21 checks, each written against a failure rather than an expected behaviour:

- a path that reads the claim without charging (taint counters, exact)
- a cap that is advertised but not enforced
- evaluations leaking past a refused call
- an oversized sweep running part-way before dying, which would let a seat
  locate the cap by watching where sweeps stop
- a public method added later and never charged (enumerates `Session` by
  reflection, so it survives me forgetting)
- a non-binding claim quietly analysed as if the budget bound it
- a greedy seat ignoring refusals and hammering the API in every shape it knows

Point evaluations and symbolic sampling are counted on **separate** taint
counters. Folding them into one would make the invariant approximate, and an
approximate invariant is exactly where a metering bug would hide.

## Still open

- The meter serves sealed fixtures. Wiring it to the real generator needs claims
  that carry a genuine sealed component; today's generator emits fully public
  claims, so `binding` would be False for all of them.
- `symbolic_check` answers by sampling five points. That is a placeholder: a
  real symbolic route should answer a structural question, not sample.
- The strategy landscape is scripted. It shows the cost geometry exists; it says
  nothing about whether an agent discovers it. That is what v0.2 A0 measures.
