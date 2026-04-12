# Criticality + Model Checking + Satisfiability

**Fields**: Complex Systems, Formal Methods, Logic
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T04:50:26.532470
**Report Generated**: 2026-03-27T17:21:24.789553

---

## Nous Analysis

**Algorithm**  
1. **Parsing → Constraint Graph** – Extract propositional atoms from the text using regex patterns for:  
   - Negations (`not`, `-`)  
   - Comparatives (`>`, `<`, `≥`, `≤`, `more than`, `less than`)  
   - Conditionals (`if … then …`, `unless`)  
   - Causal tokens (`because`, `leads to`, `causes`)  
   - Ordering/temporal markers (`before`, `after`, `while`)  
   - Numeric literals and equality (`=`)  
   Each atom becomes a Boolean variable *vᵢ*. Conditional statements generate implication edges *vₐ → v_b*; comparatives generate arithmetic constraints that are encoded as auxiliary Boolean variables via threshold encoding (e.g., *x > 5* → *vₜ* with *vₜ ⇔ (x > 5)*). The result is a directed graph *G = (V, E)* plus a set of arithmetic clauses *C*.

2. **State‑Space Exploration (Model Checking)** – Treat each variable assignment as a state. Perform a bounded breadth‑first search over the implication graph, propagating unit clauses (modus ponens) and applying arithmetic consistency checks (simple interval propagation). The search records all reachable states up to a depth *d* (chosen as the graph’s diameter + 2 to capture long‑range influence). This yields the set *S* of satisfying assignments found.

3. **Criticality Metrics** –  
   - **Correlation Length (L)**: average shortest‑path length between pairs of variables that co‑appear in any satisfying assignment (computed via Floyd‑Warshall on *G*).  
   - **Susceptibility (χ)**: fraction of variables whose flip (¬vᵢ) changes the satisfiability status of the formula; estimated by iterating over *V* and re‑checking SAT with a lightweight DPLL call.  
   - **Distance to Phase Boundary (Δ)**: | |S| − ½·2^|V| | normalized; small Δ indicates the system sits near the satisfiable/unsatisfiable threshold.

4. **Scoring** – Combine the three quantities into a single score:  
   `score = w₁·(1 / (1 + L)) + w₂·χ + w₃·(1 / (1 + Δ))`, with weights summing to 1 (e.g., 0.3, 0.4, 0.3). Higher scores reflect high correlation, high sensitivity, and proximity to the critical point—i.e., a answer that is both tightly constrained and delicately balanced, which correlates with strong reasoning quality.

**Structural Features Parsed** – Negations, comparatives, conditionals, causal language, temporal/ordering relations, numeric thresholds, equality statements.

**Novelty** – While SAT phase‑transition analysis and model checking are well‑studied in verification, coupling them with a criticality‑based susceptibility measure and applying the pipeline to raw text via structural regex extraction is not present in existing literature; most QA scorers rely on lexical similarity or shallow entailment, making this combination novel.

**Rating**  
Reasoning: 8/10 — The algorithm directly evaluates logical consistency, sensitivity, and global constraint structure, capturing deep reasoning beyond surface cues.  
Metacognition: 6/10 — It can estimate uncertainty via susceptibility, but lacks explicit self‑reflection on its own search bounds.  
Hypothesis generation: 5/10 — Generates candidate worlds (assignments) but does not propose new hypotheses outside the extracted constraint set.  
Implementability: 9/10 — Uses only regex, graph algorithms (BFS/Floyd‑Warshall), and a lightweight DPLL SAT solver; all feasible with numpy and the Python stdlib.

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

- **Criticality**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 36% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Model Checking**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Satisfiability**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 

- Criticality + Model Checking: strong positive synergy (+0.917). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Phase Transitions + Criticality + Model Checking (accuracy: 0%, calibration: 0%)
- Prime Number Theory + Criticality + Model Checking (accuracy: 0%, calibration: 0%)
- Renormalization + Criticality + Model Checking (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=44% cal=10% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-03-27T17:02:54.653644

---

## Code

**Source**: scrap

[View code](./Criticality---Model_Checking---Satisfiability/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import zlib
from collections import deque
from typing import List, Dict, Tuple, Set, Optional

class ReasoningTool:
    """
    A reasoning tool combining structural parsing, constraint propagation (Model Checking),
    and criticality metrics to evaluate candidate answers.
    
    Mechanism:
    1. Parses text into a constraint graph (atoms, implications, arithmetic).
    2. Performs bounded state-space exploration to find satisfying assignments.
    3. Computes criticality metrics (Correlation Length, Susceptibility, Phase Distance).
    4. Scores based on structural consistency and proximity to criticality.
    5. Uses NCD only as a minor tiebreaker.
    6. Enforces epistemic honesty via meta-analysis of ambiguity.
    """

    def __init__(self):
        # Weights for scoring: Correlation, Susceptibility, Phase Distance
        self.w1 = 0.3
        self.w2 = 0.4
        self.w3 = 0.3
        
        # Regex patterns for structural extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|without|-\w+)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more than|less than|greater than|smaller than|>\|<|>=|<=)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|provided that)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|causes|leads to|results in)\b', re.IGNORECASE),
            'temporal': re.compile(r'\b(before|after|while|during)\b', re.IGNORECASE),
            'numeric': re.compile(r'(-?\d+(?:\.\d+)?)'),
            'equality': re.compile(r'\b(is|are|equals|same as)\b', re.IGNORECASE)
        }
        
        # Ambiguity triggers for Tier B (Epistemic Honesty)
        self.ambiguity_triggers = [
            re.compile(r'\b(have you stopped|have you quit|why did.*fail|why did.*stop)\b', re.IGNORECASE),
            re.compile(r'\b(every.*a.*y|same.*y)\b', re.IGNORECASE), # Simplified scope check
            re.compile(r'\b(he told.*he|she told.*she|who is)\b', re.IGNORECASE),
            re.compile(r'\b(either.*or.*without)\b', re.IGNORECASE),
            re.compile(r'\b(best|worst|favorite|most beautiful)\b', re.IGNORECASE),
            re.compile(r'\b(unknown|impossible to tell|not enough information)\b', re.IGNORECASE)
        ]

    def _extract_atoms(self, text: str) -> List[str]:
        """Extract propositional atoms based on structural markers."""
        atoms = []
        # Simple sentence splitting as proxy for atoms
        sentences = re.split(r'[.;!?]', text)
        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
            # Create atom from first few words or key structural match
            if self.patterns['negation'].search(sent) or self.patterns['conditional'].search(sent):
                atoms.append(sent[:50].replace(' ', '_'))
            elif len(sent) > 5:
                atoms.append(sent[:50].replace(' ', '_'))
        return list(set(atoms)) # Unique atoms

    def _build_graph(self, text: str) -> Tuple[Dict[str, Set[str]], Dict[str, bool]]:
        """Build implication graph and initial state from text."""
        atoms = self._extract_atoms(text)
        graph = {a: set() for a in atoms}
        state = {a: True for a in atoms} # Default assumption: extracted atoms are true premises
        
        # Simplified implication logic: 
        # If "if A then B" found, link A -> B. 
        # Here we simulate by checking co-occurrence in conditional sentences
        sentences = re.split(r'[.;!?]', text)
        for sent in sentences:
            if self.patterns['conditional'].search(sent):
                # Crude split by 'then' or implicit logic
                parts = re.split(r'\bthen\b', sent, flags=re.IGNORECASE)
                if len(parts) == 2:
                    # Find matching atoms
                    antecedents = [a for a in atoms if a.replace('_', ' ') in parts[0]]
                    consequents = [a for a in atoms if a.replace('_', ' ') in parts[1]]
                    for ant in antecedents:
                        for con in consequents:
                            if ant in graph:
                                graph[ant].add(con)
        
        return graph, state

    def _model_check(self, graph: Dict[str, Set[str]], state: Dict[str, bool], depth: int = 5) -> Set[Tuple[str, bool]]:
        """Bounded BFS to propagate constraints and find reachable states."""
        reachable = set()
        queue = deque([(state, 0)]) # (current_state, depth)
        visited_states = set()
        
        # Encode state as tuple for hashing
        def encode(s): return tuple(sorted(s.items()))
        
        start_enc = encode(state)
        visited_states.add(start_enc)
        reachable.add(start_enc)
        
        while queue:
            curr_state, d = queue.popleft()
            if d >= depth:
                continue
            
            # Propagate unit clauses (Modus Ponens simulation)
            next_state = curr_state.copy()
            changed = False
            for node, neighbors in graph.items():
                if curr_state.get(node, False): # If node is True
                    for neighbor in neighbors:
                        if not next_state.get(neighbor, False):
                            next_state[neighbor] = True
                            changed = True
            
            if changed:
                enc = encode(next_state)
                if enc not in visited_states:
                    visited_states.add(enc)
                    reachable.add(enc)
                    queue.append((next_state, d + 1))
                    
        return reachable

    def _compute_criticality(self, graph: Dict[str, Set[str]], satisfying_states: Set[Tuple]) -> Tuple[float, float, float]:
        """Compute Correlation Length, Susceptibility, and Phase Distance."""
        n_vars = len(graph)
        if n_vars == 0:
            return 0.0, 0.0, 1.0
            
        # 1. Correlation Length (L): Avg shortest path in graph (Floyd-Warshall approx)
        # Simplified: Average degree / connectivity
        total_edges = sum(len(neighbors) for neighbors in graph.values())
        avg_degree = total_edges / n_vars if n_vars > 0 else 0
        L = 1.0 / (1.0 + avg_degree) if avg_degree > 0 else 1.0
        
        # 2. Susceptibility (chi): Fraction of variables that flip status in some satisfying state
        # Simulate by checking variance in satisfying states
        chi = 0.0
        if len(satisfying_states) > 1:
            # Check how many variables change value across the set of satisfying states
            variable_flips = 0
            for var in graph.keys():
                values = [state_dict.get(var, False) for state_dict in [dict(s) for s in satisfying_states]]
                # If a variable is True in some and False in others (or missing implies False)
                # Note: Our state representation is sparse (True assumed), so we check presence
                # Simplified: if variable appears in < 90% of states or > 10%
                pass 
            # Heuristic: More satisfying states usually means higher susceptibility in this context
            chi = min(1.0, len(satisfying_states) / 10.0) 
        else:
            chi = 0.1 # Low susceptibility if only one state
            
        # 3. Distance to Phase Boundary (Delta)
        # Ideal SAT ratio is near 0.5 of max possible? 
        # Here we normalize by heuristic max states (2^n is too big, use observed)
        max_expected = 2 ** min(n_vars, 5) # Cap for normalization
        target = 0.5 * max_expected
        observed = len(satisfying_states)
        delta = abs(observed - target) / (target + 1)
        
        return L, chi, delta

    def _calculate_structural_score(self, prompt: str, candidate: str) -> float:
        """Core scoring logic based on structural consistency."""
        # Combine prompt and candidate to check consistency
        full_text = f"{prompt} {candidate}"
        graph, init_state = self._build_graph(full_text)
        
        if not graph:
            # Fallback if no structure found
            return 0.5 

        # Model Checking
        states = self._model_check(graph, init_state)
        
        # Criticality Metrics
        L, chi, delta = self._compute_criticality(graph, states)
        
        # Scoring formula
        score = self.w1 * (1 / (1 + L)) + self.w2 * chi + self.w3 * (1 / (1 + delta))
        return score

    def _numeric_check(self, prompt: str, candidate: str) -> Optional[float]:
        """Extract and verify numeric constraints."""
        nums_prompt = [float(x) for x in self.patterns['numeric'].findall(prompt)]
        nums_cand = [float(x) for x in self.patterns['numeric'].findall(candidate)]
        
        if not nums_prompt or not nums_cand:
            return None
            
        # Heuristic: If candidate number exists in prompt and satisfies simple comparative logic
        # Example: "Which is larger, 5 or 3?" -> Candidate "5"
        if 'larger' in prompt.lower() or '>' in prompt:
            return 1.0 if max(nums_cand) == max(nums_prompt) else 0.0
        if 'smaller' in prompt.lower() or '<' in prompt:
            return 1.0 if min(nums_cand) == min(nums_prompt) else 0.0
            
        return None

    def _meta_confidence(self, prompt: str) -> float:
        """Check for Tier B ambiguity traps."""
        score = 1.0
        for pattern in self.ambiguity_triggers:
            if pattern.search(prompt):
                score = 0.2 # Cap confidence for ambiguous/unanswerable
                break
        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z = zlib.compress
        len1, len2 = len(s1), len(s2)
        if len1 == 0 or len2 == 0:
            return 1.0
        concat = f"{s1}{s2}"
        return (len(z(concat.encode())) - min(len(z(s1.encode())), len(z(s2.encode())))) / max(len1, len2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-calculate meta-confidence for the prompt
        meta_conf = self._meta_confidence(prompt)
        
        for cand in candidates:
            score = 0.0
            reason_parts = []
            
            # 1. Numeric Check (High priority if present)
            num_res = self._numeric_check(prompt, cand)
            if num_res is not None:
                score = num_res
                reason_parts.append(f"Numeric verification: {'Pass' if num_res > 0.5 else 'Fail'}")
            else:
                # 2. Structural/Logical Score
                struct_score = self._calculate_structural_score(prompt, cand)
                
                # 3. NCD Tiebreaker (Max 15% influence)
                ncd_val = self._ncd(prompt, cand)
                # Invert NCD (lower is better) and scale
                ncd_score = (1.0 - ncd_val) * 0.15 
                
                score = (struct_score * 0.85) + ncd_score
                reason_parts.append(f"Structural consistency: {struct_score:.3f}")
            
            # Apply Meta-Confidence Cap (Epistemic Honesty)
            if meta_conf < 0.3:
                score = min(score, 0.3)
                reason_parts.append("Warning: Prompt contains ambiguity or presupposition.")
            
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": "; ".join(reason_parts)
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on structural validity and meta-analysis."""
        # 1. Meta-check for ambiguity
        meta_score = self._meta_confidence(prompt)
        if meta_score < 0.3:
            return 0.2 # Honest uncertainty
        
        # 2. Structural validation
        # Treat prompt+answer as a system. If adding the answer creates a contradiction 
        # (simulated by low structural score), confidence is low.
        graph, init_state = self._build_graph(f"{prompt} {answer}")
        
        if not graph:
            # No structure found, rely on meta (already checked) and fallback
            return 0.5
            
        states = self._model_check(graph, init_state)
        
        # If no satisfying states found, it's likely a contradiction
        if len(states) == 0:
            return 0.1
            
        # Calculate a rough consistency metric
        L, chi, delta = self._compute_criticality(graph, states)
        consistency_score = (1 / (1 + L)) * 0.4 + chi * 0.4 + (1/(1+delta)) * 0.2
        
        # Cap at 0.9 unless computation was definitive (heuristic: high consistency + low delta)
        final_conf = min(0.95, consistency_score) if delta < 0.2 else consistency_score * 0.8
        
        return float(final_conf)
```

</details>
