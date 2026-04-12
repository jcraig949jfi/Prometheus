# Causal Inference + Counterfactual Reasoning + Sensitivity Analysis

**Fields**: Information Science, Philosophy, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T19:41:54.122110
**Report Generated**: 2026-04-02T12:33:29.266023

---

## Nous Analysis

**Algorithm**  
The tool builds a lightweight causal graph from the prompt and each candidate answer, then scores the answer by evaluating its truth under interventions, counterfactuals, and sensitivity to edge‑weight perturbations.  

1. **Parsing** – Using regex, extract tuples (subject, relation, object) where relation ∈ {causes, leads to, results in, if → then, increases, decreases}. Negations flip the sign of the edge weight; modal verbs (may, might, must) scale weight by 0.5, 0.5, 1.0 respectively. Numeric comparatives (> , < , =) generate inequality constraints stored separately.  
2. **Graph structure** – Nodes are entity strings; edges are directed with an initial weight w₀ ∈ [0,1] reflecting linguistic confidence. The graph is kept acyclic by rejecting edges that would create a cycle (or by assigning them to a separate “feedback” list ignored in scoring).  
3. **Structural equations** – For each node V, define a simple linear‑threshold SEM: V = Σ(wᵢ·Uᵢ) + b, where Uᵢ are parents, b is a bias set to 0.5. This allows deterministic evaluation of do‑interventions: to compute P(Y|do(X=x)), cut incoming edges to X, set X=x, and propagate forward. Counterfactuals are evaluated by first computing the factual state, then applying the do‑operation for the antecedent and reading the consequent.  
4. **Scoring a candidate** –  
   *Base score* = 1 if the candidate’s causal/counterfactual claim matches the graph‑derived truth value, else 0 (softened to a sigmoid of the continuous output to allow partial credit).  
   *Sensitivity* = standard deviation of the base score after perturbing each edge weight wᵢ → wᵢ+ε (ε=0.01) and re‑evaluating the candidate; high variance indicates reliance on fragile assumptions.  
   *Final score* = base – λ·sensitivity (λ=0.2, clipped to [0,1]).  

**Structural features parsed** – negations, modal auxiliaries, conditional “if‑then”, causal verbs, comparatives (>/<), temporal ordering (before/after), numeric quantities, quantifiers (all/some/none), and conjunction/disjunction cues.  

**Novelty** – While causal graph extraction and counterfactual QA exist (e.g., CausalQA, CF‑QA), few scoring mechanisms explicitly propagate sensitivity to edge‑weight perturbations as a robustness penalty. This tight integration of do‑calculus, counterfactual evaluation, and finite‑difference sensitivity is therefore relatively novel.  

Reasoning: 8/10 — captures intervention and counterfactual logic via explicit graph semantics.  
Metacognition: 7/10 — sensitivity term provides a principled uncertainty estimate.  
Hypothesis generation: 6/10 — can generate alternative worlds by varying edge weights but does not propose new causal structures.  
Implementability: 9/10 — uses only numpy for matrix ops and stdlib for regex/graph handling; no external dependencies.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 7/10 |
| Hypothesis Generation | 6/10 |
| Implementability | 9/10 |
| **Composite** | **7.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=34% cal=5% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T11:48:42.232345

---

## Code

**Source**: scrap

[View code](./Causal_Inference---Counterfactual_Reasoning---Sensitivity_Analysis/tool.py)

<details>
<summary>Show code</summary>

```python
"""
Causal Inference x Counterfactual Reasoning x Sensitivity Analysis Tool

Builds lightweight causal graphs from text, evaluates interventions and 
counterfactuals via structural equations, and penalizes fragile assumptions
through edge-weight sensitivity analysis. Tracks state dynamics across 
premise sequences to measure trajectory stability.
"""

import re
import numpy as np
from collections import defaultdict
import zlib

class ReasoningTool:
    def __init__(self):
        self.lambda_sensitivity = 0.2
        self.perturbation = 0.01
        
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        """Score candidates by causal consistency, counterfactual validity, and robustness."""
        results = []
        
        # Parse prompt graph
        prompt_graph = self._parse_causal_graph(prompt)
        
        # Extract dynamics from prompt
        dynamics_baseline = self._compute_dynamics(prompt)
        
        for candidate in candidates:
            # Build combined graph
            combined_graph = self._merge_graphs(prompt_graph, self._parse_causal_graph(candidate))
            
            # Base score: causal/counterfactual consistency
            base_score = self._evaluate_consistency(prompt, candidate, combined_graph)
            
            # Sensitivity penalty
            sensitivity = self._compute_sensitivity(prompt, candidate, combined_graph)
            
            # Dynamics stability score
            dynamics_score = self._evaluate_dynamics_stability(prompt, candidate, dynamics_baseline)
            
            # NCD tiebreaker (max 15%)
            ncd = self._normalized_compression_distance(prompt, candidate)
            ncd_score = (1 - ncd) * 0.15
            
            # Combine: dynamics 40%, base 30%, structural 15%, NCD 15%
            final_score = np.clip(
                0.4 * dynamics_score + 
                0.3 * (base_score - self.lambda_sensitivity * sensitivity) + 
                0.15 * self._structural_match(prompt, candidate) +
                ncd_score,
                0, 1
            )
            
            reasoning = f"Base:{base_score:.2f} Sens:{sensitivity:.2f} Dyn:{dynamics_score:.2f} NCD:{ncd_score:.2f}"
            results.append({"candidate": candidate, "score": final_score, "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence with epistemic honesty checks."""
        # Meta-confidence: check for ambiguity/unanswerability
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        # Build graphs
        prompt_graph = self._parse_causal_graph(prompt)
        answer_graph = self._parse_causal_graph(answer)
        combined = self._merge_graphs(prompt_graph, answer_graph)
        
        # Evaluate consistency
        base = self._evaluate_consistency(prompt, answer, combined)
        sensitivity = self._compute_sensitivity(prompt, answer, combined)
        
        # Dynamics check
        dynamics_baseline = self._compute_dynamics(prompt)
        dynamics_score = self._evaluate_dynamics_stability(prompt, answer, dynamics_baseline)
        
        # Conservative confidence
        conf = np.clip(0.5 * base + 0.3 * dynamics_score - 0.2 * sensitivity, 0, 0.9)
        
        return min(conf, meta_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Detect ambiguity, presupposition, false dichotomy, unanswerability."""
        p_lower = prompt.lower()
        
        # Presupposition traps
        if re.search(r'\b(have you stopped|have you quit|why did.*fail|why did.*stop)', p_lower):
            return 0.2
        
        # Scope ambiguity: "every X ... a Y"
        if re.search(r'\bevery\b.*\ba\b', p_lower):
            return 0.25
        
        # Pronoun ambiguity with "who" question
        if re.search(r'\b(he|she)\b', p_lower) and 'who' in p_lower:
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither\b.*\bor\b', p_lower) and 'only' not in p_lower:
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p_lower):
            return 0.3
        
        # Insufficient information markers
        if any(x in p_lower for x in ['not enough', 'cannot determine', 'insufficient']):
            return 0.2
        
        return 1.0
    
    def _parse_causal_graph(self, text: str) -> dict:
        """Extract (subject, relation, object) tuples into weighted graph."""
        graph = defaultdict(lambda: defaultdict(float))
        
        # Causal patterns
        patterns = [
            (r'(\w+)\s+(causes|leads to|results in)\s+(\w+)', 0.8),
            (r'if\s+(\w+)\s+then\s+(\w+)', 0.7),
            (r'(\w+)\s+increases\s+(\w+)', 0.6),
            (r'(\w+)\s+decreases\s+(\w+)', -0.6),
            (r'(\w+)\s+before\s+(\w+)', 0.5),
            (r'(\w+)\s+after\s+(\w+)', -0.5),
        ]
        
        for pattern, weight in patterns:
            for match in re.finditer(pattern, text.lower()):
                subj = match.group(1)
                obj = match.group(2) if len(match.groups()) == 2 else match.group(3)
                
                # Negation flips sign
                context = text[max(0, match.start()-20):match.start()]
                if re.search(r'\b(not|no|never)\b', context):
                    weight *= -1
                
                # Modal verbs scale weight
                if re.search(r'\b(may|might)\b', context):
                    weight *= 0.5
                elif re.search(r'\bmust\b', context):
                    weight *= 1.0
                
                graph[subj][obj] = weight
        
        return graph
    
    def _merge_graphs(self, g1: dict, g2: dict) -> dict:
        """Merge two causal graphs."""
        merged = defaultdict(lambda: defaultdict(float))
        for g in [g1, g2]:
            for src, targets in g.items():
                for tgt, w in targets.items():
                    merged[src][tgt] = max(merged[src][tgt], w)
        return merged
    
    def _evaluate_consistency(self, prompt: str, candidate: str, graph: dict) -> float:
        """Evaluate causal/counterfactual claims via graph propagation."""
        # Extract claims from candidate
        claims = self._extract_claims(candidate)
        if not claims:
            return 0.5
        
        matches = 0
        for claim_subj, claim_obj, expected_sign in claims:
            # Propagate through graph
            influence = self._propagate(graph, claim_subj, claim_obj)
            
            # Check sign consistency
            if (expected_sign > 0 and influence > 0.3) or (expected_sign < 0 and influence < -0.3):
                matches += 1
            elif abs(influence) < 0.2:  # Neutral
                matches += 0.5
        
        return matches / len(claims) if claims else 0.5
    
    def _extract_claims(self, text: str) -> list:
        """Extract testable causal claims."""
        claims = []
        # Positive causal claims
        for match in re.finditer(r'(\w+)\s+(causes|leads to|increases)\s+(\w+)', text.lower()):
            claims.append((match.group(1), match.group(3), 1))
        # Negative causal claims
        for match in re.finditer(r'(\w+)\s+(prevents|decreases)\s+(\w+)', text.lower()):
            claims.append((match.group(1), match.group(3), -1))
        return claims
    
    def _propagate(self, graph: dict, start: str, end: str, visited=None) -> float:
        """Compute influence of start on end via graph traversal."""
        if visited is None:
            visited = set()
        if start == end:
            return 1.0
        if start in visited:
            return 0.0
        
        visited.add(start)
        total = 0.0
        
        if start in graph:
            for neighbor, weight in graph[start].items():
                downstream = self._propagate(graph, neighbor, end, visited.copy())
                total += weight * downstream
        
        return np.clip(total, -1, 1)
    
    def _compute_sensitivity(self, prompt: str, candidate: str, graph: dict) -> float:
        """Measure score variance under edge weight perturbations."""
        base_score = self._evaluate_consistency(prompt, candidate, graph)
        
        scores = [base_score]
        for src in list(graph.keys())[:5]:  # Limit for efficiency
            for tgt in list(graph[src].keys())[:3]:
                perturbed = {k: dict(v) for k, v in graph.items()}
                perturbed[src][tgt] += self.perturbation
                perturbed_score = self._evaluate_consistency(prompt, candidate, perturbed)
                scores.append(perturbed_score)
        
        return np.std(scores) if len(scores) > 1 else 0.0
    
    def _compute_dynamics(self, text: str) -> np.ndarray:
        """Extract state trajectory from sequential premise processing."""
        sentences = re.split(r'[.!?]', text)
        states = []
        state = np.zeros(5)  # 5-dim state vector
        
        for sent in sentences:
            # Update state based on sentence features
            state[0] += len(re.findall(r'\bcauses\b', sent.lower())) * 0.3
            state[1] += len(re.findall(r'\bif\b', sent.lower())) * 0.2
            state[2] += len(re.findall(r'\bnot\b', sent.lower())) * -0.2
            state[3] += len(re.findall(r'\d+', sent)) * 0.1
            state[4] = np.tanh(state[:4].sum())  # Recurrent component
            
            states.append(state.copy())
        
        return np.array(states) if states else np.zeros((1, 5))
    
    def _evaluate_dynamics_stability(self, prompt: str, candidate: str, baseline: np.ndarray) -> float:
        """Measure trajectory convergence and stability."""
        # Compute candidate trajectory
        cand_traj = self._compute_dynamics(candidate)
        
        # Lyapunov-style stability: does trajectory converge?
        if len(cand_traj) > 1:
            deltas = np.diff(cand_traj, axis=0)
            convergence = 1.0 / (1.0 + np.mean(np.abs(deltas)))
        else:
            convergence = 0.5
        
        # Alignment with baseline trajectory
        if len(baseline) > 0 and len(cand_traj) > 0:
            alignment = 1.0 / (1.0 + np.linalg.norm(baseline[-1] - cand_traj[-1]))
        else:
            alignment = 0.5
        
        return 0.6 * convergence + 0.4 * alignment
    
    def _structural_match(self, prompt: str, candidate: str) -> float:
        """Extract structural features for matching."""
        score = 0.0
        
        # Negation consistency
        p_neg = len(re.findall(r'\b(not|no|never)\b', prompt.lower()))
        c_neg = len(re.findall(r'\b(not|no|never)\b', candidate.lower()))
        score += 0.3 * (1 - abs(p_neg - c_neg) / max(p_neg + c_neg, 1))
        
        # Conditional consistency
        p_cond = len(re.findall(r'\bif\b', prompt.lower()))
        c_cond = len(re.findall(r'\bif\b', candidate.lower()))
        score += 0.3 * (1 - abs(p_cond - c_cond) / max(p_cond + c_cond, 1))
        
        # Numeric extraction
        p_nums = [float(x) for x in re.findall(r'\d+\.?\d*', prompt)]
        c_nums = [float(x) for x in re.findall(r'\d+\.?\d*', candidate)]
        if p_nums and c_nums:
            score += 0.4 * min(len(set(p_nums) & set(c_nums)) / len(set(p_nums)), 1.0)
        
        return score
    
    def _normalized_compression_distance(self, s1: str, s2: str) -> float:
        """NCD using zlib."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
```

</details>
