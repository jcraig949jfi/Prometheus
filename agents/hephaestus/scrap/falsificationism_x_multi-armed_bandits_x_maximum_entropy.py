import re
import math
import zlib
import numpy as np
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    A reasoning tool combining Falsificationism, Multi-Armed Bandits (UCB), 
    and Maximum Entropy principles with strict epistemic honesty.
    
    Mechanism:
    1. Structural Parsing: Extracts logical features (negations, comparatives, causality).
    2. MaxEnt Constraint Satisfaction: Uses projected gradient ascent to find weights 
       that satisfy logical constraints derived from the prompt, maximizing entropy.
    3. Falsification Scoring: Candidates are scored by how well they satisfy the 
       learned logical constraints (low falsification = high score).
    4. Bandit-based Ranking: Treats candidates as arms, using UCB to prioritize 
       evaluation of uncertain but promising candidates during the internal ranking loop.
    5. Epistemic Honesty: Meta-analysis of the prompt detects ambiguity, presupposition, 
       and unanswerability, capping confidence scores to prevent overconfidence.
    """

    def __init__(self):
        # Regex patterns for structural features
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|nobody|nothing|nowhere)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse|before|after)\b|[<>]', re.I),
            'conditional': re.compile(r'\b(if|then|unless|otherwise|provided|when)\b', re.I),
            'causal': re.compile(r'\b(because|therefore|thus|hence|leads to|results in|causes)\b', re.I),
            'numeric': re.compile(r'\d+(\.\d+)?'),
            'presupposition': re.compile(r'\b(have you stopped|did you stop|why did|how did|when did)\b', re.I),
            'false_dichotomy': re.compile(r'\b(either|or both|only option|must choose)\b', re.I),
            'subjectivity': re.compile(r'\b(best|worst|favorite|opinion|believe)\b', re.I),
            'pronoun_ambiguity': re.compile(r'\b(he|she|they|him|her|it)\b.*\bwho\b', re.I)
        }
        self.epsilon = 1e-6

    def _extract_features(self, text: str) -> np.ndarray:
        """Extract binary structural features from text."""
        text_lower = text.lower()
        features = []
        # Order matters for vector consistency
        keys = ['negation', 'comparative', 'conditional', 'causal']
        for k in keys:
            match = 1.0 if self.patterns[k].search(text_lower) else 0.0
            features.append(match)
        
        # Numeric presence
        nums = self.patterns['numeric'].findall(text_lower)
        features.append(1.0 if len(nums) > 1 else 0.0) # Multiple numbers imply comparison potential
        features.append(1.0 if len(nums) > 0 else 0.0) # Any number
        
        return np.array(features, dtype=np.float64)

    def _max_entropy_weights(self, prompt_features: np.ndarray, candidate_features: np.ndarray) -> np.ndarray:
        """
        Compute weights via Maximum Entropy principle.
        Maximizes entropy subject to expected feature counts matching the prompt.
        Uses projected gradient ascent.
        """
        if len(candidate_features) == 0:
            return np.zeros_like(prompt_features)
        
        k = len(prompt_features)
        w = np.zeros(k) # Initialize weights
        phi_prompt = prompt_features
        
        # Gradient Ascent parameters
        lr = 0.1
        for _ in range(50): # Fixed iterations for determinism and speed
            # Compute probabilities p(x) proportional to exp(w . phi(x))
            # x here represents each candidate acting as a possible world
            scores = np.dot(candidate_features, w)
            scores -= np.max(scores) # Stability
            exp_scores = np.exp(scores)
            p = exp_scores / (np.sum(exp_scores) + self.epsilon)
            
            # Expected feature counts under current model
            expected_counts = np.dot(p, candidate_features)
            
            # Gradient: Prompt features (observed) - Expected features
            grad = phi_prompt - expected_counts
            
            # Update weights
            w += lr * grad
            
            # Regularization to prevent explosion (soft constraint)
            w *= 0.99 
            
        return w

    def _compute_falsification_score(self, prompt: str, candidate: str, w: np.ndarray) -> float:
        """
        Compute falsification score. 
        High score = High probability of being FALSE (Falsified).
        Low score = Consistent with constraints.
        """
        psi = self._extract_features(candidate)
        # Compatibility score s_a = sigmoid(w . psi)
        logit = np.dot(w, psi)
        # Logistic function
        s_a = 1.0 / (1.0 + np.exp(-logit))
        
        # Falsification estimate
        return 1.0 - s_a

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z = zlib.compress
        l1 = len(z(s1.encode()))
        l2 = len(z(s2.encode()))
        l12 = len(z((s1 + s2).encode()))
        if min(l1, l2) == 0: return 1.0
        return (l12 - min(l1, l2)) / max(l1, l2)

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Analyzes prompt structure for ambiguity, presupposition, and unanswerability.
        Returns a cap on confidence.
        """
        p_lower = prompt.lower()
        score = 1.0
        
        # 1. Presupposition traps
        if self.patterns['presupposition'].search(p_lower):
            score = min(score, 0.25)
            
        # 2. False Dichotomy
        if self.patterns['false_dichotomy'].search(p_lower):
            score = min(score, 0.4)
            
        # 3. Subjectivity without data
        if self.patterns['subjectivity'].search(p_lower):
            score = min(score, 0.3)
            
        # 4. Pronoun Ambiguity (simplified heuristic)
        if 'who' in p_lower and any(p in p_lower for p in ['he ', 'she ', 'they ']):
            score = min(score, 0.3)
            
        # 5. Length/Complexity heuristic for unanswerability
        # If prompt is very short and lacks numbers/logic words, it might be ambiguous
        words = prompt.split()
        if len(words) < 5 and not self.patterns['numeric'].search(prompt):
            score = min(score, 0.5)

        return score

    def _run_bandit_ranking(self, prompt: str, candidates: List[str]) -> List[Tuple[str, float, str]]:
        """
        Internal logic to rank candidates using Falsification + Bandit UCB.
        Returns list of (candidate, score, reasoning).
        """
        if not candidates:
            return []
            
        # 1. Extract Features
        prompt_feats = self._extract_features(prompt)
        cand_feats = np.array([self._extract_features(c) for c in candidates])
        
        # 2. MaxEnt Weight Learning
        # We learn weights that make the distribution of features in "valid" worlds 
        # match the prompt's structural constraints.
        w = self._max_entropy_weights(prompt_feats, cand_feats)
        
        # 3. Bandit Initialization
        n_arms = len(candidates)
        n_i = np.zeros(n_arms)
        mu_i = np.zeros(n_arms) # Empirical mean falsification
        
        # Pre-calculate all falsification scores (simulation of "evaluation")
        # In a real interactive system, this would be lazy. Here we simulate rounds.
        true_falsification = np.array([
            self._compute_falsification_score(prompt, c, w) for c in candidates
        ])
        
        # Structural bonus: If prompt has numbers, check numeric consistency
        # This boosts the "Reasoning" score by actually calculating if possible
        numeric_bonus = np.zeros(n_arms)
        prompt_nums = self.patterns['numeric'].findall(prompt.lower())
        if len(prompt_nums) > 0 and len(prompt_nums) <= 5:
            try:
                target = float(prompt_nums[-1]) # Simplified: assume last number is target or constraint
                for i, c in enumerate(candidates):
                    c_nums = self.patterns['numeric'].findall(c.lower())
                    if c_nums:
                        val = float(c_nums[0])
                        # Heuristic: If candidate number matches prompt number structure roughly
                        if abs(val - target) < 1e-6:
                            numeric_bonus[i] = 0.2 # Reduce falsification
            except:
                pass

        # Adjusted falsification for final scoring
        adjusted_falsification = np.clip(true_falsification - numeric_bonus, 0.0, 1.0)

        # 4. Bandit Simulation (UCB)
        # We simulate T rounds to let the bandit explore and exploit
        T = n_arms * 2 + 5 
        for t in range(1, T + 1):
            ucb_values = []
            for i in range(n_arms):
                if n_i[i] == 0:
                    ucb = float('inf')
                else:
                    # UCB1 formula
                    exploration = math.sqrt((2 * math.log(t + 1)) / (n_i[i] + self.epsilon))
                    ucb = mu_i[i] + exploration
                ucb_values.append(ucb)
            
            # Select arm
            arm = int(np.argmax(ucb_values))
            
            # Observe reward (falsification score)
            # Note: We want to MINIMIZE falsification, but UCB maximizes reward.
            # So we treat "Low Falsification" as "High Reward"? 
            # Actually, the prompt says: mu = empirical mean falsification. 
            # Select arm with highest UCB of falsification? 
            # No, we want to find the TRUE falsification rate to rank them.
            # The prompt says: "select arm with highest UCB ... evaluate ... update mu".
            # Then "Final ranking by descending mu (lowest estimated falsification)".
            # This implies we use UCB to efficiently estimate mu for all, then sort.
            
            r = adjusted_falsification[arm]
            n_i[arm] += 1
            mu_i[arm] += (r - mu_i[arm]) / n_i[arm]

        # 5. NCD Tiebreaker (Max 15% influence)
        # If falsification scores are very close, use NCD to prompt similarity
        ncd_scores = np.array([self._ncd(prompt, c) for c in candidates])
        # Normalize NCD to 0-1 range where 1 is good (low distance)
        # NCD is 0 (identical) to 1 (different). We want low NCD -> high score.
        ncd_utility = 1.0 - ncd_scores 
        
        # Combine: Score = (1 - Falsification) * 0.85 + NCD_utility * 0.15
        # But only if structural signal is weak. If structural signal is strong, NCD is minor.
        final_scores = (1.0 - mu_i) * 0.85 + (ncd_utility * 0.15)
        
        # Generate reasoning strings
        results = []
        for i, c in enumerate(candidates):
            f_score = mu_i[i]
            reasoning = f"Falsification prob: {f_score:.2f}. "
            if f_score < 0.3:
                reasoning += "Consistent with logical constraints."
            elif f_score > 0.7:
                reasoning += "High conflict with prompt structure."
            else:
                reasoning += "Ambiguous structural alignment."
            
            results.append((c, final_scores[i], reasoning))
            
        # Sort by score descending
        results.sort(key=lambda x: x[1], reverse=True)
        return results

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        ranked = self._run_bandit_ranking(prompt, candidates)
        meta_cap = self._meta_confidence(prompt)
        
        output = []
        for cand, score, reason in ranked:
            # Adjust score based on meta-confidence if the whole prompt is suspect
            # But evaluate() returns relative ranking. 
            # We adjust the 'score' slightly to reflect global uncertainty if needed,
            # but primarily we rely on the ranking.
            # For Tier B, if the prompt is bad, all scores should arguably be lower confidence,
            # but the relative order might still hold. 
            # The instruction says confidence() must cap. evaluate() returns ranked list.
            # We will keep relative scores but ensure the top score isn't misleadingly perfect if meta is low.
            if meta_cap < 0.5:
                score *= meta_cap * 2 # Dampen scores significantly
            
            output.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reason
            })
        return output

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-analysis of the prompt.
        """
        # 1. Meta Confidence Cap (Tier B)
        cap = self._meta_confidence(prompt)
        
        # 2. Structural Evaluation
        # Run a mini-evaluation to see how well this specific answer fits
        # We treat the single answer as a candidate list of 1
        # But we need context of "wrongness". 
        # Instead, we compute falsification directly.
        
        prompt_feats = self._extract_features(prompt)
        ans_feats = self._extract_features(answer).reshape(1, -1)
        prompt_feats_2d = prompt_feats.reshape(1, -1) # Dummy for function
        
        # Use a dummy set for MaxEnt weight calculation to avoid errors
        # We assume the answer itself provides the feature space
        w = self._max_entropy_weights(prompt_feats, ans_feats)
        
        falsification = self._compute_falsification_score(prompt, answer, w)
        
        # Base confidence is inverse of falsification
        base_conf = 1.0 - falsification
        
        # Apply numeric check specifically for this answer
        p_nums = self.patterns['numeric'].findall(prompt.lower())
        a_nums = self.patterns['numeric'].findall(answer.lower())
        if p_nums and a_nums:
            try:
                # Simple consistency check
                p_val = float(p_nums[-1])
                a_val = float(a_nums[0])
                if math.isclose(p_val, a_val, rel_tol=1e-5):
                    base_conf = min(base_conf + 0.2, 1.0)
                else:
                    base_conf *= 0.5 # Penalty for mismatched numbers
            except: pass

        # 3. Apply Cap
        final_conf = min(base_conf, cap)
        
        # 4. Floor for "No structural match"
        if np.all(ans_feats == 0) and np.all(prompt_feats != 0):
            # Answer has no structural features while prompt does
            final_conf = min(final_conf, 0.3)

        return float(final_conf)