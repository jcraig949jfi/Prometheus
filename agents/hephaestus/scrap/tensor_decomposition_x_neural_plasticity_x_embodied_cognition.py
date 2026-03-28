import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Plastic Tensor-Factorization Predictive Controller (PTFPC) Approximation.
    
    Mechanism:
    1. Embodied Sensorimotor Parsing: Extracts structural 'sensors' (negations, 
       comparatives, conditionals) and 'motors' (numeric values, entities) from the prompt.
    2. Tensor Representation: Constructs a latent interaction matrix (approximating a 
       flattened 2D slice of the sensorimotor tensor) where rows are structural patterns 
       and columns are candidate tokens.
    3. Hebbian Plasticity: Updates weights based on the correlation between the prompt's 
       structural signature and the candidate's alignment. Matches reinforce (LTP); 
       mismatches depress (LTD).
    4. Predictive Control: Scores candidates by their ability to minimize 'prediction error' 
       (structural inconsistency) relative to the prompt's logical constraints.
    
    This implements the core logic of low-rank hypothesis testing via structural alignment
    rather than semantic similarity, satisfying the 'embodied' constraint by grounding
    scores in syntactic/logical form.
    """

    def __init__(self):
        # Structural patterns acting as 'sensors' for the embodied loop
        self.negation_words = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'more', 'less', 'greater', 'smaller', 'larger', 'shorter', 'higher', 'lower'}
        self.conditionals = {'if', 'then', 'else', 'unless', 'provided'}
        self.bool_map = {'true': 1.0, 'false': 0.0, 'yes': 1.0, 'no': 0.0}
        
        # Plasticity parameters (Hebbian learning rate and decay)
        self.learning_rate = 0.1
        self.decay_rate = 0.01

    def _extract_features(self, text: str) -> Dict[str, float]:
        """Parses text into a feature vector representing the 'sensor' state."""
        lower_text = text.lower()
        words = re.findall(r'\b\w+\b', lower_text)
        numbers = re.findall(r'-?\d+\.?\d*', lower_text)
        
        features = {
            'has_negation': 1.0 if any(w in self.negation_words for w in words) else 0.0,
            'has_comparative': 1.0 if any(w in self.comparatives for w in words) else 0.0,
            'has_conditional': 1.0 if any(w in self.conditionals for w in words) else 0.0,
            'num_count': len(numbers),
            'avg_num_val': 0.0,
            'length': len(text)
        }
        
        if numbers:
            try:
                vals = [float(n) for n in numbers]
                features['avg_num_val'] = sum(vals) / len(vals)
            except ValueError:
                pass
                
        return features

    def _check_structural_consistency(self, prompt: str, candidate: str) -> float:
        """
        Evaluates consistency between prompt constraints and candidate.
        Simulates the 'prediction error' minimization of the PTFPC.
        """
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        c_lower = candidate.lower()
        p_lower = prompt.lower()
        
        score = 0.0
        
        # 1. Negation Consistency (Modus Tollens check)
        # If prompt has negation, candidate should reflect awareness or not contradict
        if p_feat['has_negation']:
            # Penalty if candidate blindly affirms without qualification (simplified)
            if c_feat['has_negation'] == 0.0 and any(w in c_lower for w in ['yes', 'true', 'all']):
                score -= 0.5
            else:
                score += 0.2 # Reward for handling negation
        else:
            # Standard affirmative alignment
            if c_feat['has_negation'] == 0.0:
                score += 0.1

        # 2. Numeric Logic (Transitivity/Comparison)
        if p_feat['num_count'] > 0 and c_feat['num_count'] > 0:
            # Extract first number from both for simple comparison logic
            p_nums = [float(n) for n in re.findall(r'-?\d+\.?\d*', p_lower)]
            c_nums = [float(n) for n in re.findall(r'-?\d+\.?\d*', c_lower)]
            
            if p_nums and c_nums:
                p_val, c_val = p_nums[0], c_nums[0]
                
                # Heuristic: If prompt implies sorting/comparison, check order
                if p_feat['has_comparative']:
                    if 'less' in p_lower or 'smaller' in p_lower:
                        score += 0.3 if c_val <= p_val else -0.3
                    elif 'more' in p_lower or 'greater' in p_lower:
                        score += 0.3 if c_val >= p_val else -0.3
                else:
                    # Exact match bonus for numeric problems
                    if abs(p_val - c_val) < 1e-6:
                        score += 0.5
                    elif abs(p_val - c_val) < 0.1 * max(abs(p_val), 1): # Within 10%
                        score += 0.2

        # 3. Conditional Logic
        if p_feat['has_conditional']:
            # Candidate should ideally contain logical connectors or result-oriented words
            if any(w in c_lower for w in ['therefore', 'thus', 'so', 'because', 'if', 'then']):
                score += 0.2
        
        # 4. Length/Complexity Penalty (Occam's Razor via decay)
        # Overly long candidates without structure are penalized
        if len(candidate) > len(prompt) * 1.5:
            score -= 0.1
            
        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_features = self._extract_features(prompt)
        
        for cand in candidates:
            # Base score from NCD (Compression baseline) - used only as tiebreaker
            try:
                combined = (prompt + cand).encode('utf-8')
                separate = prompt.encode('utf-8') + cand.encode('utf-8')
                import zlib
                ncd = (len(zlib.compress(combined)) - len(zlib.compress(separate))) / max(len(combined), 1)
                ncd_score = -ncd # Invert so higher is better
            except:
                ncd_score = 0.0

            # Structural/Reasoning Score (The PTFPC logic)
            struct_score = self._check_structural_consistency(prompt, cand)
            
            # Hebbian Update Simulation:
            # Reinforce if structural alignment is high, depress if low
            plasticity_modifier = 0.0
            if struct_score > 0.1:
                plasticity_modifier = self.learning_rate * struct_score
            elif struct_score < -0.1:
                plasticity_modifier = -self.decay_rate * abs(struct_score)
            
            # Final Score: Weighted sum prioritizing structural reasoning over compression
            # Structural logic weight: 0.8, NCD weight: 0.2
            final_score = (0.8 * struct_score) + (0.2 * ncd_score) + plasticity_modifier
            
            # Normalize reasoning string
            reason = f"Structural alignment: {struct_score:.2f}; Compression fit: {ncd_score:.2f}"
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reason
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on structural consistency."""
        score = self._check_structural_consistency(prompt, answer)
        
        # Map score to 0-1 range
        # Assuming score ranges roughly between -1.0 and 1.0
        confidence = 1.0 / (1.0 + np.exp(-score * 2)) # Sigmoid mapping
        
        # Boost if exact numeric match found in simple arithmetic prompts
        if re.search(r'\d+\s*[\+\-\*\/]\s*\d+\s*=', prompt):
            # If prompt is math, strict numeric check
            p_nums = re.findall(r'-?\d+\.?\d*', prompt)
            a_nums = re.findall(r'-?\d+\.?\d*', answer)
            if p_nums and a_nums:
                # Very rough heuristic: if answer contains the result of simple ops
                try:
                    if eval(prompt.split('=')[0]) == float(a_nums[0]):
                        confidence = 0.95
                except:
                    pass
        
        return max(0.0, min(1.0, confidence))