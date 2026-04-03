import re
import math
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Chaotic Predictive Coding Network (CPCN) Implementation.
    
    Mechanism:
    1. Chaos Theory (Exploration): Uses a deterministic chaotic map (Logistic Map at r=3.9)
       to generate high-dimensional state vectors from input features. This simulates the
       "Edge of Chaos" reservoir, creating diverse internal representations of the prompt.
    2. Neural Plasticity (Adaptation): Implements a Hebbian-like weight update where 
       connection strengths between chaotic states and output scores are modulated by 
       prediction error (difference between structural match and candidate fit).
    3. Free Energy Principle (Optimization): Computes a variational free energy score 
       balancing accuracy (structural/logical fit) and complexity (candidate length/entropy).
       Minimizing free energy selects the hypothesis that best explains the data with 
       minimal complexity.
       
    Epistemic Honesty (Tier B):
    Prioritizes detecting ambiguity, presuppositions, and unanswerable constraints.
    If meta-confidence is low, final confidence is capped strictly.
    """

    def __init__(self):
        self.reservoir_size = 32
        self.chaotic_state = [0.5] * self.reservoir_size
        self.readout_weights = [1.0] * self.reservoir_size
        self.learning_rate = 0.1
        
        # Initialize chaotic reservoir
        self._perturb_reservoir(100)

    def _perturb_reservoir(self, steps: int):
        """Run chaotic dynamics to initialize state diversity."""
        r = 3.9  # Edge of chaos parameter
        for _ in range(steps):
            new_states = []
            for i, x in enumerate(self.chaotic_state):
                # Logistic map with slight coupling
                idx_prev = (i - 1) % self.reservoir_size
                coupled = 0.9 * x + 0.1 * self.chaotic_state[idx_prev]
                new_states.append(r * coupled * (1 - coupled))
            self.chaotic_state = new_states

    def _extract_features(self, text: str) -> List[float]:
        """Convert text to numeric features for the reservoir."""
        features = []
        # Feature 1: Length normalized
        features.append(len(text) / 100.0)
        # Feature 2: Question mark presence
        features.append(1.0 if '?' in text else 0.0)
        # Feature 3: Negation count
        negations = ['no', 'not', 'never', 'none', 'neither']
        features.append(sum(1 for w in negations if re.search(r'\b' + w + r'\b', text.lower())) / 5.0)
        # Feature 4: Numeric presence
        features.append(1.0 if re.search(r'\d+', text) else 0.0)
        # Feature 5: Comparative/Superlative
        comps = ['better', 'worse', 'more', 'less', 'best', 'worst', 'most', 'least']
        features.append(sum(1 for w in comps if w in text.lower()) / 8.0)
        
        # Pad to reservoir size
        while len(features) < self.reservoir_size:
            features.append(0.0)
        return features[:self.reservoir_size]

    def _run_chaotic_forward(self, input_features: List[float]) -> List[float]:
        """Propagate input through chaotic reservoir."""
        # Inject input
        for i in range(min(len(input_features), self.reservoir_size)):
            self.chaotic_state[i] = 0.8 * self.chaotic_state[i] + 0.2 * input_features[i]
        
        # Evolve one step
        r = 3.9
        new_states = []
        for i, x in enumerate(self.chaotic_state):
            idx_prev = (i - 1) % self.reservoir_size
            coupled = 0.9 * x + 0.1 * self.chaotic_state[idx_prev]
            new_states.append(r * coupled * (1 - coupled))
        self.chaotic_state = new_states
        return self.chaotic_state

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Detect ambiguity, presupposition, and unanswerability.
        Returns a cap value (0.0 - 1.0). Low value = high ambiguity.
        """
        p_lower = prompt.lower()
        score = 1.0
        
        # 1. Presupposition Traps
        presupposition_triggers = [
            r"have you stopped", r"have you quit", r"why did .+ fail", 
            r"why did .+ stop", r"when did .+ stop", r"how often do .+ fail"
        ]
        for pattern in presupposition_triggers:
            if re.search(pattern, p_lower):
                score -= 0.8  # Heavy penalty
        
        # 2. Scope/Pronoun Ambiguity indicators
        ambiguity_triggers = [
            r"every .+ a .+", r"told .+ he ", r"told .+ she ", 
            r"who is .+\?", r"which one is .+\?"
        ]
        for pattern in ambiguity_triggers:
            if re.search(pattern, p_lower):
                score -= 0.5
                
        # 3. False Dichotomy / Loaded Assumption
        if re.search(r"either .+ or .+", p_lower) and not re.search(r"both", p_lower):
            score -= 0.4
            
        # 4. Subjectivity without criteria
        subjective_words = ["best", "worst", "favorite", "beautiful", "ugly", "good", "bad"]
        if any(w in p_lower for w in subjective_words):
            if "measure" not in p_lower and "calculate" not in p_lower and "count" not in p_lower:
                score -= 0.6
                
        # 5. Unanswerable / Missing Info
        if re.search(r"what is the color of .+\?", p_lower) and "color" not in p_lower.split("?")[0]:
             # Heuristic for missing context questions
            if len(p_lower.split()) < 15: 
                score -= 0.7

        return max(0.0, min(1.0, score))

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Tier A: Structural parsing and logical deduction.
        Returns 0.0 - 1.0 based on structural fit.
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower().strip().rstrip('.')
        score = 0.0
        
        # 1. Numeric Evaluation (Constructive Computation)
        # Detect simple comparisons like "Is 9.11 > 9.9?"
        num_match = re.search(r"(\d+\.?\d*)\s*(>|<|>=|<=|==|!=)\s*(\d+\.?\d*)", p_lower)
        if num_match:
            try:
                v1 = float(num_match.group(1))
                op = num_match.group(2)
                v2 = float(num_match.group(3))
                is_true = False
                if op == '>': is_true = v1 > v2
                elif op == '<': is_true = v1 < v2
                elif op == '>=': is_true = v1 >= v2
                elif op == '<=': is_true = v1 <= v2
                elif op == '==': is_true = v1 == v2
                elif op == '!=': is_true = v1 != v2
                
                if is_true:
                    if "yes" in c_lower or "true" in c_lower or str(v1) in candidate:
                        score += 1.0
                    else:
                        score -= 1.0
                else:
                    if "no" in c_lower or "false" in c_lower:
                        score += 1.0
                    else:
                        score -= 1.0
                return max(0, min(1, (score + 1)/2)) # Normalize to 0-1
            except:
                pass

        # 2. Negation Handling
        negation_present = bool(re.search(r'\b(no|not|never|none)\b', p_lower))
        candidate_negates = bool(re.search(r'\b(no|not|never|false)\b', c_lower))
        
        if negation_present:
            if candidate_negates:
                score += 0.5 # Candidate acknowledges negation
            else:
                score -= 0.5 # Candidate ignores negation
        
        # 3. Yes/No Consistency
        if re.search(r"^(yes|no|true|false)", c_lower):
            # If prompt asks a question, yes/no is structurally relevant
            if "?" in prompt:
                score += 0.3
        
        # 4. Transitivity / Logic Keywords
        if "therefore" in c_lower or "thus" in c_lower:
            score += 0.1 # Reward logical connectors if present
            
        return max(0.0, min(1.0, score))

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Compute Variational Free Energy F = Accuracy - Complexity.
        Lower F is better. We return negative F as the score (higher is better).
        """
        # Accuracy term: Structural fit + Semantic overlap (simplified)
        acc_term = self._structural_score(prompt, candidate)
        
        # Complexity term: Length penalty (Occam's razor)
        # Normalize length to 0-1 range roughly
        complexity = len(candidate) / 200.0 
        complexity = min(1.0, complexity)
        
        # Free Energy = Complexity - Accuracy (We want to minimize this)
        # Score = Accuracy - Complexity
        f_score = acc_term - (0.5 * complexity)
        return f_score

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # 1. Meta-Confidence Check (Tier B)
        meta_conf = self._meta_confidence(prompt)
        
        results = []
        for cand in candidates:
            # 2. Chaotic Reservoir Input
            features = self._extract_features(prompt + " " + cand)
            state = self._run_chaotic_forward(features)
            
            # 3. Plastic Readout (Hebbian-like scoring)
            # Dot product of state and weights
            raw_score = sum(s * w for s, w in zip(state, self.readout_weights))
            
            # 4. Free Energy Calculation
            fe_score = self._compute_free_energy(prompt, cand)
            
            # 5. NCD Tiebreaker
            ncd = self._ncd_distance(prompt, cand)
            
            # Combine scores: Structural/FE (50%), Chaotic (35%), NCD (15%)
            # Note: FE score is already weighted internally
            final_score = (0.50 * (fe_score + 0.5)) + (0.35 * raw_score) - (0.15 * ncd)
            
            # Apply Epistemic Honesty Cap
            if meta_conf < 0.3:
                # If ambiguous, cap the confidence regardless of score
                final_score = min(final_score, 0.25)
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Meta-conf:{meta_conf:.2f}, FE:{fe_score:.2f}, NCD:{ncd:.2f}"
            })
            
            # Plasticity Update: Adjust weights based on error between structural expectation and result
            # Simplified: If FE score is high, reinforce current state pattern
            if fe_score > 0.5:
                for i in range(self.reservoir_size):
                    self.readout_weights[i] += self.learning_rate * state[i] * 0.01
            elif fe_score < -0.5:
                for i in range(self.reservoir_size):
                    self.readout_weights[i] -= self.learning_rate * state[i] * 0.01

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1.
        Caps at 0.25 if meta-analysis detects ambiguity.
        Caps at 0.9 unless computation was definitive.
        """
        meta_conf = self._meta_confidence(prompt)
        
        # Run a quick evaluation to get structural score
        # We simulate a single candidate evaluation
        features = self._extract_features(prompt + " " + answer)
        state = self._run_chaotic_forward(features)
        fe_score = self._compute_free_energy(prompt, answer)
        
        # Base confidence derived from Free Energy (Accuracy - Complexity)
        # Map FE score (approx -0.5 to 1.0) to 0-1
        base_conf = (fe_score + 0.5) / 1.5
        base_conf = max(0.0, min(1.0, base_conf))
        
        # Apply Meta-Confidence Cap (Epistemic Honesty)
        if meta_conf < 0.3:
            return min(base_conf, 0.25)
        
        # General cap for non-computational certainty
        # Only allow > 0.9 if it looks like a hard math/logic win
        is_hard_logic = bool(re.search(r"(\d+\.?\d*)\s*(>|<|==)", prompt))
        if not is_hard_logic:
            base_conf = min(base_conf, 0.85)
            
        return float(base_conf)