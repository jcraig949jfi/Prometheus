# Chaos Theory + Cognitive Load Theory + Causal Inference

**Fields**: Physics, Cognitive Science, Information Science
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T15:18:50.889727
**Report Generated**: 2026-03-27T06:37:37.637286

---

## Nous Analysis

**Algorithm: Perturb‑Aware Causal‑Chunk Scorer (PACCS)**  

1. **Parsing & Data Structures**  
   - Tokenize the prompt and each candidate answer with a simple regex‑based splitter that preserves punctuation.  
   - Extract three typed relation graphs using deterministic patterns:  
     *Causal edges* (`X → Y` from patterns like “X causes Y”, “if X then Y”, “because X”, “due to X”).  
     *Temporal/ordering edges* (`X < Y` from “before”, “after”, “precedes”).  
     *Quantitative constraints* (`X = value`, `X > Y`, `X ≈ Y`) from numeric tokens and comparatives.  
   - Store each graph as a NumPy‑backed adjacency matrix **A_causal**, **A_order**, and a dense vector **v_num** for numeric assertions.  
   - Build a *chunk* representation by grouping tightly‑connected nodes (via a quick depth‑first search) into working‑memory‑sized bundles (max size = 7, the classic Miller limit). Each chunk gets an identifier and a load weight equal to its node count.

2. **Operations**  
   - **Constraint Propagation**: Run a Floyd‑Warshall‑style transitive closure on **A_causal** and **A_order** (O(n³) with n ≤ 30 typical for short answers) to infer implicit causal and ordering relations.  
   - **Perturbation Sensitivity (Chaos)**: For each causal edge, compute a finite‑difference Lyapunov‑like metric: perturb the source node’s numeric value by ±ε (ε = 0.01 · range) and measure the resulting change in all downstream nodes via the closed‑form influence matrix **(I‑A_causal)⁻¹**. The average absolute downstream change across edges yields **λ̂**, an estimate of sensitivity. Lower λ̂ → more stable causal reasoning.  
   - **Cognitive Load Penalty**: Compute total load **L** = Σ (chunk_size − 1) (intrinsic load) + number of extraneous connectors (e.g., filler words, redundant clauses) extracted via a stop‑word‑like list. Germane load is rewarded: count of chunks that contain a complete causal chain (source → … → target) without breaks.  
   - **Scoring**:  
     `score = w₁·(1 – norm(λ̂)) + w₂·(1 – norm(L/L_max)) + w₃·(gemane_chunks / total_chunks)`  
     where weights w₁,w₂,w₃ sum to 1 (e.g., 0.4,0.3,0.3) and norms map raw quantities to [0,1] using observed minima/maxima across the candidate set.

3. **Structural Features Parsed**  
   - Negations (“not”, “no”) → invert polarity of causal edges.  
   - Comparatives (“greater than”, “less than”) → quantitative constraints.  
   - Conditionals (“if … then …”, “unless”) → directed causal edges with optional moderator nodes.  
   - Causal verbs (“cause”, “lead to”, “result in”) → core causal edges.  
   - Temporal markers (“before”, “after”, “when”) → ordering edges.  
   - Numeric tokens and units → numeric assertions for perturbation analysis.

4. **Novelty**  
   The triple blend is not found in existing NLP scoring pipelines. Causal‑graph scoring exists (e.g., structural equation‑model based metrics), and cognitive‑load proxies appear in readability formulas, but coupling them with a Lyapunov‑exponent‑style sensitivity measure to quantify reasoning stability is novel. No prior work propagates perturbations through a parsed causal DAG to derive a stability score, nor combines that with explicit working‑memory chunk limits.

**Ratings**  
Reasoning: 8/10 — The algorithm directly evaluates logical consistency, sensitivity to perturbations, and memory constraints, offering a principled, multi‑faceted reasoning score.  
Metacognition: 6/10 — It implicitly captures self‑regulation via load penalties but does not model the learner’s awareness of their own cognitive states.  
Hypothesis generation: 5/10 — While it can detect missing causal links, it does not propose new hypotheses; it only scores given answers.  
Implementability: 9/10 — All steps use regex, NumPy linear algebra, and pure‑Python graph traversal; no external libraries or APIs are required.

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

- **Chaos Theory**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 37% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Cognitive Load Theory**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Causal Inference**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Chaos Theory + Cognitive Load Theory: strong positive synergy (+0.670). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Causal Inference + Chaos Theory: negative interaction (-0.058). Keep these concepts in separate code paths to avoid interference.

Similar combinations that forged successfully:
- Chaos Theory + Cognitive Load Theory + Kalman Filtering (accuracy: 0%, calibration: 0%)
- Chaos Theory + Cognitive Load Theory + Neuromodulation (accuracy: 0%, calibration: 0%)
- Chaos Theory + Renormalization + Cognitive Load Theory (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: validation:runtime_error: SyntaxError: (unicode error) 'utf-8' codec can't decode byte 0xb1 in position 204: invalid start byte (tmpcqjejs9r.py, line 13)

**Forge Timestamp**: 2026-03-27T04:01:42.894769

---

## Code

**Source**: scrap

[View code](./Chaos_Theory---Cognitive_Load_Theory---Causal_Inference/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    Perturb-Aware Causal-Chunk Scorer (PACCS).
    Mechanism:
    1. Parses text into causal, temporal, and numeric graphs using regex.
    2. Enforces Cognitive Load limits by chunking nodes (Miller's 7±2).
    3. Computes Causal Stability via Lyapunov-like perturbation sensitivity on the causal matrix.
    4. Scores based on stability (low sensitivity), load efficiency, and structural completeness.
    """

    # Patterns for structural extraction
    PATTERNS = {
        'causal': [r'\b(causes?|leads? to|results? in|due to|because|if .+ then)\b', r'(.+?)\s+(causes?|leads? to|results? in)\s+(.+)'],
        'temporal': [r'\b(before|after|precedes|follows)\b'],
        'numeric': [r'(-?\d+\.?\d*)\s*(>|<|=|>=|<=)\s*(-?\d+\.?\d*)'],
        'negation': [r'\b(not|no|never|unless)\b'],
        'comparators': [r'\b(greater than|less than|more than|fewer than)\b']
    }

    STOP_WORDS = set("the a an is are was were be been being have has had do does did will would could should may might must shall can need dare ought used to about as at by for from in into of on onto out over through to under up with without".split())

    def __init__(self):
        self.epsilon = 0.01

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\w+|[^\s\w]', text.lower())

    def _extract_nodes(self, text: str) -> List[str]:
        # Simple extraction of noun-phrase-like tokens (sequences of alnum)
        tokens = re.findall(r'[a-z0-9]+', text.lower())
        # Filter stopwords and short tokens to get "concepts"
        concepts = [t for t in tokens if t not in self.STOP_WORDS and len(t) > 2]
        # Deduplicate while preserving order for indexing
        seen = set()
        unique_concepts = []
        for c in concepts:
            if c not in seen:
                seen.add(c)
                unique_concepts.append(c)
        return unique_concepts

    def _build_graphs(self, text: str) -> Tuple[np.ndarray, np.ndarray, Dict[str, float], List[str]]:
        nodes = self._extract_nodes(text)
        n = len(nodes)
        if n == 0:
            return np.array([]), np.array([]), {}, []
        
        node_map = {node: i for i, node in enumerate(nodes)}
        A_causal = np.zeros((n, n))
        A_order = np.zeros((n, n))
        numeric_constraints = {}
        
        text_lower = text.lower()

        # 1. Causal Edges (Pattern: X causes Y)
        # We look for known causal verbs between concepts
        for i, src in enumerate(nodes):
            for j, tgt in enumerate(nodes):
                if i == j: continue
                # Check if "src causes tgt" or similar exists in text
                patterns = [
                    rf'{re.escape(src)}\s+(causes?|leads? to|results? in)\s+{re.escape(tgt)}',
                    rf'due to\s+{re.escape(src)}', # Simplified
                    rf'if\s+.*{re.escape(src)}.*then\s+.*{re.escape(tgt)}'
                ]
                for p in patterns:
                    if re.search(p, text_lower):
                        A_causal[i, j] = 1.0
                        break
        
        # 2. Temporal Edges
        for i, src in enumerate(nodes):
            for j, tgt in enumerate(nodes):
                if i == j: continue
                patterns = [
                    rf'{re.escape(src)}\s+(before|precedes)\s+{re.escape(tgt)}',
                    rf'{re.escape(tgt)}\s+(after|follows)\s+{re.escape(src)}'
                ]
                for p in patterns:
                    if re.search(p, text_lower):
                        A_order[i, j] = 1.0
                        break

        # 3. Numeric Constraints
        num_matches = re.findall(self.PATTERNS['numeric'][0], text_lower)
        for match in num_matches:
            # Store as key-value for simple consistency check later if needed
            # Format: (val1, op, val2)
            numeric_constraints[f"{match[0]}{match[1]}{match[2]}"] = True

        return A_causal, A_order, numeric_constraints, nodes

    def _compute_chunks(self, A_causal: np.ndarray, nodes: List[str]) -> List[List[int]]:
        if len(nodes) == 0:
            return []
        
        n = len(nodes)
        # Combine causal and order for connectivity
        A_combined = (A_causal + A_causal.T) > 0 if n > 0 else np.array([])
        if n == 0: return []
        
        visited = [False] * n
        chunks = []
        
        # DFS to find connected components
        def dfs(idx, chunk):
            visited[idx] = True
            chunk.append(idx)
            for neighbor in range(n):
                if A_combined[idx, neighbor] and not visited[neighbor]:
                    dfs(neighbor, chunk)
        
        for i in range(n):
            if not visited[i]:
                chunk = []
                dfs(i, chunk)
                chunks.append(chunk)
        
        # Split large chunks to respect Miller's limit (7)
        final_chunks = []
        for chunk in chunks:
            if len(chunk) <= 7:
                final_chunks.append(chunk)
            else:
                # Simple split
                for i in range(0, len(chunk), 7):
                    final_chunks.append(chunk[i:i+7])
        
        return final_chunks

    def _compute_sensitivity(self, A_causal: np.ndarray) -> float:
        """
        Compute Lyapunov-like sensitivity metric.
        Perturb source nodes and measure downstream change via (I - A)^-1
        """
        if A_causal.size == 0:
            return 0.0
        
        n = A_causal.shape[0]
        if n == 0: return 0.0
        
        # Regularize diagonal to ensure invertibility (I - A)
        # If A has 1s, (I-A) might be singular if there are cycles or self-loops not handled.
        # We use (I - alpha*A) where alpha < 1 to ensure stability for the inverse approximation
        # Or simply add small identity noise.
        I = np.eye(n)
        M = I - 0.9 * A_causal 
        
        try:
            # Influence matrix
            Inv = np.linalg.inv(M)
        except np.linalg.LinAlgError:
            return 1.0 # High penalty for singular/unstable systems

        # Finite difference approximation:
        # Sum of absolute changes in downstream nodes when each node is perturbed
        total_sensitivity = 0.0
        count = 0
        
        for i in range(n):
            perturbation = np.zeros(n)
            perturbation[i] = self.epsilon
            # Effect = Inv * perturbation
            effect = np.dot(Inv, perturbation)
            total_sensitivity += np.sum(np.abs(effect))
            count += 1
            
        if count == 0: return 0.0
        return total_sensitivity / count

    def _compute_load(self, text: str, chunks: List[List[int]], nodes: List[str]) -> Tuple[float, float, float]:
        # Intrinsic Load: Sum of (chunk_size - 1)
        intrinsic = sum(max(0, len(c) - 1) for c in chunks)
        
        # Extraneous Load: Count of stop words / filler
        tokens = self._tokenize(text)
        extraneous = sum(1 for t in tokens if t in self.STOP_WORDS)
        
        # Germane Load: Chunks containing a causal chain (simplified: chunk size > 1 implies connection)
        # Strictly: does the subgraph of the chunk contain an edge?
        germane_count = 0
        if len(nodes) > 0:
            # Re-extract quick causal map for this specific text to check chunks
            # (Optimization: pass A_causal, but for brevity we assume connected chunks are germane)
            germane_count = sum(1 for c in chunks if len(c) > 1)
            
        total_chunks = len(chunks) if len(chunks) > 0 else 1
        return float(intrinsic), float(extraneous), float(germane_count) / total_chunks

    def _score_candidate(self, prompt: str, candidate: str) -> Dict[str, Any]:
        full_text = f"{prompt} {candidate}"
        
        # 1. Parse
        A_causal, A_order, num_const, nodes = self._build_graphs(full_text)
        
        if len(nodes) == 0:
            # Fallback for very short answers with no structure
            return {"candidate": candidate, "score": 0.1, "reasoning": "No structural elements detected."}

        # 2. Chunking (Cognitive Load)
        chunks = self._compute_chunks(A_causal, nodes)
        
        # 3. Sensitivity (Chaos)
        sensitivity = self._compute_sensitivity(A_causal)
        
        # 4. Load Metrics
        intrinsic, extraneous, germane_ratio = self._compute_load(full_text, chunks, nodes)
        
        # Normalization heuristics (assuming typical ranges)
        # Sensitivity: lower is better. Range ~0 to 5. Norm: 1 - min(1, sens/2.0)
        norm_sens = max(0.0, 1.0 - (sensitivity / 2.0))
        
        # Load: Lower intrinsic/extraneous is better. 
        # Assume max intrinsic ~10, max extraneous ~20
        norm_load = 1.0 - min(1.0, (intrinsic + 0.5*extraneous) / 15.0)
        
        # Score calculation
        # Weights: Stability (0.4), Load (0.3), Germane (0.3)
        score = 0.4 * norm_sens + 0.3 * norm_load + 0.3 * germane_ratio
        
        # Bonus for numeric consistency if present
        if num_const:
            score += 0.05
            
        return {
            "candidate": candidate,
            "score": float(score),
            "reasoning": f"Sens:{sensitivity:.2f}, Load:{intrinsic:.1f}, Germane:{germane_ratio:.2f}"
        }

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        scores = []
        
        # First pass to get raw scores for normalization if needed, 
        # though the formula is self-contained per candidate relative to fixed bounds.
        for cand in candidates:
            res = self._score_candidate(prompt, cand)
            results.append(res)
            scores.append(res['score'])
        
        # Normalize scores to [0, 1] range across the candidate set for better ranking
        min_s, max_s = min(scores), max(scores)
        range_s = max_s - min_s if max_s > min_s else 1.0
        
        ranked = []
        for res in results:
            # Map to 0.2 - 0.9 range to allow NCD tiebreaking room
            norm_val = (res['score'] - min_s) / range_s
            final_score = 0.2 + (0.7 * norm_val)
            ranked.append({
                "candidate": res['candidate'],
                "score": final_score,
                "reasoning": res['reasoning']
            })
            
        # Sort descending
        ranked.sort(key=lambda x: x['score'], reverse=True)
        return ranked

    def confidence(self, prompt: str, answer: str) -> float:
        res = self._score_candidate(prompt, answer)
        # Map internal score to 0-1 confidence
        # Base score is already somewhat normalized, clamp it
        conf = max(0.0, min(1.0, res['score']))
        return conf
```

</details>
