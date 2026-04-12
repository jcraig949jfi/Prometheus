import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Information-Theoretic Adaptive Clonal Selection Dynamical System (IT-ACS-DS)
    
    Mechanism:
    1. Clonal Populations: Each candidate answer is a 'clone' hypothesis.
    2. Dynamical State: Each clone has a state x_i evolving via gradient flow.
    3. Fitness Function: 
       - Data Fit (KL approx): Negative structural mismatch between prompt constraints and candidate.
       - Memory Reuse (Mutual Info): Bonus if candidate shares semantic roots with high-performing structural patterns.
    4. Attractor Dynamics: Candidates settle into fixed points based on constraint satisfaction.
    5. Scoring: Final rank determined by the equilibrium state of the dynamical system.
    
    Implementation Strategy:
    - Structural Parsing: Extract negations, comparatives, conditionals, and numbers.
    - Constraint Propagation: Verify candidate against extracted logical constraints.
    - NCD: Used strictly as a tie-breaker for structural equivalence.
    """

    def __init__(self):
        self.memory_clones = []  # Stores successful structural signatures
        self.lambda_mem = 0.15   # Weight for memory mutual information
        self.noise_scale = 0.01  # Exploration noise

    def _structural_parse(self, text: str) -> dict:
        """Extract logical structure: negations, comparatives, conditionals, numbers."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither|nor)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|better|worse|than|>|<)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|otherwise|when)\b', text_lower)),
            'numbers': [],
            'length': len(text)
        }
        # Extract numbers for numeric evaluation
        nums = re.findall(r'-?\d+\.?\d*', text)
        features['numbers'] = [float(n) for n in nums]
        return features

    def _compute_structural_mismatch(self, prompt_feats: dict, cand_feats: dict) -> float:
        """
        Approximates KL Divergence between Prompt Constraints and Candidate Content.
        Lower value = better fit.
        """
        mismatch = 0.0
        
        # 1. Negation consistency (Simple heuristic: if prompt has strong negation, 
        #    candidate shouldn't blindly affirm without context, handled by length/overlap mostly)
        # Here we check if candidate contradicts prompt logic implicitly by length/diversity
        
        # 2. Numeric Consistency
        p_nums = prompt_feats['numbers']
        c_nums = cand_feats['numbers']
        
        if p_nums and c_nums:
            # Check if candidate numbers are plausible transformations of prompt numbers
            # Simple check: are they in the same order of magnitude or logical relation?
            # For now, penalize if candidate introduces random large numbers not in prompt
            for cn in c_nums:
                if not any(abs(cn - pn) < 1e-6 for pn in p_nums):
                    # Allow if it's a result of a simple operation, else small penalty
                    mismatch += 0.5 
        elif p_nums and not c_nums:
            # Prompt has numbers, candidate ignores them (potential failure)
            mismatch += 1.0

        # 3. Logical Keyword Overlap (Proxy for Mutual Information with constraints)
        # If prompt asks a comparative question, good answer often contains comparative words or specific numbers
        if prompt_feats['comparatives'] > 0:
            if cand_feats['comparatives'] == 0 and not c_nums:
                mismatch += 2.0 # High penalty for ignoring comparative nature
        
        if prompt_feats['conditionals'] > 0:
            # Candidate should ideally reflect conditional logic or provide a definitive outcome
            pass # Hard to verify without full NLI, rely on length/overlap

        return mismatch

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            denom = max(c1, c2)
            if denom == 0: return 0.0
            return (c12 - min(c1, c2)) / denom
        except:
            return 1.0

    def _dynamical_step(self, x: float, fitness: float, dt: float = 0.1) -> float:
        """Sigmoidal gradient flow update: dx/dt = -dV/dx + noise."""
        # Simple Euler step on potential landscape defined by fitness
        # Attractor dynamics: high fitness -> stable fixed point
        gradient = -fitness 
        return x - dt * gradient

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_feats = self._structural_parse(prompt)
        results = []
        
        # Pre-compute prompt compression for NCD
        prompt_comp = zlib.compress(prompt.encode('utf-8'))
        len_prompt_comp = len(prompt_comp)
        
        states = [0.5 for _ in candidates] # Initial state x_i(0)
        
        # Iterative refinement (simulating dynamical system convergence)
        # In a real ODE solver this would be continuous; here we do 3 discrete steps
        for step in range(3):
            new_states = []
            for i, cand in enumerate(candidates):
                cand_feats = self._structural_parse(cand)
                
                # 1. Information Theoretic Fitness (Negative KL approx)
                kl_div = self._compute_structural_mismatch(prompt_feats, cand_feats)
                data_fitness = -kl_div 
                
                # 2. Memory Mutual Information
                # Check similarity to stored "successful" patterns (simulated by structural richness)
                mem_bonus = 0.0
                if self.memory_clones:
                    # Simple proxy: does it share structural density with memory?
                    avg_mem_len = sum(c['len'] for c in self.memory_clones) / len(self.memory_clones)
                    if abs(len(cand) - avg_mem_len) < 20: # Rough heuristic
                        mem_bonus = 0.5
                else:
                    # Cold start: bonus for structural completeness (length > short noise)
                    if len(cand) > 5: 
                        mem_bonus = 0.2

                total_fitness = data_fitness + (self.lambda_mem * mem_bonus)
                
                # 3. Dynamical Update
                # Add small deterministic pseudo-noise based on index to break symmetry
                noise = self.noise_scale * ((i % 3) - 1) 
                x_new = self._dynamical_step(states[i], total_fitness) + noise
                
                # Clamp state [0, 1]
                x_new = max(0.0, min(1.0, x_new))
                new_states.append(x_new)
            
            states = new_states

        # Final Scoring and Ranking
        scored_candidates = []
        for i, cand in enumerate(candidates):
            final_state = states[i]
            
            # NCD Tie-breaker
            cand_comp = zlib.compress(cand.encode('utf-8'))
            # Normalized distance to prompt (lower is usually better for relevance, 
            # but distinct answers need some distance. We use it to break ties in state.)
            ncd_val = self._compute_ncd(prompt, cand)
            
            # Combine state (primary) and NCD (tiebreaker/regularizer)
            # We invert NCD logic slightly: very high NCD might mean irrelevant, very low might mean echo.
            # Optimal is moderate. But per instructions: NCD is tiebreaker.
            score = final_state - (ncd_val * 0.001) 
            
            # Update memory if this looks like a good hypothesis (high state)
            if final_state > 0.4:
                self.memory_clones.append({'len': len(cand), 'feats': cand_feats})
                if len(self.memory_clones) > 10: # Keep memory bounded
                    self.memory_clones.pop(0)

            reasoning = f"State convergence: {final_state:.3f}, Structural mismatch penalty applied, Memory bonus: {mem_bonus:.2f}"
            scored_candidates.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning
            })
        
        # Sort descending by score
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the dynamical state of the specific answer 
        relative to the prompt constraints.
        """
        # Reuse evaluation logic for a single candidate
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        # Normalize the score from evaluate (which can be slightly <0 or >1 due to noise/ncd)
        raw_score = res[0]['score']
        confidence = max(0.0, min(1.0, raw_score))
        return confidence