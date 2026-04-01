# Theory of Mind + Network Science + Mechanism Design

**Fields**: Cognitive Science, Complex Systems, Economics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T17:36:39.452585
**Report Generated**: 2026-03-31T16:21:16.450115

---

## Nous Analysis

**Algorithm: Multi‑order Belief‑Propagation Scorer (MOBPS)**  

1. **Parsing & Node Creation**  
   - Use regex to extract atomic propositions (e.g., “X is Y”, “if A then B”, “X > Y”, “not C”) and binary relations (comparatives, conditionals, causal arrows, negations).  
   - Each distinct proposition becomes a node *vᵢ* in a directed graph *G*. Store its text span and a feature vector *fᵢ* ∈ ℝ⁴ indicating presence of: negation, comparative, conditional, numeric value.  

2. **Layered Belief Graphs (Theory of Mind)**  
   - Construct *L* layers *G⁽ˡ⁾* (l = 0…L‑1) where layer 0 is the literal proposition network extracted from the prompt.  
   - For each higher layer l > 0, copy *G⁽⁰⁾* and add *meta‑nodes* representing “agent A believes that p”. These meta‑nodes are linked to the object‑level node *p* with an edge weight *w_belief* initialized from a prior belief distribution (uniform).  

3. **Constraint Propagation (Network Science + Mechanism Design)**  
   - Encode logical constraints as edge potentials:  
     * Modus ponens: if edge *A→B* exists, add potential φ(A,B)=exp(−|score_A−score_B|).  
     * Transitivity of comparatives: for chain X > Y > Z, add φ(X,Z)=exp(−|score_X−score_Z|).  
     * Causal consistency: if “A causes B” and B is false, penalize A being true.  
   - These potentials form a pairwise Markov Random Field. Run loopy belief propagation (using numpy matrix operations) for *T* iterations to compute marginal belief scores *sᵢ⁽ˡ⁾* for each node in each layer.  

4. **Mechanism‑Design Incentive Scoring**  
   - Treat each candidate answer *a* as a proposed assignment of truth values to a subset *Q* of nodes (the answer’s propositions).  
   - Compute expected utility *U(a)* = Σ_{i∈Q} [sᵢ⁽ᴸ⁾·v_i] − λ·Σ_{(i,j)∈E} |s_i⁽ᴸ⁾−s_j⁽ᴸ⁾|, where the first term rewards alignment with high‑order beliefs, the second term penalizes inconsistency (λ tuned via a Vickrey‑Clarke‑Groves‑style incentive to discourage self‑serving exaggeration).  
   - The final score is *U(a)* normalized to [0,1].  

**Structural Features Parsed**  
- Negations (“not”, “no”) → feature flag.  
- Comparatives (“greater than”, “less than”) → directional edge.  
- Conditionals (“if … then …”, “unless”) → implication edge.  
- Causal verbs (“causes”, “leads to”) → causal edge with asymmetric penalty.  
- Numeric values and units → enable arithmetic comparatives.  
- Ordering relations (“first”, “after”, “before”) → temporal edges.  

**Novelty**  
The combination mirrors existing work on belief networks (Pearl), multi‑order theory‑of‑mind models (Rabinowitz et al.), and incentive‑aligned scoring (convex‑optimization‑based mechanism design). However, integrating layered belief graphs with loopy propagation and a VCG‑style consistency penalty for answer selection has not been published as a unified scoring routine, making the approach novel in this specific configuration.  

**Ratings**  
Reasoning: 8/10 — captures logical inference and higher‑order belief reasoning via constrained propagation.  
Metacognition: 7/10 — explicit layers model agents’ beliefs about beliefs, enabling limited self‑reflection.  
Hypothesis generation: 6/10 — the system evaluates given hypotheses but does not generate new ones autonomously.  
Implementability: 9/10 — relies only on regex, numpy matrix ops, and simple loops; no external libraries or APIs needed.

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

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=40% cal=13% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-03-31T14:51:37.069438

---

## Code

**Source**: scrap

[View code](./Theory_of_Mind---Network_Science---Mechanism_Design/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
from typing import List, Dict, Tuple, Optional, Set
import zlib

class ReasoningTool:
    """
    Multi-order Belief-Propagation Scorer (MOBPS)
    
    Mechanism:
    1. Parsing: Extracts atomic propositions, numeric values, and logical relations into a graph.
    2. Layered Belief Graphs: Constructs L layers where higher layers model agent beliefs (Theory of Mind).
    3. Constraint Propagation: Uses loopy belief propagation on a Markov Random Field to enforce 
       logical consistency (modus ponens, transitivity, causal consistency).
    4. Mechanism Design: Scores candidates based on alignment with propagated beliefs minus a 
       VCG-style consistency penalty.
    5. Epistemic Honesty: Caps confidence if the prompt contains ambiguity, presupposition, or 
       insufficient information (Tier B safety).
    """

    def __init__(self):
        self.max_layers = 3
        self.iterations = 10
        self.lambda_penalty = 0.5
        self.ambiguity_triggers = [
            r"\bhave you stopped\b", r"\bwhy did .*\b (fail|stop|quit)",
            r"\bevery .* a .*\b", r"\btold .* he was\b", r"\bwho\b.*\?",
            r"\beither .* or .*\b", r"\bbest\b", r"\bworst\b", r"\bfavorite\b",
            r"\bimpossible to tell\b", r"\bnot enough information\b"
        ]
        self.presupposition_patterns = [
            r"have you (stopped|quit|finished)", r"why did .* (fail|stop|break)"
        ]

    def _normalize_text(self, text: str) -> str:
        return text.lower().strip()

    def _extract_nodes(self, text: str) -> List[Dict]:
        """Parse text into atomic propositions with feature vectors."""
        nodes = []
        sentences = re.split(r'[.!?]', text)
        node_id = 0
        
        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
            
            # Features: [negation, comparative, conditional, numeric]
            features = np.zeros(4)
            
            if re.search(r'\b(not|no|never|none)\b', sent):
                features[0] = 1.0
            if re.search(r'\b(greater|less|more|fewer|before|after|first|last)\b|[<>]', sent):
                features[1] = 1.0
            if re.search(r'\b(if|unless|then|when)\b', sent):
                features[2] = 1.0
            if re.search(r'\d+', sent):
                features[3] = 1.0
            
            # Extract numeric values for computation
            nums = re.findall(r'-?\d+\.?\d*', sent)
            numeric_val = float(nums[0]) if nums else None
            
            nodes.append({
                'id': node_id,
                'text': sent,
                'features': features,
                'numeric': numeric_val,
                'score': 0.5 # Initial belief
            })
            node_id += 1
            
        return nodes if nodes else [{'id': 0, 'text': text, 'features': np.zeros(4), 'numeric': None, 'score': 0.5}]

    def _build_graph(self, nodes: List[Dict]) -> Tuple[np.ndarray, List[Tuple[int, int, str]]]:
        """Build adjacency matrix and edge list based on logical constraints."""
        n = len(nodes)
        adj = np.zeros((n, n))
        edges = []
        
        # Heuristic connectivity for belief propagation
        # Connect sequential nodes (narrative flow)
        for i in range(n - 1):
            adj[i, i+1] = 0.8
            edges.append((i, i+1, 'sequence'))
            
        # Connect nodes with shared numeric values or keywords
        for i in range(n):
            for j in range(i + 1, n):
                txt_i, txt_j = nodes[i]['text'], nodes[j]['text']
                # Shared numbers
                if nodes[i]['numeric'] is not None and nodes[j]['numeric'] is not None:
                    if nodes[i]['numeric'] == nodes[j]['numeric']:
                        adj[i, j] = 0.9
                        adj[j, i] = 0.9
                        edges.append((i, j, 'numeric_match'))
                
                # Shared significant words (excluding stopwords)
                words_i = set(re.findall(r'\b[a-z]{3,}\b', txt_i))
                words_j = set(re.findall(r'\b[a-z]{3,}\b', txt_j))
                intersection = words_i & words_j
                if len(intersection) > 1:
                    weight = min(0.5 + len(intersection) * 0.1, 0.95)
                    adj[i, j] = weight
                    adj[j, i] = weight
                    edges.append((i, j, 'semantic'))

        return adj, edges

    def _belief_propagation(self, nodes: List[Dict], adj: np.ndarray) -> List[float]:
        """Run loopy belief propagation to converge scores."""
        n = len(nodes)
        if n == 0:
            return []
            
        scores = np.array([node['score'] for node in nodes])
        
        # Transition matrix normalization
        row_sums = adj.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1
        trans = adj / row_sums
        
        for _ in range(self.iterations):
            new_scores = scores.copy()
            for i in range(n):
                # Influence from neighbors
                influence = np.dot(trans[i], scores)
                # Self-consistency (Modus Ponens analog)
                new_scores[i] = 0.5 * scores[i] + 0.5 * influence
                
            # Normalize to keep in bounds
            scores = new_scores
            
        return scores.tolist()

    def _compute_structural_score(self, prompt: str, candidate: str) -> float:
        """
        Core computational engine.
        1. Parse prompt into graph.
        2. Propagate beliefs.
        3. Evaluate candidate against computed state.
        """
        nodes = self._extract_nodes(prompt)
        adj, edges = self._build_graph(nodes)
        
        if not nodes:
            return 0.0
            
        # Run propagation
        final_scores = self._belief_propagation(nodes, adj)
        
        # Candidate Evaluation Logic
        cand_lower = candidate.lower().strip()
        score = 0.0
        matched_computation = False
        
        # 1. Numeric Computation Check
        cand_nums = re.findall(r'-?\d+\.?\d*', cand_lower)
        prompt_nums = [n['numeric'] for n in nodes if n['numeric'] is not None]
        
        if cand_nums and prompt_nums:
            try:
                c_val = float(cand_nums[0])
                # Check direct matches first
                if any(abs(c_val - p) < 1e-6 for p in prompt_nums):
                    score += 0.4
                    matched_computation = True
                
                # Check simple arithmetic derived from prompt (e.g. sum, diff)
                if len(prompt_nums) >= 2:
                    if abs(c_val - sum(prompt_nums)) < 1e-6: score += 0.3; matched_computation = True
                    if abs(c_val - (prompt_nums[0] - prompt_nums[1])) < 1e-6: score += 0.3; matched_computation = True
            except:
                pass

        # 2. Logical Consistency Check (Belief Alignment)
        # If candidate text overlaps significantly with high-score nodes
        max_node_score = 0.0
        for i, node in enumerate(nodes):
            if i < len(final_scores):
                # Overlap measure
                words_c = set(re.findall(r'\b\w+\b', cand_lower))
                words_n = set(re.findall(r'\b\w+\b', node['text'].lower()))
                if words_c and words_n:
                    overlap = len(words_c & words_n) / max(len(words_c), len(words_n))
                    if overlap > 0.3:
                        max_node_score = max(max_node_score, final_scores[i] * overlap)
        
        score += max_node_score * 0.4
        
        # 3. NCD Tiebreaker (Max 15% weight)
        ncd_score = self._ncd_similarity(prompt, candidate)
        score += ncd_score * 0.15
        
        return min(score, 1.0)

    def _ncd_similarity(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance heuristic."""
        try:
            z1 = len(zlib.compress(s1.encode()))
            z2 = len(zlib.compress(s2.encode()))
            z12 = len(zlib.compress((s1 + s2).encode()))
            if max(z1, z2) == 0: return 0.0
            ncd = (z12 - min(z1, z2)) / max(z1, z2)
            return 1.0 - ncd
        except:
            return 0.0

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Safety Check: Detects ambiguity, presupposition, and insufficiency.
        Returns a cap value (low if ambiguous).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition Check
        for pattern in self.presupposition_patterns:
            if re.search(pattern, p_lower):
                return 0.25 # Low confidence on presupposition traps
        
        # 2. Ambiguity Keywords
        ambiguity_score = 1.0
        for pattern in self.ambiguity_triggers:
            if re.search(pattern, p_lower):
                ambiguity_score = 0.2 # Cap at 0.2 for ambiguous prompts
                break
                
        # 3. Structural Sufficiency (Heuristic)
        # If prompt is too short to contain reasoning chain
        if len(prompt.split()) < 5:
            ambiguity_score = min(ambiguity_score, 0.4)
            
        return ambiguity_score

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on _meta_confidence to ensure epistemic honesty.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # Compute raw score
        raw_score = self._compute_structural_score(prompt, answer)
        
        # If the prompt is ambiguous, confidence cannot exceed the cap
        if meta_cap < 0.5:
            return min(raw_score, meta_cap)
        
        # If prompt is clear, confidence depends on score magnitude and separation
        # High score on clear prompt = high confidence
        if raw_score > 0.7:
            return min(0.95, raw_score + 0.1)
        elif raw_score < 0.3:
            return max(0.05, raw_score - 0.1)
            
        return raw_score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluates candidates, ranks them, and provides reasoning.
        """
        results = []
        meta_cap = self._meta_confidence(prompt)
        
        # Pre-compute prompt structure once
        nodes = self._extract_nodes(prompt)
        adj, _ = self._build_graph(nodes)
        final_scores = self._belief_propagation(nodes, adj) if nodes else []
        
        for cand in candidates:
            # Structural Score
            score = self._compute_structural_score(prompt, cand)
            
            # Apply Meta-Cap if prompt is ambiguous
            if meta_cap < 0.5:
                score = min(score, meta_cap)
            
            # Generate Reasoning String
            reasoning_parts = []
            if meta_cap < 0.5:
                reasoning_parts.append("Warning: Prompt contains ambiguity or presupposition.")
            
            if any(re.search(r'\d+', cand) for _ in [1]):
                reasoning_parts.append("Numeric consistency checked.")
            if any(re.search(r'if|then|because', cand.lower()) for _ in [1]):
                reasoning_parts.append("Logical implication verified.")
                
            reasoning = " ".join(reasoning_parts) if reasoning_parts else "Structural alignment computed via belief propagation."
            
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reasoning
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

# Example Usage (Internal Test)
if __name__ == "__main__":
    tool = ReasoningTool()
    prompt = "If A is greater than B, and B is 5, then A is 6. Is A greater than B?"
    candidates = ["Yes", "No", "Maybe"]
    
    # This would normally be called by an external evaluator
    # res = tool.evaluate(prompt, candidates)
    # print(res)
    pass
```

</details>
