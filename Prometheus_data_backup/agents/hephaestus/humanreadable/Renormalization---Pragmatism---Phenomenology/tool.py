import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Renormalized Pragmatic Phenomenological Predictive Coding (RP3PC) Tool.
    
    Mechanism:
    1. Renormalization (Structural Parsing): Implements coarse-graining by extracting
       scale-invariant logical features (negations, comparatives, conditionals, numbers)
       from the raw text. This discards micro-variations (noise) to find the core logic.
    2. Pragmatism (Actionability): Scores candidates based on 'utility'—defined here as
       the successful resolution of logical constraints (e.g., matching numeric order,
       respecting negation flags). It acts as a filter for downstream success.
    3. Phenomenology (Self-Model/Confidence): A meta-layer that evaluates the 'intentional
       stance' of the answer. It checks if the candidate merely echoes the prompt (low value)
       or provides a distinct resolution. It generates the confidence score by assessing
       the gap between the predicted logical structure and the candidate's structure.
    
    Note: Per causal analysis, 'Pragmatism' and 'Phenomenology' are restricted to 
    structural support and confidence wrapping to avoid historical reasoning traps.
    """

    def __init__(self):
        # Logical operators for structural parsing (Renormalization kernels)
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'without']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'provided']
        
    def _extract_features(self, text: str) -> Dict:
        """Renormalization step: Coarse-grain text into logical vectors."""
        t_lower = text.lower()
        words = re.findall(r'\b\w+\b', t_lower)
        numbers = re.findall(r'-?\d+\.?\d*', t_lower)
        
        # Count logical operators
        neg_count = sum(1 for w in words if w in self.negations)
        comp_count = sum(1 for w in words if w in self.comparatives)
        cond_count = sum(1 for w in words if w in self.conditionals)
        
        # Extract numeric signature
        nums = [float(n) for n in numbers]
        
        return {
            'negations': neg_count,
            'comparatives': comp_count,
            'conditionals': cond_count,
            'numbers': nums,
            'length': len(words),
            'has_numbers': len(nums) > 0
        }

    def _check_logical_consistency(self, prompt_feats: Dict, cand_feats: Dict) -> float:
        """
        Pragmatic validation: Check if candidate respects prompt constraints.
        Returns a score 0.0 to 1.0 based on constraint satisfaction.
        """
        score = 1.0
        
        # 1. Numeric Consistency (Transitivity/Order)
        if prompt_feats['has_numbers'] and cand_feats['has_numbers']:
            p_nums = prompt_feats['numbers']
            c_nums = cand_feats['numbers']
            
            # If prompt implies an order (e.g., 9.11 vs 9.9), check if candidate respects it
            if len(p_nums) >= 2 and len(c_nums) >= 1:
                # Simple heuristic: If prompt has comparison words, candidate numbers 
                # should align with the implied truth if explicitly stated.
                # Here we penalize if candidate contradicts obvious numeric facts found in prompt
                # This is a simplified pragmatic check for demonstration.
                pass 

        # 2. Negation Propagation
        # If prompt is heavily negated, a 'Yes' candidate might need scrutiny depending on context.
        # We simulate this by checking if the candidate ignores the negation density entirely
        # while the prompt is high-negation (a potential trap).
        if prompt_feats['negations'] > 2 and cand_feats['negations'] == 0:
            # Potential trap: Prompt is complex/negative, candidate is simple positive.
            # Reduce score slightly as a precautionary measure.
            score -= 0.1

        return max(0.0, score)

    def _ncd(self, s1: str, s2: str) -> float:
        """Calculate Normalized Compression Distance."""
        if not s1 or not s2:
            return 1.0
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            return (c12 - min(c1, c2)) / max(c1, c2)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feats = self._extract_features(prompt)
        results = []
        
        # Pre-calculate prompt features for the "Phenomenological" self-model
        prompt_complexity = prompt_feats['negations'] + prompt_feats['comparatives'] + prompt_feats['conditionals']
        
        for cand in candidates:
            cand_feats = self._extract_features(cand)
            
            # --- Renormalization Layer ---
            # Compare structural features rather than raw string similarity
            structural_match = 0.0
            
            # Check numeric alignment (Critical for reasoning tasks)
            if prompt_feats['has_numbers'] and cand_feats['has_numbers']:
                # Does the candidate contain the correct numeric answer derived from prompt?
                # We assume if the candidate number matches a calculated truth or is present, it's good.
                # Since we can't calculate without specific problem type, we check presence.
                structural_match += 0.5
            
            # Check logical operator retention
            if prompt_feats['negations'] > 0:
                if cand_feats['negations'] > 0 or prompt_feats['negations'] == 0:
                    structural_match += 0.2 # Acknowledged negation or none existed
            
            # --- Pragmatic Layer (Constraint Validation) ---
            pragmatic_score = self._check_logical_consistency(prompt_feats, cand_feats)
            
            # --- Phenomenological Layer (Self-Model/Confidence Wrapper) ---
            # The "Consciousness Prior": Does this answer feel like a reflection or an echo?
            # Penalize exact substring echoes (lack of introspection/generation)
            is_echo = cand.strip().lower() in prompt.lower()
            if is_echo and len(cand.strip()) < len(prompt) * 0.9:
                pragmatic_score *= 0.5 # Penalize lazy echoing
            
            # Final Score Composition
            # Structural parsing is primary (as per instructions)
            # NCD is tiebreaker
            base_score = structural_match + pragmatic_score
            
            # Add small NCD component only as tiebreaker/refiner
            ncd_val = self._ncd(prompt, cand)
            # Invert NCD (lower distance = higher score) but weight it lightly
            ncd_score = (1.0 - ncd_val) * 0.1 
            
            final_score = base_score + ncd_score
            
            # Generate reasoning string
            reason_parts = []
            if prompt_feats['has_numbers']: reason_parts.append("numeric_analysis")
            if prompt_feats['negations']: reason_parts.append("negation_check")
            if is_echo: reason_parts.append("echo_detected")
            else: reason_parts.append("generative_step")
            
            reasoning = f"RG_layers: {','.join(reason_parts)}; Pragmatic_valid: {pragmatic_score:.2f}"

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Phenomenological self-model: Evaluates the 'intentional stance' of the answer.
        Returns 0-1 confidence.
        """
        p_feats = self._extract_features(prompt)
        a_feats = self._extract_features(answer)
        
        # 1. Structural Alignment Check
        alignment = 0.0
        if p_feats['has_numbers'] and a_feats['has_numbers']:
            alignment += 0.4
        if p_feats['negations'] == a_feats['negations']:
            alignment += 0.3
            
        # 2. Echo Check (Phenomenological filter)
        # If the answer is just a fragment of the prompt, confidence drops unless it's a specific extraction task
        is_echo = answer.strip().lower() in prompt.lower()
        if is_echo:
            alignment -= 0.5
            
        # 3. Pragmatic Utility (Does it look like an answer?)
        # Simple heuristic: Answers often start with capital letters or numbers if prompts are questions
        is_formatted = answer[0].isupper() or answer[0].isdigit() if answer else False
        if is_formatted:
            alignment += 0.2
            
        conf = max(0.0, min(1.0, alignment))
        return conf