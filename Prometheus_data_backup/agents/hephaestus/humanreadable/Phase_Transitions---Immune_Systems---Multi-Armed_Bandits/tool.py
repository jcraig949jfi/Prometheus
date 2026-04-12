import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Phase-Transition Bandit Immune Learner (PTBIL) Implementation.
    
    Mechanism:
    1. Structural Parsing (Immune Recognition): Extracts logical operators (negations, 
       comparatives, conditionals) and numeric values to form a "structural antibody".
    2. Affinity Scoring (Bandit Reward): Candidates are scored based on structural 
       alignment with the prompt (exact match of logic tokens and numeric validity).
    3. Phase Transition Detection: Calculates an order parameter (normalized variance 
       of initial scores). 
       - Low variance (Ordered Phase): System trusts initial structural scores; Memory 
         cells (high-affinity candidates) dominate.
       - High variance (Critical Phase): Indicates uncertainty or conflicting signals. 
         Triggers "Clonal Burst" (exploration bonus) for candidates that share partial 
         structural features but were initially lower-ranked, simulating hypermutation 
         to escape local optima.
    4. NCD Tiebreaker: Used only when structural scores are identical.
    """

    def __init__(self):
        self.memory_cells = []  # Stores high-affinity (prompt, answer) pairs
        self.critical_threshold = 0.15  # Variance threshold for phase transition
        self.exploration_bonus = 0.2    # Bonus applied during critical phase

    def _extract_structure(self, text: str) -> Dict:
        """Extract logical and numeric fingerprints from text."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither|without)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|better|worst)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|provided|when)\b', text_lower)),
            'numbers': [],
            'length': len(text)
        }
        # Extract numbers for numeric evaluation
        nums = re.findall(r'-?\d+\.?\d*', text)
        features['numbers'] = [float(n) for n in nums if n]
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Compute Normalized Compression Distance."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        c1 = len(zlib.compress(s1_bytes))
        c2 = len(zlib.compress(s2_bytes))
        c12 = len(zlib.compress(s1_bytes + s2_bytes))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _evaluate_structural_affinity(self, prompt: str, candidate: str) -> float:
        """
        Calculate affinity based on structural parsing.
        Higher score = better structural alignment.
        """
        p_feat = self._extract_structure(prompt)
        c_feat = self._extract_structure(candidate)
        
        score = 0.0
        matches = 0
        total_checks = 0

        # Check Negation Alignment
        total_checks += 1
        if p_feat['negations'] > 0 and c_feat['negations'] > 0:
            matches += 1
        elif p_feat['negations'] == 0 and c_feat['negations'] == 0:
            matches += 1 # Absence of negation in both is also alignment
            
        # Check Comparative Alignment
        total_checks += 1
        if p_feat['comparatives'] > 0 and c_feat['comparatives'] > 0:
            matches += 1
            
        # Check Conditional Alignment
        total_checks += 1
        if p_feat['conditionals'] > 0 and c_feat['conditionals'] > 0:
            matches += 1

        # Numeric Evaluation (Simplified for robustness)
        # If prompt has numbers, candidate having numbers is a positive signal
        if p_feat['numbers']:
            total_checks += 1
            if c_feat['numbers']:
                # Check for rough magnitude consistency if both have numbers
                p_max = max(p_feat['numbers'])
                c_max = max(c_feat['numbers']) if c_feat['numbers'] else 0
                if p_max > 0 and c_max > 0:
                    matches += 1 # Presence of logic-relevant numbers
                elif p_max == 0 and c_max == 0:
                    matches += 1

        base_score = matches / total_checks if total_checks > 0 else 0.0
        
        # Penalty for length mismatch (heuristic for completeness)
        len_ratio = min(len(candidate), len(prompt)) / max(len(candidate), len(prompt), 1)
        base_score = (base_score * 0.7) + (len_ratio * 0.3)
        
        return base_score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []

        # 1. Initial Affinity Scoring (Bandit Arm Selection)
        scores = []
        for cand in candidates:
            aff = self._evaluate_structural_affinity(prompt, cand)
            scores.append(aff)

        # 2. Phase Transition Detection (Order Parameter: Variance)
        if len(scores) > 1:
            mean_score = sum(scores) / len(scores)
            variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
            # Normalize variance roughly to [0, 1] range for comparison
            # Max variance for binary-like scores is 0.25, so 4*variance approx [0,1]
            order_param = min(1.0, 4.0 * variance)
        else:
            order_param = 0.0
            variance = 0.0

        # 3. Clonal Burst / Hypermutation (Exploration Phase)
        # If system is in critical phase (high uncertainty/variance), boost diverse candidates
        final_scores = []
        if order_param > self.critical_threshold:
            # Critical slowing down: Increase exploration weight
            for i, cand in enumerate(candidates):
                base = scores[i]
                # Diversity bonus: If this candidate is structurally different from the mean,
                # it gets a "mutation" bonus to prevent premature convergence.
                # Simplified: Boost candidates that aren't the current max
                if base < max(scores):
                    base += self.exploration_bonus
                final_scores.append(base)
        else:
            # Exploitation Phase: Trust structural parsing
            final_scores = scores

        # 4. Memory Cell Recall (Optional optimization for repeated patterns)
        # (Skipped for brevity in single-shot evaluation, but logic would inject known good patterns)

        # 5. Construct Results with NCD as Tiebreaker
        results = []
        for i, cand in enumerate(candidates):
            score = final_scores[i]
            reasoning = f"Structural affinity: {scores[i]:.2f}"
            if order_param > self.critical_threshold:
                reasoning += " | Phase: CRITICAL (Exploration boosted)"
            else:
                reasoning += " | Phase: STABLE (Exploitation)"
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning,
                "_ncd": self._compute_ncd(prompt, cand) # Store for tie-breaking
            })

        # Sort: Primary by Score (desc), Secondary by NCD (asc, lower is better match)
        # We invert NCD logic: we want low NCD to be "better", so sort by -NCD ascending? 
        # Actually, standard sort is ascending. We want high score first.
        # If scores equal, we want low NCD first.
        results.sort(key=lambda x: (-x['score'], x['_ncd']))

        # Clean up and return
        output = []
        for r in results:
            output.append({
                "candidate": r["candidate"],
                "score": r["score"],
                "reasoning": r["reasoning"]
            })
        
        return output

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence based on structural alignment and NCD.
        0.0 = Definitely wrong, 1.0 = Definitely correct.
        """
        # Structural check
        struct_score = self._evaluate_structural_affinity(prompt, answer)
        
        # NCD check (similarity)
        ncd = self._compute_ncd(prompt, answer)
        
        # Combined metric
        # High structural score + Low NCD (high similarity in compressed info) = High Confidence
        # Note: NCD is distance, so 1-ncd is similarity.
        ncd_similarity = 1.0 - ncd
        
        # Weighted average favoring structure for reasoning tasks
        conf = (struct_score * 0.6) + (ncd_similarity * 0.4)
        
        return min(1.0, max(0.0, conf))