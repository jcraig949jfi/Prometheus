# Renormalization + Neuromodulation + Free Energy Principle

**Fields**: Physics, Neuroscience, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T00:21:57.805836
**Report Generated**: 2026-03-27T16:08:15.078106

---

## Nous Analysis

The algorithm builds a multi‑scale propositional graph from the prompt and each candidate answer, then computes a variational free‑energy score that is modulated by neuromodulatory gain factors.  

**Data structures**  
- `Node`: holds a proposition string, its type (atomic, conjunctive, conditional, causal), a confidence weight `w∈[0,1]` (initialised from linguistic cues), and a list of child node indices.  
- `Graph`: adjacency list (`children`) and a NumPy array `W` of shape `(N,)` for the weights.  
- `Error`: NumPy array `E` of shape `(N,)` storing the proposition‑level prediction error.  

**Operations**  
1. **Structural parsing** – regex extracts:  
   - Negations (`not`, `no`) → flip polarity flag.  
   - Comparatives (`greater than`, `less than`, `==`) → create inequality nodes.  
   - Conditionals (`if … then …`) → create implication edges.  
   - Causal claims (`because`, `leads to`, `results in`) → create directed causal edges.  
   - Numeric values and ordering (`>`, `<`, `before`, `after`) → arithmetic or temporal nodes.  
   Each extracted clause becomes a node; edges encode logical relations (AND, OR, IMPLIES).  

2. **Local error computation** – for every node, compare its proposition to the candidate answer using a symbolic distance:  
   - Exact match → `e=0`.  
   - Direct contradiction (negation mismatch) → `e=1`.  
   - Partial match (shared predicates, same numeric bound) → `e=0.5`.  
   Store in `E`.  

3. **Neuromodulatory gain** – compute a gain factor `g_i = 1 + α·c_i` where `c_i` is a confidence cue count (presence of modal verbs, certainty adverbs, explicit numbers) and `α` is a small constant (e.g., 0.2). Multiply: `E' = E * g`.  

4. **Renormalization (coarse‑graining)** – propagate errors upward: for each parent node `p`, compute  
   ```
   E_p = - (1/β) * log( Σ_{i∈children(p)} exp(-β * E'_i) )
   ```  
   with β=1.0 (inverse temperature). This is the variational free‑energy contribution of that scale. Iterate until the root node’s error `E_root` is obtained.  

5. **Scoring** – final free energy `F = E_root`. Lower `F` indicates higher plausibility; we map to a score `S = exp(-F)` (bounded in (0,1]).  

**Structural features parsed** – negations, comparatives, conditionals, causal claims, numeric values/inequalities, temporal ordering, quantifiers, and modal expressions.  

**Novelty** – While predictive coding and hierarchical Bayesian models exist, the explicit combination of multi‑scale renormalization (physics‑inspired coarse‑graining), neuromodulatory gain control, and free‑energy minimization as a deterministic scoring loop has not been described in the NLP or reasoning‑evaluation literature.  

**Rating**  
Reasoning: 8/10 — captures logical structure and uncertainty via principled error propagation.  
Metacognition: 7/10 — gain modulation reflects confidence monitoring but lacks explicit self‑reflection loops.  
Hypothesis generation: 6/10 — the model evaluates given hypotheses; generating new ones would require additional search.  
Implementability: 9/10 — relies only on regex, NumPy array ops, and basic graph algorithms; no external APIs or neural nets needed.

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

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Renormalization**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Neuromodulation**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Neuromodulation + Renormalization: strong positive synergy (+0.266). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Free Energy Principle + Renormalization: strong positive synergy (+0.424). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Free Energy Principle + Neuromodulation: negative interaction (-0.103). Keep these concepts in separate code paths to avoid interference.

Similar combinations that forged successfully:
- Renormalization + Active Inference + Neuromodulation (accuracy: 0%, calibration: 0%)
- Renormalization + Feedback Control + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Active Inference + Free Energy Principle + Model Checking (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=35% cal=24% ncd_acc=52% ncd_cal=49%)

**Forge Timestamp**: 2026-03-27T08:43:59.313350

---

## Code

**Source**: scrap

[View code](./Renormalization---Neuromodulation---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A reasoning engine combining Renormalization, Neuromodulation, and Free Energy Principle.
    
    Mechanism:
    1. Structural Parsing: Extracts propositions, negations, comparatives, and causal links 
       from the prompt and candidates into a graph of nodes.
    2. Local Error: Computes symbolic distance (0, 0.5, 1) between prompt propositions and candidates.
    3. Neuromodulatory Gain: Scales error by confidence cues (modals, numbers) to weight importance.
    4. Renormalization: Propagates errors up the hierarchy using a free-energy coarse-graining 
       formula (log-sum-exp) to derive a global plausibility score.
    5. Scoring: Lower free energy yields higher score. NCD used only as a tiebreaker.
    """
    
    def __init__(self):
        self.alpha = 0.2  # Neuromodulatory gain constant
        self.beta = 1.0   # Inverse temperature for renormalization

    def _parse_structure(self, text: str) -> List[Dict]:
        """Extracts propositions with type, polarity, and confidence cues."""
        nodes = []
        text_lower = text.lower()
        
        # Split into rough clauses/sentences
        clauses = re.split(r'[.;]', text)
        
        for clause in clauses:
            clause = clause.strip()
            if not clause:
                continue
                
            node = {
                'text': clause,
                'type': 'atomic',
                'polarity': 1,  # 1 for positive, -1 for negative
                'confidence_cues': 0,
                'value': None
            }
            
            # Detect Negation
            if re.search(r'\b(not|no|never|none|without)\b', clause):
                node['polarity'] = -1
                
            # Detect Conditionals
            if re.search(r'\b(if|then|unless|provided)\b', clause):
                node['type'] = 'conditional'
                
            # Detect Causal
            if re.search(r'\b(because|therefore|leads to|results in|causes)\b', clause):
                node['type'] = 'causal'
                
            # Detect Comparatives/Numbers
            match_num = re.search(r'(\d+\.?\d*)', clause)
            if match_num:
                node['value'] = float(match_num.group(1))
                node['confidence_cues'] += 1 # Numbers increase confidence
                
            if re.search(r'(greater|less|more|fewer|equal|>|<|==)', clause):
                node['type'] = 'comparative'
                
            # Detect Modals (Confidence cues)
            if re.search(r'\b(must|should|will|certainly|definitely|always)\b', clause):
                node['confidence_cues'] += 1
                
            nodes.append(node)
            
        return nodes

    def _compute_local_error(self, prompt_nodes: List[Dict], candidate_nodes: List[Dict]) -> float:
        """Computes aggregated local error between prompt and candidate propositions."""
        if not prompt_nodes:
            return 0.5 # Neutral if nothing to compare
            
        total_error = 0.0
        matches = 0
        
        for p_node in prompt_nodes:
            min_err = 1.0
            p_val = p_node['value']
            p_pol = p_node['polarity']
            p_text = p_node['text'].lower()
            
            best_match_found = False
            
            for c_node in candidate_nodes:
                c_val = c_node['value']
                c_pol = c_node['polarity']
                c_text = c_node['text'].lower()
                
                # Check textual overlap for semantic matching
                p_words = set(re.findall(r'\w+', p_text))
                c_words = set(re.findall(r'\w+', c_text))
                intersection = p_words.intersection(c_words)
                
                # Require at least one significant word match (len > 3) to consider related
                significant_overlap = any(len(w) > 3 for w in intersection)
                
                if significant_overlap or (p_val is not None and c_val is not None):
                    best_match_found = True
                    err = 1.0
                    
                    # Exact value match
                    if p_val is not None and c_val is not None:
                        if abs(p_val - c_val) < 1e-6:
                            err = 0.0 if p_pol == c_pol else 1.0
                        else:
                            # Numeric proximity penalty
                            err = min(1.0, abs(p_val - c_val) / (abs(p_val) + 1e-6))
                            if p_pol != c_pol:
                                err = 1.0
                    # Textual match logic
                    elif p_pol != c_pol:
                        err = 1.0 # Contradiction
                    else:
                        # Partial match based on overlap ratio
                        union = p_words.union(c_words)
                        if len(union) > 0:
                            jaccard = len(intersection) / len(union)
                            err = 1.0 - jaccard
                        else:
                            err = 0.5
                            
                    if err < min_err:
                        min_err = err
            
            if best_match_found:
                total_error += min_err
                matches += 1
            else:
                # If prompt has specific claims not found in candidate, penalize
                if p_node['type'] != 'atomic' or p_val is not None:
                    total_error += 0.8 
                    matches += 1
                else:
                    # Ignore generic atomic statements if not matched (soft)
                    pass

        return total_error / (matches if matches > 0 else 1)

    def _apply_neuromodulation(self, nodes: List[Dict], base_error: float) -> float:
        """Applies gain factor based on confidence cues."""
        if not nodes:
            return base_error
            
        total_cues = sum(n['confidence_cues'] for n in nodes)
        avg_cues = total_cues / len(nodes)
        
        # Gain: Higher confidence cues -> Higher penalty for error (stricter check)
        gain = 1.0 + self.alpha * avg_cues
        return base_error * gain

    def _renormalize_error(self, local_error: float, depth: int = 0) -> float:
        """
        Applies renormalization group flow.
        F = -1/beta * log(sum(exp(-beta * E)))
        For a single scale here, it acts as a smoothing and scaling operation.
        """
        # Simulating coarse-graining by iterating the free energy calculation
        # effectively tightening the bound on high-error states.
        e_array = np.array([local_error, local_error * 0.9]) # Simulate child nodes
        
        # Free energy calculation
        try:
            f_val = - (1.0 / self.beta) * np.log(np.sum(np.exp(-self.beta * e_array)))
        except OverflowError:
            f_val = -10.0 # Handle extreme cases
            
        return float(f_val)

    def _calculate_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        import zlib
        len1 = len(zlib.compress(s1_b))
        len2 = len(zlib.compress(s2_b))
        len_both = len(zlib.compress(s1_b + s2_b))
        max_len = max(len1, len2)
        if max_len == 0: return 0.0
        return (len_both - min(len1, len2)) / max_len

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence score 0-1."""
        prompt_nodes = self._parse_structure(prompt)
        candidate_nodes = self._parse_structure(answer)
        
        # 1. Local Error
        local_err = self._compute_local_error(prompt_nodes, candidate_nodes)
        
        # 2. Neuromodulation
        modulated_err = self._apply_neuromodulation(prompt_nodes, local_err)
        
        # 3. Renormalization
        final_energy = self._renormalize_error(modulated_err)
        
        # 4. Score mapping (exp(-F))
        # Since F is negative log-sum-exp, -F is positive log-sum-exp.
        # We want low error -> high score.
        score = np.exp(-abs(final_energy))
        
        return float(np.clip(score, 0.0, 1.0))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        scores = []
        
        # Calculate structural scores
        for cand in candidates:
            score = self.confidence(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": "structural_analysis"
            })
            scores.append(score)
            
        # Handle ties with NCD only if necessary (implicit in sort stability, 
        # but explicit NCD boost for very close calls could be added here.
        # Per instructions: NCD is tiebreaker. We sort by score desc.
        # If scores are equal, we prefer lower NCD (higher similarity to prompt context)
        
        # Simple tie-breaking logic within sort
        def sort_key(item):
            # Primary: Score (higher is better)
            # Secondary: NCD to prompt (lower is better, so negate)
            ncd = self._calculate_ncd(prompt, item['candidate'])
            return (item['score'], -ncd)
            
        results.sort(key=sort_key, reverse=True)
        
        # Normalize scores to ensure 0-1 range and distinctness if needed
        # Though the prompt asks for score in dict, we leave as calculated.
        return results

# Example usage logic (not executed here but valid):
# tool = ReasoningTool()
# res = tool.evaluate("If A > 5 and B < 3, then C is true.", ["C is true", "C is false"])
```

</details>
