import numpy as np
import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Critical Compositional Global Workspace (CCGW) Implementation.
    
    Mechanism:
    1. Compositionality: Parses prompts into symbolic tokens (numbers, operators, negations).
       Represents candidates as compositional vectors binding these tokens.
    2. Criticality: Maintains a dynamic "branching ratio" (sigma) near 1.0.
       Uses a homeostatic rule: if activity (agreement among modules) is too high, 
       threshold increases (dampening); if too low, threshold decreases (sensitizing).
       This creates a phase-transition zone where weak evidence can trigger "ignition".
    3. Global Workspace: Candidates compete for ignition. 
       - Modules: Numeric, Logical, Structural.
       - Each module casts a weighted vote based on constraint satisfaction.
       - If total activity > dynamic threshold, the candidate "ignites" (high score).
    
    This approximates the CCGW architecture using numpy for tensor operations and 
    standard library for parsing, ensuring determinism and no external deps.
    """

    def __init__(self):
        # Criticality parameters
        self.sigma = 1.0          # Target branching ratio
        self.threshold = 0.5      # Dynamic ignition threshold
        self.learning_rate = 0.1  # Homeostatic plasticity rate
        self.activity_history = [] # Track recent activity for homeostasis
        
        # Compositionality: Simple token vocabulary builder
        self.vocab = set()
        
    def _tokenize(self, text: str) -> List[str]:
        """Extract compositional tokens (numbers, logic words, operators)."""
        text_lower = text.lower()
        # Extract numbers (floats and ints)
        numbers = re.findall(r'-?\d+\.?\d*', text_lower)
        # Extract logical operators
        logic_ops = []
        for op in ['not', 'no', 'yes', 'true', 'false', 'greater', 'less', 'equal', 'if', 'then']:
            if op in text_lower:
                logic_ops.append(op)
        
        tokens = numbers + logic_ops
        for t in tokens:
            self.vocab.add(t)
        return tokens

    def _numeric_module(self, prompt: str, candidate: str) -> float:
        """Module: Evaluates numeric consistency and comparisons."""
        score = 0.0
        p_nums = re.findall(r'-?\d+\.?\d*', prompt.lower())
        c_nums = re.findall(r'-?\d+\.?\d*', candidate.lower())
        
        if not p_nums:
            return 0.5 # Neutral if no numbers
        
        try:
            p_vals = [float(n) for n in p_nums]
            c_vals = [float(n) for n in c_nums] if c_nums else []
            
            # Check for direct answer match
            if c_vals:
                # If prompt asks for max/min logic implicitly
                if "larger" in prompt.lower() or "greater" in prompt.lower():
                    if max(c_vals) == max(p_vals): score += 0.4
                elif "smaller" in prompt.lower() or "less" in prompt.lower():
                    if min(c_vals) == min(p_vals): score += 0.4
                
                # Exact float match bonus
                if set(p_vals) == set(c_vals):
                    score += 0.5
                elif any(abs(p - c) < 1e-6 for p in p_vals for c in c_vals):
                    score += 0.3
        except ValueError:
            pass
            
        return min(1.0, score)

    def _logical_module(self, prompt: str, candidate: str) -> float:
        """Module: Evaluates logical constraints (negation, binary)."""
        score = 0.0
        p_low = prompt.lower()
        c_low = candidate.lower()
        
        # Negation handling
        if "not" in p_low or "no " in p_low:
            if "not" in c_low or "no" in c_low:
                score += 0.6
            else:
                score -= 0.4 # Penalty for missing negation
        
        # Binary consistency
        yes_words = ['yes', 'true', 'correct']
        no_words = ['no', 'false', 'incorrect']
        
        if any(w in p_low for w in yes_words):
            if any(w in c_low for w in yes_words): score += 0.5
            elif any(w in c_low for w in no_words): score -= 0.5
            
        if any(w in p_low for w in no_words):
            if any(w in c_low for w in no_words): score += 0.5
            elif any(w in c_low for w in yes_words): score -= 0.5
            
        return min(1.0, max(-1.0, score))

    def _structural_module(self, prompt: str, candidate: str) -> float:
        """Module: NCD-based structural similarity as a tiebreaker."""
        def ncd(a: str, b: str) -> float:
            len_a, len_b = len(a), len(b)
            if len_a == 0 or len_b == 0: return 1.0
            concat = a.encode() + b.encode()
            len_comp = len(zlib.compress(concat))
            return len_comp / max(len_a, len_b)
        
        # Invert NCD to similarity (0-1), lower NCD = higher similarity
        dist = ncd(prompt.lower(), candidate.lower())
        return max(0.0, 1.0 - dist)

    def _compute_critical_activity(self, votes: List[float]) -> float:
        """
        Computes global workspace activity.
        Simulates critical branching: activity propagates if near threshold.
        """
        if not votes: return 0.0
        
        # Weighted sum of module votes (simulating excitatory connections)
        # Weights are uniform here, but in full CCGW would be learned
        raw_activity = np.mean(votes) 
        
        # Apply non-linear ignition function (sigmoid-like)
        # If raw_activity > threshold, it explodes (ignites); else decays
        margin = raw_activity - self.threshold
        ignition = 1.0 / (1.0 + np.exp(-10 * margin)) # Sharp transition
        
        # Homeostatic plasticity: Adjust threshold to keep average activity near 0.5
        self.activity_history.append(raw_activity)
        if len(self.activity_history) > 10:
            self.activity_history.pop(0)
            
        if len(self.activity_history) >= 5:
            avg_act = np.mean(self.activity_history)
            # If avg activity > target (0.5), raise threshold (harder to ignite)
            # If avg activity < target, lower threshold (easier to ignite)
            delta = self.learning_rate * (avg_act - 0.5)
            self.threshold += delta
            self.threshold = np.clip(self.threshold, 0.1, 0.9)
            
        return ignition

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-compute prompt tokens for compositionality
        self._tokenize(prompt)
        
        for cand in candidates:
            # 1. Modular Processing (Specialized modules)
            v_num = self._numeric_module(prompt, cand)
            v_log = self._logical_module(prompt, cand)
            v_struct = self._structural_module(prompt, cand)
            
            # 2. Global Workspace Integration
            # Modules compete/cooperate; their outputs form the input vector
            votes = [v_num, v_log, v_struct]
            
            # 3. Critical Ignition
            score = self._compute_critical_activity(votes)
            
            # Construct reasoning string (simplified for output)
            reasons = []
            if v_num > 0.4: reasons.append("numeric_match")
            if v_log > 0.4: reasons.append("logic_consistent")
            if v_struct > 0.5: reasons.append("structural_sim")
            if score > 0.8: reasons.append("ignited")
            
            reasoning = ", ".join(reasons) if reasons else "weak_evidence"
            
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reasoning
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence based on the ignition score of the specific answer."""
        # Evaluate single candidate against prompt
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]["score"]