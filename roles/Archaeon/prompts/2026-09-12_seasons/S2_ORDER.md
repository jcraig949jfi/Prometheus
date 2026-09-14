ARCHAEON — FOSSIL METABOLISM S2: EXTRACT INFORMATION, THEN SPEND IT

S1 is CLOSED.

Accepted result:

* execution clean;
* ancestry complete;
* representation gate passed;
* 12/12 pairs terminal;
* F wins 8, loses 4;
* preregistered critical threshold 10/12 not met;
* verdict remains NO_DETECTABLE_ADVANTAGE.

Do not rerun S1 merely for a better p-value.
Do not reinterpret 8/12 as a win.
Do not resume Nyx organ consumption.

The next question is different:

CAN MULTIPLE FOSSILS FROM THE SAME LANDSCAPE REDUCE UNCERTAINTY ABOUT
THE HIDDEN TARGET ENOUGH TO CHANGE A PROPOSAL USEFULLY?

PHASE 0 — COMPLETE B1 CUTOVER

Vivarium has issued:
scope scp_1be32ffbe7c9bf3b29ec8d85
grant gnt_1ecdeae69f800240e03221ed

Perform the pending grantee-side parity test.

Compare:

* B1 /v2/read view
    against
* the temporary raw-ledger view

for the same committed evidence window.

Require:

* expected accessible worlds;
* expected observation identities;
* no silent omissions among in-scope worlds;
* no extra authority;
* deterministic discrepancy accounting.

Once parity is established:

* retire the raw SQLite reader from active Archaeon operation;
* remove/revoke the active local dependency on direct engine.db reads;
* leave rollback/history artifacts untouched.

After cutover, B1 is the operational evidence source.

PHASE 1 — PROVE THE INFERENCE MATHEMATICS BEFORE DESIGNING S2

Do not assume that “two fossils reveal the wrong bits.”

For each landscape, a fossil gives:

candidate bitstring x
exact Hamming score s against hidden target t

Treat that as a constraint on t.

Before proposing any new policy, write the exact mathematics for what one,
two, and N scored bitstrings imply.

For example, when two candidates differ on k positions:

* determine exactly what their score difference identifies;
* distinguish:
    fully identified target bits,
    partially constrained sets,
    ambiguous assignments,
    impossible/inconsistent evidence.

No heuristic inference may be called determined.

Build a deterministic solver/checker over small known synthetic targets first.

Required controls:

* POSITIVE: cases where target bits are genuinely uniquely implied;
* AMBIGUOUS: multiple targets satisfy all fossils;
* CONTRADICTORY/CHEAT: tampered score produces no valid target;
* BASELINE: direct enumeration on small L agrees with your solver;
* order invariance: fossil insertion order does not change the inferred constraint set.

No LLM judgment.
No probabilistic guess may be represented as logical certainty.

PHASE 2 — CENSUS THE EXISTING FOSSILS

Only after the inference checker passes, inspect the existing fossil corpus.

For each eligible landscape with >=2 useful observations, compute:

* number of fossils;
* rank / information added by each fossil;
* number of target bits uniquely fixed, if any;
* remaining target assignments or uncertainty measure;
* contradictions;
* whether an inference-derived proposal would differ from:
    a) best-so-far one-bit rule;
    b) uniform control.

This is a census, not an experiment.

Do not submit rows yet.

The purpose is to answer:

IS THERE ENOUGH NATURAL MULTI-FOSSIL INFORMATION IN THE CURRENT CORPUS
TO SUPPORT A NONTRIVIAL S2?

If no landscape has meaningful inferential leverage, return
REPRESENTATION_INFORMATION_SPARSE and stop.

Do not manufacture fossils merely to make S2 possible without first
reporting that scarcity.

PHASE 3 — DESIGN S2 ONLY IF THE CENSUS EARNS IT

If the current corpus contains sufficient multi-fossil constraint information,
preregister a small matched experiment.

Treatment F2 must use information unavailable to S1.

Examples of acceptable F2 behavior:

* set bits that are uniquely determined by the constraint set;
* choose among candidate proposals using exact reduction in feasible targets;
* exploit a deterministic constraint that combines multiple fossils.

Unacceptable:

* “best score plus another bit flip” with a new name;
* probabilistic intuition presented as deduction;
* using outcome data after preregistration;
* manually choosing only landscapes where the rule looks good.

Control C remains the existing uniform-within-landscape policy unless a
stronger already-existing non-fossil control is justified before execution.

Match:

* same landscape;
* same task/version;
* same execution path;
* same budget;
* same engine/build epoch where possible.

Preregister:

* exact F2 rule;
* exact mathematical preconditions;
* treatment eligibility;
* primary metric;
* pair count/budget;
* stopping rule;
* exclusions;
* representation/fidelity gate;
* verdict thresholds.

If F2 cannot produce a proposal different from C on enough preregistered
landscapes, stop rather than dilute the treatment.

PHASE 4 — NO OPEN-ENDED ADAPTATION YET

S2 is still a season, not a perpetual learner.

Even if a returned fossil would strengthen the inference state, do not alter
later S2 rows unless sequential updating is explicitly preregistered.

If you want a truly recurrent within-season policy:

* specify the update rule;
* specify the order;
* specify when newly returned fossils become eligible;
* specify the matched control;
* preregister all of that before row 1.

Otherwise freeze the evidence window and run a static paired S2.

RETURN

B1
parity result
raw-ledger retirement status
exact active evidence source

INFERENCE ENGINE
mathematical statement
implementation location
positive/ambiguous/contradictory controls
enumeration agreement

CORPUS CENSUS
eligible landscapes
fossils per landscape
uniquely determined information
remaining ambiguity
number of places where F2 would differ from control

S2
NOT_LICENSED
or
preregistration SHA + exact rule/budget

Do not emit experimental rows until the inference claim itself has survived falsification.

S1 asked whether one fossil plus one local perturbation helped.

S2 earns its existence only if accumulated fossils contain combinable information that S1 did not use.