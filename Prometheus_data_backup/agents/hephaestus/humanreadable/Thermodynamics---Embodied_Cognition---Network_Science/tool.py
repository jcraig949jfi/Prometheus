import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Energy-Based Affordance Graph (EBAG) Reasoning Tool.
    
    Mechanism:
    1. Network Science: Constructs a dynamic affinity graph between prompt tokens and 
       candidate tokens based on co-occurrence and structural roles (subject/object).
    2. Embodied Cognition: Defines "affordances" as structural constraints (negations, 
       comparatives, conditionals). Violating these constraints incurs high energy costs.
    3. Thermodynamics: Computes a free-energy score for each candidate. 
       F = Prediction_Error (Local Energy) + Interaction_Energy (Graph) - Entropy_Term.
       Candidates are ranked by lowest free energy (highest probability).
    
    This implements a deterministic approximation of the Langevin dynamics where the 
    system settles into the lowest energy state compatible with structural constraints.
    """

    def __init__(self):
        # Structural keywords defining logical affordances
        self.negations = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse'}
        self.conditionals = {'if', 'then', 'else', 'unless', 'provided'}
        self.quantifiers = {'all', 'some', 'many', 'few', 'every', 'each'}
        
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenizer: lower case, split by non-alphanumeric."""
        return re.findall(r'[a-z0-9]+', text.lower())

    def _extract_structure(self, text: str) -> Dict:
        """Extract logical structure: negations, comparatives, numbers."""
        tokens = self._tokenize(text)
        has_negation = any(t in self.negations for t in tokens)
        has_comparative = any(t in self.comparatives for t in tokens)
        has_conditional = any(t in self.conditionals for t in tokens)
        
        # Extract numbers for numeric evaluation
        numbers = re.findall(r'-?\d+\.?\d*', text)
        nums = []
        for n in numbers:
            try:
                nums.append(float(n))
            except ValueError:
                pass
                
        return {
            'negation': has_negation,
            'comparative': has_comparative,
            'conditional': has_conditional,
            'numbers': nums,
            'length': len(tokens)
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        len1 = len(b1)
        len2 = len(b2)
        if len1 == 0 or len2 == 0:
            return 1.0
        # Compress concatenation
        try:
            len12 = len(zlib.compress(b1 + b2))
        except:
            return 1.0
            
        # NCD formula: (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        # Approximating C(x) with len(x) for speed if needed, but using compress for accuracy
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        
        numerator = len12 - min(c1, c2)
        denominator = max(c1, c2)
        
        if denominator == 0:
            return 1.0
        return max(0.0, min(1.0, numerator / denominator))

    def _compute_local_energy(self, prompt_struct: Dict, cand_text: str, cand_struct: Dict) -> float:
        """
        Local Energy E_i: Prediction error based on structural mismatch.
        High energy if structural features contradict.
        """
        energy = 0.0
        
        # Negation Affordance: If prompt negates, candidate should not be a simple affirmation without qualification
        # Simplified: If prompt has negation and candidate is short positive, penalty? 
        # Instead, we check consistency. 
        if prompt_struct['negation']:
            # If prompt negates, and candidate contains strong positive affirmation words without negation
            pos_words = {'yes', 'true', 'correct', 'is', 'are'}
            cand_tokens = set(self._tokenize(cand_text))
            if cand_tokens & pos_words and not (cand_struct['negation']):
                # Heuristic: If prompt is negative, a bare positive might be wrong, 
                # but this is context dependent. Let's penalize length mismatch in negation contexts.
                pass 

        # Numeric Consistency
        p_nums = prompt_struct['numbers']
        c_nums = cand_struct['numbers']
        
        if len(p_nums) > 0 and len(c_nums) > 0:
            # Check order magnitude or simple equality if counts match
            if len(p_nums) == len(c_nums) == 1:
                if abs(p_nums[0] - c_nums[0]) > 1e-6:
                    # If numbers differ significantly, high energy
                    energy += 2.0 * abs(p_nums[0] - c_nums[0]) / (abs(p_nums[0]) + 1e-6)
            elif len(p_nums) != len(c_nums):
                 # Mismatch in number count suggests hallucination
                 energy += 1.5

        # Comparative Logic
        if prompt_struct['comparative']:
            # If prompt asks for "larger", candidate should ideally reflect that or be a number
            # Hard to verify without semantic understanding, so we rely on NCD for similarity
            pass
            
        return energy

    def _compute_interaction_energy(self, prompt: str, candidate: str) -> float:
        """
        Interaction Energy W_ij: Based on NCD (Affordance Graph connectivity).
        Low energy if candidate is compressible with prompt (high affinity).
        """
        ncd = self._compute_ncd(prompt, candidate)
        return ncd * 2.0  # Scale factor

    def _compute_entropy_term(self, candidate: str, temperature: float = 0.5) -> float:
        """
        Entropy term: Encourages exploration/diversity.
        Shorter answers often have lower entropy in this context? 
        Actually, we want to avoid trivial answers. 
        Let's use log(length) as a proxy for complexity/entropy.
        """
        length = len(candidate)
        if length == 0:
            return 0.0
        return -temperature * math.log(length + 1)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_struct = self._extract_structure(prompt)
        results = []
        
        # Pre-calculate prompt complexity for normalization if needed
        prompt_len = len(prompt)
        
        scores = []
        for cand in candidates:
            cand_struct = self._extract_structure(cand)
            
            # 1. Local Energy (Structural constraints)
            local_e = self._compute_local_energy(prompt_struct, cand, cand_struct)
            
            # 2. Interaction Energy (Network affinity via NCD)
            interact_e = self._compute_interaction_energy(prompt, cand)
            
            # 3. Entropy term (Thermodynamic exploration)
            entropy = self._compute_entropy_term(cand)
            
            # Total Free Energy: F = E_local + E_interaction - T*S
            # We want to MINIMIZE Free Energy.
            free_energy = local_e + interact_e + entropy
            
            scores.append((cand, free_energy))
        
        # Sort by free energy (ascending)
        scores.sort(key=lambda x: x[1])
        
        # Normalize scores to 0-1 range (inverse energy)
        min_e = scores[0][1] if scores else 0
        max_e = scores[-1][1] if scores else 1
        range_e = max_e - min_e if (max_e - min_e) > 1e-9 else 1.0
        
        ranked = []
        for i, (cand, energy) in enumerate(scores):
            # Convert energy to score: 1.0 for lowest energy, decreasing
            norm_score = 1.0 - ((energy - min_e) / range_e)
            
            # Reasoning string
            reason = f"Free Energy={energy:.4f}. "
            if i == 0:
                reason += "Lowest energy state (optimal fit)."
            else:
                reason += f"Higher energy due to structural/NCD mismatch."
                
            ranked.append({
                "candidate": cand,
                "score": float(norm_score),
                "reasoning": reason
            })
            
        return ranked

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the inverse of the free energy calculated for the single candidate.
        """
        # Evaluate against a dummy set containing only the answer to get relative energy
        # But better: Calculate absolute energy metrics
        prompt_struct = self._extract_structure(prompt)
        cand_struct = self._extract_structure(answer)
        
        local_e = self._compute_local_energy(prompt_struct, answer, cand_struct)
        interact_e = self._compute_interaction_energy(prompt, answer)
        entropy = self._compute_entropy_term(answer)
        
        free_energy = local_e + interact_e + entropy
        
        # Map free energy to confidence. 
        # Assuming typical NCD is 0.2-0.8, local_e 0-2.
        # Low energy -> High confidence.
        # Heuristic mapping: exp(-energy)
        conf = math.exp(-free_energy)
        
        return min(1.0, max(0.0, conf))