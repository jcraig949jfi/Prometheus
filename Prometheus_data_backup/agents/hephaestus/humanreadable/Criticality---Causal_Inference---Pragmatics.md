# Criticality + Causal Inference + Pragmatics

**Fields**: Complex Systems, Information Science, Linguistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T19:08:34.720047
**Report Generated**: 2026-03-27T06:37:39.463713

---

## Nous Analysis

**Algorithm**  
We treat each extracted proposition as a binary spin \(s_i\in\{-1,+1\}\) (false/true). A candidate answer fixes a subset of spins; the score is the negative free‑energy \(F = -\log Z\) of an Ising‑like system defined by three matrices built from the prompt:

1. **Causal coupling matrix \(J\)** – extracted via regex for patterns “*if* X then Y”, “*causes*”, “*leads to*”. For each directed edge \(i\rightarrow j\) we set \(J_{ij}=w_{\text{causal}}\) (positive if the edge supports \(s_i=+1\Rightarrow s_j=+1\), negative otherwise). Symmetrize: \(J_{ij}\leftarrow (J_{ij}+J_{ji})/2\) to obtain an undirected interaction energy \(-J_{ij}s_is_j\).

2. **Pragmatic field vector \(h\)** – derived from Gricean maxims and scalar implicatures. For each proposition we compute a bias:  
   - *Quantity*: “some X” → \(h_i=-0.4\) (penalizes asserting “all X”).  
   - *Quality*: negated statements → \(h_i=+0.3\) (rewards truth‑likeness).  
   - *Relation*: off‑topic clauses → \(h_i=-0.2\).  
   These are summed into \(h_i\).

3. **Criticality temperature \(T\)** – we tune the system near the Ising critical point where susceptibility \(\chi = \partial\langle s\rangle/\partial h\) diverges. Using mean‑field approximation, \(\chi = 1/(T - T_c)\) with \(T_c = \frac{1}{N}\sum_j|J_{ij}|\). We set \(T = T_c(1+\epsilon)\) with a small \(\epsilon=0.01\) to stay in the high‑susceptibility regime, maximizing sensitivity to mismatched spins.

**Scoring logic**  
Given a candidate answer vector \(s^{\text{ans}}\), compute energy  
\(E(s) = -\frac12\sum_{i,j}J_{ij}s_is_j - \sum_i h_i s_i\).  
Approximate the partition function \(Z\) via a single‑step mean‑field:  
\(m_i = \tanh\big((\sum_j J_{ij}m_j + h_i)/T\big)\) iterated to convergence (numpy).  
Free energy \(F = -\frac12\sum_{i,j}J_{ij}m_im_j - \sum_i h_i m_i + \frac{T}{2}\sum_i\big[(1+m_i)\ln\frac{1+m_i}{2}+(1-m_i)\ln\frac{1-m_i}{2}\big]\).  
Score = \(-F\) (higher = better). All operations use numpy arrays; parsing uses only `re` and `str` methods.

**Parsed structural features**  
Negations (`not`, `n’t`), comparatives (`more than`, `less than`), conditionals (`if … then …`, `unless`), numeric thresholds (`>5`, `≤3`), causal verbs (`cause`, `lead to`, `result in`), temporal ordering (`before`, `after`), quantifiers (`all`, `some`, `none`), and speech‑act markers (`I suggest`, `you must`).

**Novelty**  
Energy‑based neural models exist, but coupling an Ising criticality regime with explicit causal DAG extraction and Gricean‑style pragmatic fields in a pure‑numpy solver is not present in the literature; it combines statistical‑physics critical phenomena, causal inference, and pragmatics in a single scoring function.

**Rating**  
Reasoning: 8/10 — captures logical, causal, and pragmatic structure via a principled energy model.  
Metacognition: 6/10 — the method can estimate uncertainty via susceptibility but lacks explicit self‑reflective loops.  
Hypothesis generation: 7/10 — low‑energy spin flips suggest alternative interpretations, though generation is indirect.  
Implementability: 9/10 — relies only on regex, numpy linear algebra, and simple iteration; no external dependencies.

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
- **Causal Inference**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Pragmatics**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 36% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Causal Inference + Criticality: negative interaction (-0.065). Keep these concepts in separate code paths to avoid interference.
- Criticality + Pragmatics: strong positive synergy (+0.491). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Causal Inference + Pragmatics: strong positive synergy (+0.152). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Causal Inference + Pragmatics + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Criticality + Error Correcting Codes + Pragmatics (accuracy: 0%, calibration: 0%)
- Criticality + Pragmatics + Free Energy Principle (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=27% cal=13% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-26T01:12:34.537464

---

## Code

**Source**: scrap

[View code](./Criticality---Causal_Inference---Pragmatics/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np

class ReasoningTool:
    """
    Implements an Ising-model based reasoning engine.
    Mechanism:
    1. Parses prompt into binary propositions (spins) based on logical markers.
    2. Constructs a Causal Coupling Matrix (J) from conditional/causal patterns.
    3. Constructs a Pragmatic Field Vector (h) from Gricean maxims (negation, quantity).
    4. Evaluates candidate answers by fixing spins and computing Negative Free Energy.
    5. Uses Mean-Field Approximation near Criticality (T ~ Tc) to maximize sensitivity.
    """
    
    def __init__(self):
        self.causal_patterns = [
            (r'if\s+(.+?)\s+(?:then|,)?\s+(.+?)', 1.0),
            (r'(.+?)\s+causes?\s+(.+?)', 1.0),
            (r'(.+?)\s+leads?\s+to\s+(.+?)', 1.0),
            (r'unless\s+(.+?)\s+(.+?)', -1.0), # Unless A then B ~ If not A then B
        ]
        self.negation_words = ['not', "n't", 'no', 'never', 'none']
        self.quantifiers = ['all', 'every', 'some', 'few', 'most']

    def _tokenize(self, text):
        # Simple sentence splitting and lowercasing
        sentences = re.split(r'[.\?!]', text.lower())
        return [s.strip() for s in sentences if s.strip()]

    def _extract_features(self, text):
        """Extracts spins, J matrix components, and h vector components."""
        sentences = self._tokenize(text)
        n = max(len(sentences), 1)
        
        # Initialize structures
        # We map each sentence to a spin. +1 = true, -1 = false.
        h = np.zeros(n)
        J = np.zeros((n, n))
        
        # Map sentences to indices for causal links
        sent_map = {s: i for i, s in enumerate(sentences)}
        
        for i, sent in enumerate(sentences):
            # Pragmatic Field (h)
            # Quality: Negation penalty/reward heuristic
            if any(neg in sent for neg in self.negation_words):
                h[i] += 0.3 # Reward truth-likeness of negated statements if context fits
            
            # Quantity: "some" implies not "all"
            if 'some' in sent:
                h[i] -= 0.4 
            if 'all' in sent:
                h[i] += 0.2
                
            # Relation: Off-topic is hard to detect without context, 
            # but we assume prompt sentences are relevant.
            
        # Causal Coupling (J)
        for pattern, weight in self.causal_patterns:
            matches = re.findall(pattern, text.lower())
            for match in matches:
                # Try to find corresponding sentences
                s1, s2 = match[0].strip(), match[1].strip()
                idx1, idx2 = -1, -1
                
                # Fuzzy match to existing sentences
                for s, idx in sent_map.items():
                    if s1 in s: idx1 = idx
                    if s2 in s: idx2 = idx
                
                if idx1 != -1 and idx2 != -1:
                    J[idx1, idx2] += weight
                    J[idx2, idx1] += weight # Symmetrize immediately for undirected energy

        # Normalize J
        if n > 1:
            J = (J + J.T) / 2
            
        return sentences, h, J, n

    def _compute_free_energy(self, h, J, fixed_spins=None):
        """
        Computes negative free energy using Mean-Field Approximation.
        fixed_spins: dict {index: value} for candidate answer constraints.
        """
        n = len(h)
        if n == 0: return 0.0
        
        # Initialize magnetization m
        m = np.tanh(h) + 1e-6 
        
        # Apply fixed spins from candidate answer if provided
        if fixed_spins:
            for idx, val in fixed_spins.items():
                if 0 <= idx < n:
                    m[idx] = val

        # Critical Temperature Estimation
        Tc = np.mean(np.sum(np.abs(J), axis=1)) if n > 1 else 1.0
        if Tc == 0: Tc = 1.0
        T = Tc * 1.01 # Slightly above critical point
        
        # Iterate Mean-Field Equation: m_i = tanh((sum(J_ij * m_j) + h_i) / T)
        for _ in range(50): # Converge quickly
            m_old = m.copy()
            field = np.dot(J, m) + h
            
            # Apply fixed constraints during iteration
            if fixed_spins:
                for idx, val in fixed_spins.items():
                    if 0 <= idx < n:
                        field[idx] = np.arctanh(val) * T # Force the value
            
            m = np.tanh(field / T)
            
            if np.allclose(m, m_old, atol=1e-4):
                break

        # Free Energy F = E - TS
        # E = -0.5 * sum(J_ij * m_i * m_j) - sum(h_i * m_i)
        energy = -0.5 * np.sum(J * np.outer(m, m)) - np.sum(h * m)
        
        # Entropy S = -sum( (1+m)/2 * ln((1+m)/2) + (1-m)/2 * ln((1-m)/2) )
        # Avoid log(0)
        eps = 1e-9
        s_plus = (1 + m) / 2 + eps
        s_minus = (1 - m) / 2 + eps
        entropy = -np.sum(s_plus * np.log(s_plus) + s_minus * np.log(s_minus))
        
        F = energy - T * entropy
        return -F # Return Negative Free Energy (higher is better)

    def _parse_candidate(self, candidate, sentences):
        """
        Maps a candidate string to fixed spins.
        Returns dict {index: +1/-1}.
        """
        fixed = {}
        cand_lower = candidate.lower()
        
        # Heuristic: If candidate matches a sentence or keyword, fix that spin.
        # If candidate is "True"/"False", it applies to the main conclusion.
        
        is_true = any(x in cand_lower for x in ['true', 'yes', 'correct', 'does', 'is'])
        is_false = any(x in cand_lower for x in ['false', 'no', 'incorrect', 'not', "n't"])
        
        # If explicit boolean, apply to all extracted sentences as a consistency check?
        # Better: Apply to the last sentence (often the query) or specific matches.
        
        for i, sent in enumerate(sentences):
            # If candidate contains the sentence text
            if sent in cand_lower or cand_lower in sent:
                fixed[i] = 1.0 if is_true else (-1.0 if is_false else 1.0)
            
            # If candidate is a simple "Yes/No", we assume it affirms/denies the logical flow
            # We simulate this by checking if the candidate contradicts the sentence content
            if is_true and any(neg in sent for neg in self.negation_words):
                 # Affirming a negative statement -> Spin +1 (statement is true)
                 fixed[i] = 1.0
            elif is_false and not any(neg in sent for neg in self.negation_words):
                 # Denying a positive statement -> Spin -1 (statement is false)
                 fixed[i] = -1.0
                 
        # If no specific mapping found, default to global consistency check
        if not fixed:
            # Assume the candidate asserts the truth of the whole prompt logic
            if is_true:
                fixed = {i: 1.0 for i in range(len(sentences))}
            elif is_false:
                fixed = {i: -1.0 for i in range(len(sentences))}
                
        return fixed

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        sentences, h, J, n = self._extract_features(prompt)
        results = []
        
        # Baseline score using just prompt energy
        base_energy = self._compute_free_energy(h, J)
        
        for cand in candidates:
            fixed_spins = self._parse_candidate(cand, sentences)
            # Compute energy with candidate constraints
            score = self._compute_free_energy(h, J, fixed_spins)
            
            # Normalize slightly against base to prevent magnitude bias
            # Higher score = lower free energy = more stable state
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Ising Free Energy: {score:.4f} (Base: {base_energy:.4f})"
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on relative energy gap."""
        # Generate a dummy opposite to compare against if possible, 
        # or use absolute energy magnitude.
        # Here we use the score relative to a randomized baseline approximation.
        
        # 1. Get score for the answer
        res = self.evaluate(prompt, [answer])
        if not res: return 0.5
        score_ans = res[0]['score']
        
        # 2. Get score for a null/neutral hypothesis (approximated by empty constraint)
        # Actually, let's compare against the "False" version of the answer
        opposite = "False" if "true" in answer.lower() else "True"
        res_opp = self.evaluate(prompt, [opposite])
        score_opp = res_opp[0]['score'] if res_opp else score_ans
        
        # 3. Softmax-like normalization
        diff = score_ans - score_opp
        conf = 1.0 / (1.0 + np.exp(-diff)) # Sigmoid
        return float(np.clip(conf, 0.0, 1.0))
```

</details>
