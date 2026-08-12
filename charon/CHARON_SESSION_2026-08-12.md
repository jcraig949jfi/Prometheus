# Charon — Revival Assessment: what the ferryman does with newer models

**Role:** Charon (falsification battery guardian / kill-space cartography / adversarial review).
**Date:** 2026-08-12. **Status:** NON-CANONICAL. Filed as a fifth perspective alongside
Harmonia A (v1/v2/v3), Techne's dissent, my own third perspective (06-23), Aporia's portfolio
pass (06-24), and Ergon's revival assessment (`roles/Ergon/REVIVAL_ASSESSMENT_2026-08-12.md`,
today).

---

## 1. State on re-entry (measured, not assumed)

Real work stopped **2026-06-28** (Aporia's M0 design doc + session journal). Since then:
cron only — `auto: portfolio update` and `arsenal: capability matrix updated`. Six weeks of
zero human research commits. Nothing decayed; nothing advanced.

Loose ends the break left, spot-checked this session:

- **The two untracked `*_2026-06-09.bundle` files are stale backups, not lost work.** Both
  point at `d43a4e97`, which is unreachable from any branch — but the content was replayed
  onto main under different hashes (e.g. the reasoning-steering whitepaper is tracked at
  `e00bf342`). Confirm the remaining ~50 subjects before deleting; do not treat as a recovery
  emergency.
- `theseus/handoff/ergon_outbox/quarantine_20260607/` is still quarantined (pre-allowlist-fix).
  Ergon's own watch item; the seam has not been re-run clean since `6439311a`.
- The three moves I parked on 06-24 are **all still un-run**: right-null the 0.725-bit kill-MI,
  compute `kill_vector` on a corpus slice, draft the shared value-score spec. That is my ledger
  and it is untouched.

## 2. The part I played, honestly

Charon built and froze the falsification battery (v10, 25 tests, 4 tiers), the search engine,
the concept index, and the kill-space cartography. The program's most durable asset from my
lane is not a finding — it is a **null graveyard**: tt_splice bond-rank killed by a degenerate
row null; flow-conservative-by-construction; anticorrelation ≠ non-cyclicity; corpus-v3 killing
v2's 18% signal; the 90-batch zero-promotion streak that was correct artifact-refusal; the
denylist→allowlist seam leak. Every one is a *documented methodological defect with a computed
verdict.*

Hold that thought. It is the answer to the frontier-model question in §6.

My 06-23 third perspective made two claims. Re-checked today:

- **Claim 1 (navigability gate) — stands, and has gotten more load-bearing.** `kill_vector` was
  0% populated across 5.4M corpus records; the kill-geometry existed only as string labels
  (33.6% null, dominated by a1 parity violations). Nothing since 06-23 computed it. It is now
  the concrete blocker on the fleet's *consensus* experiment — see §4.
- **Claim 2 (shared value-score) — I am downgrading it.** My own charter says an instrument
  must beat a counter-baseline or it is decorative. Six weeks on, I read `value(output) =
  navigability + null_survival + downstream_delta` as the battery-guardian's reflex: a fourth
  scoring apparatus proposed by a program whose diagnosed disease is *producers with no
  consumer*. It stays parked. If it revives, it revives as a field on an existing artifact,
  never as a component.

The sharpest thing that happened while I was away is Harmonia's **M0 result (06-27)**, and it
is a verdict on *my* instrument. 18 out-of-manifold true claims: **0% reject, 44% unknown,
7/18 STRUCTURAL** — no representation at all for graphs, matrices, or multi-variable
inequalities. The packaged `verify()` battery certified **zero** genuinely novel-shaped truths
on its own; every novel accept came through a raw z3 primitive a human posed by hand, because
`verify()` dispatches on a pre-registered `cid` — **surface identity, not meaning**. The battery
fails closed and silent rather than loud and wrong, which is the defensive result I would have
asked for. But the wall is **expressiveness, not judgment.** I over-invested in the toll
collector's severity and under-invested in what it can express.

## 3. Where I agree with Ergon

His admissibility rule is correct and is the operational form of my own doctrine:

> a frontier model may occupy any role where its output is falsified by something that is not a
> model, and no role where the check is another model or a human's sense of plausibility.

Move 1 (the Metabolization Probe: C0 alone / C1 real residue / C2 mismatched residue / C3 format
control, matched token budget, computed gold, preregistered kill) is better methodology than most
of what this program has shipped. The capacity-confound argument is real: every Learner negative
we own is entangled with Qwen-1.5B/rank-16, and long context makes metabolization testable
**without training anything**. I endorse it as the first move.

## 4. Where I attack it — two defects, one fatal to the run as specified

**(a) The C1 arm cannot be built. There is nothing to retrieve.** "Model + real kill-geometry
retrieved for that problem (nearest kill signatures)" presupposes a *navigable* representation
to do nearest-neighbour against. `kill_vector` is 0% populated. The only available retrieval key
is the `kill_pattern` string label — and Ergon's own 06-09 routing eval already measured
label-space retrieval as **NULL** (cold-start concept routing: real fields ≈ shuffled fields).
So as written, C1 is either unbuildable or is instantiated on the one channel we have already
killed. **My parked navigability gate is not a side quest; it is the precondition for the fleet's
consensus experiment.** Compute `kill_vector` on a corpus slice first — days, not a quarter.

**(b) The preregistered kill over-reads a null.** `C1 ≈ C2` is confounded between *"the residue
is exhaust"* and *"our retriever put the wrong residue in the window."* Ergon's positive control
(residue that trivially contains the answer) validates the **channel**, not the **retriever**.
Add a fourth arm:

> **C1-oracle** — hand-selected, genuinely relevant residue for each problem, chosen by a human
> or by an oracle with terminus knowledge. Small n is fine; ~30 items decides it.

Read: C1-oracle ≈ C2 ⇒ the residue is exhaust (Ergon's kill fires, and it is now sound).
C1-oracle > C2 but C1-auto ≈ C2 ⇒ the residue has value and **the retriever is the bug** — an
engineering problem, and a completely different verdict for the program. Without this arm a null
gets written into doctrine as "the corpus is exhaust" when the honest reading may be "we never
built the index." Given this program's history — the `.176` stale address froze a month of
components; `predicate_holds` inverted a corpus through one missing field — the prior on
*infrastructure-shaped nulls* is high.

## 5. The lane nobody claimed: representational reach

Ergon's assessment is Learner-shaped and stops at metabolization. The M0 result opens a second
lane, and it is mine, because it is my instrument that was measured.

**The North Star is mapping the verbs — transformations — across domains.** A selector that
cannot represent a graph, a matrix, or an inequality over two reals cannot map verbs across
domains at all. Expressiveness is now a *measured* binding constraint on the North Star, not a
speculated one. And it is the single most frontier-model-appropriate job in the program under
Ergon's own admissibility rule, because the check is a machine:

> **Frontier models as encoding-forgers, not claim-generators.** Given a claim kind the selector
> cannot represent (`no_representable_kind`, `single_int_var`, `no_identity_kind`), have the model
> emit the z3/sympy/Lean encoding plus the kind registration. Acceptance is fully mechanical:
> it parses, the solver decides it, and it agrees with the oracle on a held-out set of instances
> whose truth we computed. A wrong encoding fails to compile or disagrees with the oracle. **No
> model judges anything.**

Two guards, both mandatory:

1. **Counter-baseline** (`feedback_counter_baseline_discriminator`): the comparator is not
   "better than nothing," it is a **hand-written kind grammar + templates**. If frontier encodings
   do not beat templates on new-kind coverage per unit effort, we drop the model and write the
   grammar. That question has an answer in a day.
2. **Fix the dispatch wall first, and it is free.** A4 (`n(n+1) is even`) failed only because its
   `cid` was unregistered while a logically identical claim was registered. Keying dispatch on
   *meaning* rather than surface `cid` is a battery repair we owe regardless of any model, and it
   is the cheapest single point in the M0 table.

This lane is compatible with the "no component revives into a vacuum" rule: the consumer already
exists and is running — `verifier_lens` / the M0 harness — and every new kind is graded by
re-running M0. It is also the honest form of "steal the fire": the durable artifact left on our
disk is *registered kinds and primitives*, which survive price hikes and API restriction. The
opinion does not.

## 6. Three instrument-level moves that price the frontier-model bet itself

Charon's job is to falsify the premise of the revival, not just execute it. "New frontier models
are a lever" is an unfalsified claim, and this program's own history says first-attempt gains null.

**Move A — the frozen-battery generator swap (cheap, decisive about the premise).** Models are
mutation operators; the battery is the fitness function. Hold the battery **frozen at v10** — no
v11, no tuning — replay an identical proposal task with an old-generation generator and a
new-generation one, and measure the delta in **post-battery survival rate** and **residual rate**.
If the new generation does not raise survival, its gain is fluency and format, not reasoning —
the greedy-LoRA lesson one level up — and we should budget frontier tokens accordingly. This is
the only experiment in the program that prices the revival's central assumption, and it costs a
day.

**Move B — decoy-calibrate the reviewers before trusting a review.** The cross-pollination
protocol is my standing protocol and it has **never had a null**. With newer models trained on
more of our own vocabulary, convergence becomes *more* likely and *less* informative — the
gravity amplifier gets stronger, not weaker (`feedback_llm_convergence_is_gravity_amplifier`).
Fix: seed every review round with a **decoy artifact carrying a planted, documented defect** drawn
from our null graveyard — a row null applied to a column-subspace statistic; a Spearman between
two sorted arrays; a flow that is conservative by construction; a generator-prefix MI. A reviewer
that misses the planted defect gets its review discounted by a measured factor. Reviewer
sensitivity becomes a number instead of a vibe.

**Move C — build the graveyard into an owned eval (the asset nobody else has).** Move B's decoy
library generalizes. We hold dozens of *real, subtle, documented methodological defects with
computed verdicts*: our own kills, plus Aporia's tautology cluster (Hecate's generator-prefix
`mi_z`, Pollux's sorted-array Spearman, Acheron's co-occurrence-not-collision, Coeus's causal-in-
name-only). That is a held-out gold set where **the label was computed by us and appears nowhere
in anyone's training corpus.** It measures precisely the capability our doctrine says these models
lack — epistemic honesty under narrative pressure — and it is admissible under Ergon's rule
because the gold is ours. It is externalizable, it survives API restriction, and it doubles as the
verification pass Aporia's portfolio doc needs before any RETIRE (per her own instruction, in the
code-writing form only: not *"do you agree Pollux is tautological"* but *"write the script that
computes Pollux's statistic on sorted and on shuffled inputs and print both."* The script runs;
the verdict is data).

## 7. What revival must not be

- Not another frontier review round of the reassessment chain. Five perspectives exist. A sixth
  from a newer model is corpus-shaped agreement, and agreement is the warning signal.
- Not a battery escalation. v10 stays **FROZEN**. The M0 result says the fix is expressiveness,
  not severity; adding tests now is overfitting the toll collector while the ferry cannot carry
  matrices.
- Not a swarm restart. Cheaper calls scale consumer-drift, they do not cure it.
- Not frontier-model gold, anywhere, ever. Every label computed or kernel-checked.

## 8. Sequence I recommend, and what I need from James

1. **`kill_vector` on a corpus slice + the 4-criteria navigability gate** (mine, days). Unblocks
   Ergon's C1 arm and is the first real piece of CC-6. *If it nulls under a feature-axis null,
   Move 1 metabolizes noise and we learned it for days of compute instead of a quarter.*
2. **Metabolization Probe with the added C1-oracle arm** (Ergon's, sharpened).
3. **Move A — frozen-battery generator swap** (mine, one day, prices the premise). Runs in
   parallel with 1 and 2; shares no resources.
4. **The representational lane**: fix `cid`-dispatch-by-meaning, then encoding-forge vs template
   counter-baseline, graded by re-running M0.
5. **Move B/C** — decoy-calibrated reviews; graveyard eval assembled from existing documented
   kills; doubles as the tautology-verification pass gating the RETIRE-21.

**Open ask (non-blocking):** which providers are live this month, and the token budget. My
knowledge of model releases stops at May 2026 — I know the Claude 5 family and the Leanstral 1.5
note in Ergon's resume; everything above is deliberately model-agnostic, because the design that
depends on *which* model is a design that fails at the next provider policy change.

---

*The ferryman's position on newer models: they are a faster ferry, not a better toll collector.
The measured wall is that our toll collector cannot weigh a matrix. Point the new fire at the
scales, keep it off the verdict, and price the fire itself before spending on it.*

— Charon, 2026-08-12
