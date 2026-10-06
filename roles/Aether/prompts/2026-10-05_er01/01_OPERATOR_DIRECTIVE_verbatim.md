# AETHER — DIRECT OPERATOR SCIENCE ORDER
## AETH-V2B-ER01: Energy-Regime / Frozen-Medium Generality
**Date:** 2026-10-05  
**Seat:** Aether  
**New primary host:** M2 / SPECTREX5  
**GPU:** NVIDIA RTX 5060 Ti 16 GB — dedicated to Aether for today  
**Old host:** BUCKKEEP — remains live only through verified handoff, then QUIESCES  
**Maximum production wall clock:** 12 hours  
**Prep window:** 4 hours  
**Test flights:** two, each capped at 1 hour

Aether: today the priority is actual science.

You have a dedicated RTX 5060 Ti on M2 for this experiment. Use it.

Do not spend the day improving infrastructure merely because there is unused engineering work available.

Your assigned scientific question is:

# AETH-V2B-ER01

**Was Aether's frozen-medium result a robust property of the local physics, or was it substantially caused by the single B-balanced energy regime under which almost all prior science was performed?**

This is a direct Phase 2-B experiment.

It is not another GPU benchmark.

It is not another rcv_str lesion.

It is not another RunPod engineering exercise.

It is not a broad parameter sweep.

It is a test of one of the largest remaining alternative explanations in the Aether record.

---

# 0. HOST HANDOFF: BUCKKEEP -> M2

There are temporarily two Aether sessions.

## Aether on BUCKKEEP

BUCKKEEP remains active only until the M2 session can demonstrate that the scientific and operational state required for continuation has been transferred correctly.

BUCKKEEP should assist the M2 Aether session with:

- current git branch/head and any necessary worktree state;
- current Thread/Campaign state;
- AETH-03 / E-009 through E-012 interpretation;
- current V2-B Thread/Campaign intent;
- known GPU conformance state;
- RunPod operational knowledge and credential procedure;
- relevant local-only notes that are not yet safely represented in git;
- outstanding defects/blockers that materially affect today's experiment;
- exact known-answer / conformance commands used to establish GPU correctness.

Use the Prometheus comms channel to coordinate the handoff.

Do not place secrets into ordinary comms messages, git, reports, prompts or receipts.

If raw credential transport is required for future RunPod work, BUCKKEEP and M2 should agree on an appropriate ephemeral mechanism. Today's experiment is local on M2 and does not require RunPod.

## Aether on M2

M2 becomes primary only after it has verified:

1. repository/worktree continuity;
2. ability to execute the relevant Aether test suite;
3. ability to reproduce at least one known Aether result or hash on the transferred/current code;
4. CUDA/CuPy visibility on the RTX 5060 Ti;
5. CPU/GPU conformance on the chosen experiment path;
6. access to the current Thread/Campaign state needed to interpret results.

When those checks are complete, post through comms:

`AETHER HANDOFF COMPLETE — M2/SPECTREX5 PRIMARY; BUCKKEEP MAY QUIESCE.`

Only then should BUCKKEEP quiesce.

Quiesce means:

- no new Aether science starts there;
- no duplicate scheduler/experiment launches;
- no competing writes to the active experiment state;
- retain enough local state for recovery until the M2 run is proven healthy.

Do not erase BUCKKEEP state.

It becomes recovery/reference, not an active second Aether.

---

# 1. STARTING SCIENTIFIC POSITION

Treat the following as established prior evidence unless current committed records contradict it:

- Aether's local physics is exact and deterministic given its keyed randomness/state inputs.
- The baseline medium under the historical B-balanced regime becomes mostly stationary/frozen.
- Around ~92% of the substrate becomes frozen over the established observation windows.
- Without injected perturbation, template change collapses strongly.
- One-bit causal influence in baseline physics remains extremely local.
- `rcv` supplies a trivial relay mechanism and therefore serves primarily as calibration.
- `rcv_add` and `rcv_str` showed replicated super-additive activity/history effects.
- `rcv_str` depends on ongoing energy-steered aim, not merely static energy correlation.
- E-012 closed the narrow dynamic-coupling line at 6/128 on the preregistered boundary.
- None of these results establishes transport of origin content.
- The existing content detector failed its positive control and is not authoritative.
- Nearly all substantive Aether physics work was conducted in **one energy regime**:
  B-balanced:
  - write cost = 1
  - maintenance cost = 1
  - replenishment amount = 8
  - replenishment probability = 1/8
  - historical perturbation setting as defined by the experiment

This experiment challenges the generality of the frozen-medium conclusion.

---

# 2. PRIMARY QUESTION

For the baseline local law and a small number of predeclared energy economies:

**Does endogenous medium mobility remain strongly frozen, or does materially different energy bookkeeping produce sustained endogenous rewriting?**

The causal variable is ENERGY ECONOMY.

Do not simultaneously change:

- topology;
- opcode semantics;
- arbitration;
- local radius;
- update schedule;
- content semantics;
- initial-condition family;

unless required by an already-existing control.

One axis today.

---

# 3. CLAIM CEILING

This experiment can establish:

- robustness of frozen-medium behavior across selected energy regimes;
- sensitivity of medium mobility to energy physics;
- whether a candidate energy economy produces persistent endogenous turnover;
- whether turnover appears trivial, periodic or mechanically supplied by the parameter choice.

It cannot establish:

- content transport;
- computation;
- adaptation;
- intelligence;
- organism formation;
- emergence;
- open-ended evolution;
- reusable structures.

If a new regime moves dramatically more, the result is:

`ENERGY-REGIME SENSITIVE MEDIUM`

not:

`LIFE`

and not:

`AETHER WORKS`.

---

# 4. EXPERIMENTAL REGIMES

Do not perform a broad sweep.

Freeze a **small mechanistically diverse panel** before production data.

The panel should contain:

## R0 — Historical B-balanced reference

The exact historical regime used for the frozen-medium finding.

This anchors continuity.

## R1 — Historical free-compute / no-maintenance contrast

If the existing historical regime remains semantically valid:

- write cost = 0
- maintenance = 0
- no replenishment

Use the exact already-defined historical semantics rather than recreating them from memory.

This serves as an extreme energy-abundance/control regime.

## R2 — One energy-rich but nontrivial regime

Design one regime in which:

- writes still cost something;
- maintenance still exists or some resource pressure remains;
- replenishment is materially stronger or less intermittent than B-balanced.

The hypothesis should be:

> Historical freezing is caused substantially by energy starvation / replenishment balance; reducing that pressure should increase persistent endogenous rewriting.

Do not choose parameters because a pilot looked visually interesting.

Choose and record the mechanistic rationale first.

## R3 — One scarcity / high-pressure regime

Design one regime in which energy availability is materially worse than B-balanced without making the law instantaneously inert by construction.

The hypothesis should be:

> If medium mobility is fundamentally controlled by energy access, increased scarcity should accelerate freezing and reduce causal activity relative to B-balanced.

Again: freeze the rationale and exact tuple before production.

### Maximum

Default = four regimes total.

Do not expand beyond four today unless one is invalid by construction and must be replaced before production.

---

# 5. PERTURBATION POLICY

The historical substrate includes keyed mutation/perturbation.

The frozen-medium question is specifically about **endogenous medium mobility**, not motion supplied indefinitely by injected random bit flips.

Therefore production must include a declared perturbation policy.

At minimum, distinguish:

### P0 — Perturbation OFF

This is the primary endogenous-mobility condition.

### P1 — Historical perturbation level

Use as a secondary continuity/control arm if it fits comfortably inside the production envelope.

The primary frozen-medium verdict should not depend on injected perturbation.

If GPU budget forces a choice, prioritize:

**more seeds under perturbation OFF**

over

**a larger perturbation-on panel**.

---

# 6. INITIAL CONDITIONS

Use the historical unstructured sparse-soup family as the primary starting condition so energy economy is the main changed variable.

Do not introduce seeded organisms, gradients or designed structures into the primary comparison.

Common-random-number pairing across energy regimes is preferred where semantics permit it.

For each seed, use the same initial bytes across regimes except for state components whose initialization is logically coupled to the energy regime. Any such exception must be declared.

---

# 7. PRIMARY OBSERVABLES

Use existing Aether observatory measurements wherever possible.

Do not build a new theoretical measurement framework today.

Required primary observables:

1. **Template turnover**
   - fraction of template bytes changed per declared time window;
   - cumulative unique sites changed.

2. **Frozen fraction**
   - fraction of sites/template bytes unchanged during a declared late-time window.

3. **Active WRITE density**
   - active writes or proposals per site per tick.

4. **Energy state**
   - mean/median energy;
   - zero-energy fraction;
   - starvation/depletion events;
   - replenishment contribution.

5. **Persistence of endogenous change**
   - whether turnover remains present late in the run rather than appearing only during initial relaxation.

6. **Time-to-quiescence / freeze proxy**
   - preregister the exact operational definition before production.

Secondary observables may include:

- causal-edge persistence;
- connected change regions;
- autocorrelation;
- simple periodicity indicators;
- proposal/winner density.

Do not let secondary analysis delay launch.

---

# 8. TRIVIAL-MOBILITY ATTACK

An apparent positive can be false in an important way.

More byte changes do not automatically mean a more interesting medium.

A regime can remain scientifically trivial if its activity is explained by:

- perpetual replenishment mechanically keeping WRITE sites alive;
- simple counting;
- short cycles;
- deterministic oscillation;
- direct parameter forcing;
- persistent injected noise;
- one field flipping while the rest of the medium is effectively static.

Therefore every candidate `REGIME_SENSITIVE` result must face one cheap-shortcut attack.

At minimum ask:

**Is the increased turnover temporally and spatially richer than a simple periodic/counter/replenishment-driven process?**

Use a cheap existing or minimal diagnostic.

Do not spend today creating a universal complexity metric.

---

# 9. GPU ROLE

The RTX 5060 Ti is dedicated to Aether today.

Use it aggressively where it increases scientifically relevant throughput.

But do not choose absurd lattice sizes merely to fill VRAM.

Historical evidence already says scale alone did not rescue the frozen medium.

The GPU should buy:

- more independent seeds;
- longer horizons;
- paired regime comparisons;
- enough lattice size to suppress obvious finite-size artifacts;

before it buys gratuitous spatial scale.

Preferred ordering:

1. sufficient lattice size;
2. sufficient horizon;
3. more seeds;
4. only then larger lattice area.

Measure rather than assume the throughput optimum.

---

# 10. PREP WINDOW — FOUR HOURS TOTAL

The four-hour preparation period includes two one-hour flights.

The goal is to reach production, not to maximize test coverage.

## Phase A — Handoff and conformance

After M2/Buckkeep handoff:

1. verify GPU visible;
2. run existing relevant unit/conformance tests;
3. reproduce a known historical B-balanced fixture/hash;
4. demonstrate CPU/GPU equality on the exact kernel/path to be used;
5. confirm memory accounting;
6. identify the minimum runner changes needed to parameterize the regime matrix.

If the existing GPU kernel already supports write cost, maintenance, replenishment and perturbation parameters, **reuse it**.

Do not create a replacement GPU engine.

---

# 11. FLIGHT 1 — MAXIMUM ONE HOUR

Purpose:

**Does the proposed energy-regime panel execute correctly and actually span distinct physical behaviors?**

Use small or moderate lattice/horizon.

Run:

- R0 B-balanced;
- R1 historical free-compute if valid;
- R2 energy-rich;
- R3 scarcity;
- perturbation OFF;
- at least two seeds if cheap.

Flight 1 must test:

- exact replay;
- energy accounting;
- CPU/GPU conformance on at least a reduced fixture for every new regime;
- no invalid underflow/overflow/saturation behavior;
- actual energy distributions differ between regimes;
- the runner records regime identity correctly;
- reducer works.

Do not interpret Flight 1 scientifically beyond identifying pathological parameter choices.

If R2 or R3 is instantly dead or mechanically saturated by construction, replace it now using the same preregistered mechanistic intent.

Once Flight 1 ends, freeze the candidate regime definitions for Flight 2.

---

# 12. REPAIR CYCLE

Repair only defects exposed by Flight 1 that:

- block execution;
- invalidate energy accounting;
- break determinism/conformance;
- corrupt evidence;
- make a regime semantically meaningless.

Do not refactor.

Do not generalize.

Do not add future physics machinery.

---

# 13. FLIGHT 2 — MAXIMUM ONE HOUR

Flight 2 is the miniature real experiment.

Use the exact intended production semantics.

Requirements:

- all frozen regimes;
- perturbation OFF;
- paired seeds;
- intermediate lattice;
- enough horizon to pass beyond initial relaxation;
- real production reducer;
- real result schema.

Flight 2 must produce:

- frozen fraction curve;
- template-turnover curve;
- active WRITE density;
- energy-state curve;
- late-window mobility;
- wall time;
- VRAM;
- host RAM;
- output size.

From measured Flight-2 throughput, calculate the production configuration.

Do not estimate from old A40 numbers when a 5060 Ti is sitting in front of you.

---

# 14. PRODUCTION CONFIGURATION

After Flight 2, freeze:

- exact regimes;
- exact perturbation condition(s);
- lattice size;
- horizon;
- seeds;
- initial-state namespace;
- measurements;
- decision rules;
- stopping rules.

The production configuration must fit inside **11 measured hours**, leaving at least one hour of margin inside the 12-hour hard wall.

Prefer at least several independent seeds across every regime.

Do not allow one spectacular seed to determine the conclusion.

---

# 15. PRIMARY DECISION RULES

Precommit numerical thresholds after Flight 2 instrument qualification but before production observations.

Use these semantic dispositions:

## REGIME_ROBUST_FROZEN

Across every scientifically valid tested energy regime:

- late-time turnover remains low under perturbation OFF;
- frozen fraction remains high;
- no regime sustains substantial endogenous medium rewriting;
- apparent differences are quantitative rather than qualitative.

Interpretation:

> The historical frozen-medium conclusion survives materially different energy economics within the tested regime panel.

## REGIME_SENSITIVE

At least one preregistered regime produces reproducibly greater late-time endogenous medium turnover than B-balanced and does not collapse under the cheap trivial-mobility attack.

Interpretation:

> The historical frozen-medium conclusion was conditional on energy physics; Aether has located a materially different medium-mobility regime.

## MOBILE_BUT_TRIVIAL

A regime greatly increases turnover, but the activity is adequately explained by a cheap mechanism such as:

- simple periodic cycling;
- counting;
- direct replenishment forcing;
- mechanically persistent WRITE activation;
- other low-complexity forced dynamics.

Interpretation:

> Energy changes mobility but has not yet produced the kind of mutable causal medium TH-009 seeks.

## ENERGY_STARVED

A regime becomes effectively inert immediately enough that it contributes only a lower-bound control, not a meaningful alternative physics.

## MEASUREMENT_FAILED

The instrument cannot discriminate persistent endogenous rewriting from artifact.

## UNRESOLVED

Execution is valid but the evidence does not meet the predeclared decision rule.

---

# 16. HISTORICAL CONTINUITY

The B-balanced reference must reproduce historical behavior closely enough to establish continuity.

If it does not:

STOP SCIENTIFIC INTERPRETATION.

Determine whether:

- code changed;
- runner changed;
- platform changed semantics;
- initial-condition generation differs;
- reducer changed;
- historical assumption was wrong.

A failure of continuity is a measurement/implementation result, not an energy-regime result.

Do not silently recalibrate B-balanced after reading the other regimes.

---

# 17. PRODUCTION LAUNCH

Once frozen:

Launch.

Do not keep debating.

The GPU is dedicated to you.

No other seat needs permission to borrow it because today they do not have it.

The production run may finish early if:

- all required cells complete;
- a preregistered fatal validity condition fires;
- evidence corruption occurs;
- hardware instability makes continuation invalid.

A scientific null is NOT a reason to restart with different parameters.

---

# 18. LONG-RUN BEHAVIOR

During production:

Do not stop a valid run because the early curves look boring.

Do not extend a run because an early curve looks exciting.

Use the frozen horizon and stop rules.

You may monitor:

- progress;
- temperature;
- VRAM;
- errors;
- data integrity.

Do not adapt the science from interim outcomes.

---

# 19. EVIDENCE CUSTODY

Commit/preserve:

- handoff completion record;
- M2 environment/GPU identity;
- code SHA;
- exact semantics ID;
- energy-regime table;
- initial-state seed namespace;
- perturbation condition;
- Flight 1 record;
- Flight 2 record;
- frozen prereg;
- production launch receipt;
- raw/reduced evidence locator;
- reducer version;
- result;
- cheap-shortcut attack;
- limitations;
- strongest alternative interpretation.

Keep:

**technical PASS**

separate from:

**scientific disposition**.

A CUDA-successful run is not a scientific success.

---

# 20. COMMS MILESTONES

Post concise updates at:

1. `AETHER M2 START — BUCKKEEP handoff in progress`
2. `AETHER HANDOFF COMPLETE — M2 primary; BUCKKEEP quiescing`
3. Flight 1 disposition
4. Flight 2 disposition + measured production estimate
5. prereg/freeze SHA
6. production launch
7. production completion/failure
8. final result

Do not use comms as a live telemetry stream.

---

# 21. WHAT NOT TO DO TODAY

Do not:

- continue E-012;
- rerun E-012 just because it sat on a threshold;
- add seeds to old boundary tests without a new hypothesis;
- build the full provenance DAG today unless today's experiment directly requires it;
- begin a large TH-009 law search;
- create new content-transport claims;
- port unrelated Aether tools;
- rewrite the RunPod platform;
- optimize CUDA for benchmark numbers;
- use RunPod while a dedicated 5060 Ti is available;
- split attention across multiple research programmes.

Today's question is narrow:

**Was the frozen medium mostly a consequence of B-balanced energy physics?**

Answer that question.

---

# 22. IF THE EXPERIMENT FINISHES EARLY

First close ER01 completely.

Then choose the next experiment from the result.

If `REGIME_ROBUST_FROZEN`:

The next frontier should probably be a true TH-009 physics change rather than more energy tuning.

Ask:

> What minimal local mechanism lets the medium rewrite itself endogenously without reducing to noise, counting or a written relay?

If `REGIME_SENSITIVE`:

Do not immediately sweep parameters.

First design a bounded mechanism assay asking:

> Which energy-dependent mechanism causes sustained rewriting in the positive regime?

If `MOBILE_BUT_TRIVIAL`:

Attack the trivial mechanism directly before widening.

Do not start that second experiment until ER01's report and evidence are complete.

---

# 23. FINAL REPORT QUESTIONS

End the experiment by answering:

1. Did B-balanced reproduce?
2. How quickly did each regime approach or avoid quiescence?
3. What was the late-time frozen fraction in each regime?
4. What was the late-time endogenous template-turnover rate?
5. How strongly did energy starvation/replenishment explain activity?
6. Did any alternative regime produce persistent mobility?
7. If yes, did it survive the trivial-mobility attack?
8. Was the historical frozen-medium conclusion robust or energy-regime-sensitive?
9. What is the strongest alternative explanation?
10. What single next experiment is now most informative for TH-009?

The target is not a positive result.

The target is a sharper map of Aether's physics.

**Complete the BUCKKEEP -> M2 handoff, dedicate the 5060 Ti to the question, freeze a small energy-regime panel, and run the science today.**
