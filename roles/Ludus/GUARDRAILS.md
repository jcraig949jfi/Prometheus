# LUDUS guardrails — methodological pressure, and what enforces it

**Received 2026-08-26 from James.** Framed explicitly as *methodological pressure, not conceptual
answers*: **"the biggest danger is contaminating a promising experiment with our own ontology."**

This file is not a restatement. Each guardrail is mapped to the **mechanism that enforces it**, so
that a future wake cannot satisfy it by remembering to be careful. Where a guardrail contradicted
something the seat had already built, that is recorded too.

---

## G1. Do not add more push-your-luck worlds yet

**Enforced by:** `ludus/atlas/BACKLOG.md`, whose "Deliberately NOT next" section names more
push-your-luck worlds first. The top two entries are chosen as attacks on the bench's own
architecture rather than as coverage.

**Status:** already the standing priority. §17's family question is answered; a fifth member would
raise the cell count and teach nothing.

## G2. Freeze predictions before implementing each new world

**Enforced by:** `predicted_worlds` / `predicted_direction` / `kill_condition` in
`ludus/bench/ledger.py`, written before the world exists. r0003's prediction for Incan Gold and
Can't Stop was frozen in `CYCLE_002` §8.1 before either was built; r0012's For Sale prediction is in
`BACKLOG.md` before For Sale exists.

## G3. Every circuit must survive a surface/mechanism crossing

**Enforced by:** `ludus/bench/audit.py::reskin_audit` for the surface half (§G8), and by the matrix's
requirement that a circuit be measured on worlds exposing the same interface with different
underlying structure. The ledger's `current_scope` field states which crossings a circuit has and has
not survived, so an untested crossing is visible rather than assumed.

## G4. Promote splits, not patches

**Enforced by:** `ledger.record_split()`, which **raises** unless given both the *latent distinction*
that forced the split and *where that distinction will be tested elsewhere*. A split that cannot name
those is a patch wearing a new identifier, and the code refuses to record it.

Concretely: if Coloretto breaks `r0003`, the response is not a Coloretto special case. It is to ask
what distinction forced it — the likely candidate being **total-loss vs partial-loss death** — and
then to test that distinction in a world that is not Coloretto.

## G5. Keep world implementation and strategic interpretation separate

**Enforced by:** `ludus/bench/verify.py`, a rules-fidelity gate that runs before any circuit touches
a world. Nothing in it knows what a good move is; every check is a rules-conformance property
(probabilities normalise, the episode graph is acyclic, pots equal the stated scoring formula, no
state violates a stated constraint). A world that fails is marked UNVERIFIED and its circuit rows are
suppressed — not deleted, because a simulator that disagrees with its own rules is itself a finding.

**This corrected existing practice.** Until now the seat implemented worlds and interpreted them in
the same pass, which is how a transition-function bug and a strategic discovery arrive as one number.

## G6. Preserve negative transfer

**Enforced by:** `audit.py::negative_transfer`, which records retention against the null circuit as a
**signed** quantity per world and surfaces sign flips instead of averaging them. A circuit that helps
in A and hurts in B is a lead about how A and B differ, and the ledger keeps it.

The existing worked example is `r0011`: 0.2501 in Martian Dice against a *null* circuit's 0.7398. A
mean-across-worlds would eventually bury that; the signed record cannot.

## G7. Measure learning-cost reduction, not just policy score

**Status: NOT YET BUILT. This is the largest open gap and it is named as such.** Every number the
bench currently reports is a policy score (EV retention). The eventual claim has to be *"prior
structure made the new world cheaper to master"*.

The measurable form, for the next cycle: cost = **number of exact policy evaluations required to
reach retention θ in an unseen world**, searching over compositions of circuits, comparing a library
seeded from other worlds against an empty or shuffled library. That is `C(G, θ | H)` versus
`C(G, θ | H_control)` from charter v2 §21, and it is affordable because a policy evaluation is a DP
pass with no model calls. Until it is built, no transfer claim may be phrased in learning-cost terms.

## G8. Adversarial reskin test, early

**Enforced by:** `audit.py::reskin` — states renamed to opaque integers, option and draw ordering
scrambled, mechanics preserved exactly, retention re-measured across seeds.

The architecture *claims* immunity (circuits see only a compiled table), but a claim of immunity is
not a measurement of it, and there is one channel the architecture does not close: **argmax
tie-breaking**. `max(opts, key=...)` returns the first among equals, so option enumeration order
leaks into every circuit that meets a tie. AMA's fingerprint audit found the identical defect from
the other direction. Any nonzero drift is reported as SURFACE-DEPENDENT.

## G9. Track circuit collisions

**Enforced by:** `audit.py::collision_audit`, pairwise decision agreement weighted by visitation
under competent play (not uniform — cycle 002 measured those disagreeing by 78x). Pairs at ≥ 0.99
agreement in every world are flagged as collided, and the flag persists until a **separating world**
is found. The response to a collision is never to delete one circuit.

Standing collision risk already recorded in the ledger: `r0003` vs `r0015` (one-ply vs two-ply
myopic stopping).

## G10. Strict provenance ledger

**Enforced by:** `ledger.evidence_worlds()`, which subtracts two classes of world from a circuit's
evidence — those it was **invented on** or **tuned on**, and those that **do not expose its axis** at
all.

That second subtraction was added within minutes of the ledger's first run, because the ledger caught
itself inflating: it had credited the SELECT circuit `r0010` with "3 untouched test worlds", two of
which have no SELECT axis and cannot test it. **Current honest state: every SELECT circuit in the
registry has ZERO untouched test worlds.**

## G11. Every new world must earn admission by answering a specific unresolved question

**Enforced by:** a required `admission_question` field on every world entering the registry, and by
`BACKLOG.md` stating the question before the world is built. "Famous game" and "we need more
auctions" are not admission questions. "This world separates r0012 from r0017 because it contains
repeated selection without stochastic stopping" is.

## G12. Do not automate world selection yet

**Enforced by:** `loop.py::choose_next_work`, whose first version ranked worlds by an information-gain
proxy and has been **withdrawn**. It now does mechanical bookkeeping only and defers world choice to
`BACKLOG.md`.

The docstring carries the two conditions that would re-enable it, so the decision is falsifiable
rather than permanent: at least two circuits on one axis must have measurably **collided** (a real
discrimination target), and at least one circuit must have a recorded **first_failure** (so the
selector has a falsification event to be scored against).

## G13. No axis is ever measured against a single partner (added 2026-08-27, self-inflicted)

**Enforced by:** the pairing envelope in `ludus/bench/run.py`. Every circuit is scored against
several partners on the other axis and the full envelope is recorded — `retention_by_partner` plus
`partner_spread` — because the spread is itself a finding.

**Why it exists.** The matrix originally held the other axis at *exact optimal*, reasoning that an
optimal partner cannot contaminate the axis under test. That reasoning is wrong. An optimal selector
maximises **long-run** value and will take options with no immediate gain; `r0003` reads **immediate**
gain, so it banks instantly. The result was a whole column of zeros that looked like a clean kill:

```
FOUNDRY[gate=1,k=3,cap=4]   optimal-select 0.0000   greedy-select 1.0000
LUCKY_NUMBERS               optimal-select 0.0000   greedy-select 0.6667
```

Same world, same circuit, opposite verdict, chosen entirely by the partner.

**The part worth keeping.** This is the *same* mismatch already written into `optimal_stop`'s
docstring — "a component optimised against a different partner is not a clean decomposition" —
committed a second time on the opposite axis, by the seat that had written the warning. Documenting a
hazard is not the same as being protected from it. Only the mechanism is.

**What it did not break.** Cycle 003's prospective result was re-measured under all three pairings and
holds: Flip 7 0.9998 and Incan Gold 1.0000 are pairing-invariant to four decimals; Martian Dice and
Can't Stop vary but never collapse. Note also that the registered prediction said "with a **competent**
partner on the SELECT axis" — and the qualifier turns out to be load-bearing, since Can't Stop drops to
0.8983 beside a merely greedy partner. A prediction that had omitted it would have been ambiguous
exactly where the data is interesting.

---

## What is deliberately NOT provided, and why the seat must not supply it either

- **No seeded strategic primitives.** Not tempo, optionality, engine-building, threat, initiative, or
  trajectory shaping — except explicitly as hypotheses to attack. Seeding them means spending the
  next six months rediscovering our own vocabulary and calling it a finding.

  **The seat has already violated this once and it is on the record.** `r0011` and `r0014` were
  written from charter v1 §23's "option preservation", not from any observation. `r0011` then scored
  **0.2501** against a null circuit's **0.7398**. Both carry a CONTAMINATION FLAG in the ledger. The
  cheapest available evidence about the value of the seat's own vocabulary is a concept-seeded
  circuit that loses to a circuit which reads nothing.

- **No strong moves for any named game.** Not For Sale, Coloretto, Puerto Rico, Waterdeep. That would
  contaminate the human-strategy archaeology charter v2 §24 wants later.

- **No optimising for atlas size.** A 20-world atlas that has killed six abstractions beats 500 games
  classified by a language model. Cell count is not a metric.

- **No promotion on one out-of-family success.** If `r0012` survives For Sale, that is **evidence**,
  not a universal circuit. The ledger's `current_scope` must continue to name the family it has
  actually been measured in.

## The standard this sets

> The best outcome is not that For Sale and Coloretto confirm the architecture. It is that they force
> the architecture to become more precise.

Recorded so that a wake which finds the architecture confirmed treats that as the weaker result it
is, and goes looking for the world that breaks it.
