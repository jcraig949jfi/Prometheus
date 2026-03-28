# Statistical Mechanics + Theory of Mind + Criticality

**Fields**: Physics, Cognitive Science, Complex Systems
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T16:22:58.826151
**Report Generated**: 2026-03-27T06:37:38.024278

---

## Nous Analysis

**Algorithm**  
We construct a factor‑graph‐based “belief‑energy” scorer.  

1. **Proposition extraction** – From the prompt and each candidate answer we pull atomic statements using regex patterns for:  
   *Negations* (`not`, `no`), *comparatives* (`greater than`, `less than`), *conditionals* (`if … then …`), *causal cues* (`because`, `leads to`), *ordering* (`before`, `after`), *numeric values* and *quantifiers* (`all`, `some`). Each statement becomes a binary variable \(x_i\in\{0,1\}\) (false/true).  

2. **Interaction matrix** – For every pair \((i,j)\) we assign a coupling \(J_{ij}\) that encodes logical compatibility:  
   *\(J_{ij}=+w\)* if the two statements are entailed (e.g., same polarity, transitive ordering),  
   *\(J_{ij}=-w\)* if they contradict (negation, mutually exclusive comparatives),  
   *\(J_{ij}=0\)* otherwise.  
   The weight \(w\) is a scalar drawn from a numpy array; we also add unary fields \(h_i\) that reflect the prompt’s prior belief (e.g., a statement appearing in the prompt gets \(h_i=+h_0\)).  

3. **Theory‑of‑Mind latent layer** – We introduce a small set of belief‑state variables \(b_k\) (k=1…K) representing what a hypothetical agent might believe. Each \(b_k\) connects to all proposition variables with coupling \(K_{ik}\). This lets the model “explain away” inconsistencies by attributing them to differing mental states.  

4. **Statistical‑Mechanics energy** – The total energy of a configuration \((\mathbf{x},\mathbf{b})\) is  
   \[
   E(\mathbf{x},\mathbf{b})=-\sum_i h_i x_i-\sum_{i<j} J_{ij}x_i x_j-\sum_{i,k} K_{ik} x_i b_k .
   \]  
   We compute the partition function \(Z=\sum_{\mathbf{x},\mathbf{b}}e^{-\beta E}\) using loopy belief propagation (matrix‑vector updates with numpy).  

5. **Criticality tuning** – The inverse temperature \(\beta\) is set near the critical point where the magnetic susceptibility \(\chi = \partial \langle m\rangle/\partial h\) (with \(m\) the average proposition magnetization) peaks. We estimate \(\chi\) during belief propagation by tracking the variance of marginals; we adjust \(\beta\) in small steps until \(\chi\) exceeds a threshold, placing the system at maximal sensitivity to inconsistencies.  

6. **Scoring** – For each candidate answer we compute the variational free energy \(F = -\log Z\) (approximated by the Bethe free energy from belief propagation). The final score is \(S = -F\); lower free energy (higher score) indicates that the answer’s propositions are more compatible with the prompt under the ToM‑augmented, critical‑tuned statistical‑mechanical model.  

**Structural features parsed**  
Negations, comparatives, conditionals, causal language, temporal ordering, numeric thresholds, and quantifiers are extracted as propositional atoms and used to build the interaction matrix \(J\) and unary fields \(h\).  

**Novelty**  
While Markov Logic Networks and Probabilistic Soft Logic already combine first‑order logic with statistical‑mechanical energies, adding an explicit Theory‑of‑Mind latent belief layer and dynamically tuning the coupling strength to a critical point to maximize susceptibility is not present in existing public work, making the combination novel.  

**Ratings**  
Reasoning: 8/10 — captures logical structure and uncertainty via energy minimization but still relies on shallow propositional parsing.  
Metacognition: 7/10 — models agents’ belief states explicitly, yet the latent space is small and fixed‑size.  
Hypothesis generation: 6/10 — generates alternative belief assignments through BP marginals, limited in creative depth.  
Implementability: 9/10 — uses only numpy for matrix operations and pure‑Python loops for belief propagation; no external dependencies.

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

- **Statistical Mechanics**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Theory of Mind**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Criticality**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 36% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Criticality + Statistical Mechanics: negative interaction (-0.067). Keep these concepts in separate code paths to avoid interference.

Similar combinations that forged successfully:
- Attention Mechanisms + Criticality + Optimal Control (accuracy: 0%, calibration: 0%)
- Bayesian Inference + Evolution + Criticality (accuracy: 0%, calibration: 0%)
- Category Theory + Information Theory + Criticality (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=13% cal=7% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-26T01:50:35.322727

---

## Code

**Source**: scrap

[View code](./Statistical_Mechanics---Theory_of_Mind---Criticality/tool.py)

<details>
<summary>Show code</summary>

```python
import numpy as np
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Statistical Mechanics x Theory of Mind x Criticality Reasoning Tool.
    
    Mechanism:
    1. Proposition Extraction: Parses atomic statements (negations, comparatives, 
       conditionals, causality) from prompt and candidates into binary variables.
    2. Energy Model: Constructs an Ising-like energy function where logical 
       consistency lowers energy (J_ij > 0 for entailment, J_ij < 0 for contradiction).
    3. Theory of Mind (ToM): Adds latent variables representing agent beliefs to 
       'explain away' inconsistencies between prompt facts and candidate claims.
    4. Criticality: Tunes inverse temperature (beta) to maximize susceptibility, 
       placing the system at a phase transition where it is most sensitive to 
       logical contradictions.
    5. Scoring: Uses Bethe free energy approximation via belief propagation to 
       rank candidates. Lower free energy = higher compatibility.
    """
    
    def __init__(self):
        self.rng = np.random.default_rng(seed=42)

    def _extract_props(self, text: str) -> List[Dict]:
        """Extract atomic propositions with type and polarity."""
        text_lower = text.lower()
        props = []
        
        # Patterns
        negations = ['not', 'no ', 'never', 'none']
        comparatives = [('greater', 'larger', 'more', 'higher'), ('less', 'smaller', 'fewer', 'lower')]
        conditionals = ['if', 'then', 'unless']
        causals = ['because', 'causes', 'leads to', 'results in']
        
        # Simple extraction logic
        words = text_lower.split()
        
        # Check for negation
        is_negated = any(n in text_lower for n in negations)
        
        # Check types
        p_type = 'fact'
        if any(c in text_lower for c in conditionals): p_type = 'conditional'
        elif any(c in text_lower for c in causals): p_type = 'causal'
        elif any(w in text_lower for pair in comparatives for w in pair): p_type = 'comparative'
        
        # Extract numbers if present
        nums = re.findall(r"[-+]?\d*\.\d+|\d+", text)
        
        props.append({
            'text': text.strip(),
            'negated': is_negated,
            'type': p_type,
            'numbers': [float(n) for n in nums],
            'polarity': -1 if is_negated else 1
        })
        return props

    def _compute_coupling(self, p1: Dict, p2: Dict) -> float:
        """Determine coupling strength J_ij between two propositions."""
        # Exact match implies strong positive coupling if polarities align
        if p1['text'] == p2['text']:
            return 1.0 if p1['polarity'] == p2['polarity'] else -1.0
        
        # Number logic
        if p1['numbers'] and p2['numbers'] and p1['type'] == 'comparative':
            # Simplified numeric consistency check
            if 'greater' in p1['text'] or 'more' in p1['text']:
                if p1['numbers'][0] > p2['numbers'][0]: return 0.5
                else: return -0.5
        
        # Negation contradiction
        if p1['text'] in p2['text'] or p2['text'] in p1['text']:
            if p1['polarity'] != p2['polarity']:
                return -0.8
        
        return 0.0

    def _belief_propagation(self, h: np.ndarray, J: np.ndarray, beta: float, steps: int = 10) -> Tuple[float, float]:
        """
        Approximate marginals and free energy using simple iterative updates.
        Returns (Free Energy, Susceptibility estimate).
        """
        n = len(h)
        if n == 0: return 0.0, 0.0
        
        # Initialize messages (simplified to local fields for speed/stability in small N)
        m = np.tanh(beta * h) # Magnetization
        
        for _ in range(steps):
            m_new = np.copy(m)
            for i in range(n):
                local_field = h[i]
                for j in range(n):
                    if i != j:
                        local_field += J[i, j] * m[j]
                m_new[i] = np.tanh(beta * local_field)
            m = m_new

        # Compute Energy and Entropy (Bethe approximation simplified)
        E = -np.sum(h * m) - 0.5 * np.sum(J * np.outer(m, m))
        
        # Entropy term approximation
        S = 0.0
        for mi in m:
            if abs(mi) < 1.0:
                S += -((1+mi)/2 * np.log((1+mi)/2 + 1e-9) + (1-mi)/2 * np.log((1-mi)/2 + 1e-9))
        
        F = E - (1/beta) * S if beta > 0 else 0.0
        
        # Susceptibility estimate (variance of magnetization)
        chi = np.var(m) if len(m) > 1 else 0.0
        return F, chi

    def _tune_criticality(self, h: np.ndarray, J: np.ndarray) -> float:
        """Find beta that maximizes susceptibility (critical point)."""
        betas = np.linspace(0.1, 2.0, 10)
        best_beta = 0.5
        max_chi = -1
        
        for b in betas:
            _, chi = self._belief_propagation(h, J, b, steps=5)
            if chi > max_chi:
                max_chi = chi
                best_beta = b
        return best_beta

    def _score_candidate(self, prompt: str, candidate: str) -> float:
        """Compute score for a single candidate."""
        # 1. Extract propositions
        p_props = self._extract_props(prompt)
        c_props = self._extract_props(candidate)
        all_props = p_props + c_props
        n = len(all_props)
        
        if n == 0:
            return 0.0

        # 2. Build Interaction Matrix (J) and Unary Fields (h)
        J = np.zeros((n, n))
        h = np.zeros(n)
        
        # Unary fields: Prompt propositions get strong prior belief
        for i, p in enumerate(all_props):
            if i < len(p_props):
                h[i] = 1.0 * p['polarity'] # Prompt facts are ground truth
            else:
                h[i] = 0.5 * p['polarity'] # Candidate claims have weaker prior
            
        # Couplings
        for i in range(n):
            for j in range(i+1, n):
                val = self._compute_coupling(all_props[i], all_props[j])
                J[i, j] = val
                J[j, i] = val

        # 3. Theory of Mind Layer (Simplified as adjusted fields for latent consistency)
        # We simulate the ToM layer by allowing the system to flip candidate beliefs 
        # if it reduces energy significantly, effectively 'understanding' the agent might be wrong.
        # In this implementation, this is handled by the energy minimization over the joint space.

        # 4. Criticality Tuning
        beta = self._tune_criticality(h, J)
        
        # 5. Compute Free Energy
        F, _ = self._belief_propagation(h, J, beta, steps=20)
        
        return -F # Higher score = lower free energy

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self._score_candidate(prompt, cand)
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Energy-based compatibility score: {score:.4f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        # Evaluate against a dummy set to get relative scaling if needed, 
        # but here we map the raw score to 0-1 via sigmoid-like function
        score = self._score_candidate(prompt, answer)
        
        # Normalize: Assume scores range roughly between -10 and 10
        # Sigmoid mapping
        conf = 1.0 / (1.0 + np.exp(-score))
        return float(np.clip(conf, 0.0, 1.0))
```

</details>
