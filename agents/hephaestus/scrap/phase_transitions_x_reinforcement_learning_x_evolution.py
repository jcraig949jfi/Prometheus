import zlib
import re
import math

class ReasoningTool:
    """
    Criticality-Driven Evolutionary Reasoner (CERL) Approximation.
    
    Mechanism:
    1. Structural Parsing (Exploitation): Extracts logical constraints (negations, 
       comparatives, conditionals) to form a rigid 'fitness landscape'.
    2. Order Parameter (Criticality): Computes the variance of structural match scores 
       across candidates. High variance indicates the system is near a 'phase transition' 
       (uncertainty between logical clusters).
    3. Evolutionary Mutation (Exploration): If criticality is detected (high variance), 
       the scoring function injects a 'mutation bonus' for candidates with higher 
       lexical diversity (simulating exploration of novel hypothesis space).
    4. Selection: Final score is a weighted sum of structural adherence and NCD-based 
       compression, tuned by the criticality state.
    """

    def __init__(self):
        self.negation_words = {"no", "not", "never", "none", "neither", "nobody", "nothing"}
        self.comparative_ops = {">", "<", ">", "<", "more", "less", "greater", "smaller"}
        self.conditionals = {"if", "then", "else", "unless", "provided"}

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """Scores based on logical constraint satisfaction (Negation, Comparatives, Conditionals)."""
        score = 0.0
        p_low = prompt.lower()
        c_low = candidate.lower()
        
        # 1. Negation Consistency
        # If prompt has negation, candidate should ideally reflect it or not contradict it directly
        p_has_neg = any(w in p_low.split() for w in self.negation_words)
        c_has_neg = any(w in c_low.split() for w in self.negation_words)
        
        if p_has_neg:
            score += 0.4 if c_has_neg else -0.2 # Reward acknowledging negation
        else:
            score += 0.2 if not c_has_neg else -0.3 # Penalize spurious negation

        # 2. Comparative Logic (Simplified numeric detection)
        # Detect numbers in prompt and candidate
        p_nums = re.findall(r"[-+]?\d*\.?\d+", p_low)
        c_nums = re.findall(r"[-+]?\d*\.?\d+", c_low)
        
        if p_nums:
            # If prompt has numbers, candidate having numbers is a strong structural signal
            if c_nums:
                score += 0.5
                # Check order preservation (heuristic)
                try:
                    p_val = float(p_nums[0])
                    c_val = float(c_nums[0])
                    if (p_val > c_val and "less" in c_low) or (p_val < c_val and "more" in c_low):
                        score += 0.3
                except: pass
            else:
                score -= 0.2 # Missing numeric data when expected

        # 3. Conditional Presence
        if any(k in p_low.split() for k in self.conditionals):
            if any(k in c_low.split() for k in self.conditionals):
                score += 0.3
        
        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Calculates Normalized Compression Distance."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        denom = max(c1, c2)
        if denom == 0: return 0.0
        return (c12 - min(c1, c2)) / denom

    def _compute_order_parameter(self, scores: list[float]) -> float:
        """
        Calculates the 'variance' of the population scores.
        In CERL, high variance implies the system is at a critical point 
        between converging on a solution and exploring new ones.
        """
        if len(scores) < 2: return 0.0
        mean = sum(scores) / len(scores)
        variance = sum((s - mean) ** 2 for s in scores) / len(scores)
        return math.sqrt(variance) # Standard deviation as order parameter

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
        
        # Phase 1: Structural Evaluation (Exploitation Base)
        struct_scores = [self._structural_score(prompt, c) for c in candidates]
        
        # Phase 2: Criticality Detection
        # Calculate order parameter (variance of structural fitness)
        order_param = self._compute_order_parameter(struct_scores)
        
        # Threshold for "Criticality" (Phase Transition)
        # If variance is high, we are undecided; trigger exploration bonus
        is_critical = order_param > 0.15 
        
        results = []
        for i, candidate in enumerate(candidates):
            base_score = struct_scores[i]
            
            # NCD as tiebreaker/refinement (Distance to prompt)
            # Lower NCD means more similar/compressible together
            ncd_val = self._ncd(prompt, candidate)
            
            # CERL Adjustment:
            # If critical, boost candidates that are structurally okay but lexically diverse 
            # (simulating mutation). Here approximated by slightly rewarding length variance 
            # if base score is non-negative.
            mutation_bonus = 0.0
            if is_critical and base_score >= 0:
                # Simple diversity proxy: length difference from average
                avg_len = sum(len(c) for c in candidates) / len(candidates)
                diversity = abs(len(candidate) - avg_len) / (avg_len + 1)
                mutation_bonus = 0.1 * diversity
            
            # Final Score Composition
            # Structural logic is primary. NCD is secondary. Mutation bonus handles edge cases.
            final_score = (base_score * 0.6) + ((1.0 - ncd_val) * 0.3) + mutation_bonus
            
            results.append({
                "candidate": candidate,
                "score": final_score,
                "reasoning": f"Structural:{base_score:.2f} | Criticality:{is_critical} | NCD:{ncd_val:.2f}"
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        # Use the evaluation logic to score the single answer against the prompt
        # Treat the answer as a candidate in a population of itself + a dummy
        res = self.evaluate(prompt, [answer, "INVALID"])
        if not res:
            return 0.0
        
        # If the answer is the top result, map its score to 0-1
        # If it's not the top result (i.e., "INVALID" scored higher), confidence is low
        top_candidate = res[0]["candidate"]
        
        if top_candidate == answer:
            # Normalize score: structural scores are roughly -1 to 1.5
            # Map to 0-1 range roughly
            raw_score = res[0]["score"]
            conf = max(0.0, min(1.0, (raw_score + 0.5) / 2.0))
            return conf
        else:
            return 0.1 # Low confidence if a dummy variable beats it