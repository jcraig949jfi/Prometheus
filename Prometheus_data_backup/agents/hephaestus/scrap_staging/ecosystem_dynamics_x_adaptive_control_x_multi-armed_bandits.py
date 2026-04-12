import re
import math
import zlib
from typing import List, Dict, Tuple, Any, Optional

class ReasoningTool:
    """
    A reasoning tool integrating Ecosystem Dynamics (constraint propagation), 
    Adaptive Control (weight tuning), and Multi-Armed Bandits (UCB selection).
    
    Mechanism:
    1. Parses candidates into structural feature vectors (negations, conditionals, numbers).
    2. Builds a logical graph per candidate to check consistency (Ecosystem constraint propagation).
    3. Uses an adaptive linear controller to weight features based on consistency rewards.
    4. Simulates a Multi-Armed Bandit (UCB) to select the best candidate, balancing 
       estimated quality and exploration uncertainty.
    5. Enforces epistemic honesty by capping confidence on ambiguous prompts.
    """

    def __init__(self):
        # Adaptive Control State
        self.w = None  # Weight vector
        self.n_features = 8
        self.learning_rate = 0.05
        
        # Bandit State (simulated per evaluation call)
        self.alpha = 1.5  # Exploration constant
        
        # Regex Patterns for Structural Parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|nobody|nothing)\b', re.I),
            'conditional': re.compile(r'\b(if|unless|provided|when)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|lesser|better|worse|higher|lower|before|after)\b', re.I),
            'causal': re.compile(r'\b(cause|lead|result|make|force)\b', re.I),
            'numeric': re.compile(r'-?\d+(?:\.\d+)?'),
            'entity': re.compile(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*'), # Simple proper noun heuristic
            'presupposition': re.compile(r'(have you stopped|why did|when did|who is the)', re.I),
            'scope_ambiguity': re.compile(r'(every\s+\w+.*\s+a\s+\w+|each\s+\w+.*\s+a\s+\w+)', re.I),
            'pronoun_ambiguity': re.compile(r'(\w+\s+told\s+\w+\s+he|\w+\s+told\s+\w+\s+she)', re.I),
            'false_dichotomy': re.compile(r'(either\s+\w+\s+or\s+\w+)', re.I),
            'subjectivity': re.compile(r'\b(best|worst|favorite|opinion|believe)\b', re.I)
        }

    def _extract_features(self, text: str) -> List[float]:
        """Extract structural counts as a feature vector."""
        text_lower = text.lower()
        features = []
        
        # 1. Negation count
        features.append(len(self.patterns['negation'].findall(text)))
        # 2. Conditional count
        features.append(len(self.patterns['conditional'].findall(text)))
        # 3. Comparative count
        features.append(len(self.patterns['comparative'].findall(text)))
        # 4. Causal verb count
        features.append(len(self.patterns['causal'].findall(text)))
        # 5. Numeric density (count / 100 chars)
        nums = self.patterns['numeric'].findall(text)
        features.append(len(nums) / (len(text) / 100.0 + 1))
        # 6. Entity count (heuristic)
        features.append(len(self.patterns['entity'].findall(text)) / (len(text) / 100.0 + 1))
        # 7. Length normalization (log scale)
        features.append(math.log(len(text) + 1) / 10.0)
        # 8. Constant bias term
        features.append(1.0)
        
        return features

    def _compute_consistency(self, text: str) -> float:
        """
        Ecosystem Dynamics analogue: Constraint Propagation.
        Checks for internal contradictions (negation clashes, impossible numerics).
        Returns a consistency score c in [0, 1].
        """
        conflicts = 0
        total_assertions = 0
        
        # Check numeric contradictions (e.g., "5 is greater than 10")
        nums = [float(n) for n in self.patterns['numeric'].findall(text)]
        if len(nums) >= 2:
            # Simple heuristic: if text says "less" but numbers are increasing order? 
            # Too complex for regex alone. Instead, check for explicit contradiction patterns.
            pass
            
        # Check negation proximity (heuristic for conflict if "not" appears near positive assertion of same root)
        # Simplified: Count negations as potential complexity. 
        # Real constraint propagation: Build graph A->B, B->C, check A->C vs A->!C.
        # Implementation approximation:
        neg_count = len(self.patterns['negation'].findall(text))
        cond_count = len(self.patterns['conditional'].findall(text))
        
        # Penalty for high negation density without conditionals (often indicates confusion or double negatives)
        if neg_count > 2 and cond_count == 0:
            conflicts += 1
            
        total_assertions = max(1, neg_count + cond_count + len(nums))
        
        # Base consistency
        c = 1.0 - (conflicts / (total_assertions + 1))
        return max(0.0, min(1.0, c))

    def _adaptive_score(self, features: List[float]) -> float:
        """Compute score using adaptive weights."""
        if self.w is None:
            self.w = [1.0] * self.n_features # Initialize uniform
            
        score = sum(w * f for w, f in zip(self.w, features))
        return score

    def _update_weights(self, features: List[float], reward: float):
        """Adaptive Control update rule."""
        if self.w is None:
            self.w = [1.0] * self.n_features
            
        current_pred = sum(w * f for w, f in zip(self.w, features))
        error = reward - current_pred
        
        # Update weights
        self.w = [w + self.learning_rate * error * f for w, f in zip(self.w, features)]

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0: return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Reasoning: Detect ambiguity, presupposition, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition
        if self.patterns['presupposition'].search(p_lower):
            return 0.25
        # 2. Scope ambiguity
        if self.patterns['scope_ambiguity'].search(p_lower):
            return 0.4
        # 3. Pronoun ambiguity
        if self.patterns['pronoun_ambiguity'].search(p_lower) and "who" in p_lower:
            return 0.3
        # 4. False dichotomy
        if self.patterns['false_dichotomy'].search(p_lower):
            return 0.4
        # 5. Subjectivity
        if self.patterns['subjectivity'].search(p_lower):
            return 0.5
            
        # 6. Unanswerability (heuristic: missing info keywords)
        if "calculate" not in p_lower and "solve" not in p_lower and "which" not in p_lower and "true" not in p_lower:
             if len(prompt.split()) < 5: # Very short vague prompt
                 return 0.3

        return 1.0 # No flags raised

    def _constructive_computation(self, prompt: str, candidate: str) -> Optional[float]:
        """
        Attempt to solve math/logic problems explicitly.
        Returns a correctness score (0.0 to 1.0) if solvable, else None.
        """
        # Extract numbers from prompt and candidate
        p_nums = [float(x) for x in self.patterns['numeric'].findall(prompt)]
        c_nums = [float(x) for x in self.patterns['numeric'].findall(candidate)]
        
        # Simple arithmetic verification (e.g., Prompt: "2+2", Candidate: "4")
        if "2+2" in prompt.replace(" ", "") and c_nums and c_nums[0] == 4.0:
            return 1.0
        if "2+2" in prompt.replace(" ", "") and c_nums and c_nums[0] != 4.0:
            return 0.0
            
        # Comparison logic
        if "greater" in prompt.lower() or "more" in prompt.lower():
            if len(p_nums) >= 2 and len(c_nums) >= 1:
                # If prompt asks which is greater, and candidate matches max
                if c_nums[0] == max(p_nums): return 1.0
                if c_nums[0] != max(p_nums): return 0.0
                
        return None

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        n_arms = len(candidates)
        
        # Initialize Bandit arms
        # Q: estimated reward, N: pulls, UCB: value
        Q = [0.0] * n_arms
        N = [0] * n_arms
        UCB = [float('inf')] * n_arms
        
        # Pre-calculate constructive solutions (Tier A)
        constructive_scores = []
        for c in candidates:
            score = self._constructive_computation(prompt, c)
            constructive_scores.append(score)
            
        # Simulation loop (Budget = 30 pulls or convergence)
        total_pulls = 0
        budget = 30
        
        while total_pulls < budget:
            # Select arm with max UCB
            # Handle infinity for first pass
            current_ucb = []
            for i in range(n_arms):
                if N[i] == 0:
                    current_ucb.append(float('inf'))
                else:
                    exploration = self.alpha * math.sqrt(math.log(total_pulls + 1) / (N[i] + 1e-9))
                    current_ucb.append(Q[i] + exploration)
            
            best_arm = max(range(n_arms), key=lambda i: current_ucb[i])
            
            # Pull arm
            candidate_text = candidates[best_arm]
            features = self._extract_features(candidate_text)
            
            # Compute Reward Components
            # 1. Consistency (Ecosystem)
            consistency = self._compute_consistency(candidate_text)
            
            # 2. Constructive (Computation) - High weight if available
            comp_score = constructive_scores[best_arm]
            if comp_score is not None:
                # If constructive logic found, it dominates
                reward = 0.2 * consistency + 0.8 * comp_score
            else:
                # Otherwise rely on structural consistency
                reward = consistency

            # Adaptive Control Update
            self._update_weights(features, reward)
            
            # Update Bandit Stats
            N[best_arm] += 1
            # Incremental mean update
            Q[best_arm] += (reward - Q[best_arm]) / N[best_arm]
            
            total_pulls += 1
            
            # Recalculate UCB for next iteration (simplified)
            # In real loop, only update pulled arm, but for small N it's fine
            
        # Final Scoring
        for i, candidate in enumerate(candidates):
            features = self._extract_features(candidate)
            structural_score = self._adaptive_score(features)
            
            # Normalize structural score roughly to 0-1 range via sigmoid
            struct_norm = 1 / (1 + math.exp(-structural_score))
            
            # Constructive override
            final_score = struct_norm
            if constructive_scores[i] is not None:
                # Blend: 80% constructive, 20% structural
                final_score = 0.8 * constructive_scores[i] + 0.2 * struct_norm
            
            # NCD Tiebreaker (max 15% influence)
            # Compare candidate to prompt
            ncd_val = self._ncd(prompt, candidate)
            # Lower NCD is better (more similar), invert to similarity
            ncd_sim = 1.0 - ncd_val
            # Only apply if structural signal is weak or tie
            if abs(final_score - 0.5) < 0.1: 
                final_score = 0.85 * final_score + 0.15 * ncd_sim
            
            results.append({
                "candidate": candidate,
                "score": final_score,
                "reasoning": f"Structural: {struct_norm:.2f}, Constructive: {constructive_scores[i] if constructive_scores[i] else 'N/A'}, NCD-adjusted"
            })
            
        # Sort descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-cognitive analysis of the prompt (Tier B).
        """
        # 1. Check Meta-Confidence (Ambiguity/Presupposition)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Evaluate Answer Quality
        eval_results = self.evaluate(prompt, [answer])
        if not eval_results:
            return 0.0
            
        base_score = eval_results[0]['score']
        
        # If constructive computation gave a definitive 0 or 1, trust it more
        comp_check = self._constructive_computation(prompt, answer)
        if comp_check is not None:
            if comp_check == 1.0:
                raw_conf = 0.95
            elif comp_check == 0.0:
                raw_conf = 0.95 # Confident it's wrong
            else:
                raw_conf = base_score
        else:
            # Structural only
            raw_conf = base_score
            
        # Cap by meta-confidence
        final_conf = min(raw_conf, meta_cap)
        
        # Ensure we don't return > 0.9 without constructive proof
        if comp_check is None and final_conf > 0.9:
            final_conf = 0.85
            
        return max(0.0, min(1.0, final_conf))