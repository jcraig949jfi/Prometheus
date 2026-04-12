import re
import math
import zlib
from typing import List, Dict, Any, Tuple, Optional

class ReasoningTool:
    """
    Maximum-Entropy Graph Bandit (MEGB) Reasoning Tool.
    
    Mechanism:
    1. Hypothesis Graph: Candidates are nodes. Edge weights are inverse NCD (similarity).
    2. Max-Entropy Prior: Uses structural constraints (length, complexity) to form a 
       least-biased prior P(h) ~ exp(-lambda * features).
    3. Bandit Selection: Scores candidates by balancing empirical reward (structural match)
       and graph-based uncertainty (exploration of diverse/central nodes).
       
    Epistemic Honesty (Tier B):
    Prioritizes detecting ambiguity, presupposition, and unanswerability.
    If meta-analysis detects traps, confidence is capped low regardless of candidate score.
    """

    # Presupposition and ambiguity triggers
    PRESUPPOSITION_TRIGGERS = [
        r"\bhave you stopped\b", r"\bwhy did.*fail\b", r"\bwhy.*stop\b", 
        r"\bwhen did.*stop\b", r"\bquit\b", r"\bassumed\b"
    ]
    SCOPE_AMBIGUITY = [r"\bevery.*a\b", r"\ball.*same\b"]
    PRONOUN_AMBIGUITY = [r"\bhe told.*he\b", r"\bshe told.*she\b", r"\bthey told.*they\b"]
    FALSE_DICHOTOMY = [r"\beither.*or\b", r"\bis it.*or\b"]
    SUBJECTIVITY = [r"\bbest\b", r"\bworst\b", r"\bfavorite\b", r"\bopinion\b"]

    def __init__(self):
        self.lambda_len = 0.1
        self.lambda_complex = 0.05
        self.exploration_weight = 0.3

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract floating point numbers for constructive computation."""
        return [float(x) for x in re.findall(r"-?\d+\.?\d*", text)]

    def _check_structural_logic(self, prompt: str, candidate: str) -> float:
        """
        Tier A: Structural parsing and constructive computation.
        Handles negations, comparatives, and numeric evaluation.
        """
        score = 0.0
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # 1. Numeric Evaluation (Constructive Computation)
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if p_nums:
            # If prompt has numbers, check if candidate computes them correctly
            # Simple heuristic: if prompt implies comparison, check candidate logic
            if "less than" in p_lower or "<" in prompt:
                if len(c_nums) >= 2 and c_nums[0] < c_nums[1]:
                    score += 0.5
                elif len(c_nums) == 1 and len(p_nums) == 2:
                    # Check if candidate picks the smaller one
                    if c_nums[0] == min(p_nums):
                        score += 0.5
            elif "greater than" in p_lower or ">" in prompt:
                if len(c_nums) >= 2 and c_nums[0] > c_nums[1]:
                    score += 0.5
            
            # Exact number match bonus
            if c_nums and c_nums[0] in p_nums:
                score += 0.2

        # 2. Negation Handling
        negation_words = ["no", "not", "never", "none", "neither"]
        has_negation = any(w in p_lower.split() for w in negation_words)
        candidate_negates = any(w in c_lower.split() for w in negation_words)
        
        if has_negation:
            if candidate_negates:
                score += 0.3
            else:
                score -= 0.3 # Penalty for ignoring negation
        
        # 3. Conditional/Transitivity (Simple keyword overlap for structure)
        # If prompt asks "If A then B", candidate should contain B or logical consequence
        if "if" in p_lower and "then" in p_lower:
            # Heuristic: Candidate length should be substantial enough to hold logic
            if len(candidate.split()) > 3:
                score += 0.1

        return min(1.0, max(0.0, score))

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Detects ambiguity, presupposition, and unanswerability.
        Returns a cap value (low if trap detected).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition Check
        for pattern in self.PRESUPPOSITION_TRIGGERS:
            if re.search(pattern, p_lower):
                return 0.25
        
        # 2. Scope Ambiguity
        for pattern in self.SCOPE_AMBIGUITY:
            if re.search(pattern, p_lower):
                # Only flag if question asks for clarification or specific scope
                if "same" in p_lower or "which" in p_lower:
                    return 0.25

        # 3. Pronoun Ambiguity
        if "who" in p_lower or "which one" in p_lower:
            for pattern in self.PRONOUN_AMBIGUITY:
                if re.search(pattern, p_lower):
                    return 0.25

        # 4. False Dichotomy
        if "either" in p_lower or "or" in p_lower:
            for pattern in self.FALSE_DICHOTOMY:
                if re.search(pattern, p_lower):
                    # Check if options are exhaustive (hard to detect, assume risky)
                    if "only" in p_lower:
                        return 0.25

        # 5. Subjectivity without criteria
        if any(re.search(p, p_lower) for p in self.SUBJECTIVITY):
            if "measure" not in p_lower and "data" not in p_lower:
                return 0.25

        # 6. Unanswerability (Missing info)
        if "impossible" in p_lower or "unknown" in p_lower:
            return 0.25
            
        return 1.0

    def _compute_maxent_prior(self, candidates: List[str]) -> List[float]:
        """
        Compute Maximum Entropy prior over candidates.
        Constraints: Expected length and complexity.
        P(h) proportional to exp(-lambda1 * len(h) - lambda2 * complexity(h))
        """
        if not candidates:
            return []
        
        scores = []
        for c in candidates:
            # Features
            f_len = len(c) / 100.0  # Normalized length
            f_comp = len(set(c)) / (len(c) + 1) # Character diversity as complexity proxy
            
            # Exponential family distribution
            energy = self.lambda_len * f_len + self.lambda_complex * f_comp
            scores.append(math.exp(-energy))
        
        # Normalize
        total = sum(scores)
        if total == 0:
            return [1.0/len(candidates)] * len(candidates)
        return [s / total for s in scores]

    def _graph_bandit_score(self, prompt: str, candidates: List[str]) -> List[float]:
        """
        Compute Graph Bandit scores.
        Reward: Structural match.
        Uncertainty: Graph centrality/diversity (via NCD similarity to others).
        """
        if not candidates:
            return []
        
        n = len(candidates)
        if n == 1:
            return [1.0]

        # 1. Build Similarity Matrix (Graph Edges)
        # Simulated for O(N^2) constraint, using NCD
        similarity_matrix = [[0.0]*n for _ in range(n)]
        for i in range(n):
            for j in range(i+1, n):
                sim = 1.0 - self._ncd(candidates[i], candidates[j])
                similarity_matrix[i][j] = sim
                similarity_matrix[j][i] = sim

        # 2. Compute Rewards (Structural Fit to Prompt)
        rewards = []
        for c in candidates:
            # Simple reward: overlap with prompt keywords + structural logic score
            struct_score = self._check_structural_logic(prompt, c)
            word_overlap = len(set(c.lower().split()) & set(prompt.lower().split())) / (len(c.split()) + 1)
            rewards.append(0.5 * struct_score + 0.5 * word_overlap)

        # 3. Compute Uncertainty (Graph Laplacian approximation)
        # High uncertainty = Low similarity to neighbors (Outlier) OR High centrality in sparse region
        # Here we use inverse average similarity as a proxy for "novelty/diversity"
        uncertainties = []
        for i in range(n):
            avg_sim = sum(similarity_matrix[i]) / (n - 1) if n > 1 else 0
            uncertainties.append(1.0 - avg_sim)

        # 4. Combine: UCB-style = Reward + Exploration * Uncertainty
        final_scores = []
        max_reward = max(rewards) if rewards else 0
        for i in range(n):
            # Normalize reward
            norm_reward = rewards[i] / (max_reward + 1e-6)
            score = norm_reward + self.exploration_weight * uncertainties[i]
            final_scores.append(score)
            
        return final_scores

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        if not candidates:
            return []

        # 1. Meta-Confidence Check (Epistemic Honesty)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. MaxEnt Priors
        priors = self._compute_maxent_prior(candidates)
        
        # 3. Graph Bandit Scoring
        bandit_scores = self._graph_bandit_score(prompt, candidates)
        
        # 4. NCD Tiebreaker (Max 15% influence)
        ncd_scores = []
        for c in candidates:
            # Distance to prompt is a proxy for relevance in absence of other signals
            dist = self._ncd(prompt, c)
            ncd_scores.append(1.0 - dist) # Convert to similarity
            
        # Normalize NCD
        max_ncd = max(ncd_scores) if ncd_scores else 1.0
        ncd_norm = [s / (max_ncd + 1e-6) for s in ncd_scores]

        # Final Aggregation
        # Score = (Structural/Bandit * 0.85) + (NCD * 0.15)
        final_results = []
        for i, c in enumerate(candidates):
            base_score = bandit_scores[i] * 0.85 + ncd_norm[i] * 0.15
            
            # Apply MaxEnt Prior adjustment (smoothing)
            adjusted_score = base_score * (1.0 + 0.1 * priors[i])
            
            # Apply Epistemic Cap
            if meta_cap < 0.3:
                # If the question is a trap, penalize high confidence unless it's an explicit "I don't know"
                if "cannot be determined" in c.lower() or "ambiguous" in c.lower() or "unknown" in c.lower():
                    final_conf = 0.9 # Reward honesty
                else:
                    final_conf = min(adjusted_score, meta_cap)
            else:
                final_conf = min(adjusted_score, 0.95) # Cap max confidence to avoid overconfidence

            final_results.append({
                "candidate": c,
                "score": final_conf,
                "reasoning": f"Structural: {bandit_scores[i]:.2f}, Prior: {priors[i]:.2f}, MetaCap: {meta_cap:.2f}"
            })

        # Sort by score descending
        final_results.sort(key=lambda x: x["score"], reverse=True)
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Calls _meta_confidence to cap based on prompt properties.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # Evaluate the specific answer against the prompt
        res_list = self.evaluate(prompt, [answer])
        if not res_list:
            return 0.0
            
        raw_score = res_list[0]["score"]
        
        # If meta-analysis says the question is trash, cap the confidence
        if meta_cap < 0.3:
            # Unless the answer explicitly addresses the ambiguity
            if "ambiguous" in answer.lower() or "cannot" in answer.lower():
                return 0.8
            return min(raw_score, meta_cap)
            
        return min(raw_score, 0.95)