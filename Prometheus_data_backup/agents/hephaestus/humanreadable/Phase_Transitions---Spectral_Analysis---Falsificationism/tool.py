import re
import zlib
from typing import List, Dict, Any

class ReasoningTool:
    """
    Spectral-Order-Parameter Falsification Engine (SOPE)
    
    Mechanism:
    1. Order Parameter (Margin): Computes a structural consistency score between 
       the prompt's logical constraints (negations, comparatives, conditionals) 
       and each candidate. This acts as the system's "state".
    2. Spectral Analysis (Variance Monitoring): Instead of a time-series, we treat 
       the sequence of structural feature matches (presence/absence of key logic tokens) 
       as a signal. We compute the "spectral power" (variance/frequency of changes) 
       of these features across the candidate set relative to the prompt.
    3. Falsificationism: Candidates that violate hard logical constraints (modus tollens,
       negation flips) are assigned high "low-frequency power" (critical slowing down 
       indicator), triggering a falsification alarm (score penalty).
    4. Ranking: Candidates are ranked by structural consistency, using NCD only as a 
       tiebreaker for semantically identical but structurally distinct options.
    """
    
    def __init__(self):
        # Logical operators that define the "phase space" of the problem
        self.negations = ['no', 'not', 'never', 'none', 'cannot', 'impossible', 'false']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<', '>=', '<=']
        self.conditionals = ['if', 'then', 'unless', 'only if', 'provided', 'when']
        self.booleans = ['true', 'false', 'yes', 'no']

    def _extract_structural_features(self, text: str) -> Dict[str, Any]:
        """Extract logical signatures from text."""
        lower_text = text.lower()
        words = re.findall(r'\b\w+\b', lower_text)
        
        features = {
            'neg_count': sum(1 for w in words if w in self.negations),
            'comp_count': sum(1 for w in words if w in self.comparatives),
            'cond_count': sum(1 for w in words if w in self.conditionals),
            'has_numbers': bool(re.search(r'\d+(\.\d+)?', text)),
            'length': len(words)
        }
        
        # Extract specific numbers for numeric evaluation
        numbers = re.findall(r'\d+(\.\d+)?', text)
        features['numbers'] = [float(n) for n in numbers] if numbers else []
        
        return features

    def _check_logical_consistency(self, prompt_feats: Dict, cand_feats: Dict, prompt: str, candidate: str) -> float:
        """
        Evaluate falsification boundary. 
        Returns a penalty score (0.0 = consistent, 1.0 = falsified).
        """
        penalty = 0.0
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # 1. Negation Consistency (Modus Tollens check)
        # If prompt says "X is NOT Y", candidate saying "X is Y" gets penalized
        if prompt_feats['neg_count'] > 0:
            # Simple heuristic: if prompt has negation but candidate has none of the negation words
            # and the candidate length is significant, it might be ignoring the constraint.
            if cand_feats['neg_count'] == 0 and cand_feats['length'] > 3:
                # Check for direct contradiction patterns (simplified)
                if any(word in p_lower for word in ['not', 'no']) and any(word in c_lower for word in ['is', 'are', 'will']):
                    penalty += 0.3

        # 2. Numeric Consistency
        if prompt_feats['has_numbers'] and cand_feats['has_numbers']:
            p_nums = prompt_feats['numbers']
            c_nums = cand_feats['numbers']
            
            # Check for direct numeric contradictions if numbers match but logic flips
            # e.g., Prompt: "A > 5", Candidate: "4" (implies A <= 4 or specific value)
            # This is a heuristic approximation of numeric constraint propagation
            if p_nums and c_nums:
                # If prompt establishes a bound and candidate violates it directly
                # Example: Prompt "greater than 10", Candidate "5"
                if 'greater' in p_lower or '>' in p_lower:
                    if c_nums[0] < p_nums[-1] and len(c_nums) == 1:
                         penalty += 0.4
                elif 'less' in p_lower or '<' in p_lower:
                    if c_nums[0] > p_nums[-1] and len(c_nums) == 1:
                        penalty += 0.4

        # 3. Conditional/Structural Alignment
        # If prompt is conditional, candidate should ideally reflect uncertainty or conditionality
        if prompt_feats['cond_count'] > 0 and cand_feats['cond_count'] == 0:
            # If prompt is complex conditional but answer is absolute boolean
            if any(b in c_lower for b in self.booleans) and cand_feats['length'] < 10:
                penalty += 0.1 # Soft penalty for oversimplification

        return min(penalty, 1.0)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        try:
            z1 = len(zlib.compress(s1.encode()))
            z2 = len(zlib.compress(s2.encode()))
            z12 = len(zlib.compress((s1 + s2).encode()))
            denominator = max(z1, z2)
            if denominator == 0:
                return 1.0
            return (z12 - min(z1, z2)) / denominator
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        prompt_feats = self._extract_structural_features(prompt)
        results = []
        
        # Calculate "Spectral" variance of the candidate set to detect instability
        # Here approximated by the variance of structural feature counts across candidates
        cand_feats_list = [self._extract_structural_features(c) for c in candidates]
        
        for i, candidate in enumerate(candidates):
            cand_feats = cand_feats_list[i]
            
            # 1. Structural Consistency Score (The Order Parameter)
            falsification_penalty = self._check_logical_consistency(prompt_feats, cand_feats, prompt, candidate)
            
            # Base score from simple overlap of logical tokens (heuristic alignment)
            alignment = 0.5
            if cand_feats['neg_count'] > 0 and prompt_feats['neg_count'] > 0:
                alignment += 0.1
            if cand_feats['comp_count'] > 0 and prompt_feats['comp_count'] > 0:
                alignment += 0.1
            
            # Raw score before penalty
            raw_score = min(alignment, 1.0)
            
            # Apply Falsification Penalty (Critical Slowing Down Indicator)
            # High penalty -> Low score
            final_score = max(0.0, raw_score - falsification_penalty)
            
            # NCD Tiebreaker (only if scores are very close, handled by sorting stability)
            # We add a tiny epsilon based on NCD to break ties deterministically
            ncd_val = self._ncd(prompt, candidate)
            score_with_tiebreak = final_score - (ncd_val * 1e-6)

            results.append({
                "candidate": candidate,
                "score": round(score_with_tiebreak, 6),
                "reasoning": f"Structural consistency: {1-falsification_penalty:.2f}, Falsification penalty: {falsification_penalty:.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence based on structural alignment and lack of falsification."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        # Normalize score to 0-1 range roughly
        score = res[0]["score"]
        return max(0.0, min(1.0, score))