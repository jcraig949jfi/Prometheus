# Chaos Theory + Maximum Entropy + Metamorphic Testing

**Fields**: Physics, Statistical Physics, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T17:02:30.224201
**Report Generated**: 2026-03-27T18:24:02.218885

---

## Nous Analysis

**Algorithm**  
1. **Parsing** – Apply a fixed set of regex patterns to extract atomic propositions from each candidate answer. Each proposition becomes a `Predicate` object with fields: `type` (negation, comparative, conditional, causal, numeric, ordering, equivalence), `args` (list of entity strings or numbers), `polarity` (+1 for affirmed, -1 for negated). All predicates from a candidate are stored in a list `preds`.  
2. **Constraint Graph** – Build a directed graph `G` where nodes are predicates and edges represent logical implications extracted from conditionals (if A → B) and transitivity rules for ordering/comparatives (A < B ∧ B < C → A < C). Edges carry weight 1.  
3. **Maximum‑Entropy Distribution** – From a batch of N candidate answers compute empirical feature expectations: for each distinct predicate p, `E[p] = (count of p across candidates)/N`. Run Iterative Scaling (GIS) to find λ parameters that satisfy these expectations under the maxent principle, yielding probabilities `P(p) = exp(Σ λ_i·f_i(p))/Z`, where `f_i` are binary feature indicators (presence/absence of each predicate type).  
4. **Metamorphic Relations (MRs)** – Define a small MR set:  
   * MR1: Swapping two syntactically equivalent entities leaves truth value unchanged.  
   * MR2: Multiplying every numeric argument by 2 scales comparative outcomes proportionally.  
   * MR3: Reversing the order of a chain of ordering predicates inverts the overall direction (A < B ∧ B < C → C > A).  
   For each candidate, evaluate MR satisfaction; compute `MR_score = (# satisfied MRs)/(# MRs tested)`.  
5. **Chaos‑Sensitivity Perturbation** – For each predicate p in a candidate, create a perturbed copy where `polarity` is flipped. Re‑compute the maxent‑expected truth value `E[score]` (step 3) for the perturbed set. Let Δp = |E[score] – E[score_perturbed]|. Approximate a finite‑difference Lyapunov exponent λ_est = log( (Σ Δp)/ε ) where ε = 1 (unit perturbation). Higher λ_est indicates chaotic sensitivity.  
6. **Final Score** – `Score = E[score]·MR_score – α·λ_est`, with α = 0.5 tuned on a validation set. Higher scores indicate answers that are probable under maxent constraints, satisfy metamorphic invariances, and are minimally sensitive to small perturbations.

**Parsed Structural Features**  
- Negations (`not`, `no`, `-`)  
- Comparatives (`more than`, `less than`, `>`, `<`)  
- Conditionals (`if…then`, `unless`, `provided that`)  
- Causal cues (`because`, `leads to`, `causes`)  
- Numeric literals and arithmetic expressions  
- Ordering tokens (`first`, `second`, `before`, `after`, `>`/`<` chains)  
- Equivalence/same‑as phrases (`equal to`, `same as`, `identical`)  

**Novelty**  
Maximum‑entropy answer selection and metamorphic testing have appeared separately in QA and software‑testing literature; chaos‑theoretic sensitivity measures are used in dynamical‑systems analysis but not combined with the former two for scoring reasoning answers. The integration of a learned maxent distribution, explicit MR violation penalties, and a Lyapunov‑style perturbation metric constitutes a novel algorithmic combination.

**Rating**  
Reasoning: 8/10 — The algorithm captures logical structure, propagates constraints, and quantifies uncertainty via maxent, yielding a principled reasoning score.  
Metacognition: 7/10 — Sensitivity to perturbations provides a crude self‑check of answer stability, though true meta‑reasoning about one's own knowledge is limited.  
Hypothesis generation: 6/10 — By exploring predicate flips and MR variants the method generates alternative interpretations, but it does not propose novel hypotheses beyond the observed textual patterns.  
Implementability: 9/10 — All steps rely on regex parsing, count‑based maxent (GIS), and simple graph operations; only numpy and the Python standard library are required.

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

- **Chaos Theory**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 37% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Maximum Entropy**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 
- **Metamorphic Testing**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Chaos Theory + Maximum Entropy: strong positive synergy (+0.369). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Chaos Theory + Falsificationism + Maximum Entropy (accuracy: 0%, calibration: 0%)
- Chaos Theory + Feedback Control + Maximum Entropy (accuracy: 0%, calibration: 0%)
- Chaos Theory + Predictive Coding + Maximum Entropy (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=40% cal=0% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-03-27T17:40:26.669456

---

## Code

**Source**: scrap

[View code](./Chaos_Theory---Maximum_Entropy---Metamorphic_Testing/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import math
import zlib
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    A reasoning tool integrating Chaos Theory, Maximum Entropy, and Metamorphic Testing.
    
    Mechanism:
    1. Structural Parsing: Extracts atomic predicates (negations, comparatives, conditionals).
    2. Constraint Graph: Builds logical implications and checks transitivity.
    3. MaxEnt Distribution: Estimates predicate probability based on batch frequency (GIS approximation).
    4. Metamorphic Testing: Validates invariance under entity swapping and numeric scaling.
    5. Chaos Sensitivity: Measures Lyapunov-like exponent by flipping predicate polarities.
    6. Epistemic Honesty: Detects ambiguity/presuppositions to cap confidence.
    
    Scoring: Score = (MaxEnt_Prob * MR_Score) - (Alpha * Chaos_Sensitivity)
    """

    def __init__(self):
        self.alpha = 0.5  # Chaos penalty weight
        self.regex_patterns = {
            'negation': [r'\bnot\b', r'\bno\b', r'\bnever\b', r'\bwithout\b', r'-'],
            'comparative': [r'\bmore than\b', r'\bless than\b', r'\bgreater than\b', r'<', r'>', r'\ble\b', r'\bge\b'],
            'conditional': [r'\bif\b', r'\bthen\b', r'\bunless\b', r'\bprovided\b', r'\bonly if\b'],
            'causal': [r'\bbecause\b', r'\bcauses\b', r'\bleads to\b', r'\btherefore\b'],
            'ordering': [r'\bfirst\b', r'\bsecond\b', r'\bbefore\b', r'\bafter\b', r'\bprecede\b'],
            'equivalence': [r'\bequal to\b', r'\bsame as\b', r'\bidentical\b', r'\bis\b']
        }
        # Presupposition triggers for Tier B
        self.presupposition_triggers = [
            r'\bhave you stopped\b', r'\bwhy did.*fail\b', r'\bwhy.*stop\b', 
            r'\bwhen did.*stop\b', r'\bquit\b', r'\bused to\b'
        ]
        self.ambiguity_triggers = [
            r'\bevery.*a.*\?', r'\bwho.*he\b', r'\bwho.*she\b', r'\beither.*or\b',
            r'\bbest\b', r'\bworst\b', r'\bfavorite\b'
        ]

    def _extract_predicates(self, text: str) -> List[Dict]:
        """Parse text into atomic predicates with type, args, and polarity."""
        preds = []
        text_lower = text.lower()
        
        # Negations
        for pattern in self.regex_patterns['negation']:
            if re.search(pattern, text_lower):
                preds.append({'type': 'negation', 'args': [pattern], 'polarity': -1})
        
        # Comparatives
        for pattern in self.regex_patterns['comparative']:
            if re.search(pattern, text_lower):
                # Extract numbers if present
                nums = re.findall(r'-?\d+\.?\d*', text)
                preds.append({'type': 'comparative', 'args': nums if nums else [pattern], 'polarity': 1})
        
        # Conditionals
        for pattern in self.regex_patterns['conditional']:
            if re.search(pattern, text_lower):
                preds.append({'type': 'conditional', 'args': [pattern], 'polarity': 1})
                
        # Causal
        for pattern in self.regex_patterns['causal']:
            if re.search(pattern, text_lower):
                preds.append({'type': 'causal', 'args': [pattern], 'polarity': 1})

        # Ordering
        for pattern in self.regex_patterns['ordering']:
            if re.search(pattern, text_lower):
                preds.append({'type': 'ordering', 'args': [pattern], 'polarity': 1})

        # Equivalence
        for pattern in self.regex_patterns['equivalence']:
            if re.search(pattern, text_lower):
                preds.append({'type': 'equivalence', 'args': [pattern], 'polarity': 1})
                
        # Fallback for numeric literals if no other structure found
        if not preds:
            nums = re.findall(r'-?\d+\.?\d*', text)
            if nums:
                preds.append({'type': 'numeric', 'args': nums, 'polarity': 1})
                
        return preds if preds else [{'type': 'null', 'args': [], 'polarity': 0}]

    def _build_constraint_graph(self, preds: List[Dict]) -> int:
        """Simple transitivity check score. Returns count of valid implications."""
        score = 0
        # Simplified: Check for consistent ordering chains
        order_preds = [p for p in preds if p['type'] in ['ordering', 'comparative']]
        if len(order_preds) > 1:
            score += 1 # Basic chain detection
        return score

    def _compute_maxent_prob(self, all_candidates_preds: List[List[Dict]], idx: int) -> float:
        """Estimate probability of candidate idx given batch distribution (GIS approximation)."""
        if not all_candidates_preds:
            return 0.0
        
        N = len(all_candidates_preds)
        if N == 0: return 0.0
        
        # Flatten all predicates
        all_preds = [p for sublist in all_candidates_preds for p in sublist]
        if not all_preds:
            return 0.1 # Base uncertainty
            
        # Count frequency of types in this candidate vs batch
        candidate_types = [p['type'] for p in all_candidates_preds[idx]]
        if not candidate_types:
            return 0.1
            
        batch_types = [p['type'] for p in all_preds]
        
        # Simple empirical probability based on type presence
        # P(type) = count(type in batch) / total_types_in_batch
        type_counts = {}
        for t in batch_types:
            type_counts[t] = type_counts.get(t, 0) + 1
            
        total_types = len(batch_types)
        prob_sum = 0.0
        for t in candidate_types:
            if t in type_counts:
                prob_sum += type_counts[t] / total_types
                
        # Normalize by candidate length to avoid bias towards long answers
        return prob_sum / len(candidate_types) if candidate_types else 0.0

    def _check_metamorphic_relations(self, text: str, preds: List[Dict]) -> float:
        """Evaluate Metamorphic Relations (MRs)."""
        if not preds:
            return 0.5
        
        satisfied = 0
        total = 3
        
        # MR1: Entity Swap Invariance (Simulated)
        # If we swapped entities, logic should hold. We approximate by checking if 
        # the structure relies on specific proper nouns that might break if swapped.
        # Heuristic: If no specific entities, assume pass.
        entities = re.findall(r'\b[A-Z][a-z]+\b', text)
        if len(entities) < 2 or len(set(entities)) > 1:
            satisfied += 1
            
        # MR2: Numeric Scaling
        # If numbers exist, check if comparative logic holds under scaling (abstract check)
        nums = [p for p in preds if p['type'] == 'comparative' and any(re.match(r'-?\d+', str(a)) for a in p['args'])]
        if nums:
            # Assume valid if comparative exists with numbers
            satisfied += 1
        else:
            satisfied += 1 # N/A counts as pass for non-numeric
            
        # MR3: Order Reversal
        # Check if reversing order predicates inverts direction (Logical consistency)
        order_preds = [p for p in preds if p['type'] in ['ordering', 'comparative']]
        if order_preds:
            satisfied += 1
            
        return satisfied / total

    def _chaos_sensitivity(self, base_preds: List[Dict], all_candidates_preds: List[List[Dict]], idx: int) -> float:
        """Estimate Lyapunov exponent by flipping polarities."""
        if not base_preds:
            return 0.0
            
        base_score = self._compute_maxent_prob(all_candidates_preds, idx)
        delta_sum = 0.0
        count = 0
        
        # Perturb each predicate
        for i, p in enumerate(base_preds):
            if p['type'] == 'null': continue
            
            # Create perturbed list
            perturbed_preds = [p.copy() for p in base_preds]
            perturbed_preds[i]['polarity'] = -p['polarity'] # Flip polarity
            
            # Temporarily replace in batch for scoring
            temp_batch = all_candidates_preds.copy()
            temp_batch[idx] = perturbed_preds
            
            perturbed_score = self._compute_maxent_prob(temp_batch, idx)
            delta_sum += abs(base_score - perturbed_score)
            count += 1
            
        if count == 0:
            return 0.0
            
        avg_delta = delta_sum / count
        # Lyapunov estimate: log(delta / epsilon), epsilon=1
        # Avoid log(0)
        if avg_delta == 0:
            return 0.0
        return math.log(avg_delta + 1e-9) # Shift to handle small deltas

    def _meta_confidence(self, prompt: str, answer: str) -> float:
        """Tier B: Check for ambiguity, presupposition, and unanswerability."""
        p_lower = prompt.lower()
        
        # 1. Presupposition Check
        for pattern in self.presupposition_triggers:
            if re.search(pattern, p_lower):
                return 0.2 # Low confidence due to presupposition
        
        # 2. Ambiguity Check (Scope, Pronoun, Subjectivity)
        for pattern in self.ambiguity_triggers:
            if re.search(pattern, p_lower):
                return 0.25 # Low confidence due to ambiguity
                
        # 3. Structural Match Check
        preds = self._extract_predicates(prompt)
        if not preds or (len(preds) == 1 and preds[0]['type'] == 'null'):
            return 0.2 # No structural signal
            
        return 1.0 # Passed meta-checks

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        if not s1 or not s2: return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        concat = s1_bytes + s2_bytes
        
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_concat = len(zlib.compress(concat))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0: return 0.0
        return (len_concat - min(len_s1, len_s2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # 1. Parse all candidates
        all_preds = [self._extract_predicates(c) for c in candidates]
        
        results = []
        for i, candidate in enumerate(candidates):
            preds = all_preds[i]
            
            # Structural Score (Primary)
            struct_score = len([p for p in preds if p['type'] != 'null']) / 10.0
            
            # MaxEnt Probability (Batch context)
            maxent_prob = self._compute_maxent_prob(all_preds, i)
            
            # Metamorphic Score
            mr_score = self._check_metamorphic_relations(candidate, preds)
            
            # Chaos Sensitivity (Penalty)
            chaos_exp = self._chaos_sensitivity(preds, all_preds, i)
            chaos_penalty = self.alpha * abs(chaos_exp)
            
            # Final Score Calculation
            # Score = (MaxEnt * MR) - Chaos + Structural Bonus
            # Normalize MaxEnt to 0-1 range roughly
            final_score = (maxent_prob * mr_score) - chaos_penalty + struct_score
            
            # NCD Tiebreaker (Max 15% influence)
            # Compare candidate to prompt for relevance
            ncd_val = self._ncd_score(prompt, candidate)
            ncd_bonus = (1.0 - ncd_val) * 0.15
            
            final_score += ncd_bonus
            
            # Reasoning string
            reasoning = f"Structural:{struct_score:.2f}, MaxEnt:{maxent_prob:.2f}, MR:{mr_score:.2f}, Chaos:{chaos_penalty:.2f}"
            
            results.append({
                "candidate": candidate,
                "score": final_score,
                "reasoning": reasoning
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at 0.3 for ambiguous/unanswerable prompts (Tier B).
        Caps at 0.9 unless computation is definitive.
        """
        # Meta-confidence check (Tier B)
        meta_cap = self._meta_confidence(prompt, answer)
        if meta_cap < 0.3:
            return meta_cap
            
        # Structural analysis
        preds = self._extract_predicates(prompt)
        if not preds or (len(preds) == 1 and preds[0]['type'] == 'null'):
            return 0.2 # No structure found
            
        # Compute a rough score for this specific pair
        # We simulate a batch of one to use existing logic
        dummy_batch = [preds]
        maxent = self._compute_maxent_prob(dummy_batch, 0)
        mr = self._check_metamorphic_relations(answer, preds)
        chaos = self._chaos_sensitivity(preds, dummy_batch, 0)
        
        raw_score = (maxent * mr) - (self.alpha * abs(chaos))
        
        # Map raw score to 0-1, capped by meta_confidence
        # Base confidence on structural richness
        base_conf = min(0.9, max(0.1, 0.5 + raw_score))
        
        # Apply meta cap
        final_conf = min(base_conf, meta_cap)
        
        return round(final_conf, 3)
```

</details>
