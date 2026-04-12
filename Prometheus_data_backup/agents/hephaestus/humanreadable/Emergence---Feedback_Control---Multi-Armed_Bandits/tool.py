import re
import numpy as np
from zlib import compress

class ReasoningTool:
    """
    Emergent Feedback Bandit Reasoning Tool.
    
    Mechanism:
    1. Structural Parsing: Extracts logical features (negations, comparatives, conditionals, causals, numbers).
    2. Emergent Consistency: Builds a constraint graph and computes a consistency score 'c' via propagation.
       This 'c' is the emergent property arising from feature interactions.
    3. Feedback Control (PID): Updates the estimated correctness (mu) of each candidate arm using a 
       discrete PID controller on the error between target consistency (1.0) and observed 'c'.
    4. Multi-Armed Bandit (UCB): Selects which candidate to refine/evaluate next based on Upper Confidence Bound,
       balancing exploration (uncertainty) and exploitation (high mu).
    5. Epistemic Honesty: Meta-checks for ambiguity/presupposition cap confidence scores.
    """

    # Regex patterns for structural features
    PATTERNS = {
        'negation': re.compile(r'\b(not|no|never|without|neither)\b', re.IGNORECASE),
        'comparative': re.compile(r'\b(more|less|greater|lesser|higher|lower|better|worse|than|as\s+\w+\s+as)\b', re.IGNORECASE),
        'conditional': re.compile(r'\b(if|unless|provided\s+that|when|then|else)\b', re.IGNORECASE),
        'causal': re.compile(r'\b(because|leads\s+to|results\s+in|due\s+to|causes|since)\b', re.IGNORECASE),
        'numeric': re.compile(r'-?\d+(?:\.\d+)?(?:\s*(?:%|units|kg|m|s))?\b'),
        'ordering': re.compile(r'\b(before|after|first|last|precede|follow|greater\s+than|less\s+than)\b', re.IGNORECASE),
        'conjunction': re.compile(r'\b(and|or|either|nor|but)\b', re.IGNORECASE)
    }
    
    # Presupposition/Ambiguity triggers for Tier B
    TRAPS = {
        'presupposition': re.compile(r'\b(have\s+you\s+stopped|have\s+you\s+quit|why\s+did\s+\w+\s+(fail|stop|die))\b', re.IGNORECASE),
        'scope_ambiguity': re.compile(r'\b(every\s+\w+\s+did\s+a\s+\w+)\b', re.IGNORECASE), # Simplified heuristic
        'pronoun_ambiguity': re.compile(r'\b(\w+\s+told\s+\w+\s+he)\b', re.IGNORECASE),
        'false_dichotomy': re.compile(r'\b(either\s+\w+\s+or\s+\w+)\b', re.IGNORECASE),
        'subjectivity': re.compile(r'\b(best|worst|favorite|most\s+beautiful)\b', re.IGNORECASE)
    }

    def __init__(self):
        # PID Constants
        self.Kp = 0.5
        self.Ki = 0.1
        self.Kd = 0.1
        self.alpha = 2.0  # UCB exploration coefficient
        self.lambda_shrink = 0.05
        self.epsilon = 1e-4
        
        # State storage for arms (candidates)
        # Structure: {candidate_string: {'mu': float, 'sigma2': float, 'n': int, 'I': float, 'D': float, 'e_prev': float}}
        self.arms = {}
        self.total_evals = 0

    def _extract_features(self, text: str) -> dict:
        """Extract structural features and numeric values."""
        features = {
            'negations': len(self.PATTERNS['negation'].findall(text)),
            'comparatives': len(self.PATTERNS['comparative'].findall(text)),
            'conditionals': len(self.PATTERNS['conditional'].findall(text)),
            'causals': len(self.PATTERNS['causal'].findall(text)),
            'orderings': len(self.PATTERNS['ordering'].findall(text)),
            'conjunctions': len(self.PATTERNS['conjunction'].findall(text)),
            'numbers': []
        }
        
        # Extract and parse numbers
        num_strs = self.PATTERNS['numeric'].findall(text)
        for s in num_strs:
            try:
                # Clean percentage
                val = float(s.replace('%', '').replace('units', '').replace('kg', '').replace('m', '').replace('s', ''))
                if '%' in s:
                    val /= 100.0
                features['numbers'].append(val)
            except ValueError:
                pass
        return features

    def _build_constraint_graph(self, prompt: str, candidate: str) -> float:
        """
        Simulate constraint propagation.
        Returns a consistency score c in [0, 1].
        1.0 = No contradictions, 0.0 = Hard conflict.
        """
        full_text = f"{prompt} {candidate}"
        feats = self._extract_features(full_text)
        
        # Base consistency starts at 1.0
        c = 1.0
        
        # Heuristic 1: Numeric Contradiction Detection
        # If candidate has numbers that contradict prompt logic (simplified)
        # We check if the candidate introduces numbers not in prompt without calculation context
        prompt_nums = self._extract_features(prompt)['numbers']
        cand_nums = self._extract_features(candidate)['numbers']
        
        if cand_nums and not prompt_nums:
            # Penalty for introducing random numbers if prompt had none (unless it's a math problem)
            if "calculate" not in prompt.lower() and "sum" not in prompt.lower():
                c -= 0.2 * len(cand_nums)
        
        # Heuristic 2: Negation/Causal Conflict
        # If prompt has strong negation and candidate asserts the negated thing directly
        if feats['negations'] > 0 and feats['causals'] > 0:
            # Simple penalty for complex negative causal chains which are error-prone
            c -= 0.1
            
        # Heuristic 3: Logical Flow (Mock Transitive Closure)
        # If conditionals exist, ensure structure implies a conclusion. 
        # Here we just penalize high conditional density without clear numbers (ambiguous)
        if feats['conditionals'] > 2 and len(feats['numbers']) == 0:
            c -= 0.15

        # Heuristic 4: Direct String Contradiction (Simple)
        # If candidate contains "not" + word from prompt that was affirmative
        prompt_words = set(re.findall(r'\b\w+\b', prompt.lower()))
        cand_words = set(re.findall(r'\b\w+\b', candidate.lower()))
        
        # Check for "not X" where X is in prompt and prompt didn't have "not"
        prompt_has_not = bool(self.PATTERNS['negation'].search(prompt))
        if not prompt_has_not:
            for word in cand_words:
                if f"not {word}" in candidate.lower() and word in prompt_words and len(word) > 3:
                    c -= 0.3 # Strong penalty for negating a prompt premise
        
        return max(0.0, min(1.0, c))

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(compress(s1_b))
        len_s2 = len(compress(s2_b))
        len_both = len(compress(s1_b + s2_b))
        
        if len_both == 0: return 0.0
        return (len_both - min(len_s1, len_s2)) / max(len_s1, len_s2, 1)

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Check: Detect ambiguity, presupposition, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # Check traps
        if self.TRAPS['presupposition'].search(p_lower):
            return 0.2
        if self.TRAPS['scope_ambiguity'].search(p_lower):
            return 0.4 # Moderate uncertainty
        if self.TRAPS['pronoun_ambiguity'].search(p_lower) and "who" in p_lower:
            return 0.2
        if self.TRAPS['false_dichotomy'].search(p_lower):
            return 0.3
        if self.TRAPS['subjectivity'].search(p_lower):
            return 0.2
            
        # Check for insufficient info markers
        if "insufficient information" in p_lower or "cannot be determined" in p_lower:
            return 0.1
            
        return 1.0

    def _update_arm(self, candidate: str, c: float):
        """Update arm statistics using PID control."""
        if candidate not in self.arms:
            self.arms[candidate] = {
                'mu': 0.5,       # Initial estimate
                'sigma2': 1.0,   # High initial uncertainty
                'n': 0,
                'I': 0.0,        # Integral term
                'D': 0.0,        # Derivative term
                'e_prev': 0.0
            }
        
        arm = self.arms[candidate]
        arm['n'] += 1
        self.total_evals += 1
        
        # PID Control
        target = 1.0
        e = target - c
        arm['I'] += e
        D = e - arm['e_prev']
        arm['D'] = D
        arm['e_prev'] = e
        
        # Update Mu (Correctness Estimate)
        # mu_new = mu_old + Kp*e + Ki*I + Kd*D
        delta = self.Kp * e + self.Ki * arm['I'] + self.Kd * D
        arm['mu'] += delta
        
        # Update Sigma2 (Uncertainty) - shrinks with consistent feedback
        # If error is small, uncertainty shrinks. If error is large, uncertainty stays high or grows slightly.
        if abs(e) < 0.1:
            arm['sigma2'] = max(arm['sigma2'] - self.lambda_shrink, self.epsilon)
        else:
            arm['sigma2'] = min(arm['sigma2'] + 0.05, 1.0) # Cap uncertainty
            
        # Clamp mu
        arm['mu'] = max(0.0, min(1.0, arm['mu']))

    def _get_ucb(self, candidate: str) -> float:
        """Calculate Upper Confidence Bound."""
        arm = self.arms[candidate]
        if arm['n'] == 0:
            return float('inf')
        
        # UCB1 formula variant
        exploration = self.alpha * np.sqrt((arm['sigma2'] * np.log(self.total_evals + 1)) / arm['n'])
        return arm['mu'] + exploration

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
            
        # Initialize arms if new candidates
        for cand in candidates:
            if cand not in self.arms:
                self.arms[cand] = {
                    'mu': 0.5, 'sigma2': 1.0, 'n': 0, 'I': 0.0, 'D': 0.0, 'e_prev': 0.0
                }

        # Simulation Budget (Bandit Iterations)
        # We simulate T rounds of evaluating the most promising candidate
        T = min(30, len(candidates) * 3) 
        
        for _ in range(T):
            # Select arm with highest UCB
            best_cand = None
            best_ucb = -1
            for cand in candidates:
                ucb = self._get_ucb(cand)
                if ucb > best_ucb:
                    best_ucb = ucb
                    best_cand = cand
            
            if best_cand is None:
                break
                
            # Evaluate consistency (Emergence)
            c_score = self._build_constraint_graph(prompt, best_cand)
            
            # Feedback Update (PID)
            self._update_arm(best_cand, c_score)

        # Final Scoring
        results = []
        meta_cap = self._meta_confidence(prompt)
        
        for cand in candidates:
            arm = self.arms.get(cand, {'mu': 0.5})
            base_score = arm['mu']
            
            # NCD Tiebreaker (max 15% influence)
            # Compare candidate to prompt. Lower NCD = more relevant (usually).
            # But we use it only if structural score is ambiguous or to break ties.
            ncd_val = self._compute_ncd(prompt, cand)
            # Normalize NCD to a relevance score (inverse)
            ncd_relevance = 1.0 - ncd_val
            
            # Weighted combination: Structural (85%) + NCD (15%)
            # Only apply NCD if structural signal is weak or for tie-breaking logic
            final_score = 0.85 * base_score + 0.15 * ncd_relevance
            
            # Apply Epistemic Cap
            if final_score > meta_cap:
                final_score = meta_cap
                
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Structural consistency: {base_score:.2f}, NCD relevance: {ncd_relevance:.2f}, Meta-cap: {meta_cap:.2f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1.
        Strictly capped by meta-analysis of the prompt for ambiguity.
        """
        # 1. Meta Check (Tier B)
        cap = self._meta_confidence(prompt)
        if cap < 0.3:
            return cap

        # 2. Structural Evaluation
        c_score = self._build_constraint_graph(prompt, answer)
        
        # 3. Simulate a quick update to get a refined mu
        # We create a temporary arm state for this specific pair if not exists
        temp_key = f"{prompt}__{answer}"
        if temp_key not in self.arms:
             # Quick initialization
             self.arms[temp_key] = {'mu': 0.5, 'sigma2': 1.0, 'n': 0, 'I': 0.0, 'D': 0.0, 'e_prev': 0.0}
        
        # Run one step of PID to see where it settles roughly
        self._update_arm(temp_key, c_score)
        mu = self.arms[temp_key]['mu']
        
        # 4. Final Confidence Calculation
        # Confidence is high only if:
        # a) Meta check passed (cap is high)
        # b) Structural consistency is high
        # c) Uncertainty is low (implied by high n or consistent updates)
        
        raw_conf = mu * c_score # Combine estimate with immediate consistency
        
        # Hard cap based on meta-analysis
        final_conf = min(raw_conf, cap)
        
        # Never return > 0.9 unless computation was definitive (simulated by high consistency)
        if c_score < 0.95:
            final_conf = min(final_conf, 0.85)
            
        return float(max(0.0, min(1.0, final_conf)))