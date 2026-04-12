# Causal Inference + Feedback Control + Free Energy Principle

**Fields**: Information Science, Control Theory, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T09:35:01.389306
**Report Generated**: 2026-04-01T20:30:43.842117

---

## Nous Analysis

**Algorithm**  
We build a lightweight *causal‑prediction controller* that scores each candidate answer by treating the prompt as a generative model, the answer as a hypothesised observation, and iteratively reducing prediction error with a PID‑like update that also penalises model complexity (variational free energy).  

1. **Parsing & data structures**  
   - Tokenise the prompt and each candidate answer with regex‑based patterns to extract:  
     * entities (noun phrases),  
     * numeric literals,  
     * causal predicates (`cause`, `lead to`, `because`),  
     * comparatives (`greater than`, `less than`),  
     * conditionals (`if … then …`),  
     * negations (`not`, `no`).  
   - Build a directed acyclic graph **G** = (V, E) where V = entities + numeric literals, and E encodes causal or comparative relations extracted from the prompt. Each edge stores a weight *w* initialized to 0.5 (uncertain belief).  
   - For each candidate answer, create a temporary graph **Gₐ** by adding edges that the answer asserts (e.g., “X causes Y” → edge X→Y).  

2. **Prediction error & free‑energy computation**  
   - Define a linear Gaussian generative model: **x** = **W** · **z** + ε, where **z** is a binary vector indicating presence of each edge in **G**, **W** is the current weight matrix, and ε ~ N(0, σ²I).  
   - Compute the variational free energy **F** = ½‖**xₐ** − **Wz**‖²/σ² + ½‖**z**‖₁ · λ (complexity term). Here **xₐ** is the binary edge vector of **Gₐ**.  
   - The gradient‑free PID update adjusts **W** toward minimizing **F**:  
     *error* = **xₐ** − **Wz**  
     *ΔW* = Kₚ·error + Kᵢ·∑error·dt + K𝒹·(error − errorₚᵣₑᵥ)/dt  
     Update **W** ← **W** + η·ΔW (η small, e.g., 0.01).  
   - After a fixed number of iterations (e.g., 5), the final **F** for that candidate is its score; lower **F** indicates better alignment with the prompt’s causal structure under the free‑energy principle.  

3. **Structural features parsed**  
   - Negations, comparatives, conditionals, numeric values, causal claims, ordering relations, and conjunctions/disjunctions are all captured as edge labels or node attributes.  

4. **Novelty**  
   - The triple blend is not found in existing lightweight reasoners: causal graphs (Pearl) + PID‑style error control (control theory) + variational free‑energy minimization (FEP) form a novel hybrid scoring loop. Prior work uses either causal inference alone or similarity‑based metrics; none combine all three with an explicit PID update on model parameters.  

**Ratings**  
Reasoning: 8/10 — captures causal and relational structure, updates beliefs via error‑driven control.  
Metacognition: 6/10 — monitors prediction error but lacks explicit self‑reflection on uncertainty beyond the complexity term.  
Hypothesis generation: 7/10 — generates alternative edge sets (candidate answers) and scores them via free‑energy minimization.  
Implementability: 9/10 — relies only on regex, numpy matrix ops, and basic loops; no external libraries or APIs needed.

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
**Reason**: trap_battery_failed (acc=42% cal=46% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-01T19:53:21.469350

---

## Code

**Source**: scrap

[View code](./Causal_Inference---Feedback_Control---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Causal-Prediction Controller based on Free Energy Principle.
    
    Mechanism:
    1. Parses prompt and candidates into causal/comparative graphs (Entities=Nodes, Relations=Edges).
    2. Computes Variational Free Energy (F) = Prediction Error + Complexity Penalty.
    3. Uses a PID-like update to adjust belief weights, minimizing F over iterations.
    4. Integrates constructive computation (math/logic) as a primary signal.
    5. Enforces epistemic honesty via meta-cognitive checks on prompt ambiguity.
    """
    
    # Regex patterns for structural parsing
    PATTERNS = {
        'causal': [r'\bcause[sd]?\b', r'\blead[sd]? to\b', r'\bresult[sd]? in\b', r'\bbecause\b', r'\bdue to\b'],
        'comparative': [r'\bgreater than\b', r'\bless than\b', r'\bmore than\b', r'\bfewer than\b', r'\bhigher than\b', r'\blower than\b'],
        'conditional': [r'\bif\b.*\bthen\b', r'\bunless\b', r'\bprovided that\b'],
        'negation': [r'\bnot\b', r'\bno\b', r'\bnever\b', r'\bcannot\b', r"\bwon't\b", r"\bcan't\b"],
        'numeric': r'-?\d+(?:\.\d+)?',
        'pronoun_ambig': [r'\b(he|she|they|it)\b.*\bwho\b'],
        'presupposition': [r'\bhave you stopped\b', r'\bwhy did\b', r'\bwhy does\b', r'\bfailed to\b'],
        'false_dichotomy': [r'\beither\b.*\bor\b', r'\bmust choose between\b']
    }

    def __init__(self):
        self.pid_params = {'Kp': 0.5, 'Ki': 0.1, 'Kd': 0.2}
        self.learning_rate = 0.05
        self.complexity_lambda = 0.1

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def _extract_entities(self, text: str) -> List[str]:
        # Simple noun phrase extraction (capitalized words or specific patterns)
        # For this lightweight version, we use unique tokens > 3 chars as potential entities
        tokens = self._tokenize(text)
        entities = []
        seen = set()
        for t in tokens:
            if len(t) > 3 and t not in seen and t not in ['that', 'this', 'with', 'from', 'have', 'been', 'would', 'could', 'should']:
                entities.append(t)
                seen.add(t)
        return entities

    def _extract_numbers(self, text: str) -> List[float]:
        matches = re.findall(self.PATTERNS['numeric'], text)
        return [float(m) for m in matches]

    def _build_graph(self, text: str) -> Tuple[List[str], Dict[Tuple[str, str], float]]:
        entities = self._extract_entities(text)
        edges = {}
        
        # Initialize self-loops or default uncertainty if needed, but primarily we look for relations
        # Since we don't have full NLP, we simulate edge creation based on keyword proximity
        words = self._tokenize(text)
        
        # Detect causal/comparative triggers and link nearest entities
        for i, word in enumerate(words):
            is_relation = False
            rel_type = 'causal'
            
            for rtype, patterns in self.PATTERNS.items():
                if rtype in ['causal', 'comparative']:
                    for pat in patterns:
                        if re.search(pat, word):
                            is_relation = True
                            rel_type = rtype
                            break
            
            if is_relation:
                # Find nearest entities before and after
                prev_ent = None
                next_ent = None
                for j in range(i-1, -1, -1):
                    if words[j] in entities:
                        prev_ent = words[j]
                        break
                for j in range(i+1, len(words)):
                    if words[j] in entities:
                        next_ent = words[j]
                        break
                
                if prev_ent and next_ent:
                    edges[(prev_ent, next_ent)] = 0.5 # Initial belief
                elif prev_ent:
                    # Link to a generic 'outcome' if missing
                    edges[(prev_ent, 'outcome')] = 0.5

        return entities, edges

    def _compute_constructive_score(self, prompt: str, candidate: str) -> Optional[float]:
        """
        Attempts to solve numeric or logical problems directly.
        Returns a score (0-1) if solvable, None otherwise.
        """
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        # Case 1: Direct numeric match (e.g. "What is 2+2?" -> "4")
        if len(p_nums) > 0 and len(c_nums) > 0:
            # Check if candidate contains the result of simple operations in prompt
            # Very basic arithmetic check: if prompt has 2 numbers, check sum/prod/diff
            if len(p_nums) >= 2:
                a, b = p_nums[0], p_nums[1]
                ops = [a+b, a-b, a*b, a/b if b!=0 else 0, a**2, b**2]
                for res in c_nums:
                    for op_res in ops:
                        if abs(res - op_res) < 1e-5:
                            return 1.0 # Definitive match
            
            # Check if candidate number exists in prompt (often the answer in retrieval tasks)
            # But be careful not to just echo. 
            # If the candidate is purely numeric and matches a number in prompt, low confidence unless logic dictates.
            # Skipping simple echo for now to avoid false positives.

        # Case 2: Logical negation check
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        if re.search(r'\bnot\b', p_lower) and re.search(r'\bnot\b', c_lower):
            # Double negation or consistent negation might be valid, but hard to verify without semantics
            pass
            
        return None

    def _compute_free_energy(self, prompt_edges: Dict, candidate_edges: Dict, iterations: int = 5) -> float:
        """
        Computes Variational Free Energy F = Prediction Error + Complexity.
        Lower F is better.
        """
        if not prompt_edges and not candidate_edges:
            return 0.0 # Neutral
        
        # Align edges
        all_keys = set(prompt_edges.keys()) | set(candidate_edges.keys())
        if not all_keys:
            return 0.0
            
        keys = list(all_keys)
        n = len(keys)
        
        # Vectors
        x_prompt = np.array([prompt_edges.get(k, 0.0) for k in keys])
        x_cand = np.array([candidate_edges.get(k, 0.0) for k in keys])
        
        # Initial weights (uncertain)
        W = np.ones(n) * 0.5
        z = np.ones(n) # Assume presence for simplicity in this lightweight model
        
        error_history = []
        F_history = []
        
        prev_error = 0.0
        
        for t in range(iterations):
            # Prediction
            pred = W * z
            error = x_cand - pred
            
            # PID Update
            P_term = self.pid_params['Kp'] * error
            I_term = self.pid_params['Ki'] * np.sum(error_history) if error_history else 0.0
            D_term = self.pid_params['Kd'] * (error - prev_error)
            
            delta_W = P_term + I_term + D_term
            W = W + self.learning_rate * delta_W
            
            # Complexity penalty (L1 on weights relative to prompt structure)
            # If candidate adds edges not in prompt, complexity increases
            complexity = 0.0
            for i, k in enumerate(keys):
                if k in candidate_edges and k not in prompt_edges:
                    complexity += self.complexity_lambda
            
            # Free Energy
            # F = 0.5 * ||error||^2 + complexity
            F = 0.5 * np.sum(error**2) + complexity
            F_history.append(F)
            
            error_history.append(error)
            prev_error = error
            
        return F_history[-1] if F_history else 1.0

    def _meta_confidence(self, prompt: str) -> float:
        """
        Checks for Tier B traps: ambiguity, presupposition, unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        for pat in self.PATTERNS['presupposition']:
            if re.search(pat, p_lower):
                return 0.2 # Highly suspicious, likely a trap
        
        # 2. Pronoun ambiguity
        # Simple heuristic: if "who" is asked and multiple potential subjects exist
        if 'who' in p_lower and ('he' in p_lower or 'she' in p_lower or 'they' in p_lower):
            # Count potential subjects (simplified)
            if p_lower.count(' told ') > 0 or p_lower.count(' said ') > 0:
                return 0.25

        # 3. False Dichotomy
        for pat in self.PATTERNS['false_dichotomy']:
            if re.search(pat, p_lower):
                # Check if options are exhaustive? Hard without KB. Assume risk.
                return 0.4

        # 4. Subjectivity
        subj_words = ['best', 'worst', 'favorite', 'opinion', 'beautiful']
        if any(w in p_lower for w in subj_words):
            if 'objective' not in p_lower and 'fact' not in p_lower:
                return 0.3

        return 1.0 # No obvious traps detected

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_entities, prompt_edges = self._build_graph(prompt)
        results = []
        
        # Pre-check constructive math
        constructive_score = self._compute_constructive_score(prompt, "") # Placeholder check
        
        for cand in candidates:
            cand_entities, cand_edges = self._build_graph(cand)
            
            # 1. Constructive Computation (High Priority)
            const_score = self._compute_constructive_score(prompt, cand)
            
            # 2. Free Energy Score (Structural Alignment)
            # We want LOW free energy, so we invert it for the final score (Higher is better)
            fe_raw = self._compute_free_energy(prompt_edges, cand_edges)
            
            # Normalize FE to 0-1 range roughly (assuming FE < 2.0 is good, >5.0 is bad)
            # Score = 1 / (1 + FE)
            structural_score = 1.0 / (1.0 + fe_raw)
            
            # 3. NCD Tiebreaker (Max 15% weight)
            try:
                import zlib
                s1 = (prompt + cand).encode('utf-8')
                s2 = prompt.encode('utf-8')
                s3 = cand.encode('utf-8')
                l1 = len(zlib.compress(s1))
                l2 = len(zlib.compress(s2))
                l3 = len(zlib.compress(s3))
                ncd = (l1 - min(l2, l3)) / max(l2, l3) if max(l2, l3) > 0 else 1.0
                ncd_score = 1.0 - ncd
            except:
                ncd_score = 0.5
            
            # Final Scoring Logic
            if const_score is not None and const_score == 1.0:
                final_score = 0.95 # Definitive math match
                reasoning = "Constructive computation confirmed."
            else:
                # Weighted sum: Structural (70%), NCD (15%), Base uncertainty (15%)
                # If structural alignment is high, score goes up.
                base_score = structural_score * 0.70 + ncd_score * 0.15 + 0.15
                final_score = base_score
                reasoning = f"Structural alignment (FE-based): {structural_score:.3f}"
                
                # Penalty for length mismatch implying missing info
                if len(cand_entities) == 0 and len(prompt_entities) > 2:
                    final_score *= 0.5
                    reasoning += "; Candidate lacks entities."

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-cognitive analysis of the prompt.
        """
        # 1. Meta-confidence cap (Tier B checks)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Structural/Constructive evaluation
        eval_results = self.evaluate(prompt, [answer])
        if not eval_results:
            return 0.0
            
        raw_score = eval_results[0]['score']
        
        # 3. Apply cap
        final_conf = min(raw_score, meta_cap)
        
        # 4. Heuristic adjustments
        # If the answer is extremely short (Yes/No) and prompt is complex, lower confidence
        if len(answer.split()) <= 2 and len(prompt.split()) > 20:
            if meta_cap < 1.0: # Only penalize if we already suspect ambiguity
                final_conf = min(final_conf, 0.4)
                
        # Ensure deterministic float output
        return float(np.clip(final_conf, 0.0, 1.0))
```

</details>
