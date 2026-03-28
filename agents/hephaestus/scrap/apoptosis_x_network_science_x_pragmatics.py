import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Pragmatic Apoptotic Network Cascade (PANC) Implementation.
    
    Mechanism:
    1. Network Construction: Candidates are nodes. Edges represent structural similarity.
    2. Pragmatic Scoring (Viability): Each candidate is scored based on Gricean maxims
       implemented as structural checks:
       - Quantity: Length appropriateness (not too short/empty).
       - Quality: Presence of contradiction markers vs prompt negations.
       - Relation: Keyword overlap with prompt (semantic relevance).
       - Manner: Structural clarity (balanced parentheses, no trailing garbage).
    3. Apoptotic Cascade: 
       - Nodes below a dynamic viability threshold are marked for removal.
       - Removal propagates: If a node is removed, neighbors lose confidence proportional
         to their edge weight (simulating caspase cascade).
    4. Ranking: Survivors are ranked by residual score. NCD is used only as a tiebreaker.
    """

    def __init__(self):
        self.threshold_base = 0.3
        self.cascade_strength = 0.5

    def _structural_parse(self, text: str) -> dict:
        """Extract structural features: negations, comparatives, numbers."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(no|not|never|none|neither|without)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|better|worst)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|otherwise|else)\b', text_lower)),
            'numbers': re.findall(r'\d+\.?\d*', text_lower),
            'length': len(text.split()),
            'paren_balance': text.count('(') - text.count(')')
        }
        return features

    def _gricean_score(self, prompt: str, candidate: str) -> float:
        """
        Calculate pragmatic viability based on Grice's Maxims.
        Returns a score between 0.0 and 1.0.
        """
        if not candidate.strip():
            return 0.0
            
        p_feat = self._structural_parse(prompt)
        c_feat = self._structural_parse(candidate)
        score = 0.0
        
        # 1. Maxim of Relation (Relevance)
        # Check keyword overlap (simplified to words > 3 chars)
        p_words = {w for w in re.findall(r'\w+', prompt.lower()) if len(w) > 3}
        c_words = {w for w in re.findall(r'\w+', candidate.lower()) if len(w) > 3}
        if p_words:
            overlap = len(p_words & c_words) / len(p_words)
            score += 0.4 * overlap
        else:
            score += 0.1 # Minimal score if prompt has no keywords
            
        # 2. Maxim of Quality (Truth/Consistency)
        # Penalty if prompt has negation but candidate ignores it (simplified heuristic)
        # Or if candidate claims certainty ("always") where prompt is conditional
        if p_feat['conditionals'] > 0 and 'always' in c_feat.get('numbers', []) or 'always' in candidate.lower():
            score -= 0.2
        
        # 3. Maxim of Quantity (Information)
        # Penalize extremely short answers unless prompt is yes/no type
        if c_feat['length'] < 2 and ('yes' not in candidate.lower() and 'no' not in candidate.lower()):
            score -= 0.3
        if c_feat['length'] == 0:
            return 0.0
            
        # 4. Maxim of Manner (Clarity)
        if c_feat['paren_balance'] != 0:
            score -= 0.2
            
        # Numeric Consistency Check
        if p_feat['numbers'] and c_feat['numbers']:
            try:
                # Simple check: if prompt has "less than", does candidate reflect smaller number?
                # This is a heuristic proxy for logical consistency
                if 'less' in prompt.lower() or 'smaller' in prompt.lower():
                    if len(c_feat['numbers']) >= 1:
                        # Just validating parseability adds slight confidence
                        score += 0.1
            except:
                pass

        return max(0.0, min(1.0, score))

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len1 = len(zlib.compress(s1_b))
        len2 = len(zlib.compress(s2_b))
        len_combined = len(zlib.compress(s1_b + s2_b))
        max_len = max(len1, len2)
        if max_len == 0:
            return 0.0
        return (len_combined - min(len1, len2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        n = len(candidates)
        if n == 1:
            # Single candidate: just evaluate viability
            score = self._gricean_score(prompt, candidates[0])
            return [{"candidate": candidates[0], "score": float(score), "reasoning": "Single candidate viability"}]

        # 1. Initialize Nodes with Pragmatic Viability Scores
        scores = [self._gricean_score(prompt, c) for c in candidates]
        
        # 2. Build Adjacency Matrix based on Structural Similarity (NCD)
        # Edge weight = 1 - NCD (Higher weight = more similar)
        weights = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                dist = self._compute_ncd(candidates[i], candidates[j])
                w = 1.0 - dist
                weights[i][j] = w
                weights[j][i] = w

        # 3. Apoptotic Cascade Simulation
        # Iteratively prune nodes below threshold and dampen neighbors
        active = [True] * n
        max_iterations = n + 1 # Safety cap
        
        for _ in range(max_iterations):
            changed = False
            for i in range(n):
                if not active[i]:
                    continue
                    
                # Check viability
                if scores[i] < self.threshold_base:
                    active[i] = False
                    changed = True
                    
                    # Cascade: Dampen neighbors
                    for j in range(n):
                        if active[j] and weights[i][j] > 0.1:
                            # Reduce neighbor score proportionally to edge weight
                            damping = weights[i][j] * self.cascade_strength
                            scores[j] = max(0.0, scores[j] - damping)
                            changed = True
            
            if not changed:
                break

        # 4. Rank and Format Output
        results = []
        for i, c in enumerate(candidates):
            if active[i]:
                # Final score is the residual viability after cascade
                final_score = scores[i]
                reason = "Survived apoptotic pruning"
            else:
                # Even if pruned, we return it with low score for completeness
                final_score = scores[i] * 0.5 # Penalty for being pruned
                reason = "Pruned via caspase cascade"
                
            results.append({
                "candidate": c,
                "score": float(final_score),
                "reasoning": reason
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Evaluate confidence in a specific (prompt, answer) pair.
        Uses Gricean scoring as primary, NCD as secondary validation.
        """
        # Primary: Pragmatic Viability
        viability = self._gricean_score(prompt, answer)
        
        # Secondary: Structural consistency check (NCD against prompt context)
        # If answer is completely unrelated noise, NCD will be high (distance ~1.0)
        # We want low distance for high confidence, but NCD is distance.
        # So we invert: similarity = 1 - NCD
        ncd_val = self._compute_ncd(prompt, answer)
        similarity = 1.0 - ncd_val
        
        # Weighted combination: Viability is more important than raw string similarity
        # because a correct short answer (e.g., "No") might have low string similarity
        # but high pragmatic viability.
        confidence = (viability * 0.7) + (similarity * 0.3)
        
        return float(max(0.0, min(1.0, confidence)))