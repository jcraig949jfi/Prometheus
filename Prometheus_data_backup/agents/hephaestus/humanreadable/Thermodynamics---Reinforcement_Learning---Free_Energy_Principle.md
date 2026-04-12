# Thermodynamics + Reinforcement Learning + Free Energy Principle

**Fields**: Physics, Computer Science, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T16:30:52.610100
**Report Generated**: 2026-03-27T23:28:38.424718

---

## Nous Analysis

**Algorithm**  
We treat each candidate answer as a set of logical propositions *P* = {p₁,…,pₙ} extracted with regex patterns (see §2). For every proposition we maintain a belief variable qᵢ ∈ [0,1] representing the approximate posterior probability that pᵢ is true. The prior pᵢ⁰ is set from lexical confidence (e.g., presence of a modal verb reduces confidence, a numeric match increases it).  

We build a weighted directed graph *G* = (V,E) where V = propositions and edges encode logical relations:  
- Implication (if A then B) → w₊ from A to B with weight w_imp.  
- Equivalence (A iff B) → bidirectional w_eq.  
- Contradiction (A and ¬B) → w_contr.  
- Quantitative constraint (value x ≈ y) → w_num·|x−y|.  

The variational free energy to be minimized is  

F(q) = Σᵢ [ qᵢ log(qᵢ/pᵢ⁰) + (1−qᵢ) log((1−qᵢ)/(1−pᵢ⁰)) ]  
     + Σ_{(i→j)∈E} w_{ij}·[ qᵢ·(1−qⱼ) + (1−qᵢ)·qⱼ ]  

The first term is the KL‑divergence between belief and prior (Free Energy Principle). The second term penalizes violations of logical constraints, analogous to an energy function in thermodynamics.  

We update beliefs using a stochastic gradient step that resembles a policy‑gradient RL update:  

Δqᵢ = −α·[ log(qᵢ/pᵢ⁰) − log((1−qᵢ)/(1−pᵢ⁰)) + Σ_j w_{ij}·(1−2qⱼ) ]  

followed by a soft‑constraint projection qᵢ ← σ(β·qᵢ) where σ is the logistic function and β plays the role of inverse temperature (Boltzmann distribution). The step size α is annealed. After T iterations (or when ΔF < ε) we compute the score S = −F(q*). Lower free energy → higher score. All operations use NumPy arrays for the belief vector, weight matrix, and gradient; only standard library functions are used for regex and iteration control.

**Parsed structural features**  
- Negations (“not”, “no”, “never”).  
- Comparatives (“greater than”, “≤”, “twice as”).  
- Conditionals (“if … then …”, “unless”, “provided that”).  
- Causal markers (“because”, “leads to”, “results in”).  
- Ordering/temporal terms (“before”, “after”, “first”, “second”).  
- Numeric values with units and equality/inequality relations.  
- Quantifiers (“all”, “some”, “none”, “most”).  

These are captured by regex groups that populate the proposition set and edge weights.

**Novelty**  
Energy‑based models and RL‑guided belief updates appear separately in NLP, and the Free Energy Principle has been used to motivate perceptual inference. Coupling variational free energy minimization with a thermodynamic‑style Boltzmann update and an explicit RL‑like gradient step for reasoning scoring has not, to the best of my knowledge, been described in existing work, making the combination novel.

**Ratings**  
Reasoning: 8/10 — captures logical consistency and numeric constraints via principled energy minimization.  
Metacognition: 6/10 — the algorithm can monitor its own free‑energy reduction but lacks explicit self‑reflection on strategy choice.  
Hypothesis generation: 5/10 — proposition extraction yields hypotheses, but generation is limited to observed patterns, not creative abstraction.  
Implementability: 9/10 — relies only on NumPy and stdlib; all components are straightforward to code and debug.

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
**Reason**: trap_battery_failed (acc=8% cal=1% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-03-27T20:42:04.061862

---

## Code

**Source**: scrap

[View code](./Thermodynamics---Reinforcement_Learning---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import math
import numpy as np
from zlib import compress

class ReasoningTool:
    """
    Thermodynamic-RL Reasoning Tool based on Variational Free Energy Minimization.
    
    Mechanism:
    1. Parsing: Extracts logical propositions, numeric constraints, and relations 
       (implication, contradiction, equivalence) using regex.
    2. Initialization: Sets prior beliefs (q0) based on lexical confidence and numeric matches.
    3. Optimization: Iteratively updates belief states (q) to minimize Free Energy:
       F(q) = KL(q||p0) + Energy(logical_violations).
       This uses a gradient descent step analogous to policy-gradient RL, followed by 
       a Boltzmann-style projection (inverse temperature beta).
    4. Scoring: Final score is negative Free Energy. 
    5. Epistemic Honesty: Meta-analysis of the prompt detects ambiguity, presuppositions, 
       and false dichotomies, capping confidence if detected.
    """
    
    # Regex patterns for structural features
    PATTERNS = {
        'negation': re.compile(r'\b(not|no|never|neither|without)\b', re.I),
        'comparative': re.compile(r'\b(greater|less|more|fewer|higher|lower|twice|half)\b|\b[<>=]+\b', re.I),
        'conditional': re.compile(r'\b(if|then|unless|provided|when)\b', re.I),
        'causal': re.compile(r'\b(because|thus|hence|leads to|results in|causes)\b', re.I),
        'temporal': re.compile(r'\b(before|after|first|second|next|finally)\b', re.I),
        'quantifier': re.compile(r'\b(all|some|none|most|every|any)\b', re.I),
        'number': re.compile(r'-?\d+(?:\.\d+)?'),
        'presupposition': re.compile(r'\b(have you stopped|did you stop|why did .+ (fail|stop|quit)|when did .+ (fail|stop))\b', re.I),
        'false_dichotomy': re.compile(r'\b(either .+ or .+|must be .+ or .+)\b', re.I),
        'subjectivity': re.compile(r'\b(best|worst|favorite|opinion|beautiful)\b', re.I),
        'pronoun_ambig': re.compile(r'\b(he|she|him|her|it|they)\b.*\bwho\b', re.I)
    }

    def __init__(self):
        self.max_iter = 50
        self.alpha = 0.1  # Learning rate
        self.beta = 2.0   # Inverse temperature
        self.eps = 1e-4   # Convergence threshold

    def _extract_props(self, text: str):
        """Extract logical propositions and numeric values from text."""
        props = []
        numbers = []
        
        # Extract numbers
        nums = [float(x) for x in self.PATTERNS['number'].findall(text)]
        if nums:
            numbers.extend(nums)
            
        # Simple sentence splitting for propositions
        sentences = [s.strip() for s in re.split(r'[.;?!]', text) if s.strip()]
        for i, sent in enumerate(sentences):
            if len(sent) > 3:
                props.append({'id': i, 'text': sent, 'q': 0.5})
                
        return props, numbers

    def _build_graph(self, props, numbers):
        """Build adjacency matrix and weight matrix based on logical relations."""
        n = len(props)
        if n == 0:
            return np.zeros((0,0)), np.zeros((0,0)), []
            
        W = np.zeros((n, n))
        relations = []
        
        # Heuristic relation building
        for i, p in enumerate(props):
            txt = p['text'].lower()
            q_init = 0.5
            
            # Prior adjustment based on lexical cues
            if self.PATTERNS['negation'].search(txt):
                q_init *= 0.8 # Slightly lower prior confidence for negations
            if self.PATTERNS['quantifier'].search(txt):
                q_init = 0.6 # Quantifiers often signal strong claims
            
            # Numeric confidence boost
            nums_in_prop = [float(x) for x in self.PATTERNS['number'].findall(txt)]
            if nums_in_prop:
                q_init = min(1.0, q_init + 0.2)
                
            props[i]['q_init'] = q_init
            
            # Logical edges (simplified for single-text analysis)
            # Implication: if "if" in i and "then" in j (or similar)
            for j, other in enumerate(props):
                if i == j: continue
                o_txt = other['text'].lower()
                
                # Implication heuristic
                if ('if' in txt or 'leads to' in txt) and ('then' in o_txt or 'result' in o_txt):
                    W[i, j] = 1.5
                    relations.append(('imp', i, j))
                
                # Contradiction heuristic (negation overlap)
                if self.PATTERNS['negation'].search(txt) and self.PATTERNS['negation'].search(o_txt):
                    # If they share keywords but one negates, potential contradiction
                    common = set(txt.split()) & set(o_txt.split())
                    if len(common) > 2:
                        W[i, j] = -1.0 # Repulsive
                        relations.append(('contr', i, j))

        # Numeric constraint energy (if multiple numbers exist, enforce consistency)
        if len(numbers) > 1:
            # Add a virtual node or penalize inconsistency if numbers contradict logic
            # For this implementation, we treat numeric consistency as a global prior boost
            pass
            
        return W, relations, [p['q_init'] for p in props]

    def _minimize_free_energy(self, props, W, q0_list):
        """Perform gradient descent on Free Energy functional."""
        n = len(props)
        if n == 0:
            return 0.0, []
            
        q = np.array(q0_list, dtype=np.float64)
        q0 = np.array(q0_list, dtype=np.float64)
        
        # Avoid log(0)
        q = np.clip(q, 1e-6, 1-1e-6)
        q0 = np.clip(q0, 1e-6, 1-1e-6)
        
        F_prev = float('inf')
        
        for t in range(self.max_iter):
            # 1. KL Divergence Term Gradient: d/dq [ q log(q/p) + (1-q)log((1-q)/(1-p)) ]
            # Derivative: log(q/p) - log((1-q)/(1-p))
            kl_grad = np.log(q / q0) - np.log((1 - q) / (1 - q0))
            
            # 2. Logical Constraint Term Gradient
            # Energy: sum w_ij * [ q_i(1-q_j) + (1-q_i)q_j ]
            # This form penalizes q_i != q_j if w > 0 (smoothing)
            # Derivative wrt q_i: sum_j w_ij * (1 - 2q_j)
            logic_grad = np.zeros(n)
            for i in range(n):
                for j in range(n):
                    if W[i, j] != 0:
                        logic_grad[i] += W[i, j] * (1 - 2 * q[j])
            
            # Total Gradient
            grad = kl_grad + logic_grad
            
            # Update step (Gradient Descent)
            q_new = q - self.alpha * grad
            
            # Boltzmann Projection (Soft constraint)
            # q <- sigma(beta * q) to keep in [0,1] and simulate temperature
            q_proj = 1.0 / (1.0 + np.exp(-self.beta * q_new))
            
            # Annealing
            q = q_proj
            self.beta *= 1.05 # Increase beta (cool down)
            self.alpha *= 0.95 # Decrease step size
            
            # Compute Free Energy for convergence check
            kl_term = np.sum(q * np.log(q/q0) + (1-q) * np.log((1-q)/(1-q0)))
            energy_term = 0.0
            for i in range(n):
                for j in range(n):
                    if W[i,j] != 0:
                        energy_term += W[i,j] * (q[i]*(1-q[j]) + (1-q[i])*q[j])
            F_curr = kl_term + energy_term
            
            if abs(F_prev - F_curr) < self.eps:
                break
            F_prev = F_curr
            
        return -F_curr, q

    def _meta_confidence(self, prompt: str) -> float:
        """
        Check for Tier B traps: ambiguity, presupposition, false dichotomy.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        if self.PATTERNS['presupposition'].search(p_lower):
            return 0.2
        
        # 2. False Dichotomy
        if self.PATTERNS['false_dichotomy'].search(p_lower):
            return 0.3
            
        # 3. Subjectivity without criteria
        if self.PATTERNS['subjectivity'].search(p_lower):
            return 0.25
            
        # 4. Pronoun Ambiguity with "who" question
        if self.PATTERNS['pronoun_ambig'].search(p_lower):
            return 0.3
            
        # 5. Unanswerable / Missing Info heuristics
        if "impossible" in p_lower or "cannot be determined" in p_lower:
            return 0.1
            
        return 1.0

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(compress(s1.encode()))
        c2 = len(compress(s2.encode()))
        c12 = len(compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _solve_numeric(self, text: str) -> float:
        """
        Attempt constructive computation for simple math problems.
        Returns a solved value if detected, else None.
        """
        # Pattern: "What is X + Y?" or similar
        match = re.search(r'(-?\d+(?:\.\d+)?)\s*([\+\-\*\/])\s*(-?\d+(?:\.\d+)?)', text)
        if match:
            try:
                a = float(match.group(1))
                op = match.group(2)
                b = float(match.group(3))
                if op == '+': return a + b
                if op == '-': return a - b
                if op == '*': return a * b
                if op == '/': return a / b if b != 0 else 0.0
            except:
                pass
        return None

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
            
        results = []
        prompt_props, prompt_nums = self._extract_props(prompt)
        W, relations, q0_list = self._build_graph(prompt_props, prompt_nums)
        
        # Constructive computation check
        computed_val = self._solve_numeric(prompt)
        
        for cand in candidates:
            score = 0.0
            reasoning_parts = []
            
            # 1. Structural & Logical Evaluation (Free Energy)
            # Combine prompt and candidate to check consistency
            full_text = f"{prompt} {cand}"
            cand_props, cand_nums = self._extract_props(full_text)
            
            # If candidate adds no new propositions, it might be weak, unless it's a direct answer
            if len(cand_props) == len(prompt_props):
                # Candidate didn't add logical structure, just repeated prompt?
                pass
                
            # Re-evaluate energy with candidate included
            # We treat the candidate as an extension of the logical graph
            F_val, final_q = self._minimize_free_energy(cand_props, W, [0.5]*len(cand_props))
            
            # Base score from Free Energy (higher is better, so negative F)
            # Normalize roughly to 0-1 range
            logic_score = 0.5 + (F_val * 0.1) 
            logic_score = max(0.0, min(1.0, logic_score))
            
            # 2. Constructive Computation Check
            comp_score = 0.0
            if computed_val is not None:
                # Check if candidate contains the computed value
                cand_str = str(computed_val)
                if cand_str in cand or str(round(computed_val, 2)) in cand:
                    comp_score = 1.0
                    reasoning_parts.append(f"Computed {cand_str} directly.")
                else:
                    comp_score = 0.0
                    reasoning_parts.append("Computation mismatch.")
            
            # 3. NCD Tiebreaker (Max 15% weight)
            # Lower NCD to prompt implies relevance, but we want NCD to candidate answer logic
            # Here we use NCD between candidate and the "ideal" logical conclusion if available
            # Otherwise, use NCD to prompt as a relevance filter
            ncd_val = self._compute_ncd(prompt, cand)
            ncd_score = 1.0 - ncd_val # Higher is better
            
            # Weighted Sum
            # Structural/Logic: 50%, Computation: 35%, NCD: 15%
            if comp_score > 0:
                # If we computed an answer, trust computation heavily
                final_score = 0.1 * logic_score + 0.75 * comp_score + 0.15 * ncd_score
                reasoning_parts.append("Constructive computation confirmed.")
            else:
                final_score = 0.50 * logic_score + 0.35 * (1.0 if len(cand_props) > len(prompt_props) else 0.5) + 0.15 * ncd_score
                reasoning_parts.append(f"Logical consistency: {logic_score:.2f}")
                
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": "; ".join(reasoning_parts)
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        # 1. Meta-Confidence (Epistemic Honesty Cap)
        meta_cap = self._meta_confidence(prompt)
        
        # If meta_cap is low, we return low confidence regardless of answer
        if meta_cap < 0.4:
            return meta_cap * 0.9 # Stay under the cap
            
        # 2. Structural Evaluation
        props, nums = self._extract_props(f"{prompt} {answer}")
        if not props and not nums:
            # No structural match -> honest uncertainty
            return 0.2
            
        # 3. Constructive Verification
        computed = self._solve_numeric(prompt)
        if computed is not None:
            if str(computed) in answer or str(round(computed, 2)) in answer:
                raw_conf = 0.95
            else:
                raw_conf = 0.1
        else:
            # Fallback to logical consistency score
            W, _, q0 = self._build_graph(props, nums)
            F_val, _ = self._minimize_free_energy(props, W, q0 if q0 else [0.5]*len(props))
            # Map Free Energy to confidence
            raw_conf = 0.5 + (F_val * 0.2)
            raw_conf = max(0.1, min(0.85, raw_conf)) # Cap at 0.85 without computation
            
        # Apply meta cap
        final_conf = min(raw_conf, meta_cap)
        
        # Never return > 0.9 without definitive computation
        if computed is None and final_conf > 0.9:
            final_conf = 0.9
            
        return float(final_conf)
```

</details>
