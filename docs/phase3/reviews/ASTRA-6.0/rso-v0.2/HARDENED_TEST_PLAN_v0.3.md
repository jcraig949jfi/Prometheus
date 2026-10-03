# Phase 3 hardened test plan v0.3

Companion to [the design](HARDENED_DESIGN_v0.3.md). The supplied ChatGPT harness
is missing; its charter execution is BLOCKED, not a scientific FAIL. The new
[reference harness](reference_harness/README.md) is a different, bounded
implementation. Passing it does not satisfy all H0-H9 or observatory acceptance.

## 1. Three validation lanes

| Lane | Entry / output | Scientific ceiling |
| --- | --- | --- |
| A: offline contract CI | Exact fixtures, small immutable graphs, source mutants; nonzero inventory, exit 0, named expected outputs | Tested software contracts and finite mathematics only |
| B: native calibration | Actual runtime traces, world-side oracle, positive/impostor, reset/observer/intervention checks, scoped isomer panel | Particular measurement/operation qualified on its operating range |
| C: registered science | Applicable lane B receipts; frozen estimand, baselines, sample unit, power, custody, stopping and costs; fresh confirmation | Only registered claim/scope, possibly negative or inconclusive |

Never turn lane A metadata into lane B evidence, or a lane B fixture selected
for legibility into lane C discovery sensitivity. Keep contract PASS,
calibration QUALIFIED and scientific ELIGIBLE separate in every dashboard.

## 2. Exact finite anchors and expected answers

These are development-time finite fixtures, not sampled scientific trials.
Expected constants are handwritten separately from executable constructors;
some use a second enumerator, but no independent authorship is claimed.

| ID | Domain and expected answer | Current implementation |
| --- | --- | --- |
| K1 | Uniform bit exposed once. Carry 2/2 correct; either fixed no-carry output 1/2; flip 0/2; independent donor 1/2. | bit_answers, detector_counts and test_retention_no_carry_and_donor |
| K2 | Uniform M keys, at most L distinguishable carried states, no side information. Bound min(1,L/M). M=4, L=1/2/4 gives 1/4, 1/2, 1. Enumerate all 16 encoders x 16 decoders at L=2. | channel_bound, channel_optimum; 256-pair cross-check |
| R1 | Chain 0->1->2, budget 2 proposals, founder score given, fitness (0,1,2). Strict and nondecreasing reach 2 on proposal 2. | search |
| R2 | Same chain with (0,0,1). Strict remains 0 after proposals (1,1); nondecreasing hits on proposal 2. | search |
| R3 | Same chain with (0,-1,1). Greedy cold policies fail; unconditional chain walk hits on proposal 2; repair founder 1 hits on proposal 1. | search, search_record; repair-as-cold refusal |
| S1 | T(q,c)=(1-q,c XOR q), output new c. From (0,0),(1,0),(0,1),(1,1), two-step traces (0,1),(1,1),(1,0),(0,0). Omitting q breaks precisely the q=1 cases. | continuation |
| S2 | Allowed bit plus forbidden displayed/pending bit. Clean reset preserves allowed, erases displayed and packet; next tick cannot recover forbidden bit. Display-only reset leaks on delivery. | BoundaryState; clean/leaky/overerase controls |
| N1 | Plain and one-hot encoding, mapped readouts both recover (0,1). First-coordinate ruler recovers (0,1) vs (1,0). | encode_bit, read_bit, biased_ruler; NOT unlike physics |
| U1 | beta,x in {1,2}; learn beta from lawful calibration; freeze eta=1/(beta*x); branch fresh y +/-1; g=-beta*x*y; S'=-eta*g. Correct U, flattened and sign-gradient R0 each 8/8; no-gradient output 0. | History, Updater, updater_rows; fixed-U/swap/bypass tests |
| E1 | Complete pinned toy graph passes; each required missing facet blocks; bad scope/hash fails; unavailable detector and strong claim unqualified. Invalidate source: all descendants, not unrelated claim. | checker and test_contracts |

K2 proof: for each of L messages the decoder can allocate at most one unit
of success mass across M equally likely keys; summing gives L/M, capped at 1.
Independent randomization cannot improve the optimum over deterministic maps.
This is a channel distinguishability bound, not a general acquired-bit assay.
A post-boundary cue correlated with the key invalidates the no-carry premise.

The new code has bounded in-memory inputs, <=64 nodes, <=4096 artifact bytes
and parsed JSON depth <=8. It is not a hostile-filesystem loader or truth oracle
for native physics. External anchors are trusted caller inputs; fabricated
data plus fabricated anchors are not authenticated by these tests.

## 3. Actual mutation tests, not a list of suspicious organisms

Run `python -B -m unittest discover -v` from reference_harness. The initial
inventory is 26 top-level methods; final inventory/results are in
[VALIDATION](VALIDATION.md). Each source mutation must have a passing unchanged
probe, compile successfully, execute the intended assertion, and yield exactly
one assertion failure with zero errors/skips. No workspace source is overwritten.

| Fault injected in memory | Probe that must kill it |
| --- | --- |
| Disable missing-facet check | Removing each required facet must return BLOCKED with its name |
| Skip external evidence-node binding | Whole graph relabeled under old anchors must fail EVIDENCE_BINDING |
| Bypass repair/cold ancestry comparison | Valid repair trace cannot qualify cold claim |
| Skip artifact SHA-256 comparison | Same-length altered artifact bytes fail ARTIFACT_DIGEST |
| Invalidate only direct children | Grandchild invalidation closure must be recorded; unrelated claim unchanged |

Report source mutants proposed/implemented/executed/killed/survived/equivalent/
blocked separately from adversarial data cases. Five kills only establish
sensitivity to these five selected faults. They do not measure a general
mutation score, a scientific false-positive rate, or counterfeit coverage.

## 4. Charter attacks and honest remaining coverage

| Required attack | New finite test / result meaning | Still required for native scientific acceptance |
| --- | --- | --- |
| >=5 deliberate mutants | Five source faults above, plus semantic data defects | Independent withheld mutations/constructors; no goldens auto-updated to pass |
| Physics-specific masquerades as shared | Re-encoding bias detected; unknown shared claim has no policy and cannot promote | >=3 genuinely unlike native positive/impostor realizations; qualified truth/readout and biased shared ruler |
| Incomplete reset | Reachable pending-bit delivery breaks forbidden-history erasure; clean allowed-state twin admitted | Channel inventory, interacting leaks, native precision/schedule and stochastic equivalence |
| Repair called cold | Declared anchored lineage inconsistent with regime refused | Independently retained founder custody and scaffold inventory; fabricated anchors remain outside toy threat model |
| Missing facet promotion | Delete every required toy facet; no caller-supplied PASS/requirements | Full pinned scientific matrix and dependency propagation for real receipts |
| Nested compiler / R8 | Strong claim always UNQUALIFIED; legitimate updater and flattened form both admitted for toy capability | An actual discriminatory cargo control, fresh task/family custody, matched priors, costs, shams and direct-answer leakage attacks |
| Strong positive attempt | U1 gives useful history-conditioned update pathway, but R0 and flattened forms match 8/8; not Q positive | Coherent stronger proposition/excluded class and independent positive truth; unavailable now |
| R1/R2 bias | Re-encoding counterexample exposes coordinate privilege; no native physics conclusion | Native R3/R4/R5 readouts, reset/observer contracts and entangled-boundary cases |
| Four statuses | Exact status/reason assertions exercise PASS/FAIL/BLOCKED/UNQUALIFIED | Production runner error/negative separation and complete multi-gate records |

No "harness escape" is claimed against absent source code. In the new checker,
parent review DID find two software escapes: whole-graph scope relabeling and
dependency stripping passed with artifact-only anchors. Both were reproduced
as failing regression tests, then repaired by anchoring complete evidence nodes.
Final counts and the red/green receipt are in VALIDATION.md. The scope-only
source mutant was replaced with an external-binding mutant to exercise a real
false admission rather than merely a changed diagnostic reason.

In the new checker,
true execution, independent custody, secret holdout access, complete inventory,
physical neutrality and full cost remain trust/integration gaps, not solved by
hash fields. Tests deliberately enforce a strong-recursion refusal, not a
scientific counterfeit detector.

## 5. Next native tests: conditions for passing AND failing

Build each negative with a clean twin. Register expected outputs and a positive
branch before measuring. A clause that never changes its answer is not tested.

1. **RESET:** inject forbidden packet, adapter, clock, RNG, solver and niche
   channels where native; include two-share leaks. Erase forbidden history while
   retaining authorized state. Capture-complete and reset-complete are separate.
2. **OBSERVER:** perturb RNG draw, event order and logging load; include cases
   with unchanged score but changed registered behavior. Permit irrelevant
   bookkeeping differences. Stochastic equivalence requires a justified margin,
   power and sampling rule; nonsignificance is not a pass.
3. **NEUTRALITY:** mapped outputs plus restricted access across native isomers;
   deliberately physics-specific ruler must fail the shared claim. Physically
   different positives without named buffers must be admitted where valid.
4. **CAUSALITY:** target perturbation, physically matched sham, wrong/random
   donor, rescue, off-target/resource measurements. An actuator-damage lesion
   with successful rescue must NOT qualify information-specific mediation.
5. **R8:** dedicated U_TRANSFER, rescue, wrong-history and reset-only fire tests;
   cover all clauses with attainable failures. Test a reset-only false promotion
   that other clauses do not already reject. A sham that speeds search is a
   measured confound, not an automatic pass because its entry count matches.
6. **DEMAND/ECONOMICS:** omitted constant/lookup/clock and oracle baselines,
   leaked label, missing tuning/library/failed-run cost, censored failures.
   Baseline owner competes to win. U1's sign-gradient equality is a warning
   example, not a full demand/economics implementation.
7. **CUSTODY:** holdout champion selection, generator-family reuse, same-code
   new-seed "replication", altered raw bytes, rewritten internal hashes,
   omitted final attempts, stale scopes, evidence cycles and fabricated praise.
   Pre-registration commitment and terminal inventory must be externally held.
8. **NULLS:** independent-founder hitting-time analysis with censoring; refuse
   unqualified IID/latent-absence inference. Example arithmetic only: four
   fixed IID zero-hit trials give upper p=1/2 at confidence 15/16 since
   (1-p)^4=1/16. This is not a default sample size or implemented statistical test.

## 6. Freeze before confirmation

The registration must contain proposition/policy, independent truth source,
positive/impostor and held-out attack domains, A/B/C/D/E relation table, genotype
and start law, search and tuning history, native access/precision/schedule,
boundary/reset, acceptance/censoring, cost vector and horizon, estimand and
effect/equivalence margins, experimental unit, power or exact domain, stopping,
multiple-comparison handling, allocation, exclusions, custody and decision table.

Preflight attainability: exact finite enumeration where possible; otherwise
justify reachable positive/negative outcomes and power over the claimed range.
Choose independent founders/world families as units where appropriate, not
individual correlated tasks. Pilot thresholds are exploratory. Any changed
baseline, generator, margin or reset after exposure creates a new protocol and
requires fresh confirmation; no repeated unplanned attempts until success.

## 7. Dependency gates replace an unfunded calendar

The incoming 90-day sequence is a planning window, not evidence that these
deliverables fit. Do not average authors' percentage allocations or pretend
different work buckets share a denominator. No paid campaign is authorized here.

| Gate | Work package / owner role | Exit and stop |
| --- | --- | --- |
| G0 | Artifact/trust inventory; implementer plus independent oracle reviewer | Original missing harness explicitly blocked. New reference bounded and named. Missing owners/budget blocks expansion. |
| G1 | Narrow contract CI, exact answers and semantic mutants; checker owner | Nonzero suite passes, known clean positive admitted, each specified defect fires. Fix semantic bugs before claiming software conformance. Current work reaches only this bounded lane. |
| G2 | One native retention witness plus clean reset/leak pair; native owner and separate world oracle | Correct positive, erasure and preservation; observer contract. Stop/demote this native inference on unresolved leakage or false rejection. |
| G3 | Small unlike panel and biased-ruler attack; native owners and second checker | Scoped neutrality with relevant native contracts. One preregistered repair round; unresolved failure suspends shared comparisons, not local observations. |
| G4 | One reach OR W1 contrast, not all axes; experiment and adversarial R0 owners | Capacity/demand/detection conditions appropriate to the chosen claim; costs and exposure complete. No clear discrimination or inadequate power within cap: redesign or publish bounded negative. |
| G5 | Independent world/checker path, custody, fresh confirmation; separate reviewer/custodian | Frozen target, attempted-run seal, stopping and uncertainty. Missing independence or custody: no confirmatory promotion. |
| G6 | Closure and allocation decision; operator | Result/negative/inconclusive, receipts, corrections, unsupported claims and measured costs. Optional foundry/strong recursion remains deferred unless separately qualified. |

Before G2+ authorize absolute person-hours per owner, independent-review hours,
maximum runtime starts, CPU/GPU time, storage, money where applicable, wall-time
deadline and one explicit repair allowance. Record estimates separately from
actuals and charge failed attempts. No values are invented by this review.
If these cannot be funded, stop at the methods/reference result. Never recover
schedule by dropping R0, genuine positives, independent oracle or custody.

Binding stop rules: no native authority before G2; no shared comparisons before
G3; no confirmation before G5; never infer Q from other gates. At a budget cap
retain censored observations and stop, rather than secretly extend it. If R0
wins or no development crossover survives full costs, select the conventional
winner or publish "no advantage in tested domain". If the Q distinction remains
undefined, retain DETECTION_UNQUALIFIED rather than manufacture a positive.

## 8. Smallest next experiment and review questions

After separate authorization/budget: implement one actual native retained-bit
organism, one no-carry impostor, a clean reset, a display-only reset whose
forbidden packet later arrives, and a clean allowed-state twin. Independently
enumerate the world-side truth before attaching the candidate ruler. The single
question is whether retention is admitted while invalid reset/attribution is
refused. An unlike native specimen comes next only to attack a named assumption.

For external review: identify a false admission or false rejection, not just
another principle. In particular, challenge the independent oracle, reset
closure, family-demand feasibility, resource matching and Q exclusion class.
"Stop here; this distinction is not worth its qualification cost" is valid.