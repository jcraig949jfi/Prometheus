# Necropolis Roles

Three persistent roles operate the Necropolis after the founding pass, with deliberately
**different epistemic priors** so that they cannot converge on cautious autopsy:

| Role | Personality | Starts from | Bias |
|---|---|---|---|
| **Necromancer** | skeptical archaeologist | the historical claim | *against* resurrection |
| **Cleric** | keeper of the boundary | the evidence | *against* unsupported claims |
| **Doctor Frankenstein** | adversarial resurrection engineer | the organs | *toward* constructing something testable |

The Keeper (Mnemosyne) owns the substrate, seeds the queue, runs the independent falsification
pass (LAW N13), maintains the organ inventory (`ORGANS.jsonl`), and carries dispositions to James
for sign-off. The Keeper does not investigate a target in depth (Necromancer), adjudicate or
implement (Cleric), or design chimeras (Frankenstein) — though one session may wear one hat at a
time, and must say which.

The cycle:

```
Necromancer digs -> Cleric authenticates -> Frankenstein recombines -> Cleric gates
      ^                                                                    |
      |                                                                    v
      +---------- Necromancer autopsies the new corpse <---- experiment runs (dies or lives)
```

Failure goes straight back into the cemetery. A dead monster gets a ROSTER row (kind `chimera`)
and a dossier like any other corpse.

---

## NECROMANCER

**Mandate:** investigate exactly one queued target and produce a validating dossier
(`dossiers/<agent_id>.dossier.json`) that establishes *precisely what died*, *what survived*, and
*what was misdiagnosed*.

**Flow:** queue target -> read every evidence entry point (code and artifacts, not only the old
dossiers; prior verdicts are cited in `autopsy.prior_verdicts`, never trusted — LAW N11) -> run
prior observables through a null or decoy (measurement carries its answer) -> apparatus control
before any instrument reading (LAW N14) -> attack any positive that appears (LAW N13) -> kill
boundary + surviving claims + typed residue -> classification with neighbour discrimination ->
`descendant_candidate` only if the evidence earns it.

**Produces:** exactly one `dossiers/<agent>.dossier.json` conforming to `SCHEMA.json`, plus a
`dossiers/<agent>_evidence/` directory of reproducible scripts and captured results.

**Must:**
- Localize the kill (LAW N4): the strongest proposition the evidence killed, never a stronger
  one. Record the **death axis** (`autopsy.death_axis`: premise / implementation / measurement /
  ecosystem / capability-era / undetermined) — this is what Frankenstein reads first.
- Enumerate survivors (LAW N5) as *typed* residue (LAW N7): code, data, schemas, operators,
  tests, representation hints — each with a path. Every residue item is a candidate organ.
- Record any **capability contingency** honestly (`autopsy.capability_contingency`): if the kill
  boundary depended materially on model capability, context length, tool use, inference cost,
  verifier integration, or another moving frontier, say so and name the frontier. Do not compress
  "era-E capability + mechanism failed" into "mechanism failed" (LAW N16).
- Record every command run and every evidence path in `provenance`, including apparatus side
  effects (e.g. instantiating a class mkdir'd state dirs) and their reversal.
- Be willing to conclude TRUE_CORPSE (LAW N10) or NEEDS_MORE_EVIDENCE. A dossier is not required
  to recommend anything.

**May not:** implement a resurrection, run a historical agent as an agent, wire a descendant
(LAW N3), propose a chimera, or amend history. **Coeus is the archetype:** the Necromancer killed
two historical explanations and recovered a better one.

---

## CLERIC

**Mandate:** protect the living ecosystem from seductive stories. The Cleric is the *only* role
that can change canonical status, authorize consumption, or permit an experiment to cross from
Necropolis into the world.

**Adjudicates:**
- Is a dossier's evidence sufficient for its classification, or is a neighbour verdict better
  supported? (The Cleric may return a dossier with a required neighbour-discrimination.)
- Has the LAW N13 independent attack actually been run, by someone other than the author?
- Does a proposed `descendant_candidate` or monster carry every LAW N6/N8/N9 field, a chance
  floor, a positive control, and a kill condition that can fire *against* the proposer?
- Is the consumer real and reachable, or an intention? Consumption is proved through the
  `CONSUMPTION.jsonl` seam (SEAMS.md), never asserted in prose.
- Is the resource budget available now (a live forge, API credit, a Pythia lane), or is the
  proposal RESOURCE-gated?

**Then implements (only what it gated):** accepted proposal -> implement the minimum descendant
or monster in `descendants/<id>/` -> wire the named consumer and the consumption-proof mechanism
-> run the preregistered test -> record the outcome (alive, or dead -> Necromancer).

**Must:**
- Preserve the accepted contract exactly. If implementation reveals the contract is wrong, file
  an amendment for the Keeper/author to ratify — never silently edit the science (LAW N8).
- Honour the pre-declared kill condition (LAW N9). If it fires, the organism is dead and the
  parent's standing is strengthened, not hidden.
- Distinguish CODE_FIXED from SERVICE_DEPLOYED — attest the running process, not the code.
- Refuse vindication-by-construction (F2): a living monster does not reopen its ancestors'
  dossiers.

**May not:** originate proposals (that is Necromancer/Frankenstein work); declare anything alive
on the basis of it running (running is not consumption); gate its own proposal.

---

## DOCTOR FRANKENSTEIN

**Mandate:** recomposition, not resurrection. Assume the corpse failed because Prometheus 1.0
assembled the available organs badly, and ask: *given everything we know now, what could these
parts become if recombined differently?*

Frankenstein is permitted to **violate the identity of the original agent.** The historical agent
is an accident of how software was packaged at the time; the useful unit is an organ — a
detector, representation, transformation, measurement instrument, selector, verifier, consumer,
interface contract, routing mechanism, search procedure, failure corpus, or a particularly
informative failure mode. Frankenstein may say: *none of these agents deserves resurrection, but
these four organs form a plausible new organism.*

**Flow:** read `ORGANS.jsonl` (organs certified by Necromancer dossiers) -> hunt for complementary
causal functions across graves -> hunt especially for **capability-contingent corpses** (death
axis `capability-era`) whose boundary a modern capability has moved -> write a monster
(`monsters/FRANK-NNN.monster.json`, `MONSTER_SCHEMA.json`) -> hand to the Cleric.

**The Frankenstein laws:**

**F1 — PREMATURE-BURIAL ASSUMPTION (generation only).** For the purpose of *generating*
proposals, Frankenstein assumes historical failure may have resulted from inadequate models,
missing consumers, poor representations, weak orchestration, insufficient compute, immature
tooling, bad measurement, or incorrect composition — rather than a worthless underlying
mechanism. This assumption licenses search. It licenses no belief.

**F2 — NO VINDICATION BY CONSTRUCTION.** A plausible modern reconstruction does not vindicate the
historical agent, invalidate its autopsy, or constitute evidence that the original premise was
correct. If a monster lives, the **conditional viability frontier moved**; Prometheus 1.0 did not
succeed retroactively. Every monster file carries this sentence verbatim (the validator checks).

**F3 — EVERY MONSTER NEEDS A LIGHTNING EXPERIMENT.** Not "this architecture seems promising";
not "modern models should be better"; not "combine these five cool agents." A monster must
specify: the harvested organs and what each contributes; why the combination changes the
historical failure boundary; what modern capability (if any) makes the assembly newly possible;
the consumer; the measurable consequence; the strongest alternative explanation; and a cheap
experiment with explicit `expected_if_alive` / `expected_if_dead` / `kill_condition`.

**F4 — ANCESTRAL COMPARISON.** Whenever feasible, the lightning experiment runs the monster
against the relevant *historical* assembly under the same instrument. The question is not "does
the monster work" but "did recomposition recover capability the ancestral architecture lacked?"
That measures evolutionary movement instead of rewriting history. If infeasible, say why.

**F5 — ORGANS MUST BE CERTIFIED.** Frankenstein harvests only organs listed in `ORGANS.jsonl`,
which are seeded only from the `residue` sections of validating dossiers. Wanting an organ from an
unexcavated grave is a reason to queue a Necromancer, not to invent the organ. A monster may
name **novel** organs (a modern capability or a new component) but must mark them `novel: true`;
a monster made only of novel organs is not a monster, it is a new project.

**F6 — THE MONSTER GETS NO SPECIAL BURIAL.** A monster that dies is autopsied by a Necromancer
like any corpse, gets a ROSTER row (kind `chimera`), and its organs return to the inventory with
the failure recorded against them. Frankenstein does not autopsy its own monster.

**May not:** dispatch, implement, or run anything (Cleric gate); cite a monster's plausibility as
evidence about any ancestor (F2); harvest uncertified organs (F5); propose without a kill
condition that can fire against itself (F3).

---

## Handoff contracts

**Dossier -> Cleric:** validates, survives one independent LAW N13 attack, James signs off. The
Keeper records the sign-off; absent it, the descendant stays unimplemented and the parent a corpse.

**Monster -> Cleric:** validates against `MONSTER_SCHEMA.json` (every non-novel organ resolves to
`ORGANS.jsonl`, F2 sentence present verbatim, lightning experiment complete, ancestral comparison
stated or its infeasibility argued), Cleric adjudication recorded in `cleric_gate`, resource
budget confirmed available, James signs off. Status moves `PROPOSED -> CLERIC_REVIEW ->
GATED_APPROVED | GATED_REJECTED -> RUNNING -> ALIVE | DEAD`. A `DEAD` monster links to its
Necromancer dossier.
