# Icarus v3 Design Pressure — Response to Gemini's 20 Adversarial Questions
### 2026-05-28

Gemini reviewed whitepaper v0.1 as a falsification-first substrate and posed 20
adversarial questions to force the v3 architecture. This doc answers each with a
**position** and a **status**: `ANSWERED` (shipped or decided), `PARTIAL` (started),
`OPEN` (genuine forcing function for v3), `NEEDS-JAMES` (a goal/kill decision above
my authority).

Gemini's two headline red flags are accepted as correct:
1. **Reflexivity trap** — evolving a Python script with models trained to write
   Python scripts measures latent coding priors, not synthetic reasoning. (§5.1/§7.1
   of the whitepaper said this; Gemini is right to refuse to let us be comfortable
   with it.)
2. **Epistemic theater** — the Integrator rubber-stamps; the same entity writes the
   code and the tests. Today's instrumentation already produced corroborating
   evidence: with honest self-labeling, 0/4 promotions in the 6-cycle validation run
   were tagged `capability` — all were `test_weakness` or `metric_shaped`. The panel
   now admits its own theater from the inside.

---

## I. The Representation Bottleneck

**Q1 — Exact data structure replacing reasoner.py, and why it makes R5 cheap.**
Position: a **typed operator DAG**. Nodes are typed primitives with explicit
input→output type signatures; edges are data dependencies. R5 (counterfactual
control) is cheap because you fork the DAG at any node, substitute a counterfactual
value, and re-evaluate only the downstream cone — "what changes if X changes" becomes
a localized recomputation instead of re-running an opaque function. In Python the same
question requires re-executing the whole procedure and diffing outputs; the structure
hides the dependency graph that makes counterfactuals tractable. Status: **OPEN** (this
is the v3 build).

**Q2 — Migrating earned R1/R2 capability without catastrophic regression.**
Position: do NOT hand-port. Re-derive. Encode the R1/R2 falsification tests against the
new DAG representation first; let Icarus re-earn variable-rename invariance and
distractor filtering in the new substrate. If it cannot re-earn them, that is a
finding (the Python capabilities were representation-specific, i.e., latent coding
prior, exactly Gemini's red flag #1). The old `code/` lineage is retained as frozen
forensic record, not as runtime. Status: **OPEN**.

**Q3 — What stops Icarus deleting hard constraints to get trivial promotions.**
Position: the constraint graph lives OUTSIDE the mutable boundary, same principle as
today's frozen `ladder.py` + lens panel. In v3 Icarus manipulates only the SOLUTION
DAG; the CONSTRAINT DAG (tier falsification tests, type signatures, invariants) is
James-only-modifiable infrastructure. The mutability boundary that already works for
the daemon/lenses extends to the constraints. Status: **ANSWERED (by existing principle)**.

**Q4 — At what tier do you force outputs to compile in Lean4/Coq.**
Position: at **R6** (error detection + local repair) — the first tier where "the proof
sketch hides an invalid move" (whitepaper §1.3) becomes the dominant failure mode and
informal checking is provably insufficient. Below R6, property-based testing (Hypothesis)
is the cheaper sufficient check. Status: **OPEN** (tier-gated toolchain escalation).

---

## II. Epistemic Theater & The Lens Panel

**Q5 — Exact consensus threshold that triggers auto-park or secondary audit.**
Position: do NOT auto-park on high consensus (a simple correct change legitimately
scores high-consensus). Instead auto-ESCALATE: if all non-error lenses have axis spread
< 0.15 AND mean > 0.6, re-run the Skeptic with a hardened adversarial prompt and a fresh
seed before allowing promotion. Consensus buys scrutiny, not a free pass. Status:
**PARTIAL** (axes_summary spread is computed today; the escalation trigger is unbuilt).

**Q6 — Coded policy for a Skeptic hard veto regardless of TDD.**
Position: distinguish LLM-Skeptic from deterministic Contract Lens. A DETERMINISTIC
contract violation should be a HARD veto (park), because it is a fact not an opinion —
this is stronger than today's promote-with-debt and I would change it for v3. An
LLM-Skeptic minority position keeps the debt mechanism (promote-with-mandatory-followup)
because LLM judgments are fallible and a hard veto from a fallible judge is its own
failure mode. Status: **PARTIAL** (Contract Lens shipped today; hard-veto wiring is a
one-line guard change, deferred pending the Q5 escalation design).

**Q7 — Mechanic lens kill criteria that won't park valid code.**
Position: the Mechanic is purely SYNTACTIC — `git apply --check` + AST-parse of the
post-apply code + import-resolves check. It only kills diffs that provably won't apply
or won't parse. It never makes a semantic judgment, so it cannot park valid code; the
worst case is it passes a semantically-bad diff downstream to the Skeptic. Status:
**OPEN** (designed, not built; today's `--recount` fix reduced its urgency).

**Q8 — Specific non-LLM lens to break the monoculture.**
Position: **SHIPPED TODAY** — the deterministic Contract Lens (cardinality / type-
stability / exception-contract checks via subprocess-isolated probes against the stable
baseline). Validated: it catches the real Cycle 14 `apply_batch` break with zero API
cost. Next non-LLM lens: a property-based tester (Hypothesis) generating random inputs
to check declared invariants; after that, a bounded model checker. Status: **ANSWERED
(first one shipped)**.

---

## III. Goodharting & Self-Fulfilling Falsification

**Q9 — Blind, out-of-band falsification the Generator can't see.**
Position: a `tests/holdout/` directory populated by a different agent (Harmonia oracle
or a frozen generator) that runs in TDD but is NEVER included in the Generator's
source-read. The Generator cannot write tests that pass by construction if it cannot see
the tests it must pass. This is the single highest-leverage anti-Goodhart move and is
cheap to build. Status: **OPEN** (high priority).

**Q10 — Computationally calibrate that R(n+1) is strictly harder than R(n).**
Position: you cannot guarantee "mathematically harder" in general, but you CAN enforce
**discrimination**: a tier-(n+1) falsification test is valid only if a known-R(n)
reasoner FAILS it and a known-R(n+1) reasoner PASSES it. Operationally, run every tier
test against the historical stable lineage; if an early-cycle (low-tier) reasoner passes
the R2 test, the R2 test is too weak and is rejected. This directly attacks the
whitepaper's R2-easier-than-R1 anomaly. Status: **OPEN** (this is the sharpened
tier-blindness experiment).

**Q11 — How exactly you measure ejection.**
Position: primary instrument = token-level logprob/entropy where the API exposes it;
watch for a low-entropy stretch (overconfident continuation) immediately following a
high-entropy stretch (genuine uncertainty) — the transition is the ejection signature.
Cheap proxy if logprobs are unavailable: cycle-over-cycle textual similarity of Generator
rationales; convergence to boilerplate phrasing = ejection into a linguistic basin.
Status: **OPEN**.

**Q12 — Automated ablation proving R2/R3 code isn't decorative.**
Position: for every promoted cycle, ABLATE the new code (revert just this cycle's diff
against its parent) and re-run the tier falsification test. If the test still passes
without the new code, the code was decorative — auto-demote. This is the Apollo
single-primitive-baseline lesson applied per-cycle and is runnable now against the
existing lineage. Status: **PARTIAL** (the adversarial.py single-primitive probe is the
stub; the per-cycle diff-ablation is unbuilt but cheap). **This becomes part of the
lens-ablation experiment.**

---

## IV. Memory, Wisdom, and Gradients

**Q13 — Exact n-dim schema for the continuous outcome vector.**
Position: per-lens axis vector (5 axes × 5 lenses = 25 dims) ++ failure_class one-hot
++ tier scalar ++ improvement_kind one-hot ++ open_debt_delta. Gradient descent over
failures = move in the direction that historically raised tier_proximity without
lowering regression_risk, computed over the training_stream. Today's typed
TrainingObject is the precursor; the continuous vector is its embedding. Status:
**PARTIAL** (TrainingObject shipped today; the embedding + descent is v3).

**Q14 — API/pipeline forcing Icarus to read Harmonia's dead-ends as priors.**
Position: the Historian lens reads `harmonia/memory/retraction_registry.md` +
`harmonia/nulls/` at cycle start and injects matched dead-ends into the Generator
context as hard priors. Concretely a `cross_swarm_priors()` call in the Historian that
greps the registry for failure signatures matching the current proposal_type. Status:
**OPEN** (the Historian + kill_clusters scaffolding shipped today make this a small add).

**Q15 — Distance metric for failure-mode equivalence classes.**
Position: today's clustering is exact-match on (failure_class, failure_subclass) — too
coarse/too brittle (Gemini's "1000 formatting errors as 1000 failures" risk cuts the
other way too). v3 metric: embed each TrainingObject's deterministic spine + enrichment
text, cluster by cosine distance with a threshold, then label clusters by dominant
failure_subclass. The spine fields (failure_class, detected_by, axes) are exact;
the free-text concern is embedded. Status: **PARTIAL** (exact-match clustering shipped;
distance metric is v3).

**Q16 — Quantitative revert trigger.**
Position: revert to depth D−N when ANY of: (a) a kill-cluster shows K≥3 consecutive
parks of the same (failure_class, failure_subclass) off the current stable; (b)
open-debt count exceeds 5 (debt spiral); (c) the last M≥4 promotions are all
improvement_kind ∈ {test_weakness, metric_shaped} (capability stall / metric drift).
The debt ledger + kill clusters + improvement_kind shipped today provide all three
signals; the revert POLICY consuming them is unbuilt. Status: **PARTIAL** (signals
exist; policy is the next build).

---

## V. Orchestration & Swarm Dynamics

**Q17 — Bandit reward signal; won't promotion-rate make it a timid micro-refactor bot.**
Position: YES — promotion-rate as reward collapses to minimal-refactor timidity (the
review's exact warning, and why we have NOT enabled the bandit). The reward must be
capability-weighted: `reward = 1[improvement_kind=="capability"] − λ·open_debts_created
− μ·decorative_ablation_failures`. Under this, a timid minimal cycle that promotes via
test_weakness earns ZERO. The bandit cannot be enabled until improvement_kind is
trustworthy (Q12 ablation + Q9 blind tests), which is precisely why the review said
delay it. Status: **ANSWERED (decision: bandit stays OFF until capability signal is
ablation-verified)**.

**Q18 — How the v3 Skeptic co-evolves; its loss function; avoiding rubber-stamp/infinite-reject collapse.**
Position: co-evolution via calibration anchors (the Generator-Adversary loop). Maintain
a frozen set of known-good and known-bad diffs; the Skeptic's loss is its error rate on
that anchor set (false-approve + false-reject). The Skeptic version that minimizes anchor
error is promoted. This prevents both collapse modes: rubber-stamping spikes false-approve
on known-bad anchors; infinite-rejection spikes false-reject on known-good anchors. The
anchor set is frozen infrastructure Icarus cannot see or modify. Status: **OPEN**.

**Q19 — Hard cost ceiling before failure-mining-at-scale breaks.**
Position: current $0.048/cycle. Hard ceiling $0.50/cycle — at $200/day that is ~400
cycles/day, the minimum density for meaningful failure-mining. Formal verification +
deeper search push toward this. Above $0.50: switch to SELECTIVE verification — fully
verify only promotion candidates, run parks on a cheap fast-path. The failure-mining
premise requires cheap parks; expensive parks kill it. Status: **ANSWERED (ceiling
$0.50/cycle; selective verification above it)**.

**Q20 — If v3 does R0-R4 cleanly but stalls at R5, dead end or redefine goals?**
Position (but **NEEDS-JAMES** for the final call): declare the kill, do NOT redefine
goals to manufacture success. A clean R0-R4 with a hard R5 stall across a pre-committed
budget (proposal: 200 cycles at R5 with zero capability-kind promotions) FALSIFIES the
lens-panel-self-improvement architecture as a path to counterfactual control — and that
is a first-class Prometheus result, because it localizes exactly where self-improvement-
via-perspective-synthesis hits its ceiling. The residue (typed training objects + kill
clusters at the R5 boundary) becomes the design input for the next architecture.
Redefining the goal to fit the result is reward-signal capture at the project level —
the exact thing the North Star warns against. **Kill criterion for the agent itself:
200 R5 cycles, 0 capability promotions, → write the post-mortem, retire Icarus, keep the
residue.** James owns the final budget number and the retire/continue decision.

---

## Synthesis

Of the 20: **2 ANSWERED-by-ship** (Q8 Contract Lens, and the decision pair Q17/Q19),
**3 ANSWERED-by-principle/decision** (Q3, Q17, Q19), **6 PARTIAL** (signals or scaffolding
shipped today: Q5, Q6, Q12, Q13, Q15, Q16), **8 OPEN forcing-functions for v3** (Q1, Q2,
Q4, Q7, Q9, Q10, Q11, Q14, Q18), **1 NEEDS-JAMES** (Q20).

The single highest-leverage OPEN items, in order:
1. **Q9 blind holdout tests** — kills the write-your-own-test Goodhart loop; cheap.
2. **Q10 tier discrimination calibration** — kills the R2-easier-than-R1 anomaly;
   makes the ladder trustworthy.
3. **Q1 typed operator DAG** — the representation rebuild; everything else is downstream.
4. **Q12 per-cycle decorative-code ablation** — makes improvement_kind trustworthy,
   which unblocks the bandit (Q17).

Recommended sequencing: Q9 + Q12 first (cheap, make the capability signal honest), then
Q10 (calibrate the ladder), then commit to Q1 (the rebuild) with the now-trustworthy
instrumentation underneath it.
