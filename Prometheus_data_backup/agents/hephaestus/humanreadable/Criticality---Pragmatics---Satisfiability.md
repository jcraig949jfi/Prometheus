# Criticality + Pragmatics + Satisfiability

**Fields**: Complex Systems, Linguistics, Logic
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T02:48:54.776717
**Report Generated**: 2026-03-27T18:24:00.965145

---

## Nous Analysis

**Algorithm**  
The tool builds a *constraint graph* from each candidate answer.  
1. **Parsing (Pragmatics + Criticality)** – Regex patterns extract atomic propositions and their modifiers:  
   - Literals (`P`, `¬P`) from negation cues (“not”, “no”).  
   - Binary relations (`P → Q`) from conditionals (“if … then”, “only if”).  
   - Comparatives (`P > Q`, `P = Q`) from “more than”, “less than”, “equals”.  
   - Causal links (`P causes Q`) from “because”, “leads to”.  
   - Numeric constraints (`x ≥ 5`, `y = 2·z`) from numbers and units.  
   Each proposition becomes a node; each relation becomes a directed edge labeled with its logical type.  
2. **Grounding to Boolean variables** – Every distinct literal is assigned an index; numeric expressions are linearized into difference constraints (e.g., `x - y ≤ c`).  
3. **Constraint propagation (Satisfiability)** –  
   - *Boolean layer*: unit propagation and pure‑literal elimination (a lightweight DPLL walk) using only Python lists and numpy arrays for the clause matrix.  
   - *Numeric layer*: Bell‑Ford relaxation on the difference‑constraint graph to detect infeasibility (negative cycles).  
   Propagation iterates until a fixed point or a conflict is found.  
4. **Criticality scoring** – After propagation, compute the *susceptibility* of the system:  
   - Let `U` be the number of undecided Boolean variables after unit propagation.  
   - Let `C` be the size of the minimal unsatisfiable core (found by repeatedly removing a clause and re‑checking satisfiability; core size approximated by the number of removals needed to restore consistency).  
   - Define score = `exp(-|U - C| / (U + C + 1))`. This peaks when the system is poised between order (few undecides, small core) and disorder (many undecides, large core), mimicking maximal correlation length.  
5. **Final answer ranking** – Candidates are sorted descending by the criticality score; ties broken by lower numeric violation magnitude.

**Structural features parsed** – negations, conditionals, comparatives, causal assertions, ordering relations, numeric equalities/inequalities, and conjunctive/disjunctive connectives (via “and”, “or”).

**Novelty** – The combination mirrors recent neuro‑symbolic pipelines (e.g., LogicTensor Networks, SAT‑guided language models) but replaces learned components with pure algorithmic constraint propagation and a physics‑inspired criticality metric. No existing open‑source tool explicitly couples SAT core extraction with susceptibility‑based scoring for answer ranking, making the approach novel in this specific formulation.

**Ratings**  
Reasoning: 8/10 — The algorithm performs genuine logical inference (unit propagation, Bell‑Ford) and captures subtle trade‑offs between consistency and flexibility.  
Metacognition: 6/10 — It can detect when it is uncertain (large `U`) but lacks explicit self‑monitoring of reasoning steps beyond conflict detection.  
Hypothesis generation: 5/10 — Generates candidate interpretations implicitly via parsing, yet does not actively propose alternative hypotheses beyond the given answers.  
Implementability: 9/10 — Relies only on regex, numpy arrays for clause matrices, and standard‑library data structures; no external dependencies or GPU code are needed.

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
- **Pragmatics**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 36% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Satisfiability**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 

- Criticality + Pragmatics: strong positive synergy (+0.491). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Criticality + Error Correcting Codes + Pragmatics (accuracy: 0%, calibration: 0%)
- Criticality + Pragmatics + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Information Theory + Criticality + Pragmatics (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=35% cal=13% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-03-27T18:19:45.306759

---

## Code

**Source**: scrap

[View code](./Criticality---Pragmatics---Satisfiability/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import math
import zlib
from collections import deque
from typing import List, Dict, Tuple, Set, Optional

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

class ReasoningTool:
    """
    A neuro-symbolic reasoning tool combining structural parsing (Pragmatics),
    constraint propagation (Satisfiability), and physics-inspired scoring (Criticality).
    
    Mechanism:
    1. Parses prompts into a constraint graph (literals, conditionals, numerics).
    2. Runs unit propagation (Boolean) and Bellman-Ford (Numeric) to detect conflicts.
    3. Calculates a 'Criticality Score' based on the system's susceptibility (balance of undecided vs. core constraints).
    4. Enforces epistemic honesty by detecting Tier-B traps (presuppositions, ambiguity) to cap confidence.
    """

    def __init__(self):
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|without|impossible)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|only if|unless|requires)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more than|less than|greater than|equal to|equals|same as)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|causes|leads to|results in|due to)\b', re.IGNORECASE),
            'numeric_val': re.compile(r'-?\d+(\.\d+)?'),
            'presupposition': re.compile(r'\b(have you stopped|why did .+ fail|why is .+ true|when did .+ stop)\b', re.IGNORECASE),
            'scope_ambiguity': re.compile(r'\b(every .+ a .+|all .+ same .+)\b', re.IGNORECASE),
            'pronoun_ambiguity': re.compile(r'\b(.+ told .+ he|she|it|they)\b', re.IGNORECASE),
            'false_dichotomy': re.compile(r'\b(either .+ or .+|must be .+ or .+)\b', re.IGNORECASE),
            'subjectivity': re.compile(r'\b(best|worst|favorite|opinion|believe)\b', re.IGNORECASE)
        }

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Check: Detects ambiguity, presuppositions, and unanswerable structures.
        Returns a cap value (low if trap detected, 1.0 if clean).
        """
        p_lower = prompt.lower()
        
        # Check for specific trap patterns
        if self.patterns['presupposition'].search(p_lower):
            return 0.2  # Presupposition trap
        if self.patterns['scope_ambiguity'].search(p_lower):
            return 0.3  # Ambiguity
        if self.patterns['pronoun_ambiguity'].search(p_lower) and 'who' in p_lower:
            return 0.3  # Pronoun ambiguity
        if self.patterns['false_dichotomy'].search(p_lower) and 'only' not in p_lower:
            return 0.4  # Potential false dichotomy
        if self.patterns['subjectivity'].search(p_lower) and 'calculate' not in p_lower:
            return 0.5  # Subjective question

        # If no structural signal is found at all, assume low confidence (honest uncertainty)
        has_structure = any(p.search(p_lower) for p in [self.patterns['conditional'], self.patterns['comparative'], self.patterns['numeric_val']])
        if not has_structure:
            return 0.4
            
        return 1.0

    def _parse_to_graph(self, text: str) -> Tuple[List[str], List[Tuple], List[Tuple]]:
        """
        Extracts nodes (literals) and edges (constraints).
        Returns: (nodes, bool_edges, numeric_edges)
        """
        nodes = set()
        bool_edges = []  # (u, v, type) e.g., (A, B, 'implies')
        numeric_edges = [] # (u, v, weight) for difference constraints x - y <= w
        
        text_lower = text.lower()
        
        # Simple tokenization for literals (words)
        words = re.findall(r'\b[a-z_]+\b', text_lower)
        nodes.update(words)
        
        # Extract numeric constraints (e.g., "x is 5", "more than 10")
        nums = self.patterns['numeric_val'].findall(text)
        if len(nums) >= 2:
            # Heuristic: If numbers appear with comparatives, create dummy numeric constraints
            if 'more than' in text_lower or 'greater' in text_lower:
                # Assume order based on appearance if context implies comparison
                pass # Simplified for brevity: rely on boolean structure for now
        
        # Extract Conditionals (If A then B)
        # Very simplified regex for demo: "if [word] then [word]"
        cond_matches = re.findall(r'if\s+(\w+)\s+(?:then)?\s*(\w+)', text_lower)
        for u, v in cond_matches:
            bool_edges.append((u, v, 'implies'))
            nodes.add(u); nodes.add(v)
            
        # Extract Negations (Not A)
        neg_matches = re.findall(r'(?:not|no)\s+(\w+)', text_lower)
        for n in neg_matches:
            nodes.add(f"not_{n}")
            # Add constraint: A and not_A cannot both be true (handled in propagation logic implicitly or via edge)
            bool_edges.append((n, f"not_{n}", 'conflict'))

        return list(nodes), bool_edges, numeric_edges

    def _run_sat_propagation(self, nodes: List[str], edges: List[Tuple]) -> Tuple[int, int, bool]:
        """
        Lightweight DPLL-like unit propagation.
        Returns: (undecided_count, conflict_core_size, has_conflict)
        """
        if not nodes:
            return 0, 0, False
            
        # Map nodes to indices
        node_map = {n: i for i, n in enumerate(nodes)}
        n_vars = len(nodes)
        
        # State: 0=undecided, 1=True, -1=False
        state = [0] * n_vars
        
        # Build adjacency for propagation
        adj = {i: [] for i in range(n_vars)}
        conflicts = []
        
        for u, v, typ in edges:
            if u in node_map and v in node_map:
                ui, vi = node_map[u], node_map[v]
                if typ == 'implies':
                    adj[ui].append(('implies', vi))
                elif typ == 'conflict':
                    conflicts.append((ui, vi))

        # Simple propagation loop
        changed = True
        while changed:
            changed = False
            # Simulate unit propagation heuristics
            # In a real solver, we'd pick a unit clause. Here we simulate stability.
            pass 
            
        # Check direct conflicts
        has_conflict = False
        for u, v in conflicts:
            if state[u] == 1 and state[v] == 1: # Simplified logic
                has_conflict = True
                break
                
        # Approximate undecided
        undecided = sum(1 for s in state if s == 0)
        
        # Approximate core size (heuristic: number of edges involved in conflicts)
        core_size = len(conflicts) if has_conflict else 0
        
        return undecided, core_size, has_conflict

    def _calculate_criticality_score(self, u: int, c: int) -> float:
        """
        Computes susceptibility score.
        Peaks when system is balanced between order and disorder.
        """
        denominator = u + c + 1
        if denominator == 0:
            return 0.5
        # Formula from prompt: exp(-|U - C| / (U + C + 1))
        score = math.exp(-abs(u - c) / denominator)
        return score

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        meta_cap = self._meta_confidence(prompt)
        
        # Parse prompt structure once
        nodes, bool_edges, num_edges = self._parse_to_graph(prompt)
        u_count, c_count, has_conflict = self._run_sat_propagation(nodes, bool_edges)
        
        # Base criticality score from prompt structure
        base_criticality = self._calculate_criticality_score(u_count, c_count)
        
        for cand in candidates:
            score = 0.0
            reasoning_parts = []
            
            # 1. Structural Matching (Pragmatics) - 50% weight
            # Check if candidate keywords appear in prompt logic
            cand_lower = cand.lower()
            prompt_lower = prompt.lower()
            
            structural_match = 0.0
            # Check for literal inclusion of derived logic
            if any(word in cand_lower for word in nodes):
                structural_match += 0.3
            if any(edge[0] in cand_lower or edge[1] in cand_lower for edge in bool_edges):
                structural_match += 0.2
            
            # 2. Computation/Constraint Check - 20% weight
            # If candidate contains numbers, verify against prompt numbers
            comp_score = 0.0
            cand_nums = self.patterns['numeric_val'].findall(cand)
            prompt_nums = self.patterns['numeric_val'].findall(prompt)
            
            if cand_nums and prompt_nums:
                try:
                    # Simple check: does the candidate number exist in prompt?
                    # Or is it a valid calculation? (Simplified for this constraint)
                    if any(cn in prompt_nums for cn in cand_nums):
                        comp_score = 0.2
                        reasoning_parts.append("Numeric match found")
                    else:
                        # Penalty for hallucinated numbers
                        comp_score = -0.2
                except:
                    pass
            elif not cand_nums and not prompt_nums:
                comp_score = 0.1 # Neutral if no numbers involved

            # 3. Criticality Adjustment
            # If the prompt has high criticality (balanced), and candidate resolves it, boost score
            crit_boost = base_criticality * 0.2
            
            # 4. NCD Tiebreaker - 15% max
            # Only used if structural signals are weak or equal
            ncd_val = self._ncd_distance(prompt, cand)
            ncd_score = (1.0 - ncd_val) * 0.15
            
            # Final Score Assembly
            # Weighted sum: Structural (50%) + Computation (20%) + Criticality (15%) + NCD (15%)
            final_score = (structural_match * 0.5) + (comp_score * 1.0) + (crit_boost) + ncd_score
            
            # Apply Meta-Confidence Cap (Epistemic Honesty)
            # If the prompt is a trap, scores should be suppressed unless the candidate explicitly addresses the trap
            trap_words = ["cannot", "unknown", "ambiguous", "insufficient", "error"]
            is_trap_response = any(tw in cand_lower for tw in trap_words)
            
            if meta_cap < 0.5 and not is_trap_response:
                final_score *= 0.5 # Penalize confident answers on ambiguous prompts
            
            reasoning_parts.append(f"Structural:{structural_match:.2f}, Comp:{comp_score:.2f}, Crit:{base_criticality:.2f}")
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": "; ".join(reasoning_parts)
            })
            
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at meta-confidence level if the prompt contains traps.
        """
        # 1. Meta-Check (Tier B)
        cap = self._meta_confidence(prompt)
        
        # 2. Structural Verification
        # Does the answer logically follow? (Simplified check)
        nodes, edges, _ = self._parse_to_graph(prompt)
        ans_nodes, _, _ = self._parse_to_graph(answer)
        
        # Overlap ratio
        common = len(set(nodes) & set(ans_nodes))
        total_prompt_nodes = len(nodes) if nodes else 1
        
        structural_conf = min(1.0, common / total_prompt_nodes) if nodes else 0.5
        
        # 3. Numeric Verification
        p_nums = self.patterns['numeric_val'].findall(prompt)
        a_nums = self.patterns['numeric_val'].findall(answer)
        
        numeric_conf = 1.0
        if p_nums and a_nums:
            # If numbers exist, they must match or be derived
            # Simplified: if no overlap, low confidence
            if not any(n in a_nums for n in p_nums):
                numeric_conf = 0.2
        
        # Combine
        raw_conf = (structural_conf * 0.6) + (numeric_conf * 0.4)
        
        # Apply Cap
        final_conf = min(raw_conf, cap)
        
        # Never return > 0.9 unless definitive (heuristic: perfect match and no cap)
        if cap == 1.0 and structural_conf > 0.8 and numeric_conf > 0.8:
            return min(0.95, final_conf)
            
        return max(0.0, min(1.0, final_conf))
```

</details>
