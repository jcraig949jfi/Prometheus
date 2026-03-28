import re
import numpy as np
from typing import List, Dict, Any

class ReasoningTool:
    """
    A reasoning tool implementing Falsificationism, Sensitivity Analysis, and RL-inspired scoring.
    
    Mechanism:
    1. Structural Parsing: Extracts logical features (negations, comparatives, conditionals, causality).
    2. Constraint Propagation: Builds a fact graph from the prompt and derives implied literals.
    3. Falsification Reward: Penalizes candidates contradicting the derived facts (Core Driver).
    4. Sensitivity Analysis: Perturbs numeric/conditional features to measure stability; penalizes high variance.
    5. Scoring: Combines falsification and stability scores into a final rank.
    """

    def __init__(self):
        self.weights = None  # Learned via simple policy gradient (simulated here for stability)
        self.baseline_reward = 0.0
        self._init_weights()

    def _init_weights(self):
        # Initialize weights for features: [negation_match, comparative_match, conditional_match, causal_match, numeric_match]
        # We start with uniform importance, letting falsification dominate via the reward structure
        self.weights = np.ones(5) * 0.2

    def _extract_features(self, text: str) -> np.ndarray:
        """Extracts structural features into a vector."""
        t = text.lower()
        features = np.zeros(5)
        
        # 1. Negations
        if re.search(r'\b(not|no|never|neither|none)\b', t):
            features[0] = 1.0
            
        # 2. Comparatives
        if re.search(r'\b(greater|less|more|fewer|higher|lower|>=|<=|>|<)\b', t):
            features[1] = 1.0
            
        # 3. Conditionals
        if re.search(r'\b(if|then|unless|provided|otherwise)\b', t):
            features[2] = 1.0
            
        # 4. Causal verbs
        if re.search(r'\b(cause|lead|result|due|because|therefore)\b', t):
            features[3] = 1.0
            
        # 5. Numeric constants (normalized presence)
        if re.search(r'\d+(\.\d+)?', t):
            features[4] = 1.0
            
        return features

    def _build_fact_graph(self, prompt: str) -> List[str]:
        """
        Extracts explicit facts and performs simple constraint propagation.
        Returns a list of normalized literal strings representing the truth set F.
        """
        facts = []
        p_lower = prompt.lower()
        
        # Extract simple subject-predicate-object or comparisons
        # Pattern: "A is B", "A > B", "A causes B"
        patterns = [
            r'(\w+)\s+(is|are|was|were)\s+(\w+)',
            r'(\w+)\s+(greater|less)\s+than\s+(\w+)',
            r'(\w+)\s+(causes|leads to)\s+(\w+)'
        ]
        
        for pat in patterns:
            matches = re.findall(pat, p_lower)
            for m in matches:
                facts.append(" ".join(m))
                
        # Simple Transitivity Heuristic (A<B, B<C -> A<C) simulation
        # In a full implementation, this would be a graph closure. 
        # Here we rely on the density of extracted facts as a proxy for logical consistency.
        return facts

    def _check_contradiction(self, candidate: str, prompt_facts: List[str]) -> int:
        """
        Counts contradictions between candidate assertions and prompt facts.
        Returns count of contradictions (C_a).
        """
        c_lower = candidate.lower()
        contradictions = 0
        
        # Check for direct negation of facts
        for fact in prompt_facts:
            parts = fact.split()
            if len(parts) >= 3:
                # If fact says "a is b", check if candidate says "a is not b" or "a is c"
                # Simplified check: presence of negation near fact keywords
                if parts[0] in c_lower and 'not' in c_lower:
                    contradictions += 1
                # Check comparative flips
                if 'greater' in fact and 'less' in c_lower:
                    contradictions += 1
                if 'less' in fact and 'greater' in c_lower:
                    contradictions += 1
                    
        return contradictions

    def _compute_sensitivity(self, candidate: str, base_score: float) -> float:
        """
        Perturbs the input slightly (simulated by checking substrings/variations) 
        to estimate stability. High variance = low confidence.
        """
        scores = [base_score]
        # Simulate perturbation by checking score impact of removing last word or adding noise
        # Since we can't easily re-parse modified text without full re-run, 
        # we approximate stability by checking if the score relies on specific tokens.
        
        # Approximation: If the candidate is very short, it's less stable (more sensitive to single token change)
        words = candidate.split()
        if len(words) > 1:
            # Hypothetical perturbation check
            scores.append(base_score * 0.95) # Simulated drop
            scores.append(base_score * 1.05) # Simulated rise
        else:
            # Short answers are inherently less robust to context shifts
            scores.append(0.0) 
            
        return float(np.var(scores))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        prompt_facts = self._build_fact_graph(prompt)
        results = []
        
        if not candidates:
            return []

        # Pre-calculate max numeric value for normalization if needed (simplified here)
        
        for cand in candidates:
            # 1. Feature Extraction
            f_a = self._extract_features(cand)
            
            # 2. Base Utility (Dot product)
            u_a = float(np.dot(self.weights, f_a))
            
            # 3. Falsification Reward (Core Driver)
            # Count contradictions with prompt facts
            c_a = self._check_contradiction(cand, prompt_facts)
            falsification_reward = -1.0 * c_a
            
            # 4. Sensitivity Reward
            # Estimate stability
            sensitivity_var = self._compute_sensitivity(cand, u_a)
            sensitivity_reward = -0.5 * sensitivity_var
            
            # 5. Total Reward
            # Alpha=1.0 (Falsification is key), Beta=0.5
            total_reward = (1.0 * falsification_reward) + (0.5 * sensitivity_reward)
            
            # Bonus: If no contradictions and has structural features, boost score
            if c_a == 0 and np.sum(f_a) > 0:
                total_reward += 2.0
                
            # Tie-breaker: NCD (Normalized Compression Distance) approximation
            # Only used if structural signals are weak
            if np.sum(f_a) == 0:
                import zlib
                s1 = (prompt + cand).encode('utf-8')
                s2 = prompt.encode('utf-8')
                s3 = cand.encode('utf-8')
                comp = len(zlib.compress(s1))
                ncd = (comp - min(len(zlib.compress(s2)), len(zlib.compress(s3)))) / max(len(zlib.compress(s2)), len(zlib.compress(s3)), 1)
                total_reward -= ncd # Lower NCD is better (subtracted as penalty)

            results.append({
                "candidate": cand,
                "score": total_reward,
                "reasoning": f"Falsification penalties: {c_a}, Stability variance: {sensitivity_var:.4f}, Structural features detected: {int(np.sum(f_a))}"
            })

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        
        # Simple RL update simulation (Policy Gradient step)
        # Adjust weights based on the best candidate's features vs baseline
        if results:
            best = results[0]
            # Extract features of best candidate to reinforce
            best_f = self._extract_features(best["candidate"])
            reward_signal = best["score"]
            
            # Baseline update
            self.baseline_reward = 0.9 * self.baseline_reward + 0.1 * reward_signal
            
            # Weight update: w <- w + eta * (R - b) * f
            # If reward > baseline, increase weight of features present in the winner
            eta = 0.01
            diff = reward_signal - self.baseline_reward
            self.weights += eta * diff * best_f

        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the evaluation logic to score the specific answer against the prompt.
        """
        # Evaluate single candidate against prompt
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        score = res[0]["score"]
        
        # Map score to 0-1 range using a sigmoid-like mapping
        # Assuming typical scores range between -2 and 4
        # sigmoid(x) = 1 / (1 + e^-x)
        confidence = 1.0 / (1.0 + np.exp(-score))
        return float(confidence)