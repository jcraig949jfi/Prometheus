ARCHAEON — FOSSIL METABOLISM S3
INFORMATION-SEEKING PROBE SELECTION

S1 and S2 are CLOSED.

S1:
fossil-directed one-bit rule
-> NO_DETECTABLE_ADVANTAGE

S2:
exact multi-fossil constraint inference built and falsified against
enumeration;
production census
-> REPRESENTATION_INFORMATION_SPARSE;
no experiment licensed.

Do not rerun either season.

B1 is now the operational evidence source.
Raw SQLite access is retired.
Vivarium maintains recurrent scope membership.
Selection ancestry is complete.

NEW QUESTION

The corpus is information-sparse partly because previous experiments were
chosen primarily as candidate solutions, not as measurements.

Change the question from:

“Which candidate do I think will score best?”

to:

“Which experiment will most reduce uncertainty about what should be
tried afterward?”

An experiment may score badly and still be highly productive if its exact
outcome eliminates hypotheses or resolves uncertainty.

But “diverse”, “novel”, and “different” are NOT themselves information.

You must prove that a proposed probe has discriminating power.

=======================================================================
PHASE 1 — DEFINE INFORMATION VALUE EXACTLY

Work first in the existing bitstring/Hamming-score world where the target
space and observation semantics are exact.

Given current fossils E, define the feasible target set:

T(E) = { t : every observed (x,s) is consistent with t }

For a candidate probe q, its possible exact score outcomes partition T(E).

Define an information-value quantity from that partition.

Prefer an exact quantity that can be computed without knowing the hidden
target, such as one or more of:

expected remaining feasible targets;
worst-case remaining feasible targets;
expected entropy after observation;
expected eliminated targets;
minimax partition size.

Choose ONE primary acquisition objective before looking at production
results.

State explicitly what prior/weighting assumption is used if “expected”
appears anywhere.

Uniform over feasible targets is permitted, but it must be named as an
assumption rather than truth.

Do not use:

* LLM scoring;
* embedding novelty;
* textual diversity;
* distance alone;
* candidate task score as a disguised information score.

A distant probe may teach nothing.
A nearby probe may be maximally discriminating.
The partition is the evidence.

=======================================================================
PHASE 2 — BUILD A PROBE-SCORING ORACLE ON SMALL KNOWN WORLDS

Before touching production, construct small synthetic worlds where the
hidden target is known to the test harness but hidden from the selector.

For each evidence state:

1. enumerate T(E) exactly;
2. enumerate admissible probes q;
3. calculate each probe’s outcome partition;
4. calculate its acquisition value;
5. identify the exact optimum or optimal equivalence class.

Then test the proposed scalable selector against this oracle.

Required controls:

POSITIVE
A probe known to split the feasible set strongly must outrank one that
leaves it mostly unresolved.

USELESS
A probe whose possible outcomes do not distinguish the remaining
hypotheses receives no artificial reward for novelty/distance.

EQUIVALENCE
probes inducing the same partition receive equivalent information value,
regardless of cosmetic representation.

AMBIGUITY
selector must not claim a unique best probe when several are tied.

CHEAT
expose the true hidden target to a deliberately cheating selector and
prove the legitimate acquisition implementation never reads that field.

ORDER
permutation of fossil input does not change probe value.

ENUMERATION
acquisition calculations agree with brute-force target enumeration on
small L.

CONTRADICTION
inconsistent fossil sets fail closed rather than producing a probe.

=======================================================================
PHASE 3 — DOES INFORMATION-SEEKING ACTUALLY LEARN FASTER?

Now conduct a SYNTHETIC sequential experiment.

No SFE/Vivarium production rows yet.

Compare at least:

I = information-selected probe
U = existing uniform probe

Start both arms with the SAME initial evidence.

After each probe:
reveal its exact score;
add that fossil;
recompute the feasible target set;
choose the next probe according to that arm.

This is deliberately sequential.

The returned observation MUST influence the next choice.

Primary comparison should concern learning, not candidate quality.

Examples:

* probes required to identify the target;
* log2 feasible-target count after fixed N probes;
* uniquely fixed bits after N probes;
* cumulative uncertainty reduction.

Preregister the synthetic comparison before running the batch.

Include multiple target/evidence seeds.

Measure both:
information acquired
and
task score of the probes.

This lets us see whether information-seeking sacrifices immediate score
while improving later knowledge.

Do not declare failure merely because an informative probe scores poorly.

=======================================================================
PHASE 4 — TEST THE QUALITY/DIVERSITY CLAIM

The Keeper’s concern is broader than this bitstring toy:

Future selection requires experiments that produce RICH, DIVERSE,
DECISION-USEFUL evidence.

Test the first part of that proposition here.

For every selected probe record separate quantities:

candidate diversity
outcome diversity
information value
immediate task quality
incremental constraint value

Ask empirically:

Does simple candidate diversity correlate with information gain?

Do not assume yes.

We want:

DIVERSE CONSEQUENCES

not merely:

DIVERSE INPUTS.

If distance/novelty is a poor proxy for information, preserve that finding.

=======================================================================
PHASE 5 — DETERMINE WHETHER PRODUCTION IS LICENSED

Production is licensed only if the synthetic season shows that the
information selector materially improves the information state relative
to uniform probing.

Preregister the licensing threshold BEFORE running the synthetic
comparison.

Possible outcomes:

INFORMATION_SELECTOR_VALIDATED
NO_ADVANTAGE_OVER_UNIFORM
INFORMATION_OBJECTIVE_MISALIGNED
COMPUTATIONALLY_INTRACTABLE
REPRESENTATION_INSUFFICIENT

If not validated:
emit ZERO production rows.

Return the failure geometry and stop.

=======================================================================
PHASE 6 — IF VALIDATED, PREREGISTER A SMALL PRODUCTION ACQUISITION CAMPAIGN

Only after synthetic validation may you propose production execution.

This campaign has a different purpose from S1:

S1 tried to produce a better candidate.

S3 tries to produce a better NEXT DECISION.

Use landscapes where:

* B1 supplies enough starting fossils;
* inference is consistent;
* multiple hypotheses remain;
* candidate probes can induce meaningfully different outcome partitions.

Define two matched sequential arms:

I = information-directed acquisition
U = uniform acquisition control

Each arm gets the same initial evidence and same probe budget.

CRITICAL:
The arms must not contaminate one another’s evidence state.

An observation generated by I cannot silently become evidence for U during
the comparison, and vice versa.

Specify exactly how evidence snapshots/lineages are isolated logically
before row 1.

Preregister:

* landscape eligibility;
* initial fossil snapshot;
* acquisition objective;
* deterministic tie breaking;
* I/U policy;
* sequential update rule;
* number of steps;
* stopping rule;
* primary information metric;
* secondary task-quality metric;
* contamination rule;
* failure handling;
* build boundary handling;
* verdict thresholds.

Keep the first production campaign SMALL.

We are validating acquisition behavior, not filling the database.

=======================================================================
PHASE 7 — VIVARIUM HANDOFF

If production becomes licensed, hand Vivarium an explicitly sequential
campaign.

Do NOT enqueue the entire I arm at once if I_(n+1) depends on result I_n.

Required recurrence:

evidence state E_n
↓
Archaeon chooses q_n
↓
exactly one licensed probe executes
↓
returned fossil becomes B1-visible
↓
verify ancestry + scope visibility
↓
construct E_(n+1)
↓
choose q_(n+1)

The selector may not choose q_(n+1) before the evidence required for it
exists.

For the matched uniform arm, preserve its own independent evidence state
and equivalent execution budget.

Vivarium remains execution-only.

=======================================================================
PHASE 8 — PRODUCTIVITY SEMANTICS

For this season, distinguish at least:

SOLUTION_PROGRESS
probe improved immediate task score;

INFORMATION_PROGRESS
probe reduced uncertainty / eliminated feasible hypotheses;

BOTH

NEITHER

A failed candidate can therefore be productive.

But an experiment is NOT productive merely because it ran or because its
input was novel.

Record the exact information delta.

This distinction is important enough to preserve for later fossil
consumers.

Do not redesign the global schema merely to support these labels; keep
them in season evidence unless a real downstream consumer later demands
promotion.

=======================================================================
PHASE 9 — STOP CONDITIONS

Stop if:

* evidence becomes contradictory;
* acquisition objective cannot be computed honestly;
* information selector collapses to uniform;
* production evidence cannot be isolated between arms;
* B1 recurrence fails;
* ancestry cannot be reconstructed;
* engine/build boundary violates preregistration;
* the synthetic licensing threshold was not met.

Do not compensate by increasing the budget.

=======================================================================
RETURN

ACQUISITION OBJECTIVE
exact definition
assumptions
tie semantics

ORACLE
brute-force comparison
controls
failures

SYNTHETIC SEASON
preregistration SHA
I vs U
uncertainty trajectory
fixed-bit trajectory
immediate-score trajectory
licensing threshold
verdict

DIVERSITY
candidate diversity vs information gain
whether diversity was actually a useful proxy

PRODUCTION
NOT_LICENSED

or

preregistration SHA
landscapes
initial evidence snapshots
sequential I/U policy
budget
isolation mechanism

If executed:

per step:
E_n identity
selected probe
acquisition value
returned fossil
information delta
task-score delta
B1 visibility
ancestry
next-state identity

FINAL VERDICT
Did information-directed probing produce a better information state
than uniform probing under equal experimental budget?

Do not answer a larger question than the experiment supports.

The objective of this season is not to generate many fossils.

It is to establish whether Prometheus can deliberately generate the
fossils that make its NEXT experiment less ignorant.

If it can, preserve that mechanism.

If it cannot, preserve exactly why.