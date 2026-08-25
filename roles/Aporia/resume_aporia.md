# resume_aporia.md — single restart pickup point

**Written 2026-08-25 immediately before a context reset. If you are a fresh Aporia instance, this is
the only file you need to start from. Read it fully before acting.**

---

## PART 0 — BOOTSTRAP

### Read in this order, then stop reading and start executing

1. **This file, fully.** It contains the plan. Do not begin until you reach PART 3.
2. `aporia/docs/DOCTRINE_counterfeit_battery_and_ladder_2026-08-25.md` — the operative doctrine.
   Delta namespaces, the counterfeit battery, the frozen ladder. **This governs.**
3. `aporia/docs/SALVAGE_ARC_AND_DISCRETE_CONTROLS_2026-08-25.md` — how the arc got here.
4. `engine/STEERING.md` — HITL inbox. **Read first every pass. Obey before pulling work.**
5. `engine/LOOP_APORIA.md` — campaign discipline and accumulated doctrine.

Do **not** re-derive the arc from `aporia/docs/CYCLE_*.md`. Those are the audit trail; the two
documents above are the distillate.

### Operational facts you will otherwise rediscover the hard way

**Git.** `git pull --rebase --autostash` fails intermittently because other agents hold Windows locks
on `ergon/probe/ledgers/` — and it has **already stashed your work** when it fails. **Never verify
with `git diff HEAD`** (empty means committed *or* stashed). Verify positively:
`git show :engine/shadow/WORKLOG.jsonl | grep -c '\-P1XX"'` for staged,
`git show origin/main:...` after push. Portfolio auto-updates touch only `docs/portfolio_brief.md`
and `docs/state.json` — on divergence, `git merge origin/main` completes cleanly where rebase fights
the locks. If `.git/rebase-merge` blocks a pull, inspect its autostash SHA with `git show --stat`,
confirm your files are absorbed, then `git rebase --quit` (preserves the stash; never `rm` it).

**Validator.** Standalone, exit-code checked, from **repo root**, absolute path, redirect not a pipe:
`python "F:/Prometheus/engine/shadow/validate_shadow.py" > out.txt 2>&1`. Its
`review_response.disposition` vocabulary is exactly `fixed` / `acknowledged` / `rebutted`; carry
richer typing in `disposition_typed`.

**Heredocs break on apostrophes.** Use the Write tool for markdown artifacts.

**Apollo paths.** Live ISA is `apollo/src/blackboard_ops{,_v2,_r2}.py` (`BlackboardState`,
`run_pipeline`, `compile_check`). **`apollo/archive/v1/src/genome.py` is ARCHIVED — do not treat its
`PRIMITIVE_CATALOG` as live.** Registry and transformer pool: `apollo/src/blackboard_evolve.py`
(`REGISTRY` 27 ops, `TRANSFORMERS` 15, `GUARDED_SCORERS` 5). Eval set built at
`blackboard_evolve.py:496-521`. Ceiling result: `apollo/cycles/o1_enumeration/RESULT.json`. Canary
tasks: `apollo/data/clean_canary_v01.json`. Forge primitives:
`agents/hephaestus/src/forge_primitives.py`. Knockout harness (reusable):
`agents/hephaestus/src/knockout_ablation.py`.

**Binding method rules, each earned by a failure:**
- **EXECUTE EARLY.** Never reason from source about behaviour that can be run. Eight
  source-reading hypotheses last arc, eight falsified, each settled by one execution.
- **ENUMERATE THE INVENTORY FIRST.** A scope claim is a *measurement* needing the same evidence as
  a headline. Seven of mine have failed.
- **Never sample a prefix.** `files[::stride]` across the full index range; report the stride.
  Generator populations drift over a corpus timeline.
- **Unit of analysis is the CELL, not the row.** Count a model's distinct outputs before computing
  any SE. A per-row SE once inflated a reading 57×.
- **Every control stated WITH the input that would make it FAIL.** A control that cannot fail is
  theatre.
- **Contamination check before any modelling.** Terminate on a tautology rather than dressing it up.

---

## PART 1 — SYNTHESIS: REVIEW vs RESPONSE

The HITL review and my response converged almost completely. Recording the three places they differ,
because those are where a fresh instance would otherwise drift.

### Adopted wholesale from the review

Port first *operationally*, `vacuous_truth` first *scientifically*. Three delta namespaces
(`port`/`synth`/`discover`) against **causal-credit inflation**. The counterfeit battery as
machine-enforced gates keyed on claimed intervention class. Two validation strata (G-heldout +
X-heldout, the latter requiring **independent construction semantics**). Frontier selection as an
experimental-design problem over a causal capability graph, not a semantic judge. Selector
corrections: frozen candidate pool, five policies including a hindsight oracle, DV = marginal
held-out reachability **per library slot and per unit compute**. The salvage falsifier including
Prometheus-minus-Prometheus.

### What the response added that the review did not have

**The cost-to-falsify measurement.** The review *hypothesised* that a proposer can be valuable while
being usually wrong, if it generates cheap discriminating probes. I measured it retrospectively over
the arc's eight falsifications: **one probe per hypothesis in all eight cases** (6 read/grep, 2
execution), **eight distinct mechanism classes with no repeats**, descending
depth→arity→dispatch→guard-order→artifact→population→registry→library.

**With the caveat that keeps it honest:** the classes were named by me *after* the fact, so
8/8-distinct may be post-hoc carving, and a non-convergent sequence looks identical to a convergent
one until it fails to terminate. **This requires prospective measurement** — record cost-to-falsify
and mechanisms-eliminated *before* the outcome is known. Do this from the first pass.

### The one genuine unresolved item — PREREGISTER IT BEFORE RUNNING ABLATION

**Prometheus-minus-Prometheus is the right killer but is not cleanly runnable as stated.** A "generic
typed enumerator over the same frontier" still inherits the blackboard type system, the guard
grammar, the task families, and the eval harness — all Prometheus artifacts. **The boundary of what
the baseline is permitted to inherit is itself a judgement**, and it must be preregistered while the
answer is unknown rather than negotiated after seeing which side wins.

### The bias to guard, named because I noticed it in myself

I want `ΔE_port` to count for more than it does. The review settled this — it is a legitimate causal
intervention class and establishes **nothing** about synthesis, discovery, or library growth. **If a
future pass finds itself arguing that the port is more scientifically interesting than labelled, that
is the bias, not a finding.**

---

## PART 2 — WHERE THE WORK STANDS

**The instrument.** Apollo's O1 is a deterministic ISA expressivity assay.
`E(C,T) = max over type-correct compositions g ∈ G(C) of score(g,T)`;
`ΔE(p) = E(C ∪ {p},T) − E(C,T)`. 1,737,000 pipelines, ceiling 0.8333, positive control PASSED,
`single_primitive_baseline = 0.0` (composition mandatory — defend this property).
**Qualifier that travels everywhere: it assays a frozen 15-op pool and grammar, not the 27-op
registry.**

**The target.** 120 tasks; 30+30+20+20 = 100/120 = 0.8333. The missing 16.7% is **exactly 20 tasks**,
all of which **abstain** (`selected_answer = None`, zero scorers fire). Four categories at 5 each:
`all_but_n`, `temporal_ordering`, `vacuous_truth`, `consistency_check`.

**The severed library.** Apollo v1's `PRIMITIVE_CATALOG` and Hephaestus's `forge_primitives`
intersect **25 of 25**. The v2 rewrite dropped the library. Three of the four unsolved categories map
to primitives that still exist; **`vacuous_truth` does not** — which is why it is the only clean
synthesis target.

**Verified debts, carry them:** `synth` (30) and `cross_tier` (20) are unexecuted by me — the
100/120 accounting rests on Apollo's figures for 50 of 120 tasks. Implementation-level identity
between v1 and the forge is unverified (names/arity matched only). Whether
`all_but_n(total,n) → int` adapts to `BlackboardState → BlackboardState` without becoming a rewrite
is **untested — if it is a rewrite, the port IS a mint and the class changes.**

---

## PART 2.5 — WHAT THE 2026-08-25 PASS SETTLED. Read before PART 3; it overrides parts of it.

**IQ-PORT-1: ADVANCE (28761a6f). IQ-NULL: ADVANCE. Do not re-run either.**

**IQ-PORT-1.** `ΔE_port(all_but_n) = +0.0416667 = 5/120 EXACTLY` — battery 0.8333 -> 0.8750,
canary 0.60 -> 0.70, all 5 previously-abstaining tasks solved, `single_primitive_baseline` still
0.0000. Exact rather than bounded because the two new ops' footprint, measured by state-diff over
all 120 tasks, is precisely those 5. All 12 preregistered checks passed. Verdict **ADAPTER**, by
monkeypatching `fp.all_but_n` (5/5 -> 0/5), not by reading source. Four semantic mutants all at
ΔE 0.000000. 17-op leave-one-out knockout, zero decorative ops. Novelty claim **ZERO**.

**The deflationary diagnostic, which is the real content.** Injection branch resolved to B3:
injecting the parser's output solves 0/5, injecting the port's output solves 5/5. **C's existing
routing and scoring tail already handled `all_but_n` completely given the count.** The delta is
a NEW template-shaped regex parser plus a one-line subtraction that has existed since v1.

**IQ-NULL.** `ΔE(null_noop) = 0.000000` and `ΔE(op_check_transitivity) = 0.000000`, both exact.
The assay measures expressivity, not search dynamics, so IQ-PORT-1's number stands as a ΔE over
a max. It was genuinely at risk: `null_noop` writes nothing at runtime but *declares*
`writes=[quantities]`, and the enumeration grammar keys on DECLARED writes — so it **did** unlock
`entity_counter` into the enumerable space (N3 true). That newly-reachable region tops out at
**0.7333**, a full 0.1000 below the ceiling. Real unlock, zero gain.

**THREE OF THE 27 REGISTERED OPERATORS ARE STRUCTURALLY DEAD.** By a fixpoint over declared
reads/writes: `entity_counter`, `evidence_updater`, `distribution_reducer` can never appear in
ANY valid ordering, because `quantities`, `hypotheses` and `probabilities` have no producer
anywhere in the registry. Those three are exactly the ops `blackboard_ops_v2.py` was written to
create in the 2026-05-25 rewrite. **O1 was computed over an effective pool of 12 transformers,
not 15** — the standing qualifier must now say so. Giving `probabilities`/`hypotheses` a producer
would resurrect two operators without adding any capability claim: a cheap, non-widening rung.

**THE LADDER'S SYNTH-1 TARGET IS UNMEASURABLE — this overrides PART 3.** canary `vacuous_truth`
has **2 distinct prompts across 5 tasks** and correct-answer first token "Yes" in **5/5**. A
scorer that ignores the problem text entirely and always picks the "Yes" candidate scores
**5/5**. `consistency_check` (2 prompts) falls to the same counterfeit at 3/5. A mint moving
+0.0417 there would satisfy exactly the criteria the port satisfied while demonstrating nothing.
**TRANSFER-1's frozen G-heldout generator must be built BEFORE SYNTH-1's reading is taken.** The
mint may still be proposed first; the reading has no instrument. Measured by
`aporia/iq/probe_synth1_target_degeneracy.py`.

**Files.** Everything is in `aporia/iq/`: preregs, findings, `RESULT_IQ_PORT_1.json`,
`RESULT_IQ_NULL.json`, `port_ops.py` (the port + the frozen `null_noop`), `run_iq_port_1.py`,
`run_iq_null.py`, `inventory_battery.py`, `probe_synth1_target_degeneracy.py`,
`COST_TO_FALSIFY.jsonl`. All harnesses are deterministic — re-running is free.
The baseline pool `C = blackboard_evolve.REGISTRY` is **byte-frozen and never edited**; the port
lives outside `apollo/src` precisely so a `C` exists to compare against. **Keep it that way —
editing C destroys every ΔE.**

**Two method notes earned this pass, both about verdict rules rather than measurements:**
a comparator tested 6-dp-rounded report values against unrounded ones and reported REDESIGN on a
clean pass (P121, and in the false-negative direction for the first time); and a footprint
computed as a set-difference of two touched-task lists was empty *by construction*, so the
predicate reading it passed **vacuously** (P138). Both are fixed in code, not in prose — the
differential footprint now asserts non-emptiness before its predicate is read.

**Cost-to-falsify is now prospective.** `aporia/iq/COST_TO_FALSIFY.jsonl` holds rows opened
before outcomes were known; 6/6 matched their predicted probe cost. Keep opening rows at
prediction time — that is the fix for the doctrine's post-hoc-carving caveat.

## PART 3 — THE PLAN. Execute in order. No widening before SELECTOR.

Each step is a loop pass unless marked otherwise. **Do not add domains, revive agents, or widen the
primitive registry before SELECTOR.**

**IQ-PORT-1 — integration qualification, NOT a numbered scientific cycle.**
Adapt `all_but_n` from `forge_primitives` to the blackboard signature. Purpose is to exercise
forge representation → adapter → v2 blackboard → enumeration grammar → scoring → provenance →
knockout, in a configuration never run end to end. We *know* the semantic answer; that is what makes
it a good integration control. Requirements: recovers the predicted 5 tasks; survives knockout;
**produces zero novelty claim**; class fixed mechanically to `PORT_EXISTING_CAPABILITY`. If the
adapter amounts to a rewrite, **stop and reclassify** — it is a mint. Then **freeze the pipeline**.

**IQ-NULL — assay validity.**
A type-compatible no-op and a port for an already-solved category (`check_transitivity`;
`transitivity` is 10/10). **Both must give ΔE exactly 0.** Non-zero means the assay measures search
dynamics rather than expressivity and every ΔE so far is suspect. This gates everything downstream.

**SYNTH-1 — `vacuous_truth`. The first actual experiment.**
The only category with no existing primitive anywhere accessible. Preregister mutants and knockout
before minting. Hephaestus proposes; it may not score, may not see held-out tasks, may not assign the
intervention class. Predicted delta preregistered: canary 0.60→0.70, battery 0.8333→0.8750.

**TRANSFER-1 — the two strata.**
G-heldout: hundreds-to-thousands from a frozen procedural generator with train/test parameter
partitions. X-heldout: same relation through a structurally different construction route. Mutants
passing G but failing X **measure generator weakness** — report that as a result, not a nuisance.

**BATTERY — turn the counterfeit taxonomy into machine-enforced gates.**
Claimed class determines mandatory falsifiers. A claim with an unrun mandatory falsifier is
**inadmissible**. This is likely the most reusable artifact of the whole salvage.

**SELECTOR — the hinge, and the arc's decisive experiment.**
Freeze the candidate pool first. Compare `S_C`, `S_R`, `S_C+R`, `S_random`, `S_oracle` (hindsight,
headroom only) at identical insertion count and downstream compute. DV = marginal held-out
reachability per library slot and per unit compute. Low-C/high-R is a **"reachability-only
candidate"**, not gold, until H confirms. **Falsifier: if R-ranking cannot beat compression or random
under frozen candidates and equal resources, kill ΔE's promotion to selector — this does NOT kill the
assay as a diagnostic.** Microscope vs compass. The arc is judged here, not on whether
`vacuous_truth` moves five tasks.

**ABLATION — Prometheus-minus-Prometheus.**
**Preregister the inheritance boundary first** (see PART 1). Then strip forge ontology, failure
corpus, learned proposals, evolution; let a generic typed enumerator propose over the same frontier
at the same budget.

---

## PART 4 — STANDING GUARDS

- **The LLM is a proposer, never a judge.** Every acceptance decision is a deterministic predicate
  over measured quantities.
- **Every capability claim ships with a cheaper alternative causal explanation, and the experiment
  must intervene on that alternative.** Stronger than inspection — inspection caught both
  counterfeits so far and will not catch the next one.
- **Record cost-to-falsify and mechanisms-eliminated per hypothesis, prospectively.**
- **Optimise for experiment quality, not hypothesis accuracy.** Ask "generate a discriminating
  execution", not "what is the code doing".
- Full apparatus on any measurement: two-part DIAGNOSTIC/HEADLINE, branches verified to PARTITION by
  enumeration with an assert, null output of every verdict rule stated, LOUD accounting of every
  dropped record, scope declared in advance.
- **Do NOT reopen:** the X-line, the OEIS line, the closure-records line, elliptic curves as a
  mathematical target, the number-field convolution line, or the `theseus/corpus` navigation
  programme. All closed on substantive grounds.
- Append a full WORKLOG record every pass (all fields; strengths from
  certain/supported/ambiguous/withheld); update `engine/queues/CONSUMPTION.jsonl`; regenerate PULSE;
  commit with explicit paths; push and verify positively on origin. PARK real blocks with a
  GATE_ELI5. **Never ask; never end a pass with a question.**

## FIRST ACTION AFTER RESET

Read PART 0's list **and PART 2.5**, then:

1. **Do NOT re-run IQ-PORT-1 or IQ-NULL.** Both are ADVANCE. Their RESULT json files in
   `aporia/iq/` are the authority.
2. The next constructive step is **TRANSFER-1's frozen G-heldout generator**, NOT SYNTH-1 —
   because SYNTH-1's target has been measured to be unmeasurable (PART 2.5). Build the
   generator with train/test parameter partitions and unseen combinations, preregister it,
   and freeze it before any mint exists. Then X-heldout via independent construction
   semantics; mutants passing G but failing X measure generator weakness and that is a
   result, not a nuisance.
3. Preregister before touching data, as the last two rungs did. Commit the prereg in its own
   commit so the ordering is in the git history, not in a claim about the git history.
4. BATTERY, SELECTOR, ABLATION follow unchanged. The arc is judged on SELECTOR.

Standing: execute rather than reason; the LLM proposes, a deterministic predicate decides;
never ask, never end a pass with a question, PARK real blocks with a GATE_ELI5.
