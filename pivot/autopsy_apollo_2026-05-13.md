# Apollo Autopsy — 2026-05-13

**Subject:** `apollo/` — evolutionary computation engine for reasoning improvements via LLM-guided program synthesis.
**Author:** Aletheia.
**Verdict (one line):** **Showed early-stage potential; the diagnostic of what was wrong already existed in the v2.1 roadmap; revival is justified only if the Frame H primitive set is updated to match the current substrate vocabulary.**
**North Star alignment:** **HIGH.** Apollo's stated deliverable is `(problem_type, primitive_sequence, verified_answer)` triples — *the dataset for the future neural routing network*. This is one of the few agents whose value proposition is directly the Learner's training data.

---

## What it actually produced

| Artifact | Count / state |
|---|---|
| Evolution reports | ~80 reports, April 6–9 (every ~30 min); none after April 9 |
| Active runs at stop | 2 hybrid runs (v2_d2, v2_d2b at gen 642 / 686) + 1 pure-Qwen run (v2_d) |
| Best accuracy margin (April 9) | v2_d2b: **+0.690** over NCD baseline; median **+0.615**, climbing steadily |
| Active LLM mutation operators | `llm_alive=0` across all runs — **LLM mutations not actually surviving to elite** |
| Elite-mutation operators in use | Only `drift` and `seed` (non-LLM) appear in `elite_mutations` |
| Apollo's stated success bar | Gen 50,000 = 1,000+ verified training triples; **Apollo stopped at gen 686** — 1.4% of target |
| Lineage / journal / graveyard / checkpoints dirs | **Do not exist on disk.** Aporia's RESUME doc described them as preserved evolutionary history; they were never created or were cleaned. |
| Local-only API spend | DeepSeek balance reported $9 USD remaining on April 9. Modest. |

## Trajectory signals (what the data says)

1. **The hybrid LLM strategy was working.** 50/50 Qwen + DeepSeek outperformed pure Qwen on both best and median accuracy. This is a *real positive signal*, not noise — DeepSeek-chat introduced diversity that the evolutionary loop could exploit.

2. **The LLM mutation premise was failing.** The whole point of LLM-assisted mutation was that AST-only mutation stalled at NCD baseline in v1. Yet in v2 the elites are still being produced by non-LLM operators (`drift`, `seed`). The LLM mutations are running but not surviving selection. The April 9 report explicitly flags this and asks for prompt tuning.

3. **Multiple v2.1 P0 problems were already biting.** The April 9 report independently surfaced *exactly* what the v2.1 roadmap predicted: archive saturated at 500 with NCD weight=0 (diversity pressure off), best ablation delta static for 10+ generations (local optimum), no stagnation detection. The diagnostic is in hand; the fix list is in hand.

4. **The evolutionary record was thin.** No lineage / graveyard / journal dirs means *the kills weren't preserved*. Apollo's deliverable is supposed to be a (problem → primitive_sequence → answer) corpus including failed organisms. If the graveyard wasn't logging, the kill-information channel was off — that's a structural defect vs. the falsification-first thesis.

## Alignment with the North Star

The North Star is structured reasoning AI: either (a) Math LLM + LoRA bolt-on, or (b) new neural net trained on substrate weights + reasoning artifacts from the forge / Apollo.

Apollo specifically produces option (b)'s training set. Every surviving organism is a verified triple of (problem_type, primitive_sequence, answer). The ablation gate (≥0.20 per primitive) guarantees every primitive in every triple is load-bearing — *which is exactly the discipline needed for a routing-network training corpus*.

**But this only holds if the primitives are still the right grammar.** Apollo evolves compositions over Forge's 25 Frame H primitives. The substrate vocabulary has since grown to 22 Tier-A++ → Tier-E primitives + 20 attack paradigms + 5 patterns + 12 anti-anchors + 2 composition rules. There is no automatic mapping from one to the other.

**Open question: does Apollo's current Frame H gene library cover the substrate vocabulary's reasoning surface, or does the substrate vocabulary obsolete Frame H?** This is the load-bearing strategic question, and it determines whether Apollo's existing 686 generations of work survive or get archived.

## Q1: Was Apollo showing potential?

**YES, modestly.** Three positive signals:
- Cross-LLM hybridization was outperforming the single-LLM baseline (real generalization).
- Median fitness was *climbing* on a 10-generation window (not stagnating).
- The diagnostic-of-what's-wrong was clearly identifiable from the April 9 report (no mystery).

Three caveats:
- Gen 686 / 50,000 is 1.4% of the success bar. "Showed potential" ≠ "delivered value."
- The LLM-mutation premise (the whole reason for v2) was failing — drift/seed beating llm/annealed at the elite tier.
- The graveyard wasn't preserved, so the negative-space signal Apollo was supposed to produce wasn't being captured.

## Q2: Would more thought / engineering help?

**YES, but the work is well-scoped.** Three workstreams in priority order:

1. **Primitive-grammar reconciliation (NEW work, blocking).** Compare Frame H's 25 primitives against the substrate vocabulary's 22 primitives + attacks + patterns. Decide: extend Frame H to cover gaps, or replace it with substrate-vocabulary as the gene library. Estimated effort: 1-2 sessions of structural analysis. This is the load-bearing call.

2. **v2.1 P0 work that already exists (DESIGNED, ~3-7 days).** NSGA-III + stagnation monitoring. ROADMAP.md has both designs sketched in detail. The April 9 report independently confirms both are needed. This is mechanical work, not research.

3. **LLM-mutation prompt tuning (DEBUGGING, ~1 session).** Investigate why LLM mutations aren't surviving. Options: smaller mutations to preserve compilation, lower application rate (5-10% vs current), different prompts. The April 9 DeepSeek analysis suggested these specifically.

**The wrong sequencing:** Don't do (2) or (3) until (1) is settled. Tuning NSGA-III on the wrong primitive set wastes the work.

## Risks of revival

- **Gaming risk:** the ablation gate is the structural guard against bypass. As long as it stays a fitness dimension and not a tiebreaker, Apollo can't degenerate into the Frame H equivalent of NCD-bypass. Verify before resuming.
- **Lineage capture:** without graveyard/lineage on disk, the kill data Apollo is supposed to produce evaporates. Verify these dirs get created and written to before any long run.
- **Single-machine fragility:** Apollo on M2 is one Windows session away from dying. The orchestrator framework would catch this; without it, plan to checkpoint very frequently and accept occasional loss.

## Recommendation

**Don't revive yet.** Do the primitive-grammar reconciliation first as a one-session structural exercise. It produces a single artifact: "do the substrate vocabulary primitives obsolete Frame H, or extend it?"

If the answer is "extend Frame H" → execute v2.1 P0 work, revive on M2 as continuous daemon. Estimated time-to-value: 1-2 weeks.

If the answer is "substrate vocabulary obsoletes Frame H" → Apollo's 686 generations are obsolete but the *infrastructure* (evolutionary loop, ablation gate, fitness eval, sandboxing) is salvageable. Rebuild gene library and seed population from substrate primitives. Estimated time-to-value: 4-6 weeks.

**Don't autopsy a third forge** until this call is made — Apollo is the one whose deliverable most directly serves the North Star, and it's the one whose continued investment depends on a structural question that isn't yet answered.
