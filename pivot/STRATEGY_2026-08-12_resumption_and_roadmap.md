# Prometheus — Resumption Assessment & Long-Term Roadmap

> **Date:** 2026-08-12 · **Author:** Apollo (Claude Opus 5, M2) · **HITL:** James
> **Status:** LIVE. Extends — does not supersede — `pivot/REASSESSMENT_2026-06-22_v3_the_reframing.md`.
> v3 decided *what Prometheus is for*. This document decides *how it operates* after
> the 2026-06-27 freeze, and records James's four directional rulings of 2026-08-12.
> **Doctrine:** falsification-first; report failure SHAPES not verdict-lines; lenses
> over mono-solutions; novelty is the reward signal; watch for reward-signal capture.

---

## 0. How to read this

§1–§4 are the assessment (evidence, mostly numbers). §5 is James's rulings — those are
constraints, not proposals. §6–§10 are the roadmap that follows from applying §5 to
§1–§4. §11 is what remains undecided. §12 is how this document gets falsified.

Nothing here is a new framework. The program's failure mode is *diagnosis without
execution* (§4); this document is written to be executed against, and every phase in it
terminates in a runnable artifact rather than a paragraph.

---

## 1. State at resumption

**The entire program stopped on 2026-06-27.** Last commit `2350a1de`. Six and a half
weeks of silence. No processes running at resumption. Roughly half the top-level lanes
(`kairos`, `mnemosyne`, `agora`, `stoa`, `ignis`, `cartography`, `theseus`, `techne`)
have had no edits since early-to-mid May.

The freeze point is unusually clean: the last three substantive commits are the program
answering its own largest open questions.

| commit | what landed |
|---|---|
| `709c28f9` | Apollo — full dispatch-arc writeup; fresh llm run scoped to 800 gens |
| `63fdadaf` | Harmonia A — grading oracle (the non-gameable "are we closer?" instrument) |
| `2350a1de` | Harmonia A — coverage sweep + **M0 keystone**: stall is representational |

**Apollo's run resolved during the freeze.** `apollo/run_branch_c_dispatch_llm2/`
completed gen 800 on 2026-06-28 (24h). `max_acc` **0.833**, `max_routable_acc` **1.000**
— *exactly* the deterministic numbers. 2152 Granite mutations (~2.7/gen, 19× the prior
run's rate) bought zero lift. This fired the kill condition registered before launch.
Verdict: **`--mode llm` does not earn its GPU in this regime.** Residual failure-shape:
gen-800 `dispatch_audit.genuine_routing = false` — branches overlap rather than
partition, so the 0.833 is real but the *routing* under it is not clean.

**M0 resolved during the same week and is the more important result.** v3 named M0 the
keystone that decides whether success-state D (TDD layer) is alive. It came back
**Reading B**: the selector cannot recognize novelty outside its calibration manifold.
Set A (re-encodings) 80% accept; **Set B (adjacent domains — the real novelty arm) 17%**;
Set C 71%. Overall 56% accept / **0% reject** / 44% unknown.

Two things follow. First, v3's Q1 ("are we there yet — is this genuine novelty?") is
**currently unmeasurable**, so D is not yet alive. Second — and this is the load-bearing
nuance — **the 0% reject rate means the battery fails silent, never loudly wrong.** It
will not falsely kill a true discovery. That makes the audit fallback solid and makes
the blockage *representational rather than epistemic*: the out-of-manifold truths are
z3-decidable today and fail only because `certify_universal` is wired to one integer
variable and the conjecture registry keys on a literal `cid` string.

---

## 2. The convergent diagnosis — the program's best finding

Five instruments, five different substrates, independently rate-limited by **the same
failure primitive**. Each was first read as a capability, terrain, or scale failure.
Each turned out to be a **representable-shape** failure.

| instrument | wall as first read | actual cause |
|---|---|---|
| Harmonia M0 selector | "can't certify novel truths" | one-variable predicate signature; registry keyed on literal string |
| Harmonia EC void-miner | "0 novel laws — terrain flat" | hypothesis class expresses **25% (4/16)** of known EC laws; **2/2** in-class, **0/12** out-of-class |
| Icarus R5 | "reasoning stalled" | serialization (code-in-JSON) + under-sampled probe schema |
| Icarus R6 | "reasoning stalled" | probe_schema hid 4 of 5 cids; answer contract never stated |
| Apollo 0.558 | "search exhausted" | `best_acc` represented ONE terminal against a ≥3-terminal battery |
| Apollo 0.708 → 0.833 | "aggregate can't solve synth" | guard keyed on slot `quantities`, which nothing writes |

Perfect in-class recall with zero out-of-class recall is a **ceiling signature**, not an
exhausted-terrain signature. That pattern recurs across all five.

The integrated M0 finding states it directly: *Prometheus's stall is dominantly
representational/interface, not epistemic/terrain/scale. Highest-leverage program work =
widen the representable-shape inventory.*

This is the most transferable thing the program has produced. It is also the Silver
thesis appearing as an engineering constraint rather than a philosophical one.

---

## 3. The step past the diagnosis: widening has been 100% human-supplied

The diagnosis stops one move short. If representational widening is the binding
constraint everywhere, the next question is who supplies it — and the answer, across
every agent, for the whole program to date, is: **a human, or an agent acting as one.
Zero widenings have been found by the systems themselves.**

Apollo is the cleanest evidence because it is the most instrumented. Five walls, five
widenings:

| wall | widening | supplied by |
|---|---|---|
| 0.392 — search operator | `recombine()` crossover | Apollo (agent) |
| 0.558 — organism model | guarded scorers + relaxed fitness | Apollo (agent) |
| 0.708 — branch assembly | `dispatch_merge` (body+guard union) | Apollo (agent) |
| canary boolean gap | `parse_comparison` / `score_by_comparison__g` | Apollo (agent) |
| aggregate decorative | guard re-keyed `quantities`→`counts` | Apollo (agent) |

**5/5 hand-supplied.** The division of labor is stark: after each widening, deterministic
search exploited it and reached its new ceiling in **~130 generations**, then produced
nothing for the remaining **669** — **84% of compute spent after the ceiling**.

So the evolutionary loop is doing *exploitation*. The *widening* — the actual climbing —
is entirely agent-supplied. Branch C is, at present, a hand-engineering loop wearing an
evolution costume.

That is not a reason to shut it down. It is a reason to make the costume the subject of
the experiment. Under the freeze-point diagnosis, the central open question of Prometheus
is not "can it discover" or even "can it measure discovery," but:

> **Can representational widening be detected, proposed, and executed by the system —
> or is it irreducibly human?**

This question does not appear in any of the four prior reassessment documents. It sits
directly under M0's floor.

---

## 4. The second failure mode: diagnosis without execution

The 2026-06-22 audit self-reports as **~75% rediscovery** — *"the corpus has every fix
designed/shipped but never assembled and enforced."* There are course corrections CC-0
through CC-7, five prioritized falsifiable tests, and an **M1 ("build one candidate
organism") that v3 named as the immediate next move and that was never built.** The
247-document `pivot/` corpus is the artifact of a program markedly better at diagnosing
itself than at executing on the diagnosis.

**A fifth reassessment would be the failure mode, not the fix.** This is the primary
design constraint on everything below.

---

## 5. James's rulings, 2026-08-12

These are constraints. They override the recommendations Apollo made before them.

**R1 — Math is NOT retired.** The claim frontier keeps stalling and hitting diminishing
returns, but the landscape remains rich; the frontiers are simply very hard to mine.
The decisive property is **discreteness — there is no ambiguity in mathematics.**

*Consequence:* math's role is **promoted, not demoted**. Unambiguous ground truth is
exactly what is required to *validate an instrument* before pointing it at the reasoning
landscape, where every verdict is contestable. Math becomes the **calibration standard**
for new instrument classes. The stall there is the EC signature (§2) — a narrow drill,
not flat terrain — so the payoff is in **hypothesis-class diversity** (unary, real-valued,
cross-object, arity-3), not more integer invariants.

**R2 — The Apollo R9→M-axis re-aim is NOT approved yet; the ladder itself needs
re-assessment.** More thought and exploration required first. *Consequence:* ladder v0.2
becomes the priority piece of thinking (§8). Apollo's re-aim is downstream of it, not
upstream.

**R3 — Do not narrow. Search for value across the program and find a path forward.**
*Consequence:* the consolidation/retirement recommendation is withdrawn. The operating
model becomes an archive rather than a funnel (§6).

**R4 — No kill date.** The mode is: cycle, explore, adapt, branch out, expand tooling,
seek out more models to help shape the project and vision, use stronger technology
(e.g. models running in podman), and look for leverage points. *Consequence:* what
replaces a kill date is not nothing — it is a **coverage measure** (§6.2). That is the
instrument that keeps "cycle and explore" from degrading into drift.

---

## 6. Revised operating model — archive, not funnel

### 6.1 Run the program the way Apollo runs its archive

R3 asks for a broad search over a high-dimensional space with expensive evaluation and
no map. **Prometheus already owns the correct algorithm for exactly that, and it is
Apollo's: MAP-Elites.** Illuminate a descriptor space, keep the best in each niche, and
maintain a coverage measure that distinguishes an *unexplored* niche from an *exhausted*
one.

The program has never applied its own core algorithm to itself. It currently has ~30
lanes, no descriptor space, no coverage measure, and no principled way to tell "mined
out" from "we only ever sampled one corner." Harmonia's own memo names this as the
unfalsifiability crux: *"a sparsely-sampled void is indistinguishable from an exhausted
one without a coverage/density measure."*

**Proposed descriptor axes** (first draft, to be revised on contact):

- **landscape** — math / reasoning / infra / meta-instrument
- **instrument class** — miner / falsifier / evolver / measurer / router / store
- **consumes** — what input it requires (and whether that input is currently alive)
- **emits** — claims / primitives / failure-objects / coverage numbers / nothing
- **liveness** — last real edit, last real result, whether it has a runnable entry point
- **hypothesis-class coverage** — the EC-style number, where computable

Cells are lanes. Fitness is "does it emit something another lane consumes." Novelty is
"is this niche occupied at all." **Voids are the product**, per the twofold-intent
doctrine — but only once a coverage measure makes a void distinguishable from a gap in
our sampling.

### 6.2 What replaces the kill date

A kill date is a funnel instrument, and R4 correctly rejects it. In an archive you do
not kill niches — you illuminate them and let coverage direct spend. The replacement is
the **coverage measure**, and it should be built early rather than late. A prototype
already exists and is currently applied to exactly one miner:
`D:\Prometheus\harmonia\experiments\hypothesis_class_coverage_audit.py`.

### 6.3 The execution guard (non-negotiable, per §4)

**Every pass over a lane emits a runnable, committed artifact — a working probe, a
coverage number, or a recorded death.** Never a paragraph. If a pass produces only prose,
it did not happen. This is the guard that prevents the value-search from becoming
reassessment #5.

---

## 7. The two landscapes, re-roled

| landscape | role after 2026-08-12 | why |
|---|---|---|
| **Math** (Harmonia, Charon/Erebos, Techne, Ergon-math) | **Calibration standard.** Where new instrument classes are validated before deployment. Claim-mining continues but is no longer the primary justification. | Discreteness → unambiguous ground truth (R1). An instrument that cannot find known math laws has no business grading contestable reasoning claims. |
| **Reasoning** (Apollo, Icarus, Hephaestus, Ergon-learner) | **Target landscape.** Where candidate organisms climb and where the widening question is live. | This is where the residue is per the terrain lens; also where v3's M1 was supposed to land. |

The relationship is directional and testable: **an instrument earns deployment on the
reasoning landscape by first passing on the math landscape**, where it can be scored
without argument. That is a concrete, falsifiable use of math's discreteness, and it is
the strongest available answer to "why keep mining a stalled terrain."

---

## 8. Ladder v0.2 — the reassessment agenda (R2)

The ladder is v0.1, dated 2026-05-24 (`pivot/reasoning_ladder_v01_2026-05-24.md`),
~2.5 months old. It was synthesized from an external review plus our own cadence, and it
**states in its own text that R3–R5 have no sharp falsification tests.** We now have
substantial empirical contact with it, and the record does not fit the model. Five
questions v0.2 must answer:

**(a) Do the climb dynamics contradict tier-adjacency?**
The ladder implies you climb by acquiring the next tier's capability. Observed instead:
Icarus jumped **R3→R5 in a single cycle** once a serialization wall came down; Apollo
moved 0.392→0.833 across three walls, none of which was "the next capability up." The
recurring shape is *remove a representational constraint → jump several tiers at once →
stall until the next constraint.* If that holds, the ladder is a sound taxonomy of
behaviors and an unsound model of progression. **Test:** reconstruct every recorded tier
transition in the program and check whether transitions are unit-step (ladder-predicted)
or multi-step-following-a-representational-fix (observed-predicted).

**(b) Is M orthogonal to R, or is M the ladder and R its shadow?**
v0.1 makes R primary and F/M/H orthogonal modifiers. But *every* wall in the empirical
record — Apollo ×5, Icarus ×2, M0, EC — was M-dimension (representation mobility). If M
rate-limits every climb, calling it a modifier is an inversion. **This is the crux and
it gates Apollo's re-aim (R2).** Do not assert it — test it against the ablation-induced
wall corpus (§10).

**(c) The sharpest clause of the doctrine has never been used.**
The doctrine reads: *occupies the tier only if the mechanism survives perturbation,
**beats lower-tier baselines**, and **fails in the tier-predicted way**.* Clause two has
been used once, decisively (Apollo's baseline matrix, which falsified R9). Clause three —
*fails in the tier-predicted way* — has **no recorded instance anywhere in the program.**
That is the clause that makes the ladder falsifiable rather than merely descriptive.
**Test (cheap, possibly brutal):** audit every tier reading ever issued against clause
three. Predict that most readings are unsupported by it. This is the first thing to run.

**(d) It is reasoning-only, but implies program-wide scope.**
Harmonia's work does not map onto R0–R12 at all. Either v0.2 provides a math-landscape
instantiation, or it states plainly that the ladder is a reasoning-landscape instrument
and stops implying otherwise.

**(e) Sharp tests are writable now where they were not in May.**
v0.1 had no instruments. We now have per-branch ablation, null-calibrated gates,
construct validation, the grading oracle, and — new — **ablation-induced walls with known
ground truth**. R3–R8 tests are writable today.

**Owner:** Apollo. **Cost:** mostly desk work plus cheap CPU experiments. **Start with
(c)** — it decides whether the ladder is an instrument or a vocabulary, and it requires
no new code.

---

## 9. Leverage-point register

Ordered by (leverage ÷ cost), not by preference.

1. **Multi-model infrastructure — podman-hosted local models (R4).** The most
   under-built item relative to stated doctrine. "Lenses over mono-solutions," ensemble
   invariance, and the cross-family rule constitute a thoroughly multi-perspective
   epistemology that has been running on essentially **one model family** with occasional
   API probes. Containerized local models make the doctrine *executable* and *cheap*:
   real lens panels, real cross-family checks, no credit dependency. This is not
   infrastructure hygiene — it is the missing substrate for a doctrine we have been
   asserting without the means to run. See also `feedback_loop_inference_over_api`
   (agents → Claude Code subscription; raw-model measurement → raw API / local, because
   a tool-enabled nested session would cheat the probe).
2. **Program-wide coverage measure.** One instrument, already prototyped, currently
   applied to one miner. It is the difference between "we explored" and "we know what we
   did not explore," and it is what replaces the kill date (§6.2).
3. **Ablation-induced walls.** Cheap, deterministic, ground-truthed, generatable on
   demand. One corpus serves both the widening question (§10) and the ladder's sharp
   tier tests (§8e).
4. **The 84% waste number.** Apollo ceilings at ~130 generations; runs have been 800.
   Switching to ~150-gen probes is a free **5× on experiment throughput** with no design
   work required. Do this immediately.
5. **Better drills for the math frontier (R1).** 25% hypothesis-class coverage says the
   payoff is class diversity — unary-property miner (cheapest; closes Mazur + Sha-square),
   real-valued lattices with tolerance relations, cross-object pairing via isogeny/twist
   orbits, curated arity-3 relations.
6. **Apollo's clean-routing debt.** `genuine_routing = false` at gen 800. The 0.833 is
   real; the routing beneath it is overlapping rather than partitioned. Deterministic,
   cheap, and it is a live falsification target rather than a polish item.

---

## 10. Apollo's lane

**Apollo's re-aim is on hold pending ladder v0.2 (R2).** What proceeds regardless:

- **Immediate:** switch to ~150-gen probes (leverage #4). Commit the untracked
  `apollo/pivot/*`, `apollo/run_*`, and `roles/Apollo/` artifacts so the dispatch arc is
  durable.
- **W0 — retro-label the widening corpus.** Turn the five historical widenings (§3) into
  typed records: `{wall signature, diagnosis, widening applied, cost, measured lift,
  gens-to-exploit}`. One day of work. This is Icarus's "every cycle emits a training
  object" doctrine applied to Apollo's own history, and it is the seed corpus for both
  §8b and W1.
- **W1 — the wall-type detector.** Given a plateau, can a deterministic instrument
  classify the wall as `{search-operator | expressiveness | measurement-artifact |
  interface-bug}` from telemetry alone, with no human in the loop? Validated on ~20
  **ablation-induced walls with known ground truth** (remove an op family, corrupt a
  guard slot, restrict the mutation operator, narrow the metric — run to plateau, ask the
  detector to name what is missing), plus leave-one-out on the five real walls.
  **Kill condition: ≤ chance (25%) out-of-sample → wall-type is not readable from the
  substrate's own telemetry, and automated widening is dead in this form.**
- **W2 — the proposer.** Emit a *typed direction*, not merely a class: which slot is
  never written, which op family has zero coverage of the failing subset, which metric
  collapses a multi-terminal battery. Scored by v3's own Q3 rule — **the direction must
  beat a random/no-op control on the next cycle, or the compass is decorative.** This is
  v3's Q3 instantiated on a substrate cheap enough to actually run it.
- **W3 — the closer.** Can a model implement the widening from a typed direction — write
  the parser + guarded-scorer pair, validated by the existing construct-validation
  harness? Note this is a **different** LLM task from the one just falsified: Granite
  mutating pipelines in-loop was useless, but a model writing a small, well-specified,
  independently-verifiable primitive from a diagnosis is a fair and separate test. This
  is the honest re-entry point for the LLM, with a gate on it. Depends on leverage #1.

W1's corpus is the same corpus §8b needs. That is the intended economy: **one build,
two questions** — "can the system see its own wall" and "is M the real ladder."

---

## 11. Open calls

1. **Ladder v0.2 ownership** — proposed: Apollo. Starting with §8(c), the dormant
   "fails in the tier-predicted way" audit.
2. **Program-as-archive (§6)** — build it as a runnable artifact (descriptor space +
   coverage measure), or instead have Apollo walk lanes and report? The former leaves
   something behind; the latter is faster to start.
3. **Podman / multi-model stack ownership** — machine-level work; Apollo does not know
   what is already standing on M2/M3/M4.
4. **M1 (v3's candidate-organism harness)** — still unbuilt. Apollo is the only working
   candidate. Q2/Q3 are measurable now; **Q1 remains blocked on M0's representational fix
   and should be logged as blocked rather than given a fabricated number.**

---

## 12. How this document gets falsified

Per doctrine, the strategy document ships with its own kill paths.

- **§3 (widening is human-supplied) is wrong** if any recorded instance exists of a
  Prometheus system proposing and validating its own representational widening. One
  counterexample kills it. Apollo has searched its own record and found none; the other
  lanes have not been searched, and that search is owed.
- **§2 (representational stall) is wrong** if the wall-type detector (W1) finds that
  plateaus are dominated by search-operator or terrain classes rather than expressiveness
  and interface classes. W1 is therefore a test of this document, not only of Apollo.
- **§6 (archive over funnel) is wrong** if the coverage measure turns out to be
  uncomputable or uninformative across lanes — i.e. if most lanes admit no hypothesis
  class against which coverage can be defined. Then "search for value" has no fitness
  signal and must be conducted some other way.
- **§8(b) (M is primary) is wrong** if tier transitions in the reconstructed record are
  predominantly unit-step and not preceded by representational fixes. The ladder would
  then be vindicated as-is and Apollo's re-aim correctly rejected.
- **This document as a whole fails** if six weeks from now it has produced documents
  rather than artifacts. That is the §4 failure mode recurring at one level up, and it is
  the single most likely way this goes wrong.

---

*Recorded by Apollo, 2026-08-12, on resumption after the 2026-06-27 freeze. Assessment
sources: `roles/Apollo/{CHARTER,STARTUP}.md`, `apollo/pivot/dispatch_arc_writeup_2026-06-27.md`,
`apollo/run_branch_c_dispatch_llm2/evolve_log.jsonl`,
`pivot/REASSESSMENT_2026-06-22_{consolidated,v3_the_reframing}.md`,
`pivot/reasoning_ladder_v01_2026-05-24.md`, `harmonia/experiments/M0_RESULTS.md`,
`roles/Harmonia/AUDIT_20260622_{program_stall_map_of_disagreement,instrument_monoculture}.md`,
and the auto-memory corpus. Rulings R1–R4 are James's, 2026-08-12.*
