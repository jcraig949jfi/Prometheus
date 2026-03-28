# Cellular Automata + Criticality + Neural Oscillations

**Fields**: Computer Science, Complex Systems, Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T17:02:01.212098
**Report Generated**: 2026-03-27T05:13:34.954556

---

## Nous Analysis

**Algorithm**  
1. **Token lattice** – Split each candidate answer into a ordered list of *n* tokens (words/punctuation). Create a 1‑D numpy array `state` of shape `(n,)` where each entry holds a small integer code representing the token’s logical class:  
   - 0 = neutral, 1 = affirmation, 2 = negation, 3 = comparative, 4 = causal, 5 = numeric, 6 = conditional.  
   The lattice is periodic (ring) to avoid boundary effects.  

2. **Local update rule (Cellular Automaton)** – For each site *i* compute the triplet `(state[i‑1], state[i], state[i+1])`. A lookup table `R` (size 3³ = 27) maps the triplet to a new state. `R` is initialized to emulate Rule 110 but with extra rows for the logical classes; e.g., if the triplet contains a negation followed by an affirmation, the center becomes negation (propagation of ¬). The rule is applied synchronously to produce `next_state`.  

3. **Criticality tuning** – After each full lattice sweep compute the *activity* `a_t = Σ|next_state−state|` (number of sites that changed). Track the running mean `μ_a` and variance `σ_a²`. Adjust a global bias parameter `b` (added to the rule table as a probabilistic flip with probability `σ(b·a_t)`) using simple gradient descent:  
   `b ← b − η·(a_t−a_target)` where `a_target` is set to the critical activity estimated from a power‑law fit of past avalanche sizes (distribution of consecutive `a_t` values). This keeps the system near the edge of chaos (maximal correlation length).  

4. **Neural‑oscillation modulation** – Two time‑scales are implemented:  
   - **Fast gamma step**: apply the CA update every iteration (Δt = 1).  
   - **Slow theta envelope**: every `K` iterations (e.g., K = 10) compute a global order parameter `m_t = |Σ s_i|/n` where `s_i = +1` for states in {affirmation, causal, numeric} and `−1` for {negation, comparative, conditional}. Store `m_t` in a buffer; after `L` theta cycles compute the susceptibility `χ = Var(m_t)·L`.  

5. **Scoring** – For a candidate answer compute:  
   - **Order score** `O = mean(m_t)` over the last theta window (higher = more globally consistent logical polarity).  
   - **Disorder score** `D = χ` (higher = system responsive to small perturbations).  
   The final scalar is `S = O / (1 + D)`. Answers with high internal consistency but not frozen (moderate susceptibility) receive higher `S`.  

**Parsed structural features** – The token coding extracts: negations, affirmations, comparatives (`>`, `<`, `equals`), causal cues (`because`, `therefore`), conditionals (`if`, `then`), numeric values, and ordering relations (via comparative codes). These are the only inputs to the CA rule; punctuation and stop‑words map to neutral.

**Novelty** – Combining a deterministic CA with a self‑tuned critical point and dual‑timescale oscillatory modulation is not found in standard NLP scoring tools. Existing work uses either pure rule‑based logic (e.g., theorem provers) or statistical similarity; none explicitly enforce critical dynamics or embed gamma/theta rhythms as algorithmic timers for constraint propagation.

**Ratings**  
Reasoning: 8/10 — The method captures logical consistency and sensitivity via measurable order and susceptibility, aligning with human‑like reasoning trade‑offs.  
Metacognition: 6/10 — Susceptibility provides a rudimentary confidence estimate, but no explicit self‑reflection on reasoning steps.  
Hypothesis generation: 5/10 — The system can explore alternative states through stochastic bias, yet it does not propose new hypotheses beyond answer revision.  
Implementability: 9/10 — Only numpy arrays, lookup tables, and simple loops are required; no external libraries or APIs.

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

- **Cellular Automata**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Criticality**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 36% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Neural Oscillations**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Cellular Automata + Criticality: strong positive synergy (+0.432). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Information Theory + Cellular Automata + Criticality (accuracy: 0%, calibration: 0%)
- Abductive Reasoning + Causal Inference + Neural Oscillations (accuracy: 0%, calibration: 0%)
- Active Inference + Neural Oscillations + Mechanism Design (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=33% cal=47% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-26T19:44:29.136293

---

## Code

**Source**: scrap

[View code](./Cellular_Automata---Criticality---Neural_Oscillations/tool.py)

<details>
<summary>Show code</summary>

```python
import numpy as np
import re
from collections import deque

class ReasoningTool:
    """
    Implements a Cellular Automaton-based reasoning engine tuned to criticality
    with neural oscillation modulation.
    
    Mechanism:
    1. Tokenizes text into logical classes (Affirmation, Negation, Causal, etc.).
    2. Runs a 1D Cellular Automaton (Rule 110 variant) on the token lattice.
    3. Tunes a global bias parameter to maintain 'criticality' (edge of chaos).
    4. Modulates updates with fast (gamma) and slow (theta) cycles.
    5. Scores based on logical consistency (Order) and responsiveness (Susceptibility).
    """

    # Logical Class Codes
    NEUTRAL, AFFIRM, NEGATE, COMPARE, CAUSAL, NUMERIC, COND = 0, 1, 2, 3, 4, 5, 6
    
    # Keywords mapping
    KEYWORDS = {
        'yes': AFFIRM, 'true': AFFIRM, 'correct': AFFIRM, 'indeed': AFFIRM,
        'no': NEGATE, 'false': NEGATE, 'incorrect': NEGATE, 'never': NEGATE, 'not': NEGATE,
        'greater': COMPARE, 'less': COMPARE, 'equal': COMPARE, 'more': COMPARE, 'than': COMPARE,
        'because': CAUSAL, 'therefore': CAUSAL, 'thus': CAUSAL, 'hence': CAUSAL, 'so': CAUSAL,
        'if': COND, 'then': COND, 'unless': COND, 'provided': COND,
        'one': NUMERIC, 'two': NUMERIC, 'three': NUMERIC, 'four': NUMERIC, 'five': NUMERIC,
        'six': NUMERIC, 'seven': NUMERIC, 'eight': NUMERIC, 'nine': NUMERIC, 'ten': NUMERIC
    }

    def __init__(self):
        self.bias = 0.0
        self.eta = 0.01
        self.a_target = 0.3  # Target activity for criticality
        self.history_a = deque(maxlen=50)
        self.theta_buffer = deque(maxlen=10)
        self.K = 10  # Theta cycle length

    def _tokenize(self, text: str) -> list[int]:
        """Convert text to list of logical class codes."""
        tokens = re.findall(r'\w+|[^\s\w]', text.lower())
        state = []
        for t in tokens:
            code = self.NEUTRAL
            if t in self.KEYWORDS:
                code = self.KEYWORDS[t]
            elif t.replace('.', '').replace('-', '').isdigit():
                code = self.NUMERIC
            elif any(c in t for c in ['>', '<', '=']):
                code = self.COMPARE
            state.append(code)
        # Ensure minimum length for CA
        if len(state) < 3:
            state += [self.NEUTRAL] * (3 - len(state))
        return state

    def _rule_110_logic(self, triplet: tuple) -> int:
        """Custom rule table combining Rule 110 dynamics with logical propagation."""
        l, c, r = triplet
        
        # Logical Propagation Rules (Priority 1)
        # Negation spreads: If neighbor is negation, center tends to negation
        if l == self.NEGATE or r == self.NEGATE:
            if c == self.AFFIRM:
                return self.NEGATE # Negation overrides affirmation
            if c == self.NEUTRAL:
                return self.NEGATE # Contagion
        
        # Causal chaining: Causal + Affirm -> Affirm
        if c == self.CAUSAL and (l == self.AFFIRM or r == self.AFFIRM):
            return self.AFFIRM
            
        # Standard Rule 110 lookup for logical classes mapped to binary
        # Map classes to binary: {0, 2, 4, 6} -> 0, {1, 3, 5} -> 1 (Arbitrary but consistent)
        # This preserves the "Rule 110" chaotic/computational property
        b_l = 0 if l in [0, 2, 4, 6] else 1
        b_c = 0 if c in [0, 2, 4, 6] else 1
        b_r = 0 if r in [0, 2, 4, 6] else 1
        
        # Rule 110: 111->0, 110->1, 101->1, 100->0, 011->1, 010->1, 001->1, 000->0
        idx = (b_l << 2) + (b_c << 1) + b_r
        rule_110_map = [0, 1, 1, 1, 0, 1, 1, 0] # Indices 0..7
        new_b = rule_110_map[idx]
        
        # Map back to original class if unchanged, else flip parity class
        if new_b == b_c:
            return c
        else:
            # Flip to opposite parity group
            if c in [0, 2, 4, 6]: return 1 # Move to affirmative/numeric group
            return 0 # Move to neutral/negate group

    def _run_ca(self, state: list[int], steps: int = 20) -> tuple[float, float, list[float]]:
        """Run CA with criticality tuning and oscillation modulation."""
        n = len(state)
        current = np.array(state, dtype=np.int8)
        # Initialize rule table R (simplified to function call for flexibility)
        
        m_history = []
        total_activity = 0
        
        # Precompute rule table for speed (27 entries for 3^3 states, simplified here)
        # We use the function directly for clarity in this constrained implementation
        
        for t in range(steps):
            next_state = current.copy()
            activity_t = 0
            
            # Gamma step: Update all cells
            for i in range(n):
                l = current[(i - 1) % n]
                c = current[i]
                r = current[(i + 1) % n]
                
                # Apply logic
                new_val = self._rule_110_logic((l, c, r))
                
                # Probabilistic flip based on bias (Criticality tuning)
                if np.random.rand() < abs(self.bias) * 0.1:
                    new_val = (new_val + 1) % 7 # Random perturbation
                
                if new_val != c:
                    activity_t += 1
                next_state[i] = new_val
            
            current = next_state
            total_activity += activity_t / n
            
            # Theta envelope: Compute order parameter every K steps
            if (t + 1) % self.K == 0:
                # m_t: +1 for {Affirm, Causal, Numeric}, -1 for {Negate, Compare, Cond}, 0 else
                s_i = np.where(np.isin(current, [1, 4, 5]), 1, 
                       np.where(np.isin(current, [2, 3, 6]), -1, 0))
                m_t = np.abs(np.sum(s_i)) / n if n > 0 else 0
                m_history.append(m_t)
            
            # Criticality adjustment (Gradient Descent on bias)
            self.history_a.append(activity_t / n)
            if len(self.history_a) > 5:
                avg_a = np.mean(self.history_a)
                self.bias -= self.eta * (avg_a - self.a_target)

        # Calculate Scores
        order_score = np.mean(m_history) if m_history else 0.0
        disorder_score = np.var(m_history) if len(m_history) > 1 else 0.0
        
        # Final Score S = O / (1 + D)
        final_score = order_score / (1.0 + disorder_score + 1e-6)
        return final_score, order_score, disorder_score

    def _extract_constraints(self, text: str) -> dict:
        """Extract structural features for baseline scoring."""
        t = text.lower()
        return {
            'neg_count': len(re.findall(r'\b(no|not|never|false|incorrect)\b', t)),
            'aff_count': len(re.findall(r'\b(yes|true|correct|indeed)\b', t)),
            'cond_count': len(re.findall(r'\b(if|then|unless|provided)\b', t)),
            'causal_count': len(re.findall(r'\b(because|therefore|thus|hence|so)\b', t)),
            'has_num': bool(re.search(r'\d+', t)),
            'has_comp': bool(re.search(r'[><=]', t))
        }

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Heuristic scorer based on structural parsing.
        Rewards logical consistency between prompt and candidate.
        """
        p_feat = self._extract_constraints(prompt)
        c_feat = self._extract_constraints(candidate)
        
        score = 0.5 # Base score
        
        # 1. Negation matching (Modus Tollens check)
        # If prompt implies negation, candidate should align
        if p_feat['neg_count'] > 0:
            if c_feat['neg_count'] > 0: score += 0.2
            else: score -= 0.2
        else:
            if c_feat['neg_count'] > c_feat['aff_count']: score -= 0.1
            
        # 2. Conditional/Causal density (Reasoning depth)
        if p_feat['cond_count'] > 0 or p_feat['causal_count'] > 0:
            # Candidate should ideally reflect some logical structure
            if c_feat['cond_count'] > 0 or c_feat['causal_count'] > 0:
                score += 0.2
            elif len(candidate.split()) > 3: # Long answers without logic markers might be fluff
                score -= 0.1
                
        # 3. Numeric consistency
        if p_feat['has_num'] and c_feat['has_num']:
            score += 0.1
            
        return max(0.0, min(1.0, score))

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        for cand in candidates:
            # 1. Structural Baseline (Primary Signal)
            struct_score = self._structural_score(prompt, cand)
            
            # 2. CA Criticality Score (Secondary Signal / Tiebreaker)
            state = self._tokenize(cand)
            ca_score, order, disorder = self._run_ca(state)
            
            # Combine: Weighted sum favoring structural integrity
            # CA score acts as a consistency multiplier
            final_score = 0.7 * struct_score + 0.3 * ca_score
            
            # Reasoning string generation
            reason = f"Structural: {struct_score:.2f}, CA Order: {order:.2f}, Susceptibility: {disorder:.2f}"
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reason
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on the evaluation score."""
        # Run evaluation for single candidate
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        # Normalize score to 0-1 range roughly (scores can exceed 1.0 slightly due to mechanics)
        raw_score = res[0]['score']
        return float(np.clip(raw_score, 0.0, 1.0))
```

</details>
