# Renormalization + Falsificationism + Free Energy Principle

**Fields**: Physics, Philosophy, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T01:10:43.108646
**Report Generated**: 2026-04-01T20:30:43.456123

---

## Nous Analysis

**Algorithm**  
1. **Parsing** – Use regex to extract propositions from the prompt and each candidate answer. A proposition is a tuple `(id, text, polarity, type)` where `polarity ∈ {+1,−1}` marks negation and `type` ∈ `{assertion, conditional, causal, comparative, numeric}`. Store propositions in a list `props`.  
2. **Factor graph** – Create nodes for each proposition. For every pair `(i,j)` add an undirected edge with weight `w_ij` computed from logical overlap:  
   - If both are assertions, `w_ij = Jaccard(set(words_i), set(words_j))`.  
   - If one is a conditional `A→B` and the other matches `A` or `B`, increase weight by 0.5.  
   - If polarities conflict (`+1` vs `−1`) on overlapping content, set `w_ij = −0.5` (falsification penalty).  
   Edges are kept in an adjacency list `graph`.  
3. **Belief initialization** – Assign each node a belief `b_i = 0.5` (probability of being true).  
4. **Variational free‑energy minimization (loopy BP)** – Iterate `T=10` times:  
   - Message from `i` to `j`: `m_{i→j} = σ( Σ_{k∈N(i)\j} w_{ik}·logit(b_k) )`, where `σ` is logistic.  
   - Update belief: `b_i = σ( Σ_{k∈N(i)} w_{ik}·logit(m_{k→i}) )`.  
   - Compute local free energy `F_i = b_i·log(b_i)+(1−b_i)·log(1−b_i) − Σ_{k∈N(i)} w_{ik}·b_i·b_k`.  
   - Total free energy `F = Σ_i F_i`.  
5. **Renormalization (coarse‑graining)** – After each BP sweep, cluster nodes with `|b_i−b_j|<ε` (ε=0.1) into a super‑node whose belief is the average and whose edges inherit summed weights. Replace clustered nodes, rebuild `graph`, and continue. This implements a scale‑dependent description; fixed points occur when clustering no longer changes the graph.  
6. **Scoring** – For each candidate answer, compute its free energy `F_cand`. Lower `F` indicates better alignment with the prompt’s constraints (fewer contradictions, higher predictive accuracy). Final score = `−F_cand` normalized to `[0,1]`.

**Structural features parsed**  
Negations (`not`, `no`), comparatives (`greater than`, `less than`, `>`, `<`), conditionals (`if … then`, `unless`), causal claims (`because`, `leads to`, `results in`), ordering relations (`first`, `second`, `before`, `after`), numeric values and units, quantifiers (`all`, `some`, `none`).

**Novelty**  
The blend of variational free‑energy minimization (Free Energy Principle) with hierarchical renormalization‑group style coarse‑graining and explicit falsification penalties is not found in standard probabilistic soft logic or Markov Logic Networks; those use static weighting. This combination introduces a dynamic, scale‑aware belief update that directly penalizes contradictions, making it algorithmically novel.

**Rating**  
Reasoning: 7/10 — captures logical structure and uncertainty but relies on heuristic weights.  
Metacognition: 6/10 — free‑energy term offers a self‑assessment of prediction error, yet no explicit reflection on reasoning process.  
Hypothesis generation: 5/10 — can propose alternative beliefs via BP, but lacks guided search for novel hypotheses.  
Implementability: 8/10 — uses only regex, numpy for matrix/logistic ops, and standard library data structures.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 8/10 |
| **Composite** | **6.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: validation:confidence_out_of_range: -0.09090909080991727

**Forge Timestamp**: 2026-04-01T17:00:00.086460

---

## Code

**Source**: scrap

[View code](./Renormalization---Falsificationism---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import math
import zlib
from collections import defaultdict
from typing import List, Dict, Tuple, Any

# --- Helper Functions for Logic & Math ---

def logistic(x):
    try:
        return 1.0 / (1.0 + math.exp(-x))
    except OverflowError:
        return 1.0 if x > 0 else 0.0

def logit(p):
    if p <= 0: return -10.0
    if p >= 1: return 10.0
    return math.log(p / (1.0 - p))

def ncd(s1: str, s2: str) -> float:
    """Normalized Compression Distance using zlib."""
    s1_b = s1.encode('utf-8')
    s2_b = s2.encode('utf-8')
    c1 = len(zlib.compress(s1_b))
    c2 = len(zlib.compress(s2_b))
    c12 = len(zlib.compress(s1_b + s2_b))
    min_c = min(c1, c2)
    if min_c == 0: return 0.0
    return (c12 - min_c) / (max(c1, c2) - min_c + 1e-9)

# --- Structural Parsers (Adversarial Robust) ---

class StructuralParser:
    """Extracts logical propositions and constraints regardless of variable names."""
    
    # Generic patterns for structural extraction
    PATTERNS = {
        'negation': [r'\b(not|no|never|without|none)\b', r'\bdoesn\'t\b', r'\bdidn\'t\b', r'\bwon\'t\b'],
        'conditional': [r'\bif\b.*\bthen\b', r'\bunless\b', r'\bonly if\b', r'\bimplies\b'],
        'causal': [r'\bcauses?\b', r'\bleads to\b', r'\bresults in\b', r'\bproduces\b', r'\bmakes\b'],
        'comparative': [r'\b(more|less|greater|smaller|higher|lower)\b', r'[<>]=?', r'\bfaster\b', r'\bslower\b'],
        'numeric': r'(\d+(?:\.\d+)?)\s*(?:times|multiplied by|plus|minus|added to|subtracted from|divided by)?\s*(\d+(?:\.\d+)?)?',
        'quantifier': [r'\b(all|every|some|none|no|at least one|most)\b'],
        'temporal': [r'\b(before|after|during|while|first|second|last)\b'],
        'identity': [r'\b(is|are|was|were|equals|means)\b']
    }

    def __init__(self):
        self.props = []

    def parse(self, text: str) -> List[Tuple]:
        """Returns list of (id, text, polarity, type)"""
        self.props = []
        text_lower = text.lower()
        sentences = re.split(r'[.!?]', text)
        
        pid = 0
        for sent in sentences:
            sent = sent.strip()
            if not sent: continue
            
            p_type = 'assertion'
            polarity = 1
            
            # Check Negation
            for pat in self.PATTERNS['negation']:
                if re.search(pat, sent_lower := sent.lower()):
                    polarity = -1
                    break
            
            # Check Type
            if any(re.search(p, sent_lower) for p in self.PATTERNS['conditional']):
                p_type = 'conditional'
            elif any(re.search(p, sent_lower) for p in self.PATTERNS['causal']):
                p_type = 'causal'
            elif any(re.search(p, sent_lower) for p in self.PATTERNS['comparative']) or re.search(r'[<>]', sent):
                p_type = 'comparative'
            elif any(re.search(p, sent_lower) for p in self.PATTERNS['temporal']):
                p_type = 'temporal'
            
            self.props.append((pid, sent, polarity, p_type))
            pid += 1
            
        return self.props

    def extract_numbers(self, text: str) -> List[float]:
        """Extracts all numeric values for computation."""
        matches = re.findall(r'-?\d+(?:\.\d+)?', text)
        return [float(m) for m in matches]

    def check_meta_traps(self, text: str) -> Dict[str, bool]:
        """Detects Tier B epistemic traps."""
        t = text.lower()
        traps = {
            'presupposition': bool(re.search(r'\b(have you stopped|did you stop|why did .+ fail|why is .+ wrong)\b', t)),
            'scope_ambiguity': bool(re.search(r'\b(every .+ a .+|same .+)\b', t)), # Simplified heuristic
            'pronoun_ambiguity': bool(re.search(r'\b(he|she|him|her|they)\b', t) and 'who' in t),
            'false_dichotomy': bool(re.search(r'\b(either .+ or .+|must be .+ or .+)\b', t)),
            'subjectivity': bool(re.search(r'\b(best|worst|favorite|beautiful|ugly)\b', t)),
            'unanswerable': bool(re.search(r'\b(unknown|impossible to tell|not enough info)\b', t))
        }
        # Additional check for missing info in math contexts
        nums = self.extract_numbers(text)
        if 'calculate' in t or 'sum' in t or 'total' in t:
            if len(nums) < 2: 
                traps['unanswerable'] = True
                
        return traps

# --- The Reasoning Engine ---

class ReasoningTool:
    """
    A reasoning tool implementing Renormalization x Falsificationism x Free Energy Principle.
    
    Mechanism:
    1. Parsing: Extracts logical propositions (assertions, conditionals, causals) with polarity.
    2. Factor Graph: Builds a graph where nodes are propositions. Edges represent logical overlap
       or contradiction (falsification penalty).
    3. Belief Propagation: Iteratively updates belief probabilities based on neighbor weights.
    4. Renormalization: Coarse-grains nodes with similar beliefs into super-nodes to find 
       scale-invariant truth states (fixed points).
    5. Scoring: Uses variational free energy to rank candidates. Lower energy = better fit.
    
    Adversarial Robustness: Relies on structural regex patterns (logic keywords) rather than 
    specific entity names or templates. Handles variable renaming and distractor sentences.
    """

    def __init__(self):
        self.parser = StructuralParser()
        self.epsilon = 0.1
        self.T = 10  # BP iterations

    def _build_graph(self, prompt_props: List[Tuple], cand_props: List[Tuple]) -> Dict[int, Dict[int, float]]:
        """Constructs adjacency list with weights based on logical overlap and falsification."""
        all_props = prompt_props + cand_props
        n = len(all_props)
        graph = defaultdict(dict)
        
        # Helper to get words
        def get_words(txt):
            return set(re.findall(r'\w+', txt.lower()))

        for i in range(n):
            for j in range(i + 1, n):
                id_i, txt_i, pol_i, type_i = all_props[i]
                id_j, txt_j, pol_j, type_j = all_props[j]
                
                words_i = get_words(txt_i)
                words_j = get_words(txt_j)
                
                # Jaccard similarity for assertions
                intersection = len(words_i & words_j)
                union = len(words_i | words_j)
                overlap = intersection / union if union > 0 else 0.0
                
                w = 0.0
                
                if type_i == 'assertion' and type_j == 'assertion':
                    w = overlap
                elif (type_i in ['conditional', 'causal'] and type_j in ['conditional', 'causal']):
                    # Check shared antecedents/consequents roughly
                    if intersection > 0: w = 0.5 + (0.5 * overlap)
                elif type_i != type_j:
                     if intersection > 0: w = 0.3 * overlap

                # Falsification Penalty: Conflicting polarities on overlapping content
                if overlap > 0.3 and pol_i != pol_j:
                    w = -0.5  # Strong penalty for contradiction
                
                if w != 0:
                    graph[i][j] = w
                    graph[j][i] = w
                    
        return graph

    def _run_bp_and_renorm(self, graph: Dict[int, Dict[int, float]], beliefs: List[float]) -> Tuple[List[float], float]:
        """Runs Loopy BP with Renormalization steps."""
        nodes = list(graph.keys())
        if not nodes:
            return beliefs, 0.0
            
        # Map original indices to current cluster indices if renormalizing
        # For simplicity in this implementation, we simulate clustering by averaging beliefs
        # of highly similar nodes after every 2 sweeps if they are close.
        
        current_beliefs = beliefs[:]
        n = len(current_beliefs)
        
        for t in range(self.T):
            new_beliefs = current_beliefs[:]
            
            # Message passing
            for i in nodes:
                sum_logit = 0.0
                for j, w_ij in graph[i].items():
                    if j < len(current_beliefs):
                        # Message from j to i
                        m_ji = logistic(w_ij * logit(current_beliefs[j]))
                        sum_logit += w_ij * logit(m_ji)
                
                # Update belief
                new_beliefs[i] = logistic(sum_logit)
            
            current_beliefs = new_beliefs
            
            # Renormalization (Coarse-graining) every 2 steps
            if t % 2 == 0 and t > 0:
                clustered = [False] * n
                new_graph = defaultdict(dict)
                new_beliefs_clustered = []
                mapping = {} # old_idx -> new_idx
                
                idx = 0
                for i in range(n):
                    if clustered[i]: continue
                    
                    cluster_nodes = [i]
                    clustered[i] = True
                    
                    # Find neighbors to cluster
                    for j in range(i+1, n):
                        if not clustered[j] and abs(current_beliefs[i] - current_beliefs[j]) < self.epsilon:
                            # Check connectivity
                            if j in graph[i] or any(k in graph[j] for k in cluster_nodes):
                                cluster_nodes.append(j)
                                clustered[j] = True
                    
                    # Create super-node
                    avg_b = sum(current_beliefs[k] for k in cluster_nodes) / len(cluster_nodes)
                    new_idx = len(new_beliefs_clustered)
                    new_beliefs_clustered.append(avg_b)
                    
                    for k in cluster_nodes:
                        mapping[k] = new_idx
                        
                    idx += 1
                
                # Rebuild graph for super-nodes
                for i_old, i_new in mapping.items():
                    for j_old, w in graph[i_old].items():
                        j_new = mapping[j_old]
                        if i_new != j_new:
                            if j_new in new_graph[i_new]:
                                new_graph[i_new][j_new] += w # Sum weights
                            else:
                                new_graph[i_new][j_new] = w
                                
                graph = new_graph
                current_beliefs = new_beliefs_clustered
                n = len(current_beliefs)
                nodes = list(range(n))

        # Compute Free Energy
        F = 0.0
        for i in nodes:
            b = current_beliefs[i]
            # Entropy term
            if b > 0 and b < 1:
                F += b * math.log(b) + (1-b) * math.log(1-b)
            # Interaction term
            for j, w in graph[i].items():
                if j < len(current_beliefs):
                    F -= w * b * current_beliefs[j]
                    
        return current_beliefs, F

    def _compute_structural_score(self, prompt: str, candidate: str) -> float:
        """Core logic: Parse, Graph, BP, Renormalize, Score."""
        p_props = self.parser.parse(prompt)
        c_props = self.parser.parse(candidate)
        
        if not p_props:
            return 0.5 # Neutral if no structure found
            
        # Combine for graph construction
        # We treat the candidate as a set of hypotheses to be tested against the prompt
        graph = self._build_graph(p_props, c_props)
        
        if not graph:
            # Fallback if graph is empty (no overlap)
            # Use NCD as a weak tiebreaker here
            return 1.0 - ncd(prompt, candidate)

        # Initialize beliefs: Prompt props start high (0.9), Candidate props start neutral (0.5)
        beliefs = []
        for i, (_, _, _, _) in enumerate(p_props):
            beliefs.append(0.9)
        for i, (_, _, _, _) in enumerate(c_props):
            beliefs.append(0.5)
            
        # Run inference
        final_beliefs, free_energy = self._run_bp_and_renorm(graph, beliefs)
        
        # Score is negative free energy, normalized roughly
        # Lower F is better. 
        # We invert and scale. F is usually negative for consistent systems.
        score = -free_energy / (len(graph) + 1) 
        return logistic(score * 10) # Scale to 0-1

    def _meta_confidence(self, prompt: str, answer: str) -> float:
        """Checks for Tier B traps and limits confidence."""
        traps = self.parser.check_meta_traps(prompt)
        
        # If any hard trap is detected, cap confidence
        if any(traps.values()):
            return 0.25 # Low confidence due to ambiguity/trap
            
        # Check for insufficient data in numeric problems
        p_nums = self.parser.extract_numbers(prompt)
        a_nums = self.parser.extract_numbers(answer)
        
        # Heuristic: If prompt asks for calculation but has < 2 numbers, low confidence
        if any(k in prompt.lower() for k in ['sum', 'total', 'calculate', 'add']) and len(p_nums) < 2:
            return 0.2
            
        return 1.0 # No obvious traps detected

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            # 1. Meta-check (Epistemic Honesty)
            meta_cap = self._meta_confidence(prompt, cand)
            
            # 2. Structural/Logical Score (85% weight)
            struct_score = self._compute_structural_score(prompt, cand)
            
            # 3. NCD Tiebreaker (15% weight max)
            # Only used if structural score is ambiguous or as a small bonus
            ncd_score = 1.0 - ncd(prompt, cand)
            
            # Weighted combination
            final_score = (0.85 * struct_score) + (0.15 * ncd_score)
            
            # Apply meta cap
            if final_score > meta_cap:
                final_score = meta_cap
                
            # Generate reasoning string
            reasoning = f"Structural alignment: {struct_score:.2f}. "
            if meta_cap < 0.3:
                reasoning += "Warning: Potential logical trap or ambiguity detected."
            elif final_score > 0.7:
                reasoning += "High consistency with prompt constraints."
            else:
                reasoning += "Moderate/Low consistency."
                
            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": reasoning
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1."""
        meta = self._meta_confidence(prompt, answer)
        if meta < 1.0:
            return meta
            
        score = self._compute_structural_score(prompt, answer)
        # Cap at 0.9 unless definitive computation (hard to guarantee without specific solvers)
        return min(score, 0.9)

# --- Example Usage / Self-Test ---
if __name__ == "__main__":
    tool = ReasoningTool()
    
    # Test 1: Logical Contradiction (Falsification)
    p1 = "All birds can fly. Penguins are birds. Penguins cannot fly."
    c1_good = "Some birds cannot fly."
    c1_bad = "All birds can fly."
    
    res1 = tool.evaluate(p1, [c1_good, c1_bad])
    print("Test 1 (Contradiction):")
    for r in res1:
        print(f" - {r['candidate']}: {r['score']} ({r['reasoning']})")
        
    # Test 2: Numeric/Structural
    p2 = "If X is greater than Y, and Y is 5, then X must be greater than 5."
    c2 = "X is 6."
    c2_bad = "X is 4."
    
    res2 = tool.evaluate(p2, [c2, c2_bad])
    print("\nTest 2 (Numeric/Comparative):")
    for r in res2:
        print(f" - {r['candidate']}: {r['score']}")

    # Test 3: Tier B Trap (Presupposition)
    p3 = "Have you stopped cheating on tests?"
    conf = tool.confidence(p3, "Yes")
    print(f"\nTest 3 (Trap Confidence): {conf}") # Should be low
```

</details>
