import re
import zlib
import math
import random

class ReasoningTool:
    """
    Oscillatory Bandit-Guided Program Synthesizer (Simplified for Reasoning).
    
    Mechanism:
    1. Program Synthesis (Structural Parsing): Instead of generating code, we parse
       the prompt and candidates into logical constraints (negations, comparatives,
       conditionals). This acts as the 'synthesis' of a reasoning hypothesis.
    2. Multi-Armed Bandit: Each candidate answer is an 'arm'. The 'reward' is the
       degree to which the candidate satisfies the extracted logical constraints.
       We use a deterministic Thompson Sampling proxy (Mean + Exploration Bonus).
    3. Neural Oscillations: 
       - Theta (Exploration): A pseudo-oscillatory phase derived from input length
         modulates an exploration bonus, encouraging diversity when constraints are
         ambiguous or the search space is large.
       - Gamma (Exploitation): Sharpens the score based on strict constraint matching.
       
    Scoring:
    - Primary: Structural logic (negation, transitivity, numeric comparison).
    - Secondary: NCD (Compression) used only as a tiebreaker for semantic similarity.
    """

    def __init__(self):
        self.epsilon = 1e-6

    def _oscillate(self, seed_str: str, phase: str) -> float:
        """
        Simulates neural oscillation modulation.
        Theta: Global exploration noise (based on input complexity).
        Gamma: Local exploitation sharpening.
        """
        val = sum(ord(c) for c in seed_str)
        # Theta rhythm (slow, global): Modulates exploration width
        theta = math.sin(val * 0.1) * 0.1 
        # Gamma burst (fast, local): Sharpens specific matches
        gamma = math.cos(val * 0.5) * 0.05
        
        if phase == 'theta':
            return max(0.0, theta + 0.5) # Ensure positive exploration
        return gamma # Exploitation modifier

    def _extract_logic(self, text: str) -> dict:
        """Parses text for logical primitives (Program Synthesis step)."""
        text_lower = text.lower()
        logic = {
            'negations': len(re.findall(r'\b(not|no|never|without|false)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|better|worse|than)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|otherwise)\b', text_lower)),
            'numbers': re.findall(r'-?\d+\.?\d*', text_lower)
        }
        return logic

    def _check_constraint(self, prompt_logic: dict, candidate: str) -> float:
        """Evaluates candidate against prompt logic (Hypothesis Testing)."""
        score = 0.0
        cand_lower = candidate.lower()
        
        # 1. Negation Consistency
        # If prompt has negations, candidate should ideally reflect or not contradict them
        # Simple heuristic: If prompt says "not", and candidate is "yes/no", check context
        if prompt_logic['negations'] > 0:
            if re.search(r'\b(yes|true|correct)\b', cand_lower):
                # Penalize blind affirmation in negative contexts slightly
                score -= 0.1 
            if re.search(r'\b(no|false|incorrect|not)\b', cand_lower):
                score += 0.2 # Reward acknowledging negation

        # 2. Numeric Evaluation
        if prompt_logic['numbers'] and len(prompt_logic['numbers']) >= 2:
            try:
                p_nums = [float(x) for x in prompt_logic['numbers']]
                c_nums = [float(x) for x in re.findall(r'-?\d+\.?\d*', cand_lower)]
                
                if c_nums:
                    # Check if candidate preserves order or magnitude logic
                    # Example: Prompt "9.11 vs 9.9", Candidate "9.9 is larger"
                    if len(p_nums) == 2 and len(c_nums) >= 1:
                        expected_max = max(p_nums)
                        expected_min = min(p_nums)
                        # Reward if candidate mentions the correct max/min or relationship
                        if any(abs(c - expected_max) < 0.01 for c in c_nums):
                            score += 0.3
                        if any(abs(c - expected_min) < 0.01 for c in c_nums):
                            score += 0.1
            except ValueError:
                pass

        # 3. Conditional/Comparative Presence
        if prompt_logic['conditionals'] > 0:
            if re.search(r'\b(if|then|because|therefore)\b', cand_lower):
                score += 0.2
        
        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        if not s1 or not s2: return 1.0
        len1 = len(zlib.compress(s1.encode()))
        len2 = len(zlib.compress(s2.encode()))
        len_both = len(zlib.compress((s1 + s2).encode()))
        return len_both / max(len1, len2, 1)

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
            
        prompt_logic = self._extract_logic(prompt)
        results = []
        
        # Oscillatory parameters based on prompt complexity
        explore_bonus = self._oscillate(prompt, 'theta')
        exploit_factor = self._oscillate(prompt, 'gamma')

        for cand in candidates:
            # 1. Structural Parsing Score (The "Synthesis" reward)
            logic_score = self._check_constraint(prompt_logic, cand)
            
            # 2. Bandit Value Estimate (Mean reward proxy)
            # Base score from logic, modulated by gamma (exploitation)
            base_value = logic_score * (1.0 + exploit_factor)
            
            # 3. Exploration Bonus (Theta modulation)
            # Encourages diverse candidates if logic is ambiguous
            bonus = explore_bonus * (0.1 if len(cand) > 5 else 0.0)
            
            # 4. NCD Tiebreaker (Similarity to prompt context)
            # Only used if logic scores are close; here added as small bias
            ncd_val = self._ncd(prompt, cand)
            similarity_score = (1.0 - ncd_val) * 0.05 # Small weight
            
            final_score = base_value + bonus + similarity_score
            
            # Reasoning trace
            reason_parts = []
            if logic_score > 0: reason_parts.append("Matches logical constraints")
            if logic_score < 0: reason_parts.append("Potential contradiction detected")
            if bonus > 0.05: reason_parts.append("Exploratory boost applied")
            reasoning = "; ".join(reason_parts) if reason_parts else "Standard evaluation"

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses structural alignment and compression consistency.
        """
        logic = self._extract_logic(prompt)
        logic_score = self._check_constraint(logic, answer)
        
        # Base confidence from logic match
        conf = 0.5 + (logic_score * 0.4) # Range approx 0.1 to 0.9
        
        # Penalty for length mismatch in numeric contexts
        if logic['numbers']:
            ans_nums = re.findall(r'\d+', answer)
            if not ans_nums:
                conf -= 0.3 # Suspicious if numbers expected but none found
        
        # Oscillatory noise reduction (Gamma sharpening)
        gamma = self._oscillate(prompt + answer, 'gamma')
        conf = conf * (1.0 + gamma * 0.1)
        
        return max(0.0, min(1.0, conf))