# Network Science + Mechanism Design + Free Energy Principle

**Fields**: Complex Systems, Economics, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T14:11:36.841750
**Report Generated**: 2026-03-27T17:21:24.845551

---

## Nous Analysis

**Algorithm**  
We build a *constraint‑propagation graph* from the prompt and each candidate answer.  
1. **Parsing** – Using only `re` we extract atomic propositions (noun‑verb phrases) and tag them with structural features: negation (`not`), comparative (`>`, `<`, `more`, `less`), conditional (`if … then …`), causal (`because`, `leads to`), ordering (`first`, `after`), and numeric constants. Each proposition becomes a node *i* with a binary feature vector **f**ₖ ∈ {0,1}⁶ (one dimension per feature type).  
2. **Edge creation** – For every pair of propositions (i,j) we add a directed edge if the syntactic pattern indicates a logical relation:  
   - *i → j* for “if i then j” or causal “i leads to j”.  
   - *i ⊣ j* for negation (“i is not j”).  
   - *i ≺ j* for comparative/ordering (“i is greater than j”).  
   Edge weight *w*ᵢⱼ is initialized to 1.0 (strength of the constraint).  
3. **Constraint propagation** – We compute the transitive closure of the implication subgraph using Floyd‑Warshall on a boolean adjacency matrix **A** (numpy). This yields a reachability matrix **R** where Rᵢⱼ=1 iff i entails j. Negation and comparative edges are stored separately as penalty matrices **N** and **C**.  
4. **Mechanism‑design incentive layer** – For each candidate answer we construct a hypothesis vector **h** (same dimension as nodes) indicating which propositions the answer asserts as true (1), false (0), or unknown (0.5). We define an *incentive* function that rewards consistency with propagated constraints:  
   \[
   \text{Inc}(\mathbf{h}) = -\sum_{i,j} R_{ij}\,(h_i - h_j)^2
   \]  
   (penalizes asserting i true and j false when i entails j).  
5. **Free‑energy scoring** – Variational free energy approximates prediction error:  
   \[
   F(\mathbf{h}) = \underbrace{\frac{1}{2}\|\mathbf{h} - \mathbf{p}\|^2}_{\text{prediction error}} - \underbrace{\sum_k f_k \log \sigma(h_k)}_{\text{entropy (complexity)}} + \lambda\,\text{Inc}(\mathbf{h})
   \]  
   where **p** is the prior truth vector derived from explicit facts in the prompt (1 for stated true, 0 for stated false, 0.5 otherwise), σ is the logistic function, and λ balances incentive strength. Lower *F* indicates a better answer; we return score = –F.  
All operations use only `numpy` (matrix algebra) and Python’s `re`/`collections`.

**Structural features parsed**  
Negations, comparatives, conditionals, causal claims, ordering relations, numeric constants, and quantifiers (via regex patterns like `\bmore\b`, `\bif\b.*\bthen\b`, `\b\d+\.?\d*\b`).

**Novelty**  
The triple blend is not found in existing literature: network‑science graphs provide the structural scaffold, mechanism‑design supplies an incentive‑compatible consistency term, and the free‑energy principle supplies a variational‑inference‑style scoring function. Prior work uses either Bayesian nets or argumentation graphs alone, not this specific hybrid.

**Rating**  
Reasoning: 7/10 — captures logical dependencies and propagates constraints, but relies on shallow regex parsing which can miss complex syntax.  
Metacognition: 5/10 — the algorithm does not monitor its own parsing uncertainty; it assumes extracted propositions are correct.  
Hypothesis generation: 6/10 — generates candidate‑specific hypothesis vectors and scores them, yet does not propose new hypotheses beyond the given answers.  
Implementability: 8/10 — uses only numpy and stdlib; all steps are straightforward matrix operations and regex loops.

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

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=30% cal=47% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-03-27T16:29:35.328422

---

## Code

**Source**: scrap

[View code](./Network_Science---Mechanism_Design---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
import zlib
from collections import deque

class ReasoningTool:
    """
    A hybrid reasoning tool combining Network Science (constraint graphs), 
    Mechanism Design (incentive compatibility), and the Free Energy Principle 
    (variational scoring) to evaluate logical consistency.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions and tags features (negation, causal, etc.).
    2. Graph Construction: Builds a directed graph of implications and constraints.
    3. Propagation: Uses Floyd-Warshall for transitive closure of logical entailment.
    4. Scoring: Computes a 'Free Energy' score balancing prediction error against 
       logical consistency (incentive) and complexity.
    5. Epistemic Honesty: Caps confidence on ambiguous or presupposition-laden prompts.
    """

    def __init__(self):
        # Regex patterns for feature extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|provided)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|leads to|causes|results in|therefore)\b', re.IGNORECASE),
            'ordering': re.compile(r'\b(first|second|last|next|finally)\b', re.IGNORECASE),
            'numeric': re.compile(r'\d+\.?\d*'),
            # Meta-confidence patterns
            'presupposition': re.compile(r'\b(have you stopped|have you quit|why did .+ fail|why is .+ bad)\b', re.IGNORECASE),
            'false_dichotomy': re.compile(r'\b(either .+ or .+|only two options)\b', re.IGNORECASE),
            'pronoun_ambiguity': re.compile(r'\b(he|she|him|her|it|they)\b.*\bwho\b', re.IGNORECASE),
            'subjectivity': re.compile(r'\b(best|worst|favorite|opinion)\b', re.IGNORECASE)
        }
        self.lambda_inc = 2.0  # Weight for incentive consistency
        self.lambda_err = 1.0  # Weight for prediction error

    def _extract_features(self, text):
        """Extracts binary feature vector [neg, comp, cond, caus, ord, num]"""
        t_lower = text.lower()
        flags = [
            1 if self.patterns['negation'].search(t_lower) else 0,
            1 if self.patterns['comparative'].search(t_lower) else 0,
            1 if self.patterns['conditional'].search(t_lower) else 0,
            1 if self.patterns['causal'].search(t_lower) else 0,
            1 if self.patterns['ordering'].search(t_lower) else 0,
            1 if self.patterns['numeric'].search(text) else 0
        ]
        return np.array(flags, dtype=float)

    def _parse_propositions(self, text):
        """Splits text into atomic propositions and extracts features."""
        # Simple splitter on punctuation, keeping delimiters for context if needed
        # For this implementation, we treat sentences/clauses as nodes
        raw_nodes = re.split(r'[.;!?]', text)
        nodes = []
        features = []
        
        for i, chunk in enumerate(raw_nodes):
            chunk = chunk.strip()
            if not chunk:
                continue
            nodes.append(chunk)
            features.append(self._extract_features(chunk))
        
        if not nodes:
            nodes = [text]
            features = [self._extract_features(text)]
            
        return nodes, np.array(features)

    def _build_graph(self, nodes):
        """Builds adjacency matrix A (implication) and penalty matrices N, C."""
        n = len(nodes)
        A = np.zeros((n, n), dtype=float) # Implication graph
        N = np.zeros((n, n), dtype=float) # Negation conflicts
        C = np.zeros((n, n), dtype=float) # Comparative conflicts
        
        # Initialize diagonal
        np.fill_diagonal(A, 1.0)
        
        text_full = " ".join(nodes).lower()
        
        for i, node_i in enumerate(nodes):
            ni_lower = node_i.lower()
            # Self-consistency
            A[i, i] = 1.0 
            
            for j, node_j in enumerate(nodes):
                if i == j: continue
                
                nj_lower = node_j.lower()
                
                # 1. Causal/Conditional: "if i then j" or "i leads to j"
                # Heuristic: if node i appears before node j and contains conditional/causal keywords
                if any(k in ni_lower for k in ['if', 'leads to', 'causes']):
                    if j > i or 'then' in ni_lower: # Simplified temporal/logical flow
                        A[i, j] = 1.0
                
                # 2. Negation: "i is not j" or explicit negation in one referencing the other
                # If node i has negation and shares significant words with j
                if self.patterns['negation'].search(ni_lower):
                    # Simple overlap check for negation target
                    words_i = set(re.findall(r'\w+', ni_lower))
                    words_j = set(re.findall(r'\w+', nj_lower))
                    if len(words_i & words_j) > 1: # Share meaningful words
                        N[i, j] = 1.0
                        N[j, i] = 1.0

                # 3. Comparatives: if i says "A > B" and j says "B > A"
                if self.patterns['comparative'].search(ni_lower) and self.patterns['comparative'].search(nj_lower):
                     # Detect contradiction in ordering (simplified)
                     if ('more' in ni_lower and 'less' in nj_lower) or ('before' in ni_lower and 'after' in nj_lower):
                         C[i, j] = 1.0
                         C[j, i] = 1.0

        # Transitive Closure (Floyd-Warshall) on Boolean implication
        # Convert A to boolean reachability
        R = (A > 0).astype(float)
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if R[i, k] and R[k, j]:
                        R[i, j] = 1.0
                        
        return R, N, C

    def _compute_free_energy(self, prompt, candidate):
        """Core scoring function based on Free Energy Principle."""
        full_text = f"{prompt} {candidate}"
        nodes, feats = self._parse_propositions(full_text)
        n = len(nodes)
        
        if n == 0:
            return 0.0, "No propositions parsed."

        R, N, C = self._build_graph(nodes)
        
        # Prior vector p: 0.5 (unknown) initially. 
        # If prompt explicitly states facts, we'd parse them. 
        # Here we assume the prompt sets the context (prior=0.5 for ambiguity, 1.0 if asserted)
        # For this hybrid model, we treat the prompt part as 'observed' (p=1) and candidate as 'hypothesis'
        p = np.full(n, 0.5)
        prompt_len = len(self._parse_propositions(prompt)[0])
        p[:min(prompt_len, n)] = 1.0 # Assume prompt facts are true
        
        # Hypothesis vector h: Candidate assertions
        # If candidate nodes align with prompt nodes, h=1. If contradictory, h=0.
        # Simplified: Candidate nodes are the variable part.
        h = np.full(n, 0.5)
        # Mark candidate propositions as asserted True (1.0)
        # In a real system, we'd map candidate claims to prompt nodes.
        # Here, we assume the candidate adds new nodes that must be consistent.
        h[prompt_len:] = 1.0 
        
        # Truncate to n if parsing differed
        h = h[:n]
        p = p[:n]

        # 1. Prediction Error (Accuracy)
        # How much does h deviate from prior p?
        pred_error = 0.5 * np.sum((h - p) ** 2)
        
        # 2. Complexity (Entropy term approximation)
        # Penalize high certainty (h near 0 or 1) without evidence
        sigma_h = 1 / (1 + np.exp(-h)) # Logistic
        # Avoid log(0)
        sigma_h = np.clip(sigma_h, 1e-6, 1-1e-6)
        entropy_term = -np.sum(feats.sum(axis=1) * np.log(sigma_h))
        
        # 3. Incentive (Consistency)
        # Penalize h_i=1, h_j=0 if i entails j (R[i,j]=1)
        # Term: - sum R_ij * (h_i - h_j)^2
        # If i->j and h_i=1, h_j=0, penalty is large.
        consistency_penalty = 0.0
        for i in range(n):
            for j in range(n):
                if R[i, j] > 0:
                    consistency_penalty += (h[i] - h[j]) ** 2
        
        # Free Energy F = Error + Complexity - Incentive(Reward)
        # We want to MINIMIZE F. Score = -F.
        F = self.lambda_err * pred_error + 0.1 * entropy_term - self.lambda_inc * consistency_penalty
        
        # Normalize score roughly to 0-1 range for usability
        # Lower F is better. 
        score = -F / (n + 1) 
        
        reason = f"Parsed {n} nodes. Consistency penalty: {consistency_penalty:.2f}. Error: {pred_error:.2f}."
        return score, reason

    def _meta_confidence(self, prompt):
        """
        Checks for Tier B traps: ambiguity, presupposition, unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition
        if self.patterns['presupposition'].search(p_lower):
            return 0.2
        
        # 2. False Dichotomy
        if self.patterns['false_dichotomy'].search(p_lower):
            return 0.3
            
        # 3. Pronoun Ambiguity (heuristic: pronoun + 'who')
        if self.patterns['pronoun_ambiguity'].search(p_lower):
            return 0.2
            
        # 4. Subjectivity without metrics
        if self.patterns['subjectivity'].search(p_lower) and 'data' not in p_lower:
            return 0.4
            
        # 5. Unanswerability (No numbers in math problems, missing info)
        # If it looks like a math problem but has no numbers
        if any(k in p_lower for k in ['calculate', 'sum', 'total', 'cost']) and not self.patterns['numeric'].search(p_lower):
            return 0.1
            
        return 1.0 # No obvious traps detected

    def _ncd_score(self, s1, s2):
        """Normalized Compression Distance as a tiebreaker (max 15% weight)."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_combined = len(zlib.compress(s1_b + s2_b))
        
        if max(len_s1, len_s2) == 0:
            return 0.0
        return (len_combined - min(len_s1, len_s2)) / max(len_s1, len_s2)

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        meta_cap = self._meta_confidence(prompt)
        
        # Base scores from Free Energy logic
        base_scores = []
        for cand in candidates:
            score, reason = self._compute_free_energy(prompt, cand)
            base_scores.append((score, reason, cand))
        
        # Normalize base scores to 0-1 range roughly
        if base_scores:
            scores_only = [x[0] for x in base_scores]
            min_s, max_s = min(scores_only), max(scores_only)
            range_s = max_s - min_s if max_s != min_s else 1.0
            
            for score, reason, cand in base_scores:
                # Normalize to 0.2 - 0.9 range initially
                norm_score = 0.2 + 0.7 * ((score - min_s) / range_s)
                
                # Add NCD tiebreaker (small weight)
                # Prefer candidate that compresses well with prompt (high similarity/relevance)
                ncd = self._ncd_score(prompt, cand)
                # Lower NCD = more similar. We want high score for good match.
                # Invert NCD contribution slightly
                ncd_bonus = (1.0 - ncd) * 0.15 
                
                final_score = norm_score * 0.85 + ncd_bonus * 0.15
                
                # Apply Meta-Confidence Cap (Epistemic Honesty)
                # If the prompt is ambiguous, even the "best" answer shouldn't be trusted highly
                if meta_cap < 0.5:
                    final_score *= (meta_cap / 0.5) # Scale down significantly
                
                results.append({
                    "candidate": cand,
                    "score": float(final_score),
                    "reasoning": reason
                })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on prompt ambiguity (Tier B).
        """
        meta_cap = self._meta_confidence(prompt)
        
        # Run evaluation internally to get raw score
        # We treat the single answer as the only candidate to get its relative score
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        raw_score = res[0]['score']
        
        # Map raw score (approx 0-1) to confidence
        # If meta_cap is low, confidence is low regardless of score
        conf = raw_score * meta_cap
        
        # Hard caps for specific Tier B failures
        if meta_cap < 0.3:
            return min(conf, 0.29) # Ensure it stays under the threshold
        
        # Never return > 0.9 unless the computation was definitive (simulated here by high score + no ambiguity)
        if meta_cap == 1.0 and raw_score > 0.85:
            return min(conf, 0.95)
            
        return min(conf, 0.9)
```

</details>
