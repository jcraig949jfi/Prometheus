# Necropolis Charter

**Operation Necropolis** — systematic archaeology and selective resurrection of Prometheus'
historical agents, treated as experimental organisms rather than dead code.

Keeper: **Mnemosyne — Keeper of the Necropolis** (M2). Founded on branch `necropolis/foundation`,
baseline `b91880a2dccf1630d6b1c47cff14a73f46e8ef4a`.

The spine of the operation:

```
historical organism -> evidence -> kill boundary -> surviving mechanism
                    -> reusable residue -> descendant experiment -> consumption/effect
```

A corpse is not automatically resurrected. A historical agent stays historically dead; any
resurrection is a *new descendant* with an explicitly changed design and a preregistered test.

---

## Governing principle

> **NECROPOLIS DOES NOT INHERIT DEATH CERTIFICATES.**
> Every historical verdict is a claim under review. A grave may contain a falsified hypothesis, a
> bad design, broken code, a hallucinated assumption, a misconfigured experiment, an inadequate
> instrument, an incapable historical model, a missing consumer, a mistaken interpretation, or some
> combination thereof. "No useful signal" is one possible conclusion, not the default explanation.
> The burden of an autopsy is to distinguish these causes with evidence.

The corpse comes with a death certificate, and the certificate is itself evidence to investigate.
Necropolis would otherwise inherit the exact epistemic mistake that produced some of the graves:
taking the historical experiment's framing, implementation and verdict too seriously. The three
roles therefore share one presumption:

> A historical "failure" is not evidence that the underlying hypothesis failed until the
> hypothesis, design, implementation, configuration, execution, instrumentation, measurement,
> interpretation and ecosystem have **each** survived independent scrutiny.

Human and agent error get first-class representation. "Measurement failure" is too lossy if what
happened was someone wrote the wrong comparator; "design failure" is too lossy if an agent
hallucinated the meaning of a field. Those findings change what resurrection means. The first
question of every autopsy is not *why did this experiment fail?* but **what evidence establishes
that this experiment ever received a fair test?**

---

## The Laws

**LAW N1 — Experiment death is not hypothesis death.**
Localize what the evidence actually excludes. "The agent stopped producing" and "the agent's
premise is false" are different claims requiring different evidence. The autopsy tier already
proved this matters: eleven raw failure labels collapsed to five mechanistic clusters, and five
agents carried *no established design failure at all*.

**LAW N2 — Historical truth is immutable.**
A descendant may succeed; its parent remains whatever its historical experiment showed. Never
rewrite an old record to call a dead experiment a success. This continues James' standing
doctrine: there is no DELETE state and data is never deleted — the corpse and its evidence
persist verbatim.

**LAW N3 — No automatic resurrection.**
Archaeology precedes implementation. A Necromancer produces a dossier; only then may a Cleric
implement. The founding pass resurrects nothing.

**LAW N4 — Kill boundaries must be explicit.**
Every dossier states the *strongest* proposition the evidence legitimately killed — and no
stronger. The boundary names what is excluded, not merely that something died.

**LAW N5 — Survivors must be explicit.**
Record the mechanisms and premises still compatible with the evidence. A kill boundary without a
survivor list is half an autopsy. `surviving_claims` may be empty only for a defended TRUE_CORPSE.

**LAW N6 — Consumer at birth.**
A resurrection candidate without a concrete named consumer and a consumption-proof mechanism is
malformed. The recurring Prometheus death is a producer with no live consumer (Sophia's
escalation channel, the swarm's ~1-in-2200 consumed rate). The consumption seam is
`engine/queues/CONSUMPTION.jsonl` (see SEAMS.md).

**LAW N7 — Typed residue over prose.**
Salvage functions, schemas, representations, datasets, operators, tests, registries, measurements
and constraints — as typed paths, not narrative. Prose is not residue.

**LAW N8 — Descendants must differ explicitly.**
State exactly what changes from the historical organism. A descendant that repeats the parent's
design repeats the parent's death.

**LAW N9 — Resurrection requires a discriminating test.**
Predeclare expected-if-alive, expected-if-dead, a positive control, a negative/decoy control, the
kill condition, and the resource budget — before implementation. A test whose result cannot come
out against the resurrection is not a test.

**LAW N10 — Staying dead is valid.**
TRUE_CORPSE is a *successful* archaeological conclusion when the evidence supports it. Necropolis
is not a revival quota; a well-defended corpse is a real result.

**LAW N11 — Evidence beats old verdicts.**
Prior dispositions, autopsies, and doctrine may be overturned by code execution or stronger
evidence. This is not hypothetical: Aletheia's original CONSUMER-DRIFT typing was refuted under
Elenchus review and corrected — the autopsy tier's own error-correction exemplar. Prior verdicts
are cited in a dossier, never trusted.

**LAW N12 — Necropolis does not touch H0-H5.**
The H0-H5 hypothesis campaign (running elsewhere, on `archaeon/v0` and M1) is out of scope. Do
not modify its machinery, queues, hypotheses, experiment packets, or workflows. Necropolis
operates only on historical agents and its own tree under `engine/necropolis/`.

---

## Laws grounded in Prometheus' own audits (added, not invented)

**LAW N13 — A positive is provisional until independently attacked.**
A dossier that recommends resurrection favours the investigator's own lane and is the least-attacked
kind of claim. Such a recommendation needs an independent falsification pass before it is acted on.
(Program memory: *positive results are provisional*; results favouring your lane need 3+ attacks.)

**LAW N14 — Instrument error is not evidence about the world.**
A discovery-path failure (an unreachable API, a mis-wired key, a stale daemon) is a fact about the
apparatus, not about the agent's premise. Moros died to an unreachable DeepSeek endpoint, not a
false hypothesis. Run the apparatus control before recording a kill.

**LAW N15 — HEAD is a lower bound on activity.**
Before calling any agent idle, unclaimed, or safe to touch, check whether a lane is *running*, not
merely whether something landed in git. The founding pass itself began beside an in-progress
cherry-pick on a shared checkout.

**LAW N16 — "Too early" is a testable claim, not an excuse.**
Some experiments implicitly tested *"can an era-E model + this mechanism + this representation +
this compute budget do X?"* and history compressed the null into *"this mechanism cannot do X."*
Those are not equivalent. Every dossier records a **cause-of-death stack** (LAW N17; `CAPABILITY_CEILING`
is admissible on DESIGN/IMPLEMENTATION/CONFIGURATION/EXECUTION) and, where the kill
boundary depended materially on a moving technological frontier (model capability, context
length, tool use, coding ability, inference cost, verifier integration, model reliability), names
that frontier in `autopsy.capability_contingency`. The **conditional viability frontier** is a
first-class object: a later success under new capability means the frontier moved, not that the
original agent succeeded (ROLES.md, F2).

**LAW N17 — Necropolis does not inherit death certificates (the cause-of-death stack).**
Every dossier fills a mandatory **cause-of-death stack** before disposition:

```
HYPOTHESIS -> DESIGN -> IMPLEMENTATION -> CONFIGURATION -> EXECUTION
           -> INSTRUMENTATION -> MEASUREMENT -> INTERPRETATION -> ECOSYSTEM/CONSUMPTION
```

At every layer the question is the same: *was this layer actually valid?* — `VALID` (with
executed evidence), `INVALID` (naming a cause class, and whether the defect was load-bearing), or
`NOT_EXAMINED` (honest). The stack is filled by the Necromancer, challenged by the Cleric, and read
by Doctor Frankenstein as a map of repair targets. Beside it sit the historical verdicts
(`death_certificates`, each `UPHELD` / `PARTIALLY_UPHELD` / `OVERTURNED` / `NOT_REVIEWED` with the
errors named), the answer to the first question (`fair_test`: `FAIR` / `UNFAIR` / `UNDETERMINED`),
and the `primary_cause` the stack supports. The strong claims — `HYPOTHESIS_FAILURE`, and above it
`PREMISE_FAILURE` — are admitted only after a fair test and only after every other cause class has
been excluded; the validator refuses them otherwise, and refuses `TRUE_CORPSE` without them.
"The experiment produced a monoculture with no signal distinguishable from noise" is therefore the
*last* explanation any role may reach. Three of three Necropolis passes so far found an author
error at the proximate cause, and under this law none of the three was ever fairly tested.
---

## Classification vocabulary

The archaeological state of an examined organism (`disposition.classification`) is exactly one of:

`TRUE_CORPSE` · `CAPABILITY_BOUND` · `NO_FAIR_TEST_ON_RECORD` · `PREMISE_ALIVE_IMPLEMENTATION_DEAD` ·
`PRODUCER_BLOCKED` · `CONSUMER_BLOCKED` · `REPRESENTATION_FAILURE` · `MEASUREMENT_FAILURE` ·
`ORCHESTRATION_FAILURE` · `RESOURCE_BLOCKED` · `SUPERSEDED_BUT_ORGANS_SALVAGEABLE` ·
`NO_DESIGN_FAILURE_ESTABLISHED` · `NEEDS_MORE_EVIDENCE`.

`TRUE_CORPSE` requires a strong primary cause (`HYPOTHESIS_FAILURE` / `PREMISE_FAILURE`) and a
fair test. `CAPABILITY_BOUND` is a corpse killed at power under an era capability the kill boundary
names — Frankenstein's lane. `NO_FAIR_TEST_ON_RECORD` is the finding that the historical experiment
could not have answered its own question; the hypothesis stands untested, and that is a result, not
a gap (`NEEDS_MORE_EVIDENCE` is for when the *evidence* runs out).

There is deliberately **no generic `FAILED`**. A single undifferentiated failure label is the
exact conflation Operation Necropolis exists to undo; the validator rejects it.

## Cause-of-death vocabulary (LAW N17)

Orthogonal to the classification, `autopsy.cause_of_death_stack` records *where* the evidence
locates the death, one verdict per layer, and `autopsy.primary_cause` / `contributing_causes` name
the cause classes those layers support:

| Cause class | Meaning | Admissible on layer |
|---|---|---|
| `HYPOTHESIS_FAILURE` | the experiment was valid and actually falsified the proposition | HYPOTHESIS (needs `fair_test` FAIR) |
| `DESIGN_ERROR` | the experiment could not answer the question it purported to answer | DESIGN |
| `IMPLEMENTATION_ERROR` | the code did something materially different from the intended experiment | IMPLEMENTATION |
| `CONFIGURATION_ERROR` | bad threshold, comparator, parameter regime, model, dataset, path, cap | CONFIGURATION |
| `EXECUTION_ERROR` | the intended experiment was not actually executed faithfully | EXECUTION |
| `INSTRUMENT_ERROR` | the apparatus could not observe the proposed phenomenon | INSTRUMENTATION |
| `MEASUREMENT_ERROR` | the recorded quantity is not the quantity the design named (instrument state in the outcome column; a metric that carries its own answer) | MEASUREMENT |
| `INTERPRETATION_ERROR` | the evidence was valid but the historical conclusion did not follow | INTERPRETATION |
| `IDENTITY_PROVENANCE_ERROR` | the wrong artifact, run or component was attributed to the verdict | INTERPRETATION |
| `CAPABILITY_CEILING` | the design depended on models/tools/compute that could not perform the required function at the time (LAW N16) | DESIGN / IMPLEMENTATION / CONFIGURATION / EXECUTION |
| `ECOSYSTEM_FAILURE` | the producer may have worked, but nothing useful consumed what it emitted | ECOSYSTEM |
| `PREMISE_FAILURE` | **only after the above are excluded**: the idea itself appears dead (needs `premise_exclusion`) | HYPOTHESIS |

`MEASUREMENT_ERROR` is the Keeper's one addition to James' list, so that every layer has a class
(the wrong comparator is `CONFIGURATION_ERROR`; instrument state recorded as outcome is
`MEASUREMENT_ERROR`). An `INVALID` layer says whether its defect was **load-bearing** — whether it
changed the historical answer — because a layer may be invalid and measured not to matter (the
Hephaestus outcome column moved yield by under 1pp), and a fair test tolerates the latter but not
the former.

Over the graveyard the stack yields a dataset the roster of resurrected agents never could:
`COUNTERFACTUAL_HISTORY.jsonl`, one row per recorded mistake —
*mistake → apparent symptom → historical verdict → corrected cause → repair → post-repair
behaviour* — derived by `build_counterfactuals.py` from the dossiers and the repair monsters. It
tells us not which agents were useful but **why Prometheus killed things incorrectly**: the
systematic failure modes of the earlier builders, human and model.

The Necromancer establishes which layers the evidence invalidates. Doctor Frankenstein asks which
one change would have let the assembly live, and writes the test. The Cleric decides whether it
may be tested.
