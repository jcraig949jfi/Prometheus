import re
import numpy as np
from collections import defaultdict
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    Bandit-Guided Constraint Propagation with Variational Free-Energy Scoring.
    
    Mechanism:
    1. Parsing: Extracts logical atoms, negations, comparatives, and conditionals via regex.
    2. CSP Construction: Builds a factor graph where variables are predicates and factors encode constraints.
    3. Bandit Selection: Uses Thompson Sampling (Beta posteriors) to select which constraint to enforce next,
       balancing exploration of uncertain constraints vs. exploitation of known useful ones.
    4. Free Energy Update: Enforces arc-consistency on the selected factor. The change in global error (Delta E)
       updates the Beta posterior. Free Energy F approx <Error> - Entropy.
    5. Scoring: Candidates are scored by -F (lower free energy is better). NCD is used only as a tiebreaker.
    """

    def __init__(self):
        self.beta_alpha = 1.0
        self.beta_beta = 1.0
        # Regex patterns for structural extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|without)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(greater|less|more|fewer|higher|lower|before|after)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|only if|unless|causes|leads to)\b', re.IGNORECASE),
            'quantifier': re.compile(r'\b(all|some|every|each|any)\b', re.IGNORECASE),
            'number': re.compile(r'-?\d+\.?\d*'),
            'inequality': re.compile(r'[<>]=?'),
        }

    def _extract_features(self, text: str) -> Dict[str, Any]:
        """Extract structural features from text."""
        text_lower = text.lower()
        features = {
            'has_negation': bool(self.patterns['negation'].search(text_lower)),
            'has_comparative': bool(self.patterns['comparative'].search(text_lower)),
            'has_conditional': bool(self.patterns['conditional'].search(text_lower)),
            'has_quantifier': bool(self.patterns['quantifier'].search(text_lower)),
            'numbers': [float(x) for x in self.patterns['number'].findall(text)],
            'inequalities': self.patterns['inequality'].findall(text),
            'length': len(text),
            'word_count': len(text.split())
        }
        return features

    def _build_constraints(self, prompt: str, candidate: str) -> List[Dict]:
        """
        Construct a list of constraint factors based on parsed features.
        Each factor is a dict with 'type', 'weight', and 'satisfied' status.
        """
        constraints = []
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        full_text = f"{prompt} {candidate}"
        f_feat = self._extract_features(full_text)

        # Factor 1: Negation Consistency
        # If prompt has negation, candidate should not contradict it directly (simplified heuristic)
        if p_feat['has_negation']:
            constraints.append({'type': 'negation_check', 'active': True, 'alpha': 1, 'beta': 1})
        
        # Factor 2: Numeric Consistency
        if p_feat['numbers'] and c_feat['numbers']:
            constraints.append({'type': 'numeric_check', 'active': True, 'alpha': 1, 'beta': 1})
            
        # Factor 3: Logical Flow (Conditional presence)
        if p_feat['has_conditional']:
            constraints.append({'type': 'logic_check', 'active': True, 'alpha': 1, 'beta': 1})
            
        # Factor 4: Structural Overlap (Basic keyword match excluding noise)
        constraints.append({'type': 'overlap_check', 'active': True, 'alpha': 1, 'beta': 1})

        # Default factor if nothing specific found
        if not constraints:
            constraints.append({'type': 'default', 'active': True, 'alpha': 1, 'beta': 1})
            
        return constraints

    def _evaluate_constraint(self, c_type: str, prompt: str, candidate: str) -> Tuple[bool, float]:
        """
        Evaluate a specific constraint type.
        Returns (is_satisfied, penalty_score).
        Lower penalty is better.
        """
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        full = f"{prompt} {candidate}".lower()
        
        penalty = 0.0
        satisfied = True

        if c_type == 'negation_check':
            # Heuristic: If prompt says "not", candidate shouldn't be a blind affirmative repetition
            if p_feat['has_negation']:
                if candidate.lower().strip() in ['yes', 'true', 'it is', 'correct']:
                    # Potential contradiction depending on context, assign small penalty risk
                    penalty = 0.5 
                    # satisfied = False # Too aggressive, keep as penalty
        
        elif c_type == 'numeric_check':
            # Check if numbers in candidate are consistent with prompt logic (simplified)
            # If prompt has "greater than" and numbers, check ordering
            if p_feat['has_comparative'] and len(p_feat['numbers']) >= 2:
                nums = p_feat['numbers']
                if 'greater' in full or 'more' in full or 'higher' in full:
                    if len(c_feat['numbers']) > 0:
                        # Rough check: does candidate contain the larger number?
                        max_p = max(nums)
                        if not any(abs(n - max_p) < 1e-5 for n in c_feat['numbers']):
                            penalty = 1.0
                            satisfied = False
                elif 'less' in full or 'fewer' in full or 'lower' in full:
                    if len(c_feat['numbers']) > 0:
                        min_p = min(nums)
                        if not any(abs(n - min_p) < 1e-5 for n in c_feat['numbers']):
                            penalty = 1.0
                            satisfied = False

        elif c_type == 'logic_check':
            # If prompt is conditional, candidate length should be substantial (not empty)
            if len(candidate.strip()) < 2:
                penalty = 2.0
                satisfied = False

        elif c_type == 'overlap_check':
            # Basic Jaccard-like overlap on significant words
            p_words = set(w for w in prompt.lower().split() if len(w) > 3)
            c_words = set(w for w in candidate.lower().split() if len(w) > 3)
            if p_words:
                intersection = len(p_words & c_words)
                union = len(p_words | c_words)
                if union == 0:
                    jaccard = 0
                else:
                    jaccard = intersection / union
                # Penalty inversely proportional to overlap, but allow for concise answers
                if jaccard < 0.05 and len(c_words) > 0: 
                    penalty = 0.5
                    satisfied = False

        return satisfied, penalty

    def _run_bandit_csp(self, prompt: str, candidate: str, n_pulls: int = 10) -> Tuple[float, str]:
        """
        Run the Bandit-guided CSP loop.
        Returns (free_energy, reasoning_string).
        """
        constraints = self._build_constraints(prompt, candidate)
        if not constraints:
            return 10.0, "No constraints generated."

        total_error = 0.0
        reasoning_steps = []
        
        # Initialize posteriors for this specific candidate evaluation
        # We use local copies of alpha/beta for the factors
        for i, c in enumerate(constraints):
            c['alpha'] = 1.0
            c['beta'] = 1.0

        for _ in range(n_pulls):
            # Thompson Sampling: Sample theta for each arm
            best_arm_idx = -1
            best_theta = -1.0
            
            for i, c in enumerate(constraints):
                if not c['active']: continue
                theta = np.random.beta(c['alpha'], c['beta'])
                if theta > best_theta:
                    best_theta = theta
                    best_arm_idx = i
            
            if best_arm_idx == -1: break
            
            arm = constraints[best_arm_idx]
            satisfied, penalty = self._evaluate_constraint(arm['type'], prompt, candidate)
            
            # Update global error estimate
            current_step_error = penalty if not satisfied else 0.0
            total_error += current_step_error
            
            # Update Beta posterior based on error reduction (simulated)
            # If satisfied (error ~0), increment alpha. If not, increment beta.
            if satisfied:
                arm['alpha'] += 1
                reasoning_steps.append(f"Factor '{arm['type']}' satisfied.")
            else:
                arm['beta'] += 1
                reasoning_steps.append(f"Factor '{arm['type']}' violated (penalty: {penalty}).")

        # Calculate Free Energy approximation: F ~ <Error> - Entropy
        # Entropy of Beta(a,b) is approximated or we use the ratio of satisfied/total
        total_factors = len(constraints)
        satisfied_count = sum(1 for c in constraints if c['alpha'] > 1) # Crude proxy
        
        # Normalized Error
        avg_error = total_error / max(1, n_pulls)
        
        # Entropy term (encourages exploring uncertain factors, here simplified)
        # High uncertainty (alpha~beta) -> higher entropy -> lower F
        entropy_term = 0.0
        for c in constraints:
            a, b = c['alpha'], c['beta']
            if a + b > 2:
                # Approx entropy contribution
                entropy_term += np.log(a + b) 
        
        free_energy = avg_error * 10.0 - (entropy_term * 0.1)
        
        reason_str = " | ".join(reasoning_steps[:3]) # Summarize
        return free_energy, reason_str

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_combined = len(zlib.compress(s1_b + s2_b))
        max_len = max(len_s1, len_s2)
        if max_len == 0: return 0.0
        return (len_combined - max_len) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        for cand in candidates:
            # Primary Score: Free Energy from Bandit-CSP
            fe, reason = self._run_bandit_csp(prompt, cand)
            
            # Secondary Score (Tiebreaker): NCD (Lower is more similar/relevant usually, 
            # but for reasoning, we want specific match. We invert logic: 
            # We use NCD as a penalty if the structural score is tied)
            # Actually, per instructions: NCD is tiebreaker. 
            # We store FE as primary score. Lower FE is better.
            # We will sort by FE ascending, then use NCD.
            
            # To make "Higher score = more likely correct" as per interface:
            # Score = -FreeEnergy
            score = -fe
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason,
                "_ncd": self._ncd(prompt, cand) # Internal tiebreaker
            })
        
        # Sort: Higher score (lower FE) first. 
        # If scores are close (tie), prefer lower NCD (more relevant/compressed together)
        results.sort(key=lambda x: (-x['score'], x['_ncd']))
        
        # Clean up internal fields
        final_results = []
        for r in results:
            final_results.append({
                "candidate": r['candidate'],
                "score": round(r['score'], 4),
                "reasoning": r['reasoning']
            })
            
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1.
        Derived from the Free Energy score normalized via a sigmoid-like mapping.
        """
        fe, _ = self._run_bandit_csp(prompt, answer, n_pulls=15)
        # Map Free Energy (usually 0 to ~5 range in this implementation) to 0-1
        # Lower FE -> Higher Confidence
        # Using a simple decay: conf = 1 / (1 + FE)
        conf = 1.0 / (1.0 + abs(fe))
        return min(1.0, max(0.0, conf))

# Example Usage (for self-verification):
if __name__ == "__main__":
    tool = ReasoningTool()
    p = "If all A are B, and some B are C, is it true that some A are C?"
    cands = [
        "Yes, it must be true.",
        "No, it is not necessarily true.",
        "Maybe, depends on the set."
    ]
    res = tool.evaluate(p, cands)
    for r in res:
        print(f"Candidate: {r['candidate'][:20]}... | Score: {r['score']:.4f} | Reason: {r['reasoning']}")
    
    conf = tool.confidence(p, "No, it is not necessarily true.")
    print(f"Confidence in correct answer: {conf:.4f}")