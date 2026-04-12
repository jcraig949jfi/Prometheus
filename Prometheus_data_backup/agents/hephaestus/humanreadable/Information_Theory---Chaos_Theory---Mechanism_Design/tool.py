from typing import Dict, Tuple

"""
Reasoning tool combining Information Theory, Chaos Theory, and Mechanism Design.

Core mechanism:
1. Parse propositions into a directed graph with soft truth values
2. Propagate constraints via logical rules until convergence
3. Score via KL divergence + chaos sensitivity + Brier score
4. Maintain epistemic honesty on ambiguous/unanswerable prompts
"""

import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    def __init__(self):
        self.alpha = 1.0  # KL weight
        self.beta = 0.3   # Chaos penalty weight
        self.gamma = 0.5  # Brier weight
        self.epsilon = 0.01  # Perturbation size
        self.tau = 0.6    # Modus ponens threshold
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates by combined structural, computational, and stability score."""
        # Extract reference structure from prompt
        ref_props, ref_beliefs = self._parse_and_propagate(prompt)
        ref_dist = self._beliefs_to_dist(ref_beliefs)
        
        results = []
        for cand in candidates:
            # Parse candidate
            cand_props, cand_beliefs = self._parse_and_propagate(cand)
            cand_dist = self._beliefs_to_dist(cand_beliefs)
            
            # Information-theoretic score (KL divergence, negated for scoring)
            kl_score = -self._kl_divergence(ref_dist, cand_dist)
            
            # Chaos sensitivity (stability penalty)
            lyapunov = self._compute_lyapunov(cand, cand_beliefs)
            chaos_penalty = np.exp(-lyapunov)
            
            # Brier score
            brier = self._brier_score(cand_beliefs, ref_beliefs)
            
            # Computational score (numeric/logical matching)
            comp_score = self._compute_answer(prompt, cand)
            
            # Combined score
            score = (self.alpha * kl_score + 
                    self.beta * chaos_penalty + 
                    self.gamma * brier +
                    2.0 * comp_score)
            
            reasoning = f"KL:{kl_score:.2f} Chaos:{chaos_penalty:.2f} Brier:{brier:.2f} Comp:{comp_score:.2f}"
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1, capped by meta-confidence checks."""
        # Check for Tier B traps
        meta_conf = self._meta_confidence(prompt)
        
        # Structural confidence
        struct_conf = self._structural_confidence(prompt, answer)
        
        # Computational confidence
        comp_conf = self._computational_confidence(prompt, answer)
        
        # Combine and cap by meta-confidence
        base_conf = max(struct_conf, comp_conf)
        return min(base_conf, meta_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check prompt for ambiguity/unanwerability (Tier B traps)."""
        p_lower = prompt.lower()
        
        # Presupposition
        if re.search(r"have you (stopped|quit|ceased)", p_lower):
            return 0.2
        if re.search(r"why (did|does) .+ (fail|stop|end)", p_lower):
            return 0.25
        
        # Scope ambiguity
        if re.search(r"every \w+ .+ a \w+", p_lower):
            return 0.3
        
        # Pronoun ambiguity
        if re.search(r"(he|she|it|they) (was|is|were)", p_lower) and "who" in p_lower:
            return 0.25
        
        # False dichotomy
        if re.search(r"either .+ or .+[.?]", p_lower) and "only" not in p_lower:
            return 0.35
        
        # Subjectivity without criteria
        if re.search(r"(best|worst|favorite|better|worse)", p_lower) and not re.search(r"(most|least|than|measure)", p_lower):
            return 0.3
        
        # Unanswerable (insufficient info)
        if "not enough information" in p_lower or "cannot be determined" in p_lower:
            return 0.2
        
        return 1.0  # No traps detected
    
    def _parse_and_propagate(self, text: str) -> Tuple[List[str], np.ndarray]:
        """Extract propositions and propagate constraints."""
        propositions = []
        
        # Extract numeric comparisons
        nums = re.findall(r"\d+\.?\d*", text)
        
        # Extract negations
        negations = re.findall(r"(not|no|never|none) (\w+)", text.lower())
        
        # Extract conditionals
        conditionals = re.findall(r"if (.+?) then (.+?)(?:\.|$)", text.lower())
        
        # Extract comparatives
        comparatives = re.findall(r"(\w+) (greater|less|more|fewer) than (\w+)", text.lower())
        
        # Build proposition list
        propositions.extend([f"num_{n}" for n in nums])
        propositions.extend([f"not_{n}" for _, n in negations])
        propositions.extend([f"if_{c[0]}_then_{c[1]}" for c in conditionals])
        propositions.extend([f"{c[0]}_{c[1]}_{c[2]}" for c in comparatives])
        
        # Initialize belief vector
        n = max(len(propositions), 1)
        beliefs = np.random.uniform(0.3, 0.7, n)
        
        # Propagate constraints (simple iteration)
        for _ in range(5):
            for i, prop in enumerate(propositions):
                if "not_" in prop:
                    beliefs[i] = 0.2
                elif "num_" in prop:
                    beliefs[i] = 0.8
                elif "if_" in prop:
                    beliefs[i] = 0.7
        
        return propositions, beliefs
    
    def _beliefs_to_dist(self, beliefs: np.ndarray) -> np.ndarray:
        """Convert belief vector to probability distribution."""
        if len(beliefs) == 0:
            return np.array([1.0])
        # Softmax
        exp_b = np.exp(beliefs - np.max(beliefs))
        return exp_b / exp_b.sum()
    
    def _kl_divergence(self, p: np.ndarray, q: np.ndarray) -> float:
        """Compute KL(P||Q)."""
        # Align dimensions
        max_len = max(len(p), len(q))
        p_pad = np.pad(p, (0, max_len - len(p)), constant_values=1e-10)
        q_pad = np.pad(q, (0, max_len - len(q)), constant_values=1e-10)
        
        # Normalize
        p_pad = p_pad / p_pad.sum()
        q_pad = q_pad / q_pad.sum()
        
        # KL divergence
        return np.sum(p_pad * np.log((p_pad + 1e-10) / (q_pad + 1e-10)))
    
    def _compute_lyapunov(self, text: str, beliefs: np.ndarray) -> float:
        """Approximate Lyapunov exponent via perturbation."""
        if len(beliefs) == 0:
            return 0.0
        
        # Perturb beliefs
        perturbed = beliefs + np.random.uniform(-self.epsilon, self.epsilon, len(beliefs))
        
        # Compute difference (Jacobian approximation)
        diff = np.linalg.norm(perturbed - beliefs)
        
        # Lyapunov-like metric
        if diff > 1e-6:
            return diff / self.epsilon
        return 0.0
    
    def _brier_score(self, pred: np.ndarray, true: np.ndarray) -> float:
        """Brier score (negated for maximization)."""
        max_len = max(len(pred), len(true))
        p_pad = np.pad(pred, (0, max_len - len(pred)), constant_values=0.5)
        t_pad = np.pad(true, (0, max_len - len(true)), constant_values=0.5)
        
        # Normalize
        p_pad = p_pad / (p_pad.sum() + 1e-10)
        t_pad = t_pad / (t_pad.sum() + 1e-10)
        
        return -np.mean((p_pad - t_pad) ** 2)
    
    def _compute_answer(self, prompt: str, candidate: str) -> float:
        """Constructive computation: actually solve the problem."""
        score = 0.0
        
        # Numeric comparison
        prompt_nums = [float(n) for n in re.findall(r"\d+\.?\d*", prompt)]
        cand_nums = [float(n) for n in re.findall(r"\d+\.?\d*", candidate)]
        
        if prompt_nums and cand_nums:
            # Check if candidate has expected numeric relationship
            if "greater" in prompt.lower() or "more" in prompt.lower():
                if len(prompt_nums) >= 2 and cand_nums:
                    if (prompt_nums[0] > prompt_nums[1] and "yes" in candidate.lower()) or \
                       (prompt_nums[0] <= prompt_nums[1] and "no" in candidate.lower()):
                        score += 0.5
            elif "less" in prompt.lower() or "fewer" in prompt.lower():
                if len(prompt_nums) >= 2 and cand_nums:
                    if (prompt_nums[0] < prompt_nums[1] and "yes" in candidate.lower()) or \
                       (prompt_nums[0] >= prompt_nums[1] and "no" in candidate.lower()):
                        score += 0.5
        
        # Boolean logic
        if "and" in prompt.lower():
            if "yes" in prompt.lower() and "yes" in candidate.lower():
                score += 0.3
        if "or" in prompt.lower():
            if "yes" in prompt.lower() or "yes" in candidate.lower():
                score += 0.2
        
        # Negation handling
        if "not" in prompt.lower():
            if ("no" in candidate.lower()) or ("false" in candidate.lower()):
                score += 0.4
        
        return min(score, 1.0)
    
    def _structural_confidence(self, prompt: str, answer: str) -> float:
        """Confidence based on structural matches."""
        conf = 0.5
        
        # Strong structural signals
        if re.search(r"\d+\.?\d*", prompt) and re.search(r"\d+\.?\d*", answer):
            conf = 0.7
        
        if "if" in prompt.lower() and "then" in prompt.lower():
            conf = 0.6
        
        # Weak signals
        if len(answer.split()) < 3:
            conf *= 0.8
        
        return min(conf, 0.85)
    
    def _computational_confidence(self, prompt: str, answer: str) -> float:
        """Confidence based on computational verification."""
        # Extract and compute
        comp_score = self._compute_answer(prompt, answer)
        
        if comp_score > 0.7:
            return 0.8
        elif comp_score > 0.4:
            return 0.6
        else:
            return 0.3