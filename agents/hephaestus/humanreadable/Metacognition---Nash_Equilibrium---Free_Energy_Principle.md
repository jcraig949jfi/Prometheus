# Metacognition + Nash Equilibrium + Free Energy Principle

**Fields**: Cognitive Science, Game Theory, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T02:58:37.499696
**Report Generated**: 2026-03-27T16:08:15.606685

---

## Nous Analysis

**Algorithm**  
1. **Parsing stage** – Using only `re` and `str` methods, extract a set of propositional atoms \(P=\{p_i\}\) from the prompt and each candidate answer. Atoms include:  
   - atomic predicates (e.g., “X > Y”),  
   - negated predicates (`not`),  
   - comparatives (`>`, `<`, `=`),  
   - conditionals (`if … then …`),  
   - causal verbs (`causes`, `leads to`),  
   - numeric constants.  
   Each atom is assigned an index and stored in a binary feature vector \(x\in\{0,1\}^k\) where \(k=|P|\).  

2. **Prediction‑error (free‑energy) computation** – For a candidate answer \(a\) we define a generative model \(M_a\) that predicts the truth value of each atom based on logical rules extracted from the prompt (modus ponens, transitivity, symmetry). Let \(\hat{y}_a = M_a x\) be the predicted truth‑value vector (real‑valued in \([0,1]\) obtained by fuzzy‑logic evaluation of rules). The observed truth‑value vector \(y\) is built from the prompt’s explicit facts (1 for true, 0 for false). The variational free energy for \(a\) is approximated by the squared prediction error:  
   \[
   F(a)=\|y-\hat{y}_a\|_2^2 .
   \]  
   This is computed with `numpy.linalg.norm`.  

3. **Metacognitive confidence** – Each answer carries a confidence estimate \(c_a = \exp(-\lambda F(a))\) (inverse free energy, \(\lambda\) a scaling constant). Confidence is updated after each evaluation step (error monitoring).  

4. **Nash‑equilibrium selection** – Treat the set of candidate answers as pure strategies in a symmetric game where the payoff to choosing \(a\) is \(-F(a)\). Mixed strategies \(\pi\) over answers evolve via replicator dynamics:  
   \[
   \dot{\pi}_a = \pi_a\bigl(-F(a)-\sum_b \pi_b(-F(b))\bigr).
   \]  
   Iterate until \(\|\dot{\pi}\|_1<\epsilon\) (using only numpy). The stationary distribution \(\pi^*\) is a Nash equilibrium: no unilateral deviation lowers expected free energy.  

5. **Scoring** – Final score for answer \(a\) is \(S_a = \pi^*_a \cdot c_a\). Higher \(S_a\) indicates a strategy that is both stable (equilibrium) and metacognitively confident.  

**Structural features parsed** – negations, comparatives, conditionals, numeric values, causal claims, ordering relations (transitive chains), and logical connectives (AND/OR via conjunction of atoms).  

**Novelty** – The triple binding of variational free‑energy minimization, evolutionary game‑theoretic equilibrium, and metacognitive confidence updating is not found in existing open‑source reasoning scorers; related work appears separately in predictive coding, Bayesian games, and metacognitive RL, but their conjunction for answer scoring is novel.  

**Ratings**  
Reasoning: 8/10 — captures logical consistency via prediction error and equilibrium, though limited to propositional fuzzy logic.  
Metacognition: 7/10 — provides confidence calibration and error monitoring, but relies on a simple exponential mapping.  
Hypothesis generation: 6/10 — generates hypotheses implicitly via answer strategies; does not propose new atoms beyond those extracted.  
Implementability: 9/10 — uses only regex, numpy, and basic loops; no external libraries or APIs required.

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

- **Metacognition**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Nash Equilibrium**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Free Energy Principle + Metacognition: strong positive synergy (+0.425). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Ergodic Theory + Metacognition + Nash Equilibrium (accuracy: 0%, calibration: 0%)
- Error Correcting Codes + Nash Equilibrium + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Mechanism Design + Nash Equilibrium + Free Energy Principle (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=30% cal=17% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-03-27T16:01:20.294442

---

## Code

**Source**: scrap

[View code](./Metacognition---Nash_Equilibrium---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
from zlib import compress

class ReasoningTool:
    """
    A reasoning tool integrating Metacognition, Nash Equilibrium, and Free Energy Principle.
    
    Mechanism:
    1. Parsing: Extracts propositional atoms (negations, comparatives, conditionals, numbers).
    2. Free Energy: Computes prediction error between prompt facts and candidate implications.
    3. Metacognition: Caps confidence based on prompt ambiguity (Tier B checks).
    4. Nash Equilibrium: Uses replicator dynamics to find stable strategy distribution over candidates.
    5. Scoring: Combines equilibrium stability with metacognitive confidence.
    """
    
    def __init__(self):
        self.lambda_scale = 2.0
        self.epsilon = 1e-4
        self.steps = 100
        
        # Tier B Patterns for Epistemic Honesty
        self.presupposition_patterns = [
            r"\bhave you stopped\b", r"\bwhy did.*(?:fail|stop|quit)\b", 
            r"\bwhen did.*(?:stop|fail)\b", r"\bsince.*(?:failed|stopped)\b"
        ]
        self.scope_patterns = [r"\bevery\s+\w+.*\ba\s+\w+\b"] # Simplified scope check
        self.pronoun_patterns = [r"\b(he|she|him|her)\b.*\bwho\b", r"\btold\s+\w+\s+he\b"]
        self.dichotomy_patterns = [r"\beither\s+.*\bor\s+.*\b", r"\bis it\s+.*\or\s+.*\?"]
        self.subjectivity_patterns = [r"\b(best|worst|favorite|beautiful)\b"]
        self.unanswerable_patterns = [r"\bwithout\s+information\b", r"\bmissing\s+data\b"]

    def _extract_atoms(self, text):
        """Extract structural atoms: negations, comparatives, numbers, conditionals."""
        atoms = []
        text_lower = text.lower()
        
        # Negations
        if re.search(r"\b(not|no|never|neither)\b", text_lower):
            atoms.append("has_negation")
            
        # Comparatives
        if re.search(r"\b(more|less|greater|smaller|higher|lower|better|worse)\b", text_lower):
            atoms.append("has_comparative")
        if re.search(r"[<>]=?", text):
            atoms.append("has_symbolic_comp")
            
        # Conditionals
        if re.search(r"\b(if|then|unless|otherwise)\b", text_lower):
            atoms.append("has_conditional")
            
        # Causal
        if re.search(r"\b(causes|leads to|results in|because|therefore)\b", text_lower):
            atoms.append("has_causal")
            
        # Numbers (extract count as a feature proxy)
        nums = re.findall(r"-?\d+\.?\d*", text)
        if nums:
            atoms.append(f"num_count:{len(nums)}")
            try:
                # Simple numeric consistency check
                vals = [float(n) for n in nums]
                if len(vals) >= 2:
                    if vals[0] > vals[1]: atoms.append("num_order_desc")
                    elif vals[0] < vals[1]: atoms.append("num_order_asc")
            except: pass
            
        # Logic connectors
        if re.search(r"\b(and|or|but|however)\b", text_lower):
            atoms.append("has_connector")
            
        return set(atoms)

    def _compute_ncd(self, s1, s2):
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2: return 1.0
        s1b = s1.encode()
        s2b = s2.encode()
        try:
            c1 = len(compress(s1b))
            c2 = len(compress(s2b))
            c12 = len(compress(s1b + s2b))
            min_len = min(c1, c2)
            if min_len == 0: return 1.0
            return (c12 - min_len) / (max(c1, c2) + 1e-6)
        except: return 0.5

    def _meta_confidence(self, prompt):
        """
        Tier B Check: Analyze prompt for ambiguity, presupposition, or unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition
        for pat in self.presupposition_patterns:
            if re.search(pat, p_lower): return 0.2
            
        # 2. Scope Ambiguity (Simplified heuristic)
        if re.search(r"\bevery\s+\w+.*\ba\s+\w+\b", p_lower) and "same" in p_lower:
            return 0.3
            
        # 3. Pronoun Ambiguity
        if re.search(r"\b(he|she|him|her)\b", p_lower) and re.search(r"\bwho\b", p_lower):
            return 0.3
            
        # 4. False Dichotomy
        if re.search(r"\beither\b", p_lower) and not re.search(r"\bor\s+not\b", p_lower):
             # Heuristic: if "either" exists but not explicit "or not", might be false dichotomy
             if "only" in p_lower: return 0.4
             
        # 5. Subjectivity
        for pat in self.subjectivity_patterns:
            if re.search(pat, p_lower):
                # Check if context implies objective measurement
                if "measurable" not in p_lower and "data" not in p_lower:
                    return 0.5
                    
        # 6. Unanswerability cues
        if re.search(r"\b(insufficient|missing|unknown)\b", p_lower):
            return 0.2
            
        return 1.0

    def _compute_free_energy(self, prompt_atoms, candidate_atoms):
        """
        Compute prediction error (Free Energy) between prompt structure and candidate.
        Lower F = better match.
        """
        # Create union of all possible atoms
        all_atoms = prompt_atoms.union(candidate_atoms)
        k = len(all_atoms) if all_atoms else 1
        
        # Vectorize
        p_vec = np.array([1.0 if a in prompt_atoms else 0.0 for a in all_atoms])
        c_vec = np.array([1.0 if a in candidate_atoms else 0.0 for a in all_atoms])
        
        # Generative model prediction: 
        # If prompt has "num_order_asc", candidate should ideally reflect it or not contradict.
        # Simplified: Direct mismatch penalty + logical implication penalty
        error = p_vec - c_vec
        
        # Specific logical rules (Modus Ponens approximation)
        # If prompt has conditional, candidate should not be a bare fact without condition
        if "has_conditional" in prompt_atoms and "has_conditional" not in candidate_atoms:
            # Penalize missing structure
            error = np.append(error, 0.5) 
            
        return float(np.linalg.norm(error)**2)

    def _replicator_dynamics(self, free_energies):
        """
        Evolve mixed strategies via replicator dynamics to find Nash Equilibrium.
        Payoff = -FreeEnergy.
        """
        n = len(free_energies)
        if n == 0: return []
        if n == 1: return [1.0]
        
        # Initialize uniform distribution
        pi = np.ones(n) / n
        F = np.array(free_energies)
        payoffs = -F # Higher payoff = lower free energy
        
        for _ in range(self.steps):
            avg_payoff = np.dot(pi, payoffs)
            delta = pi * (payoffs - avg_payoff)
            pi_new = pi + 0.1 * delta # Learning rate
            pi_new = np.clip(pi_new, 0, 1)
            sum_pi = np.sum(pi_new)
            if sum_pi > 0:
                pi_new /= sum_pi
            else:
                pi_new = np.ones(n) / n # Reset if collapse
            
            if np.linalg.norm(pi_new - pi) < self.epsilon:
                break
            pi = pi_new
            
        return pi.tolist()

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
            
        prompt_atoms = self._extract_atoms(prompt)
        meta_cap = self._meta_confidence(prompt)
        
        # 1. Parse candidates and compute Free Energy
        free_energies = []
        candidate_data = []
        
        for cand in candidates:
            cand_atoms = self._extract_atoms(cand)
            # Add prompt atoms that should be inherited
            # (Simplified: assume candidate inherits prompt context unless contradicted)
            F_val = self._compute_free_energy(prompt_atoms, cand_atoms)
            free_energies.append(F_val)
            candidate_data.append({
                "candidate": cand,
                "atoms": cand_atoms,
                "F": F_val
            })
            
        # 2. Nash Equilibrium Selection
        pi_star = self._replicator_dynamics(free_energies)
        
        # 3. Scoring
        results = []
        max_F = max(free_energies) + 1e-6
        min_F = min(free_energies)
        
        for i, data in enumerate(candidate_data):
            F_a = data["F"]
            pi_a = pi_star[i] if i < len(pi_star) else 0
            
            # Metacognitive confidence: exp(-lambda * F) capped by meta-analysis
            raw_conf = np.exp(-self.lambda_scale * (F_a - min_F))
            conf = min(raw_conf, meta_cap)
            
            # Final Score: Equilibrium weight * Metacognitive Confidence
            # Add NCD as minor tiebreaker (< 15% influence)
            ncd_score = 1.0 - self._compute_ncd(prompt, data["candidate"])
            structural_score = pi_a * conf
            
            # Weighted sum: 85% structural, 15% NCD
            final_score = 0.85 * structural_score + 0.15 * ncd_score
            
            # Reasoning string
            reason = f"Free Energy: {F_a:.2f}, Equilibrium Weight: {pi_a:.2f}, Meta-Cap: {meta_cap:.2f}"
            if meta_cap < 0.6:
                reason += " [Warning: Prompt ambiguity detected]"
                
            results.append({
                "candidate": data["candidate"],
                "score": float(final_score),
                "reasoning": reason
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1. 
        Strictly capped by meta-cognitive analysis of the prompt.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # If prompt is ambiguous, return low confidence immediately
        if meta_cap < 0.3:
            return meta_cap
            
        # Compute structural match
        p_atoms = self._extract_atoms(prompt)
        a_atoms = self._extract_atoms(answer)
        F_val = self._compute_free_energy(p_atoms, a_atoms)
        
        # Base confidence on error
        # If F is 0, conf = 1. If F is high, conf -> 0
        base_conf = np.exp(-self.lambda_scale * F_val)
        
        # Apply cap
        final_conf = min(base_conf, meta_cap)
        
        # Never return > 0.9 unless computation was perfect (F approx 0)
        if F_val > 0.1:
            final_conf = min(final_conf, 0.9)
            
        return float(np.clip(final_conf, 0.0, 1.0))
```

</details>
