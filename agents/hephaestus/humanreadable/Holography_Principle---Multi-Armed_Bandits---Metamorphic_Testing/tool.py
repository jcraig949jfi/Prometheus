import numpy as np
from typing import Dict, List

class ReasoningTool:
    """
    Bandit-Guided Metamorphic Holographic Scorer (BMHS).
    
    Holography: Compresses answer structure into boundary vector.
    Bandits: UCB1 selects which metamorphic relations to test.
    Metamorphic Testing: Applies transformations, checks consistency.
    """
    
    def __init__(self):
        self.F = 512  # Boundary vector dimension
        self.budget = 30  # Bandit pulls per evaluation
        self.ucb_c = 1.0  # Exploration constant
        
    def _extract_boundary(self, text: str) -> np.ndarray:
        """Extract holographic boundary vector from text."""
        text_lower = text.lower()
        features = []
        
        # Negations
        features.append(1.0 if re.search(r'\b(not|no|n\'t|never|none)\b', text_lower) else 0.0)
        
        # Comparatives
        features.append(1.0 if re.search(r'(greater|more|larger|higher|above)', text_lower) else 0.0)
        features.append(1.0 if re.search(r'(less|fewer|smaller|lower|below)', text_lower) else 0.0)
        features.append(1.0 if re.search(r'(equal|same|identical)', text_lower) else 0.0)
        
        # Conditionals
        features.append(1.0 if re.search(r'\b(if|when|unless|provided)\b', text_lower) else 0.0)
        
        # Causal
        features.append(1.0 if re.search(r'(because|due to|leads to|causes|results in)', text_lower) else 0.0)
        
        # Temporal ordering
        features.append(1.0 if re.search(r'(first|before|earlier|prior)', text_lower) else 0.0)
        features.append(1.0 if re.search(r'(last|after|later|following)', text_lower) else 0.0)
        
        # Extract numbers
        numbers = re.findall(r'-?\d+\.?\d*', text)
        num_count = len(numbers)
        features.append(min(1.0, num_count / 5.0))
        if numbers:
            features.append(min(1.0, float(numbers[0]) / 100.0))
        else:
            features.append(0.0)
        
        # Hash text tokens into remaining dimensions
        tokens = re.findall(r'\b\w+\b', text_lower)
        vec = np.zeros(self.F)
        vec[:len(features)] = features
        for token in tokens[:50]:
            idx = hash(token) % (self.F - len(features)) + len(features)
            vec[idx] = min(1.0, vec[idx] + 0.1)
        
        return vec / (np.linalg.norm(vec) + 1e-9)
    
    def _metamorphic_relations(self):
        """Define metamorphic transformation functions."""
        return {
            'negate': lambda x: negate(x) if len(x) < 100 else x,
            'double_numbers': lambda x: re.sub(r'\b(\d+)\b', lambda m: str(int(m.group(1)) * 2), x),
            'swap_order': lambda x: ' '.join(x.split()[::-1]),
            'remove_negation': lambda x: re.sub(r'\b(not|no|n\'t)\b', '', x, flags=re.I),
            'flip_comparison': lambda x: x.replace('greater', 'LESS').replace('less', 'greater').replace('LESS', 'less'),
        }
    
    def _ucb_bandit_score(self, b_cand: np.ndarray, b_ref: np.ndarray, ref_text: str) -> float:
        """Run UCB bandit to select metamorphic relations and score consistency."""
        relations = self._metamorphic_relations()
        K = len(relations)
        arm_names = list(relations.keys())
        n = np.zeros(K)  # Pull counts
        s = np.zeros(K)  # Cumulative rewards
        
        for t in range(1, self.budget + 1):
            # Compute UCB scores
            ucb = np.where(n > 0, s / n + self.ucb_c * np.sqrt(np.log(t) / (n + 1e-9)), 1e9)
            k_star = np.argmax(ucb)
            
            # Apply metamorphic relation
            try:
                transformed = relations[arm_names[k_star]](ref_text)
                b_trans = self._extract_boundary(transformed)
                reward = 1.0 - np.arccos(np.clip(np.dot(b_cand, b_trans), -1, 1)) / np.pi
            except:
                reward = 0.0
            
            n[k_star] += 1
            s[k_star] += reward
        
        return np.sum(s / np.maximum(1, n)) / K
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check prompt for ambiguity/unanswerability markers."""
        prompt_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'(have you stopped|have you quit|why did .* (fail|stop))', prompt_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'every .* a \w+', prompt_lower):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'(he|she|they|it) (was|is|said)', prompt_lower) and 'who' in prompt_lower:
            return 0.25
        
        # False dichotomy
        if re.search(r'either .* or .*\?', prompt_lower) and 'only' not in prompt_lower:
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', prompt_lower) and not re.search(r'(according to|by measure)', prompt_lower):
            return 0.3
        
        # Insufficient information
        unknowns = len(re.findall(r'\b(unknown|not given|missing|unclear)\b', prompt_lower))
        if unknowns > 0:
            return 0.2
        
        return 0.8  # Default high meta-confidence
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates using holographic bandit-metamorphic scoring."""
        b_ref = self._extract_boundary(prompt)
        results = []
        
        for cand in candidates:
            b_cand = self._extract_boundary(cand)
            
            # Core holographic-bandit score
            bandit_score = self._ucb_bandit_score(b_cand, b_ref, prompt)
            
            # Structural similarity
            struct_score = np.dot(b_cand, b_ref)
            
            # NCD tiebreaker (max 10%)
            ncd = len(zlib.compress((prompt + cand).encode())) / (len(zlib.compress(prompt.encode())) + len(zlib.compress(cand.encode())) + 1e-9)
            ncd_score = 1.0 - ncd
            
            # Combine: 50% bandit, 40% structural, 10% NCD
            final_score = 0.5 * bandit_score + 0.4 * struct_score + 0.1 * ncd_score
            
            reasoning = f"Bandit={bandit_score:.2f}, Struct={struct_score:.2f}, NCD={ncd_score:.2f}"
            results.append({"candidate": cand, "score": final_score, "reasoning": reasoning})
        
        # Use primitive for agreement-based confidence
        scores = [r["score"] for r in results]
        if len(scores) > 1:
            score_entropy = entropy(np.array(scores) / (np.sum(scores) + 1e-9))
            for r in results:
                r["score"] *= (1.0 - 0.3 * score_entropy)  # Penalize high entropy
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on prompt properties and answer quality."""
        # Meta-confidence from prompt analysis
        meta_conf = self._meta_confidence(prompt)
        
        # If prompt is problematic, cap confidence
        if meta_conf < 0.5:
            return meta_conf
        
        # Evaluate answer quality
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.3
        
        base_score = results[0]["score"]
        
        # Check if answer has structural content
        b_ans = self._extract_boundary(answer)
        if np.linalg.norm(b_ans) < 0.1:
            return 0.2  # Empty/trivial answer
        
        # Cap confidence unless we have strong signal
        conf = min(0.85, base_score * meta_conf)
        
        # Never exceed 0.9 unless perfect match
        if conf > 0.9:
            conf = 0.85
        
        return max(0.1, conf)