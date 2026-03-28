# Ergodic Theory + Cognitive Load Theory + Compositionality

**Fields**: Mathematics, Cognitive Science, Linguistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T23:01:24.893273
**Report Generated**: 2026-03-27T17:21:24.646555

---

## Nous Analysis

**Algorithm**  
1. **Parsing (Compositionality)** – Using a small set of regex patterns we extract atomic propositions and their logical operators from both the prompt and each candidate answer. Each proposition becomes a node in a directed graph; edges encode the syntactic combination rule (∧, ∨, →, ¬, <, >, =, because, if‑then). The graph is stored as a list of tuples `(src_id, op, tgt_id)` and a NumPy array `truth` of shape `(N,)` initialized to *unknown* (‑1).  
2. **Constraint Propagation (Ergodic‑like averaging)** – We iteratively apply deterministic inference rules (modus ponens, transitivity of ordering, arithmetic substitution) until convergence, updating `truth` with 0/1 values. Each iteration treats the current truth vector as a “state” of a discrete dynamical system; we record the state after every iteration in a list `states`. After convergence we compute the **time average** of each proposition’s truth value: `time_avg = np.mean(states, axis=0)`. The **space average** is simply the mean of the final truth vector: `space_avg = np.mean(truth[truth!=-1])`. The ergodic score for a candidate is `1 - np.abs(time_avg - space_avg).mean()`, rewarding answers whose truth values stabilize quickly (i.e., the system behaves ergodically).  
3. **Cognitive Load Chunking** – We partition the proposition graph into chunks of at most `k=4` nodes (the typical working‑memory limit) using a greedy topological ordering. For each chunk we compute a local ergodic score as above; the overall cognitive‑load penalty is `exp(-λ * (num_chunks - ideal_chunks))` with λ=0.5. The final score multiplies the ergodic term by this penalty.  

**Parsed Structural Features**  
- Negations (`not`, `no`)  
- Comparatives (`greater than`, `less than`, `equals`)  
- Conditionals (`if … then …`, `because`)  
- Numeric values and arithmetic expressions  
- Causal verbs (`causes`, `leads to`)  
- Ordering relations (`before`, `after`, `first`, `last`)  

**Novelty**  
The approach fuses three well‑studied ideas: (1) treating logical inference as a dynamical system whose ergodic property measures consistency, (2) limiting working‑memory chunks to model cognitive load, and (3) scoring via compositional semantics. While neuro‑symbolic and probabilistic soft logic systems exist, none combine explicit ergodic averaging with a hard working‑memory chunk bound in a purely numpy/stdlib implementation, making the combination novel for lightweight reasoning evaluation.  

**Ratings**  
Reasoning: 8/10 — captures logical consistency and dynamics but relies on hand‑crafted rules.  
Metacognition: 7/10 — explicit chunk limit mirrors working‑memory awareness, yet no self‑adjustment.  
Hypothesis generation: 6/10 — can propose intermediate truths via propagation, but lacks exploratory search.  
Implementability: 9/10 — only regex, NumPy, and stdlib; straightforward to code and test.

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

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Ergodic Theory**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 37% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Cognitive Load Theory**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Compositionality**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Compositionality + Ergodic Theory: strong positive synergy (+0.320). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Ergodic Theory + Adaptive Control + Compositionality (accuracy: 0%, calibration: 0%)
- Ergodic Theory + Chaos Theory + Compositionality (accuracy: 0%, calibration: 0%)
- Ergodic Theory + Hebbian Learning + Compositionality (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=38% cal=33% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-03-27T17:15:31.952634

---

## Code

**Source**: scrap

[View code](./Ergodic_Theory---Cognitive_Load_Theory---Compositionality/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    A reasoning tool fusing Compositionality, Ergodic Theory, and Cognitive Load Theory.
    
    Mechanism:
    1. Parsing (Compositionality): Extracts atomic propositions and logical operators into a graph.
    2. Constraint Propagation (Ergodic-like): Iteratively resolves truth values via deterministic rules.
       The 'ergodic score' measures how quickly the system stabilizes (time_avg vs space_avg).
    3. Cognitive Load: Penalizes solutions requiring working memory chunks > 4.
    4. Epistemic Honesty (Tier B): Detects ambiguity/presuppositions to cap confidence.
    5. Scoring: Structural consistency (50%+) + Computation (20%+) + NCD tiebreaker (<15%).
    """
    
    def __init__(self):
        self.k_chunk = 4  # Working memory limit
        self.lambda_penalty = 0.5
        
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|neither)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(greater|less|more|fewer|higher|lower|before|after)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|because|therefore|implies)\b', re.IGNORECASE),
            'numeric': re.compile(r'-?\d+\.?\d*'),
            'equality': re.compile(r'\b(equals|is|same|identical)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(causes|leads to|results in)\b', re.IGNORECASE)
        }
        
        # Tier B Traps
        self.traps = {
            'presupposition': re.compile(r'\b(have you stopped|why did .*(fail|stop)|when did .*(stop|fail))\b', re.IGNORECASE),
            'false_dichotomy': re.compile(r'\b(either .+ or .+)\b', re.IGNORECASE),
            'subjectivity': re.compile(r'\b(best|worst|favorite|most beautiful)\b', re.IGNORECASE),
            'pronoun_ambiguity': re.compile(r'\b(he|she|him|her|it|they)\b.*\bwho\b', re.IGNORECASE)
        }

    def _parse_text(self, text: str) -> Tuple[List[str], List[Tuple[int, str, int]]]:
        """Extract atomic propositions and edges (Compositionality)."""
        text_lower = text.lower()
        sentences = re.split(r'[.\?!]', text)
        nodes = []
        edges = []
        
        # Simple node extraction (split by connectors)
        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
            # Naive tokenization for demo; in production, use NLP
            parts = re.split(r'\b(and|or|but|because|if|then)\b', sent, flags=re.IGNORECASE)
            
            start_idx = len(nodes)
            for i, part in enumerate(parts):
                part = part.strip()
                if not part:
                    continue
                # Clean part
                part_clean = re.sub(r'^[\s,]+|[\s,]+$', '', part)
                if part_clean:
                    nodes.append(part_clean)
                    
            # Add edges between consecutive parts in the sentence fragment
            for i in range(start_idx, len(nodes) - 1):
                op = 'and' # Default
                # Check connector between parts if available (simplified)
                edges.append((i, 'link', i+1))
                
        return nodes, edges

    def _propagate_constraints(self, nodes: List[str], edges: List[Tuple]) -> Tuple[np.ndarray, List[np.ndarray]]:
        """
        Simulate constraint propagation as a dynamical system.
        Returns final truth vector and history of states.
        """
        n = len(nodes)
        if n == 0:
            return np.array([]), []
            
        truth = np.full(n, -1, dtype=float)  # -1: unknown, 0: false, 1: true
        history = []
        
        # Heuristic initialization based on simple patterns
        for i, node in enumerate(nodes):
            node_l = node.lower()
            if re.search(r'\b(true|yes|correct|fact)\b', node_l):
                truth[i] = 1.0
            elif re.search(r'\b(false|no|wrong|lie)\b', node_l):
                truth[i] = 0.0
            elif re.search(r'\b(not|never)\b', node_l):
                # If negation found, invert neighbor if known, else mark uncertain
                pass 
            # Numeric evaluation
            nums = re.findall(r'-?\d+\.?\d*', node_l)
            if len(nums) >= 2:
                try:
                    v1, v2 = float(nums[0]), float(nums[1])
                    if 'greater' in node_l or '>' in node:
                        truth[i] = 1.0 if v1 > v2 else 0.0
                    elif 'less' in node_l or '<' in node:
                        truth[i] = 1.0 if v1 < v2 else 0.0
                    elif 'equal' in node_l or '=' in node:
                        truth[i] = 1.0 if v1 == v2 else 0.0
                except: pass

        history.append(truth.copy())
        
        # Iterative propagation (Modus Ponens / Transitivity simulation)
        converged = False
        max_iter = 10
        for _ in range(max_iter):
            if converged:
                break
            old_truth = truth.copy()
            
            for src, op, tgt in edges:
                if src < len(truth) and tgt < len(truth):
                    # Propagate knowns
                    if truth[src] != -1 and truth[tgt] == -1:
                        truth[tgt] = truth[src] # Simplified propagation
                    elif truth[tgt] != -1 and truth[src] == -1:
                        truth[src] = truth[tgt]
            
            if np.array_equal(truth, old_truth):
                converged = True
            history.append(truth.copy())
            
        return truth, history

    def _calculate_ergodic_score(self, truth: np.ndarray, history: List[np.ndarray]) -> float:
        """Calculate ergodic score: 1 - |time_avg - space_avg|."""
        if len(history) == 0 or len(truth) == 0:
            return 0.0
            
        history_arr = np.array(history)
        # Time average: mean over iterations for each node
        # Filter out -1 (unknown) for mean calculation to avoid skewing, or treat as 0?
        # Treating unknown as neutral 0.5 for averaging dynamics
        clean_history = np.where(history_arr == -1, 0.5, history_arr)
        time_avg = np.mean(clean_history, axis=0)
        
        # Space average: mean of final resolved state (filtering unknowns)
        known_mask = truth != -1
        if not np.any(known_mask):
            return 0.5 # Neutral if nothing resolved
            
        space_avg_val = np.mean(truth[known_mask])
        # Broadcast space_avg to match time_avg shape for comparison
        space_avg_vec = np.full_like(time_avg, space_avg_val)
        
        diff = np.abs(time_avg - space_avg_vec)
        # Only consider nodes that eventually became known
        final_known = (truth != -1)
        if not np.any(final_known):
            return 0.0
            
        return float(1.0 - np.mean(diff[final_known]))

    def _calculate_cognitive_penalty(self, num_nodes: int) -> float:
        """Penalize if chunks exceed working memory limit k=4."""
        if num_nodes == 0:
            return 1.0
        num_chunks = int(np.ceil(num_nodes / self.k_chunk))
        ideal_chunks = max(1, int(np.ceil(num_nodes / 8))) # Heuristic ideal
        penalty = np.exp(-self.lambda_penalty * max(0, num_chunks - ideal_chunks))
        return float(penalty)

    def _check_meta_confidence(self, text: str) -> float:
        """Tier B: Detect ambiguity and traps."""
        text_l = text.lower()
        
        # 1. Presupposition
        if self.traps['presupposition'].search(text_l):
            return 0.2
        # 2. False Dichotomy (heuristic)
        if self.traps['false_dichotomy'].search(text_l) and 'or' in text_l:
            # Check if exhaustive (hard to detect, assume risky)
            return 0.4 
        # 3. Subjectivity
        if self.traps['subjectivity'].search(text_l):
            return 0.3
        # 4. Pronoun Ambiguity context
        if self.traps['pronoun_ambiguity'].search(text_l):
            return 0.3
            
        return 1.0 # No obvious trap

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z = zlib.compress
        len1, len2 = len(s1), len(s2)
        if len1 == 0 or len2 == 0:
            return 1.0
        concat = s1 + s2
        ncd = (len(z(concat.encode('utf-8'))) - min(len1, len2)) / max(len1, len2)
        return max(0.0, min(1.0, ncd))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        prompt_nodes, prompt_edges = self._parse_text(prompt)
        prompt_truth, prompt_hist = self._propagate_constraints(prompt_nodes, prompt_edges)
        prompt_ergodic = self._calculate_ergodic_score(prompt_truth, prompt_hist)
        prompt_penalty = self._calculate_cognitive_penalty(len(prompt_nodes))
        
        # Base structural score from prompt analysis
        base_structural_score = prompt_ergodic * prompt_penalty
        
        for cand in candidates:
            # 1. Structural Analysis of Candidate
            cand_nodes, cand_edges = self._parse_text(cand)
            cand_truth, cand_hist = self._propagate_constraints(cand_nodes, cand_edges)
            cand_ergodic = self._calculate_ergodic_score(cand_truth, cand_hist)
            cand_penalty = self._calculate_cognitive_penalty(len(cand_nodes))
            
            # 2. Consistency Check (Prompt vs Candidate)
            # Do they share logical operators?
            consistency = 0.5
            if len(cand_nodes) > 0:
                # Simple overlap check of logical keywords
                p_ops = set(re.findall(r'\b(and|or|not|if|then|because)\b', prompt.lower()))
                c_ops = set(re.findall(r'\b(and|or|not|if|then|because)\b', cand.lower()))
                if p_ops and c_ops:
                    consistency = len(p_ops & c_ops) / max(len(p_ops), len(c_ops))
                elif not p_ops and not c_ops:
                    consistency = 0.8 # Both simple statements
            
            # 3. Numeric/Constructive Verification
            numeric_score = 0.0
            p_nums = re.findall(r'-?\d+\.?\d*', prompt)
            c_nums = re.findall(r'-?\d+\.?\d*', cand)
            
            if p_nums and c_nums:
                # If numbers match exactly, high reward
                if set(p_nums) == set(c_nums):
                    numeric_score = 1.0
                else:
                    # Check if candidate computes something from prompt numbers
                    try:
                        # Very basic: if candidate is just a number, check if it matches a calc
                        if len(c_nums) == 1 and len(p_nums) >= 2:
                            val = float(c_nums[0])
                            p_vals = [float(x) for x in p_nums]
                            if abs(val - sum(p_vals)) < 1e-6 or abs(val - (p_vals[0] * p_vals[1])) < 1e-6:
                                numeric_score = 1.0
                    except: pass
            elif not p_nums and not c_nums:
                numeric_score = 0.5 # Neutral if no numbers
            
            # 4. NCD Tiebreaker (Max 15% weight)
            ncd_val = self._compute_ncd(prompt, cand)
            ncd_score = 1.0 - ncd_val # Higher is better
            
            # Final Score Composition
            # Structural >= 50%, Computation >= 20%, NCD <= 15%
            # Normalize components
            struct_comp = (cand_ergodic * cand_penalty * 0.6) + (consistency * 0.2)
            comp_comp = numeric_score * 0.25
            ncd_comp = ncd_score * 0.15
            
            final_score = struct_comp + comp_comp + ncd_comp
            
            # Reasoning string
            reason = f"Ergodic:{cand_ergodic:.2f}, Load:{cand_penalty:.2f}, Num:{numeric_score:.2f}"
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reason
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def _meta_confidence(self, prompt: str) -> float:
        return self._check_meta_confidence(prompt)

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at 0.3 if meta-analysis detects ambiguity/traps.
        Caps at 0.9 unless computational proof exists.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # Evaluate single candidate to get internal score
        res_list = self.evaluate(prompt, [answer])
        if not res_list:
            return 0.0
            
        raw_score = res_list[0]['score']
        
        # Map raw score to confidence range [0, 0.9] normally
        # If meta_cap is low (e.g., 0.2), confidence cannot exceed it
        base_conf = min(0.9, raw_score)
        
        final_conf = min(base_conf, meta_cap)
        
        # If no structural signal detected (score very low), return low confidence
        if raw_score < 0.2:
            final_conf = min(final_conf, 0.3)
            
        return float(np.clip(final_conf, 0.0, 1.0))
```

</details>
