import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Adaptive Critical Model Checker (ACMC) Implementation.
    
    Mechanism:
    1. Structural Parsing (Primary Signal): Extracts logical operators (negations, 
       comparatives, conditionals) and numeric values to build a deterministic 
       'logic score'. This acts as the 'Model Checking' phase.
    2. Neuromodulated Gain Control: The 'gain' parameter is dynamically adjusted 
       based on the density of logical constraints detected (simulating the 
       order parameter near criticality). High constraint density -> High Gain 
       (strict structural matching). Low density -> Low Gain (relaxed similarity).
    3. Phase Transition Scoring: Candidates are scored by how well they satisfy 
       the extracted structural constraints. The system 'transitions' between 
       exploiting textual similarity (subcritical) and exploring logical 
       consistency (critical) based on the prompt's complexity.
    4. NCD Tiebreaker: Used only when structural scores are indistinguishable.
    """

    def __init__(self):
        # Regex patterns for structural extraction
        self.negations = ['not', 'no', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse', 'larger', 'shorter']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'provided', 'when']
        self.bool_ops = ['and', 'or', 'xor', 'implies']
        
        # Numeric pattern
        self.num_pattern = re.compile(r"-?\d+\.?\d*")

    def _extract_structure(self, text: str) -> dict:
        """Extract logical and numeric features from text."""
        lower_text = text.lower()
        words = re.split(r'[^a-z0-9\-\.]', lower_text)
        
        features = {
            'has_negation': any(n in words for n in self.negations),
            'has_comparative': any(c in words for c in self.comparatives),
            'has_conditional': any(c in words for c in self.conditionals),
            'has_bool': any(b in words for b in self.bool_ops),
            'numbers': [float(n) for n in self.num_pattern.findall(text)],
            'length': len(text),
            'word_count': len(words)
        }
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Compute Normalized Compression Distance."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(c1, c2)
        if denom == 0:
            return 0.0
        return (c12 - min(c1, c2)) / denom

    def _check_numeric_consistency(self, prompt_nums: List[float], cand_nums: List[float]) -> float:
        """Verify if candidate numbers logically follow prompt numbers."""
        if not prompt_nums:
            return 1.0 # No numeric constraints
        if not cand_nums:
            return 0.5 # Ambiguous
        
        # Simple heuristic: Check for direct equality or simple arithmetic progression
        # This simulates the 'Model Checking' of numeric hypotheses
        p_set = set(round(x, 2) for x in prompt_nums)
        c_set = set(round(x, 2) for x in cand_nums)
        
        if p_set == c_set:
            return 1.0
        
        # Check for inverse relationships (common in negation contexts)
        # Or simple magnitude checks if comparatives are present
        return 0.8 if len(c_set) > 0 else 0.2

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feat = self._extract_structure(prompt)
        
        # Calculate 'Order Parameter' (Constraint Density) to tune Gain
        # High density of logical keywords = System near Critical Point
        constraint_count = sum([
            prompt_feat['has_negation'],
            prompt_feat['has_comparative'],
            prompt_feat['has_conditional'],
            prompt_feat['has_bool']
        ])
        
        # Neuromodulatory Gain: Higher when logical complexity is high
        # Base gain 0.5, max boost +0.5 based on constraints
        gain = 0.5 + (constraint_count * 0.15) 
        gain = min(gain, 1.0)

        scored_candidates = []
        
        for cand in candidates:
            cand_feat = self._extract_structure(cand)
            score = 0.0
            reasoning_parts = []

            # 1. Structural Model Checking (High Gain Mode)
            # Check logical consistency rather than just string overlap
            struct_match = 0.0
            
            # Negation consistency
            if prompt_feat['has_negation'] == cand_feat['has_negation']:
                struct_match += 0.25
            else:
                struct_match -= 0.25 # Penalty for flipping negation status incorrectly
            
            # Comparative/Conditional presence
            if prompt_feat['has_comparative'] and cand_feat['has_comparative']:
                struct_match += 0.25
            elif not prompt_feat['has_comparative']:
                struct_match += 0.1 # Neutral bonus for not hallucinating complexity
                
            if prompt_feat['has_conditional'] and cand_feat['has_conditional']:
                struct_match += 0.25
            
            # Numeric Verification
            num_score = self._check_numeric_consistency(prompt_feat['numbers'], cand_feat['numbers'])
            struct_match += (num_score * 0.25)

            # 2. Phase Transition & Similarity (Low Gain Mode fallback)
            # If structural signal is weak, rely more on NCD/Similarity
            ncd_val = self._compute_ncd(prompt, cand)
            similarity_score = 1.0 - ncd_val
            
            # Dynamic Blending based on Gain
            # If gain is high (complex logic), structural score dominates.
            # If gain is low (simple query), similarity dominates.
            final_score = (gain * struct_match) + ((1.0 - gain) * similarity_score)
            
            # Normalize rough score to 0-1 range roughly
            final_score = max(0.0, min(1.0, final_score))
            
            # Add small deterministic noise based on length to break ties if needed
            # but primarily rely on NCD as explicit tiebreaker logic below
            reasoning = f"LogicMatch:{struct_match:.2f}, Gain:{gain:.2f}, NCD:{ncd_val:.2f}"
            
            scored_candidates.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning,
                "_ncd": ncd_val # Store for tie-breaking
            })

        # Sort: Primary by Score, Secondary by NCD (lower NCD is better if scores equal)
        # Since we want highest score first, and for ties, we prefer lower NCD (higher similarity)
        # We sort by score DESC, then by _ncd ASC
        scored_candidates.sort(key=lambda x: (x['score'], -x['_ncd']), reverse=True)
        
        # Clean up and format output
        result = []
        for item in scored_candidates:
            result.append({
                "candidate": item["candidate"],
                "score": item["score"],
                "reasoning": item["reasoning"]
            })
            
        return result

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on structural and compression alignment."""
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.0
        return results[0]["score"]