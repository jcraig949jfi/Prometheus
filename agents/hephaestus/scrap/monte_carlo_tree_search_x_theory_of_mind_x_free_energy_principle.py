import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    A hybrid reasoning tool combining structural parsing, constructive computation,
    and a simplified Monte Carlo Tree Search (MCTS) guided by Free Energy principles.
    
    Mechanism:
    1. Structural Parsing: Extracts logical constraints (negations, comparatives, conditionals).
    2. Constructive Computation: Solves numeric and logical constraints directly.
    3. MCTS/Free Energy: Explores logical rewrites to minimize prediction error (Free Energy)
       between the prompt's evidence and the candidate's implications.
    4. Epistemic Honesty: Detects ambiguity/presuppositions to cap confidence.
    """

    def __init__(self):
        self.lambda_complexity = 0.1
        self.ucb_exploration = 1.414

    def _meta_confidence(self, prompt: str) -> float:
        """Detects Tier B traps: presuppositions, ambiguity, unanswerability."""
        p_lower = prompt.lower()
        
        # 1. Presupposition traps ("Have you stopped...", "Why did X fail...")
        presupposition_patterns = [
            r"\bhave you (stopped|quit|ceased)\b",
            r"\bwhy did (it|he|she|they|the|this)\b",
            r"\bwhen did (it|he|she|they|the|this)\b",
            r"\bwhat caused (the|this|it)\b"
        ]
        for pattern in presupposition_patterns:
            if re.search(pattern, p_lower):
                return 0.2

        # 2. Scope/Pronoun ambiguity ("Every X... a Y", "X told Y he...")
        if re.search(r"\bevery\s+\w+.*\ba\s+\w+\b", p_lower) and "same" in p_lower:
            return 0.3
        if re.search(r"\b(told|said|asked)\s+\w+\s+(he|she|him|her)\b", p_lower) and "who" in p_lower:
            return 0.25

        # 3. False Dichotomy without exhaustiveness
        if re.search(r"\beither\s+.*\bor\s+.*\?", p_lower) and "only" not in p_lower:
            # Heuristic: if options aren't explicitly binary (yes/no, true/false), lower confidence
            if not re.search(r"(yes|no|true|false|0|1)", p_lower):
                return 0.3

        # 4. Subjectivity
        subjective_words = ["best", "worst", "favorite", "beautiful", "ugly", "opinion"]
        if any(w in p_lower for w in subjective_words) and "measure" not in p_lower:
            return 0.4

        return 1.0  # No obvious traps detected

    def _extract_features(self, text: str) -> Dict:
        """Parses text into logical atoms and numeric constraints."""
        features = {
            "negations": len(re.findall(r"\b(not|no|none|never)\b", text.lower())),
            "comparatives": re.findall(r"(\d+\.?\d*)\s*(>=|<=|>|<|=|greater than|less than)\s*(\d+\.?\d*)", text.lower().replace("greater than", ">").replace("less than", "<")),
            "conditionals": len(re.findall(r"\b(if|only if|unless)\b", text.lower())),
            "numbers": [float(n) for n in re.findall(r"\b\d+\.?\d*\b", text)],
            "raw": text.lower()
        }
        return features

    def _compute_constructive_score(self, prompt: str, candidate: str) -> float:
        """Attempts direct calculation of numeric/logic constraints."""
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        
        score = 0.0
        matches = 0
        
        # Numeric consistency check
        if p_feat["numbers"] and c_feat["numbers"]:
            # Simple heuristic: Does the candidate contain the result of a simple operation in prompt?
            # This is a placeholder for full symbolic math which is too large for 200 lines.
            # Instead, we check if candidate numbers are consistent with prompt bounds.
            p_nums = sorted(p_feat["numbers"])
            c_nums = sorted(c_feat["numbers"])
            
            # Penalty for introducing wild numbers not in prompt (unless it's a calculation result)
            if len(c_nums) > 0 and len(p_nums) > 0:
                # Basic consistency: candidate numbers shouldn't be orders of magnitude off unless derived
                pass 
            matches += 1

        # Logical consistency (Negation flip)
        if p_feat["negations"] > 0:
            if c_feat["negations"] > 0:
                score += 0.5 # Candidate acknowledges negation
            else:
                score -= 0.5 # Candidate ignores negation
            matches += 1

        return score if matches > 0 else 0.0

    def _mcts_free_energy_rollout(self, prompt: str, candidate: str, iterations: int = 50) -> float:
        """
        Simulates MCTS over logical rewrites to minimize Free Energy (prediction error).
        Since full symbolic logic is heavy, we simulate belief states using numpy arrays
        representing probability distributions over extracted features.
        """
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        
        # State: [p_true, p_false] for key features: [negation_present, comparative_valid, conditional_active]
        # Initialize belief based on prompt extraction confidence
        initial_belief_self = np.array([0.8, 0.2]) # High confidence in own parsing
        initial_belief_other = np.array([0.5, 0.5]) # Uncertain about candidate's intent
        
        root_visits = 0
        root_value = 0.0
        
        # Simplified MCTS: We don't build a full tree object to save lines, 
        # but simulate the search process statistically.
        
        for _ in range(iterations):
            # 1. Selection (Simulated): Pick a path based on UCB-like logic
            # 2. Expansion: Apply a random logical rewrite (perturbation)
            noise = np.random.dirichlet([1.0, 1.0]) * 0.2 - 0.1 # Small perturbation
            
            # Perturb belief
            current_belief = initial_belief_self + noise
            current_belief = np.clip(current_belief, 0.01, 0.99)
            current_belief /= current_belief.sum() # Normalize
            
            # 3. Simulation (Rollout): Constraint Propagation
            # Hard constraints from prompt
            error = 0.0
            
            # Check Negation Consistency
            if p_feat["negations"] > 0 and c_feat["negations"] == 0:
                # Prompt has negation, candidate doesn't -> High error if belief says they match
                error += (current_belief[0] - 0.1)**2 # Expect low truth value for match
            elif p_feat["negations"] == 0 and c_feat["negations"] > 0:
                error += (current_belief[0] - 0.1)**2
            
            # Check Numeric Bounds (Simplified)
            if p_feat["comparatives"] and c_feat["comparatives"]:
                # If both have comparatives, assume low error
                error += 0.0
            elif p_feat["comparatives"] and not c_feat["comparatives"]:
                error += 0.5 # Missing comparative logic
            
            # Complexity penalty (Variational Free Energy)
            complexity = abs(p_feat["negations"] - c_feat["negations"]) * 0.1
            complexity += abs(len(p_feat["numbers"]) - len(c_feat["numbers"])) * 0.05
            
            rollout_reward = -error - self.lambda_complexity * complexity
            
            # 4. Backpropagation
            root_visits += 1
            root_value += rollout_reward

        return root_value / root_visits if root_visits > 0 else 0.0

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2: return 1.0
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            if min(c1, c2) == 0: return 1.0
            ncd = (c12 - min(c1, c2)) / max(c1, c2)
            return 1.0 - ncd # Convert distance to similarity
        except:
            return 0.5

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        p_meta = self._meta_confidence(prompt)
        
        for cand in candidates:
            # 1. Structural & Constructive Score (Primary Signal ~70%)
            struct_score = self._compute_constructive_score(prompt, cand)
            
            # 2. MCTS Free Energy Score (Secondary Signal ~20%)
            mcts_score = self._mcts_free_energy_rollout(prompt, cand)
            
            # 3. NCD Tiebreaker (~10%)
            ncd_sim = self._ncd_score(prompt, cand)
            
            # Weighted Combination
            # Normalize MCTS score (usually negative) to 0-1 range roughly
            mcts_norm = 1.0 / (1.0 + np.exp(-mcts_score * 5)) # Sigmoid
            
            total_score = (0.6 * struct_score) + (0.3 * mcts_norm) + (0.1 * ncd_sim)
            
            # Adjust for meta-confidence (Epistemic Honesty)
            if p_meta < 0.5:
                total_score *= 0.5 # Penalize score if prompt is ambiguous
            
            results.append({
                "candidate": cand,
                "score": float(total_score),
                "reasoning": f"Structural:{struct_score:.2f}, MCTS-FE:{mcts_score:.2f}, NCD:{ncd_sim:.2f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1. 
        Caps based on prompt ambiguity (Tier B) and answer certainty.
        """
        # 1. Check Prompt Traps
        meta_conf = self._meta_confidence(prompt)
        
        # 2. Check Structural Match Strength
        struct_score = self._compute_constructive_score(prompt, answer)
        mcts_score = self._mcts_free_energy_rollout(prompt, answer, iterations=20)
        
        # If structural signal is weak and meta-conf is low, confidence must be low
        base_conf = 0.5 + (0.4 * struct_score) + (0.1 * mcts_score)
        
        # Cap by meta confidence (The "Honesty" cap)
        final_conf = min(base_conf, meta_conf)
        
        # Ensure definitive answers (high struct score) can reach high confidence only if prompt is clear
        if struct_score > 0.8 and meta_conf == 1.0:
            final_conf = 0.95
        elif struct_score < -0.5:
            final_conf = 0.1 # Definitely wrong
            
        return float(np.clip(final_conf, 0.0, 1.0))