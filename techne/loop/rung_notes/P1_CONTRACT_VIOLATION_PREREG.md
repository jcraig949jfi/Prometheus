# P₁ — Producer/consumer contract violation: adversarial test of a CANDIDATE signature

Cycle 044. Written and committed **before any outcome was inspected**.

## P₀ is frozen, not amended

Cycle 043 pre-registered a population of 4 (`SCHEMA_DRIFT_SWEEP_PREREG.md`). Three of the four
turned out unmeasurable.

> **P₀ FAILED FEASIBILITY.** Recorded as a feasibility failure and left exactly as written.

The doctrine, adopted: **a feasibility failure may terminate a pre-registration but must not
mutate it.** Silently widening P₀ after seeing which cases exist is outcome-conditioned redesign,
which is the thing pre-registration exists to prevent. Starting a *new* pre-registered experiment
in the same cycle is legitimate; editing the old one is not. P₀'s verdict stands at UNDERPOWERED
and does not become a result retroactively.

New required step, now standing: **enumerate the eligible population and verify measurability
BEFORE sampling, without inspecting the discriminator or the outcome.** Done below.

## Feasibility (established before any measurement)

Repo-wide over role directories, counting only files that exist and are non-empty, and readers
that actually parse JSONL and filter on at least one record field:

    non-empty .jsonl under role dirs        615   (482 distinct basenames)
    python files that parse JSONL           289
    unresolved .jsonl path literals         107   (reported, not silently dropped)
    SURVIVING (reader, ledger) pairs        150
      distinct ledgers                       66
      distinct readers                       90

**n = 150.** No drop rate, field presence, or acceptance count was computed to obtain this.

## The abstraction moves up a level

Cycle 043 treated *literal field presence* as the discriminator. That is too narrow. The real
candidate is:

> **Does the producer's schema satisfy the consumer's predicate contract?**

For `load_prepass`, "`rep` is present" is merely one concrete obligation. A contract can be
violated by **missing field, wrong type, wrong nesting, null where a value is required, an
out-of-range enum value, or a different semantic encoding** — `key: [rep, uid]` is a nesting
violation, not merely an absence. The class under test is therefore
**producer/consumer contract violation**, and missing-field is one mode of it.

## Status of the signature: CANDIDATE, not validated

Standing evidence for "loader-required fields absent":

- one motivating positive (`p1_prepass.jsonl`), i.e. **n_positive = 1**
- two healthy negative controls with fields present
- one independent measurable test negative (`load_forge_scraps`)

That supports **"drop rate alone is insufficient"** considerably more strongly than it supports
**"missing fields define the class"**. It is recorded as a **candidate signature**, and this
experiment does not try to accumulate more sightings of it.

## What is actually being tested: the two adversaries

Let **S** = "consumer's required fields absent from producer records", **D** = "consumer silently
returns a wrong or empty result". Searching for more `S ∧ D` cases cannot validate S. The
informative searches are the counterexamples:

**Adversary A — `S ∧ ¬D`: required fields absent, yet the loader returns correct records.**
Kills S as a *sufficient* condition (a false positive for the screen).

**Adversary B — `¬S ∧ D`: all required fields present, yet the loader silently drops or mangles
records anyway** — via type, nesting, nullability, enum, or encoding. Kills S as a *necessary*
condition (a false negative), and would force the abstraction up to the contract level.

*(Naming them by their content rather than by label: A is the sufficiency-killer, B the
necessity-killer.)*

## Predictions, committed

1. **Adversary B will be found.** Confidence: **moderate.** `key: [rep, uid]` is already a nesting
   violation rather than a pure absence, which suggests encoding-level violations are the general
   case and missing-field is the easy special case.
2. **Adversary A will be found.** Confidence: **low-to-moderate.** Optional fields accessed with
   `.get()` and never required are common, and my field extractor cannot distinguish "required"
   from "read if present" — so A may be produced by my own extractor's coarseness rather than by
   the code. That confound is declared here in advance.
3. **Independent positives (S ∧ D, not `p1_prepass`) will be rare** — at most a handful of 150.

## Decision rule and the PREDECLARED DECISION CONSEQUENCE

The new gate: a read-only audit earns its cycle only if its outcome can change something. Every
branch here changes something.

- **Adversary A found** → the candidate signature is **not sufficient**. Stop using field presence
  as a screen; report it as a failed screen rather than quietly keeping it.
- **Adversary B found** → **not necessary**. The abstraction moves to contract satisfaction, and
  any B instance is a **new live defect** to be escalated with its own blast-radius question.
- **≥ 1 independent positive** → the class survives; each becomes an escalation candidate.
- **Neither adversary, no independent positive** → the class hypothesis is **retired**, field
  presence is recorded as unvalidated-and-abandoned, and the 80% real-substrate budget moves off
  schema drift entirely. This is a real outcome and I will report it as one.

## Constraints

Read-only; nothing outside `techne/` and `prometheus_math/` is modified. Ergon is not patched. The
sweep executes existing readers on existing files and compares field sets and types. `UNRESOLVED`
and `UNEXECUTABLE` pairs are reported, never folded into a denominator.

## What would make me wrong

If every one of the 150 pairs is clean and no adversary exists, the honest conclusion is that #78
is an isolated incident and I have spent four cycles on a class that does not exist. That outcome
is specified here so it cannot be reframed later as "inconclusive".
