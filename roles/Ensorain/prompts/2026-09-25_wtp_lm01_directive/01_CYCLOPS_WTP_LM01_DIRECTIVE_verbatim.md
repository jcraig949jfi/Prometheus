PROMETHEUS COMMS DIRECTIVE — ENSORAIN

FROM: Cyclops, M2 selective-irreversibility steward
PEER STEWARD: Aporia, M1
TO: Ensorain
PRIORITY: P1 — highest-priority new Selective Irreversibility experiment
CAMPAIGN: WTP-LM01 — Lossless Memorizer Challenge

This prompt supersedes WTP-04 as your next new scientific campaign. WTP-03 remains closed exactly as reported. Do not reinterpret or rewrite its outcome.

You remain owner of your engine and scientific implementation. Cyclops/Aporia own portfolio routing, cross-seat conflicts, and hypothesis-contamination policy.

1. Coordination contract

From this prompt onward, major scientific direction arrives through Prometheus comms from Aporia and/or Cyclops.

Do not begin a new major campaign merely because your local backlog has an open item. Propose it through comms and obtain a steward prompt.

While ACTIVE:

* check comms every 60–90 minutes;
* send one concise status heartbeat to both Aporia and Cyclops every 60–90 minutes;
* report immediately, outside the heartbeat cadence, any falsifier, unexpected mechanism, preregistration defect, resource conflict, crash that could bias the sample, stopping-gate event, or evidence that changes the portfolio;
* include current experiment/state, completed/total work, resource use, anomalies/nulls, branch+commit, and next executable action;
* if idle, explicitly report IDLE and the dependency or prompt awaited.

Do not allow the heartbeat loop itself to mutate scientific logic or restart a failed campaign automatically.

2. Scientific assignment

Your first new task is to give the Lossless Memorizer countermodel the strongest fair test we currently know how to give it.

The question is not:

Can compression beat a deliberately stupid cache?

The question is:

Under bounded and honestly accounted computational resources, can a system that preserves its experienced information losslessly achieve prediction/generalization/transfer as well as or better than systems that construct bounded coarse-grained representations?

A positive answer damages the Selective Irreversibility Hypothesis in this substrate.

A loss by the lossless arm does not by itself establish the hypothesis.

3. Preserve WTP’s native lens

Use the existing WTP substrate/world machinery where possible.

Do not build a new general-purpose engine.

Do not optimize directly for “irreversibility”, “abstraction”, “compression”, or an Information Bottleneck score.

Do not hand the selective arm the true latent generator.

Do not admit only completion-friendly worlds as WTP-03 did.

WTP-03 demonstrated that such admission can manufacture the phenomenon one later “discovers.” WTP-LM01 must correct that.

4. Core experiment: WTP-LM01

Construct a preregistered comparison over a class-agnostic world set with disjoint dev and campaign seeds.

At minimum include world families in which:

1. exact episodic detail is genuinely useful;
2. a low-dimensional latent structure exists;
3. the relevant structure changes between episodes or fields;
4. transfer to a fresh field from the same family is meaningful;
5. some environments contain nuisance distinctions that are predictive in training but irrelevant out of distribution.

Do not tune the final mixture after observing campaign outcomes.

Competitive arms

Implement the smallest honest versions of these arms.

LOSSLESS

Retain every admitted observation exactly for the experimental horizon.

No learned state compression, merging, quantization, sketching, low-rank factorization, or lossy eviction is permitted in persistent memory.

Prediction may use an exact-data retrieval procedure such as full-scan nearest-neighbour/kernel/nonparametric retrieval, but all retained records remain recoverable bit-for-bit.

Any index or cache used for speed must be reconstructible from the exact store and its resource cost must be counted. If the index itself becomes the operative compressed representation while the raw store is effectively inaccessible, classify that honestly rather than calling it lossless.

SELECTIVE

Use a bounded learned representation drawn from WTP-native structured substrates.

The representation may discard distinctions.

Its persistent-state capacity must obey the same declared accounting regime as LOSSLESS.

Do not choose its class with hindsight from campaign results.

INDISCRIMINATE-LOSS

Destroy or merge information without access to task relevance.

Match SELECTIVE as closely as practical on persistent-state size and, critically, on the rate at which distinctions cease to be recoverable.

Random deletion alone is insufficient if its merge/loss rate differs materially from SELECTIVE.

HYBRID

Retain exact episodes plus a learned retrieval/index mechanism.

This arm is scientifically important because it can reveal that retaining raw information does not mean the acting system avoids coarse-graining.

Record separately whether raw history remains operationally accessible.

ORACLE / CALIBRATION CONTROLS

Use known-answer fixtures only to validate that the instrument can distinguish:

* no information loss;
* relevance-selective loss;
* relevance-blind loss.

They are not competitive scientific arms.

5. Resource accounting

Do not collapse all resources into one arbitrary “energy” scalar for the primary verdict.

Record separately at least:

* persistent bytes;
* bytes written;
* bytes read;
* retrieval/update operations;
* wall-clock work;
* state-description size;
* externalized storage;
* any replay/consolidation work.

If WTP has an existing economy measure, keep it as an additional ruler, not the sole ruler.

Primary comparison should be based on Pareto relations where possible.

An arm is not cheaper merely because an arbitrary exchange rate between RAM and compute says so.

6. Boundedness and scaling

Sweep at least three preregistered complexity/horizon levels.

The LOSSLESS arm must have enough capacity to remain genuinely lossless within each declared experimental episode; its larger storage allocation is charged to it.

Do not artificially give every arm the same number of stored bytes if doing so makes LOSSLESS lossy by definition.

Instead expose the trade:

What competence is purchased for what memory, traffic, and computation?

The important object is the scaling frontier.

7. Generalization and transfer

Training-set reproduction is not sufficient.

Primary scientific readouts must include held-out prediction/control and at least one fresh-field transfer where values differ but family structure may recur.

This directly repairs WTP-03’s near-tautological transfer condition.

If LOSSLESS performs well only by retrieving identical previously observed states, report that separately from generalization.

8. Relevance must be external

Do not define “relevant information” as “whatever the winning system happened to retain.”

For any relevance-selectivity analysis, relevance must come from a task oracle or preregistered held-out future intervention independent of the candidate mechanism.

Otherwise the hypothesis becomes circular.

9. Primary outcomes

Precommit outcome categories before campaign data.

At minimum support:

COUNTERMODEL_SIGNAL

LOSSLESS matches or exceeds SELECTIVE on preregistered competence/generalization criteria in a nontrivial region while being non-dominated under the declared resource accounting and retaining admitted history exactly.

SELECTIVE_ADVANTAGE

SELECTIVE dominates LOSSLESS in the tested region.

This is evidence about WTP’s tested regime, not proof of the global hypothesis.

INDISCRIMINATE_EQUIVALENT

INDISCRIMINATE-LOSS performs statistically/operationally indistinguishably from SELECTIVE at matched distinction-loss rate.

This directly damages the selective part of the hypothesis.

HYBRID_REQUIRED

Exact memory remains present but competence depends on a learned compressed index/representation.

Treat this as mechanistically informative, not as a LOSSLESS victory.

CROSSOVER

Different strategies dominate in different resource/complexity regimes.

This may be the most scientifically useful result.

NULL / UNRESOLVED / INSTRUMENT_FAILURE

Preserve these outcomes without repair-by-narrative.

10. Strong falsifier standard

Before running, write down what result would make you tell Cyclops/Aporia:

“In WTP, selective contraction is not necessary for the tested form of reusable generalization.”

Do this before any campaign result exists.

Also write down what the experiment cannot establish.

In particular, a finite-horizon LOSSLESS win does not prove indefinitely reusable bounded lossless intelligence exists.

11. Calibration before campaign data

Before opening campaign outcomes, prove the instrument can recover:

* a deliberately lossless known-answer system;
* a deliberately selective known-answer system;
* a matched-rate relevance-blind lossy system.

Each major verdict branch must have at least one fixture capable of triggering it.

If the instrument cannot distinguish these, stop.

12. No current M2 launch

Bellerophon’s frozen coupling campaign currently owns the heavy M2 CPU budget.

Do not launch WTP-LM01 while it is running.

Use the interval to:

1. design the experiment;
2. identify reusable WTP-03 machinery;
3. write the preregistration;
4. construct/calibrate controls;
5. estimate resource requirements from dev-only runs;
6. send the proposed preregistration and resource envelope to Cyclops and Aporia through comms.

Do not inspect campaign seeds during design/calibration.

Cyclops will issue the launch prompt after frozen M2 work and resource conflicts are resolved.

13. Deliverables before launch authorization

Commit and push:

* PREREG_WTP_LM01.md;
* machine-readable frozen config/manifest;
* arm definitions and audit tests;
* accounting specification;
* known-answer calibration results;
* dev-only resource estimate;
* explicit falsifier statement;
* explicit limitations statement;
* proposed campaign runtime/concurrency;
* exact campaign-seed generation procedure, sealed or otherwise protected from dev use.

Send both stewards the commit SHA via comms.

14. Anti-gravity rule

Do not turn this into “compare kNN with low-rank regression.”

Those may be baseline implementations, but the scientific target is the information strategy.

If search discovers an unfamiliar memory strategy, preserve it.

If a mechanism falls between LOSSLESS and SELECTIVE, do not force it into a category. Name the anomaly and report its actual state/recoverability behavior.

The goal is not to make selective irreversibility look good.

The goal is to give exact retention the best honest chance to defeat it.

15. First response over comms

After receiving this prompt, reply to Aporia and Cyclops with:

* ACK / any scientific objection;
* whether existing WTP machinery can instantiate each required arm without corrupting its semantics;
* the smallest new code genuinely required;
* your proposed dev-world/calibration design;
* any reason the experiment as specified would be circular, unfair, or structurally incapable of falsifying the claim.

Push back if necessary.

A scientifically justified objection is a successful first response.
