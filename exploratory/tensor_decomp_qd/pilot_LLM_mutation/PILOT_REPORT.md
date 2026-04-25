# LLM-Mutation Pilot Report — polymul-n=3 over F_2

**Run:** Harmonia_M2_sessionB, 2026-04-25
**Scope:** wrap Claude Haiku 4.5 as the mutation operator inside MAP-Elites,
applied to the polymul-n=3 substrate where local mutation already showed
12 sub-optimal rank-9 orbits. Tests whether LLM proposals can bridge orbits
that local moves cannot.

## Outcome

**B — LLM mutation at the entry-edit level produces zero valid decompositions and zero novel orbits.**

The pilot's automated diagnosis emitted "OUTCOME A" based on one rank-9 orbit unique to the LLM-AUG run vs the matched-budget baseline. Reading the LLM-attribution counter (which tracks orbits discovered specifically via the LLM mutation path), that single orbit was **not** LLM-attributed — it came from local-mutation stochasticity. With LLM-attributed = 0 novel orbits, the honest outcome is B.

## What the numbers actually say

| Metric | BASELINE (local only) | LLM-AUG (local + LLM) |
|---|---|---|
| Generations | 1500 | 1500 |
| Population | 50 | 50 |
| Total submissions | 1552 | 1552 |
| Valid decompositions | 44 | 47 |
| Fitness rate | 2.84% | 3.03% |
| Cells populated | 3 | 3 |
| Orbits found | 3 | 3 |
| Karatsuba rank-6 found | yes | yes |
| Distinct rank-9 orbits | 2 | 2 |
| **LLM-attributed orbits** | n/a | **0** |
| API calls used | n/a | 139 / 150 (cap respected) |
| Parse success | n/a | 139 / 139 (100%) |
| API success | n/a | 139 / 139 (100%) |
| **Valid LLM mutations** | n/a | **0 / 139** |

The technical integration is flawless — 139 successive API calls, every response parsed cleanly, no failures. **And every single LLM-proposed mutation produced an invalid decomposition.**

## Why it failed (the structural finding)

The LLM was prompted to propose a "small modification (1-3 entry changes OR a column-level swap) that might lead to a different valid decomposition." It dutifully proposed small modifications. Those small modifications hit the **exact Hamming-isolation wall already documented across all five F_2 + F_3 matmul pilots and the polymul pilot:** valid decompositions are isolated points in factor-matrix space; tiny perturbations almost always invalidate.

The LLM has no privileged access to algebraic correctness over F_2. From its perspective, a "small edit" of (A, B, C) is a syntactic transformation of three numpy arrays — it has no way to know that flipping bit (3, 2) in B will destroy the matmul-sum identity. Its mutations are no better than random small flips, and we already proved random small flips don't work.

**This isn't a prompt-engineering problem.** A more sophisticated prompt that asks the LLM to "reason about which edits preserve the bilinear sum identity" would not help unless the LLM can do that reasoning correctly with high reliability — which is asking the model to do, on the fly, what 50+ years of algebraic-complexity research has produced specific tools for (Brent equations, Kruskal uniqueness, flip graphs).

## What the LLM mutation IS the right tool for

By process of elimination, the comparable AlphaEvolve approach succeeds where this approach failed for two reasons:
1. **Higher-level edits** — AlphaEvolve evolves CODE that *generates* decompositions, not the entry tensor itself. The semantic level is one rung up.
2. **Larger compute budget** — AlphaEvolve uses thousands of GPU-hours of LLM evaluation, not 139 calls.

Our pilot's defensible negative finding: **direct entry-level LLM mutation does not bridge the Hamming isolation that local moves cannot.** This narrows the LLM-mutation hypothesis space — if we want to use LLMs as mutation operators in tensor-decomposition QD, they must either:
- propose at the code/algorithm level rather than the tensor level, or
- be coupled with a validity-preserving wrapper (e.g., proposed edits are projected onto the validity manifold via a separate solver before evaluation), or
- be calibrated for much larger budgets where occasional valid hits become statistically findable.

## What works (infrastructure-level wins)

- **API integration is solid.** `keys.get_key("anthropic")` works as advertised; client construction wraps cleanly; 139 calls completed without API or parse errors. The framework is reusable for any future LLM-as-mutation experiment.
- **Budget enforcement is tight.** Hard cap at 150 calls held; the run exited at 139 because the loop ended naturally, not because of cap-throttle. The `BudgetCounter` is reusable.
- **JSON parsing is defensive.** Code-fence stripping, trailing-text tolerance, dimension validation all worked across 139 different LLM responses.
- **Side-by-side comparison framework** is reusable for any future pilot comparing two mutation operators at matched compute budget.

## Honest claim

> Wrapping a small LLM (Claude Haiku 4.5) as a mutation operator inside MAP-Elites,
> at entry-edit granularity with a 150-call budget, **does not surface any valid
> decompositions** on the polymul-n=3 over F_2 substrate. The bottleneck is the same
> factor-matrix Hamming-isolation that defeated bit-flip mutation across all
> earlier pilots. LLM proposals are not better than random small perturbations
> when the model has no algebraic feedback signal.

## Compatible interpretations of the data

1. **Strong null:** at this granularity and budget, LLM mutation provides nothing.
2. **Weak null:** Haiku 4.5 specifically, at this granularity and budget, provides nothing — Sonnet/Opus might do better; but the structural issue (no algebraic feedback) stays.
3. **Methodology critique:** the "edit a tensor" framing is wrong; "edit code that generates a tensor" is the AlphaEvolve framing and might work at our budget if the code is small enough that local edits preserve correctness.

For (3) to be tested, an entirely different pilot architecture would be needed — out of scope for this run but a clean follow-up direction.

## Provenance

- Code: `tensor_decomp_qd/pilot_LLM_mutation/`
  - `llm_mutate.py` — API client + serialization + parse
  - `map_elites_llm.py` — MAP-Elites with LLM mutation slot
  - `run_pilot.py` — side-by-side orchestrator
  - `smoke_test_api.py` — 1-call connectivity verification
- Logs: `llm_calls.log` (139 entries), `run_log.txt`
- Reuses: `pilot_polymul_n3/` for tensor + canonicalizer + descriptors
- API model: `claude-haiku-4-5-20251001`
- Total API cost: trivial (~$0.10 estimated for 139 small Haiku calls)
- Reproducible under fixed seed (seed=0 for both runs)
