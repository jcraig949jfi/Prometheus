import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Prime-Embodied Spectral Reasoner (PESR) Implementation Strategy:
    
    Given the causal warning that 'Prime Number Theory' is a historical inhibitor for direct scoring,
    this implementation adopts a hybrid strategy:
    
    1. Structural Parsing (Primary Signal): Extracts logical constraints (negations, comparatives,
       conditionals) and numeric values. This handles the "Reasoning" and "Constraint Propagation"
       requirements robustly.
    2. Embodied Spectral Simulation (Metacognitive Signal): 
       - We simulate an "agent" traversing the candidate string as a 1D number line.
       - Step sizes are derived from character codes (embodied trajectory).
       - A simplified spectral analysis (Fourier-like energy distribution) is computed on the 
         step-differentiated signal.
       - This acts as a "fingerprint" to detect structural randomness vs. patterned logic, 
         serving as the tie-breaker and confidence modifier.
    3. Prime Theory (Confidence Wrapper): Used ONLY to modulate confidence scores based on 
       string length properties (prime lengths get a slight penalty boost if they look like noise),
       adhering to the constraint to restrict prime theory to the confidence wrapper.
    4. NCD: Used strictly as a final tie-breaker.
    """

    def __init__(self):
        self._stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being'}

    def _is_prime(self, n: int) -> bool:
        if n < 2: return False
        if n == 2: return True
        if n % 2 == 0: return False
        for i in range(3, int(n**0.5) + 1, 2):
            if n % i == 0: return False
        return True

    def _structural_parse(self, text: str) -> Dict:
        """Extract logical structures: negations, comparatives, numbers."""
        text_lower = text.lower()
        features = {
            'negation_count': len(re.findall(r'\b(not|no|never|neither|none|cannot)\b', text_lower)),
            'comparative_count': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', text_lower)),
            'conditional_count': len(re.findall(r'\b(if|then|unless|provided|except)\b', text_lower)),
            'numbers': [],
            'has_logic_ops': bool(re.search(r'\b(and|or|implies|therefore)\b', text_lower))
        }
        # Extract numbers for evaluation
        nums = re.findall(r'-?\d+\.?\d*', text)
        features['numbers'] = [float(n) for n in nums if n]
        return features

    def _embodied_spectral_signature(self, text: str) -> float:
        """
        Simulates an agent walking the text string.
        Returns a 'spectral energy' score based on step variance.
        High variance in steps = high frequency content (noise/randomness).
        Low variance = periodicity (structure).
        """
        if len(text) < 2:
            return 0.0
        
        # Convert to embodied trajectory (ascii values as positions)
        trajectory = [ord(c) for c in text]
        
        # Compute step lengths (velocity)
        steps = [trajectory[i+1] - trajectory[i] for i in range(len(trajectory)-1)]
        
        if not steps:
            return 0.0

        # Simplified Spectral Analysis: 
        # Calculate the ratio of high-frequency energy to total energy.
        # We approximate frequency content by looking at second-order differences (acceleration)
        # compared to first-order (velocity).
        
        # Total energy (L2 norm of steps)
        total_energy = sum(s**2 for s in steps) + 1e-9
        
        # High freq proxy: Energy of differences of steps (acceleration)
        # Rapid changes in step size imply high frequency components
        accelerations = [steps[i+1] - steps[i] for i in range(len(steps)-1)]
        high_freq_energy = sum(a**2 for a in accelerations) + 1e-9
        
        # Spectral Ratio: Higher ratio implies more chaotic/noisy structure
        return high_freq_energy / total_energy

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        concat = s1_bytes + s2_bytes
        
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_concat = len(zlib.compress(concat))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_concat - min(len_s1, len_s2)) / max_len

    def _score_candidate(self, prompt: str, candidate: str) -> Tuple[float, str]:
        prompt_feat = self._structural_parse(prompt)
        cand_feat = self._structural_parse(candidate)
        
        score = 0.0
        reasons = []

        # 1. Logical Consistency Check (Constraint Propagation)
        # If prompt has negation, correct answer often needs to reflect it or oppose a false premise
        if prompt_feat['negation_count'] > 0:
            # Heuristic: If prompt negates, and candidate is short "Yes/No", check context
            # This is a simplified proxy for logical alignment
            if cand_feat['negation_count'] > 0:
                score += 0.2
                reasons.append("Aligned negation structure")
        
        # 2. Numeric Evaluation
        if prompt_feat['numbers'] and cand_feat['numbers']:
            p_nums = prompt_feat['numbers']
            c_nums = cand_feat['numbers']
            
            # Check for direct answer match
            if c_nums[-1] in p_nums:
                score += 0.3
                reasons.append("Numeric match found")
            
            # Check for simple arithmetic consistency (e.g., prompt asks for larger, candidate is larger)
            if prompt_feat['comparative_count'] > 0:
                if 'more' in prompt.lower() or 'greater' in prompt.lower():
                    if c_nums[-1] >= max(p_nums):
                        score += 0.4
                        reasons.append("Numeric comparative satisfied")
                elif 'less' in prompt.lower() or 'smaller' in prompt.lower():
                    if c_nums[-1] <= min(p_nums):
                        score += 0.4
                        reasons.append("Numeric comparative satisfied")

        # 3. Embodied Spectral Analysis (The "PESR" core)
        # We expect valid reasoning to have lower spectral chaos than random gibberish
        spectral_chaos = self._embodied_spectral_signature(candidate)
        
        # Baseline chaos for English text is roughly within a range. 
        # Extreme chaos suggests random characters. Extreme low chaos suggests repetition.
        # We penalize extreme chaos.
        if spectral_chaos > 5.0: # Threshold for "noisy"
            score -= 0.3
            reasons.append(f"High spectral noise ({spectral_chaos:.2f})")
        else:
            score += 0.1
            reasons.append(f"Stable spectral signature ({spectral_chaos:.2f})")

        # 4. Structural Presence
        if cand_feat['has_logic_ops']:
            score += 0.1
            reasons.append("Contains logical operators")
            
        if not reasons:
            reasons.append("Baseline structural assessment")

        return score, "; ".join(reasons)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-calculate prompt features for NCD baseline if needed
        prompt_clean = prompt.lower()
        
        scored_candidates = []
        for cand in candidates:
            base_score, reason_str = self._score_candidate(prompt, cand)
            
            # NCD as tie-breaker / secondary signal
            # If the candidate is very similar to the prompt (echo), it might be wrong in QA tasks
            # But if it's a completion task, similarity is good. 
            # We use NCD to differentiate candidates with same base_score.
            ncd_val = self._compute_ncd(prompt, cand)
            
            # Heuristic: Moderate NCD is often best (relevant but not identical)
            # This is a weak proxy, so we weight it lightly unless scores are tied.
            scored_candidates.append({
                'candidate': cand,
                'base_score': base_score,
                'ncd': ncd_val,
                'reasoning': reason_str
            })
        
        # Sort primarily by base_score (descending), then by NCD (ascending - closer is usually better for relevance)
        # Note: In strict QA, sometimes the answer is short and distinct, so NCD logic is tricky.
        # We prioritize the structural score heavily.
        scored_candidates.sort(key=lambda x: (x['base_score'], -x['ncd']), reverse=True)
        
        # Normalize scores to 0-1 range roughly
        max_score = max(c['base_score'] for c in scored_candidates) if scored_candidates else 0
        min_score = min(c['base_score'] for c in scored_candidates) if scored_candidates else 0
        range_score = max_score - min_score if (max_score - min_score) > 0 else 1
        
        final_results = []
        for item in scored_candidates:
            # Normalize
            norm_score = (item['base_score'] - min_score) / range_score
            # Add small NCD influence to break ties deterministically
            final_score = norm_score * 0.9 + (1.0 - item['ncd']) * 0.1
            
            final_results.append({
                'candidate': item['candidate'],
                'score': final_score,
                'reasoning': item['reasoning']
            })
            
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses Prime Number Theory ONLY as a wrapper/modulator on string length.
        If length is prime, we apply a slight penalty assuming prime-length strings 
        in this context might be arbitrary or less structured (historical inhibitor heuristic).
        """
        if not answer:
            return 0.0
            
        # Base confidence from structural coherence
        score, _ = self._score_candidate(prompt, answer)
        
        # Normalize base score (roughly -1 to 1 -> 0 to 1)
        base_conf = max(0.0, min(1.0, (score + 1.0) / 2.0))
        
        # Prime Length Modulator (The "Causal Inhibitor" constraint)
        # If length is prime, reduce confidence slightly (simulating the 'inhibitor' effect)
        length = len(answer)
        if self._is_prime(length):
            # Prime lengths are historically inhibitors in this specific causal graph
            base_conf *= 0.85
        
        # Spectral sanity check
        spectral_chaos = self._embodied_spectral_signature(answer)
        if spectral_chaos > 8.0:
            base_conf *= 0.5
            
        return max(0.0, min(1.0, base_conf))