import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a triadic reasoning engine: Evolution x Spectral Analysis x Free Energy.
    
    Mechanism:
    1. FREE ENERGY (Core): Evaluates 'surprise' by measuring structural coherence between
       prompt constraints and candidate answers. Low free energy = high consistency.
       We approximate this via constraint satisfaction (negations, comparatives, logic).
    2. SPECTRAL ANALYSIS (Metacognition): Analyzes the 'frequency' of tokens.
       Penalizes candidates with unnatural spectral signatures (e.g., excessive repetition
       indicating narrowband instability, or chaotic length mismatches).
    3. EVOLUTION (Search): Treats candidates as a population. Fitness is a weighted sum
       of Free Energy (accuracy) and Spectral Regularization (stability).
       
    This structure prioritizes logical consistency (FEP) while using spectral metrics
    to prune unstable or over-fitted (repetitive) hypotheses.
    """

    def __init__(self):
        # Stopwords for spectral smoothing (common low-info tokens)
        self._stopwords = set(['the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'to', 'of'])
        # Logical operators for structural parsing
        self._negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self._comparatives = ['greater', 'less', 'more', 'fewer', 'higher', 'lower', 'larger', 'smaller']
        self._conditionals = ['if', 'then', 'else', 'unless', 'provided']

    def _structural_parse(self, text: str) -> Dict:
        """Extracts logical constraints: negations, comparatives, conditionals, numbers."""
        lower_text = text.lower()
        words = re.findall(r'\b\w+\b', lower_text)
        
        has_negation = any(n in words for n in self._negations)
        has_comparative = any(c in words for c in self._comparatives)
        has_conditional = any(c in words for c in self._conditionals)
        
        # Extract numbers for numeric evaluation
        numbers = re.findall(r'\d+\.?\d*', lower_text)
        nums = [float(n) for n in numbers]
        
        return {
            'negation': has_negation,
            'comparative': has_comparative,
            'conditional': has_conditional,
            'numbers': nums,
            'word_count': len(words)
        }

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Calculates negative variational free energy.
        Low surprise (high score) occurs when candidate structure aligns with prompt constraints.
        """
        p_struct = self._structural_parse(prompt)
        c_struct = self._structural_parse(candidate)
        
        score = 0.0
        
        # Constraint 1: Negation consistency (Modus Tollens approximation)
        # If prompt implies negation, candidate should likely reflect it or not contradict strongly
        if p_struct['negation']:
            # Reward if candidate acknowledges negation or is neutral, penalize if it asserts positively without context
            # Simplified: Just matching the presence helps alignment
            score += 2.0 if c_struct['negation'] else 0.5
        else:
            # If no negation in prompt, penalize unexpected negation in short answers
            if c_struct['negation'] and c_struct['word_count'] < 10:
                score -= 1.0
            else:
                score += 1.0

        # Constraint 2: Comparative logic
        if p_struct['comparative']:
            # Check if candidate has numbers or comparatives
            if c_struct['comparative'] or len(c_struct['numbers']) > 0:
                score += 2.0
            else:
                score += 0.5 # Weak match
        else:
            score += 1.0

        # Constraint 3: Conditional logic
        if p_struct['conditional']:
            score += 1.5 if c_struct['conditional'] else 0.5
        else:
            score += 1.0

        # Numeric consistency (Simple transitivity check)
        # If prompt has numbers and candidate has numbers, check magnitude alignment roughly
        if len(p_struct['numbers']) > 0 and len(c_struct['numbers']) > 0:
            # Heuristic: If prompt asks for max/min, candidate should reflect it. 
            # Here we just reward numeric engagement if prompt has numbers
            score += 1.5
        elif len(p_struct['numbers']) == 0 and len(c_struct['numbers']) == 0:
            score += 1.0
            
        return score

    def _spectral_analysis(self, candidate: str) -> float:
        """
        Computes spectral regularizer.
        Analyzes token frequency distribution.
        Rewards power-law-like decay (natural language), penalizes narrowband (repetition) or flat noise.
        Returns a penalty score (lower is better).
        """
        words = re.findall(r'\b\w+\b', candidate.lower())
        if not words:
            return 0.0
            
        # Frequency count
        freq = {}
        for w in words:
            if w not in self._stopwords: # Ignore stopwords for spectral shape
                freq[w] = freq.get(w, 0) + 1
        
        if not freq:
            return 0.0
            
        counts = sorted(freq.values(), reverse=True)
        total_tokens = sum(counts)
        if total_tokens == 0:
            return 0.0
            
        # Spectral Leakage Check: Repetition Ratio
        # High repetition of single concepts indicates narrowband instability (overfitting)
        max_freq = counts[0]
        repetition_penalty = max_freq / len(words) if len(words) > 0 else 0
        
        # Entropy approximation (Spectral flatness proxy)
        # Natural language has specific entropy; random noise is high, repetition is low
        entropy = 0.0
        for count in counts:
            if count > 0:
                p = count / total_tokens
                entropy -= p * math.log2(p)
        
        # Normalize entropy by max possible entropy
        max_entropy = math.log2(len(counts)) if len(counts) > 1 else 1.0
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
        
        # Ideal spectral profile: Moderate entropy, low repetition
        # Penalty for too much repetition (narrowband) or too little structure (chaotic/flat)
        # We want normalized_entropy to be around 0.6-0.8 (typical for text)
        spectral_deviation = abs(normalized_entropy - 0.7)
        
        # Combined spectral score (lower is better)
        return (repetition_penalty * 2.0) + (spectral_deviation * 0.5)

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denominator = max(c1, c2)
        if denominator == 0:
            return 1.0
        return (c12 - min(c1, c2)) / denominator

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        results = []
        
        # Pre-calculate prompt structural features to avoid re-parsing
        p_struct = self._structural_parse(prompt)
        
        for cand in candidates:
            # 1. Free Energy (Prediction Accuracy)
            fe_score = self._compute_free_energy(prompt, cand)
            
            # 2. Spectral Regularization (Dynamic Stability)
            spec_penalty = self._spectral_analysis(cand)
            
            # 3. Evolutionary Fitness Function
            # Fitness = Accuracy - Instability
            fitness = fe_score - spec_penalty
            
            # Tiebreaker: NCD (only if scores are very close, handled by sorting stability)
            # We store raw components for now.
            results.append({
                "candidate": cand,
                "score": fitness,
                "reasoning": f"FEP:{fe_score:.2f} Spec:{spec_penalty:.2f}",
                "_ncd": self._ncd_distance(prompt, cand)
            })
        
        # Sort by fitness (descending), then by NCD (ascending) as tiebreaker
        # Since we want highest score first, and lowest NCD first:
        results.sort(key=lambda x: (-x['score'], x['_ncd']))
        
        # Clean up internal keys
        for r in results:
            del r['_ncd']
            
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the combined fitness of the answer.
        """
        # Evaluate single candidate against prompt
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        raw_score = res[0]['score']
        
        # Map raw score to 0-1 range using a sigmoid-like function
        # Typical FEP scores might range from -2 to 6 depending on constraints
        # Center around 2.0, spread 2.0
        confidence = 1.0 / (1.0 + math.exp(-(raw_score - 2.0) / 2.0))
        
        # Clamp
        return max(0.0, min(1.0, confidence))