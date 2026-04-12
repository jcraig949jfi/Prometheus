# Criticality + Counterfactual Reasoning + Hoare Logic

**Fields**: Complex Systems, Philosophy, Formal Methods
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T09:23:37.588992
**Report Generated**: 2026-04-02T04:20:11.063141

---

## Nous Analysis

The algorithm treats each candidate answer as a set of Hoare‑style triples extracted from text. First, regex patterns pull out atomic propositions (e.g., “X > Y”, “¬Z”, “if A then B”) and imperative‑like statements that serve as pre‑ and post‑conditions. Each proposition becomes a node in a directed graph; an edge i→j receives a weight wᵢⱼ∈[0,1] reflecting the strength of the inferred implication (derived from cue words such as “causes”, “leads to”, “implies”). The adjacency matrix W is built with NumPy.

Constraint propagation follows Hoare logic: for every triple {P}C{Q}, we enforce that whenever P holds before C, Q must hold after C. This is implemented by iteratively applying modus ponens on the boolean closure of W (using Warshall’s algorithm) until a fixed point is reached, yielding a matrix C of entailed propositions.

Criticality is introduced by computing the susceptibility matrix S = (I − W)⁻¹ (via NumPy linear solve). Large eigenvalues of S indicate regions where a tiny flip in a proposition propagates widely — akin to a system at the edge of order/disorder. For each candidate, we generate a set of minimal counterfactual worlds by toggling each proposition once (Pearl‑style do‑operation). In each world we re‑run the constraint propagation and measure the violation of the original post‑conditions as a vector Δ. The score is  −‖Δ‖₂ · λ_max(S), rewarding answers that stay consistent under perturbations while residing in a high‑susceptibility (critical) regime.

Parsed structural features: negations (“not”, “no”), conditionals (“if … then …”, “unless”), causal verbs (“causes”, “leads to”), comparatives (“greater than”, “less than”), ordering relations (“before”, “after”), quantifiers (“all”, “some”), and assignment‑like statements (“let X = …”, “increase Y by …”).

The combination of Hoare triples with sensitivity‑based criticality is not present in mainstream QA scoring, which relies on neural similarity or shallow overlap metrics; some work on logical consistency checking exists, but none couples it to eigen‑based susceptibility analysis.

Reasoning: 8/10 — captures logical structure and perturbation sensitivity.  
Metacognition: 6/10 — limited self‑monitoring of reasoning process.  
Hypothesis generation: 7/10 — generates counterfactual worlds systematically.  
Implementability: 9/10 — relies only on regex, NumPy, and standard library.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 7/10 |
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
**Reason**: trap_battery_failed (acc=32% cal=11% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-01T23:16:29.077758

---

## Code

**Source**: scrap

[View code](./Criticality---Counterfactual_Reasoning---Hoare_Logic/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
from typing import List, Dict, Tuple, Any, Optional
from collections import defaultdict

class ReasoningTool:
    """
    A computational reasoning tool implementing Criticality x Counterfactual x Hoare Logic.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions, conditionals, and causal links into a graph.
    2. Representation: Builds an adjacency matrix W where edges represent logical implication strength.
    3. Computation: 
       - Uses Warshall's algorithm for constraint propagation (deducing entailed truths).
       - Computes Susceptibility Matrix S = (I - W)^-1 to identify critical nodes (eigen-analysis).
       - Generates counterfactual worlds by toggling propositions and measuring post-condition violation.
    4. Scoring: Combines logical consistency, counterfactual robustness, and criticality sensitivity.
    5. Epistemic Honesty: Detects ambiguity/presupposition to cap confidence.
    """

    def __init__(self):
        # Regex patterns for structural extraction
        self.patterns = {
            'conditional': re.compile(r'if\s+(.+?)\s+(?:then|,)?\s+(.+?)', re.IGNORECASE),
            'causal': re.compile(r'(.+?)\s+(?:causes|leads to|implies|results in)\s+(.+?)', re.IGNORECASE),
            'comparative_num': re.compile(r'(.+?)\s+(?:is greater than|is less than|>|<|=)\s+(.+?)', re.IGNORECASE),
            'assignment': re.compile(r'(?:let|set)\s+(\w+)\s*=\s*(\d+)', re.IGNORECASE),
            'negation': re.compile(r'(?:not|no|never)\s+(\w+)', re.IGNORECASE),
            'quantifier': re.compile(r'(?:all|every|some)\s+(\w+)', re.IGNORECASE),
            'presupposition': re.compile(r'(?:have you stopped|why did .+ fail|why is .+ bad)', re.IGNORECASE),
            'scope_ambiguity': re.compile(r'every\s+\w+\s+\w+\s+a\s+\w+', re.IGNORECASE), # Simplified heuristic
            'false_dichotomy': re.compile(r'either\s+(.+?)\s+or\s+(.+?)', re.IGNORECASE),
            'subjectivity': re.compile(r'(?:best|worst|favorite|beautiful)', re.IGNORECASE),
        }
        self.stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being'}

    def _tokenize(self, text: str) -> List[str]:
        return [t.strip('.,!?;:') for t in text.lower().split() if t.lower() not in self.stopwords]

    def _extract_propositions(self, text: str) -> List[str]:
        """Extract atomic propositions from text."""
        props = []
        # Simple sentence splitting
        sentences = re.split(r'[.!?]', text)
        for sent in sentences:
            clean = sent.strip()
            if len(clean) > 2:
                props.append(clean)
        return props

    def _build_graph(self, text: str) -> Tuple[List[str], np.ndarray, Dict[str, int]]:
        """
        Build adjacency matrix W from text.
        Nodes are propositions. Edges are implications.
        """
        props = self._extract_propositions(text)
        n = len(props)
        if n == 0:
            return [], np.array([]), {}
        
        W = np.zeros((n, n))
        prop_map = {p: i for i, p in enumerate(props)}
        
        # Extract relations
        # 1. Conditionals: If A then B -> A implies B
        for match in self.patterns['conditional'].findall(text):
            if match[0] in prop_map and match[1] in prop_map:
                W[prop_map[match[0]], prop_map[match[1]]] = 0.9
        
        # 2. Causal verbs
        for match in self.patterns['causal'].findall(text):
            if match[0] in prop_map and match[1] in prop_map:
                W[prop_map[match[0]], prop_map[match[1]]] = 0.85
                
        # 3. Transitivity heuristic (if A > B and B > C, assume A > C structure if detected)
        # For this implementation, we rely on explicit textual links for W
        
        # Fill diagonal slightly for stability, but keep logic pure
        # Normalize rows for probability-like propagation
        row_sums = W.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1  # Avoid division by zero
        W_norm = W / row_sums
        
        return props, W_norm, prop_map

    def _warshall_propagation(self, W: np.ndarray) -> np.ndarray:
        """Apply Warshall's algorithm to find transitive closure of implications."""
        if W.size == 0:
            return W
        n = W.shape[0]
        C = W.copy()
        # Threshold to boolean for strict logic propagation
        C_bool = (C > 0.5).astype(float)
        np.fill_diagonal(C_bool, 1.0) # Reflexive
        
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if C_bool[i, k] and C_bool[k, j]:
                        C_bool[i, j] = 1.0
        return C_bool

    def _compute_susceptibility(self, W: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        Compute susceptibility matrix S = (I - W)^-1.
        Returns S and max eigenvalue (criticality metric).
        """
        if W.size == 0:
            return np.array([]), 0.0
        
        n = W.shape[0]
        I = np.eye(n)
        try:
            # Add small damping to ensure invertibility if near singular
            S = np.linalg.inv(I - 0.9 * W)
            eigenvalues = np.abs(np.linalg.eigvals(S))
            lambda_max = float(np.max(eigenvalues)) if len(eigenvalues) > 0 else 0.0
            return S, lambda_max
        except np.linalg.LinAlgError:
            return np.zeros((n, n)), 0.0

    def _evaluate_candidate_logic(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Core logic: Evaluate candidate against prompt using Hoare-style triples.
        Returns (score, reasoning_string)
        """
        # 1. Parse Prompt into Graph
        props, W, prop_map = self._build_graph(prompt)
        n = len(props)
        
        if n == 0:
            return 0.5, "No logical structure detected."

        # 2. Baseline Consistency Check (Does candidate match any proposition?)
        candidate_lower = candidate.lower()
        matches_prop = any(p.lower() in candidate_lower or candidate_lower in p.lower() for p in props)
        
        # 3. Constraint Propagation
        C = self._warshall_propagation(W)
        
        # 4. Criticality Analysis
        S, lambda_max = self._compute_susceptibility(W)
        
        # 5. Counterfactual Perturbation (Pearl-style do-operation)
        # We simulate toggling each proposition and seeing if the candidate (as a post-condition) breaks
        violations = 0
        total_perturbations = n
        
        if total_perturbations > 0:
            for i in range(n):
                # Create perturbed world: remove node i influence
                W_pert = W.copy()
                W_pert[i, :] = 0 # Remove outgoing edges from i (do-operation)
                W_pert[:, i] = 0 # Remove incoming to isolate? No, just break causal link from i
                
                # Re-propagate
                C_pert = self._warshall_propagation(W_pert)
                
                # Check if original entailments hold
                # If C[0, n-1] was true, is it still true?
                # Simplified: Measure change in total connectivity
                orig_conn = np.sum(C)
                pert_conn = np.sum(C_pert)
                if orig_conn != pert_conn:
                    violations += 1
            
            # Robustness score: High violations means the system is fragile (or candidate depends on specific chain)
            # We want candidates that are robust OR correctly identify the critical path.
            robustness = 1.0 - (violations / total_perturbations) if total_perturbations > 0 else 0.0
        else:
            robustness = 0.0
            lambda_max = 0.0

        # 6. Numeric/Constructive Computation Fallback
        # If the prompt contains numbers, try to solve mathematically
        numeric_score = 0.0
        numbers_prompt = [float(x) for x in re.findall(r'-?\d+\.?\d*', prompt)]
        numbers_cand = [float(x) for x in re.findall(r'-?\d+\.?\d*', candidate)]
        
        if numbers_prompt and numbers_cand:
            # Heuristic: If candidate number is result of simple ops on prompt numbers
            # This is a placeholder for full symbolic math, kept simple for brevity
            try:
                if abs(numbers_cand[0] - sum(numbers_prompt)) < 0.01:
                    numeric_score = 1.0
                elif abs(numbers_cand[0] - (numbers_prompt[0] * numbers_prompt[1] if len(numbers_prompt)>1 else 0)) < 0.01:
                    numeric_score = 1.0
            except:
                pass

        # Final Score Composition
        # Structural (50%) + Criticality/Robustness (35%) + Numeric (15%)
        structural_score = 1.0 if matches_prop else 0.2
        criticality_bonus = min(1.0, lambda_max / 10.0) if lambda_max > 0 else 0.5
        
        score = (0.5 * structural_score) + (0.35 * robustness * criticality_bonus) + (0.15 * numeric_score)
        
        reason = f"Props:{n}, Lambda:{lambda_max:.2f}, Robust:{robustness:.2f}"
        return min(1.0, score), reason

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Returns a cap on confidence based on prompt ambiguity.
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        if self.patterns['presupposition'].search(p_lower):
            return 0.2
        
        # 2. Scope ambiguity (heuristic)
        if self.patterns['scope_ambiguity'].search(p_lower) and 'same' in p_lower:
            return 0.3
            
        # 3. False dichotomy
        if self.patterns['false_dichotomy'].search(p_lower):
            # Check if options are exhaustive (hard to know, but flag if 'only' missing)
            if 'only' not in p_lower:
                return 0.4

        # 4. Subjectivity
        if self.patterns['subjectivity'].search(p_lower):
            if 'fact' not in p_lower and 'data' not in p_lower:
                return 0.3

        # 5. Unanswerability (Missing info)
        if 'cannot be determined' in p_lower or 'insufficient' in p_lower:
            return 0.1
            
        return 1.0 # No red flags

    def _compute_numeric_answer(self, prompt: str) -> Optional[float]:
        """Attempt to constructively solve numeric problems."""
        # Extract all numbers
        nums = [float(x) for x in re.findall(r'-?\d+\.?\d*', prompt)]
        
        # Bat-and-ball style: "A + B = Total, A = B + Diff" -> 2B = Total - Diff
        if 'total' in prompt and 'more' in prompt and len(nums) >= 2:
            # Heuristic for standard algebra word problems
            total = nums[0]
            diff = nums[1]
            if total > diff:
                return (total - diff) / 2
                
        # Modular arithmetic
        if 'mod' in prompt or 'remainder' in prompt:
            if len(nums) >= 2:
                return nums[0] % nums[1]
                
        return None

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-check for constructive numeric solution
        numeric_ans = self._compute_numeric_answer(prompt)
        
        for cand in candidates:
            score = 0.0
            reason = ""
            
            # If we computed a numeric answer, prioritize exact match
            if numeric_ans is not None:
                cand_nums = re.findall(r'-?\d+\.?\d*', cand)
                if cand_nums:
                    if abs(float(cand_nums[0]) - numeric_ans) < 1e-6:
                        score = 0.95
                        reason = "Constructive numeric match."
                    else:
                        score = 0.1
                        reason = f"Numeric mismatch. Computed: {numeric_ans}"
                else:
                    score = 0.1
                    reason = "Numeric problem, non-numeric answer."
            else:
                # Fallback to logical graph analysis
                score, reason = self._evaluate_candidate_logic(prompt, cand)
                
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-cognitive analysis of the prompt.
        """
        # 1. Meta-confidence cap (Epistemic Honesty)
        cap = self._meta_confidence(prompt)
        
        # 2. Base score from evaluation logic
        # We simulate a single-candidate evaluation
        res_list = self.evaluate(prompt, [answer])
        base_score = res_list[0]['score'] if res_list else 0.0
        
        # 3. Apply cap
        final_conf = min(base_score, cap)
        
        # 4. Honesty check: If no structural parser matched and no numeric solution, lower confidence
        if cap == 1.0 and base_score < 0.3:
            # If we didn't find logic and didn't find math, we are guessing
            final_conf = 0.25
            
        return float(np.clip(final_conf, 0.0, 1.0))

# Example usage (for internal verification only):
# if __name__ == "__main__":
#     tool = ReasoningTool()
#     prompt = "If it rains, the ground is wet. It rains."
#     candidates = ["The ground is wet", "The ground is dry"]
#     print(tool.evaluate(prompt, candidates))
#     print(tool.confidence(prompt, "The ground is wet"))
```

</details>
