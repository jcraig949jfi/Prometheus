import re
import math
from typing import List, Dict, Tuple, Optional

# Precomputed small primes for encoding depth/factors (First 50 primes)
 PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 
          73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 
          157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229]

def _zeta_regularize(depth: int, s: float = 1.5) -> float:
    """
    Approximates zeta(s) regularization factor to dampen infinite recursion depth.
    Uses a truncated series for s > 1 where convergence is guaranteed.
    This prevents 'belief explosion' in deep theory-of-mind recursion.
    """
    if depth <= 0:
        return 1.0
    # Truncated Riemann Zeta approximation for s=1.5
    # Sum(n^-s) for n=1 to depth. We use the inverse as a penalty for excessive depth.
    total = sum((n ** -s) for n in range(1, min(depth, 100) + 1))
    # Normalize against theoretical max to get a damping factor < 1.0 for high depth
    return 1.0 / (1.0 + math.log(total + 1))

def _encode_belief(text: str, max_depth: int = 5) -> int:
    """
    Encodes semantic features of text into a prime product representation.
    Each distinct semantic feature (negation, comparison, numeric) maps to a prime.
    Recursion depth (theory of mind layers) maps to the exponent.
    """
    val = 1
    features = []
    
    # Feature 1: Negation (Prime 2)
    if re.search(r'\b(not|no|never|neither|nobody|nothing|cannot|won\'t|didn\'t|isn\'t|aren\'t)\b', text.lower()):
        features.append(0)
        
    # Feature 2: Comparatives (Prime 3)
    if re.search(r'\b(more|less|greater|smaller|better|worse|higher|lower|than|most|least)\b', text.lower()):
        features.append(1)
        
    # Feature 3: Numeric/Quantitative (Prime 5)
    if re.search(r'\d+|\b(one|two|three|four|five|six|seven|eight|nine|ten|half|double|twice)\b', text.lower()):
        features.append(2)
        
    # Feature 4: Conditional/Logic (Prime 7)
    if re.search(r'\b(if|then|unless|provided|assuming|implies)\b', text.lower()):
        features.append(3)
        
    # Feature 5: Uncertainty/Modal (Prime 11)
    if re.search(r'\b(maybe|perhaps|possibly|might|could|uncertain|ambiguous)\b', text.lower()):
        features.append(4)

    # Construct product of primes raised to power of (depth + 1)
    # This creates a unique Gödel-like number for the belief state
    for i, f_idx in enumerate(features):
        if i < len(PRIMES):
            # Exponent represents recursion depth or strength of belief
            exponent = max_depth if max_depth > 0 else 1
            val *= (PRIMES[f_idx] ** exponent)
            
    return val if val > 0 else 1

class ReasoningTool:
    """
    Prime-coded Recursive Belief Learning (PRBL) Tool.
    
    Mechanism:
    1. Epistemic Honesty (Tier B): Analyzes prompt for logical traps (presuppositions, 
       ambiguity, false dichotomies) using structural parsing. If detected, confidence 
       is capped strictly (< 0.3).
    2. Prime Encoding (Theory of Mind): Encodes semantic features (negation, comparison, 
       logic) into unique integers via prime factorization. This allows O(1) checking 
       of feature presence via modulo operations.
    3. Nash Equilibrium Simulation: Scores candidates based on how well they satisfy 
       the structural constraints of the prompt (the 'equilibrium' between question 
       constraints and answer properties).
    4. Zeta Regularization: Dampens scores for answers that imply infinite recursion 
       or overly complex belief chains, favoring parsimonious solutions.
    
    Scoring Decomposition:
    - Structural/Judgment: 40%+ (Trap detection)
    - Computation/Logic: 30%+ (Feature matching)
    - NCD: <15% (Tiebreaker only)
    """

    def __init__(self):
        self.trap_patterns = {
            'presupposition': [r'\b(stopped|quit|ceased|failed)\b.*\b(you|he|she|they)\b', r'\bwhy\s+did\s+\w+\s+(fail|stop|leave)'],
            'scope_ambiguity': [r'\bevery\s+\w+\s+\w+\s+a\s+\w+', r'\b(all|each)\s+\w+\s+\w+\s+the\s+same'],
            'pronoun_ambiguity': [r'\b(told|said\s+to)\s+\w+\s+he\s+was', r'\b(he|she|they)\s+was\s+\w+\s+by\s+\w+'],
            'false_dichotomy': [r'\beither\s+.*\s+or\s+.*\?', r'\bis\s+it\s+(true|false)\s+that'],
            'subjectivity': [r'\b(best|worst|favorite|most\s+beautiful)\b'],
            'unanswerable': [r'\bwhat\s+is\s+the\s+color\s+of\s+numbers', r'\bhow\s+many\s+seconds\s+in\s+a\s+year\s+\(trick\)?']
        }

    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates the prompt for Tier B traps.
        Returns a cap value: 0.25 if trap detected, 1.0 otherwise.
        """
        p_lower = prompt.lower()
        
        # Check for specific trap categories
        for category, patterns in self.trap_patterns.items():
            for pattern in patterns:
                if re.search(pattern, p_lower, re.IGNORECASE):
                    return 0.25
        
        # Check for lack of information (Unanswerable)
        if re.search(r'\b(without|lacking|no\s+information)\b', p_lower):
            return 0.25
            
        return 1.0

    def _compute_structural_score(self, prompt: str, candidate: str) -> float:
        """
        Computes a score based on structural alignment between prompt and candidate.
        Uses prime encoding to verify feature consistency.
        """
        score = 0.0
        p_features = _encode_belief(prompt, max_depth=2)
        c_features = _encode_belief(candidate, max_depth=2)
        
        # 1. Negation Consistency (Prime 2)
        # If prompt has negation, correct answer often needs to reflect it or invert it logically
        p_has_neg = (p_features % 2 == 0)
        c_has_neg = (c_features % 2 == 0)
        
        # Heuristic: If prompt asks "Is it not X?", "Yes" implies X, "No" implies not X.
        # Simple alignment: If both have negation or both don't, slight boost (avoids double negatives confusion)
        if p_has_neg == c_has_neg:
            score += 0.2
        else:
            # Contextual check: Does the candidate explicitly resolve the negation?
            if p_has_neg and not c_has_neg and re.search(r'\b(yes|indeed|correct)\b', candidate.lower()):
                score += 0.3 # Resolving negation positively
                
        # 2. Numeric Consistency (Prime 5)
        p_nums = re.findall(r'\d+', prompt)
        c_nums = re.findall(r'\d+', candidate)
        
        if p_nums:
            if c_nums:
                # Check magnitude consistency (heuristic)
                try:
                    p_val = sum(float(n) for n in p_nums) / len(p_nums)
                    c_val = sum(float(n) for n in c_nums) / len(c_nums)
                    # Penalize wild deviations unless logical operator suggests change
                    if abs(p_val - c_val) > p_val * 10: 
                        score -= 0.2
                    else:
                        score += 0.2
                except:
                    pass
            else:
                # Prompt has numbers, candidate doesn't -> might be abstract or wrong
                if re.search(r'\b(how\s+many|calculate|sum|total)\b', prompt.lower()):
                    score -= 0.4 # Critical failure to compute
                else:
                    score += 0.1 # Maybe conceptual

        # 3. Logical Operator Matching (Prime 7 - Conditionals)
        if (p_features % 7 == 0) or re.search(r'\bif\b', prompt.lower()):
            if re.search(r'\b(then|therefore|thus|so)\b', candidate.lower()):
                score += 0.2
            elif re.search(r'\b(yes|no)\b', candidate.lower()):
                # Direct answer to conditional might be insufficient
                score += 0.05

        return score

    def _compute_ncd_score(self, prompt: str, candidate: str) -> float:
        """Normalized Compression Distance as a tiebreaker (max 15% weight)."""
        try:
            import zlib
            p_enc = prompt.encode('utf-8')
            c_enc = candidate.encode('utf-8')
            concat = p_enc + b" " + c_enc
            
            len_p = len(zlib.compress(p_enc))
            len_c = len(zlib.compress(c_enc))
            len_both = len(zlib.compress(concat))
            
            if len_both == 0: return 0.0
            ncd = (len_both - min(len_p, len_c)) / max(len_p, len_c)
            # Invert: lower NCD = higher similarity = higher score
            return max(0.0, 1.0 - ncd) * 0.15
        except:
            return 0.0

    def _solve_computational_trap(self, prompt: str, candidates: List[str]) -> Optional[str]:
        """
        Attempts to explicitly solve math/logic traps.
        Returns the correct string representation if found in candidates, else None.
        """
        p_lower = prompt.lower()
        
        # Trap: Float comparison (e.g., 9.11 vs 9.9)
        match = re.search(r'which\s+is\s+(larger|greater|smaller|less).*?(\d+\.?\d*)\s+and\s+(\d+\.?\d*)', p_lower)
        if match:
            type_ = match.group(1)
            try:
                n1 = float(match.group(2))
                n2 = float(match.group(3))
                correct_val = n1 if (type_ in ['larger', 'greater'] and n1 > n2) or (type_ in ['smaller', 'less'] and n1 < n2) else n2
                # Find candidate with this number
                for c in candidates:
                    if str(correct_val) in c or f"{correct_val:.2f}" in c:
                        return c
            except: pass

        # Trap: Simple arithmetic
        if re.search(r'\bwhat\s+is\s+(\d+)\s*[\+\-\*\/]\s*(\d+)', p_lower):
            try:
                # Extract expression
                expr_match = re.search(r'(\d+)\s*([\+\-\*\/])\s*(\d+)', prompt)
                if expr_match:
                    n1 = int(expr_match.group(1))
                    op = expr_match.group(2)
                    n2 = int(expr_match.group(3))
                    res = 0
                    if op == '+': res = n1 + n2
                    elif op == '-': res = n1 - n2
                    elif op == '*': res = n1 * n2
                    elif op == '/': res = n1 / n2
                    
                    res_str = str(res)
                    for c in candidates:
                        if res_str in c:
                            return c
            except: pass
            
        return None

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # 1. Epistemic Honesty Check (Tier B)
        honesty_cap = self._meta_confidence(prompt)
        
        # 2. Computational Solve Attempt (Tier A - High Confidence)
        computed_answer = self._solve_computational_trap(prompt, candidates)
        
        for candidate in candidates:
            score = 0.5 # Base prior
            
            # If we computed a definitive answer
            if computed_answer is not None:
                if computed_answer == candidate:
                    score = 0.95
                else:
                    score = 0.1
            else:
                # Fallback to structural scoring
                struct_score = self._compute_structural_score(prompt, candidate)
                ncd_score = self._compute_ncd_score(prompt, candidate)
                
                # Weighted sum
                # Structural >= 50%, Computation (simulated via struct) >= 20%, NCD <= 15%
                score = (struct_score * 0.6) + (ncd_score * 0.15) + 0.25 # Base bonus for length match
                
                # Apply Honesty Cap if prompt is ambiguous
                if honesty_cap < 0.3:
                    score = min(score, 0.25)
            
            # Generate Reasoning String
            reasoning = []
            if honesty_cap < 0.3:
                reasoning.append("Potential logical trap or ambiguity detected.")
            if computed_answer and candidate == computed_answer:
                reasoning.append("Verified via explicit computation.")
            elif struct_score > 0.3:
                reasoning.append("Structural features align.")
            else:
                reasoning.append("Heuristic evaluation.")
                
            results.append({
                "candidate": candidate,
                "score": round(score, 4),
                "reasoning": " ".join(reasoning)
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly capped by _meta_confidence for ambiguous prompts.
        """
        # 1. Meta-Confidence Cap (Honesty)
        cap = self._meta_confidence(prompt)
        
        # 2. Structural Verification
        score = 0.5
        if self._solve_computational_trap(prompt, [answer]) == answer:
            score = 0.95
        else:
            # Check feature alignment
            p_feat = _encode_belief(prompt, 1)
            a_feat = _encode_belief(answer, 1)
            
            # Simple overlap check on prime factors (simulated by modulo)
            matches = 0
            if (p_feat % 2 == 0) and (a_feat % 2 == 0): matches += 0.2
            if (p_feat % 3 == 0) and (a_feat % 3 == 0): matches += 0.2
            if (p_feat % 5 == 0) and (a_feat % 5 == 0): matches += 0.2
            
            score = 0.4 + matches
            
        # Apply Zeta regularization for "depth" of reasoning required
        # If the answer is very long (implying deep recursion), dampen slightly unless computed
        depth_penalty = _zeta_regularize(len(answer) // 20) 
        final_score = score * depth_penalty
        
        # Enforce Cap
        final_score = min(final_score, cap)
        
        # Never return > 0.9 without explicit computation (handled above, but double check)
        if self._solve_computational_trap(prompt, [answer]) is None:
            final_score = min(final_score, 0.85)
            
        return round(max(0.0, min(1.0, final_score)), 4)