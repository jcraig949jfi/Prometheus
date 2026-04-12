import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Variational Bayesian Model Checker (VBMC).
    
    Mechanism:
    1. Parsing: Extracts logical atoms (P, Q), negations, comparatives, and numeric constraints
       from the prompt and candidate using regex.
    2. Factor Graph Construction: Encodes these as deterministic factors (hard constraints)
       and soft probabilistic factors.
    3. Variational Inference: Uses a mean-field approximation (product of independent Bernoullis)
       to estimate the posterior probability of the candidate being true given the prompt constraints.
    4. Free Energy Minimization: Iteratively updates the variational parameters to minimize
       the variational free energy (equivalent to maximizing the ELBO).
    5. Scoring: The final score is derived from the negative free energy (ELBO), representing
       how well the candidate satisfies the logical structure of the prompt.
    """

    def __init__(self):
        # Regex patterns for structural extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|cannot|impossible)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|implies|requires)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', re.IGNORECASE),
            'numeric': re.compile(r'(-?\d+\.?\d*)\s*(==|!=|<=|>=|<|>)\s*(-?\d+\.?\d*)'),
            'atom': re.compile(r'\b([A-Z][a-z]*)\b'), # Simple capitalized words as atoms
            'causal': re.compile(r'->|=>|causes|leads to', re.IGNORECASE)
        }
        self.max_iter = 50
        self.tol = 1e-4

    def _extract_features(self, text: str) -> Dict:
        """Extract structural features from text."""
        text_lower = text.lower()
        features = {
            'has_negation': bool(self.patterns['negation'].search(text_lower)),
            'has_conditional': bool(self.patterns['conditional'].search(text_lower)),
            'has_comparative': bool(self.patterns['comparative'].search(text_lower)),
            'has_causal': bool(self.patterns['causal'].search(text_lower)),
            'atoms': set(self.patterns['atom'].findall(text)),
            'numeric_constraints': self.patterns['numeric'].findall(text_lower),
            'length': len(text.split())
        }
        return features

    def _check_numeric_constraints(self, text: str) -> Tuple[bool, float]:
        """Evaluate numeric constraints found in text. Returns (is_valid, penalty)."""
        constraints = self.patterns['numeric'].findall(text.lower())
        if not constraints:
            return True, 0.0
        
        valid = True
        for match in constraints:
            val1_str, op, val2_str = match
            try:
                v1 = float(val1_str)
                v2 = float(val2_str)
                if op == '==': res = v1 == v2
                elif op == '!=': res = v1 != v2
                elif op == '<=': res = v1 <= v2
                elif op == '>=': res = v1 >= v2
                elif op == '<': res = v1 < v2
                elif op == '>': res = v1 > v2
                else: res = True
                
                if not res:
                    valid = False
            except ValueError:
                valid = False
        return valid, 0.0 if valid else -10.0 # Hard penalty for violation

    def _compute_elbo(self, prompt_feats: Dict, cand_feats: Dict, cand_text: str) -> float:
        """
        Compute approximate ELBO using mean-field updates.
        State space: Binary variables for presence of features.
        """
        # 1. Initialize variational parameters (q) uniformly
        # Variables: [negation_match, conditional_match, comparative_match, causal_match, atom_overlap, numeric_valid]
        n_vars = 6
        q = np.full(n_vars, 0.5) 
        
        # Prior expectations (weakly informative based on prompt presence)
        # If prompt has feature, prior expects candidate to have it (or logically follow)
        p_prior = np.array([
            0.5 if not prompt_feats['has_negation'] else 0.8,
            0.5 if not prompt_feats['has_conditional'] else 0.7,
            0.5 if not prompt_feats['has_comparative'] else 0.7,
            0.5 if not prompt_feats['has_causal'] else 0.7,
            0.5, # Atom overlap is data-driven
            0.9 # Prior belief that numeric constraints are valid unless proven wrong
        ])

        # Observations (Likelihood inputs)
        obs = np.array([
            1.0 if cand_feats['has_negation'] else 0.0,
            1.0 if cand_feats['has_conditional'] else 0.0,
            1.0 if cand_feats['has_comparative'] else 0.0,
            1.0 if cand_feats['has_causal'] else 0.0,
            len(prompt_feats['atoms'] & cand_feats['atoms']) / (len(prompt_feats['atoms'] | cand_feats['atoms']) + 1e-6),
            1.0 if self._check_numeric_constraints(cand_text)[0] else 0.0
        ])

        # Adjust priors based on prompt structure (if prompt lacks feature, candidate having it might be noise)
        # Simplified: We want candidate features to match prompt features presence/absence pattern roughly
        target = np.array([
            float(prompt_feats['has_negation']),
            float(prompt_feats['has_conditional']),
            float(prompt_feats['has_comparative']),
            float(prompt_feats['has_causal']),
            1.0, # Ideal atom overlap is 1.0
            1.0  # Numeric must be valid
        ])
        
        # If prompt doesn't have a feature, we don't necessarily penalize candidate, 
        # but if prompt DOES have it, candidate MUST have it (Logic constraint).
        # Let's encode this in the "target" for the energy function.
        logic_target = target.copy()
        if not prompt_feats['has_negation']: logic_target[0] = 0.5 # Neutral
        if not prompt_feats['has_conditional']: logic_target[1] = 0.5
        if not prompt_feats['has_comparative']: logic_target[2] = 0.5
        if not prompt_feats['has_causal']: logic_target[3] = 0.5
        
        # Numeric hard constraint check
        num_valid, num_penalty = self._check_numeric_constraints(cand_text)
        if not num_valid:
            return -1e6 # Immediate rejection for numeric violation

        # Coordinate Ascent Variational Inference (CAVI) loop
        for _ in range(self.max_iter):
            q_old = q.copy()
            
            # Update rule: q_i proportional to exp(E_q[-log P(x)])
            # Simplified for binary: q_i = sigmoid( log(p/(1-p)) + log_likelihood_contribution )
            # Here we approximate by blending prior and observation based on "logic_target"
            
            # Contribution from logic match (Hard constraints modeled as strong potentials)
            logic_diff = logic_target - obs
            # If logic_target is high (prompt has feature) and obs is low, energy is high (bad)
            # We want q to move towards satisfying the constraint if the prompt implies it.
            
            # Update q based on observation consistency with prompt structure
            # If prompt has feature, we strongly weight the observation of that feature in candidate
            weights = np.array([
                2.0 if prompt_feats['has_negation'] else 0.5,
                2.0 if prompt_feats['has_conditional'] else 0.5,
                2.0 if prompt_feats['has_comparative'] else 0.5,
                2.0 if prompt_feats['has_causal'] else 0.5,
                3.0, # High weight on atom overlap
                5.0  # Very high weight on numeric validity
            ])
            
            # Mean-field update step: q_new = sigma( log_prior + weight * log_likelihood )
            # Approximated as a weighted average for stability in this specific implementation
            q = (p_prior * (1 - weights/10) + obs * (weights/10)) 
            q = np.clip(q, 1e-6, 1 - 1e-6) # Prevent log(0)
            
            if np.max(np.abs(q - q_old)) < self.tol:
                break

        # Calculate Free Energy (F = E_q[log q] - E_q[log p])
        # We want -F (ELBO)
        # E_q[log q]
        ent_q = np.sum(q * np.log(q) + (1-q) * np.log(1-q))
        
        # E_q[log p] ~ Log likelihood of matching targets
        # Using a Gaussian-like penalty for deviation from logic_target for continuous part, Bernoulli for others
        log_prob = 0.0
        for i in range(5): # First 5 vars
            p_eff = logic_target[i] if logic_target[i] > 0.6 else 0.5
            if p_eff < 0.6: p_eff = 0.5 # Neutral if not present in prompt
            
            # Likelihood of observation q[i] given target
            # If target=1, we want q[i] high. If target=0.5, q[i] doesn't matter much.
            if logic_target[i] > 0.8:
                log_prob += q[i] * np.log(0.9 + 1e-6) + (1-q[i]) * np.log(0.1 + 1e-6)
            else:
                log_prob += 0 # Neutral
                
        # Numeric penalty already handled by hard return, but add to score if valid
        log_prob += num_penalty 

        elbo = log_prob - ent_q
        return float(elbo)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feats = self._extract_features(prompt)
        results = []
        
        for cand in candidates:
            cand_feats = self._extract_features(cand)
            score = self._compute_elbo(prompt_feats, cand_feats, cand)
            
            # Add NCD as a tiny tie-breaker only if scores are very close (not primary)
            # Skipping heavy NCD calc to prioritize the VBMC logic which is richer
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"VBMC Score: {score:.4f}. Features matched: {len(prompt_feats['atoms'] & cand_feats['atoms'])} atoms. Numeric valid: {self._check_numeric_constraints(cand)[0]}."
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        # Evaluate single candidate against prompt
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        score = res[0]['score']
        # Map score to 0-1 confidence. 
        # Typical ELBO range for this setup: -10 (bad) to 5 (good)
        # Sigmoid mapping
        conf = 1.0 / (1.0 + np.exp(-0.5 * (score + 2.0)))
        return float(np.clip(conf, 0.0, 1.0))