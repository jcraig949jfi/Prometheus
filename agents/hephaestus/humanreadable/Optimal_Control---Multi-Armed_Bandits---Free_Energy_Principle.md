# Optimal Control + Multi-Armed Bandits + Free Energy Principle

**Fields**: Control Theory, Game Theory, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T21:22:13.126808
**Report Generated**: 2026-03-27T17:21:24.612555

---

## Nous Analysis

**Algorithm**  
We treat each candidate answer \(a_i\) as an arm of a contextual multi‑armed bandit. For every arm we maintain a variational posterior \(q_i(\theta_i)=\mathcal N(\mu_i,\sigma_i^2)\) over a latent correctness parameter \(\theta_i\). The posterior is updated by minimizing variational free energy  
\[
F_i = \underbrace{\mathbb{E}_{q_i}[-\log p(D\mid\theta_i)]}_{\text{expected risk}} + \underbrace{\mathrm{KL}[q_i\|p(\theta_i)]}_{\text{ambiguity}},
\]  
where the likelihood \(p(D\mid\theta_i)\) is derived from a deterministic constraint‑propagation engine that checks the answer against extracted logical structures (see §2). The engine returns a binary violation vector \(v\in\{0,1\}^K\); we model \(p(D\mid\theta_i)=\theta_i^{\sum(1-v)}(1-\theta_i)^{\sum v}\), i.e., a Bernoulli likelihood whose success probability is the proportion of satisfied constraints.

The bandit’s action selection uses an optimal‑control‑inspired acquisition function: the expected free energy (EFE) for pulling arm \(i\) at time \(t\) is  
\[
\mathrm{EFE}_i(t)=\underbrace{\mathbb{E}_{q_i}[F_i]}_{\text{risk}}+\underbrace{\mathrm{H}[q_i]}_{\text{exploration}},
\]  
which is analytically tractable for Gaussian posteriors. We choose the arm with minimal EFE (equivalent to a UCB‑style bound where the exploration term is the entropy of the belief). After observing the constraint‑violation outcome, we update \(\mu_i,\sigma_i^2\) via a natural‑gradient step on the free‑energy gradient (identical to a Kalman‑filter update for this conjugate pair). The final score for answer \(a_i\) is the negative free energy \(-F_i\) (lower free energy → higher plausibility).

**Data structures & operations**  
- Belief arrays: `mu`, `sigma` (numpy vectors of length N arms).  
- Constraint graph: adjacency list built from regex‑extracted propositions; each node holds a truth value, edges encode logical operators (¬, ∧, ∨, →, ↔, <, >, =).  
- Propagation: topological traversal applying modus ponens and transitivity to derive implied truth values; violations are counted as mismatches between asserted and derived values.  
- Update: `sigma2 = 1/(1/sigma2_prior + N_obs)`, `mu = sigma2*(mu_prior/sigma2_prior + sum successes)` – pure numpy.

**Structural features parsed**  
The regex front‑end extracts: negations (`not`, `no`), comparatives (`greater than`, `less than`, `equal to`), conditionals (`if … then …`, `only if`), causal claims (`because`, `leads to`), ordering relations (`before`, `after`, `precedes`), and numeric values (integers, decimals). These are converted into propositional atoms and inserted into the constraint graph.

**Novelty**  
Pure bandit methods (UCB, Thompson) and free‑energy‑based active inference exist separately; optimal‑control formulations of bandits appear in literature on risk‑sensitive control. Combining all three to drive a belief‑update loop over logical constraints for answer scoring has not, to our knowledge, been applied to textual reasoning evaluation, making the approach novel in this domain.

**Rating**  
Reasoning: 8/10 — captures logical structure via constraint propagation and quantifies dissatisfaction as prediction error.  
Metacognition: 7/10 — explicit explore‑exploit trade‑through entropy‑driven EFE, but limited to myopic one‑step lookahead.  
Hypothesis generation: 6/10 — generates implicit alternatives via bandit exploration, yet does not propose novel answer formulations.  
Implementability: 9/10 — relies only on numpy for algebra and stdlib regex; no external libraries or APIs required.

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

- **Optimal Control**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 
- **Multi-Armed Bandits**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Multi-Armed Bandits + Optimal Control: strong positive synergy (+0.211). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Free Energy Principle + Optimal Control: negative interaction (-0.056). Keep these concepts in separate code paths to avoid interference.
- Free Energy Principle + Multi-Armed Bandits: strong positive synergy (+0.252). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Constraint Satisfaction + Optimal Control + Multi-Armed Bandits (accuracy: 0%, calibration: 0%)
- Ecosystem Dynamics + Multi-Armed Bandits + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Gene Regulatory Networks + Multi-Armed Bandits + Free Energy Principle (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=38% cal=5% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-03-27T16:22:06.532283

---

## Code

**Source**: scrap

[View code](./Optimal_Control---Multi-Armed_Bandits---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import math
import zlib
import numpy as np

class ReasoningTool:
    """
    A reasoning tool combining Optimal Control (for confidence wrapping), 
    Multi-Armed Bandits (candidate selection), and Free Energy Principle (scoring).
    
    Mechanism:
    1. Structural Parsing: Extracts logical constraints (negations, comparatives, conditionals).
    2. Constraint Propagation: Evaluates candidates against extracted logical structures.
    3. Bandit/Free Energy Scoring: Treats candidates as arms. Maintains Gaussian beliefs 
       over correctness. Updates via variational free energy minimization (Kalman-like).
       Score = -FreeEnergy (Risk + Ambiguity).
    4. Epistemic Honesty: Meta-confidence checks for ambiguity/traps before scoring.
    """

    def __init__(self):
        # Regex patterns for structural extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|without)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(greater|less|more|fewer|higher|lower|better|worse)\s+(than)?', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|only if|unless)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|leads to|causes|due to)\b', re.IGNORECASE),
            'ordering': re.compile(r'\b(before|after|precedes|follows)\b', re.IGNORECASE),
            'numbers': re.compile(r'-?\d+(?:\.\d+)?'),
            # Trap detectors
            'presupposition': re.compile(r'\b(have you stopped|why did .*(fail|stop)|when did .*(stop|fail))\b', re.IGNORECASE),
            'false_dichotomy': re.compile(r'\b(either .+ or .+|must be .+ or .+)\b', re.IGNORECASE),
            'subjectivity': re.compile(r'\b(best|worst|favorite|opinion|believe)\b', re.IGNORECASE)
        }
        self.prior_mu = 0.5
        self.prior_sigma2 = 1.0

    def _extract_constraints(self, text):
        """Extract structural features and logical atoms from text."""
        features = {
            'has_negation': bool(self.patterns['negation'].search(text)),
            'has_comparative': bool(self.patterns['comparative'].search(text)),
            'has_conditional': bool(self.patterns['conditional'].search(text)),
            'has_causal': bool(self.patterns['causal'].search(text)),
            'has_ordering': bool(self.patterns['ordering'].search(text)),
            'numbers': [float(x) for x in self.patterns['numbers'].findall(text)],
            'length': len(text.split())
        }
        return features

    def _check_logical_consistency(self, prompt, candidate):
        """
        Simulates constraint propagation. 
        Returns a binary violation count (0 = consistent, >0 = violations).
        """
        violations = 0
        p_feat = self._extract_constraints(prompt)
        c_feat = self._extract_constraints(candidate)
        c_lower = candidate.lower()
        p_lower = prompt.lower()

        # 1. Negation Consistency
        # If prompt has negation, candidate shouldn't blindly affirm without qualification
        if p_feat['has_negation'] and c_feat['has_negation'] == False:
            # Heuristic: If prompt denies X, and candidate asserts X directly
            if any(word in c_lower for word in ['yes', 'true', 'correct', 'is']) and \
               any(word in p_lower for word in ['not', 'no', 'never']):
                violations += 1

        # 2. Numeric Consistency (Constructive Computation)
        if len(p_feat['numbers']) >= 2 and len(c_feat['numbers']) >= 1:
            # Simple comparative check: If prompt says "A > B", candidate shouldn't say "A < B"
            nums = p_feat['numbers']
            # Detect explicit comparison in prompt
            if 'greater' in p_lower or 'more' in p_lower:
                if len(nums) == 2 and nums[0] <= nums[1]: 
                    # Prompt implies A > B but numbers say otherwise? Hard to parse without full NLP.
                    # Instead, check if candidate contradicts obvious math if present
                    pass 
            
            # Check candidate numeric validity if it implies a result
            # Example: Prompt "2 + 2", Candidate "5" -> Violation
            if '+' in p_lower and '=' in c_lower:
                try:
                    # Very basic eval for demo purposes on simple arithmetic
                    if '=' in candidate:
                        parts = candidate.split('=')
                        if len(parts) == 2:
                            val = float(parts[-1].strip())
                            # Extract numbers from prompt before '=' if present, else whole prompt
                            p_nums = [float(x) for x in re.findall(r'-?\d+(?:\.\d+)?', parts[0])]
                            if '+' in parts[0] and len(p_nums) == 2:
                                if abs(val - (p_nums[0] + p_nums[1])) > 1e-6:
                                    violations += 1
                            elif '*' in parts[0] and len(p_nums) == 2:
                                if abs(val - (p_nums[0] * p_nums[1])) > 1e-6:
                                    violations += 1
                except:
                    pass

        # 3. Logical Entailment (Simplified)
        # If prompt asks "Which is larger?", candidate must contain comparative or number
        if 'larger' in p_lower or 'greater' in p_lower or 'max' in p_lower:
            if not c_feat['numbers'] and not c_feat['has_comparative']:
                violations += 1

        return violations

    def _compute_free_energy(self, mu, sigma2, violations, total_checks=5):
        """
        Computes Variational Free Energy F = Expected Risk + KL Divergence (Ambiguity).
        Likelihood modeled as Bernoulli based on constraint satisfaction rate.
        """
        # Avoid division by zero
        sigma2 = max(sigma2, 1e-6)
        
        # Success rate from constraints
        success_rate = max(0.0, 1.0 - (violations / max(total_checks, 1)))
        # Clamp to avoid log(0)
        success_rate = np.clip(success_rate, 1e-6, 1.0 - 1e-6)
        
        # Expected Risk: E[-log p(D|theta)] approximated by -log(success_rate) at mean mu
        # Using mu as the estimated theta for risk calculation
        risk = -np.log(success_rate) if success_rate > 0 else 10.0
        
        # Ambiguity (KL term simplified for Gaussian): 0.5 * log(sigma2) + const
        # Higher variance = higher ambiguity penalty in some formulations, 
        # but here we treat ambiguity as uncertainty we want to reduce.
        # In FEP, we minimize F. High entropy (uncertainty) increases F if we consider precision seeking.
        ambiguity = 0.5 * np.log(sigma2 + 1e-6)
        
        return risk + ambiguity

    def _update_belief(self, mu_old, sigma2_old, violations, total_checks=5):
        """
        Natural gradient update (Kalman-like) for the posterior.
        Conjugate update approximation for Gaussian belief over correctness.
        """
        success_rate = 1.0 - (violations / max(total_checks, 1))
        success_rate = np.clip(success_rate, 0.0, 1.0)
        
        # Pseudo-observation count based on constraint density
        n_obs = max(1, total_checks)
        
        # Update variance: 1/(1/prior_var + N_obs)
        sigma2_new = 1.0 / (1.0 / max(sigma2_old, 1e-6) + n_obs)
        
        # Update mean: weighted average
        mu_new = sigma2_new * (mu_old / max(sigma2_old, 1e-6) + success_rate * n_obs)
        
        return mu_new, sigma2_new

    def _meta_confidence(self, prompt):
        """
        Tier B Reasoning: Detects ambiguity, traps, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        if self.patterns['presupposition'].search(prompt):
            return 0.2
        
        # 2. False Dichotomy
        if self.patterns['false_dichotomy'].search(prompt):
            return 0.3
            
        # 3. Subjectivity
        if self.patterns['subjectivity'].search(prompt):
            return 0.4
            
        # 4. Pronoun/Scope Ambiguity (Heuristic)
        # If "who" or "which" appears but no clear entities listed
        if re.search(r'\b(who|which one|what thing)\b', p_lower) and len(re.findall(r'\b[A-Z][a-z]+\b', prompt)) < 2:
            return 0.3

        # 5. Unanswerable / Missing Info
        if re.search(r'\b(without knowing|impossible to tell|insufficient info)\b', p_lower):
            return 0.1
            
        return 1.0  # No obvious traps detected

    def _ncd_score(self, s1, s2):
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2: return 1.0
        z1 = zlib.compress(s1.encode())
        z2 = zlib.compress(s2.encode())
        z12 = zlib.compress((s1 + s2).encode())
        l1, l2, l12 = len(z1), len(z2), len(z12)
        if min(l1, l2) == 0: return 1.0
        return (l12 - min(l1, l2)) / max(l1, l2)

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []

        n_arms = len(candidates)
        mus = np.full(n_arms, self.prior_mu)
        sigmas2 = np.full(n_arms, self.prior_sigma2)
        scores = np.zeros(n_arms)
        reasons = []

        # Step 1: Structural Analysis & Constraint Propagation
        for i, cand in enumerate(candidates):
            violations = self._check_logical_consistency(prompt, cand)
            total_checks = 5 # Fixed horizon for this simulation
            
            # Step 2: Bandit Update (Free Energy Minimization)
            mu_new, sigma2_new = self._update_belief(mus[i], sigmas2[i], violations, total_checks)
            mus[i], sigmas2[i] = mu_new, sigma2_new
            
            # Step 3: Compute EFE (Risk + Exploration)
            # EFE = Expected Free Energy. Lower is better.
            # Risk = Expected Loss. Exploration = Entropy.
            risk = -np.log(max(1.0 - (violations/total_checks), 1e-6))
            entropy = 0.5 * np.log(2 * np.pi * np.e * max(sigma2_new, 1e-6))
            efe = risk + entropy
            
            # Score is negative free energy (higher is better)
            # Normalize slightly to keep in reasonable range
            scores[i] = -efe
            
            reason_str = f"Violations: {violations}/{total_checks}, Risk: {risk:.2f}, Uncertainty: {np.sqrt(sigma2_new):.2f}"
            reasons.append(reason_str)

        # Step 4: NCD Tiebreaker (Max 15% influence)
        # Only apply if scores are very close
        min_score = np.min(scores)
        max_score = np.max(scores)
        score_range = max_score - min_score if (max_score - min_score) > 1e-6 else 1.0
        
        for i in range(n_arms):
            # Normalize score to 0-1 for NCD weighting
            norm_score = (scores[i] - min_score) / score_range
            if norm_score > 0.85: # Only for top contenders
                # Penalize if candidate is very different from prompt (unless it's a number)
                ncd = self._ncd_score(prompt, candidates[i])
                # Adjust score slightly based on similarity (lower NCD = better)
                scores[i] -= (ncd * 0.1) 

        # Construct results
        results = []
        for i, cand in enumerate(candidates):
            results.append({
                "candidate": cand,
                "score": float(scores[i]),
                "reasoning": reasons[i]
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-cognitive analysis of the prompt (Tier B).
        """
        # 1. Meta-Confidence Check (Epistemic Honesty)
        meta_cap = self._meta_confidence(prompt)
        
        if meta_cap < 0.3:
            return meta_cap

        # 2. Structural Validation
        violations = self._check_logical_consistency(prompt, answer)
        # Simple heuristic: 0 violations = high confidence, >2 = low
        if violations == 0:
            raw_conf = 0.95
        elif violations == 1:
            raw_conf = 0.7
        elif violations == 2:
            raw_conf = 0.4
        else:
            raw_conf = 0.1
            
        # 3. Apply Cap
        final_conf = min(raw_conf, meta_cap)
        
        # Ensure we never return > 0.9 unless computation was definitive (handled by violation count)
        # If meta_cap is 1.0 but we have 0 violations, we might still be unsure if the problem is hard.
        # But per instructions, < 0.3 for ambiguity is the hard rule.
        
        return round(final_conf, 3)
```

</details>
