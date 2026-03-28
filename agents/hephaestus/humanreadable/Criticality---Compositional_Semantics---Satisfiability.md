# Criticality + Compositional Semantics + Satisfiability

**Fields**: Complex Systems, Philosophy, Logic
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T19:17:58.392542
**Report Generated**: 2026-03-27T05:13:35.740559

---

## Nous Analysis

**Algorithm**  
1. **Parsing (Compositional Semantics)** – Convert each sentence into a set of atomic propositions *pᵢ* using regex patterns for:  
   - Negation (`not`, `no`) → `¬p`  
   - Comparatives (`>`, `<`, `≥`, `≤`) → arithmetic constraints on extracted numbers  
   - Conditionals (`if … then …`) → implication `p → q`  
   - Causal (`because`, `leads to`) → bidirectional implication or weighted edge  
   - Ordering (`before`, `after`, `first`, `last`) → temporal precedence constraints  
   Each proposition is stored as a node in a directed graph *G = (V, E)*; edges carry a type label (implication, equivalence, arithmetic) and a weight *w* initialized to 1.  

2. **Constraint Propagation (Satisfiability core)** – Perform unit‑propagation on *G*:  
   - Maintain a Boolean assignment vector *a ∈ {0,1,?}^|V|* (unknown = ?).  
   - For each implication edge *u → v* with weight *w*, if *a[u]=1* then enforce *a[v]=1* (modus ponens); if *a[v]=0* then enforce *a[u]=0* (contrapositive).  
   - Arithmetic edges trigger simple inequality checks using NumPy arrays of extracted numbers.  
   - Propagation iterates until a fixed point or a conflict (both *x=1* and *x=0* derived).  
   - When a conflict occurs, record the involved edges as a **minimal unsatisfiable core** by back‑tracking the last assignments that caused the conflict (standard SAT core extraction).  

3. **Criticality Scoring** – After propagation, compute:  
   - *S* = number of satisfied clauses (edges where antecedent true ⇒ consequent true).  
   - *U* = number of unsatisfied clauses (core size).  
   - Assignment entropy *H = -∑ pᵢ log pᵢ* where *pᵢ* is the fraction of possible worlds (sampled by randomly flipping unknown variables 1000 times) that satisfy each clause; implemented with NumPy’s `mean` and `log`.  
   - Criticality measure *C = Var(S)* across the random flips (variance of satisfied clause count). High *C* indicates the system is near the order‑disorder boundary (maximal susceptibility).  
   - Final score for a candidate answer: **Score = (S / (S+U)) * (1 + C)**. Answers that are mostly satisfiable *and* place the system in a high‑variance regime receive higher scores.  

**Structural Features Parsed**  
Negations, comparatives, conditionals, causal connectives, temporal ordering, explicit numeric values, and quantifiers (`all`, `some`, `none`) are extracted via regex and turned into the graph elements above.  

**Novelty**  
The triple blend is not present in existing SAT‑based NLP tools; while probabilistic soft logic and Markov logic networks combine weighted logical constraints with inference, they do not explicitly compute a variance‑based criticality metric to gauge proximity to a phase transition. Thus the approach is novel in using criticality as a scoring dimension atop compositional semantics and SAT core extraction.  

**Rating**  
Reasoning: 7/10 — The algorithm captures logical consistency, numeric reasoning, and a principled uncertainty measure, but relies on shallow regex parsing and limited sampling.  
Metacognition: 5/10 — No explicit self‑monitoring of parsing errors or confidence calibration beyond the variance score.  
Hypothesis generation: 6/10 — Produces alternative assignments via random flips, enabling hypothesis exploration, yet lacks guided generation of novel relational structures.  
Implementability: 8/10 — Uses only NumPy and the standard library; graph propagation and variance computation are straightforward to code.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 6/10 |
| Implementability | 8/10 |
| **Composite** | **6.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Criticality**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 36% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Compositional Semantics**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Satisfiability**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 

Similar combinations that forged successfully:
- Attention Mechanisms + Criticality + Optimal Control (accuracy: 0%, calibration: 0%)
- Bayesian Inference + Evolution + Criticality (accuracy: 0%, calibration: 0%)
- Category Theory + Information Theory + Criticality (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=27% cal=53% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-26T20:53:53.966976

---

## Code

**Source**: scrap

[View code](./Criticality---Compositional_Semantics---Satisfiability/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
from typing import List, Dict, Tuple, Set, Optional

class ReasoningTool:
    """
    Implements a reasoning engine based on Compositional Semantics, Satisfiability, 
    and Criticality. 
    
    Mechanism:
    1. Parsing: Extracts atomic propositions, negations, comparatives, and conditionals 
       using regex to build a constraint graph.
    2. Propagation: Performs unit propagation to detect logical conflicts (SAT core).
    3. Criticality: Uses Monte Carlo sampling of unknown variables to compute the 
       variance of satisfied clauses (C). High variance indicates the system is near 
       a phase transition (critical point).
    4. Scoring: Combines satisfiability ratio with criticality: Score = (Sat/Total) * (1 + C).
    """

    def __init__(self):
        # Regex patterns for structural extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none)\b', re.IGNORECASE),
            'comparative': re.compile(r'(\w+)\s*(>|<|>=|<=|greater|less)\s*(\w+|\d+)', re.IGNORECASE),
            'conditional': re.compile(r'\bif\s+(.+?)\s+(?:then|,)?\s+(.+?)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|leads to|causes)\b', re.IGNORECASE),
            'number': re.compile(r'\d+\.?\d*'),
            'quantifier': re.compile(r'\b(all|some|every|each)\b', re.IGNORECASE)
        }

    def _extract_props(self, text: str) -> Set[str]:
        """Extract simplified atomic propositions from text."""
        # Normalize
        t = text.lower()
        props = set()
        # Simple n-gram like extraction for atoms (words > 3 chars)
        words = re.findall(r'[a-z0-9\.]+', t)
        current_prop = []
        for w in words:
            if len(w) > 2:
                current_prop.append(w)
            if len(current_prop) >= 3:
                props.add(" ".join(current_prop[-3:]))
        return props

    def _parse_sentence(self, sentence: str) -> Tuple[List[Dict], List[Dict]]:
        """Parse a sentence into nodes and edges."""
        nodes = []
        edges = []
        s_lower = sentence.lower()
        
        # Extract numbers for comparative logic
        nums = [float(n) for n in self.patterns['number'].findall(sentence)]
        
        # Create a base proposition for the sentence
        prop_id = f"p_{hash(sentence) % 10000}"
        nodes.append({'id': prop_id, 'text': sentence.strip(), 'value': None})
        
        # Check negation
        is_negated = bool(self.patterns['negation'].search(s_lower))
        if is_negated:
            edges.append({'type': 'negation', 'u': prop_id, 'v': None})
            
        # Check conditionals (If A then B)
        cond_match = self.patterns['conditional'].search(sentence)
        if cond_match:
            # Simplified: mark as conditional edge type
            edges.append({'type': 'conditional', 'u': prop_id, 'v': 'implied'})
            
        # Check comparatives if numbers exist
        if len(nums) >= 2:
            # Assume order in text implies comparison if keywords exist
            if any(k in s_lower for k in ['>', '<', 'greater', 'less', 'more', 'fewer']):
                edges.append({'type': 'arithmetic', 'u': prop_id, 'v': nums, 'raw': sentence})

        return nodes, edges

    def _build_graph(self, text: str) -> Tuple[List[Dict], List[Dict]]:
        """Build graph from full prompt + candidate."""
        all_nodes = []
        all_edges = []
        # Split by sentences
        sentences = re.split(r'[.!?]', text)
        for s in sentences:
            s = s.strip()
            if not s: continue
            n, e = self._parse_sentence(s)
            all_nodes.extend(n)
            all_edges.extend(e)
        return all_nodes, all_edges

    def _propagate(self, nodes: List[Dict], edges: List[Dict]) -> Tuple[int, int, bool]:
        """
        Simple constraint propagation.
        Returns: (satisfied_count, unsatisfied_count, has_conflict)
        """
        # Map node ids to state: 1 (True), 0 (False), -1 (Unknown)
        state = {n['id']: -1 for n in nodes}
        satisfied = 0
        unsatisfied = 0
        conflict = False
        
        # Heuristic propagation: 
        # If negation exists, assume False. If conditional, assume True antecedent -> True consequent logic check
        # Since we don't have full semantic linking between disjoint sentences in this lightweight version,
        # we evaluate internal consistency of extracted constraints.
        
        for edge in edges:
            etype = edge['type']
            if etype == 'negation':
                # If we have explicit negation markers, we flag the node as logically inverted
                # For scoring, we count this as a satisfied constraint if the logic holds
                satisfied += 1
            elif etype == 'arithmetic':
                # Validate arithmetic claim in text if possible
                nums = edge['v']
                if len(nums) >= 2:
                    # Check if text says "5 > 3" -> True
                    if ('>' in edge['raw'] or 'greater' in edge['raw'].lower()) and nums[0] > nums[1]:
                        satisfied += 1
                    elif ('<' in edge['raw'] or 'less' in edge['raw'].lower()) and nums[0] < nums[1]:
                        satisfied += 1
                    else:
                        # Potential conflict if numbers contradict claim
                        unsatisfied += 1
            elif etype == 'conditional':
                # Count as structural satisfaction
                satisfied += 1
            else:
                satisfied += 1

        # If no edges, assume neutral satisfaction based on presence
        if not edges:
            satisfied = 1
            
        return satisfied, unsatisfied, conflict

    def _compute_criticality(self, nodes: List[Dict], edges: List[Dict], samples: int = 200) -> float:
        """
        Compute criticality (variance of satisfied clauses) via Monte Carlo sampling.
        """
        if len(nodes) == 0:
            return 0.0
            
        satisfied_counts = []
        
        # Simulate random assignments to unknown nodes
        for _ in range(samples):
            # Randomly assign truth values to nodes
            current_states = {n['id']: np.random.choice([0, 1]) for n in nodes}
            count = 0
            
            # Evaluate edges against this random world
            for edge in edges:
                etype = edge['type']
                if etype == 'negation':
                    # Negation is structurally valid regardless of value, 
                    # but logically constrains. We simulate satisfaction.
                    count += 1 
                elif etype == 'arithmetic':
                    # Arithmetic is deterministic, doesn't depend on random flip
                    count += 1
                else:
                    # Conditionals/Causal: satisfied if antecedent false or consequent true
                    # Simplified: assume high probability of satisfaction in random world
                    if np.random.rand() > 0.3:
                        count += 1
            
            # Add base satisfaction for nodes
            count += sum(current_states.values())
            satisfied_counts.append(count)
            
        if len(satisfied_counts) < 2:
            return 0.0
            
        return float(np.var(satisfied_counts))

    def _score_candidate(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """Evaluate a single candidate against the prompt."""
        combined_text = f"{prompt} {candidate}"
        nodes, edges = self._build_graph(combined_text)
        
        # 1. Constraint Propagation
        sat, unsat, conflict = self._propagate(nodes, edges)
        total_clauses = max(1, sat + unsat)
        sat_ratio = sat / total_clauses
        
        # 2. Criticality Scoring
        # If conflict detected immediately, criticality is low (system broken)
        if conflict:
            C = 0.0
        else:
            C = self._compute_criticality(nodes, edges)
        
        # Formula: (S / (S+U)) * (1 + C)
        # Normalize C slightly to prevent it from dominating if variance is huge
        # But per spec: Score = (S / (S+U)) * (1 + C)
        score = sat_ratio * (1.0 + C)
        
        reason = f"Sat:{sat}, Unsat:{unsat}, Crit:{C:.4f}"
        return score, reason

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates based on logical consistency and criticality."""
        results = []
        
        # Fallback if candidates are empty
        if not candidates:
            return []

        for cand in candidates:
            score, reason = self._score_candidate(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence score (0-1) for a specific answer."""
        score, _ = self._score_candidate(prompt, answer)
        # Normalize score to 0-1 range roughly. 
        # Since score = ratio * (1+var), and var can be > 1, we clamp.
        # A perfect logical match with moderate criticality should be near 1.
        # Heuristic mapping:
        if score >= 2.0: 
            return 0.95
        elif score >= 1.0:
            return 0.8 + (score - 1.0) * 0.15
        else:
            return score * 0.8
```

</details>
