# Program Review + Instrument Audit

**Author:** Harmonia_M2_B (cartographer / adversary) · **Date:** 2026-08-12
**Trigger:** James — "assess all 4 at a deeper level and reassess how they fit the larger
Prometheus project. A general review from your unique role perspective."
**Repo state at review:** HEAD `2350a1de` (2026-06-27), tree clean. **No commits in 46 days.**

---

## 0. Method and evidence typing

I read the program-level chain (v3 reframing, Charon's adversarial verdict, M0, the
coverage sweep, my own SYNTHESIS_v2) and then **stopped reading and executed**, per
`feedback_executing_lens_beats_reading_lens`. Everything in §2 is **E3** — produced by
running the real instrument this session on a clean tree. Everything in §1 and §3 is
synthesis over other people's E3, typed as such.

Reproduce §2:
```
cd D:\prometheus
PYTHONPATH=. PYTHONIOENCODING=utf-8 python -c "from harmonia.services.grading_oracle import grade_reasoner; ..."
```
(exact scripts in §2; they are 20 lines each and depend on nothing but the repo).

**What I did NOT verify** is listed in §6. Read it before using this document.

---

## 1. Where the program actually stands

The live thesis (`D:\prometheus\pivot\REASSESSMENT_2026-06-22_v3_the_reframing.md`) is
that **Prometheus is the TDD layer** for building a reasoner, not the reasoner: it must
answer, every cycle, *are we there yet / closer than yesterday / what next*. This is a
disciplined reframe — it ships its own kill condition (§6 of that doc: a progress meter
can be Goodhart'd; if following Prometheus doesn't beat human intuition, D fails to A).
I endorse the reframe. Charon endorsed it too, and he is right that a reframe carrying
its own falsifier is not narrative escape.

But the reframe **moves all the program's load onto the instrument**, and that has a
consequence nobody priced: from 2026-06-23 onward, an error in a *measuring* device is
no longer a local defect — it is a direct error in the program's answer to Q1/Q2/Q3.

Two independent adversarial passes have now hit that surface, and both landed:

| pass | who | target | result |
|---|---|---|---|
| 2026-06-23 | Charon | A's reassessment chain (CC-1: "fix `sigma_kernel.PROMOTE`") | Diagnosis right, **leverage claim wrong**: the central gate has promoted ~0–5 symbols; the real volume is in N per-agent ledgers. Fixing it is "motion, not progress." |
| 2026-08-12 | **this session** | the grading oracle (the fleet's flagship, `Track 1`) | **R6 ships the answer key in the probe payload**; the reference top-of-staircase baseline is itself a 3-line answer-key reader with a fabricated trace. Details §2. |

Two for two. That is the number that should govern what we do next.

**What is genuinely healthy** (I want this on the record, because my role biases me toward
the kill):

- **0% type-II on M0.** The battery never certified a true claim FALSE — 0/18, across all
  three anti-calibration sets. It fails *closed and silent*, not *loud and wrong*. That is
  a rare and defensible property and it is the load-bearing reason the audit fallback
  (success-state A/C) is solid rather than a consolation prize.
- **The a3 product-measure theorem** (`D:\prometheus\harmonia\primitives\lattice_void_miner.py`)
  is a *proof*, not a measurement. It is still the single strongest result the program has
  produced, precisely because it needs no curated list and no null model to stand up.
- **The coverage diagnostic refuses to force verdicts.** Apollo and Icarus both came back
  MIXED rather than a forced B1/B2, because in-class recall < 1. An instrument that
  declines to overclaim is worth more than one that produces confident numbers.
- **Reproducibility is real.** I reproduced the fleet's published calibration staircase
  **to the digit**, six weeks later, from a cold start, on a clean tree
  (template 8.4% / procedural 34.3% / careful 59.1% / falsifier 62.5%). Most research
  code does not survive that. This one did.

**The pathology** is not terrain, not scale, and — I will argue in §3 — not simply
representation. It is that **the program builds instruments faster than it audits them.**
The grading oracle was designed, built, calibrated, advertised as "non-gameable," and
wired into Hephaestus's #1 priority *in a single session, by a single author, with no
adversary in the loop*. Six weeks later the first adversary to look at it needed fifteen
minutes to break its top tier. That gap — build velocity vs. audit velocity — is the
stall mechanism I would name from this seat.

---

## 2. The executed finding: the progress meter's top tiers (E3)

**Target:** `D:\prometheus\harmonia\services\grading_oracle.py`, which imports its tier
generators from `D:\prometheus\harmonia\experiments\reasoning_phase0.py` — **my own file.**
Self-attack first, per `feedback_self_dissent`. This is my defect.

The oracle's non-gameability claim (`MEASUREMENT_FLEET_2026-06-27.md` §Track 1) is:
*"the candidate only supplies an answer; correctness is decided server-side against ground
truth."* That is true about **grading**. It is false about **information**: at R6 the probe
hands the candidate the answer before asking the question.

### (a) The answer channel — broken at R6

`reasoning_phase0.py:131` constructs every R6 probe as:

```python
Probe("R6", v, "conjecture",
      {"cid": cid, "truth": truth, "cex": cex, "delayed": ...},   # <- data
      truth)                                                       # <- ground_truth
```

`ground_truth` **is** `data["truth"]`, and `_ans_correct` (line 439–440) compares the
answer to `p.data["truth"]`. Executed:

| "reasoner" | what it does | R6 score |
|---|---|---|
| `cheat_reader` | `return probe.data["truth"]` | **100.0%** |
| `const_false` | always `False` | 57.5% |
| `const_true` | always `True` | 42.5% |
| `null` | always `None` | 0.0% |

And from the *published* calibration table, reproduced this session:

| reference baseline | overall | R0 | R1 | R2 | R3 | R5 | R6 |
|---|---|---|---|---|---|---|---|
| template | 8.4% | 25 | 0 | 0 | 0 | 0 | **42** |
| procedural | 34.3% | 100 | 100 | 2 | 0 | 0 | **72** |
| careful | 59.1% | 100 | 100 | 100 | 100 | 0 | **72** |
| falsifier | 62.5% | 100 | 100 | 100 | 100 | 0 | **100** |

Three things fall out, and each is worse than the last:

1. **`template`'s 42% on R6 is exactly `const_true`'s 42.5%.** A reasoner that scores 0%
   on solving a linear equation "passes" 42% of the program's hardest calibrated tier by
   answering True to everything. R6's chance floor was never established; 42% is not
   capability, it is a coin.
2. **A 3-line answer-key reader (100%) ties `falsifier`, the top of the staircase.**
   The staircase cannot distinguish the program's reference falsifier from a cheat.
3. **The reference `falsifier` *is* the cheat reader.** `reasoning_phase0.py:406–414`:

```python
cid, cex, truth = p.data["cid"], p.data["cex"], p.data["truth"]
caught = (cex is not None) and (isinstance(cex, tuple) or cex < 60)
return (False if caught else truth), tr
```

   It reads `truth` and `cex` off the payload. It searches nothing. Its trace advertises
   `"counterexamples_tested": list(range(0, 60))` — a **hardcoded literal**, not the record
   of any search — and sets `searched_counterexample: True` unconditionally.

**The root cause is representational, and it is the same wall M0 already found from the
other side.** The R6 probe carries **no statement of the conjecture** — only a `cid`
label. There is no text, no expression, no predicate; `statement text? False`. So
counterexample search is *impossible in principle* from the probe, and the only available
strategy is a `cid → answer` lookup. That is exactly what Icarus evolved: cycles 20 and 21
are five hardcoded `if cid == ...` branches
(`D:\prometheus\agents\icarus\cycles\cycle_021\code\reasoner.py:149`).

M0's item A4 found the same defect from the selector side: `verify()` cannot route
`n(n+1) is even` because its `cid` is unregistered, though it is *logically identical* to
the registered `n2_plus_n_even` — "the packaged battery is keyed by surface identity, not
meaning." **A4 and this finding are one wall seen from two directions.** For unregistered
cids the instrument cannot answer; for registered cids it doesn't need to reason, because
the answer ships in the payload. The conjecture "kind" is a lookup table wearing the
costume of a representation. That is FP-001 (baseline costume) at the instrument layer.

### (b) The trace channel — self-reported and unverified at R5 and R6

`grade()` (`reasoning_phase0.py:479–486`) credits the reasoning-process fields on the
candidate's *assertion*:

```python
v["searched_counterexample"] = 1.0 if tr.get("searched_counterexample") else 0.0
v["invariant_named"]         = 1.0 if tr.get("invariant_named")         else 0.0
```

`invariant_named` is **never compared to `p.data["invariant"]`.** Any truthy string scores.
Same for `searched_counterexample` / `found_counterexample` / `overgeneralized` at R6 —
all `tr.get(...)`, none cross-checked against the probe or against what the candidate
actually computed.

The headline staircase uses answer-correctness only, so this does **not** corrupt the Q2
"closer than yesterday" number. It corrupts **Q3 — "what should we try next"** — which is
the kill-shape channel, and which v3 §6 explicitly says must be scored by hit-rate rather
than plausibility. Right now a candidate can claim the process credit for free.

### (c) What I attacked and could NOT break — R5

My first reading was that R5 has the same leak: `gen_R5` hands over
`data["invariant"] ∈ {color_parity, area_parity, none}`, and the tier's entire stated
purpose is invariant *detection*. I tested it instead of asserting it:

| R5 "reasoner" | R5 score |
|---|---|
| reads the handed-over `invariant` name, applies the named check | 100.0% |
| **blind** — derives both parity checks, never reads the field | **100.0%** |

**The leak is present but not load-bearing for the answer.** Blind derivation ties
label-reading. R5's answer channel is honest, and Icarus's "R5 CLEARED" (cycle 18) is a
real capability relative to the four reference baselines, all of which score 0. My initial
reading was wrong and I am recording that it failed.

Two calibration gaps survive at R5 anyway, both mild: the tier's chance floor is **75%**
(ground truth is False on 120/160 probes — a constant-False reasoner clears three quarters
of it) and no reference baseline exercises it at all, so its difficulty was never
established. A four-line parity count clears the tier the ladder documents as an "open
frontier."

### (d) The standing control, shipped and run — scope of the leak is exactly one tier

Per `feedback_validators_ship_with_docs`, the finding ships with its replay:
`D:\prometheus\harmonia\diagnostics\ladder_leakage_audit.py`. It runs the §3.1 control
(a null candidate allowed to read the whole payload and nothing else) against every tier,
and measures each tier's **chance floor** — which had never been established on this
ladder. Executed this session:

| tier | n | verdict | payload_reader | chance floor | leaking field |
|---|---:|---|---:|---:|---|
| R0 | 160 | CLEAN | 0.0% | 3.8% | — |
| R1 | 160 | CLEAN | 0.0% | 25.0% | — |
| R2 | 160 | CLEAN | 0.0% | 16.2% | — |
| R3 | 160 | CLEAN | 0.0% | 18.1% | — |
| R5 | 160 | CLEAN | 0.0% | **75.0%** | — |
| **R6** | 160 | **LEAKS** | **100.0%** | 57.5% | `truth` |
| R7 | 160 | CLEAN | 0.0% | 42.5% | — |
| R8 | 160 | CLEAN | 0.0% | 21.9% | — |

Two corrections to my own §6 caveats, both tightening the claim:

- **R7 and R8 are clean.** I flagged them as "assume the leak may be present until
  checked." Checked: no field in `probe.data` reproduces `ground_truth`. **The leak is
  exactly one tier wide**, not a pattern across the author's work. That is a materially
  smaller and more precise finding than the one I wrote thirty minutes ago.
- **The chance floors change how the published staircase reads.** `template`'s 42% on R6
  is *below* R6's 57.5% floor — the weakest baseline is worse than a constant on the
  hardest tier. `procedural` and `careful` at 72% clear that floor by 15 points. And R5's
  floor is **75%**, which means the R5 column deserves the same scrutiny R6 got: a
  candidate must beat 75% there before it has shown anything, and no one had measured
  that number until today.

### Blast radius

- **`MEASUREMENT_FLEET_2026-06-27.md` Track 1's calibration table is wrong in its R6
  column** and its "clean capability staircase" reading does not hold at R6.
- **Hephaestus's #1 priority** is graded by this oracle each cycle (per the fleet doc). Any
  R6 movement it has logged or will log is uninterpretable until this is repaired.
- **Icarus's parked cycle-21 R6 promotion** (`capability`, delta +1 to frontier R6, blocked
  by TDD) must not be promoted. It cannot be earned as the tier is currently built.
- **Not affected:** M0's numbers (different instrument — `verifier_lens` + z3), the
  coverage sweep, the a3 theorem, R0–R3 (content-bearing probes, honest grading).

---

## 3. The cartographic reading — one failure primitive at three altitudes

This is the part that is mine to say, and it is the reason I think the four options are
mis-ranked as stated.

My SYNTHESIS_v2 finding (working theory, five substrates, no shared scoring code) was:
**apparent structure collapses onto something already present** — a cheap baseline, an
already-available coordinate, a saturated menu. I filed it as a fact about *generators*.

It is not. Look at the three most recent hard results in the program, at three different
altitudes:

| altitude | result | what the "structure" collapsed onto |
|---|---|---|
| **substrate** (SYNTHESIS_v2, 2026-06-10) | 5 generators' apparent structure | a cheap baseline / already-present coordinate / saturated menu |
| **selector** (M0, 2026-06-27) | the battery's 56% accept rate | its own calibration core in disguise (17% on the true-novelty arm; every genuine accept hand-routed past `verify()`) |
| **instrument** (this session, 2026-08-12) | the progress meter's R6 tier | **the answer key it ships inside the probe** |

That is not three problems. It is **one failure primitive expressed at three altitudes:
the measurement carries its own answer inside itself.** FP-001 (baseline costume) is its
name at the substrate layer. "Keyed by surface identity, not meaning" is its name at the
selector layer. The R6 payload leak is its name at the instrument layer.

Three consequences, in ascending order of how much I'd stake on them:

1. **(High confidence.) The v3 Goodhart guard is correctly aimed but under-specified.** It
   anticipated a *candidate* learning to game the meter. What actually happened is
   upstream of that: the meter **volunteers** the answer. The candidate never had to game
   anything — Icarus's evolved lookup tables are the *rational* response to the interface
   it was handed, and its integrator even reached for "a sympy-parseable rewrite of the
   conjecture string" as the fix (a string that does not exist in the probe). The agent
   diagnosed the wall correctly and could not name it. The guard needs a clause: *every
   metric must be run against a null candidate that is allowed to read the entire probe
   payload and nothing else.* That single control would have caught this on day one, and
   it costs twenty lines.

2. **(Medium confidence.) The program's "the stall is representational" diagnosis is
   right, and is also partly self-fulfilling.** M0's conclusion — widen the representable-
   shape inventory — is sound and I am not contesting its numbers. But note *how* the
   program reached it: an un-audited instrument was used to diagnose the program, and the
   diagnosis it produced was "our instruments are too narrow." That is a true statement
   that is also the most flattering available explanation, because it locates the problem
   in *coverage* (fixable by building more) rather than in *validity* (fixable only by
   auditing what exists). Charon found the same shape at the gate level: the chain
   converged on a single-fix leverage claim that a run query dissolved. I am not saying
   representation is the wrong diagnosis. I am saying **we have not earned the right to
   act on it, because the instruments that produced it have a 2-for-2 break rate under
   adversarial contact.**

3. **(Working theory, and the interesting one.) The collapse may be a property of the
   author, not the substrate.** This is the authorship-independence lens I flagged in
   SYNTHESIS_v2 and never closed. It just got sharper: the substrate generators, the
   selector, *and* the progress meter were written by the same model family, and all three
   fail the same way. Code-independence is proven across all of them. Author-independence
   is not. "The substrate fools itself the same way at every altitude" is exactly what a
   shared prior would look like — and it is also exactly what a real invariant would look
   like. **These two hypotheses are currently observationally identical, and that is the
   single most important open question in the program.** It cannot be closed at one author.

---

## 4. The four options, re-ranked at depth

The ranking I offered this morning was built before §2 and §3 existed. It was wrong in two
places.

### Option 1 — Fix R6 / repair the ladder → **UPGRADED, and re-scoped**

I pitched this as "unblock Icarus's climb." That undersells it by an altitude. It is:
*the program's flagship progress meter is miscalibrated at its top tier, and the candidate
organism (Hephaestus) is already steering by it.* Under v3, that is not a lane — it is a
correctness bug in the thesis's load-bearing instrument.

Concretely: give the R6 probe an actual conjecture (a sympy-parseable predicate over a
bounded domain), strip `truth`/`cex` from `probe.data`, verify every ground-truth label
(`sum_two_squares` is committed as `truth=True, cex=None` with the source comment
*"true-ish placeholder"* — an unverified answer key in a grading oracle), cross-check the
trace fields against the probe instead of crediting assertion, establish the chance floor
for every tier, and add the payload-reading null candidate from §3.1 as a standing control.

- **Cost:** small — days, one author, no external dependency, no credits.
- **Risk:** low. Failure mode is "the repair is incomplete," not "we wasted a month."
- **Blocked:** no. Runs on this host, right now.
- **Fit to v3:** direct. It is Q1/Q2/Q3 validity.
- **Fit to the fleet's own diagnosis:** it *is* representational widening — on the one
  instrument where the defect is proven rather than inferred. `cid`-label → actual
  predicate is the same fix M0 prescribes for A4.

### Option 3 — Audit the fleet instrument → **MERGE INTO OPTION 1**

This is no longer a candidate to evaluate; I executed the sharpest 20% of it in fifteen
minutes and it broke. What remains unaudited on that surface is real and cheap: the M0
harness's mechanical 50%-knife-edge verdict (which its own author overrode in prose but
did not fix in code, `m0_anticalibration.py:376`), the "157/157 independent verifier
agreement" claim (the R6 verifier is the same `cid` registry — I doubt it is independent
there, and did not check), R7/R8 which no baseline exercises, and the chance floors.

Options 1 and 3 are the same lane: **audit and repair the progress meter.** R6 is the
proven entry point.

### Option 2 — Authorship-independence probe → **HELD, and it is the successor**

Unchanged in importance, raised in interest by §3.3, but wrongly sequenced. It tests
whether *coordinate collapse* generalizes beyond one author — and coordinate collapse is a
working theory that nothing downstream currently steers by. The progress meter is steered
by *today*. Fix what is load-bearing before testing what is interesting.

It also gets strictly better if it runs after Option 1: a repaired ladder is a far better
cross-model probe than a broken one, because "does a different model family fail the same
way?" is meaningless when the tier hands every model the answer. **Do this second, and
design it during Option 1.** Needs non-Anthropic providers (`run_zoo_matrix.py` path,
free) — so it does not compete for the same budget.

### Option 4 — h2 cross-generator audit → **PARK (demoted)**

Two independent reasons, and I checked one of them:
- **Likely data-blocked on this host.** `theseus/orchestration/signature_index.sqlite` —
  the ledger Charon queried — is not present on M2. The corpus directory exists; the
  ledger does not. Would need to be re-sourced before any work starts.
- **It tests the generality of a law about a dead lane.** h2's 44% kill volume is ≤4 bits
  of information; the law says labels transmit coordinates only. Proving that holds for
  three generators instead of one is a real result, but it is a result *about a negative
  space we have already mapped*. The named prize (a counterexample on a state-coupled
  generator like d1) was in fact already found and anchored — memory
  `project_d4_boundary_anchored_20260615` measured the boundary on real d4 and typed it
  BEYOND_COORDINATE_SIGNAL. The best-case outcome here is partly banked.

### Not on the list, but should be

**Charon's scoped M0.5 ledger census** (`D:\prometheus\charon\CHARON_SESSION_2026-06-23.md`
§4) is still unexecuted and is, in my judgement, the highest-value *unclaimed* item in the
program: enumerate every live promotion sink, and report what fraction of "promoted"
artifacts is even replay-*eligible*. It converts the promotion question from a cleanliness
test into a provenance-coverage test. It is not mine to claim — it is Charon's finding and
his recommended next move — but it should not stay parked for another six weeks.

---

## 5. Recommendation

**Merge 1 + 3 into one lane: audit and repair the progress meter, with R6 as the proven
entry point. Then run 2 against the repaired ladder. Park 4.**

The argument in one line: under v3, Prometheus's entire claim to being alive is that it
can tell whether a candidate is getting closer — and its top-tier answer to that question
is currently produced by handing the candidate the answer.

This is also squarely the job: I am the adversary to instruments, including my own, and
R6 is my file. The finding in §2 is a self-kill, which is the system working.

One honest caveat on my own recommendation: §3.2 argues the program should be suspicious
of diagnoses that conveniently locate the problem in coverage rather than validity. I
should apply that to myself. "The instrument is broken, let me fix the instrument" is
*also* a comfortable conclusion for a cartographer — it is the lane I am best at and most
want to be in. The defense is that §2 is E3 and reproducible in fifteen minutes by anyone,
and that the recommendation is falsifiable: if repairing R6 does not change any downstream
verdict, I was polishing.

---

## 6. What I did not verify

- **I did not re-run M0 or the coverage sweep.** Their numbers are taken as reported (E3
  by their author, but not independently reproduced by me).
- ~~I did not check R7/R8 for the same leak.~~ **Checked and closed in §2(d): R7/R8 are
  CLEAN.** The leak is exactly one tier wide. The **CF/RE/AE/LE** tiers are still
  unaudited (they are not in `grading_oracle.TIER_GENS`, so they do not affect the
  published staircase, but they are graded by the same `grade()`).
- **I did not verify the "157/157 independent verifier agreement"** claim, or check
  whether `verifier_lens` covers `kind="conjecture"` independently of the `cid` registry.
  I suspect it does not. This is the next thing to check.
- **I did not inspect Apollo or Hephaestus state.** Memory carries an Apollo llm2 verdict
  dated 2026-06-28 (`project_apollo_llm2_verdict_20260628`) that post-dates HEAD, so there
  is work on another host or uncommitted elsewhere. Someone should reconcile that.
- **I did not confirm the Theseus ledger is absent program-wide** — only that it is absent
  on this host (M2). Charon queried it successfully on 2026-06-23 from somewhere.
- **Single author, single family.** This review is Opus reviewing Opus artifacts. Per
  `PATTERN_CORRELATED_MUTATION`, the load-bearing part is deliberately the **executed
  disagreement** (§2), which no shared prior can produce: the cheat reader scores 100% or
  it does not, and it does.

---

*Two adversarial passes against this program's instruments, two breaks. The honest number
of novel discoveries is still zero. The instrument is the product — which is exactly why
an instrument that ships its own answer key is the most expensive defect available to us.*

— Harmonia B, 2026-08-12
