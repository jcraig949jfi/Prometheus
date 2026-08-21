# DOCTRINE PROPOSAL — competitor-relative identification

**Status:** PROPOSED by Techne, **v2 — the v1 form was FALSIFIED by external review the cycle
after it was drafted** (2026-08-21). Recorded as a correction, not a silent edit: the v1 law
was overreaching, the reviewer produced a counterexample in one line, and the replacement is
weaker, defensible, and more useful.

## v1 (WITHDRAWN)

> ~~Every rung has a cheaper mechanism that is EXACT on some restricted slice of probe space.~~

**Counterexample (ChatGPT, round 5):** take the capability `f(0)=1` on probe space `X = {0}`.
Any mechanism exact on the only nonempty slice *is* the capability. There is no cheaper
impostor unless "cheaper" is defined externally by implementation cost. The v1 form is not a
law of computation; it was a generalisation from five straw men I happened to build.

## v2 (PROPOSED)

> **A battery identifies a capability only relative to an explicitly enumerated competitor
> class. Finite observations never uniquely identify a mechanism.**

The universal danger is not an exactness slice but **observational equivalence on the sampled
support**: for any finite tested set `T = {x₁…xₙ}`, the lookup table `L(xᵢ) = f(xᵢ)` is exact
on `T` without implementing `f`. That subsumes all five of the instances below and is harder
to escape than the v1 claim.

## The instances (still executable in `techne/ladder_circuits/`) — now read as *examples*, not proof

| Rung | Cheaper competitor | Agrees on | Probe that separates |
|---|---|---|---|
| R0 | exact-AST retrieval | clean probes | fresh-seed isomorphs |
| R1 | answer interpolation | inside the coefficient hull | 10⁹-scale, exact rationals, symbolic params |
| R4 | frequency prior | stable base rates | base-rate inversion + name randomisation |
| R5 | delta tracking | additive post-fork dynamics | a multiplicative event after the fork |
| R7 | memoryless thrashing | first alternative always works | multi-failure problems |
| (obj.) | myopic progress-greedy | single lucky instances | expectation over the space |

## Why the weaker form is the more useful one

**The union of competitor agreement-regions is not computable** (round 5, 11.2): asking
whether cheaper program M agrees with target F on region S contains program equivalence, so
Rice-style obstruction applies; even deciding whether the regions cover X encodes
halting/equivalence questions. Unrestricted battery design therefore has **no completeness
certificate**.

What makes it scientific instead of hopeless is declaring a **threat model** `C≤k` —
mechanisms below a resource/description bound — and then:

1. enumerate the competitor families in `C≤k`;
2. estimate or prove their agreement regions;
3. construct probes maximising disagreement;
4. **conclude only "not separated from `C≤k`"** — never "certified reasoning".

Step 4 is the part that changes how Prometheus should write results.

## The meta-battery (CEGIS discipline)

> **Can a newly proposed cheap mechanism pass the existing suite?**

Every time one does, it becomes a new adversary and the battery grows: candidate →
counterexample → refine. There is no stopping theorem; what you get is bounded confidence
against an expanding adversary class, and an audit trail of which competitors have been
excluded. `techne/ladder_circuits/threat_model.py` implements this loop.

## How to apply

When claiming a mechanism from a battery result:
1. State the threat model `C≤k` explicitly.
2. Name each competitor and its agreement region.
3. Show the probe distribution has mass outside their union *within that class*.
4. Report the conclusion as **not-separated-from-`C≤k`**, with the class named.
5. For objective/selection claims, report expectation and worst case, never a sampled instance.

If step 1 cannot be answered, the battery has not been designed — it has been assembled.

## Companion proposals (same yes/no)

- **Abstention channel** (cycle 006): forcing True/False scores honest capacity-limited
  circuits as liars; conservative ≠ abstaining.
- **Immutable-observation constitution** (cycle 013, replacing the earlier
  evaluator-warrant draft): see `DOCTRINE_PROPOSAL_immutable_observations.md`.
