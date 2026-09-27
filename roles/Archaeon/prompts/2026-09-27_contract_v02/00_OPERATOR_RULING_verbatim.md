ARCHAEON — CAUSAL LINEAGE CONTRACT v0.2

Record these operator rulings verbatim.

OPERATOR RULINGS

1. Proceed with Contract v0.2 now.
2. Do not preregister or launch the proposed cross-engine host-conditioned reproduction assay yet.
3. After v0.2 is complete, rerun the existing PORTABILITY-01 adapters and differential tables as the regression suite.
4. Only if the host-conditioned phenomenon remains coherent under v0.2 should you produce an assay-readiness recommendation and draft design. Do not launch it.
5. Do not reduce the causal lens to an ENVGATE-local tool. The current verdict remains:

PORTABLE_WITH_DOMAIN_LIMITS

until v0.2 evidence changes it.

6. Do not launch heavy compute on M2 while Bellerophon’s multi-day campaign is occupying the host. This round should be code, contracts, preserved-record analysis, and bounded replay only.
7. Leave the old Aphrodite Campaign 1 requests untouched during this work. They are stale queued requests, not implicit authorization.
8. Leave Azure and admission-gate TODOs explicitly BLOCKED_ON_OPERATOR_INPUT where operator information is genuinely required. Do not fabricate inputs.

⸻

OBJECTIVE

PORTABILITY-01 found five ontology gaps:

* B1 — Heritable-unit continuity is ill-posed under symmetric recombination and some rearranged copying.
* B2 — ENTITY conflates persistent body with engine identity.
* B3 — “Executed material” conflates write-governing code with where execution time occurred.
* B4 — Provenance conflates WHOSE material with WHERE material arose.
* B5 — Factual contribution and counterfactual sufficiency are different notions of authorship.

Contract v0.2 must repair these without turning the five observed anomalies into special cases.

The target is a better causal language, not a patch for BEE/NPE/PTE.

1. VERSIONING RULE

CAUSAL_LINEAGE_CONTRACT v0.1 is frozen historical evidence.

Do not edit it in place.

Create:

* CAUSAL_LINEAGE_CONTRACT_v0.2.md
* a v0.2 schema implementation;
* a changelog/migration document from v0.1;
* v0.2 conformance tests.

Any v0.1 artifact must remain interpretable.

Where possible, provide a deterministic v0.1 → v0.2 upgrader.

If a v0.1 claim cannot be upgraded without adding information, preserve it and mark the missing v0.2 field appropriately.

2. REPAIR B1 — HERITABLE UNIT IS NOT ALWAYS WELL-POSED

The current HU is a useful derived object, not a primitive.

Make the causal contribution graph primary.

resulting_hu must now permit at least:

* concrete HU reference;
* NOT_APPLICABLE;
* NOT_IDENTIFIABLE;
* ILL_POSED.

Define the distinction carefully:

NOT_IDENTIFIABLE

A meaningful answer exists in principle, but available evidence cannot determine it.

ILL_POSED

The requested singular identity is not well-defined under the declared ontology.

Examples include symmetric recombination where neither contributor has privileged continuity, or transformations where continuity is inherently many-to-many.

Do not use ILL_POSED merely because the adapter lacks data.

Architecture class

Add an optional higher-level architecture_class concept for cases where HU continuity is ill-posed but persistent organization is still meaningfully recognizable.

Architecture identity must be separately declared and justified.

It may be:

* exact;
* equivalence-class based;
* behavioral;
* structural;
* NOT_IDENTIFIABLE;
* ILL_POSED.

Do not default from sequence similarity.

Establishment

Establishment must state what persists:

* HU;
* architecture class;
* other declared heritable object.

No generic established=true without a persistence object.

3. REPAIR B2 — BODY VS IDENTITY

Split the old ENTITY concept.

At minimum distinguish:

BODY

A persistent physical/computational locus carrying state through time.

Examples:

* NPE victim body before and after rename;
* cell;
* organism memory allocation;
* persistent site.

IDENTITY

An engine-level identifier assigned to a body/process/entity.

Identities may:

* persist;
* change;
* be overwritten;
* split;
* merge;
* be absent.

A body may receive a new identity without ceasing to be the same body.

An identity may potentially migrate between bodies if the engine supports that.

Represent their relation explicitly.

Do not let engine IDs stand in automatically for embodied continuity.

Update host so it may reference BODY independently of IDENTITY.

Synthetic tests must include:

* same body / renamed identity;
* new body / inherited identity if representable;
* body destroyed and replacement created;
* host body persisting while material identity changes.

4. REPAIR B3 — SPLIT “EXECUTED MATERIAL”

Replace the ambiguous singular notion with explicit causal roles.

At minimum support:

WRITE_GOVERNING_MATERIAL

Material whose execution directly governed writes/contributions to the heritable output.

This answers something like:

Which code caused the inherited bytes/state to be written?

EXECUTION_SHARE

A distribution over material/regions describing where execution effort occurred.

This answers:

Where did execution time/steps occur?

They are not equivalent.

An event may spend most execution in foreign code while heritable writes remain governed by self material, or vice versa.

Keep an optional generic execution trace relation underneath them if useful.

Do not define “autonomous” until the contract states which role autonomy refers to.

If existing BEE categories use own-copy PCs while the lens uses overall step share, preserve both.

5. REPAIR B4 — PROVENANCE HAS ORTHOGONAL AXES

Separate at least:

MATERIAL ANCESTRY

WHOSE / from what prior material?

Examples:

* random founder;
* seed;
* transplant;
* copied source;
* mutation ancestor;
* recombination contributors.

SPATIAL / CONTEXTUAL ORIGIN

WHERE / under what local context was the material generated?

Add optional fields such as:

* made_in;
* location/niche/world reference;
* environment/regime reference where appropriate.

A niche tag must never be interpreted as material ancestry.

A transplant may therefore carry:

* material ancestry from donor;
* a new transport/context event;
* original made_in location;
* current location.

Keep these axes independent.

6. REPAIR B5 — FACTUAL CONTRIBUTION VS COUNTERFACTUAL SUFFICIENCY

This distinction is central.

Represent both separately.

FACTUAL CONTRIBUTOR

Derived from the actual realized trace:

Did material X contribute causally to the output that actually occurred?

Evidence basis may include:

* trace;
* taint;
* native write record;
* deterministic replay of the realized event.

COUNTERFACTUAL SUFFICIENCY / NECESSITY

Derived from intervention:

Could X produce the outcome under a specified counterfactual?
Was X necessary under a specified intervention?

Every counterfactual claim must include the intervention.

Examples:

* rebuild a randomized victim;
* remove donor writes;
* substitute host state;
* replace environmental input.

Do not expose a bare sufficient=true.

Use something like:

SUFFICIENCY(X, intervention=..., outcome=...)

Likewise for necessity.

An actual contributor can fail a sufficiency test.

A component can be counterfactually sufficient despite contributing little in the observed event.

Neither contradiction should be “resolved.”

This is exactly the distinction exposed by NPE.

7. TRUTH STATUS

Retain:

* YES
* NO
* NOT_IDENTIFIABLE

Add ILL_POSED only where the question itself is undefined, not for ordinary Boolean properties unless semantically justified.

Document which field classes permit it.

Do not allow adapters to use ILL_POSED as a softer NOT_IDENTIFIABLE.

Add validation tests that reject misuse.

8. GRAPH MODEL

Revisit the graph vocabulary after B1–B5.

Likely node classes now include:

* MATERIAL
* BODY
* IDENTITY
* EXECUTION
* TRANSFORMATION
* HERITABLE_UNIT
* ARCHITECTURE_CLASS
* ENVIRONMENT
* LOCATION

Likely relation families include:

* performed_by_body;
* assigned_identity;
* write_governed_by;
* execution_share;
* contributes_material;
* copies_from;
* mutates_from;
* recombines_with;
* hosted_by_body;
* transported_to/from;
* made_in;
* member_of_hu;
* member_of_architecture;
* counterfactual_test.

These names are suggestions, not a mandate.

Prefer the smallest coherent model.

Do not create ontology furniture that no specimen requires.

9. REWRITE THE INVARIANTS

Produce v0.2 invariants.

Preserve the substance of v0.1 I1–I12, but update them for the new distinctions.

Add explicit invariants covering at least:

HU ambiguity

No singular hereditary continuity may be asserted when the declared rule says continuity is ill-posed.

Body/identity

Identity reassignment cannot erase embodied host continuity.

Execution

Execution share cannot by itself establish write authorship.

Location

Spatial origin cannot establish material ancestry.

Counterfactuals

Counterfactual sufficiency cannot be substituted for factual contribution.

Intervention specificity

No counterfactual result exists without a named intervention and outcome.

Architecture

Architecture-class continuity cannot silently substitute for exact material/HU continuity.

Resolution

No adapter may report contributor granularity finer than its evidence.

10. SYNTHETIC CORPUS v0.2

Expand the existing corpus specifically to attack the new contract.

Include at least:

1. symmetric 50/50 recombination → HU ILL_POSED;
2. 60/40 recombination under a declared majority-HU policy;
3. rearranged self-copy where positional similarity is low but factual provenance is high;
4. persistent body renamed after overwrite;
5. executor spends 90% of steps in foreign material but own code governs inherited writes;
6. reverse case: local execution dominates but foreign code governs inherited writes;
7. material made in niche A but descended from donor B;
8. transplanted donor made in A, now located in C;
9. factual contributor that fails random-victim sufficiency;
10. low factual contribution that is counterfactually sufficient;
11. host required as state/scaffold but contributes no material;
12. multiple contributors with no meaningful singular lineage but stable architecture;
13. insufficient evidence → NOT_IDENTIFIABLE rather than ILL_POSED;
14. genuinely meaningless concept → ILL_POSED;
15. parent/body/identity all diverge.

Every case should have expected graph facts and explicit prohibited inferences.

11. RERUN PORTABILITY-01 AS A REGRESSION SUITE

Do not discover new adapter rules by looking at desired verdicts.

First port/freeze each adapter against v0.2 semantics.

Then rerun the same preserved evidence.

Targets:

* Archaeon
* BEE
* NPE
* PTE

Produce a v0.1 → v0.2 differential.

For every previously reported anomaly/disagreement state whether v0.2:

* RESOLVES_BY_DISTINCTION
* REMAINS_REAL_DISAGREEMENT
* BECOMES_NOT_IDENTIFIABLE
* BECOMES_ILL_POSED
* UNCHANGED

Do not count “resolved by distinction” as one side winning.

12. SPECIFIC EXPECTATIONS TO TEST, NOT FORCE

BEE AN1 / FF-28

Hypothesis:

write-governing authorship and execution-share decoupling explains the apparent disagreement.

Test it.

Do not force that answer.

BEE AN7 / FF-27

Hypothesis:

segment/material provenance plus architecture class handles frame-shifted copying better than positional resemblance or majority HU alone.

Test it.

NPE AN3 / FF-29

Hypothesis:

factual contribution + explicit counterfactual sufficiency captures host-conditioned reproduction without contradiction.

This is especially important.

PTE B1 / AN6

Hypothesis:

symmetric crossover should sometimes yield a meaningful architecture class while singular HU continuity is ILL_POSED.

Test this.

NPE FF-11

Hypothesis:

BODY vs IDENTITY preserves host continuity through renaming.

Test this directly.

13. PORTABILITY VERDICT AFTER v0.2

Do not preserve PORTABLE_WITH_DOMAIN_LIMITS automatically.

Re-adjudicate.

Possible outcomes remain:

* PORTABLE_CAUSAL_LENS_SUPPORTED
* PORTABLE_WITH_DOMAIN_LIMITS
* Z80_SPECIFIC
* ONTOLOGY_FAILURE
* INSTRUMENT_FAILURE

A promotion to PORTABLE_CAUSAL_LENS_SUPPORTED requires more than cleaner terminology.

At minimum:

* B1–B5 are representable without special-case hacks;
* all four engine adapters still work;
* the non-copy substrate remains legitimate;
* disagreements remain visible;
* abstention remains possible;
* no new contradiction as serious as B1–B5 appears.

14. HOST-CONDITIONED ASSAY READINESS

After v0.2 regression, evaluate the proposed cross-engine host-conditioned reproduction assay.

Do NOT preregister it yet.

Produce:

HOST_CONDITIONED_ASSAY_READINESS.md

Answer:

1. Is “host-conditioned reproduction” now definable in the same causal language across Archaeon, BEE, and NPE?
2. For each engine, can we independently manipulate:
    * donor/material;
    * host/body state;
    * environment;
        while holding the relevant other factors fixed?
3. Can the same abstract contrasts be implemented without pretending the engines have identical mechanics?
4. What is the common endpoint?

Prefer something like:

factual reproduction occurs in the observed host, but fails or changes under a preregistered host-state intervention.

Do not use a Z80-specific byte-copy endpoint as the universal criterion.

5. What would falsify the cross-engine claim?
6. Which engine has inadequate identifiability?
7. Can paired sham-host controls exist in all three?
8. What compute would the assay require?
9. Can it wait until Bellerophon’s current M2 campaign finishes?

End with exactly one readiness status:

* READY_TO_PREREGISTER
* READY_WITH_ENGINE_SPECIFIC_LIMITS
* NOT_READY
* QUESTION_NOT_PORTABLE

If READY, include a draft assay skeleton, but do not freeze a preregistration and do not launch.

15. LIGHT OBSERVATORY REVISIONS

Update OBSERVATORY_DESIGN.md for v0.2.

The cheap online layer should collect only the minimum needed for later causal reconstruction.

In particular, derive concrete ASK fields for each engine from the new gaps:

BEE

Consider persisting:

* replaced/occupant identity;
* per-source write counts;
* enough execution-source aggregation to separate write governance from execution share;
* recombination mate identity where applicable.

NPE

Consider:

* pre-rename body identifier;
* donor writes vs retained victim material;
* explicit intervention IDs for P-11-style sufficiency tests.

PTE

Consider:

* GA parent indices;
* recombination contributors;
* operator identity.

These remain proposed ASK fields.

Do not modify other seats’ engines unless explicitly coordinated.

16. PERFORMANCE

Measure the v0.2 overhead against the same specimens used in PORTABILITY-01.

Report separately:

* schema/adapter overhead;
* LIGHT observatory projected/actual overhead;
* FULL forensic overhead.

Do not run a long campaign to obtain these measurements.

17. NO HEAVY WORK

Bellerophon currently has a multi-day campaign on M2.

Do not compete with it.

Avoid:

* large process pools;
* long campaigns;
* large new replay batches;
* anything likely to consume several GB of RAM continuously.

Use preserved evidence and bounded single/few-worker replays.

If a required regression is unexpectedly expensive, run the minimum specimen needed to establish semantic correctness.

18. OTHER OPEN QUEUES

Do not execute the old Aphrodite Campaign 1 requests during this directive.

Create no new work from #452, #472, #475, #492, or #534.

Leave them pending for separate operator triage.

For Azure/admission-gate TODOs:

* identify the exact missing operator inputs;
* record them succinctly;
* do not guess values;
* do not block Contract v0.2 on them unless they are genuinely required for this work.

19. FINAL PACKET

Return one compact review packet containing:

1. v0.2 contract;
2. v0.1 → v0.2 changelog;
3. revised graph/schema;
4. new invariants;
5. synthetic corpus results;
6. all four adapter regressions;
7. B1–B5 disposition;
8. old anomaly/disagreement disposition;
9. v0.2 portability matrix;
10. updated false-friends ledger;
11. any new ontology break;
12. performance;
13. revised portability verdict;
14. host-conditioned assay readiness;
15. proposed light-observatory asks;
16. exact commits/tests/evidence pointers;
17. remaining operator inputs for Azure/admission items.

Do not optimize for promoting the verdict.

The most valuable outcome would be discovering that one of B1–B5 was merely the first symptom of a deeper failure.

The question is:

Can this become a rigorous causal language for inheritance across artificial substrates, while preserving the right to say that identity, heredity, or authorship is ambiguous—or not even well-defined?
