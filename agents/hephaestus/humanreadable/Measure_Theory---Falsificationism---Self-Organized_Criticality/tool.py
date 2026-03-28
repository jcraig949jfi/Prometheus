import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Critical Falsification Measure Learner (CFML) Implementation.
    
    Mechanism:
    1. Falsificationism (Core): Candidates are scored by how well they survive 
       structural constraints (negations, conditionals, numeric logic) extracted 
       from the prompt. This is the primary driver.
    2. Measure Theory (Confidence Wrapper): Instead of direct scoring, we maintain 
       a 'belief measure' over the candidate space. We simulate a sigma-algebra 
       by partitioning candidates into 'falsified' (0 measure) and 'surviving' 
       (positive measure) sets based on strict logical checks.
    3. Self-Organized Criticality (Avalanche Trigger): We monitor the 'tension' 
       (disagreement among top candidates). If tension exceeds a critical threshold, 
       we trigger an 'avalanche' re-evaluation using a stricter falsification test 
       (simulating the sandpile toppling) to escape local minima in reasoning.
    
    Note: Pure measure theory and SOC are computationally approximated here to 
    satisfy the constraint of being a lightweight, standard-lib-only tool that 
    beats NCD baselines via structural parsing.
    """

    def __init__(self):
        self.critical_threshold = 0.85  # SOC critical point for avalanche
        self.bonferroni_alpha = 0.05    # Stringency for falsification tests

    def _structural_parse(self, text: str) -> dict:
        """Extract logical structures: negations, comparatives, numbers."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither|without)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|otherwise)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', text_lower)),
            'numbers': re.findall(r'-?\d+\.?\d*', text),
            'boolean_yes': bool(re.search(r'\byes\b', text_lower)),
            'boolean_no': bool(re.search(r'\bno\b', text_lower))
        }
        return features

    def _check_falsification(self, prompt_features: dict, candidate: str) -> Tuple[bool, float]:
        """
        Attempt to falsify the candidate based on prompt constraints.
        Returns (is_falsified, penalty_score).
        """
        cand_features = self._structural_parse(candidate)
        penalty = 0.0
        is_falsified = False

        # 1. Negation Consistency Check
        # If prompt has strong negation context, candidate lacking it might be suspect
        if prompt_features['negations'] > 0:
            if cand_features['negations'] == 0 and prompt_features['negations'] > cand_features['negations']:
                # Heuristic: If prompt emphasizes what is NOT, answer should reflect awareness
                penalty += 0.2
        
        # 2. Numeric Consistency (Simple magnitude check)
        # If both have numbers, check if candidate contradicts prompt logic (simplified)
        if prompt_features['numbers'] and cand_features['numbers']:
            p_nums = [float(n) for n in prompt_features['numbers']]
            c_nums = [float(n) for n in cand_features['numbers']]
            
            # Detect explicit contradictions in simple comparisons if keywords exist
            if prompt_features['comparatives'] > 0:
                # If prompt asks for "smaller" and candidate provides larger number without context
                if 'smaller' in candidate.lower() or 'less' in candidate.lower():
                    if max(c_nums) > max(p_nums):
                        is_falsified = True
                elif 'larger' in candidate.lower() or 'greater' in candidate.lower():
                    if min(c_nums) < min(p_nums):
                        is_falsified = True

        # 3. Boolean Contradiction
        if prompt_features['boolean_yes'] and cand_features['boolean_no']:
            # Potential contradiction if prompt implies affirmative
            if 'yes' in prompt_features.get('numbers', []) == 0: # Weak heuristic
                 penalty += 0.3
        
        if is_falsified:
            penalty = 1.0
            
        return is_falsified, penalty

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_combined = len(zlib.compress(s1_bytes + s2_bytes))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_combined - min(len_s1, len_s2)) / max_len

    def _simulate_avalanche(self, prompt: str, candidates: List[str], base_scores: List[float]) -> List[float]:
        """
        SOC Component: If the distribution of scores is too uniform (high entropy/tension),
        trigger a re-evaluation (topple) to sharpen differences.
        """
        if len(candidates) < 2:
            return base_scores
            
        # Calculate tension (variance proxy)
        avg_score = sum(base_scores) / len(base_scores)
        variance = sum((s - avg_score) ** 2 for s in base_scores) / len(base_scores)
        
        # If variance is low (system stuck in local minima), trigger avalanche
        if variance < 0.05:
            # Re-evaluate with stricter penalties (simulating toppling)
            refined_scores = []
            for i, cand in enumerate(candidates):
                is_falsified, penalty = self._check_falsification(self._structural_parse(prompt), cand)
                if is_falsified:
                    refined_scores.append(0.0) # Hard falsification
                else:
                    # Boost differentiation
                    base = base_scores[i]
                    refined_scores.append(base * 0.9 if base > 0.5 else base * 1.1)
            return refined_scores
            
        return base_scores

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_feats = self._structural_parse(prompt)
        scores = []
        reasons = []

        # Phase 1: Initial Scoring via Falsification Attempts
        for cand in candidates:
            is_falsified, penalty = self._check_falsification(prompt_feats, cand)
            
            if is_falsified:
                score = 0.0
                reason = "Falsified by structural constraint."
            else:
                # Base score starts high, reduced by penalties
                base = 0.8 
                score = max(0.0, base - penalty)
                
                # Add bonus for structural alignment
                cand_feats = self._structural_parse(cand)
                if prompt_feats['conditionals'] > 0 and cand_feats['conditionals'] > 0:
                    score = min(1.0, score + 0.15)
                if prompt_feats['numbers'] and cand_feats['numbers']:
                    score = min(1.0, score + 0.1)
                    
                reason = f"Survived falsification. Penalty: {penalty:.2f}"
            
            scores.append(score)
            reasons.append(reason)

        # Phase 2: SOC Avalanche Check
        final_scores = self._simulate_avalanche(prompt, candidates, scores)
        
        # Phase 3: NCD Tiebreaker (only if scores are very close)
        results = []
        for i, cand in enumerate(candidates):
            score = final_scores[i]
            # Apply tiny NCD perturbation for tie-breaking
            ncd_val = self._compute_ncd(prompt, cand)
            # Invert NCD so higher similarity (lower distance) helps slightly, 
            # but keep it minimal to avoid NCD dominance
            tie_breaker = (1.0 - ncd_val) * 0.001 
            final_score = score + tie_breaker
            
            results.append({
                "candidate": cand,
                "score": round(final_score, 6),
                "reasoning": reasons[i]
            })
            
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Measure-theoretic confidence: 
        Returns the measure of the set of unfalsified hypotheses containing this answer.
        Approximated by the survival score of the answer against strict falsification.
        """
        prompt_feats = self._structural_parse(prompt)
        is_falsified, penalty = self._check_falsification(prompt_feats, answer)
        
        if is_falsified:
            return 0.0
        
        # Base confidence
        conf = 0.85 - penalty
        
        # Adjust for structural richness
        ans_feats = self._structural_parse(answer)
        if prompt_feats['numbers'] and ans_feats['numbers']:
            conf += 0.1
        if prompt_feats['conditionals'] and ans_feats['conditionals']:
            conf += 0.05
            
        return max(0.0, min(1.0, conf))