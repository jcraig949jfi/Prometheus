# Phase Transitions + Criticality + Sensitivity Analysis

**Fields**: Physics, Complex Systems, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T16:34:39.297638
**Report Generated**: 2026-03-27T23:28:38.519718

---

## Nous Analysis

**Algorithm**  
We treat each candidate answer as a dynamical system of logical propositions. First, a regex‑based parser extracts atomic propositions and builds a directed weighted graph \(G=(V,E)\) where each node \(v_i\) is a literal (e.g., “X > 5”, “¬Y”). Edges encode three constraint types extracted from the text:  
1. **Implication** \(v_i\rightarrow v_j\) (from “if X then Y” or causal cues) with weight \(w_{ij}=1\).  
2. **Equivalence/Order** \(v_i\leftrightarrow v_j\) (from comparatives “X is greater than Y”, ordering) with weight \(w_{ij}=0.5\).  
3. **Mutual exclusion** \(v_i\rightarrow \neg v_j\) (from negations, “not X”).  

We store the adjacency matrix \(W\in\mathbb{R}^{n\times n}\) (numpy array). A state vector \(s\in[0,1]^n\) holds the current truth‑strength of each literal (initially 0.5 for unknowns). Constraint propagation is performed by iterating  
\[
s^{(t+1)} = \sigma\!\big(W^\top s^{(t)}\big),
\]  
where \(\sigma\) is a clipped linear function \(\sigma(x)=\min(1,\max(0,x))\). Convergence (fixed point) is reached when \(\|s^{(t+1)}-s^{(t)}\|_1<10^{-3}\); this mimics the relaxation toward an ordered or disordered phase.

The **order parameter** \(O\) is the fraction of satisfied clauses:  
\[
O = \frac{1}{|C|}\sum_{c\in C}\big[ s_i \ge \theta \;\text{iff}\; \text{literal }i\text{ appears positively in }c\big],
\]  
with threshold \(\theta=0.5\).  

**Sensitivity analysis** computes the susceptibility \(\chi\) by finite‑difference perturbations: for each literal \(i\), flip its value (0↔1), re‑propagate, and record \(\Delta O_i\). Then  
\[
\chi = \sqrt{\frac{1}{n}\sum_i (\Delta O_i)^2}.
\]  
High \(\chi\) indicates the answer lies near a critical point where small input changes cause large output swings.

The final score combines order and distance from criticality:  
\[
\text{Score}= O \cdot e^{-\chi}.
\]  
Answers with high internal consistency (large \(O\)) and low fragility (small \(\chi\)) receive the highest marks.

**Parsed structural features** – negations (“not”, “no”), comparatives (“greater than”, “less than”), conditionals (“if … then …”, “implies”), causal claims (“causes”, “leads to”), numeric values and thresholds, ordering relations (“first”, “after”, “precede”), and conjunction/disjunction cues.

**Novelty** – The approach maps concepts from statistical physics (phase transition, order parameter, susceptibility) onto a constraint‑propagation scoring engine. While SAT‑phase‑transition research and probabilistic soft logic use similar ideas, explicitly combining order‑parameter measurement with sensitivity‑based susceptibility to score reasoning answers is not present in existing public tools, making the combination novel for this evaluation setting.

**Ratings**  
Reasoning: 8/10 — captures logical consistency and fragility via well‑defined mathematical operations.  
Metacognition: 6/10 — the method does not explicitly model self‑reflection or uncertainty about its own parsing.  
Hypothesis generation: 5/10 — focuses on evaluating given answers; generating new hypotheses would require additional abductive modules.  
Implementability: 9/10 — relies only on regex, numpy matrix ops, and simple loops; readily producible in <200 lines.

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

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=40% cal=40% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-03-27T21:10:25.426417

---

## Code

**Source**: scrap

[View code](./Phase_Transitions---Criticality---Sensitivity_Analysis/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    """
    A reasoning tool combining phase transition dynamics, criticality analysis,
    and epistemic honesty checks.
    
    Mechanism:
    1. Epistemic Honesty (Tier B): Scans prompt for ambiguity, presuppositions, 
       and unanswerable structures. Caps confidence if detected.
    2. Structural Parsing: Extracts literals, implications, equivalences, and 
       mutual exclusions using regex.
    3. Dynamical System: Models truth values as a state vector evolving via 
       constraint propagation (s' = sigma(W^T s)).
    4. Order Parameter (O): Measures fraction of satisfied constraints at convergence.
    5. Susceptibility (chi): Measures sensitivity to perturbations (criticality).
    6. Scoring: Score = O * exp(-chi). High consistency + low fragility = high score.
    """
    
    def __init__(self):
        # Regex patterns for structural extraction
        self.patterns = {
            'implication': [r'\bif\s+(.+?)\s+(?:then|,)?\s+(.+?)\b', r'\b(.+?)\s+implies\s+(.+?)\b', r'\b(.+?)\s+leads?\s+to\s+(.+?)\b'],
            'equivalence': [r'\b(.+?)\s+is\s+(?:greater|less|equal)\s+to\s+(.+?)\b', r'\b(.+?)\s+equals?\s+(.+?)\b'],
            'negation': [r'\bnot\s+(.+?)\b', r'\bno\s+(.+?)\b', r'\bnever\s+(.+?)\b'],
            'exclusive': [r'\beither\s+(.+?)\s+or\s+(.+?)\b', r'\bcannot\s+be\s+both\s+(.+?)\s+and\s+(.+?)\b'],
            'presupposition': [r'\b(have|has|did)\s+you\s+(stopped|quit|failed)\s+', r'\bwhy\s+did\s+.+\s+(fail|stop|die)\b'],
            'ambiguity': [r'\b(every|all)\s+\w+\s+.*\s+a\s+\w+\b', r'\b(he|she|it|they)\s+was\s+(wrong|right|told)\b'], # Simplified scope/pronoun checks
            'subjectivity': [r'\b(best|worst|favorite|most\s+beautiful)\s+\w+\b'],
            'false_dichotomy': [r'\beither\s+(.+?)\s+or\s+(.+?)\b(?!.*\bother\b)']
        }
        self.stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare', 'ought', 'used', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now'}

    def _normalize_text(self, text: str) -> str:
        return text.lower().strip()

    def _extract_literals(self, text: str) -> List[str]:
        """Extract potential atomic propositions."""
        # Simple split by conjunctions and punctuation, filter noise
        cleaned = re.sub(r'[,.!?;:]', ' ', text)
        cleaned = re.sub(r'\b(if|then|else|or|and|but|either|neither|both)\b', ' ', cleaned)
        parts = [p.strip() for p in re.split(r'\s{2,}|\.|,|;', cleaned) if p.strip()]
        literals = []
        for p in parts:
            words = p.split()
            if len(words) > 0 and len(words) < 15 and not any(w in self.stop_words for w in words if len(w)>2):
                literals.append(p)
        # Deduplicate roughly
        unique = []
        seen = set()
        for l in literals:
            if l not in seen:
                unique.append(l)
                seen.add(l)
        return unique if unique else [text[:50]] # Fallback

    def _build_graph(self, text: str, literals: List[str]) -> Tuple[np.ndarray, List[str]]:
        """Build adjacency matrix W based on extracted constraints."""
        n = len(literals)
        if n == 0:
            return np.array([]), []
        
        W = np.zeros((n, n))
        text_lower = text.lower()
        
        # Map literals to indices for faster lookup (substring matching)
        def get_idx(sub):
            sub_norm = sub.lower().strip()
            for i, lit in enumerate(literals):
                if sub_norm in lit.lower() or lit.lower() in sub_norm:
                    return i
            return -1

        # 1. Implications (Weight 1.0)
        for pattern in self.patterns['implication']:
            matches = re.findall(pattern, text_lower)
            for m in matches:
                i, j = get_idx(m[0]), get_idx(m[1])
                if i != -1 and j != -1 and i != j:
                    W[j, i] = 1.0 # Column i affects Row j (W[j,i] means i->j)

        # 2. Equivalence/Order (Weight 0.5)
        for pattern in self.patterns['equivalence']:
            matches = re.findall(pattern, text_lower)
            for m in matches:
                i, j = get_idx(m[0]), get_idx(m[1])
                if i != -1 and j != -1 and i != j:
                    W[j, i] = 0.5
                    W[i, j] = 0.5

        # 3. Mutual Exclusion / Negation (Weight -1.0 for exclusion logic)
        # Handling "Either A or B" as A -> not B (simplified)
        for pattern in self.patterns['exclusive']:
            matches = re.findall(pattern, text_lower)
            for m in matches:
                if isinstance(m, tuple):
                    i, j = get_idx(m[0]), get_idx(m[1])
                else:
                    # Fallback for single match groups if regex varies
                    continue
                if i != -1 and j != -1 and i != j:
                    W[j, i] = -1.0 
                    W[i, j] = -1.0

        # Self-loops for stability (optional, but helps convergence)
        np.fill_diagonal(W, 0.1)
        
        return W, literals

    def _propagate(self, W: np.ndarray, s_init: np.ndarray) -> np.ndarray:
        """Iterate s = sigma(W^T s) until convergence."""
        if W.size == 0:
            return s_init
        
        s = s_init.copy()
        WT = W.T
        for _ in range(50): # Max iterations
            s_new = np.clip(WT @ s, 0, 1)
            # Add inertia to prevent oscillation
            s = 0.5 * s + 0.5 * s_new 
            if np.linalg.norm(s_new - s, 1) < 1e-3:
                break
        return s

    def _calculate_order_parameter(self, s: np.ndarray, W: np.ndarray, threshold: float = 0.5) -> float:
        """Calculate fraction of satisfied constraints."""
        if W.size == 0 or len(s) == 0:
            return 0.5
            
        satisfied = 0
        total = 0
        n = len(s)
        
        for i in range(n):
            for j in range(n):
                w = W[i, j]
                if w == 0: continue
                total += 1
                
                # Check constraint satisfaction
                # Implication (w=1): if s[j] high, s[i] should be high
                if w > 0:
                    if (s[j] >= threshold and s[i] >= threshold) or (s[j] < threshold):
                        satisfied += 1
                # Exclusion (w<0): if s[j] high, s[i] should be low
                else:
                    if (s[j] >= threshold and s[i] < threshold) or (s[j] < threshold):
                        satisfied += 1
                        
        return satisfied / total if total > 0 else 0.5

    def _calculate_susceptibility(self, W: np.ndarray, s_base: np.ndarray, threshold: float = 0.5) -> float:
        """Calculate chi via finite difference perturbations."""
        if W.size == 0 or len(s_base) == 0:
            return 0.0
            
        n = len(s_base)
        deltas = []
        base_O = self._calculate_order_parameter(s_base, W, threshold)
        
        for i in range(n):
            s_pert = s_base.copy()
            s_pert[i] = 1.0 - s_pert[i] # Flip
            s_conv = self._propagate(W, s_pert)
            new_O = self._calculate_order_parameter(s_conv, W, threshold)
            deltas.append((new_O - base_O)**2)
            
        return np.sqrt(np.mean(deltas)) if deltas else 0.0

    def _meta_confidence(self, prompt: str) -> float:
        """
        Check for Tier B traps: presupposition, ambiguity, subjectivity.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition
        for pat in self.patterns['presupposition']:
            if re.search(pat, p_lower):
                return 0.2
        
        # 2. Subjectivity
        for pat in self.patterns['subjectivity']:
            if re.search(pat, p_lower):
                return 0.3
                
        # 3. Ambiguity markers (simplified)
        for pat in self.patterns['ambiguity']:
            if re.search(pat, p_lower):
                # Only penalize if question asks "who" or similar
                if re.search(r'\b(who|which|whose)\b', p_lower):
                    return 0.25

        # 4. False Dichotomy check (heuristic)
        if re.search(r'\beither\b', p_lower) and not re.search(r'\bother\b', p_lower):
             if re.search(r'\bquestion|choose|pick\b', p_lower):
                return 0.4

        return 1.0

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z1 = zlib.compress(s1.encode())
        z2 = zlib.compress(s2.encode())
        z12 = zlib.compress((s1 + s2).encode())
        max_len = max(len(z1), len(z2))
        if max_len == 0: return 0.0
        return (len(z12) - min(len(z1), len(z2))) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_clean = self._normalize_text(prompt)
        literals = self._extract_literals(prompt)
        W, _ = self._build_graph(prompt, literals)
        
        # Base state
        n = len(literals)
        s_init = np.full(n, 0.5) if n > 0 else np.array([])
        
        # Pre-calculate prompt metrics
        meta_cap = self._meta_confidence(prompt)
        
        for cand in candidates:
            cand_clean = self._normalize_text(cand)
            full_text = f"{prompt_clean} {cand_clean}"
            
            # Re-extract literals including candidate info if possible, 
            # but for scoring consistency, we evaluate the candidate's fit to the prompt's logic
            # We treat the candidate as a set of asserted truths.
            
            # 1. Structural Score (Phase Transition Logic)
            # We simulate the system with the candidate's assertions as fixed points
            if n > 0:
                s_cand = np.full(n, 0.5)
                # Assert candidate literals if they match
                for i, lit in enumerate(literals):
                    if lit in cand_clean or cand_clean in lit:
                        s_cand[i] = 1.0
                
                s_final = self._propagate(W, s_cand)
                O = self._calculate_order_parameter(s_final, W)
                chi = self._calculate_susceptibility(W, s_final)
                
                # Score formula: Consistency * Stability
                struct_score = O * np.exp(-chi)
            else:
                struct_score = 0.5 # No structure found

            # 2. Numeric/Computation Check (Constructive)
            # Detect simple comparisons like "9.11 < 9.9"
            comp_score = 1.0
            nums = re.findall(r"[-+]?\d*\.\d+|\d+", cand_clean)
            if len(nums) >= 2:
                try:
                    vals = [float(x) for x in nums]
                    # If candidate claims an order, verify it
                    if "less" in cand_clean and vals[0] >= vals[1]: comp_score = 0.1
                    if "greater" in cand_clean and vals[0] <= vals[1]: comp_score = 0.1
                    # Simple consistency: if numbers are present, ensure they aren't contradictory to prompt numbers
                    prompt_nums = re.findall(r"[-+]?\d*\.\d+|\d+", prompt_clean)
                    if prompt_nums:
                        # Rough check: does candidate contradict prompt numbers?
                        pass 
                except: pass

            # 3. NCD Tiebreaker (Max 15% influence)
            ncd = self._ncd_score(prompt_clean, cand_clean)
            # Normalize NCD to be a positive signal (lower distance = higher score)
            # But NCD is unreliable for reasoning, so we dampen it heavily.
            ncd_signal = 1.0 - ncd 
            
            # Final Score Composition
            # Structural: 60%, Computation: 25%, NCD: 15%
            final_score = (0.6 * struct_score) + (0.25 * comp_score) + (0.15 * ncd_signal)
            
            # Apply Meta-Confidence Cap (Epistemic Honesty)
            # If the prompt is ambiguous, even a "consistent" answer shouldn't be trusted fully
            if meta_cap < 0.5:
                final_score *= meta_cap

            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Order={O:.2f}, Susceptibility={chi:.2f}, MetaCap={meta_cap:.2f}"
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at meta-confidence limit.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # If meta_cap is low, return low confidence immediately
        if meta_cap < 0.3:
            return meta_cap
            
        # Evaluate the specific answer against the prompt
        res_list = self.evaluate(prompt, [answer])
        if not res_list:
            return 0.0
            
        base_score = res_list[0]['score']
        
        # Cap by meta confidence
        final_conf = min(base_score, meta_cap)
        
        # Never return > 0.9 unless it's a perfect structural match and no ambiguity
        if meta_cap == 1.0 and base_score > 0.95:
            return 0.95
            
        return float(np.clip(final_conf, 0.0, 1.0))
```

</details>
