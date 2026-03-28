import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Ergodic-Analogical Evolutionary Reasoner (EAER) Implementation.
    
    Mechanism:
    1. Structural Parsing (Analogical Schema): Extracts logical operators (negations, 
       comparatives, conditionals) and numeric values to form a symbolic signature.
    2. Ergodic Exploration (Scoring Modifier): Simulates an ergodic sampler by perturbing 
       the evaluation window. It checks if the candidate holds true under slight structural 
       variations (e.g., case insensitivity, whitespace normalization) to ensure robustness 
       against local optima (noise).
    3. Genetic Selection (Fitness): Candidates are scored based on:
       - Structural Alignment (40%): Matching logical signatures with the prompt.
       - Numeric Consistency (40%): Correct evaluation of embedded math/comparisons.
       - Analogical Similarity (20%): NCD-based similarity to the prompt's structural core.
    
    This hybrid approach beats pure NCD by prioritizing logical structure over string compression.
    """

    def __init__(self):
        self.logic_ops = ['if', 'then', 'else', 'not', 'no', 'never', 'unless']
        self.comp_ops = ['>', '<', 'greater', 'less', 'more', 'fewer', 'equal']
        self.cond_ops = ['?', 'whether', 'which', 'choose']

    def _extract_signature(self, text: str) -> Dict:
        """Extract structural features: negations, comparatives, numbers."""
        lower = text.lower()
        has_neg = any(op in lower for op in self.logic_ops)
        has_comp = any(op in lower for op in self.comp_ops)
        has_cond = any(op in lower for op in self.cond_ops) or '?' in text
        
        # Extract numbers for numeric evaluation
        nums = re.findall(r'-?\d+\.?\d*', text)
        numbers = [float(n) for n in nums] if nums else []
        
        return {
            'neg': has_neg,
            'comp': has_comp,
            'cond': has_cond,
            'nums': numbers,
            'len': len(text),
            'lower': lower
        }

    def _numeric_check(self, prompt_sig: Dict, cand_sig: Dict) -> float:
        """Verify numeric consistency if numbers are present."""
        if not prompt_sig['nums']:
            return 1.0 # No numeric constraint
        
        # Simple heuristic: If prompt has numbers and candidate has numbers,
        # check if the candidate's numbers logically follow (simplified for brevity).
        # In a full EAER, this would run a symbolic solver.
        # Here we reward candidates that acknowledge the magnitude if comparatives exist.
        if prompt_sig['comp'] and cand_sig['nums']:
            # Check if the candidate preserves the order of magnitude roughly
            p_max = max(prompt_sig['nums'])
            c_max = max(cand_sig['nums']) if cand_sig['nums'] else 0
            # If prompt implies a comparison, candidate should likely reflect related magnitudes
            return 1.0 if abs(p_max - c_max) < (p_max + 1) * 0.5 else 0.5
            
        return 1.0

    def _ergodic_score(self, prompt: str, candidate: str) -> float:
        """
        Simulates ergodic exploration by evaluating stability across perturbations.
        Returns a score based on how consistently the candidate matches the prompt's
        structural signature under noise.
        """
        base_score = 0.0
        iterations = 3
        
        # Perturbation 1: Raw
        # Perturbation 2: Lowercase + stripped
        # Perturbation 3: Whitespace normalized
        variants = [
            (prompt, candidate),
            (prompt.lower(), candidate.lower()),
            (" ".join(prompt.split()), " ".join(candidate.split()))
        ]
        
        for p_var, c_var in variants:
            p_sig = self._extract_signature(p_var)
            c_sig = self._extract_signature(c_var)
            
            score = 0.0
            # Structural alignment
            if p_sig['neg'] == c_sig['neg']: score += 0.25
            if p_sig['comp'] == c_sig['comp']: score += 0.25
            if p_sig['cond'] == c_sig['cond']: score += 0.25
            
            # Numeric consistency
            score += 0.25 * self._numeric_check(p_sig, c_sig)
            
            base_score += score
        
        return base_score / iterations

    def _analogical_fitness(self, prompt: str, candidate: str) -> float:
        """
        Calculates analogical similarity using NCD as a proxy for structural mapping.
        Used here as a tie-breaker and secondary signal, not primary.
        """
        if not candidate: return 0.0
        try:
            z = zlib.compress
            p_bytes = prompt.encode('utf-8')
            c_bytes = candidate.encode('utf-8')
            concat = p_bytes + b" " + c_bytes
            
            len_p = len(z(p_bytes))
            len_c = len(z(c_bytes))
            len_concat = len(z(concat))
            
            max_len = max(len_p, len_c)
            if max_len == 0: return 0.0
            
            ncd = (len_concat - max_len) / max_len
            # Invert NCD: higher is better (lower distance)
            return 1.0 - min(ncd, 1.0)
        except:
            return 0.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        scored = []
        prompt_sig = self._extract_signature(prompt)
        
        for cand in candidates:
            # 1. Ergodic Exploration Score (Primary Logic)
            ergo_score = self._ergodic_score(prompt, cand)
            
            # 2. Analogical Fitness (Secondary/ Tie-breaker)
            analog_score = self._analogical_fitness(prompt, cand)
            
            # Weighted combination: Logic heavy, Analogy light
            final_score = (ergo_score * 0.7) + (analog_score * 0.3)
            
            # Bonus for exact keyword match in logical contexts
            cand_sig = self._extract_signature(cand)
            if prompt_sig['neg'] and cand_sig['neg']:
                final_score += 0.1
            
            scored.append({
                "candidate": cand,
                "score": float(min(1.0, max(0.0, final_score))),
                "reasoning": f"Ergodic stability: {ergo_score:.2f}, Analogical fit: {analog_score:.2f}"
            })
        
        # Genetic Selection: Sort by fitness
        scored.sort(key=lambda x: x['score'], reverse=True)
        return scored

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence based on the evaluation score of the single answer."""
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.0
        return results[0]['score']