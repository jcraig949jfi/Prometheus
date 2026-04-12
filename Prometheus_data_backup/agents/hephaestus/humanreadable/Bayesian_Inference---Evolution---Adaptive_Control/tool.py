from typing import Dict, Tuple

import re
import math
import zlib
from typing import List, Dict, Tuple
import random

class ReasoningTool:
    """
    Bayesian-Evolutionary Adaptive Scorer (BEAS)
    
    Combines Bayesian inference, evolutionary optimization, and adaptive control
    to score reasoning answers based on structural feature alignment and 
    computational validation.
    
    Parses logical structure (negations, conditionals, numerics) into feature
    vectors, evolves candidate representations, updates posterior beliefs, and
    adaptively tunes mutation rates to maximize evidence alignment.
    """
    
    def __init__(self):
        self.feature_dim = 12  # Number of structural features
        self.pop_size = 20
        self.generations = 15
        self.sigma_sq = 1.0
        self.eta = 0.05
        random.seed(42)  # Deterministic
        
    def _extract_features(self, text: str) -> List[float]:
        """Extract structural features from text."""
        text_lower = text.lower()
        features = [
            len(re.findall(r'\b(not|no|never|none|neither)\b', text_lower)),  # Negations
            len(re.findall(r'\b(more|less|greater|fewer|higher|lower)\b', text_lower)),  # Comparatives
            len(re.findall(r'\b(if|when|unless|whether)\b', text_lower)),  # Conditionals
            len(re.findall(r'\b(because|since|thus|therefore|so|leads to|causes)\b', text_lower)),  # Causals
            len(re.findall(r'\b\d+\.?\d*\b', text)),  # Numeric values
            len(re.findall(r'\b(first|second|before|after|then|next)\b', text_lower)),  # Ordering
            len(re.findall(r'\b(all|every|each|any|some)\b', text_lower)),  # Quantifiers
            len(re.findall(r'\b(and|or|but|yet|however)\b', text_lower)),  # Connectives
            len(re.findall(r'\b(always|sometimes|never|usually)\b', text_lower)),  # Modals
            len(re.findall(r'\b(must|should|could|may|might)\b', text_lower)),  # Modals2
            len(re.findall(r'\?', text)),  # Questions
            len(text.split())  # Length
        ]
        return features
    
    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (max 15% weight)."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
    
    def _compute_numeric_answer(self, prompt: str) -> Tuple[bool, float]:
        """Compute numeric answers for common patterns."""
        # Bat and ball: X + Y = A, X = Y + B
        match = re.search(r'(\d+\.?\d*)\s*dollars?.+costs?\s*(\d+\.?\d*)\s*dollars?\s*more', prompt, re.I)
        if match:
            total_match = re.search(r'cost\s*(\d+\.?\d*)', prompt, re.I)
            if total_match:
                total = float(total_match.group(1))
                diff = float(match.group(2))
                ball = (total - diff) / 2
                return True, ball
        
        # Simple arithmetic in prompt
        match = re.search(r'(\d+\.?\d*)\s*[\+\-\*/]\s*(\d+\.?\d*)', prompt)
        if match:
            try:
                result = eval(re.search(r'[\d\+\-\*/\.\(\)\s]+', prompt).group())
                return True, float(result)
            except:
                pass
        
        return False, 0.0
    
    def _parse_comparison(self, prompt: str, candidates: List[str]) -> Tuple[bool, str]:
        """Parse and compute numeric comparisons."""
        numbers = re.findall(r'\b(\d+\.?\d*)\b', prompt)
        if len(numbers) >= 2 and any(w in prompt.lower() for w in ['greater', 'larger', 'bigger', 'smaller', 'less']):
            nums = [float(n) for n in numbers[:2]]
            
            for cand in candidates:
                cand_lower = cand.lower()
                if 'yes' in cand_lower or 'correct' in cand_lower or 'true' in cand_lower:
                    if ('greater' in prompt.lower() or 'larger' in prompt.lower()) and nums[0] > nums[1]:
                        return True, cand
                    if ('less' in prompt.lower() or 'smaller' in prompt.lower()) and nums[0] < nums[1]:
                        return True, cand
                elif 'no' in cand_lower or 'incorrect' in cand_lower or 'false' in cand_lower:
                    if ('greater' in prompt.lower() or 'larger' in prompt.lower()) and nums[0] <= nums[1]:
                        return True, cand
        
        return False, ""
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check for ambiguity, presupposition, and unanswerability."""
        prompt_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|quit|why did .+ fail|when did .+ stop)\b', prompt_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery .+ a \b', prompt_lower) and 'same' not in prompt_lower:
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'\b(he|she|it|they)\b', prompt_lower) and re.search(r'\bwho\b', prompt_lower):
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither .+ or\b', prompt_lower) and 'only' not in prompt_lower:
            return 0.3
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|prefer)\b', prompt_lower) and not re.search(r'\b(most|least|criteria|measure)\b', prompt_lower):
            return 0.3
        
        # Unanswerable
        if re.search(r'\b(impossible|cannot|no way|insufficient)\b', prompt_lower):
            return 0.2
        
        return 1.0  # No meta-issues detected
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Evaluate candidates using BEAS algorithm."""
        if not candidates:
            return []
        
        # Try computational approaches first
        has_num, num_answer = self._compute_numeric_answer(prompt)
        has_comp, comp_answer = self._parse_comparison(prompt, candidates)
        
        # Extract reference features from prompt
        prompt_features = self._extract_features(prompt)
        
        # Initialize population with candidate features
        population = []
        for cand in candidates:
            features = self._extract_features(cand)
            weight = 1.0 / len(candidates)
            population.append({'text': cand, 'features': features, 'weight': weight})
        
        # Evolutionary-Bayesian optimization
        tau_sq = 0.1
        gain = 1.0
        
        for gen in range(self.generations):
            # Compute likelihood for each individual
            for ind in population:
                f = ind['features']
                dist_sq = sum((f[i] - prompt_features[i]) ** 2 for i in range(self.feature_dim))
                likelihood = math.exp(-dist_sq / (2 * self.sigma_sq))
                ind['weight'] = likelihood
            
            # Normalize weights
            total_w = sum(ind['weight'] for ind in population) + 1e-10
            for ind in population:
                ind['weight'] /= total_w
            
            # Adaptive control: adjust mutation based on entropy
            entropy = -sum(ind['weight'] * math.log(ind['weight'] + 1e-10) for ind in population)
            target_entropy = math.log(len(population))
            error = target_entropy - entropy
            gain = max(0.01, gain + self.eta * error)
            tau_sq = gain ** 2
            
            # Evolution step (simple mutation)
            if gen < self.generations - 1:
                for ind in population:
                    for i in range(self.feature_dim):
                        ind['features'][i] += random.gauss(0, math.sqrt(tau_sq)) * 0.1
                        ind['features'][i] = max(0, ind['features'][i])
        
        # Compute final scores
        results = []
        for cand in candidates:
            # Find matching individual
            match = next((ind for ind in population if ind['text'] == cand), None)
            structural_score = match['weight'] if match else 0.0
            
            # Computational score
            comp_score = 0.0
            if has_num:
                cand_nums = re.findall(r'\b(\d+\.?\d*)\b', cand)
                if cand_nums:
                    for num_str in cand_nums:
                        if abs(float(num_str) - num_answer) < 0.01:
                            comp_score = 1.0
            
            if has_comp and cand == comp_answer:
                comp_score = 1.0
            
            # NCD score (max 15%)
            ncd_score = 1.0 - self._compute_ncd(prompt, cand)
            
            # Weighted combination
            final_score = 0.6 * structural_score + 0.25 * comp_score + 0.15 * ncd_score
            
            reasoning = f"Structural: {structural_score:.3f}, Computational: {comp_score:.3f}, NCD: {ncd_score:.3f}"
            results.append({'candidate': cand, 'score': final_score, 'reasoning': reasoning})
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 for a prompt-answer pair."""
        # Check meta-confidence first
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.5:
            return meta_conf
        
        # Evaluate this answer against all structural signals
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.3
        
        base_score = results[0]['score']
        
        # Check if computational answer exists
        has_num, num_answer = self._compute_numeric_answer(prompt)
        if has_num:
            ans_nums = re.findall(r'\b(\d+\.?\d*)\b', answer)
            if ans_nums and abs(float(ans_nums[0]) - num_answer) < 0.01:
                return min(0.85, base_score)
        
        # Never return > 0.9 unless definitive
        return min(0.75, base_score * meta_conf)