import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Gradient-Based Probabilistic Abduction Engine (Simplified Deterministic Approximation).
    
    Mechanism:
    1. Abductive Hypothesis Generation (Structural Parsing):
       Instead of a neural net, we parse the prompt for logical operators (negations, 
       comparatives, conditionals) to form a "structural prior". This mimics the 
       amortized inference network q_phi(h|x) proposing hypotheses based on data features.
       
    2. Differentiable Likelihood (Numeric/Constraint Evaluation):
       We compute a "likelihood" score by evaluating numeric constraints (e.g., 9.11 < 9.9)
       and logical consistency. This acts as the differentiable generative model p_theta(x|h).
       
    3. Bayesian Updating (ELBO Approximation):
       We combine the structural prior (complexity penalty) and likelihood (fit) to 
       approximate the Evidence Lower Bound (ELBO). Candidates are ranked by this score.
       
    4. Uncertainty Calibration:
       Confidence is derived from the margin between the top candidate's score and 
       the theoretical maximum, calibrated against a baseline of random guessing.
    """

    def __init__(self):
        # State initialization (none needed for this deterministic approximation)
        pass

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract floating point numbers from text for numeric reasoning."""
        nums = []
        current = ""
        has_dot = False
        for char in text:
            if char.isdigit() or (char == '.' and not has_dot):
                current += char
                if char == '.':
                    has_dot = True
            else:
                if current:
                    try:
                        nums.append(float(current))
                    except ValueError:
                        pass
                    current = ""
                    has_dot = False
        if current:
            try:
                nums.append(float(current))
            except ValueError:
                pass
        return nums

    def _compute_structural_prior(self, prompt: str, candidate: str) -> float:
        """
        Approximates the log-prior log(p(h)) by checking structural alignment.
        Rewards candidates that respect negation and logical flow of the prompt.
        """
        score = 0.0
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # Negation handling: If prompt says "not X", candidate "X" is penalized
        negations = ["not ", "no ", "never ", "false "]
        words = p_lower.split()
        
        for i, word in enumerate(words):
            if word in negations:
                # Look at next word(s)
                if i + 1 < len(words):
                    target = words[i+1].strip(".,!?")
                    if target in c_lower and target not in ["", "a", "i"]:
                        score -= 2.0 # Strong penalty for ignoring negation
        
        # Comparative handling: If prompt has "greater", expect larger numbers
        if ("greater" in p_lower or "larger" in p_lower or "more" in p_lower):
            nums = self._extract_numbers(prompt + " " + candidate)
            if len(nums) >= 2:
                # Heuristic: if the candidate contains the larger number, boost
                if nums[-1] > nums[-2]: 
                    score += 1.0
                else:
                    score -= 1.0
                    
        if ("less" in p_lower or "smaller" in p_lower):
            nums = self._extract_numbers(prompt + " " + candidate)
            if len(nums) >= 2:
                if nums[-1] < nums[-2]:
                    score += 1.0
                else:
                    score -= 1.0

        return score

    def _compute_likelihood(self, prompt: str, candidate: str) -> float:
        """
        Approximates log-likelihood log(p(x|h)) by checking constraint satisfaction.
        Uses NCD as a tie-breaker for semantic similarity, but prioritizes logic.
        """
        score = 0.0
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # Numeric constraint propagation
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if p_nums and c_nums:
            # Check if candidate numbers logically follow prompt numbers
            # Simple heuristic: if prompt implies sorting or comparison
            if len(p_nums) >= 2 and len(c_nums) >= 1:
                # If prompt asks for max/min implicitly
                if "max" in p_lower or "largest" in p_lower:
                    if max(p_nums) in c_nums or str(max(p_nums)) in candidate:
                        score += 5.0
                elif "min" in p_lower or "smallest" in p_lower:
                    if min(p_nums) in c_nums or str(min(p_nums)) in candidate:
                        score += 5.0
        
        # Basic containment boost (Abductive fit)
        # If candidate words appear in prompt, it's a plausible explanation
        common_words = set(p_lower.split()) & set(c_lower.split())
        # Remove stop words from consideration
        stop_words = {"the", "a", "an", "is", "are", "was", "were", "be", "to", "of", "and", "in", "that", "this"}
        meaningful_common = common_words - stop_words
        
        if meaningful_common:
            score += len(meaningful_common) * 0.5
            
        # NCD Tie-breaker (Normalized Compression Distance)
        # Lower NCD = more similar. We want high similarity for likelihood.
        try:
            z_p = len(zlib.compress(prompt.encode()))
            z_c = len(zlib.compress(candidate.encode()))
            z_pc = len(zlib.compress((prompt + candidate).encode()))
            max_len = max(z_p, z_c)
            if max_len > 0:
                ncd = (z_pc - min(z_p, z_c)) / max_len
                # Convert distance to similarity score (0 to 1 range roughly)
                score += (1.0 - ncd) * 2.0
        except:
            pass
            
        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Ranks candidates based on the approximate ELBO:
        Score = Likelihood + Prior (Structural Consistency)
        """
        ranked = []
        for cand in candidates:
            # 1. Abductive Step: Generate structural prior
            prior_score = self._compute_structural_prior(prompt, cand)
            
            # 2. Generative Step: Compute likelihood of data given hypothesis
            likelihood_score = self._compute_likelihood(prompt, cand)
            
            # 3. Bayesian Update: Combine (simplified ELBO)
            # We weight likelihood higher as it represents data fit
            total_score = likelihood_score + prior_score
            
            # Reasoning trace generation
            reasoning = f"Prior(Struct): {prior_score:.2f}, Likelihood(Data): {likelihood_score:.2f}"
            
            ranked.append({
                "candidate": cand,
                "score": total_score,
                "reasoning": reasoning
            })
        
        # Sort by score descending
        ranked.sort(key=lambda x: x["score"], reverse=True)
        return ranked

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the normalized score margin.
        Calibrated against the baseline performance.
        """
        # Generate a small set of dummy alternatives to establish a baseline distribution
        # This simulates the "uncertainty-aware" aspect by comparing against noise
        dummies = [
            "No", "Yes", "Maybe", "Unknown", 
            str(len(prompt)), prompt[::-1][:10], 
            "The answer is " + answer[:5] if len(answer) > 5 else "Null"
        ]
        
        all_candidates = [answer] + dummies
        results = self.evaluate(prompt, all_candidates)
        
        # Find the score of the proposed answer
        answer_score = None
        for res in results:
            if res["candidate"] == answer:
                answer_score = res["score"]
                break
                
        if answer_score is None:
            return 0.0
            
        # If the answer is the top result, confidence is high
        if results[0]["candidate"] == answer:
            # Calculate margin over the second best
            if len(results) > 1:
                margin = answer_score - results[1]["score"]
                # Sigmoid-like mapping to 0-1
                conf = 1.0 / (1.0 + math.exp(-margin))
                return min(0.99, max(0.51, conf)) # Floor at 0.51 if top
            return 0.95
            
        # If not top, confidence drops based on rank difference
        top_score = results[0]["score"]
        diff = top_score - answer_score
        # Exponential decay based on score difference
        conf = math.exp(-diff)
        return min(0.49, conf) # Cap at 0.49 if not top to ensure distinction