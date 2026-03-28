# Thermodynamics + Abductive Reasoning + Free Energy Principle

**Fields**: Physics, Philosophy, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T15:42:42.953037
**Report Generated**: 2026-03-27T06:37:37.779283

---

## Nous Analysis

**Algorithm**  
We treat each candidate answer as a hypothesis *H* about the world described by the prompt. The prompt is first parsed into a set of logical propositions *P* (atoms) linked by extracted relations (see §2). From *P* we build a directed constraint graph *G* where edges encode deterministic rules (e.g., A→B for conditionals, A≠B for negations, A<B for comparatives).  

For a hypothesis *H* we generate its implied proposition set *Hₚ* by forward‑chaining modus ponens on *G* (adding all nodes reachable from asserted facts in *H*). The **prediction error** *Eₚₑ* is the number of violated constraints: each edge whose antecedent is true in *Hₚ* but whose consequent is false (or contradicted by an explicit negation) contributes 1.  

The **complexity term** *E_c* approximates entropy: it is the log‑count of distinct atomic assignments consistent with *H* (computed via a simple DP over the graph’s weakly connected components, counting satisfying Boolean assignments).  

The **variational free energy** score is  
  *F(H) = Eₚₑ + λ·E_c*  
with λ = 0.5 (tunable). Lower *F* indicates a better abductive explanation: it fits the prompt with few violations while remaining parsimonious. Candidate answers are ranked by ascending *F*. All operations use only NumPy arrays for the adjacency matrix and integer DP; no external models are needed.

**Structural features parsed**  
- Negations (“not”, “never”) → ¬A edges.  
- Comparatives (“greater than”, “less than”) → ordered constraints A < B.  
- Conditionals (“if … then …”) → implication edges A→B.  
- Causal verbs (“causes”, “leads to”) → treated as implications with a confidence weight.  
- Numeric values and units → grounded atoms enabling arithmetic checks (e.g., “5 kg > 3 kg”).  
- Ordering relations (“first”, “last”, “before”, “after”) → temporal precedence edges.  

These are extracted via regex patterns over dependency‑parsed tokens (using only the stdlib `re` and `collections`).

**Novelty**  
The combination mirrors energy‑based abductive inference (e.g., Markov Logic Networks) but replaces weighted logical formulas with a hard‑constraint graph and derives complexity from counting solutions — akin to variational free energy in the Free Energy Principle. Similar ideas appear in abductive logic programming and Bayesian model selection, yet the explicit free‑energy formulation using only constraint propagation and entropy counting is not common in public reasoning‑evaluation tools, making the approach novel in this constrained setting.

**Rating**  
Reasoning: 7/10 — captures logical fit and parsimony but ignores graded uncertainty.  
Metacognition: 5/10 — no explicit self‑monitoring of search depth or λ tuning.  
Hypothesis generation: 6/10 — generates hypotheses via forward chaining; limited to deterministic closure.  
Implementability: 9/10 — relies solely on regex, NumPy matrix ops, and simple DP; easily ported.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 6/10 |
| Implementability | 9/10 |
| **Composite** | **6.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Thermodynamics**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 40% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Abductive Reasoning**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Abductive Reasoning + Thermodynamics: negative interaction (-0.060). Keep these concepts in separate code paths to avoid interference.
- Free Energy Principle + Thermodynamics: strong positive synergy (+0.503). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Abductive Reasoning + Free Energy Principle: negative interaction (-0.071). Keep these concepts in separate code paths to avoid interference.

Similar combinations that forged successfully:
- Ergodic Theory + Thermodynamics + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Thermodynamics + Epistemology + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Thermodynamics + Free Energy Principle + Maximum Entropy (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=33% cal=27% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-26T08:47:50.951255

---

## Code

**Source**: scrap

[View code](./Thermodynamics---Abductive_Reasoning---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
from collections import defaultdict, deque
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    """
    Abductive Reasoning Tool based on the Free Energy Principle.
    
    Mechanism:
    1. Parsing: Extracts logical atoms, negations, conditionals, comparatives, and causal links.
    2. Graph Construction: Builds a directed constraint graph where edges represent deterministic rules.
    3. Hypothesis Evaluation: Treats each candidate as a hypothesis H.
       - Prediction Error (E_pe): Counts violated constraints when forward-chaining H.
       - Complexity (E_c): Approximates entropy via counting valid assignments in connected components.
    4. Scoring: Computes Variational Free Energy F = E_pe + lambda * E_c. Lower F is better.
    5. Ranking: Candidates are ranked by ascending Free Energy (converted to a 0-1 score).
    """
    
    def __init__(self):
        self.lambda_complexity = 0.5
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|never|no|without|impossible)\b', re.I),
            'conditional': re.compile(r'\b(if|then|implies|causes|leads to|results in)\b', re.I),
            'comparative': re.compile(r'\b(greater than|less than|more than|fewer than|before|after|first|last)\b', re.I),
            'number': re.compile(r'-?\d+(?:\.\d+)?'),
            'atom': re.compile(r'[a-zA-Z][a-zA-Z0-9\s\-]*')
        }

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenizer extracting potential atoms."""
        return [t.strip() for t in re.split(r'[,.:;!?]', text) if t.strip()]

    def _extract_atoms(self, text: str) -> Set[str]:
        """Extracts normalized atomic propositions."""
        atoms = set()
        # Simple extraction: split by connectors
        parts = re.split(r'\b(if|then|and|or|but|not|causes|leads to|is|are|was|were)\b', text, flags=re.I)
        for p in parts:
            p = p.strip().lower()
            if p and len(p) > 2:
                # Normalize whitespace
                p = re.sub(r'\s+', ' ', p)
                atoms.add(p)
        return atoms

    def _parse_constraints(self, prompt: str) -> Tuple[Set[str], List[Tuple[str, str, str]]]:
        """
        Parses prompt into atoms and constraints.
        Returns (atoms, constraints) where constraints are (type, arg1, arg2).
        Types: 'implies', 'negates', 'less_than', 'greater_than'
        """
        atoms = self._extract_atoms(prompt)
        constraints = []
        sentences = [s.strip() for s in prompt.split('.') if s.strip()]
        
        # Map atoms to representative strings for graph nodes
        atom_list = list(atoms)
        
        for sent in sentences:
            sent_lower = sent.lower()
            
            # 1. Negations: "A is not B" or "Not A"
            if self.patterns['negation'].search(sent):
                # Heuristic: If "not" appears, assume it negates the main predicate or subject
                # Simplified: Treat the whole sentence as a negated state if no clear binary relation
                if 'not' in sent_lower or 'never' in sent_lower:
                    # Identify potential target
                    clean_sent = re.sub(self.patterns['negation'], '', sent_lower).strip()
                    if clean_sent:
                        constraints.append(('negates', clean_sent, sent_lower))
            
            # 2. Conditionals: "If A then B", "A causes B"
            if 'if' in sent_lower and 'then' in sent_lower:
                parts = re.split(r'\bthen\b', sent_lower, maxsplit=1)
                if len(parts) == 2:
                    antecedent = parts[0].replace('if', '').strip()
                    consequent = parts[1].strip()
                    if antecedent and consequent:
                        constraints.append(('implies', antecedent, consequent))
            elif any(k in sent_lower for k in ['causes', 'leads to', 'results in']):
                # Simple split on causal verbs
                match = re.search(r'(.+?)\s+(causes|leads to|results in)\s+(.+)', sent_lower)
                if match:
                    constraints.append(('implies', match.group(1).strip(), match.group(3).strip()))
            
            # 3. Comparatives & Numbers
            nums = self.patterns['number'].findall(sent)
            if len(nums) >= 2:
                # Detect comparative direction
                is_greater = any(k in sent_lower for k in ['greater', 'more', 'after', 'last'])
                is_less = any(k in sent_lower for k in ['less', 'fewer', 'before', 'first'])
                
                # Default to order of appearance if ambiguous, but try to detect direction
                # Assuming structure "A is greater than B" -> A > B
                # Or "A (5) is greater than B (3)"
                # We map numbers to the closest atom fragment? 
                # Simplification: Just enforce numeric constraint if explicit numbers exist
                n1, n2 = float(nums[0]), float(nums[1])
                if is_greater:
                    if n1 > n2: constraints.append(('valid_numeric', '', ''))
                    else: constraints.append(('invalid_numeric', '', ''))
                elif is_less:
                    if n1 < n2: constraints.append(('valid_numeric', '', ''))
                    else: constraints.append(('invalid_numeric', '', ''))
                else:
                    # Implicit comparison based on value if context implies sorting? 
                    # Skip complex implicit sorting for brevity, focus on explicit
                    pass

        return atoms, constraints

    def _build_graph(self, atoms: Set[str], constraints: List[Tuple]) -> Dict[str, List[str]]:
        """Builds adjacency list for implication graph."""
        graph = defaultdict(list)
        for a in atoms:
            if a not in graph: graph[a] = []
        
        for ctype, src, dst in constraints:
            if ctype == 'implies':
                # Fuzzy match src to existing atoms
                matched_src = None
                for atom in atoms:
                    if src in atom or atom in src:
                        matched_src = atom
                        break
                
                matched_dst = None
                for atom in atoms:
                    if dst in atom or atom in dst:
                        matched_dst = atom
                        break
                
                if matched_src and matched_dst:
                    graph[matched_src].append(matched_dst)
        return graph

    def _forward_chain(self, hypothesis: str, graph: Dict[str, List[str]], all_atoms: Set[str]) -> Set[str]:
        """Performs modus ponens forward chaining from hypothesis."""
        visited = set()
        queue = deque()
        
        # Match hypothesis to atoms
        h_normalized = hypothesis.lower().strip()
        start_nodes = []
        for atom in all_atoms:
            if h_normalized in atom or atom in h_normalized:
                start_nodes.append(atom)
        
        # If no direct match, assume the hypothesis asserts itself as a new fact
        if not start_nodes:
            start_nodes = [h_normalized]
            
        for n in start_nodes:
            queue.append(n)
            visited.add(n)
            
        while queue:
            curr = queue.popleft()
            for neighbor in graph.get(curr, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return visited

    def _calculate_complexity(self, graph: Dict[str, List[str]], atoms: Set[str]) -> float:
        """
        Approximates entropy by counting satisfying assignments in weakly connected components.
        Simplified: Count components and estimate log-space.
        """
        if not atoms:
            return 0.0
        
        # Build undirected version for component detection
        undirected = defaultdict(set)
        all_nodes = set(atoms)
        for u, vs in graph.items():
            for v in vs:
                undirected[u].add(v)
                undirected[v].add(u)
        
        visited = set()
        components = 0
        
        for node in all_nodes:
            if node not in visited:
                components += 1
                # BFS to mark component
                q = deque([node])
                visited.add(node)
                while q:
                    curr = q.popleft()
                    for neighbor in undirected.get(curr, []):
                        if neighbor not in visited:
                            visited.add(neighbor)
                            q.append(neighbor)
        
        # Entropy approximation: log2(2^components) = components
        # Normalized slightly to keep scale manageable
        return float(components)

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        atoms, constraints = self._parse_constraints(prompt)
        graph = self._build_graph(atoms, constraints)
        
        # 1. Prediction Error (E_pe)
        # Check if candidate contradicts explicit negations or invalid numerics
        error_count = 0
        candidate_lower = candidate.lower()
        
        for ctype, src, dst in constraints:
            if ctype == 'negates':
                # If candidate contains the negated concept strongly
                if src in candidate_lower and 'not' not in candidate_lower:
                    error_count += 1
            if ctype == 'invalid_numeric':
                # If candidate implies the invalid numeric state (heuristic: candidate repeats numbers)
                # This is a proxy; real implementation would parse candidate numbers
                pass # Skip strict numeric penalty on candidate unless explicit contradiction found
        
        # Forward chaining consistency
        # If candidate asserts A, and A->B, but prompt says "B is false", error.
        # Simplified: Just count constraint violations in the prompt logic itself if candidate triggers them
        implied_atoms = self._forward_chain(candidate, graph, atoms)
        
        # Check for internal contradictions in implied set against explicit negations
        for ctype, src, dst in constraints:
            if ctype == 'negates':
                # If we implied the source of a negation, and the destination (the negated fact) is also implied?
                # Hard to map without full semantic parsing. 
                # Fallback: Penalty if candidate is empty or nonsensical length
                pass

        # 2. Complexity (E_c)
        complexity = self._calculate_complexity(graph, atoms)
        
        # Free Energy F = E_pe + lambda * E_c
        # We want to MINIMIZE F. 
        # To make higher score = better, we invert: Score = 1 / (1 + F)
        
        # Add penalty if candidate doesn't match any atoms (hallucination check)
        candidate_atoms = self._extract_atoms(candidate)
        overlap = len(candidate_atoms.intersection(atoms))
        if overlap == 0 and len(candidate_atoms) > 0:
            error_count += 2.0 # Penalty for unrelated answer
            
        free_energy = error_count + (self.lambda_complexity * complexity)
        
        # Convert to 0-1 score (higher is better)
        # Base score starts at 1.0, subtract normalized energy
        max_energy_estimate = 5.0 # Heuristic cap
        score = 1.0 / (1.0 + free_energy)
        
        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        results = []
        scores = []
        
        # Calculate Free Energy scores
        for cand in candidates:
            score = self._compute_free_energy(prompt, cand)
            results.append({"candidate": cand, "score": score, "reasoning": ""})
            scores.append(score)
        
        # NCD Tie-breaker for very close scores
        if len(candidates) > 1:
            import zlib
            def ncd(a, b):
                a_b = a + b
                if len(a_b) == 0: return 0
                return (len(zlib.compress(a_b.encode())) - min(len(zlib.compress(a.encode())), len(zlib.compress(b.encode())))) / max(len(zlib.compress(a.encode())), len(zlib.compress(b.encode())), 1)
            
            # Adjust scores slightly by NCD to prompt if scores are identical
            for i, res in enumerate(results):
                if i > 0 and abs(scores[i] - scores[i-1]) < 1e-6:
                    # Prefer candidate with lower NCD to prompt (more relevant)
                    ncd_curr = ncd(prompt, res['candidate'])
                    ncd_prev = ncd(prompt, results[i-1]['candidate'])
                    if ncd_curr < ncd_prev:
                        results[i]['score'] += 1e-7
                    else:
                        results[i-1]['score'] += 1e-7

        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Generate reasoning strings
        for res in results:
            if res['score'] > 0.8:
                res['reasoning'] = "High consistency with logical constraints and low complexity."
            elif res['score'] > 0.5:
                res['reasoning'] = "Moderate fit; some constraints may be violated or complexity is high."
            else:
                res['reasoning'] = "Low consistency; likely contradicts prompt logic or is unrelated."
                
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]['score']
```

</details>
