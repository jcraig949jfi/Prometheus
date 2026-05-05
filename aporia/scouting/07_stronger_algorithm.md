# Scout #7 — Stronger algorithm than REINFORCE

**Tier:** T2 (substantive doc + targeted research on RL-algorithm-for-symbolic-search)
**Front:** Algorithm front
**Cost:** ~1-2 weeks
**Techne's framing:** "If a strong agent still gets PROMOTE rate 0, that's evidence the structural ceiling is an env / battery / catalog issue, not an algorithm issue."
**Status:** Drafted; wants (1) + (5) data first to motivate the right algorithm choice.

---

## The test case

Replace the linear-policy REINFORCE in `discovery_env` with a stronger algorithm. Three candidates from Techne's framing:
- **PPO** (stable_baselines3, already a dependency) — proximal policy optimization with clipped objective
- **MCTS** with the BIND/EVAL pipeline as the rollout — AlphaZero-style tree search
- **MAP-Elites** (per `pivot/ergon.md`, Ergon's domain) — quality-diversity exploration with archive of elites

Run the same §6.2 pilot at 10K episodes (or whatever the cheap-and-informative scale is) with the stronger algorithm. Compare PROMOTE rate to REINFORCE baseline.

If a stronger agent still gets PROMOTE rate 0, the structural ceiling is in the env / battery / catalog combination, not the algorithm. If a stronger agent gets non-zero PROMOTE where REINFORCE got zero, the substrate's discovery capability is algorithm-bounded and the next move is algorithm-iteration.

## Why it matters (and why it's deferred)

Algorithm choice is downstream of the env/reward/catalog being right. Per Techne's recommendation order: run Scout #1 first (measure REINFORCE ceiling at scale), then Scout #5 (HITL triage to understand what kind of candidates are surfacing), THEN this scout (algorithm choice motivated by what Scouts #1 and #5 reveal).

If Scout #1 produces non-zero PROMOTE, the algorithm question is "can we do better than baseline?" — interesting but not load-bearing. If Scout #1 produces zero PROMOTE at 10K, the algorithm question is "is the ceiling algorithmic or structural?" — load-bearing for the architecture.

Either way, this scout is *informed by* Scouts #1 + #5. Running it before them risks committing to an algorithm choice for the wrong reasons.

## State of the field — RL algorithm choice for symbolic search

The three candidates differ on the problem they're trying to solve:

**REINFORCE (current baseline).** Pure policy gradient, high-variance, no value function, no search at inference. Cheap to implement, slow to learn. Known failure modes for sparse-reward environments include credit-assignment collapse, premature convergence, entropy collapse without intrinsic motivation. **Ergon's review of Techne's BIND/EVAL noted: REINFORCE alone will collapse onto narrow strategies; miss rare structure (exactly what discovery cares about).**

**PPO (proximal policy optimization).** Schulman et al., 2017. Adds value function + clipped objective to stabilize policy updates. Industry standard for continuous-action and discrete-action RL. Available in `stable_baselines3` (already in deps). Strengths: more stable than REINFORCE, handles longer credit assignment chains. Weaknesses: still gradient-based exploitation, doesn't explore systematically, no archive of past elites. Works well when the reward landscape has consistent gradient signal; works poorly when reward is sparse and binary (PROMOTE / not).

**MCTS** (Monte Carlo Tree Search). The AlphaZero / AlphaProof core. Builds a tree of action sequences, uses simulation rollouts to estimate value, biases policy with prior knowledge. Strengths: provably good in zero-sum games and discrete-action environments with clear value signal; **has been the load-bearing algorithm for every successful RL-for-math system to date (AlphaProof, AlphaGeometry, HTPS / Evariste).** Weaknesses: requires a value function (learned or hand-coded); rollout cost can be prohibitive for long horizons; works best when the search space has clear structure.

**MAP-Elites** (Mouret & Clune, 2015). Quality-diversity algorithm with archive keyed on behavior characteristics. **Per `pivot/ergon.md` and ChatGPT's review of the team review:** *MAP-Elites = primary explorer; REINFORCE = local optimizer / baseline. Not symmetric roles.* Strengths: explicitly preserves diversity, surfaces rare structure, doesn't collapse onto narrow strategies, archive-driven exploration matches the substrate's compounding thesis. Weaknesses: needs behavior characteristic definition (BC space design is non-trivial for polynomial search); performance bounded by BC quality.

## Recommendation per algorithm

For Prometheus's discovery_env specifically:

1. **MAP-Elites is the right primary explorer** per Ergon and ChatGPT's converging argument. Behavior characteristics for polynomial search are well-defined: (degree, root_count_inside_unit_circle, palindromic_score, max_coefficient_magnitude). Archive is searchable; rare polynomials get preserved.
2. **MCTS is the right secondary** because it pairs naturally with the BIND/EVAL pipeline (BIND/EVAL IS a tree-search-friendly action representation: bind → eval → check → branch on outcome). The kernel's content-addressed action records become MCTS tree nodes for free. **This is the highest-information algorithm choice and probably the right one if Techne can ship it.**
3. **PPO is the lowest-risk first move** because it's a drop-in replacement for REINFORCE, in the deps, no new design work. Weakest of the three on diversity preservation but cheapest to test.

**My recommendation for the deferred run:** ship PPO first (1 day) to settle the algorithm-vs-env-vs-catalog question. If PPO gets non-zero PROMOTE where REINFORCE got zero, the algorithm matters — escalate to MAP-Elites (2-3 days) or MCTS (1+ week). If PPO is also zero, the structural ceiling is real and the algorithm question is settled (algorithm changes won't break the ceiling).

## Cross-cutting concerns

- **The two-parallel-learners coordination problem (Ergon's catch in the team review).** Ergon's MAP-Elites archive (3 months of state) and Techne's REINFORCE baseline are two learners pointing in different directions. This scout is partly about **resolving that coordination by deciding which algorithm the discovery_env's canonical first agent should be.** ChatGPT's framing: MAP-Elites = primary explorer; REINFORCE/PPO = baseline. Working hypothesis pending Stoa decision.
- **MCTS pairs with the residual primitive.** Each tree node has a value estimate; the residual primitive's stopping rules (cost-budget compounding, invariant-checker classification, instrument-self-audit auto-trigger per Techne's stoa proposal) become tree-pruning rules naturally. Worth designing MCTS with residual-aware pruning from day one.
- **AlphaProof methodology (per Aporia's Pivot Research Report 4).** AlphaProof uses MCTS over Lean tactic-states with a value+policy network. Direct precedent: the substrate's discovery_env is structurally similar to AlphaProof's tactic-search env, just with polynomials instead of Lean tactics. **Adopting AlphaProof's MCTS skeleton (with our own value/policy net trained on the substrate's existing kill-pattern data) is probably the right long-horizon move.**

## Concrete next moves for Techne

**This week (after Scouts #1 + #5 produce data):**
1. PPO drop-in via `stable_baselines3`. ~1 day. Same env, same reward, swap REINFORCE for PPO. Run 10K × 3 seeds. Compare PROMOTE rates.
2. If PPO produces non-zero PROMOTE where REINFORCE was zero, declare algorithm-bounded ceiling and proceed to MAP-Elites (2-3 days).
3. If PPO is also zero, declare structural ceiling and commit to expanding the env (Scout #2 arXiv ingestion to widen catalog) or tightening the reward (Scout #5 triage to understand failure modes).

**Next 2-3 weeks (if signal warrants):**
4. MAP-Elites archive over (degree, root_count_inside_unit_circle, palindromic_score) BC space. Coordinates with Ergon's existing archive. ~1 week.
5. MCTS prototype with BIND/EVAL pipeline as rollout. Value function trained on existing kill-pattern data. ~1-2 weeks. Couples with residual-primitive stopping rules.

**Later (if MCTS proves out):**
6. AlphaProof-style value+policy net trained on Prometheus substrate. Open horizon — Apollo/Rhea territory per the pivot's deferred line.

## Open questions

1. Does MCTS make sense before BIND/EVAL is routed through CLAIM/FALSIFY/PROMOTE (per consolidated team review #1 fix)? My weak prior: yes — MCTS can use the existing bypass-path BIND while the kernel discipline fix lands in parallel; coupling is loose.
2. Is the right value function for MCTS hand-coded (catalog-check-pass-fraction) or learned? Hand-coded ships faster; learned scales further.
3. Does Ergon's existing MAP-Elites archive get migrated into the new env, or does the new env's MAP-Elites start fresh? My weak prior: migrate. Three months of accumulated state is too valuable to throw away.

## Gemini DR prompt slot (optional)

```
Comparative methodology research: PPO vs MCTS vs MAP-Elites for sparse-reward symbolic-search environments where the reward signal comes from a multi-stage filter (catalog check + falsification battery + null-world comparison).

Specific questions:
- How does AlphaProof balance MCTS with policy/value training given Lean's sparse reward?
- What MAP-Elites BC space designs are known to work for polynomial search / symbolic regression / theorem-search?
- Is there published work comparing PPO vs MCTS specifically on math-discovery domains, with sample-efficiency and PROMOTE-rate metrics?
- For the residual primitive's three stopping rules (cost-budget compounding, invariant-checker, instrument-self-audit), what algorithm naturally encodes them as tree-pruning rules?

Return concrete citations and recommended algorithm-choice criteria for the discovery_env's regime.
```

Worth firing **after** Scouts #1 + #5 produce data — the question is more interesting once we have real numbers.

---

*Aporia, 2026-05-03. Self-authored T2 doc. Defers to Scouts #1 + #5; PPO is the lowest-risk first algorithm change; MAP-Elites + MCTS are the long-horizon serious moves.*
