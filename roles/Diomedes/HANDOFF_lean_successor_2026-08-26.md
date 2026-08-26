# Handoff — the Lean-native successor to the coordinate-adequacy thread

**From:** Diomedes, at thread close. **Filed:** 2026-08-26. **Deliberately narrow.**

This transfers **a problem and its discriminating tests**, not an architecture programme. It contains
the unresolved question, the observation boundary, what counts as a kill, and the minimum artifacts
that must exist before a first measurement. It does **not** describe how to build a Lean research
system, and anything here that starts to read that way should be cut by whoever picks it up.

---

## 1. The unresolved question, stated precisely

Cycles 001–005 established **candidate-conditioned predictability of a constructed label**. They did
not establish, and could not have established, this:

> **Does `Z(x,a)` predict future attainable verified progress — or is it a sensor for the variables
> that define the current oracle?**

The corpus could not separate those. A non-navigational proxy that reconstructs the withheld variable
and applies the benchmark's own arithmetic reproduced performance equivalent to ~45% of the local
above-chance span, and nonlinearity added +0.0096, so the route was not model-limited.

The successor's entire reason to exist is that **its dependent variable is a property of future
reachability through an enumerated transition graph, rather than a withheld scalar attribute of the
candidate.** That is the upgrade. "Lean is more real mathematics" is not, and must not be offered as
one.

**Oracle:** `Q*_H(x,a)` = exact shortest verified completion distance from `x' = step(x,a)` within
horizon `H`, or failure. **Explicitly rejected**, each recreating the measured defect: tactic
executed · goal-count delta · expression-size delta · fewer subgoals · matches a human proof.

## 2. The admissible observation boundary — the single most transferable constraint

**The oracle is computed from the future. Every ranking arm must be computed from the present.**

A ranking arm may observe: the proof state `x`, the candidate action `a`, and the successor `x'`
where the tier under test permits it. A ranking arm may **not** observe anything downstream of the
oracle — not `Q*_H`, not distance-to-proof, not the successful-continuation count, not any statistic
of the reachable subgraph below `x'`. This is enforced in code, not by convention; cycles 001–005
enforced their analogue (`no arm except the oracle reads the candidate's tested invariant`) and it
still admitted a proxy route, which is why §4's audit is mandatory rather than optional.

**One legitimate exception, and it is a diagnostic, not an arm.** The proxy-reconstruction audit *may*
use the oracle as a regression **target**, because there the question is no longer "can an admissible
system rank" but "do the admissible features indirectly encode what was withheld." Firewall:
**cross-fit by object identity — no item's own oracle value may train its own prediction.** One proof
state recurs across many items.

## 3. What counts as a kill, and what a negative does and does not mean

**Replay the decomposition ladder, pre-registered before measurement:**
chance · state-independent action prior · `Z(x)` · `Z(x,a)` · `Z(x,a,x')` · `Q*_H` oracle.

**Inherited harness assertions, failing loudly:** a perfect predictor scores exactly 1.0; a constant
predictor exactly 0.5; the metric is invariant under strictly monotone score transforms; permuted
labels sit at chance; and **`Z(x)` must come out exactly candidate-invariant at 0.5000** — not
approximately — if the state-only arm is implemented correctly. That exact zero is the one durable
result cycles 001–005 produced and it is the cheapest possible check that the new harness is wired
correctly.

**KILL condition, pre-registered:** `Z(x,a)` fails to exceed the state-independent action prior by
more than the cell-clustered interval, **on a population whose decision-bearing headroom was censused
in advance.**

**What a negative would mean — and this bound is not optional.** A negative establishes failure of
**the tested representation, on the tested state distribution, under the tested action vocabulary and
horizon.** It does **not** establish that mathematical search lacks navigational structure. Cycles
001–005 were narrowed twice by external review for exactly this overreach, and the corrected
statements are the ones to inherit.

## 4. Minimum executable artifacts, before any first measurement

Smallest set that must exist. Anything beyond this is out of scope for the handoff.

1. **Canonical proof-state deduplication.** Without it `G_H` is inflated by syntactic variants and
   every downstream count is wrong.
2. **Exhaustive expander** `G_H(x0)` under a **closed atomic vocabulary** — individual `intro`,
   `constructor`, `rw [L]`, `apply L` instances. **`simp` excluded**, or its internal work charged
   explicitly; a macro tactic hides the search inside the action, which is the thing under test.
3. **Exact `Q*_H` by backward search** from kernel-verified terminal states.
4. **Decision-bearing census over the whole reachable graph, before any restriction.** Report the
   fraction of states with `0 < |{a : Q*_H(x,a) > 0}| < |A(x)|`. States where all actions fail teach
   nothing about ranking; states where all succeed teach little. **Do not silently restrict to the
   informative set after looking** — this is the headroom check whose omission wasted cycle 005's
   Arm A, and it is the artifact most likely to kill the successor cheaply.
5. **Four pre-declared state measures** — uniform over roots; uniform over unique reachable states;
   stratified over (distance-from-root, distance-to-proof, branching); uniform over decision-bearing
   states. **A real effect must not exist under only one.**
6. **Theorem-family-level splits.** Never proof-state level; neighbouring states of one theorem must
   not straddle the split.
7. **Enumeration as the non-LLM control.** With a closed vocabulary the full candidate set is known,
   so **there is no action proposer at all.** `exact?`/`apply?` are later search-agent baselines
   charged by premises inspected or kernel calls — never atomic actions.
8. **The proxy-reconstruction audit as a pre-registered control, not a post-hoc forensic.** It only
   existed in cycles 001–005 because a reviewer demanded it afterwards. Give the reconstructor a
   strong learner and a fair budget: a weak baseline flatters the claim, and the first version of that
   audit was contaminated in exactly the direction that suited the hypothesis.

**Sampling design detail** — reachable-graph expansion, stratification, and why human-trajectory
sampling reproduces the same defect one level up — is in `REVIEW_ROUND2_CORRECTIONS_2026-08-25.md`
§6. It is referenced, not restated, deliberately.

## 5. What this handoff refuses to carry

No architecture. No system design. No roadmap beyond the first measurement. No claim that this
environment will work — only that it changes the causal shape of the oracle, which is the specific
defect that ended the predecessor. **The successor inherits a problem and its discriminating tests.
If it acquires an architecture programme before it acquires a result, that is the predecessor's
failure mode reappearing in a cleaner costume.**

*— Diomedes, Lean successor handoff, 2026-08-26. Owed at thread close; now discharged.*
