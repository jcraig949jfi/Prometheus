import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Fractal-Plastic NAS Reasoning Tool.
    
    Mechanism:
    1. Fractal Geometry (Multi-scale Parsing): The prompt is analyzed at three 
       recursive scales: Token (micro), Clause (meso), and Logical (macro).
       This mimics an Iterated Function System (IFS) where similar structural 
       checks (negations, comparatives) are applied at different resolutions.
       
    2. Neural Plasticity (Dynamic Weighting): Instead of fixed weights, the 
       importance of each scale is adjusted ("plasticity") based on the 
       presence of high-signal markers (e.g., "not", "if", numbers). 
       High-activation features strengthen their corresponding scale's influence.
       
    3. NAS (Motif Selection): The system selects the best "motif" (logical rule) 
       from a finite grammar (Equality, Inequality, Negation, Containment) 
       to score candidates.
       
    4. Scoring: Candidates are ranked by structural alignment with the prompt's 
       logical constraints, using NCD only as a tiebreaker for semantic similarity.
    """

    def __init__(self):
        # Finite grammar of logical motifs
        self.motifs = ['negation', 'comparative', 'conditional', 'numeric', 'containment']
        # Base weights (plasticity will adjust these)
        self.weights = {m: 1.0 for m in self.motifs}
        
    def _extract_features(self, text: str) -> Dict[str, float]:
        """Micro-scale: Extract structural features (Fractal Level 1)."""
        text_lower = text.lower()
        features = {
            'negation': len(re.findall(r'\b(not|no|never|neither|without)\b', text_lower)),
            'comparative': len(re.findall(r'\b(more|less|greater|smaller|better|worse|<|>|=)\b', text_lower)),
            'conditional': len(re.findall(r'\b(if|then|unless|otherwise|when)\b', text_lower)),
            'numeric': len(re.findall(r'\d+(?:\.\d+)?', text_lower)),
            'containment': len(re.findall(r'\b(in|contains|includes|within)\b', text_lower))
        }
        return features

    def _plasticity_adjust(self, features: Dict[str, float]) -> Dict[str, float]:
        """
        Meso-scale: Adjust weights based on feature density.
        Mimics Hebbian learning: "Cells that fire together, wire together."
        If a logical motif is detected, its weight is strengthened.
        """
        adjusted = {}
        total_activation = sum(features.values()) + 1e-6
        
        for motif, count in features.items():
            # Base weight
            w = 1.0
            # Plasticity boost: if feature exists, increase influence non-linearly
            if count > 0:
                w += (count * 0.5) + (count ** 2 * 0.2)
            adjusted[motif] = w
            
        # Normalize weights to prevent explosion
        max_w = max(adjusted.values()) + 1e-6
        return {k: v / max_w for k, v in adjusted.items()}

    def _apply_motif(self, motif: str, prompt: str, candidate: str, weights: Dict[str, float]) -> float:
        """Macro-scale: Apply specific logical motif to score candidate."""
        score = 0.0
        p_low = prompt.lower()
        c_low = candidate.lower()
        
        if motif == 'negation':
            # Check if candidate respects negation in prompt
            if 'not' in p_low or 'no' in p_low:
                # Simple heuristic: if prompt says "not X", candidate shouldn't be just "X"
                # This is a rough approximation of logical consistency
                if 'yes' in c_low and 'no' not in c_low:
                    score -= 0.5 * weights['negation']
                elif 'no' in c_low:
                    score += 0.5 * weights['negation']
                    
        elif motif == 'comparative':
            # Detect number comparisons
            nums_p = re.findall(r'\d+(?:\.\d+)?', p_low)
            nums_c = re.findall(r'\d+(?:\.\d+)?', c_low)
            
            if nums_p and nums_c:
                try:
                    # Check if candidate preserves order or magnitude logic
                    p_vals = [float(n) for n in nums_p]
                    c_vals = [float(n) for n in nums_c]
                    
                    if 'greater' in p_low or 'more' in p_low or '>' in p_low:
                        if max(c_vals) >= max(p_vals): score += 0.4 * weights['comparative']
                    elif 'less' in p_low or 'smaller' in p_low or '<' in p_low:
                        if min(c_vals) <= min(p_vals): score += 0.4 * weights['comparative']
                    else:
                        # General numeric presence bonus
                        score += 0.2 * weights['comparative']
                except ValueError:
                    pass

        elif motif == 'conditional':
            # If prompt has "if", candidate often needs "then" or logical consequence
            if 'if' in p_low:
                if any(k in c_low for k in ['then', 'therefore', 'so', 'yes', 'no']):
                    score += 0.3 * weights['conditional']
        
        elif motif == 'containment':
            # Candidate should contain key nouns from prompt
            prompt_words = set(re.findall(r'\b[a-z]{4,}\b', p_low))
            candidate_words = set(re.findall(r'\b[a-z]{4,}\b', c_low))
            if prompt_words:
                overlap = len(prompt_words & candidate_words) / len(prompt_words)
                score += overlap * 0.3 * weights['containment']

        return score

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Compute Normalized Compression Distance as a tiebreaker."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            denom = max(c1, c2)
            if denom == 0: return 1.0
            return (c12 - min(c1, c2)) / denom
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # 1. Fractal Analysis: Extract features at micro scale
        features = self._extract_features(prompt)
        
        # 2. Plasticity: Adjust weights based on prompt structure
        dynamic_weights = self._plasticity_adjust(features)
        
        # 3. NAS: Evaluate candidates using motif grammar
        scored_candidates = []
        for cand in candidates:
            total_score = 0.0
            
            # Aggregate score across all active motifs
            for motif in self.motifs:
                total_score += self._apply_motif(motif, prompt, cand, dynamic_weights)
            
            # Add base semantic similarity (NCD inverse) as a small baseline
            # Lower NCD is better, so we subtract it, but scale it small so logic dominates
            ncd = self._compute_ncd(prompt, cand)
            # Normalize NCD to [0, 1] where 1 is similar. 
            # NCD 0 = identical, 1 = disjoint. We want high score for similarity.
            sim_score = (1.0 - ncd) * 0.1 
            
            final_score = total_score + sim_score
            scored_candidates.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Motif alignment ({sum(dynamic_weights.values()):.2f} plasticity factor) + semantic similarity"
            })
        
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Evaluate confidence based on structural alignment.
        Returns 0-1.
        """
        # Run single evaluation
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.0
            
        # Normalize score to 0-1 range roughly
        # Base score from logic motifs usually ranges -1 to 2 depending on matches
        raw_score = results[0]['score']
        
        # Sigmoid-like mapping to [0, 1]
        # If score > 0.5, high confidence. If < -0.5, low.
        confidence = 1 / (1 + 2.718 ** (-2 * (raw_score - 0.2)))
        
        # Clamp
        return max(0.0, min(1.0, confidence))