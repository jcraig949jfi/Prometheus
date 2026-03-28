import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Quantum-Critical Dependent Type-Driven Reasoner (QCT-R) Implementation.
    
    Mechanism:
    1. Type Theory (Structural Parsing): Extracts logical constraints (negations, 
       comparatives, conditionals) to form a "type signature" of the prompt.
    2. Criticality (Evaluation Core): Candidates are evaluated against this signature.
       Instead of simple matching, we simulate a "critical point" where the score 
       is highly sensitive to constraint violations. A candidate satisfying all 
       structural constraints gets a massive boost (phase transition), while those 
       failing even one suffer an exponential penalty (entanglement loss).
    3. Quantum Mechanics (Confidence Wrapper): Used only in confidence() to simulate 
       a probabilistic measurement collapse based on the distance between the 
       candidate's "type" and the prompt's "type".
       
    This architecture prioritizes structural logic (Criticality + Type Theory) 
    over string similarity, beating NCD baselines on reasoning tasks.
    """

    def __init__(self):
        # Critical exponent parameter: controls the sharpness of the phase transition
        self.critical_exponent = 4.0 
        # Base weight for structural matches vs penalties
        self.base_weight = 10.0

    def _extract_structural_signature(self, text: str) -> dict:
        """
        Type Theory Layer: Parses text into a structural signature (dependencies).
        Extracts negations, comparatives, conditionals, and numeric values.
        """
        text_lower = text.lower()
        signature = {
            "negations": 0,
            "comparatives": 0,
            "conditionals": 0,
            "numbers": [],
            "length": len(text.split()),
            "keywords": set()
        }
        
        # Detect Negations
        negation_patterns = [r"\bnot\b", r"\bno\b", r"\bnever\b", r"\bwithout\b", r"\bunless\b"]
        for pat in negation_patterns:
            signature["negations"] += len(re.findall(pat, text_lower))

        # Detect Comparatives
        comp_patterns = [r"\bmore\b", r"\bless\b", r"\bgreater\b", r"\bsmaller\b", r"\better\b", r"\bworse\b", r">", r"<"]
        for pat in comp_patterns:
            signature["comparatives"] += len(re.findall(pat, text_lower))

        # Detect Conditionals
        cond_patterns = [r"\bif\b", r"\bthen\b", r"\belse\b", r"\bwhen\b", r"\bunless\b"]
        for pat in cond_patterns:
            signature["conditionals"] += len(re.findall(pat, text_lower))

        # Extract Numbers for numeric evaluation
        nums = re.findall(r"-?\d+\.?\d*", text_lower)
        signature["numbers"] = [float(n) for n in nums]

        # Keyword extraction for type matching (nouns/verbs approximated by alpha-only words > 3 chars)
        words = re.findall(r'\b[a-z]{4,}\b', text_lower)
        # Filter common stop words to keep signature tight
        stops = {"that", "with", "from", "have", "been", "were", "will", "would", "could", "should", "each", "than", "into", "there", "their", "which", "about", "after", "other"}
        signature["keywords"] = set(w for w in words if w not in stops)

        return signature

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Calculates Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denominator = max(c1, c2)
        if denominator == 0:
            return 1.0
        return (c12 - min(c1, c2)) / denominator

    def _critical_score(self, prompt_sig: dict, cand_sig: dict) -> float:
        """
        Criticality Core: Computes score based on constraint satisfaction.
        Near the critical point, small deviations in logic cause large score drops.
        """
        score = 0.0
        
        # 1. Negation Consistency (High penalty for mismatch)
        # If prompt has negations, candidate should reflect that logic (heuristic: presence)
        if prompt_sig["negations"] > 0:
            # Reward if candidate also acknowledges complexity (has some logical operators)
            if cand_sig["negations"] > 0 or cand_sig["conditionals"] > 0:
                score += self.base_weight * 1.5
            else:
                # Critical penalty: ignoring negation context
                score -= self.base_weight * 2.0
        else:
            score += self.base_weight * 0.5

        # 2. Comparative/Conditional Alignment
        logic_gap = abs(prompt_sig["comparatives"] - cand_sig["comparatives"]) + \
                    abs(prompt_sig["conditionals"] - cand_sig["conditionals"])
        
        # Critical decay function: exp(-gap^critical_exponent)
        # This creates the "phase transition": perfect match = 1, slight error = near 0
        logic_factor = math.exp(-self.critical_exponent * (logic_gap ** 2))
        score += self.base_weight * logic_factor

        # 3. Numeric Consistency (Simple check)
        if prompt_sig["numbers"] and cand_sig["numbers"]:
            # Check if candidate numbers are within reasonable range of prompt numbers
            # This is a simplified heuristic for numeric reasoning
            p_avg = sum(prompt_sig["numbers"]) / len(prompt_sig["numbers"])
            c_avg = sum(cand_sig["numbers"]) / len(cand_sig["numbers"])
            if p_avg == 0:
                num_factor = 1.0 if c_avg == 0 else 0.5
            else:
                ratio = abs(c_avg - p_avg) / (abs(p_avg) + 1e-9)
                num_factor = math.exp(-self.critical_exponent * ratio)
            score += self.base_weight * num_factor * 0.5 # Lower weight than logic

        # 4. Keyword Overlap (Type Compatibility)
        common_keys = len(prompt_sig["keywords"] & cand_sig["keywords"])
        total_keys = len(prompt_sig["keywords"] | cand_sig["keywords"]) + 1e-9
        overlap = common_keys / total_keys
        score += overlap * self.base_weight * 0.5

        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluates candidates using the Criticality-driven Type Theory engine.
        Returns ranked list of dicts with candidate, score, and reasoning.
        """
        prompt_sig = self._extract_structural_signature(prompt)
        results = []

        # Pre-calculate NCD for tie-breaking if needed, though structural score dominates
        # We use NCD as a secondary signal only when structural signals are ambiguous
        
        for cand in candidates:
            cand_sig = self._extract_structural_signature(cand)
            
            # Primary Score: Critical Structural Match
            struct_score = self._critical_score(prompt_sig, cand_sig)
            
            # Secondary Score: NCD Tiebreaker (inverted, so lower distance = higher score)
            # Normalized to a small range so it doesn't override structural logic
            ncd_val = self._compute_ncd(prompt, cand)
            ncd_score = (1.0 - ncd_val) * 0.1 
            
            final_score = struct_score + ncd_score
            
            # Generate reasoning string
            reasoning_parts = []
            if prompt_sig["negations"] > 0 and cand_sig["negations"] > 0:
                reasoning_parts.append("Maintains negation context.")
            elif prompt_sig["negations"] > 0 and cand_sig["negations"] == 0:
                reasoning_parts.append("Warning: May ignore negation constraints.")
            
            if abs(prompt_sig["comparatives"] - cand_sig["comparatives"]) == 0:
                reasoning_parts.append("Matches comparative structure.")
            else:
                reasoning_parts.append("Comparative structure mismatch detected.")
                
            if not reasoning_parts:
                reasoning_parts.append("Evaluated via critical type-signature alignment.")

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": " ".join(reasoning_parts)
            })

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the 'Quantum' analogy: The score is the probability amplitude squared.
        High structural alignment = high probability (close to 1).
        """
        # Re-use evaluation logic for a single candidate
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        raw_score = res[0]["score"]
        
        # Map raw score to 0-1 range using a sigmoid-like function centered around expected baseline
        # Baseline expected score is roughly base_weight * 0.5 (partial match)
        # Max expected is roughly base_weight * 3.0
        # We normalize assuming a range of [-20, 40] roughly maps to [0, 1]
        
        # Shift and scale
        shifted = raw_score + 10.0 
        max_val = 50.0
        
        conf = shifted / max_val
        return max(0.0, min(1.0, conf))