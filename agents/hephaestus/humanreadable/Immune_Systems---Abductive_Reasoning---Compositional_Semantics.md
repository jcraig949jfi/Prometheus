# Immune Systems + Abductive Reasoning + Compositional Semantics

**Fields**: Biology, Philosophy, Philosophy
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T04:45:57.248219
**Report Generated**: 2026-04-01T20:30:43.591123

---

## Nous Analysis

**Algorithm**  
1. **Parse** each prompt and candidate answer into a *compositional semantic graph* (CSG). Nodes are predicates (e.g., `GreaterThan`, `Cause`, `Negate`) or constants (numbers, entities). Edges encode argument slots (subject, object, modifier). Parsing uses a fixed set of regex patterns that extract:  
   - Negation tokens (`not`, `no`) → `Negate` node.  
   - Comparatives (`>`, `<`, `more than`, `less than`) → `GreaterThan`/`LessThan` with numeric constants.  
   - Conditionals (`if … then …`) → `Implies` node linking antecedent and consequent sub‑graphs.  
   - Causal cues (`because`, `leads to`, `results in`) → `Cause`.  
   - Ordering/temporal (`before`, `after`, `first`, `last`) → `Before`/`After`.  
   The CSG is stored as a list of triples `(predicate, arg1, arg2)`; missing arguments are filled with a special `NULL` token. All triples are converted to a fixed‑length feature vector **v** ∈ ℝᴰ using a hand‑crafted one‑hot encoding for predicate type plus normalized numeric values (numpy arrays).  

2. **Clonal‑selection hypothesis generation**:  
   - Initialise a hypothesis pool **H₀** with the CSG of each candidate answer.  
   - For each hypothesis **h** ∈ **Hᵢ**, compute its *explanatory score* s(h) = exp(−‖vₚ − vₑ‖₂) where vₚ is the hypothesis vector, vₑ is the prompt (evidence) vector, and ‖·‖₂ is Euclidean distance (numpy.linalg.norm).  
   - Select the top‑k hypotheses (e.g., k=5) proportionally to s(h).  
   - Clone each selected hypothesis **c** times (c = round(s(h)·Cmax)).  
   - Apply mutation operators to clones: randomly swap one argument, insert/delete a `Negate` node, or perturb a numeric constant by ±ε (ε=0.1 of its range).  
   - Form the next pool **Hᵢ₊₁** from all clones; repeat for T=3 iterations.  

3. **Scoring**: After the final iteration, the score of a candidate answer is the maximum s(h) over all hypotheses derived from it. Higher scores indicate better abductive fit to the prompt under compositional semantics.  

**Structural features parsed** – negations, comparatives, conditionals, numeric constants, causal claims, ordering/temporal relations.  

**Novelty** – While clonal selection, abductive scoring, and compositional semantics each appear separately in cognitive models or NLP pipelines, their tight integration — using a mutation‑selection loop over logically parsed graphs to optimise explanatory fit — has not been described in the public literature for answer scoring.  

**Ratings**  
Reasoning: 8/10 — The algorithm directly measures explanatory compatibility via distance in a logical feature space, capturing relational reasoning beyond surface similarity.  
Metacognition: 6/10 — It monitors hypothesis quality through clonal expansion but lacks explicit self‑reflection on search adequacy or uncertainty calibration.  
Hypothesis generation: 9/10 — Clonal‑selection with mutation provides a rich, stochastic hypothesis space guided by explanatory scores, enabling diverse abductive candidates.  
Implementability: 7/10 — All steps rely on regex parsing, numpy vector ops, and simple loops; no external libraries or APIs are needed, though careful tuning of mutation rates and iteration count is required.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 9/10 |
| Implementability | 7/10 |
| **Composite** | **7.67** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: validation:syntax_error: '(' was never closed (line 352)

**Forge Timestamp**: 2026-04-01T19:24:45.499719

---

## Code

**Source**: scrap

[View code](./Immune_Systems---Abductive_Reasoning---Compositional_Semantics/tool.py)

<details>
<summary>Show code</summary>

```python
class ReasoningTool:
    """
    Implements an Abductive Reasoning Engine using Clonal Selection over Compositional Semantic Graphs (CSG).
    
    Mechanism:
    1. Parsing: Converts text into a CSG (nodes=predicates/constants, edges=arguments).
       Handles negation, comparatives, conditionals, causality, and temporal ordering.
    2. Hypothesis Generation (Clonal Selection):
       - Initializes hypotheses from candidate answers.
       - Scores fit to prompt evidence via Euclidean distance in feature space.
       - Selects top-k, clones them proportionally to fitness, and mutates (swap args, toggle negation, perturb numbers).
       - Iterates T=3 times to converge on the best explanatory fit.
    3. Epistemic Honesty (Tier B): Detects ambiguity, presupposition, and unanswerability to cap confidence.
    4. Scoring: Combines structural fit (CSG distance), computational verification (math/logic), and NCD (tiebreaker).
    """

    def __init__(self):
        self.predicates = ['Negate', 'GreaterThan', 'LessThan', 'Implies', 'Cause', 'Before', 'After', 'Equal', 'NULL']
        self.p_idx = {p: i for i, p in enumerate(self.predicates)}
        self.D = len(self.predicates) + 5  # Predicate one-hot + num_val, num_flag, arg1_hash, arg2_hash, length_norm

    def _parse_to_csg(self, text: str) -> List[Tuple[str, str, str]]:
        """Parse text into CSG triples (predicate, arg1, arg2)."""
        triples = []
        text_lower = text.lower()
        
        # 1. Negation
        if re.search(r'\b(not|no|never|none)\b', text_lower):
            triples.append(('Negate', 'GLOBAL', 'TRUE'))
        
        # 2. Comparatives & Numbers
        num_pattern = r'(-?\d+\.?\d*)'
        numbers = [float(x) for x in re.findall(num_pattern, text)]
        if len(numbers) >= 2:
            # Simple heuristic: first number > second number if "more/greater" exists, else <
            if any(x in text_lower for x in ['more', 'greater', 'larger', 'above']):
                triples.append(('GreaterThan', str(numbers[0]), str(numbers[1])))
            elif any(x in text_lower for x in ['less', 'smaller', 'below', 'fewer']):
                triples.append(('LessThan', str(numbers[0]), str(numbers[1])))
            else:
                # Default ordering assumption or equality check
                triples.append(('Equal', str(numbers[0]), str(numbers[1])))
        elif len(numbers) == 1:
             triples.append(('NULL', 'NUM_CONST', str(numbers[0])))

        # 3. Conditionals
        if re.search(r'\bif\b.*\bthen\b|\bimplies\b|\bleads to\b', text_lower):
            triples.append(('Implies', 'ANTECEDENT', 'CONSEQUENT'))
            
        # 4. Causality
        if re.search(r'\bbecause\b|\bcauses\b|\bresults in\b', text_lower):
            triples.append(('Cause', 'CAUSE', 'EFFECT'))
            
        # 5. Temporal
        if re.search(r'\bbefore\b', text_lower):
            triples.append(('Before', 'EVENT_A', 'EVENT_B'))
        if re.search(r'\bafter\b', text_lower):
            triples.append(('After', 'EVENT_A', 'EVENT_B'))

        # Fallback for empty parse
        if not triples:
            triples.append(('NULL', 'ROOT', text[:20]))
            
        return triples

    def _vectorize(self, triples: List[Tuple[str, str, str]]) -> np.ndarray:
        """Convert CSG triples to a fixed-length feature vector."""
        vec = np.zeros(self.D)
        if not triples:
            return vec
            
        # Aggregate predicate counts (one-hot-ish)
        pred_counts = {}
        nums = []
        for p, a1, a2 in triples:
            if p in self.p_idx:
                pred_counts[p] = pred_counts.get(p, 0) + 1
            # Extract numbers for normalization
            try:
                if a1 and a1 not in ['GLOBAL', 'TRUE', 'FALSE', 'NULL', 'ROOT']:
                    nums.append(float(a1))
                if a2 and a2 not in ['GLOBAL', 'TRUE', 'FALSE', 'NULL', 'ROOT']:
                    nums.append(float(a2))
            except ValueError:
                pass
        
        # Fill predicate slots
        for p, count in pred_counts.items():
            if p in self.p_idx:
                vec[self.p_idx[p]] = min(count, 1.0) # Normalize count
        
        # Numeric features
        if nums:
            vec[len(self.predicates)] = np.mean(nums) / 100.0 # Normalized mean
            vec[len(self.predicates)+1] = 1.0 # Num flag
            
        # Simple hash-based arg distribution (mocked via length for simplicity in limited space)
        vec[len(self.predicates)+2] = len(triples) / 10.0 
        
        return vec

    def _compute_explanatory_score(self, v_prompt: np.ndarray, v_hyp: np.ndarray) -> float:
        """Calculate s(h) = exp(-||v_p - v_h||_2)."""
        dist = np.linalg.norm(v_prompt - v_hyp)
        return math.exp(-dist)

    def _mutate(self, triples: List[Tuple[str, str, str]], rate: float = 0.2) -> List[Tuple[str, str, str]]:
        """Apply mutation operators: swap args, toggle negation, perturb numbers."""
        new_triples = []
        for p, a1, a2 in triples:
            # Clone
            tp = (p, a1, a2)
            
            # Mutate: Toggle Negate
            if np.random.rand() < rate and p == 'Negate':
                tp = ('NULL', a1, a2) # Remove negation
            elif np.random.rand() < rate and p != 'Negate':
                if 'not' in str(a1).lower() or 'not' in str(a2).lower():
                     pass # Already negative context
                else:
                    # Add negation context loosely
                    tp = ('Negate', a1, a2)

            # Mutate: Perturb numbers
            try:
                if np.random.rand() < rate:
                    if a1 not in ['GLOBAL', 'TRUE', 'FALSE', 'NULL', 'ROOT', 'ANTECEDENT', 'CONSEQUENT', 'CAUSE', 'EFFECT', 'EVENT_A', 'EVENT_B']:
                        val = float(a1)
                        val += np.random.normal(0, 0.1)
                        tp = (p, f"{val:.2f}", a2)
            except: pass
            
            new_triples.append(tp)
        return new_triples

    def _clonal_selection(self, prompt_triples: List, candidate_triples_list: List[List]) -> Tuple[float, List]:
        """Run clonal selection algorithm to find best fit hypothesis."""
        v_prompt = self._vectorize(prompt_triples)
        
        # Initialize pool H0 from candidates
        # We treat each candidate's parsed graph as an initial hypothesis
        H = []
        for i, triples in enumerate(candidate_triples_list):
            H.append({'source_idx': i, 'triples': triples, 'vec': self._vectorize(triples)})
        
        T = 3 # Iterations
        C_max = 5
        
        for _ in range(T):
            if not H: break
            
            # Score all
            scores = []
            for h in H:
                s = self._compute_explanatory_score(v_prompt, h['vec'])
                scores.append(s)
            
            # Select top-k (proportional selection simulation)
            total_score = sum(scores) + 1e-9
            probs = [s/total_score for s in scores]
            
            # Select top 5 or all if fewer
            selected_indices = np.argsort(scores)[-5:]
            selected_hypotheses = [H[i] for i in selected_indices]
            
            next_H = []
            for h in selected_hypotheses:
                s = self._compute_explanatory_score(v_prompt, h['vec'])
                clones = round(s * C_max)
                for _ in range(max(1, clones)):
                    mutated_triples = self._mutate(h['triples'])
                    next_H.append({
                        'source_idx': h['source_idx'],
                        'triples': mutated_triples,
                        'vec': self._vectorize(mutated_triples)
                    })
            
            H = next_H

        # Final scoring: Max score over all derived hypotheses for each original candidate
        final_scores = {}
        for h in H:
            s = self._compute_explanatory_score(v_prompt, h['vec'])
            idx = h['source_idx']
            if idx not in final_scores or s > final_scores[idx]:
                final_scores[idx] = s
        
        # Ensure all original candidates have a score (even if 0 from elimination)
        for i in range(len(candidate_triples_list)):
            if i not in final_scores:
                # Re-calculate direct distance if eliminated
                v_c = self._vectorize(candidate_triples_list[i])
                final_scores[i] = self._compute_explanatory_score(v_prompt, v_c)
                
        best_score = max(final_scores.values()) if final_scores else 0.0
        return best_score, final_scores

    def _compute_structural_score(self, prompt: str, candidate: str) -> float:
        """Core reasoning: Parse and compute fit."""
        p_triples = self._parse_to_csg(prompt)
        c_triples = self._parse_to_csg(candidate)
        
        # Run clonal selection to get abductive fit score
        # We wrap the single candidate in a list for the algorithm, but since we need relative scoring,
        # we actually run the algorithm on the set of all candidates in evaluate().
        # Here, we just return the direct fit for single evaluation or helper.
        v_p = self._vectorize(p_triples)
        v_c = self._vectorize(c_triples)
        return self._compute_explanatory_score(v_p, v_c)

    def _check_computation(self, prompt: str, candidate: str) -> float:
        """
        Attempt to solve math/logic problems explicitly.
        Returns 1.0 if candidate matches computed answer, 0.0 otherwise, 0.5 if unsure.
        """
        p_lower = prompt.lower()
        
        # 1. Numeric Comparison / Extraction
        nums = [float(x) for x in re.findall(r'-?\d+\.?\d*', prompt)]
        if 'which is larger' in p_lower or 'greater' in p_lower:
            if len(nums) >= 2:
                expected = str(max(nums))
                if expected in candidate or str(int(max(nums))) in candidate:
                    return 1.0
                return 0.1

        # 2. Simple Arithmetic (e.g., "What is 5 + 3?")
        match = re.search(r'what is\s+(-?\d+\.?\d*)\s*([\+\-\*\/])\s*(-?\d+\.?\d*)', p_lower)
        if match:
            n1, op, n2 = float(match.group(1)), match.group(2), float(match.group(3))
            res = 0
            if op == '+': res = n1 + n2
            elif op == '-': res = n1 - n2
            elif op == '*': res = n1 * n2
            elif op == '/': res = n1 / n2 if n2 != 0 else 0
            
            if str(res) in candidate or f"{res:.1f}" in candidate or f"{res:.0f}" in candidate:
                return 1.0
            return 0.1

        # 3. Bat-and-Ball style (x + (x+delta) = total)
        # Pattern: "A and B cost $X. A costs $Y more than B." -> Not robust enough for regex only without LLM, 
        # but we can try simple linear extraction if structure is clear. Skipping complex algebraic parsing for brevity,
        # relying on CSG fit for structural similarity.
        
        return 0.5 # Neutral if no specific computation triggered

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Returns a cap on confidence based on prompt properties.
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        presupposition_triggers = ['have you stopped', 'did you stop', 'why did', 'when did', 'quit', 'fail to']
        if any(t in p_lower for t in presupposition_triggers):
            # Check if it implies a prior state that might not exist
            if 'stop' in p_lower or 'quit' in p_lower or 'fail' in p_lower:
                return 0.25

        # 2. Scope/Pronoun Ambiguity
        if re.search(r'\bevery\s+\w+.*\ba\s+\w+\b', p_lower) and 'same' not in p_lower:
            # "Every X did a Y" - ambiguous if Y is same instance
            pass # Hard to detect purely, but flag if "who" question follows
        if re.search(r'\btold\s+\w+\s+he\b', p_lower) or re.search(r'\bsaid\s+to\s+\w+\s+he\b', p_lower):
            if 'who' in p_lower:
                return 0.2 # Pronoun ambiguity with explicit question

        # 3. False Dichotomy
        if re.search(r'\beither\s+.*\bor\s+.*\?', p_lower):
            # Check for exhaustive markers like "only"
            if 'only' not in p_lower:
                return 0.4 # Potential false dichotomy

        # 4. Subjectivity
        subjective_words = ['best', 'worst', 'favorite', 'beautiful', 'ugly', 'opinion']
        if any(w in p_lower for w in subjective_words):
            if 'objective' not in p_lower and 'data' not in p_lower:
                return 0.3

        # 5. Unanswerability / Missing Info
        if 'cannot be determined' in p_lower or 'insufficient' in p_lower:
            return 0.1
        
        # If the prompt is extremely short or lacks verbs, it might be nonsense
        if len(re.findall(r'\w+', prompt)) < 3:
            return 0.2
            
        return 1.0 # No obvious traps detected

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        b1, b2 = s1.encode(), s2.encode()
        l1, l2 = len(b1), len(b2)
        if l1 == 0 or l2 == 0: return 1.0
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            ncd = (c12 - min(c1, c2)) / max(c1, c2, 1)
            return max(0.0, min(1.0, ncd))
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # 1. Parse Prompt
        p_triples = self._parse_to_csg(prompt)
        v_prompt = self._vectorize(p_triples)
        
        # 2. Parse Candidates
        c_triples_list = [self._parse_to_csg(c) for c in candidates]
        
        # 3. Run Clonal Selection for Abductive Fit
        # We pass the whole list to allow relative comparison within the algorithm if needed,
        # but the algorithm defined above returns scores for indices.
        max_abductive_score, score_map = self._clonal_selection(p_triples, c_triples_list)
        
        results = []
        meta_cap = self._meta_confidence(prompt)
        
        for i, cand in enumerate(candidates):
            # A. Structural/Abductive Score (from clonal selection)
            abductive_score = score_map.get(i, 0.0)
            
            # B. Computational Score (Explicit math/logic)
            comp_score = self._check_computation(prompt, cand)
            
            # C. NCD Tiebreaker (Max 15% weight logic handled in aggregation)
            ncd_val = self._ncd_score(prompt, cand)
            ncd_score = 1.0 - ncd_val # Convert distance to similarity
            
            # Aggregation:
            # Structural >= 50%, Computation >= 20%, NCD <= 15%
            # We normalize abductive_score (0-1) and comp_score (0-1)
            
            # If computation gives a definitive 1.0 or 0.0, it dominates
            if comp_score == 1.0:
                final_score = 0.95
            elif comp_score == 0.0:
                final_score = 0.05
            else:
                # Weighted sum
                # Base score from abductive reasoning (CSG fit)
                base_score = abductive_score 
                # Boost if computation hints at correctness
                if comp_score > 0.5:
                    base_score = min(1.0, base_score + 0.
```

</details>
