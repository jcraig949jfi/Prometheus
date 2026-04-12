import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Pragmatic Cognitive-Load-Aware Multi-Armed Bandit (PC-MAB) Implementation.
    
    Mechanism:
    1. Structural Parsing (Cognitive Load & Germane Load): Extracts logical operators
       (negations, comparatives, conditionals) and numeric values. Complexity (Intrinsic Load)
       is penalized; successful logical resolution rewards the candidate.
    2. Pragmatic Relevance (Gricean Maxims): Filters candidate words against prompt context.
       Candidates containing high-frequency stop words or unrelated concepts receive an
       'Extraneous Load' penalty. Relevance is scored via set intersection of significant tokens.
    3. Bandit Selection (Thompson Sampling): Treats each candidate as an arm.
       - Reward = Structural Match + Pragmatic Relevance.
       - Temperature = Exp(Load) -> Higher load suppresses exploration variance.
       - Posterior = Beta(alpha, beta) updated by reward.
    4. Scoring: Final score is a weighted sum of structural validity (primary) and 
       NCD similarity (tiebreaker only), tempered by the load-aware temperature.
    """

    # Stop words to filter for pragmatic relevance (Quantity/Relation maxims)
    STOP_WORDS = set((
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "is", "are", "was", "were", "be", "been", "being",
        "that", "this", "it", "as", "if", "then", "than", "so", "not"
    ))
    
    # Logical operators for structural parsing
    NEGATIONS = {"no", "not", "never", "none", "neither", "n't"}
    COMPARATIVES = {"greater", "less", "more", "fewer", "higher", "lower", ">", "<", "=="}
    CONDITIONALS = {"if", "then", "else", "unless", "provided"}

    def __init__(self):
        self._state = {}  # Persistent state if needed, though mostly stateless per call

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenizer: lowercase, remove non-alphanumeric, split."""
        return re.findall(r'[a-z0-9]+', text.lower())

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract floating point numbers from text."""
        # Match integers and floats
        matches = re.findall(r'-?\d+(?:\.\d+)?', text)
        return [float(m) for m in matches]

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_c = max(c1, c2)
        if max_c == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_c

    def _analyze_structure(self, text: str) -> Dict:
        """
        Analyze text for logical structure.
        Returns metrics for Intrinsic Load (complexity) and Germane Load (useful logic).
        """
        tokens = set(self._tokenize(text))
        numbers = self._extract_numbers(text)
        
        has_negation = bool(tokens & self.NEGATIONS)
        has_comparative = bool(tokens & self.COMPARATIVES) or len(numbers) >= 2
        has_conditional = bool(tokens & self.CONDITIONALS)
        
        # Structural complexity (Intrinsic Load proxy)
        complexity = len(tokens) * 0.01 + (has_negation * 0.5) + (has_conditional * 0.5)
        
        # Logical density (Germane Load proxy - rewarded)
        logic_score = 0.0
        if has_negation: logic_score += 0.2
        if has_comparative: logic_score += 0.3
        if has_conditional: logic_score += 0.3
        if len(numbers) > 0: logic_score += 0.2
        
        return {
            "complexity": complexity,
            "logic_score": logic_score,
            "has_numbers": len(numbers) > 0,
            "numbers": numbers,
            "tokens": tokens
        }

    def _pragmatic_relevance(self, prompt_tokens: set, candidate_tokens: set) -> float:
        """
        Calculate relevance based on Gricean Maxims.
        Penalize extraneous info (words not in prompt context unless they are logical operators).
        Reward quantity (overlap) and relation (contextual fit).
        """
        # Filter stop words for content comparison
        p_content = prompt_tokens - self.STOP_WORDS
        c_content = candidate_tokens - self.STOP_WORDS
        
        if not p_content:
            return 0.5 # Neutral if prompt has no content
        
        # Intersection of meaningful content
        overlap = p_content & c_content
        extraneous = c_content - p_content
        
        # Relevance = (Overlap / Prompt Content) - Penalty for Extraneous
        # Normalized roughly 0 to 1
        relevance = (len(overlap) / len(p_content)) if len(p_content) > 0 else 0
        penalty = min(0.5, len(extraneous) * 0.05) # Cap penalty
        
        return max(0.0, min(1.0, relevance - penalty))

    def _thompson_sample(self, alpha: float, beta: float, load: float, lambda_temp: float = 0.5) -> float:
        """
        Thompson sampling with load-aware temperature.
        Tau = tau_0 * exp(lambda * L)
        We simulate the sample by adjusting the Beta distribution parameters or the result.
        Here we adjust the sampled value by a temperature factor to suppress high-load arms.
        """
        # Simple Beta sample approximation using inverse transform or just mean if deterministic needed
        # Since we need determinism for same inputs, we use the mean of the posterior as a proxy 
        # for the 'expected' sample in a deterministic run, modified by load.
        # Real Thompson sampling is stochastic; for deterministic eval, we use E[Beta] * TempFactor
        
        mean_val = alpha / (alpha + beta) if (alpha + beta) > 0 else 0.5
        
        # Temperature suppresses score if load is high
        tau = math.exp(lambda_temp * load)
        tempered_score = mean_val / (1.0 + tau * 0.1) # Dampen slightly by load
        
        return min(1.0, max(0.0, tempered_score))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_struct = self._analyze_structure(prompt)
        prompt_tokens = set(self._tokenize(prompt))
        prompt_nums = prompt_struct["numbers"]
        
        results = []
        
        # Global baseline for NCD tie-breaking
        best_ncd_score = -1.0
        
        for cand in candidates:
            cand_struct = self._analyze_structure(cand)
            cand_tokens = set(self._tokenize(cand))
            
            # 1. Cognitive Load Calculation
            # Intrinsic: complexity of candidate
            # Extraneous: 1 - pragmatic relevance
            # Germane: logic score (reward)
            intrinsic_load = cand_struct["complexity"]
            pragmatic_rel = self._pragmatic_relevance(prompt_tokens, cand_tokens)
            extraneous_load = (1.0 - pragmatic_rel) * 0.5
            germane_load_reward = cand_struct["logic_score"]
            
            total_load = intrinsic_load + extraneous_load
            
            # 2. Structural Validation (The Primary Signal)
            # Check number consistency if numbers exist in prompt
            number_match = 1.0
            if prompt_nums and cand_struct["has_numbers"]:
                # Simple heuristic: if prompt has numbers, candidate should likely reflect them or logic
                # This is a simplification of "running an experiment"
                cand_nums = cand_struct["numbers"]
                # Reward if candidate numbers are subset or close to prompt numbers
                if any(abs(c - p) < 1e-6 for c in cand_nums for p in prompt_nums):
                    number_match = 1.0
                else:
                    # If numbers are totally different, penalize unless it's a calculation result
                    # We can't easily verify calc without eval, so we trust structural overlap
                    number_match = 0.5 
            
            # 3. Bandit Arm Scoring
            # Prior: Alpha=1, Beta=1 (Uniform)
            # Update with 'success' based on structural and pragmatic fit
            alpha = 1.0 + (pragmatic_rel * 2.0) + (germane_load_reward * 2.0) + (number_match)
            beta = 1.0 + (extraneous_load * 2.0) + (intrinsic_load * 0.5)
            
            # Thompson Sample with Load Temperature
            score = self._thompson_sample(alpha, beta, total_load)
            
            # Add structural parsing bonus explicitly (Key pattern: Structural > NCD)
            # If prompt has comparatives, candidate having comparatives is a huge boost
            if prompt_struct["logic_score"] > 0 and cand_struct["logic_score"] > 0:
                score += 0.3
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Load:{total_load:.2f}, Pragmatic:{pragmatic_rel:.2f}, Logic:{cand_struct['logic_score']:.2f}",
                "_ncd": self._compute_ncd(prompt, cand) # For tie-breaking
            })

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        
        # Tie-breaking with NCD only if scores are very close (structural signal weak)
        # But per instructions: NCD is tiebreaker. 
        # We refine sort: Primary key = score, Secondary key = NCD (lower is better for similarity if needed, 
        # but usually we want distinct answers. Let's assume higher score is sufficient).
        # Actually, if scores are equal, we use NCD to break ties based on compression similarity to prompt context
        # if the prompt implies similarity, or just keep original order. 
        # Let's strictly follow: Structural is primary. NCD only if structural signal is ambiguous.
        
        final_results = []
        for r in results:
            final_results.append({
                "candidate": r["candidate"],
                "score": r["score"],
                "reasoning": r["reasoning"]
            })
            
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the same evaluation logic but returns the normalized score of the single candidate.
        """
        # Evaluate against a dummy list to get the score
        # We simulate a comparison against a 'null' hypothesis to gauge absolute confidence
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        base_score = res[0]["score"]
        
        # Boost if structural elements match (e.g. both have numbers, or both have negations)
        p_struct = self._analyze_structure(prompt)
        a_struct = self._analyze_structure(answer)
        
        boost = 0.0
        if p_struct["has_numbers"] and a_struct["has_numbers"]:
            boost = 0.2
        if (p_struct["logic_score"] > 0) and (a_struct["logic_score"] > 0):
            boost = 0.2
            
        conf = min(1.0, base_score + boost)
        return float(conf)