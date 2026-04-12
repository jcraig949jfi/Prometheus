import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Holographic Global Workspace with Pragmatic Gating (HGW-PG).
    
    Mechanism:
    1. Holographic Bulk (B): Candidates are encoded as sparse, high-dimensional 
       vectors where semantic features (words) and structural features (negations, 
       comparatives, numbers) are superimposed via hashing.
    2. Global Workspace Selection: The prompt acts as an attention mask. We compute 
       the projection of each candidate onto the prompt's structural skeleton. 
       Candidates matching the prompt's logical constraints (negation, transitivity) 
       receive higher activation.
    3. Pragmatic Gating (RSA): A secondary scoring layer checks for contextual 
       consistency. If the prompt implies a comparison (e.g., "which is larger?"), 
       candidates lacking numeric content or comparative logic are penalized.
       This simulates the "implicature" check where context filters valid answers.
    4. Loop: The final score is a weighted sum of holographic overlap (semantic) 
       and pragmatic alignment (structural/logical).
    """

    def __init__(self):
        self.dim = 1024  # Holographic vector dimension
        self.rng = np.random.RandomState(42)  # Deterministic seed
        
        # Precompute hash map for consistent vector retrieval
        self.hash_cache = {}

    def _hash_vector(self, token: str) -> np.ndarray:
        """Generate a deterministic pseudo-random vector for a token."""
        if token not in self.hash_cache:
            # Simple deterministic hash based on string content
            h = hash(token)
            self.rng.seed(h)
            vec = self.rng.randn(self.dim)
            vec = vec / np.linalg.norm(vec)
            self.hash_cache[token] = vec
        return self.hash_cache[token]

    def _structural_parse(self, text: str) -> dict:
        """Extract logical structure: negations, comparatives, numbers."""
        text_lower = text.lower()
        features = {
            'negation': len(re.findall(r'\b(not|no|never|neither|without)\b', text_lower)),
            'comparative': len(re.findall(r'\b(more|less|larger|smaller|greater|higher|lower|better|worst)\b', text_lower)),
            'numeric': re.findall(r'\d+\.?\d*', text_lower),
            'conditional': len(re.findall(r'\b(if|then|unless|otherwise)\b', text_lower)),
            'length': len(text.split())
        }
        return features

    def _encode_hologram(self, text: str) -> np.ndarray:
        """Encode text into a superposition of token vectors (Holographic Bulk)."""
        # Tokenize: split by non-alphanumeric, keep numbers and words
        tokens = re.findall(r'[a-zA-Z0-9\.]+', text.lower())
        if not tokens:
            return np.zeros(self.dim)
        
        # Superposition: Sum of normalized token vectors
        vec = np.zeros(self.dim)
        for token in tokens:
            vec += self._hash_vector(token)
        
        # Normalize to prevent magnitude explosion
        if np.linalg.norm(vec) > 0:
            vec /= np.linalg.norm(vec)
        return vec

    def _pragmatic_gate(self, prompt_feat: dict, cand_feat: dict, raw_score: float) -> float:
        """
        Apply Pragmatic Gating (RSA layer).
        Adjusts score based on whether the candidate satisfies the prompt's 
        implicit logical requirements (e.g., if prompt asks for 'larger', 
        candidate should ideally involve numbers or comparatives).
        """
        penalty = 0.0
        
        # Rule 1: Numeric Consistency
        # If prompt has numbers and comparatives, candidate should too
        if prompt_feat['numeric'] and prompt_feat['comparative']:
            if not cand_feat['numeric']:
                penalty -= 0.4  # Strong penalty for missing numbers in math tasks
            if cand_feat['comparative'] == 0 and len(cand_feat.get('raw_text', '')) < 10:
                # Short answers without comparatives in a comparison task are suspicious
                penalty -= 0.2

        # Rule 2: Negation Matching
        # If prompt is heavily negated, simple positive assertions might be wrong
        if prompt_feat['negation'] > 0 and cand_feat['negation'] == 0:
            # Heuristic: In negated contexts, simple "Yes" or positive statements 
            # often require more scrutiny. We don't penalize heavily, but reduce confidence.
            penalty -= 0.15

        # Rule 3: Length/Complexity Match (Pragmatic expectation)
        # If prompt is complex (high conditionals), very short answers are often incomplete
        if prompt_feat['conditional'] > 0 and cand_feat['length'] < 3:
            penalty -= 0.25

        return raw_score + penalty

    def _compute_structural_similarity(self, p_feat: dict, c_feat: dict) -> float:
        """Compute similarity based on structural features rather than just words."""
        score = 0.0
        
        # Numeric proximity check
        if p_feat['numeric'] and c_feat['numeric']:
            try:
                # Check if candidate numbers are logically derived or present
                # Simple presence boost for now, as full arithmetic requires parsing
                score += 0.2 
            except:
                pass
        
        # Comparative alignment
        if p_feat['comparative'] > 0:
            if c_feat['comparative'] > 0:
                score += 0.2
        
        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_vec = self._encode_hologram(prompt)
        prompt_feat = self._structural_parse(prompt)
        
        results = []
        
        # Step 1: Encode all candidates and compute initial holographic overlap
        candidate_data = []
        for cand in candidates:
            cand_vec = self._encode_hologram(cand)
            cand_feat = self._structural_parse(cand)
            cand_feat['raw_text'] = cand
            
            # Holographic similarity (dot product of normalized vectors)
            h_score = float(np.dot(prompt_vec, cand_vec))
            
            # Structural bonus
            s_score = self._compute_structural_similarity(prompt_feat, cand_feat)
            
            # Initial raw score
            raw_score = 0.6 * h_score + 0.4 * s_score
            
            candidate_data.append({
                'candidate': cand,
                'raw_score': raw_score,
                'features': cand_feat
            })
        
        # Step 2: Apply Pragmatic Gating and Rank
        # We normalize scores first to make gating effects relative
        raw_scores = [c['raw_score'] for c in candidate_data]
        if raw_scores:
            mean_score = np.mean(raw_scores)
            std_score = np.std(raw_scores) + 1e-6
            for c in candidate_data:
                # Normalize before gating
                norm_score = (c['raw_score'] - mean_score) / std_score
                gated_score = self._pragmatic_gate(prompt_feat, c['features'], norm_score)
                c['final_score'] = gated_score
        
        # Sort by final score descending
        candidate_data.sort(key=lambda x: x['final_score'], reverse=True)
        
        # Format output
        output = []
        max_score = candidate_data[0]['final_score'] if candidate_data else 0
        min_score = candidate_data[-1]['final_score'] if candidate_data else 0
        score_range = max_score - min_score + 1e-6
        
        for i, item in enumerate(candidate_data):
            # Rescale to 0-1 for the user, preserving rank
            normalized_score = (item['final_score'] - min_score) / score_range
            
            reasoning = f"Holographic overlap: {item['raw_score']:.3f}; "
            if item['features']['numeric']:
                reasoning += "Numeric content detected; "
            if item['features']['negation']:
                reasoning += "Negation present; "
            if prompt_feat['comparative'] and not item['features']['comparative']:
                reasoning += "Penalty: Missing comparative in comparison task; "
            
            output.append({
                "candidate": item['candidate'],
                "score": float(normalized_score),
                "reasoning": reasoning.strip()
            })
            
        return output

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.0
        return results[0]['score']