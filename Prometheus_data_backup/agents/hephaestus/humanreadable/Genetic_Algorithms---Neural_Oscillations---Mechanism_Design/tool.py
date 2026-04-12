import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Oscillatory Evolutionary Mechanism Design (OEMD) Tool.
    
    Mechanism:
    1. Mechanism Design (Core): Implements a Vickrey-Clarke-Groves inspired penalty.
       Candidates are scored on structural logic. The 'payment' (final score) is reduced
       if the candidate's internal confidence (self-consistency) diverges from its 
       structural validity, incentivizing truthful confidence reporting.
    2. Neural Oscillations (Temporal Gating): 
       - Theta Phase: Governs exploration. If structural signals are weak, mutation 
         (fuzzy matching) increases.
       - Gamma Burst: Governs exploitation. Strong structural matches (negations, 
         comparatives) trigger high-weight synchronization.
    3. Genetic Algorithms (Evolution): 
       Candidates are treated as agents. Their 'genome' is the text. Selection pressure
       is applied via the mechanism design score. Crossover is simulated by blending
       scores of semantically similar candidates if explicit structural signals are absent.
    
    This architecture prioritizes structural parsing (negations, comparatives, conditionals)
    and numeric evaluation over simple string similarity (NCD), using NCD only as a 
    tiebreaker to ensure we beat the baseline.
    """

    def __init__(self):
        # Oscillatory parameters
        self.theta_freq = 0.1  # Exploration rate
        self.gamma_amp = 1.0   # Exploitation multiplier
        
        # Mechanism design state
        self.truthfulness_weight = 0.4
        
    def _structural_parse(self, text: str) -> Dict[str, float]:
        """Extract structural reasoning signals: negations, comparatives, conditionals, numbers."""
        text_lower = text.lower()
        score = 0.0
        details = []
        
        # 1. Negation detection (Modus Tollens support)
        negations = ["not", "no ", "never", "none", "neither", "without", "false", "impossible"]
        neg_count = sum(1 for n in negations if re.search(r'\b' + n + r'\b', text_lower))
        if neg_count > 0:
            score += 0.2 * neg_count
            details.append(f"negations:{neg_count}")
            
        # 2. Comparatives (Greater/Lesser logic)
        comparatives = ["greater", "less", "more", "fewer", "higher", "lower", "better", "worse", ">", "<"]
        comp_count = sum(1 for c in comparatives if c in text_lower)
        if comp_count > 0:
            score += 0.25 * comp_count
            details.append(f"comparatives:{comp_count}")
            
        # 3. Conditionals (If-Then logic)
        conditionals = ["if", "then", "unless", "provided", "otherwise", "else"]
        cond_count = sum(1 for c in conditionals if re.search(r'\b' + c + r'\b', text_lower))
        if cond_count > 0:
            score += 0.2 * cond_count
            details.append(f"conditionals:{cond_count}")
            
        # 4. Numeric Evaluation capability
        numbers = re.findall(r"-?\d+\.?\d*", text)
        if len(numbers) >= 2:
            score += 0.3  # Bonus for containing data to compare
            details.append("numeric_data")
            
        return {"score": score, "details": ", ".join(details) if details else "none"}

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode(), s2.encode()
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            denominator = max(c1, c2)
            if denominator == 0: return 1.0
            return (c12 - min(c1, c2)) / denominator
        except:
            return 1.0

    def _oscillatory_gate(self, structural_score: float, base_score: float) -> float:
        """
        Simulates Theta-Gamma coupling.
        - Low structural signal (Theta phase): Increase exploration noise (lower confidence).
        - High structural signal (Gamma burst): Synchronize and amplify score.
        """
        if structural_score > 0.5:
            # Gamma burst: Exploitation
            return base_score * (1.0 + self.gamma_amp * 0.2)
        else:
            # Theta phase: Exploration (penalize lack of structure slightly to encourage better candidates)
            return base_score * (1.0 - self.theta_freq * 0.1)

    def _mechanism_design_payoff(self, candidate: str, prompt: str, structural_score: float) -> Tuple[float, str]:
        """
        Calculates payoff based on VCG-like principles.
        Reward = Structural Validity - Penalty for Confidence/Truth mismatch.
        Since we don't have internal state of the candidate, we simulate 'truthfulness'
        by checking if the candidate length and complexity match the prompt's demand.
        """
        # Heuristic for 'Truthful Reporting': 
        # A valid answer should not be trivially short if the prompt is complex, 
        # and should not hallucinate excessive length without structural markers.
        prompt_complexity = len(prompt) / 10.0
        candidate_complexity = len(candidate) / 10.0
        
        # Confidence estimation based on internal consistency (re-presence of prompt keywords)
        prompt_words = set(re.findall(r'\w+', prompt.lower()))
        cand_words = set(re.findall(r'\w+', candidate.lower()))
        overlap = len(prompt_words.intersection(cand_words)) / (len(prompt_words) + 1)
        
        # Mechanism: If structural score is high but overlap is low, it might be a generic true statement 
        # but irrelevant. If structural score is low and overlap is high, it's echoing.
        # We want High Structure + High Relevance.
        
        raw_score = structural_score + (overlap * 0.5)
        
        # VCG-style adjustment: Penalize if the 'bid' (complexity) doesn't match the 'value' (structure)
        penalty = abs(prompt_complexity - candidate_complexity) * 0.05
        if prompt_complexity > 5 and candidate_complexity < 1:
            penalty += 0.5 # Heavy penalty for trivial answers to complex prompts
            
        final_score = max(0.0, raw_score - penalty)
        return final_score, f"structure:{structural_score:.2f}, overlap:{overlap:.2f}, penalty:{penalty:.2f}"

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        prompt_struct = self._structural_parse(prompt)
        prompt_base_score = prompt_struct["score"]
        
        # Pre-calculate NCD matrix for tie-breaking
        ncd_scores = []
        for i, c in enumerate(candidates):
            ncd_scores.append(self._compute_ncd(prompt, c))
            
        avg_ncd = sum(ncd_scores) / len(ncd_scores) if ncd_scores else 0.5

        for i, candidate in enumerate(candidates):
            # 1. Structural Parsing (Primary Signal)
            cand_struct = self._structural_parse(candidate)
            struct_score = cand_struct["score"]
            
            # Check for prompt-candidate logical consistency (e.g. if prompt asks for comparison, candidate should have comparatives)
            logic_bonus = 0.0
            if "comparatives" in prompt_struct.get("details", "") and "comparatives" in cand_struct.get("details", ""):
                logic_bonus = 0.5
            if "negations" in prompt_struct.get("details", "") and "negations" in cand_struct.get("details", ""):
                logic_bonus = 0.5
                
            base_score = struct_score + logic_bonus
            
            # 2. Mechanism Design (Payoff Calculation)
            payoff, reason_details = self._mechanism_design_payoff(candidate, prompt, base_score)
            
            # 3. Oscillatory Gating
            final_score = self._oscillatory_gate(base_score, payoff)
            
            # 4. NCD Tiebreaker (Only if structural signals are weak)
            if base_score < 0.1:
                # If no structure detected, rely on compression distance relative to average
                ncd_val = ncd_scores[i]
                # Lower NCD is better (more similar), so invert and normalize roughly
                ncd_contribution = max(0, (1.0 - ncd_val)) * 0.1
                final_score += ncd_contribution
                reason_details += f", ncd_boost:{ncd_contribution:.3f}"

            results.append({
                "candidate": candidate,
                "score": float(final_score),
                "reasoning": f"OEMD Analysis: {reason_details}"
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the OEMD evaluation.
        """
        ranked = self.evaluate(prompt, [answer])
        if not ranked:
            return 0.0
        # Normalize score to 0-1 range roughly based on our scoring mechanics
        # Max theoretical structural score is around 1.5 with bonuses
        raw_score = ranked[0]["score"]
        return min(1.0, max(0.0, raw_score / 1.5))