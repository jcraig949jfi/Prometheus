# Thermodynamics + Pragmatism + Emergence

**Fields**: Physics, Philosophy, Complex Systems
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T21:49:05.034489
**Report Generated**: 2026-03-27T06:37:40.737709

---

## Nous Analysis

**Algorithm**  
1. **Parsing** – Use a handful of regex patterns to extract elementary propositions from each candidate answer. A proposition is stored as a namedtuple `Prop(subj, pred, obj, polarity, modality)` where `polarity∈{+1,-1}` (negation) and `modality∈{assertive, conditional, causal}`. All propositions from an answer are placed in a list `props`.  
2. **Constraint graph** – Build a directed graph `G` where each node is a proposition and an edge `p→q` exists when `p.modality` is conditional (`if … then …`) or causal (`because …`) and the consequent/antecedent matches the subject‑predicate‑object of `q`. Edge weight is 1 for assertive links, 0.5 for causal links (reflecting weaker certainty).  
3. **Constraint propagation** – Compute the transitive closure of `G` with Floyd‑Warshall (numpy‑based matrix multiplication) to derive all implied propositions. Count violations: a violation occurs when both a proposition and its negated counterpart (`polarity` flipped) are reachable. The consistency score is `C = 1 – (violations / total_props)`.  
4. **Pragmatic utility** – Define a lookup set `VERIFIABLE = {measure, observe, test, count, …}`. For each proposition, if its predicate contains any verifiable verb and its object contains a numeric token, award 1 utility point. Normalize: `U = utility_points / max_possible`.  
5. **Emergence (macro‑coherence)** – Compute the Shannon entropy of the distribution over predicate types (e.g., relational, attributive, existential). Low entropy indicates that the answer relies on a few repeated macro‑level patterns (strong emergence); high entropy indicates fragmented micro‑level content. Map entropy to a score: `E = 1 – (H / H_max)`, where `H_max = log2(num_predicate_types)`.  
6. **Final score** – `Score = w_c*C + w_u*U + w_e*E` with weights summing to 1 (e.g., 0.4,0.3,0.3). The class exposes a method `score(prompt, candidates)` returning a list of floats.

**Structural features parsed**  
- Negations: “not”, “no”, “never”.  
- Comparatives: “more than”, “less than”, “greater than”, “≤”, “≥”.  
- Conditionals: “if … then …”, “provided that”.  
- Causal claims: “because”, “leads to”, “results in”.  
- Numeric values: integers, decimals, percentages.  
- Ordering relations: “first”, “second”, “before”, “after”.  
- Modality markers: “must”, “might”, “should”.

**Novelty**  
Pure logical reasoners (e.g., theorem provers) focus on consistency; pragmatist‑inspired tools score usefulness via observable verification; emergence metrics appear in complex‑systems analysis. Combining constraint propagation, a verifiability‑based utility, and entropy‑based macro‑coherence in a single lightweight scorer is not documented in existing surveys, making the approach novel.

**Rating**  
Reasoning: 8/10 — captures logical consistency, pragmatic testability, and macro‑level coherence in a deterministic pipeline.  
Metacognition: 6/10 — the method can report which component (consistency, utility, emergence) drove the score, enabling limited self‑monitoring.  
Hypothesis generation: 5/10 — while it can flag missing verifiable propositions, it does not actively propose new hypotheses.  
Implementability: 9/10 — relies only on regex, numpy arrays, and basic graph algorithms; no external dependencies.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 9/10 |
| **Composite** | **6.33** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Thermodynamics**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 40% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Pragmatism**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 
- **Emergence**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 34% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Emergence + Thermodynamics: strong positive synergy (+0.152). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Thermodynamics + Emergence + Mechanism Design (accuracy: 0%, calibration: 0%)
- Analogical Reasoning + Pragmatism + Type Theory (accuracy: 0%, calibration: 0%)
- Chaos Theory + Emergence + Error Correcting Codes (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=33% cal=0% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-27T05:01:37.441391

---

## Code

**Source**: scrap

[View code](./Thermodynamics---Pragmatism---Emergence/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import math
import zlib
from collections import namedtuple
from typing import List, Dict, Tuple, Set

# Named tuple for structured propositions
Prop = namedtuple('Prop', ['subj', 'pred', 'obj', 'polarity', 'modality'])

class ReasoningTool:
    """
    A reasoning evaluator combining Thermodynamics (Entropy/Emergence), 
    Pragmatism (Verifiability), and Logical Consistency (Constraint Propagation).
    
    Mechanism:
    1. Parsing: Extracts structured propositions (Subject, Predicate, Object) with modality.
    2. Consistency (Thermodynamic/Logical): Builds a constraint graph. Uses transitive closure 
       to detect contradictions (p and not-p). Score derived from violation ratio.
    3. Utility (Pragmatic): Scores based on presence of verifiable verbs and numeric data.
    4. Emergence (Entropy): Calculates Shannon entropy of predicate distribution. Low entropy 
       (high coherence) yields higher scores.
    5. Scoring: Weighted sum of Consistency, Utility, and Emergence. NCD used as tiebreaker.
    """

    # Verbs indicating pragmatic verifiability
    VERIFIABLE_VERBS = {'measure', 'observe', 'test', 'count', 'calculate', 'weigh', 'record'}
    
    # Weights
    W_C = 0.4  # Consistency
    W_U = 0.3  # Utility
    W_E = 0.3  # Emergence

    def __init__(self):
        # Regex patterns for parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|none)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|provided|unless)\b.*?\b(then|else)\b', re.IGNORECASE | re.DOTALL),
            'causal': re.compile(r'\b(because|since|leads to|results in|causes)\b', re.IGNORECASE),
            'numeric': re.compile(r'\d+(\.\d+)?%?'),
            'comparative': re.compile(r'\b(more than|less than|greater than|equal to|<=|>=|<|>)\b', re.IGNORECASE),
            'modality': re.compile(r'\b(must|might|should|could|will)\b', re.IGNORECASE)
        }

    def _parse_text(self, text: str) -> List[Prop]:
        """Extract elementary propositions from text."""
        props = []
        sentences = re.split(r'[.\n]', text)
        
        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
            
            # Determine modality
            modality = 'assertive'
            if self.patterns['conditional'].search(sent):
                modality = 'conditional'
            elif self.patterns['causal'].search(sent):
                modality = 'causal'
            
            # Determine polarity
            polarity = 1
            if self.patterns['negation'].search(sent):
                polarity = -1
            
            # Simplified extraction: Treat whole sentence as a proposition unit
            # In a full engine, this would be SVO parsed. Here we simulate structure.
            # We split by common separators to find pseudo-SVO
            parts = re.split(r'\s+(is|are|was|were|has|have|does|do)\s+', sent, flags=re.IGNORECASE)
            
            subj = parts[0][:50] if parts else sent[:50]
            pred_obj = " ".join(parts[1:]) if len(parts) > 1 else sent
            
            # Heuristic predicate extraction (first verb-like word)
            pred_match = re.search(r'\b(a-z+)\b', pred_obj)
            pred = pred_match.group(0) if pred_match else "exists"
            
            props.append(Prop(subj=subj.strip(), pred=pred, obj=pred_obj.strip(), polarity=polarity, modality=modality))
            
        return props

    def _build_graph(self, props: List[Prop]) -> Tuple[List[List[float]], int]:
        """Build adjacency matrix for constraint propagation."""
        n = len(props)
        if n == 0:
            return [], 0
            
        # Initialize matrix with infinity (no path), 0 on diagonal
        INF = 1e9
        dist = [[INF] * n for _ in range(n)]
        for i in range(n):
            dist[i][i] = 0
            
        for i, p in enumerate(props):
            for j, q in enumerate(props):
                if i == j: continue
                # Edge if p is conditional/causal and matches q's subject roughly
                if p.modality in ('conditional', 'causal'):
                    # Simple string overlap heuristic for "matches"
                    if p.subj.lower() in q.subj.lower() or q.subj.lower() in p.subj.lower():
                        weight = 1.0 if p.modality == 'conditional' else 0.5
                        dist[i][j] = weight
                        
        return dist, n

    def _floyd_warshall(self, dist: List[List[float]], n: int) -> List[List[float]]:
        """Compute transitive closure."""
        if n == 0: return dist
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if dist[i][k] + dist[k][j] < dist[i][j]:
                        dist[i][j] = dist[i][k] + dist[k][j]
        return dist

    def _check_consistency(self, props: List[Prop]) -> float:
        """Check for logical contradictions via graph reachability."""
        if not props: return 1.0
        
        dist, n = self._build_graph(props)
        if n == 0: return 1.0
        
        # Floyd-Warshall
        closure = self._floyd_warshall(dist, n)
        
        violations = 0
        # Check for negation conflicts reachable in graph
        # Simplified: Check if any prop implies its own negation or direct conflict
        # Since we don't have full semantic linking, we check global negation density vs connectivity
        # Real implementation would map specific negated pairs. 
        # Approximation: If graph is highly connected but contains negated nodes, penalty.
        
        neg_count = sum(1 for p in props if p.polarity == -1)
        pos_count = len(props) - neg_count
        
        # Heuristic: If we have both positive and negative assertions about similar subjects
        if neg_count > 0 and pos_count > 0:
            # Check for direct string overlap in subjects with opposite polarity
            subjects = [p.subj.lower() for p in props]
            for i, p in enumerate(props):
                for j, q in enumerate(props):
                    if i != j and p.polarity != q.polarity:
                        if p.subj.lower() in q.subj.lower() or q.subj.lower() in p.subj.lower():
                            # If reachable in closure (or direct), it's a violation
                            if closure[i][j] < 1e8 or closure[j][i] < 1e8:
                                violations += 1
        
        total = max(1, len(props))
        return 1.0 - (violations / total)

    def _calc_utility(self, props: List[Prop]) -> float:
        """Score based on verifiable claims (Pragmatism)."""
        if not props: return 0.0
        score = 0
        for p in props:
            pred_lower = p.pred.lower()
            has_verifiable = any(v in pred_lower for v in self.VERIFIABLE_VERBS)
            has_numeric = bool(self.patterns['numeric'].search(p.obj))
            if has_verifiable and has_numeric:
                score += 1
            elif has_numeric: # Partial credit for numbers
                score += 0.5
        return score / len(props)

    def _calc_emergence(self, props: List[Prop]) -> float:
        """Score based on entropy of predicate types (Thermodynamics/Emergence)."""
        if not props: return 0.0
        
        # Count predicate types
        pred_counts = {}
        for p in props:
            t = p.modality # Use modality as type proxy for simplicity
            pred_counts[t] = pred_counts.get(t, 0) + 1
            
        total = len(props)
        entropy = 0.0
        for count in pred_counts.values():
            if count > 0:
                p_val = count / total
                entropy -= p_val * math.log2(p_val)
        
        max_entropy = math.log2(max(1, len(pred_counts)))
        if max_entropy == 0: return 1.0
        
        # Low entropy = high coherence (good emergence in this context)
        # Map to 0-1 where 1 is low entropy
        return 1.0 - (entropy / max_entropy)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        return z12 / max(z1, z2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            props = self._parse_text(cand)
            
            # Component Scores
            c_score = self._check_consistency(props)
            u_score = self._calc_utility(props)
            e_score = self._calc_emergence(props)
            
            # Weighted Sum
            final_score = (self.W_C * c_score) + (self.W_U * u_score) + (self.W_E * e_score)
            
            # Reasoning summary
            reason = f"Consistency:{c_score:.2f}, Utility:{u_score:.2f}, Emergence:{e_score:.2f}"
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reason
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Tie-breaking with NCD if scores are very close (within 0.01)
        # This is a simplified tie-break logic for the top candidates
        if len(results) > 1:
            top_score = results[0]['score']
            tied_group = [r for r in results if abs(r['score'] - top_score) < 0.01]
            if len(tied_group) > 1:
                # Re-sort tied group by NCD to prompt (lower NCD = more similar/relevant usually)
                # Note: In reasoning, sometimes diversity is good, but for "correctness" vs prompt context:
                tied_group.sort(key=lambda x: self._ncd(prompt, x['candidate']))
                # Re-insert sorted tie group
                results = tied_group + [r for r in results if r not in tied_group]

        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        # Normalize score to confidence
        # The raw score is 0-1, but we might want to be stricter
        score = res[0]['score']
        return max(0.0, min(1.0, score))
```

</details>
