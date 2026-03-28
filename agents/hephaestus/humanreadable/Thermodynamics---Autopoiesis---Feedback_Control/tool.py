import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Thermodynamic Autopoietic Feedback Network (TAFN) Approximation.
    
    Mechanism:
    1. Thermodynamics (Entropy): Measures structural disorder in candidate logic.
       Low entropy (high order) in logical structures (negations, comparatives) yields lower 'E'.
    2. Autopoiesis (Self-Production): The candidate must reconstruct the prompt's core constraints.
       We parse the prompt into a 'structural manifold' (set of logical atoms). 
       Candidates are scored on how well they preserve these atoms (reconstruction loss).
    3. Feedback Control (PID): A simulated learning rate modulates the score based on the 
       deviation between the candidate's logical density and the prompt's logical density.
       
    This implements a physics-inspired scoring function where valid reasoning minimizes 
    free energy (error + entropy) while maintaining structural integrity (autopoiesis).
    """

    def __init__(self):
        # PID Controller Parameters (Simulated)
        self.Kp = 1.0  # Proportional gain
        self.Ki = 0.1  # Integral gain
        self.Kd = 0.05 # Derivative gain
        self._integral = 0.0
        self._prev_error = 0.0
        
        # Structural patterns for parsing
        self.negations = ['not', 'no', 'never', 'neither', 'nobody', 'nothing', 'cannot', "n't"]
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'higher', 'lower', 'before', 'after']
        self.conditionals = ['if', 'then', 'else', 'unless', 'provided', 'when']

    def _parse_structure(self, text: str) -> Dict[str, float]:
        """Extract structural features: negations, comparatives, conditionals, numbers."""
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        neg_count = sum(1 for w in words if any(n in w for n in self.negations))
        comp_count = sum(1 for w in words if any(c in w for c in self.comparatives))
        cond_count = sum(1 for w in words if any(c in w for c in self.conditionals))
        
        # Extract numbers for numeric evaluation
        numbers = re.findall(r'-?\d+\.?\d*', text_lower)
        num_count = len(numbers)
        num_sum = sum(float(n) for n in numbers) if numbers else 0.0
        
        # Length normalization
        length = len(words) if len(words) > 0 else 1.0
        
        return {
            'neg_density': neg_count / length,
            'comp_density': comp_count / length,
            'cond_density': cond_count / length,
            'num_count': num_count,
            'num_sum': num_sum,
            'length': length
        }

    def _calculate_entropy_production(self, prompt_struct: Dict, cand_struct: Dict) -> float:
        """
        Calculate entropy production (Housekeeping heat equivalent).
        High deviation in structural density implies high entropy production (disorder).
        """
        # Difference in logical densities
        delta_neg = abs(prompt_struct['neg_density'] - cand_struct['neg_density'])
        delta_comp = abs(prompt_struct['comp_density'] - cand_struct['comp_density'])
        delta_cond = abs(prompt_struct['cond_density'] - cand_struct['cond_density'])
        
        # Entropy term: Higher deviation = Higher entropy production
        # We want to minimize this, so it adds to Free Energy (bad)
        entropy_prod = (delta_neg * 2.0) + (delta_comp * 1.5) + (delta_cond * 1.5)
        return entropy_prod

    def _calculate_autopoietic_loss(self, prompt_struct: Dict, cand_struct: Dict) -> float:
        """
        Autopoietic closure loss.
        Penalizes deviation from the self-produced organizational manifold.
        The 'manifold' is defined by the prompt's structural signature.
        """
        # Reconstruction error: Can the candidate reproduce the prompt's logical complexity?
        # If prompt has numbers, candidate should likely engage with them or match magnitude logic
        num_err = 0.0
        if prompt_struct['num_count'] > 0:
            # Normalize number difference
            if cand_struct['num_count'] > 0:
                num_err = abs(prompt_struct['num_sum'] - cand_struct['num_sum']) / (abs(prompt_struct['num_sum']) + 1e-6)
            else:
                num_err = 1.0 # Total failure to reproduce numeric manifold
        
        # Length coherence (organizational integrity)
        len_ratio = min(cand_struct['length'], prompt_struct['length']) / (max(cand_struct['length'], prompt_struct['length']) + 1e-6)
        integrity_loss = 1.0 - len_ratio
        
        return (num_err * 0.5) + (integrity_loss * 0.5)

    def _pid_modulate(self, error: float) -> float:
        """Simulated PID controller to adjust scoring sensitivity."""
        self._integral += error
        derivative = error - self._prev_error
        self._prev_error = error
        
        # Output modulation factor (learning rate analog)
        modulation = self.Kp * error + self.Ki * self._integral + self.Kd * derivative
        return modulation

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_struct = self._parse_structure(prompt)
        results = []
        
        # Reset PID state for this evaluation batch
        self._integral = 0.0
        self._prev_error = 0.0

        # Pre-calculate prompt complexity for baseline
        prompt_complexity = prompt_struct['neg_density'] + prompt_struct['comp_density'] + prompt_struct['cond_density']

        for cand in candidates:
            cand_struct = self._parse_structure(cand)
            
            # 1. Thermodynamic Term (Entropy Production)
            entropy_term = self._calculate_entropy_production(prompt_struct, cand_struct)
            
            # 2. Autopoietic Term (Reconstruction Loss)
            auto_loss = self._calculate_autopoietic_loss(prompt_struct, cand_struct)
            
            # Combined Free Energy (F = E - TS + lambda*Loss)
            # We minimize F. Lower F = Better candidate.
            # Here we invert logic: Score = -F
            free_energy = entropy_term + (0.5 * auto_loss)
            
            # 3. Feedback Control (PID Modulation)
            # Error is the difference in complexity handling
            current_error = abs(prompt_complexity - (cand_struct['neg_density'] + cand_struct['comp_density']))
            modulation = self._pid_modulate(current_error)
            
            # Base score from NCD (as tiebreaker/secondary signal per instructions)
            ncd = self._ncd_distance(prompt, cand)
            
            # Final Score Construction
            # High score = Good. 
            # We want low free_energy. 
            # We want low NCD (similarity in content) but primarily structural match.
            # Structural match is captured in free_energy (low is good).
            
            raw_score = (1.0 / (1.0 + free_energy)) - (modulation * 0.1)
            
            # NCD as tiebreaker modifier (small weight)
            # If structural scores are close, NCD breaks ties.
            # But per instructions: NCD is tiebreaker. 
            # We use it here as a small bonus for semantic closeness if structure is valid.
            ncd_bonus = (1.0 - ncd) * 0.05 
            
            final_score = raw_score + ncd_bonus
            
            # Reasoning string generation
            reasoning = (
                f"Thermo: EntropyProd={entropy_term:.3f}; "
                f"Auto: ClosureLoss={auto_loss:.3f}; "
                f"Control: PID_Mod={modulation:.3f}; "
                f"NCD_Tiebreak={ncd:.3f}"
            )
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on Free Energy minimization.
        Low free energy -> High confidence.
        """
        struct_p = self._parse_structure(prompt)
        struct_a = self._parse_structure(answer)
        
        entropy = self._calculate_entropy_production(struct_p, struct_a)
        auto_loss = self._calculate_autopoietic_loss(struct_p, struct_a)
        
        free_energy = entropy + (0.5 * auto_loss)
        
        # Convert free energy to confidence (0 to 1)
        # If FE is 0, confidence is 1. As FE grows, confidence drops.
        confidence = 1.0 / (1.0 + free_energy)
        
        return max(0.0, min(1.0, confidence))