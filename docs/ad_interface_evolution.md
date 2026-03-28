# A/D Interface Evolution Design

*Evolve interfaces between Solver (A/C) and Critic (D) tools*

## The Insight

The tool library has a natural division:
- **97 Solvers** (Architecture A/C): 91-92% unseen accuracy, can compute answers
- **240 Critics** (Architecture D): 73% Tier B accuracy, good at detecting problems

Don't evolve D tools into A tools. Evolve better **interfaces** between them.

## Architecture

```
Prompt + Candidates
    │
    ▼
┌─────────────┐
│  Solver (A)  │──→ Ranked candidates + scores
└─────────────┘
    │
    ▼
┌─────────────┐
│  Critic (D)  │──→ Confidence adjustment + flags
└─────────────┘
    │
    ▼
Final ranking (Solver accuracy + Critic judgment)
```

## Interface Protocol

```python
class SolverCriticPair:
    def __init__(self, solver, critic):
        self.solver = solver  # Architecture A/C tool
        self.critic = critic  # Architecture D tool

    def evaluate(self, prompt, candidates):
        # Step 1: Solver ranks candidates
        solver_result = self.solver.evaluate(prompt, candidates)

        # Step 2: Critic evaluates each candidate independently
        critic_scores = {}
        for cand in candidates:
            critic_result = self.critic.evaluate(prompt, [cand, ""])
            critic_scores[cand] = critic_result[0]["score"] if critic_result else 0.5

        # Step 3: Blend (solver 70%, critic 30%)
        blended = []
        for r in solver_result:
            c_score = critic_scores.get(r["candidate"], 0.5)
            combined = 0.7 * r["score"] + 0.3 * c_score
            blended.append({
                "candidate": r["candidate"],
                "score": combined,
                "reasoning": f"solver:{r['score']:.2f} critic:{c_score:.2f} | {r.get('reasoning', '')}",
            })
        blended.sort(key=lambda x: -x["score"])
        return blended

    def confidence(self, prompt, answer):
        s_conf = self.solver.confidence(prompt, answer)
        c_conf = self.critic.confidence(prompt, answer)
        # Critic's LOW confidence overrides solver's HIGH confidence
        if c_conf < 0.3:
            return min(s_conf, c_conf + 0.1)  # Cap at critic's doubt + small margin
        return 0.6 * s_conf + 0.4 * c_conf
```

## Selection Pressure

The key innovation: **Critic negative signals override Solver positive signals.**

When a Critic tool says "this looks wrong" (confidence < 0.3) and the Solver says
"this looks right" (confidence > 0.7), the pair returns low confidence. This creates
selection pressure for:
- Solvers that produce answers Critics agree with
- Critics that flag genuinely problematic answers (not random noise)

## Evolution Strategy

1. Pre-compute all Solver × Critic pairs on the 89-category battery
2. Select pairs where the combination outperforms the Solver alone
3. These pairs define "compatible" Solver-Critic relationships
4. Apollo can breed within compatible pairs

## Metrics

- **Pair accuracy**: does the combination beat the Solver alone?
- **Pair calibration**: does Critic suppression improve calibration?
- **Complementarity**: do they disagree on different categories?
