import re
import math
import zlib
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Thermodynamic-Bandit Adaptive Scorer (TBAS)
    
    Mechanism:
    1. Feature Extraction: Parses candidates for logical structures (negations, comparatives, etc.).
    2. Energy (E): Calculates constraint violations based on prompt logic vs candidate features.
    3. Entropy (S): Measures uncertainty in violated constraints.
    4. Adaptive Control: Updates feature weights via gradient descent on violations.
    5. Bandit Selection: Uses UCB to explore candidates minimizing Free Energy (F = E - TS).
    6. Epistemic Honesty: Caps confidence if prompt contains ambiguity traps (Tier B).
    """
    
    # Regex patterns for feature extraction
    PATTERNS = {
        'negation': re.compile(r'\b(not|no|never|neither|nor)\b', re.IGNORECASE),
        'comparative': re.compile(r'\b(more than|less than|greater than|smaller than|>\|<)\b', re.IGNORECASE),
        'conditional': re.compile(r'\b(if|then|unless|provided that)\b', re.IGNORECASE),
        'numeric': re.compile(r'\b\d+(\.\d+)?\b'),
        'causal': re.compile(r'\b(because|due to|leads to|causes|therefore)\b', re.IGNORECASE),
        'ordering': re.compile(r'\b(before|after|first|last|precedes|follows)\b', re.IGNORECASE)
    }
    
    # Tier B Trap Patterns
    TRAPS = {
        'presupposition': re.compile(r'\b(have you stopped|did you stop|why did|why does|when did)\b', re.IGNORECASE),
        'false_dichotomy': re.compile(r'\b(either .+ or | is it .+ or .+\?)', re.IGNORECASE),
        'subjectivity': re.compile(r'\b(best|worst|favorite|opinion|believe)\b', re.IGNORECASE),
        'pronoun_ambiguity': re.compile(r'\b(he|she|they|him|her)\b.*\bwho\b', re.IGNORECASE),
        'unanswerable': re.compile(r'\b(cannot be determined|insufficient information)\b', re.IGNORECASE)
    }

    def __init__(self):
        self.d = len(self.PATTERNS)
        self.w = np.zeros(self.d)  # Adaptive weights
        self.alpha = 0.1
        self.beta = 0.01
        self.t_updates = 1
        self.feature_names = list(self.PATTERNS.keys())

    def _extract_features(self, text: str) -> np.ndarray:
        """Extract binary feature vector from text."""
        vec = np.zeros(self.d)
        for i, key in enumerate(self.feature_names):
            if self.PATTERNS[key].search(text):
                vec[i] = 1.0
        return vec

    def _extract_constraints(self, prompt: str) -> List[str]:
        """Extract logical constraints from prompt (simplified for regex-based approach)."""
        constraints = []
        # Detect comparative constraints
        if re.search(r'\b(must|should|only if|requires)\b', prompt, re.IGNORECASE):
            constraints.append('mandatory')
        if re.search(r'\b(not|no|never)\b.*\b(must|should)\b', prompt, re.IGNORECASE):
            constraints.append('prohibition')
        if re.search(r'\d+\s*<\s*\d+|\d+\s*>\s*\d+|less than|greater than', prompt, re.IGNORECASE):
            constraints.append('numeric_order')
        if re.search(r'\bif\b', prompt, re.IGNORECASE):
            constraints.append('conditional_logic')
        return constraints if constraints else ['default']

    def _check_violation(self, constraint: str, features: np.ndarray, candidate: str) -> int:
        """Return 1 if constraint is violated, 0 otherwise."""
        # Map constraints to feature indices for simple logical checks
        # This is a heuristic approximation of logical consistency
        idx_neg = self.feature_names.index('negation')
        idx_num = self.feature_names.index('numeric')
        idx_comp = self.feature_names.index('comparative')
        
        if constraint == 'mandatory':
            # If prompt requires something, candidate lacking strong features might violate
            if np.sum(features) == 0: return 1
        elif constraint == 'prohibition':
            # If prompt prohibits, and candidate has high activity without negation
            if features[idx_neg] == 0 and np.sum(features) > 2: return 1
        elif constraint == 'numeric_order':
            # Heuristic: If prompt has numbers, candidate should too or explain absence
            if features[idx_num] == 0 and not re.search(r'\b(no|none|zero)\b', candidate, re.IGNORECASE):
                 # Only flag if prompt actually had numbers (checked in extraction)
                 return 1 
        elif constraint == 'conditional_logic':
            # If prompt is conditional, candidate lacking conditional markers might be weak
            idx_cond = self.feature_names.index('conditional')
            if features[idx_cond] == 0 and features[idx_neg] == 0:
                return 1
                
        return 0

    def _calculate_energy(self, prompt: str, candidate: str, features: np.ndarray) -> float:
        """Calculate Energy E (sum of violated constraints)."""
        constraints = self._extract_constraints(prompt)
        violations = 0
        for c in constraints:
            violations += self._check_violation(c, features, candidate)
        return float(violations)

    def _calculate_entropy(self, violations_count: int) -> float:
        """Calculate Entropy S = log(violations + 1)."""
        return math.log(violations_count + 1)

    def _update_weights(self, features: np.ndarray, violation_score: float):
        """Adaptive control: update weights to minimize future violations."""
        gradient = violation_score * features
        eta = self.alpha / (1.0 + self.beta * self.t_updates)
        self.w -= eta * gradient  # Move against gradient of violation
        self.t_updates += 1

    def _meta_confidence(self, prompt: str) -> float:
        """Check for Tier B traps. Returns cap value (low if trap detected)."""
        p_lower = prompt.lower()
        
        # 1. Presupposition
        if self.TRAPS['presupposition'].search(prompt):
            return 0.2
        # 2. False Dichotomy
        if self.TRAPS['false_dichotomy'].search(prompt):
            return 0.3
        # 3. Subjectivity
        if self.TRAPS['subjectivity'].search(prompt):
            return 0.4
        # 4. Pronoun Ambiguity (simplified)
        if self.TRAPS['pronoun_ambiguity'].search(prompt) and 'who' in p_lower:
            return 0.3
            
        return 1.0

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance heuristic."""
        z = zlib.compress
        len1, len2 = len(s1), len(s2)
        if len1 == 0 or len2 == 0: return 1.0
        concat = s1 + s2
        c1, c2, c_concat = len(z(s1.encode())), len(z(s2.encode())), len(z(concat.encode()))
        return (c_concat - min(c1, c2)) / max(c1, c2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_features = self._extract_features(prompt)
        constraints = self._extract_constraints(prompt)
        
        # Bandit parameters
        T0 = 1.0
        gamma = 1.5
        B = len(candidates) * 2  # Budget
        
        # Initialize arms
        arms = {}
        for c in candidates:
            arms[c] = {'n': 0, 'Q': 0.0, 'features': self._extract_features(c)}
            
        results = []
        
        # Simulation loop (Bandit)
        for t in range(1, B + 1):
            best_ucb = -float('inf')
            selected_candidate = None
            
            # Annealing temperature
            T = T0 / math.log(t + 2)
            
            for c, data in arms.items():
                if data['n'] == 0:
                    ucb = float('inf')
                else:
                    exploration = gamma * math.sqrt(math.log(t) / data['n'])
                    ucb = data['Q'] + exploration
                
                if ucb > best_ucb:
                    best_ucb = ucb
                    selected_candidate = c
            
            # Evaluate selected candidate
            c_feat = arms[selected_candidate]['features']
            E = self._calculate_energy(prompt, selected_candidate, c_feat)
            
            # Count specific violations for entropy
            viol_count = 0
            for cons in constraints:
                viol_count += self._check_violation(cons, c_feat, selected_candidate)
                
            S = self._calculate_entropy(viol_count)
            F = E - T * S  # Free energy
            
            # Update Bandit Stats
            n_old = arms[selected_candidate]['n']
            Q_old = arms[selected_candidate]['Q']
            n_new = n_old + 1
            # Incremental mean update for negative free energy (maximize -F)
            Q_new = Q_old + ( (-F) - Q_old ) / n_new
            
            arms[selected_candidate]['n'] = n_new
            arms[selected_candidate]['Q'] = Q_new
            
            # Adaptive Control Update
            self._update_weights(c_feat, E)

        # Final Scoring
        final_T = T0 / math.log(B + 2)
        scored_candidates = []
        
        for c in candidates:
            data = arms[c]
            E = self._calculate_energy(prompt, c, data['features'])
            viol_count = sum(self._check_violation(cons, data['features'], c) for cons in constraints)
            S = self._calculate_entropy(viol_count)
            F = E - final_T * S
            score = -F  # Higher is better
            
            # Blend with NCD (max 15% weight)
            # Compare candidate to prompt structure
            ncd = self._ncd_score(prompt, c)
            structural_score = score * 0.85 + (1.0 - ncd) * 0.15
            
            scored_candidates.append({
                "candidate": c,
                "score": structural_score,
                "reasoning": f"E={E:.2f}, S={S:.2f}, F={F:.2f}"
            })
            
        # Sort descending by score
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        # 1. Check Meta-Confidence (Tier B Traps)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Structural Match Check
        ans_features = self._extract_features(answer)
        prompt_features = self._extract_features(prompt)
        
        # If no structural features match and prompt is complex, lower confidence
        if np.sum(ans_features) == 0 and np.sum(prompt_features) > 0:
            meta_cap = min(meta_cap, 0.25)
            
        # 3. Compute Score via evaluate logic
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        raw_score = res[0]['score']
        
        # Normalize score to 0-1 range roughly (heuristic scaling)
        # Assuming typical F ranges, map to probability
        # High negative free energy (low F) -> High score -> High confidence
        base_conf = 1.0 / (1.0 + math.exp(-raw_score)) # Sigmoid
        
        # Cap by meta-confidence
        final_conf = min(base_conf, meta_cap)
        
        # Ensure we don't return > 0.9 without definitive computation
        # (Our energy model is heuristic, so cap at 0.95 unless perfect match)
        if meta_cap == 1.0 and raw_score > 5.0:
            final_conf = min(final_conf, 0.95)
        elif meta_cap < 1.0:
            final_conf = min(final_conf, 0.29) # Strict cap for ambiguous
            
        return round(final_conf, 4)