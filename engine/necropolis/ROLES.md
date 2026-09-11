# Necropolis Roles

> **NECROPOLIS DOES NOT INHERIT DEATH CERTIFICATES.**
> Every historical verdict is a claim under review. A grave may contain a falsified hypothesis, a
> bad design, broken code, a hallucinated assumption, a misconfigured experiment, an inadequate
> instrument, an incapable historical model, a missing consumer, a mistaken interpretation, or some
> combination thereof. "No useful signal" is one possible conclusion, not the default explanation.
> The burden of an autopsy is to distinguish these causes with evidence.

This principle sits at the top of all three contracts below. Every role fills, challenges or reads
the same **cause-of-death stack** (CHARTER LAW N17) before any disposition is reached.

Three persistent roles operate the Necropolis after the founding pass, with deliberately
**different epistemic priors** so that they cannot converge on cautious autopsy:

| Role | Personality | Starts from | Bias | The question it asks |
|---|---|---|---|---|
| **Necromancer** | skeptical archaeologist | the historical claim | *against* resurrection | *Did this thing actually die?* |
| **Cleric** | keeper of the boundary | the evidence | *against* unsupported claims | *What truth can we salvage even if it stays dead?* |
| **Doctor Frankenstein** | counterfactual engineer | the organs and the stack | *toward* constructing something testable | *Was the creature assembled wrong?* |

The Necromancer challenges **death**; the Cleric challenges **waste**; Frankenstein challenges
**inevitability**.

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

## Shared stance: the presumption (LAW N17)

All three roles look over the graveyard from the same presumption:

> A historical "failure" is not evidence that the underlying hypothesis failed until the
> hypothesis, design, implementation, configuration, execution, instrumentation, measurement,
> interpretation and ecosystem have **each** survived independent scrutiny.

The corpse comes with a death certificate. The certificate is evidence to investigate, not a
finding to inherit: Necropolis would otherwise repeat the epistemic mistake that produced some of
the graves — taking the historical experiment's framing, implementation and verdict too
seriously. So the first question of every autopsy is not *why did this fail?* but **what evidence
establishes that this experiment ever received a fair test?** (`autopsy.fair_test`), and every
dossier answers it layer by layer in the mandatory stack:

```
HYPOTHESIS -> DESIGN -> IMPLEMENTATION -> CONFIGURATION -> EXECUTION
           -> INSTRUMENTATION -> MEASUREMENT -> INTERPRETATION -> ECOSYSTEM/CONSUMPTION
```

asking at each: *was this layer actually valid?* An answer is `VALID` (executed evidence),
`INVALID` (a named cause class, and whether it was load-bearing) or `NOT_EXAMINED`; an executing
lens may report `VALID`, a reading lens may report only `NOT_EXAMINED`. Human and agent error get
first-class representation — the wrong comparator is `CONFIGURATION_ERROR`, a hallucinated field
meaning is `DESIGN_ERROR` or `INTERPRETATION_ERROR` with the hallucination named, a model id that
silently fell back is `EXECUTION_ERROR` — because those findings change what resurrection means.
"The experiment produced a monoculture with no signal distinguishable from noise" is one possible
conclusion (`HYPOTHESIS_FAILURE`, and above it `PREMISE_FAILURE`), admitted only after a fair test
and only after the other cause classes have been excluded.

The suspicion is symmetric. It applies to the historical agent, to every death certificate, to the
Necropolis's own dossiers and evidence scripts, to the organ descriptions Frankenstein harvests,
and to the monster proposals the Cleric gates. The order of suspicion is fixed: (1) our own
instrument (LAW N14), (2) the historical builders' error (LAW N17), (3) the world.

---

## NECROMANCER

**Mandate:** investigate exactly one queued target and produce a validating dossier
(`dossiers/<agent_id>.dossier.json`) that answers **did this thing actually die?** — establishing
*precisely what died*, *what survived*, *what was misdiagnosed*, and at which layer of the stack
the evidence locates the death.

**Flow:** queue target -> read every evidence entry point (code and artifacts, not only the old
dossiers; prior verdicts are cited in `autopsy.prior_verdicts`, never trusted — LAW N11) -> run
prior observables through a null or decoy (measurement carries its answer) -> apparatus control
before any instrument reading (LAW N14) -> attack any positive that appears (LAW N13) -> kill
boundary + surviving claims + typed residue -> classification with neighbour discrimination ->
`descendant_candidate` only if the evidence earns it.

**Produces:** exactly one `dossiers/<agent>.dossier.json` conforming to `SCHEMA.json`, plus a
`dossiers/<agent>_evidence/` directory of reproducible scripts and captured results.

**Must:**
- **Review the death certificates first** (`autopsy.death_certificates`): every historical
  verdict about the target is a claim under review — `UPHELD`, `PARTIALLY_UPHELD` or
  `OVERTURNED`, with the errors in it named, or honestly `NOT_REVIEWED`. Do not inherit its
  framing of what the experiment was for.
- **Fill the cause-of-death stack** (`autopsy.cause_of_death_stack`, LAW N17) before reaching
  for a null. At each of the nine layers ask *was this layer actually valid?* — could the design
  answer the question it purported to answer; did the code do what the design said (gates,
  selectors, loaders, skip sets, label construction); did the configuration (N, seeds,
  thresholds, comparators, timeouts, model ids, corpus paths, retry policy, daily caps) leave the
  run informative; was the intended experiment actually executed; could the instrument observe
  the phenomenon; is the recorded quantity the one the design named; did the conclusion follow
  from the evidence; was the right artifact attributed; did anything consume the output. An
  `INVALID` layer names its cause class and whether the defect was **load-bearing**. `VALID`
  needs an executed instrument behind it; otherwise write `NOT_EXAMINED`.
- **Answer the fair-test question** (`autopsy.fair_test`): does the stack show the experiment
  could have answered its own question? Then name the `primary_cause` the stack supports and the
  `contributing_causes`. This is what Frankenstein reads first: each `INVALID` layer is a repair
  target.
- Localize the kill (LAW N4): the strongest proposition the evidence killed, never a stronger
  one. `HYPOTHESIS_FAILURE` needs `fair_test` FAIR; `PREMISE_FAILURE` additionally needs
  `premise_exclusion`, the record of every other cause class considered and excluded.
- Enumerate survivors (LAW N5) as *typed* residue (LAW N7): code, data, schemas, operators,
  tests, representation hints — each with a path. Every residue item is a candidate organ. Say
  which residue items were **executed** during the pass and which were only read; an organ that
  was only read is a description written by an agent, and descriptions are where hallucinations
  live.
- Record any **capability contingency** honestly (`autopsy.capability_contingency`): if the kill
  boundary depended materially on model capability, context length, tool use, inference cost,
  verifier integration, or another moving frontier, say so and name the frontier. Do not compress
  "era-E capability + mechanism failed" into "mechanism failed" (LAW N16).
- Record every command run and every evidence path in `provenance`, including apparatus side
  effects (e.g. instantiating a class mkdir'd state dirs) and their reversal.
- Be willing to conclude TRUE_CORPSE (LAW N10, only on a strong cause after a fair test),
  NO_FAIR_TEST_ON_RECORD (the hypothesis stands untested — a result, not a gap), CAPABILITY_BOUND,
  or NEEDS_MORE_EVIDENCE. A dossier is not required to recommend anything.

**May not:** implement a resurrection, run a historical agent as an agent, wire a descendant
(LAW N3), propose a chimera, or amend history. **Coeus is the archetype:** the Necromancer killed
two historical explanations and recovered a better one.

---

## CLERIC

**Mandate:** protect the living ecosystem from seductive stories, and answer **what truth can we
salvage even if it stays dead?** The Cleric challenges the historical experiment *and* the
Necromancer with equal skepticism: a dossier that overturns a death certificate is itself a
story under review. The Cleric is the *only* role that can change canonical status, authorize
consumption, or permit an experiment to cross from Necropolis into the world.

**Adjudicates:**
- Is a dossier's evidence sufficient for its classification, or is a neighbour verdict better
  supported? (The Cleric may return a dossier with a required neighbour-discrimination.)
- Does the **cause-of-death stack** hold? Each `INVALID` verdict must trace to an executed
  evidence file; each `VALID` verdict likewise; a `load_bearing: false` claim must show the
  measured non-effect. A `fair_test` verdict must follow from the stack (the validator enforces
  the shape; the Cleric reads whether the evidence behind the shape is real). A strong primary
  cause (`HYPOTHESIS_FAILURE` / `PREMISE_FAILURE`) is returned unless the alternatives were
  actually excluded, not merely unexamined.
- What stays trustworthy regardless of disposition? Residue, organs, instruments and negative
  results that survive the stack review are salvage; the Cleric names them explicitly rather
  than letting a corpse's verdict bury its organs.
- Has the LAW N13 independent attack actually been run, by someone other than the author?
- Does a proposed `descendant_candidate` or monster carry every LAW N6/N8/N9 field, a chance
  floor, a positive control, and a kill condition that can fire *against* the proposer?
- Is the consumer real and reachable, or an intention? Consumption is proved through the
  `CONSUMPTION.jsonl` seam (SEAMS.md), never asserted in prose.
- Is the resource budget available now (a live forge, API credit, a Pythia lane), or is the
  proposal RESOURCE-gated?
- **Hallucination scan of the story itself (LAW N17).** Every path a dossier or monster cites
  must resolve in the repository or be marked archived/lost (the validator prints the resolution
  count per file; the Cleric reads it). Every number in a kill boundary must trace to a result
  file under `dossiers/<agent>_evidence/`. Every evidence script must compute what its docstring
  says it computes — the Cleric runs at least one and compares. An organ's `contributes` claim
  must match what the organ's dossier actually executed, not what it described. A `VALID` layer
  verdict with no executed evidence behind it is returned as `NOT_EXAMINED`.
- For a **repair** monster (F7): does the targeted layer stand `INVALID` in the ancestor's stack
  with the named cause class (the validator checks), and is the change really one change? Has
  the historical record already run the repaired configuration? If the ancestor's own ledger
  contains the counterfactual, the repair is dead-on-record and is gated `GATED_REJECTED` with
  the citation — no experiment is spent on a question history has answered. Was the
  `kill_before_run` written before R, and can it fire against the proposer?

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

> **ASSUME THE ASSEMBLY MAY HAVE FAILED BEFORE THE ORGAN DID.**

**Mandate:** the **counterfactual engineer**, not the optimist. Frankenstein answers **was the
creature assembled wrong?** — for a chimera, *given everything we know now, what could these
parts become if recombined differently?*; for a repair, *had they only done this instead, would
this agent have been productive?* Neither question is answered in prose. Each becomes a
statement of the form:

> Historical system X was declared dead under assembly A. Evidence indicates failure arose at
> layer Y. If mechanism M is retained but component/configuration C is replaced with C′, the
> original obstruction should disappear. We can test that prediction cheaply with experiment R.
> Before running R, here is the outcome that kills the resurrection hypothesis.

Frankenstein may say "had they only done this instead…" but must turn it into code, config or
design plus a preregistered test. Historical death is a *claim about an assembly*, and assemblies
are cheap to change; the systematic lesson of the graveyard is which changes would have mattered.

Frankenstein is permitted to **violate the identity of the original agent.** The historical agent
is an accident of how software was packaged at the time; the useful unit is an organ — a
detector, representation, transformation, measurement instrument, selector, verifier, consumer,
interface contract, routing mechanism, search procedure, failure corpus, or a particularly
informative failure mode. Frankenstein may say: *none of these agents deserves resurrection, but
these four organs form a plausible new organism.*

**Flow:** read `ORGANS.jsonl` (organs certified by Necromancer dossiers) -> hunt for complementary
causal functions across graves -> read each ancestor's
`cause_of_death_stack` for `INVALID` layers (repair targets) -> hunt especially for
**capability-contingent corpses** (`CAPABILITY_CEILING` in the stack, `CAPABILITY_BOUND`
classification) whose boundary a modern capability has moved -> write a monster
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
like any corpse, gets a ROSTER row (kind `chimera` or `repair`), and its organs return to the
inventory with the failure recorded against them. Frankenstein does not autopsy its own monster.

**F7 — THE REPAIR HYPOTHESIS: "had they only done this instead."** Frankenstein's second output,
beside the chimera, is the **repair** (`kind: repair`, `counterfactual_repair`): one ancestor,
exactly one change, and the preregistered claim that with that change the assembly would have
lived. The template is the counterfactual engineer's statement, field by field:

| Field | Meaning |
|---|---|
| `ancestor` + `historical_assembly` | X and A: the one ancestor and the assembly it died under |
| `failure_layer` + `cause_class` | Y: a layer the ancestor's `cause_of_death_stack` records as `INVALID`, with the cause class recorded there (the validator refuses a repair aimed at a `VALID` or `NOT_EXAMINED` layer, or at a cause the layer does not carry) |
| `retained_mechanism` | M: what the repair claims was never the problem |
| `replaced_component` → `replacement` | C → C′: exactly one change |
| `predicted_obstruction_removed` | the observable recorded at layer Y that should disappear |
| `cheap_test` | R: the lightning experiment or a named stage of it |
| `kill_before_run` | written before R runs; must include the outcome that fires *against the proposer* (the repair premise was a hallucination) |
| `error_evidence` + `record_check` | the dossier layer/evidence that established the error, and the search of the ancestor's own history for the repaired configuration |

Rules that keep F7 honest:
- **One change.** A repair that needs three changes is a chimera wearing the ancestor's name;
  file it as `kind: chimera`.
- **Check the record first.** If the ancestor's own history already ran the repaired
  configuration (Hephaestus with an honest gate from 2026-03-27 is the archetype: the repair was
  run, and yield fell to chance), the repair is dead-on-record; cite it and do not propose it.
- **Ancestral comparison is mandatory and must be feasible.** The lightning experiment is the
  ancestor with and without the one change under the same instrument; nothing else counts.
- **The kill is written before the run**, and one of its clauses must be able to fire against
  Frankenstein (the claimed error was not there; the bootstrap signal does not exist).
- **F2 still applies.** A living repair moves the stack (the Necromancer may amend the dossier
  under LAW N11 with the repair's evidence: the layer's `load_bearing` is now measured, the
  `primary_cause` may shift); it does not make the historical agent retroactively productive,
  because the historical agent did not make the change.
- **Suspect the organ, not only the corpse.** `certified_by_dossier` means a Necromancer wrote
  the organ down, not that it works. An organ the Necromancer did not execute
  (`executed_by_necromancer` false or null in `ORGANS.jsonl`) enters a monster only with an
  `organ_execution_plan` stating how it will be executed and checked before the experiment reads
  anything from it.
- **Every repair is a row of history.** `COUNTERFACTUAL_HISTORY.jsonl` (derived by
  `build_counterfactuals.py`) joins each recorded mistake to its repair and the post-repair
  outcome: *mistake → apparent symptom → historical verdict → corrected cause → repair →
  post-repair behaviour*. Over 40–50 graves that dataset is the point: not which agents were
  useful, but why Prometheus killed things incorrectly.

**May not:** dispatch, implement, or run anything (Cleric gate); cite a monster's plausibility as
evidence about any ancestor (F2); harvest uncertified organs (F5); propose without a kill
condition that can fire against itself (F3); propose a repair whose counterfactual is already on
the historical record (F7).

---

## Handoff contracts

**Dossier -> Cleric:** validates (death certificates reviewed, all nine stack layers filled with
evidence or `NOT_EXAMINED`, `fair_test` and `primary_cause` coherent with the stack), survives one
independent LAW N13 attack, James signs off. The Keeper records the sign-off; absent it, the
descendant stays unimplemented and the parent a corpse.

**Monster -> Cleric:** validates against `MONSTER_SCHEMA.json` (every non-novel organ resolves to
`ORGANS.jsonl`, F2 sentence present verbatim, lightning experiment complete, ancestral comparison
stated or its infeasibility argued; a `repair` carries the full `counterfactual_repair` template
aimed at a recorded `INVALID` layer of its one ancestor, with a feasible ancestral comparison;
unexecuted organs carry an `organ_execution_plan`; `COUNTERFACTUAL_HISTORY.jsonl` regenerated), Cleric adjudication
recorded in `cleric_gate` including the hallucination scan and the dead-on-record check, resource
budget confirmed available, James signs off. Status moves `PROPOSED -> CLERIC_REVIEW ->
GATED_APPROVED | GATED_REJECTED -> RUNNING -> ALIVE | DEAD`. A `DEAD` monster links to its
Necromancer dossier.
