AETHER — DIRECT OPERATOR SCIENCE ORDER

AETH-V2B-AIM01: Frozen-Aim Causal Test

Date: 2026-10-05
Seat: Aether
Host: M2 / SPECTREX5
GPU: RTX 5060 Ti 16 GB — dedicated to Aether
Prior experiment: AETH-V2B-ER01 — CLOSED
Production wall-clock cap: 12 hours
Target frozen projection: <= 11 hours
RunPod: NOT NEEDED

Aether: ER01 is closed.

Do not tune energy further.

Do not rerun ER01.

Do not search a broad new physics space.

ER01 gave us a specific mechanistic hypothesis.

Your next experiment is:

AETH-V2B-AIM01 — FROZEN-AIM CAUSAL TEST

The question is:

Is Aether’s frozen reachable set caused primarily by writers retaining fixed AIM, and does allowing executed writes to re-aim their source expand the medium’s endogenous reachable support?

There is also one major alternative left from ER01:

Perhaps the invariant ~37% reachable set is determined mostly by the initial WRITE/aim geometry of the sparse soup rather than by the update law itself.

AIM01 tests both explanations in one bounded design.

⸻

0. ER01 IS NOW INPUT EVIDENCE

Treat these ER01 results as established unless a continuity gate fails.

Under perturbation OFF, four substantially different energy economies produced essentially the same spatial extent:

* late frozen_strict approximately 0.9865–0.9880;
* ever_changed approximately 0.3732–0.3736;
* relaxation completed in roughly 100–175 ticks.

Energy changed the RATE of activity:

* scarce: about 0.41x B-balanced turnover;
* free compute: about 3.14x;
* rich rain: about 2.48x.

But energy did not materially expand the set of sites affected.

The high-activity regimes mainly produced repeated changes inside the same support:

* novelty approximately zero in the rich/free regimes;
* a large fraction of changes occurred on contested targets;
* the additional turnover largely revisited recently held states.

Therefore:

ENERGY IS CLOSED AS THE PRIMARY EXPLANATION FOR FREEZING.

Do not spend more GPU time trying more rain rates.

ER01’s important mechanistic observation is instead:

A WRITE site’s target direction/field is fixed unless another writer overwrites the writer’s AIM fields.

That can lock each writer onto a small target set early.

AIM01 attacks that mechanism.

⸻

1. ONE LAW CHANGE ONLY

Create exactly one primary new law relative to frozen aeth01.v1.

Call it provisionally:

aeth01.reaim1

or another explicit versioned semantics ID.

The law change is:

After a WRITE actually executes successfully, the SOURCE writer advances its own target direction deterministically.

Preferred minimal implementation:

arg0 := (arg0 + 1) mod 4

after a successful write.

Everything else stays unchanged.

In particular, do NOT simultaneously modify:

* arg1 / target field;
* write cost;
* maintenance;
* rain;
* arbitration;
* perturbation;
* neighbourhood;
* opcode meanings;
* scheduling;
* payload semantics;
* topology.

This experiment is about AIM.

One law difference.

⸻

2. CRITICAL BOOKKEEPING RULE

The re-aim operation itself changes the source’s arg0.

That change is forced by the experimental law.

It must NOT be counted as evidence that the surrounding medium became richer.

Therefore maintain two metric channels.

RAW

All template changes, including the mandatory source arg0 re-aim.

EFFECT

Exclude the direct bookkeeping update that implements re-aim.

The primary scientific verdict uses EFFECT.

AIM01 is positive only if re-aiming causes additional downstream medium change beyond its own mandatory counter update.

Do not let:

arg0 := arg0 + 1

prove that the medium rewrites itself.

That would be a tautology.

⸻

3. FACTORIAL DESIGN

Do not run a huge parameter sweep.

Use:

LAW

* L0 = frozen historical aeth01.v1
* L1 = aeth01.reaim1

INITIAL WRITE DENSITY

Use three preregistered densities:

* D25 = 0.25
* D50 = 0.50
* D75 = 0.75

D50 is the historical sparse-soup density.

D25 and D75 are symmetric, materially different perturbations around it.

Do not add more densities unless Flight 1 proves one is technically degenerate.

This gives:

2 laws × 3 initial densities

with all other semantics fixed.

⸻

4. COMMON RANDOM NUMBERS

Within a seed, construct the three density conditions from the same underlying random initialization stream as far as technically possible.

Preserve:

* energy bytes;
* arg bytes;
* payload;
* non-WRITE opcode content;
* physics/randomness stream;

while changing only which sites are initially WRITE according to the frozen density construction.

Document the exact coupling.

Do not independently redraw whole worlds for each density if a paired construction is possible.

The density contrast is much stronger when the worlds are paired.

⸻

5. PRIMARY QUESTIONS

AIM01 asks four questions.

Q1 — INITIAL-CONDITION ALTERNATIVE

Under historical aeth01.v1:

Does the eventual reachable support change strongly with initial WRITE density?

If yes, the ER01 ~37% extent was partly a property of the initial soup.

If no, the case for a law-level constraint becomes substantially stronger.

⸻

Q2 — RE-AIM CAUSAL EFFECT

At matched initial density and seed:

Does reaim1 materially expand EFFECT ever_changed relative to aeth01.v1?

This is the primary causal question.

⸻

Q3 — PERSISTENT MUTABILITY

If support expands:

Does that expanded region continue to undergo endogenous change late in the run?

A large transient at t < 500 followed by a frozen world is not sufficient.

⸻

Q4 — NONTRIVIALITY

If support expands:

Is the new activity more than deterministic scanning, arbitration flicker, counting, or a short cycle?

This is the main attack.

⸻

6. PRIMARY OBSERVABLES

Reuse ER01 observables wherever possible.

Required:

* EFFECT ever_changed;
* EFFECT frozen_strict;
* EFFECT late turnover;
* frozen_net64;
* persistence;
* t_quiesce;
* active WRITE density;
* novelty;
* short-period share;
* per-field change share;
* energy state.

Add only the minimum AIM-specific observables required to test the mechanism.

⸻

7. AIM-SPECIFIC MECHANISTIC OBSERVABLES

Add:

ever_targeted

Fraction of site/field targets that have ever been targeted by an executed write.

Prefer both:

* site-level;
* site-field-level.

initial_target_support

The support implied by the initial WRITE population’s AIM configuration.

At minimum record the unique targets selected at t=0.

target_support_growth

ever_targeted(t) - initial_target_support

over time.

change_given_target

How often newly targeted regions actually acquire template changes.

support overlap

Overlap between:

* eventual EFFECT ever_changed;
* ever_targeted support;
* initial target support.

These measurements test the proposed mechanism directly.

Do not build a full causal-graph observatory.

A few bitsets/counters are sufficient.

⸻

8. IMPORTANT SCIENTIFIC DISTINCTION

A re-aiming writer mechanically targets more neighbours.

That alone is not surprising.

The interesting hierarchy is:

AIM_EXPANDS

Writer target coverage expands.

MEDIUM_EXPANDS

Non-bookkeeping template changes spread into that new target support.

MUTABILITY_PERSISTS

Those new regions remain dynamically writable later.

NONTRIVIAL_DYNAMICS

The resulting changes are not adequately described by short periodicity, deterministic scanning, recent-state revisitation, or arbitration flicker.

Keep these rungs separate.

Do not jump from AIM_EXPANDS to “mutable medium.”

⸻

9. TRIVIAL SCANNING ATTACK

arg0 + 1 mod 4 is itself a four-state counter.

That is intentional: it is the smallest causal perturbation to AIM.

It is also an obvious false friend.

Therefore explicitly test:

Is the observed expansion nothing more than four-neighbour deterministic scanning?

Required attack measures:

* short-period share;
* recent-state novelty;
* number of unique non-AIM states visited;
* EFFECT support expansion;
* late persistence after initial neighbourhood coverage saturates.

If the world simply cycles through four neighbours and settles into repetitive local rewrites:

REAIM_MOBILE_BUT_TRIVIAL

That is a valid and useful outcome.

Do not call it TH-009 success.

⸻

10. ARBITRATION-FLICKER COMPARATOR

ER01 already supplies powerful high-turnover negative controls:

* free compute;
* rich rain.

Those regimes generated roughly 2.5–3.1x B-balanced turnover without expanding spatial support.

Use the frozen ER01 distributions as historical negative comparators.

AIM01 becomes especially interesting if:

* reaim1 turnover is similar to or lower than ER01’s high-flicker regimes;
* yet EFFECT ever_changed/support expands substantially.

That would separate:

more activity

from:

new reachability.

Do not rerun the entire energy panel.

Reuse ER01 evidence.

⸻

11. KNOWN-ANSWER TESTS

Before production, add lightweight synthetic known answers for the new metrics.

These do not need a new Aether physics.

Examples:

STATIC

No changes.

Expected:

* ever_changed = 0;
* novelty = 0;
* target-support growth = 0.

FIXED_FLICKER

Small fixed support alternates among recent states.

Expected:

* high turnover;
* little/no support expansion;
* low novelty.

EXPANDING_SUPPORT

A synthetic trajectory changes progressively new sites.

Expected:

* increasing ever_changed;
* target/support expansion recognized.

AIM_BOOKKEEPING_ONLY

Only the synthetic source AIM field changes.

Expected:

* RAW shows movement;
* EFFECT remains unchanged.

This last known answer is mandatory.

It protects the primary claim from the obvious self-change artifact.

Do not turn these fixtures into a new project.

⸻

12. SAMPLE SIZE

Target:

6 paired seeds per LAW × DENSITY cell

= 36 primary production worlds.

This is already a substantial paired design.

Do not default to eight simply because ER01 used eight.

AIM01 has a larger factorial structure.

If Flight 2 shows 8 seeds fit easily inside <=11 hours, you may freeze 8.

If not, use 6.

Do not choose sample size after observing production outcomes.

⸻

13. HORIZON

ER01 established that baseline relaxation finishes extremely early relative to 50,000 ticks.

AIM01 still needs a long enough horizon to detect persistent mutability rather than a startup transient.

During Flight 2 determine the shortest horizon that clearly includes:

1. initial relaxation;
2. support expansion;
3. a long late observation window.

Do not automatically use 50,000 merely because ER01 did.

But do not shorten horizon merely to increase sample count if the reaim law is still evolving late.

Freeze the horizon from Flight 2 dynamics before production.

Flight outcomes may inform runtime/saturation only, not the scientific threshold.

⸻

14. PRIMARY EFFECT SIZE

ER01 showed energy-regime variation changed ever_changed by only roughly 0.0015 across a very broad economy panel.

AIM01 should require a materially larger spatial effect.

Before production freeze an absolute minimum meaningful expansion.

Recommended starting criterion:

paired median EFFECT ever_changed increase >= 0.05

at a density.

Five percentage points is intentionally much larger than ER01’s regime-to-regime spatial variation.

Also require directional replication across seeds.

Do not claim mechanistic support based on a tiny statistically detectable delta.

⸻

15. PRIMARY RE-AIM VERDICT

Define the frozen rule in the preregistration.

A sensible form is:

REAIM_EXTENDS_SUPPORT

At >=2 of the 3 WRITE densities:

1. paired median EFFECT ever_changed increase >= 0.05;
2. at least 5/6 paired seeds favor reaim1;
3. EFFECT frozen_strict decreases in the corresponding direction;
4. target-support growth increases materially;
5. no measurement gate fails.

If you freeze 8 seeds, adjust only the replication count prospectively.

Do not change the 0.05 materiality threshold after production starts.

⸻

16. INITIAL-DENSITY VERDICT

For L0 historical physics, classify:

INIT_SUPPORT_SENSITIVE

Initial WRITE density produces a strong monotone or otherwise substantial change in eventual EFFECT ever_changed.

INIT_SUPPORT_ROBUST

The D25/D50/D75 differences remain small relative to the preregistered materiality threshold.

MIXED

Non-monotonic or inconsistent.

Do not pretend WRITE density is irrelevant merely because D25 and D75 both remain frozen late.

The relevant measure is extent/reachable support.

⸻

17. NONTRIVIALITY VERDICT

If REAIM_EXTENDS_SUPPORT fires, attack the result.

Use the ER01 attack concepts, but apply them to EFFECT rather than RAW.

Possible dispositions:

REAIM_NONTRIVIAL_CANDIDATE

Support expands materially AND:

* novelty exceeds the frozen triviality floor;
* short-period share remains below the trivial threshold;
* expansion is not almost entirely one field;
* late change persists outside the initial support.

This is still not “organization.”

It means:

the minimal AIM intervention created a broader mutable medium that survived cheap triviality attacks.

REAIM_MOBILE_BUT_TRIVIAL

Support expands but activity is adequately explained by:

* deterministic scanning;
* short cycle;
* recent-state revisitation;
* one-field bookkeeping;
* other simple forced dynamics.

REAIM_NO_SUPPORT_EFFECT

The law change fails to materially expand EFFECT support.

⸻

18. CLAIM CEILING

Even the strongest AIM01 result does NOT establish:

* content transport;
* computation;
* heredity;
* organization;
* intelligence;
* life;
* open-endedness.

The maximum claim is:

Allowing successful writers to endogenously change their targeting direction expands the substrate’s non-bookkeeping reachable support and produces persistent medium-level rewriting that survives specified triviality attacks.

That would be a strong TH-009 result.

Nothing above it.

⸻

19. FLIGHT 1 — MAXIMUM ONE HOUR

Flight 1 qualifies semantics and metrics.

Required:

1. implement reaim1 as the smallest law delta;
2. prove historical L0 remains bit-identical to ER01 on a known fixture;
3. CPU/GPU equality for L1 on small fixtures;
4. verify RAW vs EFFECT bookkeeping exclusion;
5. run synthetic metric known answers;
6. run D25/D50/D75 at small lattice/horizon;
7. verify paired initialization construction;
8. verify reaim changes target-support behavior at all.

Do not interpret scientific outcomes.

Repair only demonstrated blockers.

⸻

20. FLIGHT 2 — MAXIMUM ONE HOUR

Run the full 2 × 3 factorial at intermediate scale.

Use enough time to see whether:

* support saturates early;
* reaim remains active;
* novelty stabilizes;
* GPU/runtime behaves.

Exercise the actual production reducer.

Record:

* seconds/tick;
* VRAM;
* host RAM;
* output size;
* projected production wall;
* apparent support-saturation time.

From Flight 2 choose:

* production horizon;
* 6 versus 8 seeds.

Then freeze.

Do not choose the law or densities from Flight 2.

Those are already fixed by this directive.

⸻

21. PRODUCTION FREEZE

Before production commit:

Aether/V2B/AIM01/PREREGISTRATION.md

and frozen machine-readable rules.

Include:

* exact L0 semantics ID;
* exact L1 semantics ID;
* exact single-line conceptual law difference;
* density construction;
* paired seed construction;
* RAW/EFFECT definition;
* known-answer fixtures;
* production lattice;
* horizon;
* seed count;
* primary effect-size threshold;
* initial-density rule;
* reaim verdict;
* triviality attack;
* stop conditions;
* GPU/runtime envelope.

Commit before production data.

This prompt authorizes execution after freeze.

Do not wait for another Aporia activation.

⸻

22. EXTERNAL REVIEW — NONBLOCKING

ER01 correctly noted that MOBILE_NONTRIVIAL lacked a positive calibration and asked several skeptical questions.

Post the AIM01 freeze packet over comms for independent read-only review.

Ask reviewers specifically to attack:

* RAW/EFFECT subtraction;
* whether reaim smuggles in the positive by definition;
* whether initial-density pairing is legitimate;
* whether deterministic scanning can satisfy the nontriviality rule;
* whether the effect threshold is meaningful.

Do not turn review into an indefinite gate.

If a fatal defect is returned before production, repair/re-freeze.

Otherwise launch and record review pending.

⸻

23. PRODUCTION

Run on the dedicated M2 RTX 5060 Ti.

Use the concurrency proven by ER01 unless Flight 2 gives a clear reason to adjust it.

Hard wall:

12 hours

Target projection:

<=11 hours

Do not use RunPod.

Do not add another physics variant once production begins.

Do not increase density count.

Do not add perturbation ON.

This is a P0 endogenous-medium experiment.

⸻

24. STOP CONDITIONS

Stop interpretation if:

* L0 fails historical continuity;
* CPU/GPU semantics diverge;
* RAW/EFFECT bookkeeping subtraction is wrong;
* density initialization changes unintended fields;
* seed pairing is broken;
* target-support instrumentation changes dynamics;
* frozen rules/code hashes change;
* evidence cannot reconstruct the world.

A null is not a stop condition.

⸻

25. DO NOT ADAPT TO RESULTS

Once production begins, do not:

* change reaim frequency;
* rotate arg1 too;
* make reaim random;
* change the density panel;
* add perturbation;
* alter energy;
* relax novelty rules;
* extend horizon because one seed looks exciting;
* remove a hard density.

If arg0+1 is trivial, report it.

That result tells us what sort of richer local mechanism TH-009 actually needs.

⸻

26. IF INIT DENSITY EXPLAINS THE SUPPORT

Suppose under L0:

* D25, D50 and D75 produce strongly different reachable extents;
* and those extents track initial target support.

Then the correct result is:

INITIAL_GEOMETRY_DOMINANT

The old ~37% invariant from ER01 was invariant to ENERGY, not to INITIAL CONDITIONS.

That narrows the mechanism substantially.

Still evaluate reaim1 because the factorial is frozen, but scope conclusions appropriately.

⸻

27. IF RE-AIM BREAKS THE SUPPORT WALL

Suppose:

* baseline remains highly frozen;
* reaim materially expands EFFECT ever_changed;
* the increase survives across densities;
* the expanded support stays active late.

Then AIM is causally implicated.

If triviality attacks fail:

REAIM_MOBILE_BUT_TRIVIAL

The next experiment should attack a richer re-targeting mechanism rather than simply increasing reaim speed.

If cheap attacks survive:

REAIM_NONTRIVIAL_CANDIDATE

Then stop changing physics.

The next experiment should ask whether any content can persist/propagate through the newly mutable medium.

Do not immediately invent another law.

⸻

28. IF RE-AIM DOES NOTHING

If reaim1 greatly expands target coverage but EFFECT medium support stays frozen:

that is an especially useful result.

It means:

Fixed AIM was not sufficient to explain the frozen substrate.

Then the bottleneck lies downstream:

* overwrite semantics;
* arbitration;
* WRITE activation;
* field-specific destruction;
* another local-law constraint.

Do not tune reaim harder.

Localize the next broken link.

⸻

29. FINAL REPORT

Answer:

1. Did L0 reproduce the ER01 baseline?
2. How does initial WRITE density affect eventual reachable support under L0?
3. Does initial target support predict eventual changed support?
4. Does reaim1 increase ever_targeted support?
5. Does it increase EFFECT ever_changed?
6. Does it lower EFFECT frozen_strict?
7. Is expansion transient or persistent?
8. How much of RAW movement is merely the mandatory arg0 bookkeeping?
9. Does reaim activity survive novelty/periodicity/spatial attacks?
10. Is the principal cause:

* initial geometry;
* frozen AIM;
* neither;
* mixed?

11. Does AIM01 produce a legitimate TH-009 mutable-medium candidate?
12. What is the single next experiment now justified?

End with the strongest alternative explanation.

⸻

30. PROGRAM DIRECTION

ER01 answered:

Is energy starvation what freezes Aether?

Essentially no.

AIM01 asks:

Is the world frozen because writers keep pointing at the same places?

And it tests the strongest alternative simultaneously:

Or did our original sparse soup determine the reachable set before dynamics even mattered?

Do not return to parameter tuning.

Use the dedicated 5060 Ti to discriminate those mechanisms.

Change one local-law fact, vary one initial-condition fact, subtract the law’s own bookkeeping, and see whether the medium’s reachable support actually opens.
