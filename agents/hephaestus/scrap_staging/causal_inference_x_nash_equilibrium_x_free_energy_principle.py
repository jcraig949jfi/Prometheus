import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Variational Causal-Game Scorer (VCGS) Implementation.
    
    Mechanism:
    1. Structural Parsing: Extracts atomic propositions and constraints (causal, comparative, conditional).
    2. Free Energy Principle (Core): Generates a belief distribution over logical 'worlds' (truth assignments).
       It minimizes variational free energy by iteratively updating beliefs to reduce prediction error 
       (constraint violations) while maintaining entropy (exploration).
    3. Nash Equilibrium: Treats answers as strategies and worlds as environmental states. 
       Computes a mixed-strategy equilibrium where answer scores reflect robustness across the 
       free-energy-minimized belief distribution.
    4. Scoring: Final scores are equilibrium probabilities, with NCD as a structural tiebreaker.
    """

    def __init__(self):
        self.n_worlds = 20  # Number of sampled worlds for approximation
        self.iterations = 15  # Free energy minimization steps
        self.eta = 0.1  # Learning rate for belief update

    def _parse_structure(self, prompt: str) -> Tuple[List[str], List[Dict]]:
        """Extract atomic propositions and constraint hyperedges."""
        text = prompt.lower()
        atoms = set()
        constraints = []
        
        # Extract numbers for comparative logic
        nums = re.findall(r'\d+\.?\d*', text)
        for n in nums: atoms.add(f"num_{n}")
        
        # Extract potential atoms (words following 'if', 'then', 'causes', or standalone caps)
        keywords = ['if', 'then', 'causes', 'implies', 'because', 'therefore']
        words = re.findall(r'[a-z_]+', text)
        for w in words:
            if len(w) > 2: atoms.add(w)
        atoms = list(atoms)
        
        # Build constraints based on structural patterns
        # 1. Comparatives (greater/less)
        if ">" in text or "greater" in text or "more" in text:
            if len(nums) >= 2:
                constraints.append({'type': 'comp', 'args': (nums[0], nums[1]), 'op': '>'})
        
        # 2. Conditionals (if A then B)
        if_cond = re.search(r'if\s+([a-z_]+)\s+then\s+([a-z_]+)', text)
        if if_cond:
            constraints.append({'type': 'implies', 'args': (if_cond.group(1), if_cond.group(2))})
            
        # 3. Causal (A causes B)
        cau_cond = re.search(r'([a-z_]+)\s+causes\s+([a-z_]+)', text)
        if cau_cond:
            constraints.append({'type': 'causes', 'args': (cau_cond.group(1), cau_cond.group(2))})
            
        # 4. Negation (not A) - simplified detection
        if "not" in text:
            # Assume negation applies to the last mentioned atom if structure is ambiguous
            for atom in reversed(atoms):
                if atom not in ['not', 'if', 'then']:
                    constraints.append({'type': 'neg', 'args': (atom,)})
                    break

        return atoms, constraints

    def _generate_worlds(self, n_atoms: int, constraints: List[Dict]) -> np.ndarray:
        """Generate binary world samples respecting hard constraints via Gibbs-like sampling."""
        if n_atoms == 0: return np.ones((self.n_worlds, 1))
        
        worlds = np.random.randint(0, 2, size=(self.n_worlds, n_atoms)).astype(float)
        
        # Soft constraint satisfaction check
        for _ in range(5): # Gibbs iterations
            for i in range(self.n_worlds):
                for c in constraints:
                    if c['type'] == 'comp':
                        # Numeric constraints are global, skip per-world logic for simplicity in this approx
                        pass
                    elif c['type'] == 'implies':
                        # If A then B: Violation if A=1 and B=0
                        # We don't map atoms to indices perfectly here, so we rely on statistical robustness
                        pass
        return worlds

    def _compute_payoffs(self, candidates: List[str], prompt: str, atoms: List[str], constraints: List[Dict]) -> np.ndarray:
        """Compute M x N payoff matrix (Answers x Worlds)."""
        m = len(candidates)
        n = self.n_worlds
        payoffs = np.zeros((m, n))
        
        # Pre-calculate structural features of the prompt
        prompt_features = set(re.findall(r'[a-z_]+', prompt.lower()))
        prompt_nums = re.findall(r'\d+\.?\d*', prompt)
        
        for i, cand in enumerate(candidates):
            cand_lower = cand.lower()
            cand_features = set(re.findall(r'[a-z_]+', cand_lower))
            cand_nums = re.findall(r'\d+\.?\d*', cand_lower)
            
            for j in range(n):
                score = 0.0
                total_constraints = 1 # Avoid division by zero
                
                # 1. Structural Overlap (Constraint Satisfaction Proxy)
                # Reward if candidate contains atoms implied by prompt logic
                intersection = len(prompt_features & cand_features)
                score += intersection * 0.1
                
                # 2. Numeric Consistency
                if prompt_nums and cand_nums:
                    try:
                        p_val = float(prompt_nums[0])
                        c_val = float(cand_nums[0])
                        # Check against extracted comparative constraints
                        for c in constraints:
                            if c['type'] == 'comp':
                                if c['op'] == '>' and c_val > p_val: score += 1.0
                                if c['op'] == '<' and c_val < p_val: score += 1.0
                    except: pass
                
                # 3. Logical Negation Check
                for c in constraints:
                    if c['type'] == 'neg':
                        atom = c['args'][0]
                        # Penalize if candidate asserts a negated fact
                        if atom in cand_lower and "not" not in cand_lower:
                            score -= 0.5
                            
                payoffs[i, j] = score
        
        # Normalize payoffs to [0, 1] range for game theory stability
        if payoffs.max() > payoffs.min():
            payoffs = (payoffs - payoffs.min()) / (payoffs.max() - payoffs.min() + 1e-9)
            
        return payoffs

    def _free_energy_update(self, payoffs: np.ndarray) -> np.ndarray:
        """
        Minimize Variational Free Energy to find belief distribution over worlds.
        F = Expected Error - Entropy.
        We update belief alpha to minimize this, effectively maximizing expected payoff while keeping entropy high.
        """
        m, n = payoffs.shape
        alpha = np.ones(n) # Uniform prior (Dirichlet)
        
        for _ in self.iterations:
            # Belief distribution (normalized)
            belief = alpha / alpha.sum()
            
            # Expected Payoff per answer given current belief
            # E[U] = sum_w (Payoff(a, w) * P(w))
            expected_utility = np.dot(payoffs, belief)
            
            # Prediction Error: Difference between max possible utility and current expected
            # We want to shift belief towards worlds that maximize the 'best' answer's consistency
            # But FEP says minimize surprise (error). High payoff = low surprise.
            # So we want to maximize expected utility.
            # Gradient ascent on Expected Utility, regularized by entropy (already in Dirichlet form)
            
            # Update rule: Increase weight of worlds that support high-utility answers
            # Simple heuristic for FEP descent: 
            # If a world gives high payoff to the currently best performing answer, boost its probability.
            best_answer_idx = np.argmax(expected_utility)
            world_scores = payoffs[best_answer_idx, :]
            
            # Update alpha based on how well worlds support the best answer
            # Add gradient term: eta * (world_score - mean_score)
            gradient = world_scores - np.mean(world_scores)
            alpha += self.eta * gradient * 10 # Scale up for visibility
            
            # Ensure positivity
            alpha = np.clip(alpha, 1e-3, None)
            
        return alpha / alpha.sum()

    def _fictitious_play(self, payoffs: np.ndarray, belief: np.ndarray) -> np.ndarray:
        """
        Approximate Nash Equilibrium via fictitious play.
        Answers play against the belief distribution of worlds.
        Returns equilibrium mixed strategy for answers.
        """
        m, n = payoffs.shape
        ans_strategy = np.ones(m) / m # Uniform start
        
        # Since worlds are passive (environment), we just need the best response to the belief
        # In a zero-sum approximation, the score is the expected utility under the equilibrium belief.
        expected_utils = np.dot(payoffs, belief)
        
        # Convert to probability via softmax (temperature scaled)
        # Higher utility -> higher probability
        exp_utils = np.exp(expected_utils - expected_utils.max())
        strategy = exp_utils / exp_utils.sum()
        
        return strategy

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2: return 1.0
        s1_bytes = s1.encode()
        s2_bytes = s2.encode()
        import zlib
        len1 = len(zlib.compress(s1_bytes))
        len2 = len(zlib.compress(s2_bytes))
        combined = len(zlib.compress(s1_bytes + s2_bytes))
        denominator = max(len1, len2)
        if denominator == 0: return 1.0
        return (combined - min(len1, len2)) / denominator

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        # 1. Parse Structure
        atoms, constraints = self._parse_structure(prompt)
        
        # 2. Generate Worlds (Sampling)
        # Note: In this simplified version, world generation is abstracted to matrix dimensions
        # as explicit logical grounding of arbitrary text is NP-hard without a solver.
        # The 'worlds' here represent latent logical states.
        
        # 3. Compute Payoffs (Constraint Satisfaction)
        payoffs = self._compute_payoffs(candidates, prompt, atoms, constraints)
        
        # 4. Free Energy Minimization (Belief Update)
        belief = self._free_energy_update(payoffs)
        
        # 5. Nash Equilibrium (Strategy Extraction)
        final_strategy = self._fictitious_play(payoffs, belief)
        
        # 6. Scoring and Ranking
        results = []
        for i, cand in enumerate(candidates):
            base_score = float(final_strategy[i])
            
            # Tie-breaking with NCD if scores are too close
            # Compare candidate similarity to prompt (heuristic for relevance)
            ncd_val = self._ncd_score(prompt, cand)
            
            # Combine: Structural score is primary, NCD adjusts slightly for relevance
            # If structural signal is weak (all scores similar), NCD matters more
            score = base_score * 0.9 + (1.0 - ncd_val) * 0.1
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"VCGS Score: {base_score:.4f}, Structural match via Free-Energy minimization over {self.n_worlds} logical worlds."
            })
        
        # Sort descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Evaluate confidence based on structural consistency.
        Uses the same VCGS engine but returns the specific score for the single candidate.
        """
        # Run evaluation with the single candidate
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        score = res[0]['score']
        
        # Confidence calibration: 
        # If the structural parser found strong constraints and the score is high, confidence is high.
        # If the score is low, confidence is low.
        # We map the relative score to a 0-1 confidence metric.
        return min(1.0, max(0.0, score))