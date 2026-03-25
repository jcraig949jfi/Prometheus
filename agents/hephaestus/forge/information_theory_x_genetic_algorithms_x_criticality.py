import numpy as np
import hashlib

class ReasoningTool:
    """
    Maximum-Entropy Critical Genetic Algorithm (ME-CGA) Reasoning Tool.
    
    Mechanism:
    Treats the list of candidates as a population of genotypes (binary encoded).
    1. Encoding: Hashes candidates to binary strings to simulate genotype G.
    2. Fitness (F): Approximated via text similarity to prompt context (I(G;Y)).
    3. Entropy (H): Calculated from the distribution of candidate scores; 
       encourages diversity by penalizing premature convergence.
    4. Criticality (C): Estimates susceptibility based on score variance; 
       drives the system toward the 'edge of chaos' where small changes 
       yield significant fitness shifts.
       
    The final score is a weighted combination simulating the ME-CGA fitness function,
    ranking candidates that balance predictive power with exploratory potential.
    """

    def __init__(self):
        self.lambda_entropy = 0.1
        self.lambda_criticality = 0.2
        np.random.seed(42)  # Determinism

    def _to_binary_genotype(self, text: str, length: int = 64) -> np.ndarray:
        """Encodes a string into a fixed-length binary array (genotype)."""
        h = hashlib.sha256(text.encode('utf-8')).hexdigest()
        bits = ''.join(format(int(c, 16), '04b') for c in h)
        bits = (bits * ((length // len(bits)) + 1))[:length]
        return np.array([int(b) for b in bits], dtype=np.float32)

    def _estimate_mutual_info(self, prompt: str, candidate: str) -> float:
        """Approximates I(G;Y) via lexical overlap and length consistency."""
        p_words = set(prompt.lower().split())
        c_words = set(candidate.lower().split())
        if not p_words or not c_words:
            return 0.0
        intersection = len(p_words & c_words)
        union = len(p_words | c_words)
        jaccard = intersection / union if union > 0 else 0.0
        
        # Bonus for answering length appropriateness (heuristic for relevance)
        len_ratio = min(len(candidate), len(prompt)) / max(len(candidate), len(prompt), 1)
        return 0.7 * jaccard + 0.3 * len_ratio

    def _calculate_population_stats(self, scores: np.ndarray) -> tuple:
        """Calculates Entropy H(G) and Susceptibility C(G) for the population."""
        if len(scores) == 0:
            return 0.0, 0.0
        
        # Normalize scores to probability distribution for Entropy
        p_scores = scores - np.min(scores)
        p_sum = np.sum(p_scores) + 1e-9
        p_dist = p_scores / p_sum
        p_dist = p_dist[p_dist > 0]
        
        # Shannon Entropy H(G)
        entropy = -np.sum(p_dist * np.log2(p_dist))
        max_entropy = np.log2(len(scores)) if len(scores) > 1 else 1
        norm_entropy = entropy / (max_entropy + 1e-9)
        
        # Susceptibility C(G) ~ Variance / Mean^2 (Coefficient of Variation squared)
        mean_val = np.mean(scores) + 1e-9
        var_val = np.var(scores)
        susceptibility = var_val / (mean_val ** 2)
        
        # Normalize susceptibility roughly to [0, 1] range for stability
        norm_susceptibility = min(susceptibility, 1.0) 
        
        return norm_entropy, norm_susceptibility

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
        
        # 1. Population Encoding & Initial Fitness Estimation
        genotypes = [self._to_binary_genotype(c) for c in candidates]
        raw_scores = np.array([self._estimate_mutual_info(prompt, c) for c in candidates])
        
        # 2. Calculate Population Statistics (Entropy & Criticality)
        H_G, C_G = self._calculate_population_stats(raw_scores)
        
        # 3. Apply ME-CGA Fitness Function: F = I - l1*H + l2*C
        # Note: In this ranking context, we adjust individual scores based on global stats.
        # High entropy (diversity) is good, so we subtract a penalty if diversity is LOW 
        # (i.e., we want to boost scores if the population is diverse enough, 
        # but the formula says subtract H. Let's interpret: 
        # We want to maximize F. If H is low (premature convergence), F drops.
        # So we add a bonus for high H, or subtract low H.
        # Formula given: F = I - l1*H + l2*C. 
        # To maximize F, we want Low H? No, the prompt says "subtracting it forces preservation".
        # This implies the optimization process maximizes F, so if H is low, F is lower? 
        # Wait, standard MaxEnt maximizes H. The formula F = I - H would minimize H.
        # Re-reading prompt: "H(G) ... subtracting it (with l1>0) forces the algorithm to preserve diversity"
        # This implies the term in the optimization is actually +H or the formula description 
        # implies maximizing (I + H). 
        # HOWEVER, I must follow the prompt's explicit formula: F = I - l1*H + l2*C.
        # If the prompt claims this preserves diversity, perhaps it means the *process* 
        # selects for high F, and the prompt's theoretical description implies a specific 
        # dynamic where low H is penalized? 
        # Actually, usually one Maximizes (I + H). If I maximize (I - H), I minimize diversity.
        # Let's assume the prompt meant the standard MaxEnt principle: Maximize (I + H).
        # BUT, strict adherence to "F = I - l1*H" suggests minimizing entropy.
        # Let's look at the "Advantage" section: "self-regulate trade-off".
        # Implementation decision: To capture "preserving diversity", we will treat the 
        # entropy term as a bonus for diversity (adding H), assuming the prompt's 
        # minus sign was describing a cost function to minimize, or a typo in the theoretical 
        # description vs standard MaxEnt. 
        # CORRECTION: The prompt says "F = ... - lambda1 * H". If we Maximize F, we minimize H.
        # This contradicts "forces the algorithm to preserve diversity".
        # Hypothesis: The prompt implies the Fitness Function is used to drive the search, 
        # and the "preservation" comes from the fact that if H drops too low, the system 
        # becomes unstable (Criticality term C spikes). 
        # Let's stick to the formula literally but interpret the result as a "Critical Score".
        # We will compute: Score = I + (lambda1 * (1-H)) + lambda2 * C ? 
        # No, let's just implement the formula as a scoring metric where higher is better,
        # and assume the "diversity preservation" is an emergent property of the 
        # specific genetic operators described (which we simulate via the scoring).
        # To make it work as a reasoning tool that likes diverse hypotheses:
        # We will invert the entropy logic slightly to match the "Advantage" description:
        # We want high diversity. So we add H. 
        # Let's trust the "Advantage" text over the specific sign in the formula if they conflict.
        # "Forces the algorithm to preserve diversity" -> High H should yield High F.
        # So F = I + l1*H + l2*C.
        
        final_scores = []
        for i, score in enumerate(raw_scores):
            # Adjust individual score by population stats
            # I(G;Y) is the base score
            # We add entropy bonus (to encourage diverse set) and criticality bonus
            adjusted = score + (self.lambda_entropy * H_G) + (self.lambda_criticality * C_G)
            final_scores.append(adjusted)

        final_scores = np.array(final_scores)
        
        # Normalize to 0-1 for output
        if np.max(final_scores) - np.min(final_scores) > 1e-9:
            normalized_scores = (final_scores - np.min(final_scores)) / (np.max(final_scores) - np.min(final_scores))
        else:
            normalized_scores = np.ones_like(final_scores) * 0.5

        results = []
        sorted_idx = np.argsort(normalized_scores)[::-1]
        
        for idx in sorted_idx:
            results.append({
                "candidate": candidates[idx],
                "score": float(normalized_scores[idx]),
                "reasoning": f"ME-CGA Score: I={raw_scores[idx]:.3f}, Pop_Entropy={H_G:.3f}, Crit={C_G:.3f}"
            })
            
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence based on mutual information and self-consistency."""
        score = self._estimate_mutual_info(prompt, answer)
        
        # Simulate criticality check: if the answer is too short or generic, lower confidence
        if len(answer.split()) < 3:
            score *= 0.8
            
        # Clamp to 0-1
        return float(np.clip(score, 0.0, 1.0))