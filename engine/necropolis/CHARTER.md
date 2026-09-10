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

---

## Classification vocabulary

The archaeological state of an examined organism (`disposition.classification`) is exactly one of:

`TRUE_CORPSE` · `PREMISE_ALIVE_IMPLEMENTATION_DEAD` · `PRODUCER_BLOCKED` · `CONSUMER_BLOCKED` ·
`REPRESENTATION_FAILURE` · `MEASUREMENT_FAILURE` · `ORCHESTRATION_FAILURE` · `RESOURCE_BLOCKED` ·
`SUPERSEDED_BUT_ORGANS_SALVAGEABLE` · `NO_DESIGN_FAILURE_ESTABLISHED` · `NEEDS_MORE_EVIDENCE`.

There is deliberately **no generic `FAILED`**. A single undifferentiated failure label is the
exact conflation Operation Necropolis exists to undo; the validator rejects it.
