# Outcome-variable hygiene for selection signals -- DRAFT RESIDUE, not doctrine

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11. Status: **DRAFT RESIDUE**. This is not constitutional,
not adopted, and not enforced anywhere. It is extracted from one corpse by
the corpse, under the operator's PARK ruling, which asked for the reusable
invariant and explicitly forbade constitutionalizing it unilaterally or
designing a new Coeus around it.

Whoever adopts this owns it. Coeus does not, and is parked.

## The invariant, in one sentence

A number that steers selection -- a priority, a weight, a sampling
probability, a fitness term, an admission threshold -- must carry, at the
point of use, enough of its own provenance that a consumer can refuse it.

## Why, from the one case that produced it

Coeus published `survival_rate: 1.0` for Epigenetics. The denominator was
one. `nous._load_coeus_weights` read the rate, did not see a denominator
because the emitter had stripped it, and raised Epigenetics to 2.5x in the
distribution Nous drew concept triples from. Eleven of the sixteen
concepts at 2.5x got there the same way, four of them on a single
observation (FINDINGS_2026-09-11.md, F6).

Nothing in that chain was malicious, hidden, or even unusual. Each step
was locally reasonable. The defect is that the representation of the
number did not carry what a downstream consumer needed in order to
distrust it, and there was no place in the pipeline where distrust could
be expressed.

The second half came from the same corpse: Coeus regressed an outcome
variable in which 2,176 of the attempts record `api_call_failed` as
`scrap`, alongside genuine trap-battery failures, and never held out along
the time axis on which the judge changed. What it learned was the forge
calendar (Necropolis, MEASUREMENT_FAILURE).

## The five properties a selectable signal should expose

Each is stated so that a consumer can CHECK it, and so that failing it is
observable rather than a matter of taste. None is novel on its own; the
claim is only that a selection signal that exposes none of them is not
auditable at the point of use.

1. **LABEL PROVENANCE AND EXCLUSIONS.** What outcome was regressed or
   counted, and which rows were dropped and why. A label that mixes
   instrument failure with subject failure is a different variable from
   the one the name suggests. Checkable: the signal names its outcome
   field and carries the exclusion predicate that produced it, with the
   count excluded.

2. **DENOMINATOR AND EFFECTIVE SAMPLE SIZE.** Every rate ships with its
   numerator and denominator, and the denominator is the count of
   INDEPENDENT observations, not of joins. Coeus's `n_tasks` summed to
   37,035 over 92 actual tasks. Checkable: n is present, its unit is
   named, and the sum of per-group n is reconcilable with the total.

3. **TEMPORAL OR INSTRUMENT REGIME.** The signal records which
   configuration of the measuring apparatus produced it -- judge version,
   battery version, model, API health window -- and any validation held
   out along the axis on which that configuration changed. Holding out by
   producer (Nous run) while the instrument changed by consumer date
   (forge day) is what let the calendar pass for structure. Checkable: the
   regime field exists and the holdout axis is named.

4. **UNCERTAINTY SUFFICIENT TO STOP A TINY-N EXTREMUM BECOMING A
   CONFIDENT WEIGHT.** An interval, a posterior, a shrunk estimate, or at
   minimum a declared minimum-n below which the value is INDETERMINATE
   rather than extreme. 1-of-1 must not be representable as 1.0 with the
   same type as 486-of-1397. Checkable: the extreme values in the file are
   reachable only at n above the declared floor, or are typed
   INDETERMINATE.

5. **INDEPENDENCE BETWEEN MODEL SELECTION AND THE CHANGING AXIS.**
   Whatever chose the model, the features, or the threshold did not get to
   see the axis along which the measurement process moved. Checkable: the
   selection procedure and the regime field are declared together, and the
   procedure's folds do not straddle a regime boundary.

A sixth is implied by all five and is the cheapest of them: **the consumer
records which version of the signal it used.** Coeus's whole downstream
story is unrecoverable because `ledger.jsonl` has no priority field and
Nous's runs record no weight vector. Two integers per row would have made
the counterfactual measurable. They were not there, so the question is
permanently closed.

## What this is NOT

- It is not a schema to impose. The five properties are what a consumer
  needs; how they are carried is the consumer's business.
- It is not a new seat's mandate. See the ownership section.
- It is not validated. It is one case generalized, which is the weakest
  possible evidential base -- exactly the base-rate error this program
  names (N striking instances is not a pattern). Before it binds anything,
  someone who is not Coeus should check whether selection signals
  elsewhere in Prometheus actually fail these properties, or whether
  Coeus was an outlier. That check has not been run.

## Where it would bite first, and who should own enforcement

The ruling asked for a named owner and a concrete first consumer, and for
NONE if there is none. This seat examined the live selection paths it
could see from the committed tree and reports:

**Owner, recommended: the seat that owns the contract mechanism, not a
new one.** Prometheus already has the enforcement shape this needs:
`roles/Harmonia/contracts/conformance_check.py` and D-22, which make a
consumer declare its route set and record contract hash, engine instance
and gate state on every row before it may work. A selection-signal
declaration is the same move one layer in: the consumer declares the
signals it reads and refuses the ones that do not carry their provenance.
That is an addition to an existing gate, not a new instrument, and the
base role's rule 1 (inheritance over duplication) favours it.

**First consumer where it would bite: NAMED, with a caveat.** The three
Coeus consumers are all dead or unimported (Nous cold since 2026-03-27,
hephaestus's forge dead since 2026-05-28, rlvf_fitness never imported).
Among live paths, the one with the right shape is the SFE engine's
selection surface owned by Daedalus, with Vivarium as the consumer that
already halts on a bad gate state -- but this seat has NOT read that code
and will not assert that its fitness terms lack these properties. Naming a
victim without reading its code is precisely the error this document is
about.

So the honest answer, stated as the ruling permits:

    FIRST CONSUMER: NONE VERIFIED. A candidate is named (the SFE
    selection surface, Daedalus, with Vivarium downstream) but was not
    examined. Until someone reads it and finds a signal that fails one of
    the five properties, this stays residue and binds nothing.

If that check is run and finds nothing failing, the correct outcome is to
leave this file as a dead artifact in a parked seat's directory. That is a
legitimate result and is preferred to adopting a rule nobody needed.

## The falsifier for this document

If a survey of live selection signals in Prometheus finds that they
already expose the five properties, or that consumers that ignore them
suffer no measurable harm, then this invariant is a lesson about one dead
pipeline and not about the program. Coeus asserts the first half (the
lesson is real for Coeus, measured) and explicitly does not assert the
second (that it generalizes). The generalization is the untested claim.
