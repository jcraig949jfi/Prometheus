import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    CAINC: Compositional Adaptive Immune Network operating at Criticality.
    
    Mechanism:
    1. Compositionality: Parses prompts into structural primitives (negations, comparatives, 
       conditionals, numeric values) rather than raw strings.
    2. Immune Dynamics: Treats candidates as 'clones'. Affinity is determined by structural 
       alignment with the prompt's logical constraints (e.g., does the candidate satisfy 
       the detected negation or numeric inequality?).
    3. Phase Transitions: Uses a global control parameter (lambda) tuned by the variance 
       of structural matches. 
       - Low variance (frozen): High confidence in dominant structural pattern; strict scoring.
       - High variance (critical/explosive): Relaxes scoring to allow diverse candidates 
         if structural signals are weak, preventing premature convergence on wrong answers.
    
    Scoring: Primary signal is structural/logic match. NCD is used only as a tie-breaker.
    """

    def __init__(self):
        self.lambda_c = 0.5  # Critical threshold
        self.clonal_decay = 0.9

    def _extract_structural_features(self, text: str) -> Dict:
        """Extract compositional primitives: negations, comparatives, numbers, conditionals."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither|without)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|provided)\b', text_lower)),
            'numbers': [float(n) for n in re.findall(r'-?\d+\.?\d*', text)],
            'length': len(text.split())
        }
        return features

    def _check_logical_consistency(self, prompt_feats: Dict, cand_feats: Dict, prompt: str, candidate: str) -> float:
        """Evaluate affinity based on logical constraint propagation."""
        score = 0.0
        constraints_met = 0
        total_constraints = 0

        # 1. Numeric Evaluation (Transitivity/Comparison)
        if prompt_feats['numbers'] and cand_feats['numbers']:
            total_constraints += 1
            p_nums = prompt_feats['numbers']
            c_nums = cand_feats['numbers']
            
            # Check for direct number presence or logical derivation
            # Simple heuristic: If prompt has comparison words, check order
            if prompt_feats['comparatives'] > 0:
                if 'more' in prompt.lower() or 'greater' in prompt.lower() or 'higher' in prompt.lower():
                    if c_nums[0] >= max(p_nums): # Candidate implies larger value
                        score += 1.0
                        constraints_met += 1
                elif 'less' in prompt.lower() or 'smaller' in prompt.lower() or 'lower' in prompt.lower():
                    if c_nums[0] <= min(p_nums): # Candidate implies smaller value
                        score += 1.0
                        constraints_met += 1
            else:
                # Exact number match bonus
                if any(abs(p - c) < 1e-6 for p in p_nums for c in c_nums):
                    score += 0.8
                    constraints_met += 1
        
        # 2. Negation Handling
        if prompt_feats['negations'] > 0:
            total_constraints += 1
            # If prompt has negation, candidate should ideally reflect it or be short (Yes/No)
            # Heuristic: If candidate contains negation words, it might be aligning with a negative constraint
            if cand_feats['negations'] > 0 or cand_feats['length'] < 4: 
                score += 0.9
                constraints_met += 1
            else:
                # Penalty for ignoring negation if the candidate is long and affirmative
                if cand_feats['length'] > 4 and cand_feats['negations'] == 0:
                    score -= 0.5 

        # 3. Conditional/Structural Overlap
        if prompt_feats['conditionals'] > 0:
            total_constraints += 1
            if cand_feats['conditionals'] > 0 or any(k in candidate.lower() for k in ['if', 'then', 'so', 'therefore']):
                score += 0.7
                constraints_met += 1

        # Normalize by constraints found
        if total_constraints > 0:
            return score / total_constraints
        return 0.0

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tie-breaker."""
        if not s1 or not s2:
            return 1.0
        len1 = len(zlib.compress(s1.encode()))
        len2 = len(zlib.compress(s2.encode()))
        len_joint = len(zlib.compress((s1 + s2).encode()))
        max_len = max(len1, len2)
        if max_len == 0:
            return 0.0
        return (len_joint - min(len1, len2)) / max_len

    def _compute_order_parameter(self, affinities: List[float]) -> float:
        """Calculate variance to detect phase transition (Criticality)."""
        if len(affinities) < 2:
            return 0.0
        mean_aff = sum(affinities) / len(affinities)
        variance = sum((a - mean_aff) ** 2 for a in affinities) / len(affinities)
        return math.sqrt(variance)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []

        prompt_feats = self._extract_structural_features(prompt)
        results = []
        affinities = []

        # Phase 1: Clonal Selection (Affinity Calculation)
        for cand in candidates:
            cand_feats = self._extract_structural_features(cand)
            # Primary Score: Structural Logic
            logic_score = self._check_logical_consistency(prompt_feats, cand_feats, prompt, cand)
            affinities.append(logic_score)

        # Phase 2: Criticality Tuning
        # Order parameter (variance) determines if we are in frozen (exploitation) or explosive (exploration) regime
        order_param = self._compute_order_parameter(affinities)
        
        # Adjust scoring sensitivity based on proximity to criticality
        # If variance is low (frozen), small differences matter less (smoothing)
        # If variance is high (near critical), we amplify differences to select the best
        critical_factor = 1.0
        if order_param > 0.1: # Near critical/explosive
            critical_factor = 1.5 # Amplify differences
        elif order_param < 0.01: # Frozen
            critical_factor = 0.8 # Smooth out noise

        # Phase 3: Scoring and Ranking
        scored_candidates = []
        for i, cand in enumerate(candidates):
            base_score = affinities[i]
            
            # Apply criticality modulation
            modulated_score = base_score * critical_factor
            
            # Add small deterministic noise based on index to break ties consistently if needed
            # but primarily rely on NCD for true ties in logic
            scored_candidates.append({
                'candidate': cand,
                'logic_score': modulated_score,
                'raw_affinity': base_score
            })

        # Sort by logic score descending
        scored_candidates.sort(key=lambda x: x['logic_score'], reverse=True)

        # Apply NCD as tie-breaker for top candidates with similar logic scores
        final_results = []
        threshold = 0.05 # Logic score difference considered a tie
        
        for i, item in enumerate(scored_candidates):
            current_score = item['logic_score']
            reasoning = f"Structural match: {item['raw_affinity']:.2f}. "
            
            # Check for ties with neighbors
            is_tie = False
            if i > 0 and abs(current_score - scored_candidates[i-1]['logic_score']) < threshold:
                is_tie = True
            
            if is_tie:
                # Use NCD against prompt to break tie
                prev_item = final_results[-1] # The one currently ranked higher
                ncd_curr = self._ncd(prompt, item['candidate'])
                ncd_prev = self._ncd(prompt, prev_item['candidate'])
                
                if ncd_curr < ncd_prev:
                    # Swap logic: current is closer to prompt structurally via compression
                    reasoning += "NCD tie-breaker favored this candidate. "
                    # We don't re-sort the whole list here for simplicity, 
                    # but in a full sort we would have swapped. 
                    # Instead, we adjust the final score slightly to reflect rank.
                    final_score = current_score + 0.001 
                else:
                    final_score = current_score - 0.001
                    reasoning += "NCD tie-breaker maintained previous rank. "
            else:
                final_score = current_score
                reasoning += "Distinct structural signal."

            final_results.append({
                "candidate": item['candidate'],
                "score": float(final_score),
                "reasoning": reasoning
            })

        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses structural alignment strength as the primary proxy for confidence.
        """
        prompt_feats = self._extract_structural_features(prompt)
        cand_feats = self._extract_structural_features(answer)
        
        logic_score = self._check_logical_consistency(prompt_feats, cand_feats, prompt, answer)
        
        # Map logic score to confidence
        # Strong structural match -> High confidence
        # Weak/No structural match -> Low confidence (relying on NCD fallback implies uncertainty)
        
        base_conf = max(0.0, min(1.0, logic_score))
        
        # Boost if numbers match exactly
        if prompt_feats['numbers'] and cand_feats['numbers']:
            if any(abs(p - c) < 1e-6 for p in prompt_feats['numbers'] for c in cand_feats['numbers']):
                base_conf = min(1.0, base_conf + 0.2)
                
        return float(base_conf)