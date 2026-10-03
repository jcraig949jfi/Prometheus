# Phase 3 hardened design v0.3

Status: implementation-charter proposal plus a separately bounded reference
implementation. Scientific status NOT_VERIFIED. Strong recursion remains
DETECTION_UNQUALIFIED. This supersedes design recommendations in the earlier
ASTRA review only where explicitly stated; it does not modify incoming sources.
Source index and comparative rationale: [README](README.md),
[decision report](reports/Comparison_and_decisions.md).

## 1. Objective and non-goals

Build the smallest instrument that can admit a real bounded capability and
refuse a specified false interpretation of it. An honest negative or stop is
a successful program outcome. Agreement among reviewers is not qualification.

The architecture is a thin federation of native runtimes, not a universal
organism VM. Shared contracts govern observations, costs, custody, evidence
and comparisons. They must not require detachable modules, global clocks,
explicit pointers, V/U/S anatomy, or a fast/persistent state partition.

Non-goals in this slice: open-ended foundry search, W2 adversarial universe,
large ecology, a seat per architecture, universal neutrality, endogenous
cognition, a new origin theorem, and a promised strong-recursion positive.

## 2. Keep four distinct objects

1. **Claim:** proposition, estimand, population, boundary, allowed channels,
   alternatives excluded, resource horizon, and exact registered cell revision.
2. **Capability declaration:** native observations and interventions available,
   including unsupported operations. Availability is not qualification.
3. **Qualification receipt:** evidence that a specified measurement or operation
   meets its contract on a stated domain. A ruler's self-declared PASS is not one.
4. **Eligibility decision:** a reproducible derived view of applicable receipts
   under a pinned policy; invalidated dependencies trigger a new decision.

Cell C = (physics, search, world, development, boundary, resources, measurement,
exposure). Each component has a version/content identity, not just a name.
World ORDER describes task/family/meta-family organization; useful RETENTION
is a measured proposition across a boundary. ORIGIN is a separate unresolved
inference. Increasing world order or layer count does not measure causal depth.

## 3. Claim-specific requirement matrix

All scientific rows require valid measurement, identity, custody/exposure,
complete attempt accounting, resource scope, and a declared uncertainty or exact
enumeration method. Additional requirements below are claim-specific. Missing
evidence blocks eligibility; an unsupported operation caps only affected claims.

| ID / claim | Additional necessary evidence | Not implied |
| --- | --- | --- |
| O / observed performance | Defined output/score and sampling domain | Retention, origin, demand, search success |
| T / useful retention | Known positive and impostor; boundary/channel contract; valid no-carry reference; observer/reset qualification where used; causal controls if usefulness is attributed causally | Learning-to-learn or bits without a separate applicable information bound |
| B / named-comparator advantage | Frozen comparator implementations, competitive tuning, matched competence or registered utility, lifecycle horizon and inference rule | Exclusion of every possible cheap policy |
| X / restricted-class exclusion | Precisely bounded class/interface, proof or exact enumeration, applicability check including all side information | Larger-class exclusion, structural origin or recursion |
| R / repair or cold reach | Start-law and ancestry custody, operator/budget, functional verifier, independent unit, censoring and tuning; distinct regime declarations | Repair implies discovery; zero verified hits implies impossibility |
| N / bounded search negative | R requirements plus detector operating range; capacity witness if making a reach-not-capacity interpretation | Latent-hit bounds without a sensitivity model |
| C / mediated updater change | Qualified native V/U mapping; freeze/disconnect/manipulation fidelity; matched shams, damage and resources; fresh task custody; fixed-U and swap contrasts | Exclusive changed-builder origin or strong recursion |
| S / shared comparison | Relevant native qualification for each realization/encoding AND scoped neutrality panel with biased-ruler positive control | Neutrality outside the panel or for a different estimand |
| I / independent reproduction | Separately justified implementation/world/checker lineage, custody and frozen target claim | Different seeds constitute independent methods |
| P / prediction | Frozen prediction, new admissible data and uncertainty scoring | Post-hoc fit, causal identification or universal law |
| Q / strong recursive improvement | Coherent proposition/excluded class plus independent genuine-positive and discriminatory-negative qualification; currently unavailable | Any promotion from other rows |

Display L0-L4 may summarize these rows only with a published proposition-specific
policy. There is no automatic L-number ladder in the reference checker. Reject
the incoming blanket L1 ceiling for all unbounded structure claims: exact
bounds authorize X, not every kind of robust evidence. A local replicated
mechanism or named comparison must not be relabeled whole-class exclusion.
Capacity, demand, reach, detection, developability and neutrality are explicitly
referenced qualification records, never lost when deriving display labels.

## 4. Execution, gate and outcome semantics

- Execution: NOT_RUN, COMPLETED, ERROR. Record errors and attempted-run inventory.
- Observation: positive, negative, inconclusive, or exact finite result.
- Gate: PASS, FAIL, BLOCKED, UNQUALIFIED, with predicate and reason.
- Missing artifact/facet: BLOCKED. Present wrong hash/scope or contradicted
  contract: FAIL for that contract. Missing calibration/positive or invalid
  intervention: UNQUALIFIED for the inference. An executed sham mismatch can
  separately FAIL calibration. None of these proves absence of a mechanism.
- A registered null can PASS the protocol while supporting a scoped negative.
- Fail-closed refusal is an action, not a fifth scientific verdict. Preserve
  all individual records even if a consumer needs a combined status.

Eligibility = all applicable pinned prerequisites satisfied. Requirements come
from the policy, not a producer-supplied empty list. Unknown claim types block.
Corrections preserve old records and append supersession/invalidation reasons.
Recompute only affected descendants, preserving unrelated eligible claims.
Untrusted praise or accusations cannot directly promote or revoke evidence.

## 5. Receipt and trust contract

Each production receipt must bind schema/policy/registration identities; all
eight cell components; runtime, world, ruler, readout, observer, reset and oracle
artifacts; dependencies; exact inputs/outputs; native configuration; run status;
actual unit-typed resources; omissions/failures; custody/exposure; experimental
unit; expected-answer source; verdict rule; limitations and applicability range.

Use immutable artifact refs (role, content digest, byte length). Canonical
serialization and a content hash identify bytes, not truthful execution,
independent authorship, hidden-state completeness or absence of label leakage.
The independently retained registration commitment must precede outcome access.
An independently sealed terminal run inventory is required to detect omitted
tail trials; an internally rewritten hash chain alone cannot do that.

The consumer verifies anchors obtained outside the producer, hashes exact bytes
once, recomputes supported predicates, rejects scope/version mismatches and
dependency cycles, and refuses missing evidence. Do not execute artifact code
or fetch arbitrary paths/URLs while checking receipts. A future untrusted loader
must be bounded and reject duplicate keys, non-finite values, traversal and
reparse/symlink escapes. Authentication and safe loading are NOT implemented
by the new in-memory finite checker. Its anchors are synthetic in tests.

## 6. Native runtime contract and reset closure

Declare native transition/scheduling/precision semantics, observation/action
access, inheritance, perturbations, capture/restart equivalence, resource units,
native search, optional intervention/tracing capabilities, AND reset kinds.

For each task/family/lifetime/confirmation reset:

1. Inventory all modeled future-influencing channels: organism, adapter/readout,
   packet/queue, scheduler/clock, RNG, solver/optimizer, worksite, host caches,
   participating agents, measurement feedback and search scaffolds. Mark each
   retained, erased, resampled or inaccessible, with ownership and rationale.
2. Define authorized retained R and future exogenous E. For histories sharing R,
   scientifically relevant post-reset outcomes under E must not depend on the
   forbidden past. Use exact equality only where native semantics justify it;
   otherwise register equivalence estimands, margins, noise and power.
3. Inject a reachable sentinel into each forbidden channel and interacting
   pairs. Two individually uninformative shares can jointly leak a target.
4. Preserve allowed R in a clean twin. An indiscriminate wipe cannot qualify by
   destroying both leakage and the capability under study.
5. Separate continuation from reset: faithfully restoring a forbidden packet
   is excellent replay AND an invalid content reset. Matching public buffers
   does not establish equality of future behavior.

Closure is relative to a modeled interface, not proof of no physical side
channels. Unknown channels cap the claim. A packet in the niche may support
external/joint retention instead of organism-only retention; it is not cheating
when declared, priced and controlled.

## 7. Observer and comparison qualification

Compare observer off/minimal/full/overloaded under registered scientifically
relevant state/action traces or distributions, not final score alone. Exercise
RNG consumption, queue order, timing, integrator precision and backpressure.
Bookkeeping differences can be irrelevant; event-emission effects may not be.
Native asynchronous happens-before closure is valid without a universal clock.
A deterministic scheduler qualifies only that scheduling cell.

Two-door admission remains: designed known positive plus impostor, or a
mechanism-blind found positive with an independent world-side certifier. A
candidate ruler cannot write its own truth table. Mechanism blindness is not
blindness to world grammar, tuning feedback or confirmation outcomes.

The first native retention panel should contain genuinely unlike stored,
recurrent, in-flight and spatial realizations with restricted readouts. Require
at least three for the incoming observatory acceptance target, but recognize
that a count is coverage, not proof of universality. Two encodings of one Python
tuple are NOT two physics. A global readout solving a local task must be counted
as part of the system and priced, not called a neutral adapter.

Each shared-ruler receipt names proposition, realizations, encodings, noise,
resources, positive/impostor truth and biased-ruler control. Retention isomers
do not qualify origin, economics or interventions. Permit useful local rulers;
changing their label to SHARED cannot manufacture qualification.

## 8. Nested claims and the R8 admission contract

V -> U -> S is an optional experimental mapping. Freeze U's update law while
allowing declared runtime state to evolve; disconnect subsequent V influences
without damaging S or removing legitimate task observations. Cross histories,
swap U, clamp U across histories, and test response changes on identical S and
evidence streams. Match physical damage/access/resources, not just object count.
Include actuator-damage lesions, irrelevant-history donors, independent donors,
rescue and off-target controls with actually attainable contrary outcomes.

Register relationships among A curriculum and B/C/D/E: instance seeds, primitive
overlap, composition grammar, latent laws, generator family and exposure. Cross
curriculum shape with part sharing in discovery, then freeze one feasible
confirmation demand. State whether D/E reset to post-A or continue through B;
only the latter could support a successive-improvement claim under further tests.

R8 specimens each get a vector, not a global counterfeit label: retention,
reuse, updater behavior, direct-answer exclusion, economics, origin and strong
recursion. Fixed libraries may be legitimate reuse/updater positives. Cargo is
an attack on an interpretation; R0 is a competitor; flattening is a test of
representation dependence. They are different roles.

If nested and flattened programs preserve all tested interventions, access and
declared resources, this assay cannot both treat them as equivalent and declare
one a strong positive and the other a counterfeit. If compilation changes cost
or available intervention, measure that change. Bound any excluded selector
class by information and resources; a selector class containing every permitted
finite program cannot leave a distinct finite positive outside it.

**Current Q status: DETECTION_UNQUALIFIED.** Our new rational updater is an
attainable C-style toy control, not a genuine positive for Q. beta and x in
{1,2}, eta=1/(beta*x), gradient g=-beta*x*y, fresh y in {-1,+1}, initial S=0
give S'=-eta*g=y. A fixed sign-gradient policy also recovers y. Thus the direct
pre-C answer is unavailable, but an acquired family prior is allowed and a
fixed decoder solves the task. Eight exact successes give no R0 advantage.

## 9. Search, W1 and economics

Report capacity witness, developmental trajectory, repair and cold discovery
as separate events. Bind founder construction, scaffold history, witness
selection, search operator/acceptance, costs, verifier and censoring. Use
functional equivalence, not original target bytes. Greedy failure on a finite
plateau demonstrates a search-policy limitation, not substrate incapacity.

Search nulls bound verified-hit rates under declared sampling. Latent-hit
bounds require a justified detector model; curated fixture sensitivity is not
sensitivity over all undiscovered phenotypes. Do not analyze adaptive founder
selection as IID by assigning different seeds.

W1 asks where development pays, including nowhere. Start with a renewal
hidden-law family varying law turnover and reuse horizon. Give R0 an owner
charged with winning using fixed, sufficient-statistic, lookup, library,
adaptive/meta and ideal-observer methods where applicable. Freeze competitors
after fair tuning and before fresh confirmation.

Report deployment and full-lifecycle vectors: native operations, host compute,
memory/communication, inherited description/decoder, construction, development,
world generation, tuning, failed attempts, measurement and maintenance. Do not
sum unrelated units without registered exchange weights. Equal bytes are not
equal useful priors. Match competence or register utility. A lifecycle crossover
requires an explicit horizon and uncertainty; none is measured by this review.

## 10. Portfolio and implementation boundary

| Family | v0.3 disposition / activation question |
| --- | --- |
| R0 | Serious reference first; winning changes allocation. Toy R0 here is not the full suite. |
| R1/R2 | One provisional thin kernel with reference/growth/rule-write toggles; split if transition semantics, access or costs cannot be preserved. No equivalence assumed. |
| R3 | Separate plasticity/reach hypothesis, not automatically NEXT. Activate for a matched search-geometry contrast. A latch alone is retention, not plastic learning. |
| R4/R5 | Small native locality/distributed-state standards before interface freeze. Defer chemistry/packet ecology. |
| R6/R10 | Catalogue entangled/material alternatives; two-door admission, not rejection for lacking modules. |
| R7 | No standalone build now; reopen for a distinct falsifiable tensor/factor question. |
| R8 | Admission AND overclaim kit; import Fable corrections with immutable receipts. |
| R9 | Encoding switches only while constructor information, native semantics and resource contrast remain honest. |
| Foundry/W2 | Grammar/custody on paper. Bounded blind search only for a registered question after qualification and budget. |

The reference harness implements only finite analogues and toy evidence
policies. It has no production levels, unlike native engines, custodian,
stochastic observer test, scientific cargo detector or lifecycle accounting.
The [test plan](HARDENED_TEST_PLAN_v0.3.md) states actual coverage and deferred
acceptance requirements. Do not mark the cross-physics observatory accepted.