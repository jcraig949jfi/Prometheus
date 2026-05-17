# Hephaestus Forge — Actionable Next Steps

**Filed:** 2026-05-17
**Source:** Frontier review synthesis + big-picture coalescence discussion
**Status:** Concrete implementation plan, priority-ordered

---

## The Grounding Principle

Before building more infrastructure, answer: **does the forge produce reusable signal?**

The frontier review consensus plus ChatGPT's grounding check converge on one mandate:

> Expand measurement first. Then layer annotations on confirmed signal. Not the reverse.

The forge currently admits tools at 43% accuracy on a 15-trap battery where the NCD baseline is 42%. With n=15 and binomial CIs of ±13pp, this is statistically indistinguishable from noise. The novelty gate rescues structurally unique tools, but "unique code" ≠ "unique behavior" until proven.

**The decisive question is not "how do we score more dimensions?"**
**It is: "do the failures carry reusable structure?"**

ChatGPT's insight: the failure signatures (kill vectors, scrap reasons, near-miss patterns) may be the more valuable dataset than what clears gates. This aligns perfectly with Prometheus's thesis: negative-space data is the training target.

---

## Phase 0: Measurement Infrastructure (Do Now)

These actions are preconditions for everything else. They cost CPU time, not design time.

### Action 1: Expand the trap battery to 50+ per tier

**Why:** 15 traps gives ±13pp CIs. You cannot distinguish tools from baseline. All tier annotations built on this foundation are suspect.

**How:**
1. Tier-stratify: 10 probes each for R1, R2, R3, R4, R5 (50 minimum)
2. Anchor against external benchmarks (ARC-AGI difficulty bands, BIG-Bench Hard tasks)
3. Include generated probes with hidden seeds (anti-contamination)
4. Store per-tier accuracy, not just aggregate

**Where in code:** Extend `agents/hephaestus/src/test_harness.py`. Add `TIER_PROBES` dict alongside existing `TRAPS` list. Modify `run_trap_battery()` to return per-tier breakdown.

**Estimated effort:** 1 session to design probes, 1 session to implement.

### Action 2: Behavioral phenotype vectors for existing library

**Why:** Determine whether source-code novelty = behavioral novelty. If high-NCD tools produce the same outputs as low-NCD tools, the novelty gate is harvesting syntax, not substance.

**How:**
1. Run all ~120 tools in forge/ through the expanded battery
2. Store output vectors (which candidate each tool picks per probe)
3. Cluster by output phenotype (not source code)
4. Compare clusters against source-code NCD

**Key question answered:** Does qwen-397B produce more behavioral phenotypes or just more syntax?

**Where in code:** Extend `agents/hephaestus/src/novelty_scorer.py`. Add `compute_behavior_vectors()` and `cluster_phenotypes()`.

### Action 3: Failure orthogonality matrix

**Why:** A 43% tool that solves the same problems as every other 43% tool is worthless. A 43% tool that uniquely solves problems no one else gets is gold. This is the most important missing metric per all reviewers.

**How:**
1. For each tool, record which specific probes it gets right
2. Compute pairwise failure overlap: `overlap(A,B) = |correct_A ∩ correct_B| / |correct_A ∪ correct_B|`
3. Tools with low overlap against the library are high-value regardless of accuracy

**Output:** `failure_orthogonality_score` per tool. This becomes a first-class admission criterion alongside accuracy and novelty.

---

## Phase 1: Classify What's Being Produced

Once Phase 0 confirms there IS behavioral signal (not just syntax noise):

### Action 4: Tier profile per tool

Run each tool against the expanded tier-stratified battery. Store:

```json
{
  "accuracy_by_tier": {"R1": 0.62, "R2": 0.48, "R3": 0.31, "R4": 0.55, "R5": 0.20},
  "failure_orthogonality": 0.73,
  "behavioral_cluster_id": "cluster_7",
  "symbol_relabel_delta": -0.03,
  "matched_null_delta": 0.11
}
```

The `matched_null_delta` is critical (ChatGPT): compare against a dumb random-search scaffold with same interface and runtime. This separates "genuinely computes something useful" from "arrives at answers by accident."

### Action 5: Mechanism knockout ablation

For tools with claimed R3+ mechanisms:
- **R3 learner:** Freeze/randomize weight updates → measure output delta
- **R4 searcher:** Reduce budget to 1 / remove backtracking → measure output delta
- **R5 causal:** Reverse causal graph edges → measure output delta
- **R6 monitor:** Force confidence constant → measure calibration delta

If knockout has no effect, the mechanism is decorative. Tool gets reclassified to its actual behavioral tier (likely R1-R2).

### Action 6: Scrap failure taxonomy

Classify the scrap pile not by "why it failed the gate" but by "what kind of reasoning it attempted":

```
For each scrapped tool:
  - What mechanism did it try? (static analysis)
  - How close did it get? (accuracy, per-tier breakdown)
  - What specific problems did it solve that nothing else solves? (failure orthogonality)
  - What killed it? (gate failure reason)
  - Is the kill informative? (does this failure predict anything about adjacent tools?)
```

This turns the scrap pile from "garbage" into "structured failure data" — which is what Prometheus's thesis says is the real training signal.

---

## Phase 2: Value Demonstration

### Action 7: Close one tiny loop

The decisive test of whether the forge produces value:

```
1. Hephaestus generates 500 tools (already done — we have 1,960)
2. Profile them (behavior vectors, tier, failure orthogonality)
3. Apollo composes organisms from a DIVERSE subset vs a HOMOGENEOUS subset
4. Measure: does the diverse subset (selected by failure orthogonality)
   outperform the homogeneous subset (selected by accuracy alone)?
```

If yes: the forge's novelty/diversity produces compositional value for Apollo.
If no: the forge is just a tool farm and novelty scoring is not buying anything.

### Action 8: Track whether failures compound into structure

For the kill ledger (5,309 entries):
- Do kill patterns cluster by concept type? (e.g., "all Topology combos fail on R2 chaining")
- Do kill patterns predict which concepts will succeed? (mutual information between failure mode and future forge success)
- Can a simple model predict whether a NEW concept combo will forge or scrap, based on its concepts' historical kill patterns?

If yes: the negative-space data has learnable structure, vindicating the Prometheus thesis.
If no: failures are random and the kill ledger is just a log.

---

## The Coverage Map (Quality-Diversity Health)

Once we have tier profiles + morpheme classification + failure orthogonality, build a coverage map:

```
              R1    R2    R3    R4    R5    R6
Parser        ███   ██    ░     ░     ░     ░     ← oversupplied
Chainer       ██    ███   █     ░     ░     ░     ← oversupplied  
Learner       ░     █     ██    █     ░     ░     ← undersupplied
Searcher      ░     ░     █     ██    ░     ░     ← undersupplied
Critic        ░     ░     ░     █     ░     ██    ← rare, high value
Monitor       ░     ░     ░     ░     ░     ██    ← rare, high value
Causal        ░     ░     ░     ░     █     ░     ← rare
```

This tells the forge what to aim for next. Bias Nous concept selection toward combinations that historically produce underrepresented morpheme types.

---

## What "Demonstrable Value" Looks Like

Not "we have 1,960 tools." Not "novelty score is high." Not "tier profile says R4."

Demonstrable value = one of these measurable claims:

1. **Tools with high failure orthogonality compose better in Apollo** (diversity → compositional gain)
2. **Kill patterns predict future forge outcomes** (failures are structured, not random)
3. **Behavioral tier correlates with ablation impact in Apollo** (tier annotations have compositional meaning)
4. **Forge search can be biased by historical outcomes** (the loop closes, even weakly)
5. **Near-miss scraps contain repair signals** (scrap pile → future forge improvement)

Each is testable. Each has a null baseline. Each, if confirmed, justifies continued forge operation.

---

## Implementation Priority

| Priority | Action | Effort | Blocks |
|---|---|---|---|
| **P0** | Expand trap battery to 50+ | 2 sessions | Everything downstream |
| **P0** | Behavioral phenotype vectors | 1 session | Novelty validation |
| **P0** | Failure orthogonality matrix | 1 session | Value scoring |
| **P1** | Tier profile per tool | 1 session | Classification |
| **P1** | Mechanism knockout ablation | 1 session | Decorative-R4 filter |
| **P1** | Scrap failure taxonomy | 1 session | Structured negative data |
| **P2** | Close one tiny loop (diverse vs homogeneous Apollo) | Requires Apollo | The decisive test |
| **P2** | Kill pattern predictability | 1 session | Prometheus thesis validation |

---

## The North Star Check

Every 30 days, ask:

> Has any subsystem measurably improved another subsystem's output quality or search efficiency?

If yes after 90 days: the ecology is real.
If no after 90 days: the ecology is a collection of independent MVPs with a shared aesthetic.

Both answers are useful. The second tells you to stop investing in integration and just run the parts that produce standalone value (probably the falsification battery and the forge's novelty-diverse tool library as a standalone benchmark corpus).
