# Lessons — transferable methodology from the Incubation program

Each lesson states the rule, the specific observation that forced it (with the file
where it is recorded), and how to apply it elsewhere. These are behavior deltas, not
commentary; a lesson that cannot change a future experiment's design does not belong
here.

---

**1. Census before build, and census the population, not the generator's intent.**
Forced by: v1 census_v0 — the planted composition was in every witness, yet 85% of
witnesses were non-minimal and only 31% of the survivors forced it; the intended
phenomenon barely existed in the minimal-solution population the solver actually
inhabits. (results/census_v0.json)
Apply: before measuring any effect, prove the target structure is reachable, forced,
and non-vacuous in the population that generates the measurements — with pre-stated
pass bands, so a failed census is a rejection, not a discussion.

**2. Value-collision collapse scales ~1/m; small alphabets forge counterfeit
shortcuts.** Forced by: v1 census_v1 — acceptance 0.9–2.8% because short words touch
2–4 slots, making the effective space m^2..m^3; same-length alternatives and shorter
collapses are birthday effects. Large prime moduli fixed it (0.24–0.50).
(results/census_v1.json, census_v2.json)
Apply: when a claim depends on solution uniqueness or forcing, size the value space
so coincidences are measurably rare, and verify by exact enumeration on samples.

**3. In deterministic search, cost is ~a function of the witness; shared witnesses
are shared measurements.** Forced by: v1's first full run — every gate passed, then
the anti-cheat battery found 6 witness-word collisions between training and transfer
cells; identical words means the transfer cell partially re-tests the training
search tree. (commit 4cf4ab0d message; fix in worlds/families + harness used-sets)
Apply: sample witness structure without replacement across every cell of a
replicate; make the check executable and let it veto finished runs.

**4. Budgets must be strict or deep search lies.** Forced by: v2 census_meta_v0 —
an expansion could overshoot the meter mid-layer and still claim the goal, which
made forward search look able to solve worlds it cannot afford (and made
SEQ(fwd,fwd) "solve" the recursion world). (v2/results/census_meta_v0.json)
Apply: no success credit for work past the budget, ever; test it explicitly
(tests: strict_budget_no_goal_credit).

**5. Measure growth; never assume branching.** Forced by: v2 census — register
domains grow at 3.55^d, not 4^d (swap/rotation relations), which silently halved
effective depth; and the first dC generator set (involutions + 3-cycle) grew at
2.4^d, erasing the pathology the world existed to create.
(v2/results/census_meta_v0.json, census_meta_v1.json)
Apply: empirically measure ball growth for any generator system before choosing
depths, budgets, or "deep" thresholds.

**6. Separate storage from computation with two flat controls.** Forced by: v1
design requirement; the data made the separation total — the flat expression as a
one-shot candidate is node-identical to baseline, the inline unreified block is
strictly worse, and only the reified slot wins (0.169). (results/incubation_v1.json)
Apply: any abstraction claim needs a control that possesses the abstraction's
content without its structural privilege.

**7. Run the useless-artifact control; usefulness must be content-specific.**
Forced by: v1 P3R — a random length-matched macro is 3.3x WORSE than baseline
(230,626 vs 70,088 median nodes). Without this control, "the macro helps" could have
been an artifact of alphabet extension or depth accounting.
Apply: for every admitted artifact, measure a structurally identical but
content-random twin; the twin must lose.

**8. Predicate learners need cost-aware selection and structured candidate pools.**
Forced by: two v1 guard-learner defects found in smoke: (a) it preferred a single
2-execution-probe atom over an equivalent free+1-exec pair — guards must be cheap to
consult, so exact covers are ranked by evaluation cost; (b) equality atoms sharing a
failing probe inherit that probe's base coverage, so a flat top-N pool floods with
near-duplicates and evicts the atoms every real cover needs — pool per (probe, slot,
op) instead. (concepts/guard.py comments)
Apply: when fitting executable predicates, optimize (correctness, then evaluation
cost), and structure candidate pools by feature identity, not raw coverage.

**9. A trap must attack the operator's degradation mode, not its intended mode.**
Forced by: three dD designs. Starving the backward tree (drop rate) cannot break
meet-search because the backward ROOT is always meetable — a dead backward process
degrades bidirectional to forward-plus-waste (~1.4x), never failure. The lever that
works is the cost of backward expansion (spurious volume): at 24 junk predecessors
per call the frontier-balancing variant pays 2.1x and alternating variants collapse
(28x, solve-loss). (v2/results/census_meta_v3.json, v2/domains.py lineage comment,
recorded sweep in session; census_meta_v4.json)
Apply: before building a hostile world, derive how the target mechanism *degrades*
when its assumptions fail; aim the world at the degraded form.

**10. DSL leakage is a measurable quantity, not a vibe.** Forced by: the v2
requirement that the language must not spell BIDIRECTIONAL. Operationalized as:
count behaviorally distinct organizations by instrumented trace (78), the target
class's fraction of the space (2.52%), and the canonical rank of its first member
(49) — with pre-stated bands and the enumeration sha frozen into the
preregistration so the order cannot be tuned afterward.
(v2/results/census_meta_v2.json, v2/dsl.py)
Apply: whenever a hypothesis space could encode its own answer, quantify
"spelledness" before running, and pin the enumeration cryptographically.

**11. Behavioral equivalence is world-relative; admission needs hostile worlds.**
Forced by: v2's two operator variants (ALT vs frontier-balancing) tying EXACTLY in
clean worlds — both capture 1.000 of the ceiling — then splitting 33x vs ~2x under
the trap. Clean-world admission scored them identical; only dD could rank them.
(v2/results/operator_genesis_v1.json per-seed dD medians)
Apply: an equivalence claim is only as strong as the world set it was measured on;
include adversarial worlds in any artifact-ranking pipeline.

**12. One-seed smoke is engineering, never evidence.** Forced by: the v2 smoke
(seed 11) passing all twenty gates, followed by the 5-seed run failing two of them
— the smoke seed happened to construct the operator variant the trap punishes most,
inflating apparent harm. (v2/results/operator_genesis_v1.json, first-run record in
commit 6f2abe32 message)
Apply: treat single-replicate results as pipeline validation only; claims begin at
the preregistered replicate count.

**13. Detection signals must be executable, label-free, and zero-base-rate in
clean worlds.** Forced by: both experiments. v1: runtime failures (0 in wA/wB,
2.1M in wC). v2: meet-verify failures turned out to be RARE in the strengthened
trap, so detection moved to the backward-edge audit — replay of claimed edges —
which is 100%/0% by construction. (v2/runtime.py audit_backward; census W3/W4)
Apply: choose the failure channel whose clean-world base rate is provably zero;
if the obvious channel loses signal under a design change, move the channel, not
the gate.

**14. Learning-to-learn is measurable as acquisition cost, and the thing prior
learning changes is the ORDER of hypothesis evaluation.** Forced by: v2 phase E —
naive and experienced learners share the same space, budget, probes, and selection
rule; only the enumeration order differs (canonical vs library-neighborhood-first).
Naive: 1,200 candidates, nothing. Experienced: candidate #2.
(v2/learner.py naive_order/experienced_order; operator_genesis_v1.json e_naive/e_experienced)
Apply: to test whether learning changed later learning, freeze everything except
the ordering/prior that earlier learning is allowed to install, and meter the
search to first competence.

**15. Ship the rows with the verdict, and let executable batteries veto finished
work.** Forced by: program-wide practice inherited from standing doctrine — and
vindicated twice, when a fully-passing v1 run was discarded by its own witness
check and a fully-passing v2 smoke was contradicted by the replicated run. Every
verdict commit contains its per-task rows (3,125 and 1,640), its preregistration,
and its anti-cheat results.
Apply: a verdict without rows is an assertion; an anti-cheat battery that cannot
veto a passing run is decoration.
