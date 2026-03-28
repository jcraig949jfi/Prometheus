# Criticality + Compositionality + Mechanism Design

**Fields**: Complex Systems, Linguistics, Economics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T14:35:56.394392
**Report Generated**: 2026-03-27T16:08:11.291359

---

## Nous Analysis

**Algorithm**  
We build a *Weighted Constraint Hypergraph* (WCH) from the prompt and each candidate answer.  
1. **Parsing (Compositionality)** – Using a handful of regex patterns we extract atomic propositions \(p_i\) and binary relations \(r_{ij}\) (negation, comparative, conditional, causal, numeric equality/inequality, ordering). Each proposition becomes a node; each relation becomes a hyper‑edge linking its arguments with a type label (e.g., `NOT`, `GT`, `IF‑THEN`, `CAUSE`).  
2. **Constraint Encoding** – Every hyper‑edge is turned into a factor \(f_{ij}(x_i,x_j)\) that returns 1 if the relation holds under the Boolean assignment \(x\in\{0,1\}^n\) and 0 otherwise. Numeric comparisons are evaluated after parsing the extracted numbers with `float`.  
3. **Criticality‑Driven Inference** – We run loopy belief propagation (sum‑product) on the WCH to obtain node marginals \(μ_i = P(x_i=1)\). The *order parameter* is the average magnetization \(m = \frac{1}{n}\sum_i (2μ_i-1)\). The *susceptibility* χ is approximated by the variance of \(m\) under a small uniform field \(h\): χ ≈ \(\frac{\partial m}{\partial h}\big|_{h=0}\) computed by a finite‑difference BP run with \(h=±10^{-3}\). A system near criticality shows high χ and \(m≈0\).  
4. **Mechanism‑Design Scoring** – For each candidate answer we treat its propositions as *evidence* that adds unary factors \(g_i(x_i)=exp(β·[answer says p_i])\) with β > 0. We re‑run BP, obtain new \(m'\) and χ′. The score is a proper scoring rule:  
\[
S = -\big[(m'-m)^2 + λ(χ'-χ)^2\big],
\]  
where λ balances order and susceptibility. Answers that push the system toward higher order (|m'| larger) *and* reduce susceptibility (moving away from the critical point) receive higher scores, incentivizing truthful, coherent responses.  

**Parsed Structural Features** – negations (`not`, `no`), comparatives (`greater than`, `less than`, `≈`), conditionals (`if … then …`, `unless`), causal verbs (`cause`, `lead to`, `result in`), numeric values and units, ordering relations (`first`, `last`, `before`, `after`).  

**Novelty** – The combination is not a direct replica of existing work. While Markov Logic Networks and Probabilistic Soft Logic use weighted factors, and proper scoring rules appear in mechanism design, the explicit use of *criticality diagnostics* (susceptibility) as a regularizer for compositional inference is novel in the context of answer scoring.  

**Ratings**  
Reasoning: 8/10 — captures logical structure and uncertainty via BP, but approximations may miss higher‑order loops.  
Metacognition: 6/10 — susceptibility provides a global uncertainty signal, yet the model lacks explicit self‑monitoring of its own inference quality.  
Hypothesis generation: 7/10 — the BP marginals naturally generate alternative truth assignments as hypotheses, though ranking them relies on the scoring rule.  
Implementability: 9/10 — only regex, numpy array operations, and simple iterative BP; no external libraries or APIs needed.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 7/10 |
| Implementability | 9/10 |
| **Composite** | **7.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Criticality**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 36% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Compositionality**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Mechanism Design**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 38% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Compositionality + Criticality: strong positive synergy (+0.329). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Criticality + Mechanism Design: strong positive synergy (+0.232). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Criticality + Mechanism Design + Type Theory (accuracy: 0%, calibration: 0%)
- Fourier Transforms + Criticality + Compositionality (accuracy: 0%, calibration: 0%)
- Global Workspace Theory + Criticality + Compositionality (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=38% cal=29% ncd_acc=52% ncd_cal=49%)

**Forge Timestamp**: 2026-03-27T08:51:38.858610

---

## Code

**Source**: scrap

[View code](./Criticality---Compositionality---Mechanism_Design/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a Weighted Constraint Hypergraph (WCH) with Belief Propagation.
    Mechanism:
    1. Compositionality: Parses atomic propositions and relations (NOT, GT, IF, CAUSE).
    2. Criticality: Uses BP to find system magnetization (m) and susceptibility (chi).
    3. Mechanism Design: Scores candidates by how much they reduce susceptibility (chi)
       and increase order (|m|), incentivizing coherent, truthful answers.
    """
    
    def __init__(self):
        self.beta = 2.0  # Strength of evidence from candidate
        self.lambda_reg = 0.5  # Weight for susceptibility in scoring
        self.iterations = 20  # BP iterations
        
        # Regex patterns for structural parsing
        self.patterns = {
            'not': re.compile(r'\b(not|no|never|without)\b', re.I),
            'gt': re.compile(r'\b(greater than|more than|exceeds|larger than|>\b)', re.I),
            'lt': re.compile(r'\b(less than|fewer than|under|<\b)', re.I),
            'if': re.compile(r'\b(if|unless|provided that)\b', re.I),
            'cause': re.compile(r'\b(causes|leads to|results in|because|since)\b', re.I),
            'num': re.compile(r'-?\d+\.?\d*')
        }

    def _extract_props(self, text: str) -> List[str]:
        """Extract atomic propositions (simplified to sentences/clauses)."""
        # Split by common delimiters to get rough propositions
        raw = re.split(r'[.,;:?]', text)
        props = [p.strip() for p in raw if len(p.strip()) > 2]
        return props if props else ["default_prop"]

    def _build_graph(self, text: str) -> Tuple[List[str], List[Tuple[int, int, str]]]:
        """Parse text into nodes and edges (relations)."""
        props = self._extract_props(text)
        edges = []
        n = len(props)
        
        # Self-consistency edges (diagonal dominance approximation)
        for i in range(n):
            edges.append((i, i, 'SELF'))

        # Detect relations between propositions or within propositions
        for i, p in enumerate(props):
            lower_p = p.lower()
            
            # Negation
            if self.patterns['not'].search(p):
                edges.append((i, i, 'NOT'))
            
            # Comparatives (Numeric)
            nums = [float(x) for x in self.patterns['num'].findall(p)]
            if len(nums) >= 2:
                if self.patterns['gt'].search(p) or (len(nums)==2 and nums[0] > nums[1] and '>' in p):
                     # Logic: If p says A > B, and we assume p is true, then A>B holds.
                     # We model this as a constraint on the truth of p relative to reality
                     edges.append((i, i, 'NUM_GT'))
                elif self.patterns['lt'].search(p):
                    edges.append((i, i, 'NUM_LT'))

            # Conditionals (simplified: if present, adds conditional weight)
            if self.patterns['if'].search(p):
                edges.append((i, i, 'IF'))
                
            # Causal
            if self.patterns['cause'].search(p):
                edges.append((i, i, 'CAUSE'))

        return props, edges

    def _run_bp(self, n: int, edges: List, evidence: List[int], h_field: float = 0.0) -> Tuple[float, float]:
        """
        Run Loopy Belief Propagation.
        Returns (magnetization, susceptibility_approx).
        """
        if n == 0: return 0.0, 0.0
        
        # Initialize messages (uniform)
        # State: 0 (False), 1 (True)
        # Beliefs b[i] = [P(False), P(True)]
        beliefs = np.ones((n, 2)) * 0.5
        
        # Apply evidence as unary factors
        for i, val in enumerate(evidence):
            if val == 1:
                beliefs[i, :] = [0.01, 0.99] # Strong prior for True
            elif val == -1:
                beliefs[i, :] = [0.99, 0.01] # Strong prior for False

        # Add external field h_field to bias towards True/False slightly for susceptibility calc
        if h_field != 0:
            bias = np.array([np.exp(-h_field), np.exp(h_field)])
            beliefs *= bias
            beliefs /= beliefs.sum(axis=1, keepdims=True)

        for _ in range(self.iterations):
            new_beliefs = beliefs.copy()
            for i in range(n):
                # Collect messages from neighbors (simplified to self-consistency and global coupling)
                # In this compact implementation, we simulate constraints via local factors
                factor = np.ones(2)
                
                for (u, v, type_) in edges:
                    if u == i: # Self edge
                        if type_ == 'NOT':
                            factor *= np.array([0.1, 0.9]) if beliefs[i, 1] > 0.5 else np.array([0.9, 0.1])
                        elif type_ == 'NUM_GT':
                            # Encourage consistency with numeric logic (heuristic)
                            factor *= np.array([0.8, 1.2]) 
                        elif type_ == 'IF':
                            # Conditionals increase uncertainty slightly unless resolved
                            factor *= np.array([1.0, 1.0]) 
                    
                    # Simple pairwise coupling (global coherence)
                    if u != i and v == i:
                        # Encourage agreement with neighbors
                        factor *= beliefs[u] 

                # Normalize and update
                new_beliefs[i] = beliefs[i] * factor
                new_beliefs[i] /= new_beliefs[i].sum() + 1e-9
            
            beliefs = new_beliefs

        # Calculate Magnetization m = avg(2*P(True) - 1)
        p_true = beliefs[:, 1]
        m = np.mean(2 * p_true - 1)
        
        return m, p_true

    def _compute_score(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """Core logic: Build WCH, run BP, compute criticality-based score."""
        full_text = f"{prompt} {candidate}"
        props, edges = self._build_graph(full_text)
        n = len(props)
        
        if n == 0:
            return -1.0, "No structure found"

        # 1. Base run (Prompt only context)
        # Map candidate props to evidence
        # Heuristic: If candidate words appear in prompt props, they are asserted
        evidence = [0] * n 
        cand_words = set(self._extract_props(candidate))
        
        for i, p in enumerate(props):
            for cw in cand_words:
                if cw in p or p in cw:
                    evidence[i] = 1 # Asserted true by candidate
                    break
        
        # Run BP for base state (h=0)
        m_base, _ = self._run_bp(n, edges, evidence, h_field=0.0)
        
        # Run BP for susceptibility (h = +/- delta)
        delta = 1e-3
        m_plus, _ = self._run_bp(n, edges, evidence, h_field=delta)
        m_minus, _ = self._run_bp(n, edges, evidence, h_field=-delta)
        
        # Susceptibility chi ~ dm/dh
        chi = (m_plus - m_minus) / (2 * delta)
        
        # 2. Mechanism Design Scoring
        # Goal: Maximize order (|m|) and minimize susceptibility (chi)
        # A good answer should make the system decisive (high |m|) and stable (low chi)
        
        # Target: We want m to be far from 0 (decisive) and chi to be small (stable)
        # Score = -[(m_target - m_obs)^2 + lambda * chi^2]
        # Since we don't know m_target, we assume coherent answers push |m| towards 1.
        # So we maximize |m| and minimize chi.
        
        order_score = abs(m_base)
        stability_score = -abs(chi) # Lower chi is better
        
        final_score = order_score + self.lambda_reg * stability_score
        
        reason = f"Nodes:{n}, Magnetization:{m_base:.3f}, Susceptibility:{chi:.3f}"
        return final_score, reason

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        base_scores = []
        
        # First pass: get raw scores
        for cand in candidates:
            score, reason = self._compute_score(prompt, cand)
            base_scores.append((cand, score, reason))
            
        # Fallback to NCD if structural signal is weak (all scores very close)
        # But per instructions, NCD is only a tiebreaker. 
        # We rely on the WCH score primarily.
        
        # Normalize scores to 0-1 range for consistency if needed, but ranking is key
        sorted_candidates = sorted(base_scores, key=lambda x: x[1], reverse=True)
        
        for cand, score, reason in sorted_candidates:
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reason
            })
            
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on the scoring mechanism."""
        score, _ = self._compute_score(prompt, answer)
        # Map score (roughly -2 to 2) to 0-1
        # Assuming a good score is > 0, bad < 0
        conf = 1.0 / (1.0 + np.exp(-score)) # Sigmoid
        return max(0.0, min(1.0, conf))

# Example usage logic (not part of class, for context):
# tool = ReasoningTool()
# res = tool.evaluate("If A > B and B > C, is A > C?", ["Yes, A is greater than C", "No, A is less than C"])
# print(res)
```

</details>
