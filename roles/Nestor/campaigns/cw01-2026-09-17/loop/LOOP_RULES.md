# CW01 priority loop — constitutional rules (operator directive of 2026-09-18, made durable)

CW01 is no longer a one-way sequence of experiments. It is a persistent
revisit / perturb / stasis / reactivate loop over its entire history.

## Constitution

**Nothing scientific is ever killed.** Experiments terminate, implementations are
rejected, assays return NULL, worlds become unreachable under a substrate, trajectories
enter temporal stasis. Every hypothesis, result, anomaly, defect, fossil, failed
operationalisation, null and inconclusive trajectory remains an addressable candidate.
There is no scientific delete operation. A prior disposition describes only what happened
under that world, representation, search, pressure, ruler, budget and system state; it
never resolves the underlying hypothesis.

## Records (this directory)

- `TRAJECTORIES.jsonl` — one IMMUTABLE record per trajectory (append only; never rewrite
  an old conclusion; append evidence instead).
- `EVIDENCE.jsonl` — append-only evidence events keyed by `trajectory_id`
  (a run, a probe, a later discovery elsewhere that attacks an assumption).
- `STATE.jsonl` — append-only state events: `ACTIVE` / `TEMPORAL_STASIS` with the exact
  reason and the marginal-information history; the latest event is the current state.
- `PERTURBATIONS.jsonl` — candidate perturbations: parent, delta, what did NOT change,
  which failure surface or uncertainty it attacks, why informative NOW, cost, type.
- `PRIORITY_<date>.json` — a priority pass: scores, diversity constraints, protected
  (anti-gravity / serendipity) slots, the frozen top ten.
- `BOUNDARY_REPORT_<date>.md` — the compact report produced before execution.

## Temporal stasis

A trajectory enters TEMPORAL_STASIS when recent perturbations show diminishing returns:
given the presently available substrate, mechanisms, perturbations and compute, nearby
exploration yields little new information. It does NOT mean false, dead, uninteresting,
exhausted, disproven or superseded. The record states exactly why (repeated perturbations
converge on one mechanism; budget changes nothing material; nearby representations
reproduce the same boundary; every available intervention strikes the same surface;
search trapped under multiple operators; the next informative perturbation needs
machinery not yet available). "Seems exhausted" alone is never a reason.

## Every campaign begins with global re-evaluation

Re-evaluate ALL trajectories before allocating compute. Do not privilege recency,
COMPLETE over NULL, easily described concepts, or mature rulers. Ask what has changed
since each trajectory last ran (new operator, affordance, mutation topology, primitive,
fossil, representation, assay, intervention, budget, understanding of a defect, result
elsewhere, ability to transplant). A stasis trajectory reactivates whenever a meaningful
perturbation becomes available; reactivation is mechanical where dependencies are
explicit and never depends on an author remembering.

## Perturbations, not reruns

Every candidate carries a perturbation delta. No unchanged rerun unless replication is
the question. Prefer perturbations that attack a known failure surface; reserve capacity
for perturbations whose value is not yet legible.

## Priority is compute allocation, not verdict

The ordering answers only "which trajectories receive the next compute". A candidate
rises when: a later discovery attacks an old assumption; a failure surface is now
perturbable; unexplained structure exists; independent experiments intersect it; a
formerly inaccessible regime is reachable; information gain is large; the delta differs
from prior attempts; it discriminates mechanisms; cost fell; an old NULL becomes a
contrast against a changed representation; an inconclusive can now be posed; the branch
was underexplored because it was hard to operationalise. **Anti-gravity bonus** for
trajectories historically deprioritised for lacking a familiar ruler, not mapping onto
known constructs, hard-to-name phenotypes, unusual representations, or repeated
translation into conventional questions. No priority for being familiar, measurable or
publishable.

## Diversity in the top ten

Ten trajectories per campaign, representing distinct perturbational opportunities across
hypothesis family, representation, search regime, pressure, failure surface, mechanism,
age, prior disposition and perturbation type. Some from long-stasis or awkward branches.
A minority of slots are SERENDIPITY: older trajectories crossed with newly available
mechanisms, executable and recorded, not required to be justified by familiar theory.
Rank is temporary; exclusion from the ten is waiting, not rejection.

## Run all ten

Each: preregister the perturbation; state the parent trajectory, what changed, what did
not, what it attacks; preserve lineage identity, ancestry and fossils; execute
independently under its own lawful contract; append results. The ten need not share one
statistical ontology (confirmatory, exploratory, reconstruction, transplant,
search-boundary, break-a-null). Claim strength matches evidence.

## Diminishing returns

After each run, append to the trajectory's information history whether the map changed
materially (new regime, mechanism, falsification, defect removed, boundary, convergence,
NULL overturned under a changed assumption, representation or search dependence,
invariant, unexplained phenotype). Successive nearby non-material runs lower short-term
priority and place the trajectory in stasis. Never delete, never summarise away.

## Forbidden inferences

INCONCLUSIVE -> hypothesis weakened. NULL -> trajectory dead. Three failed
implementations -> concept exhausted. Cannot operationalise -> low priority forever.
No current ruler -> no experiment. Old -> obsolete. Familiar assay -> superior. Agent
cannot understand phenotype -> unimportant. Top-ten exclusion -> rejected.

## Evidence standards are unchanged

Within an experiment: preregistration binds causal claims; controls are real; lineage is
the unit where appropriate; leakage invalidates; broken rulers cannot certify themselves;
NULL stays NULL under its contract; INCONCLUSIVE stays INCONCLUSIVE. No result acquires
veto power over future perturbations.

## Campaign cycle

A RECONCILE (read the whole pool + new machinery) -> B REACTIVATE (generate candidates)
-> C PRIORITISE (opportunity, not truth) -> D DIVERSIFY -> E FREEZE TOP TEN (record the
ten and their deltas before execution) -> F EXECUTE -> G APPEND -> H STASIS UPDATE
-> I REPEAT over the entire pool. There is no terminal scientific state.
