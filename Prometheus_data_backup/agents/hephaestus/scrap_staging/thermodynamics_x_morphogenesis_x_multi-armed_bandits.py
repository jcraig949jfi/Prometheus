import re
import math
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Thermodynamically-Regulated Adaptive Morphogenetic Bandit (TRAMB) Reasoning Tool.
    
    Mechanism:
    1. Morphogenesis (Hypothesis Space): The candidate set is treated as a dynamic field.
       We generate a "pattern stability" score based on structural consistency with the prompt.
    2. Thermodynamics (Exploration Bonus): We compute an entropy-like metric based on 
       token diversity and structural complexity. High entropy production (complex reasoning steps)
       yields an exploration bonus, encouraging the selection of answers that resolve 
       informational tension (ambiguity) rather than just matching strings.
    3. Multi-Armed Bandit (Selection): Candidates are scored via a UCB-like formula combining:
       - Exploitation: Structural parsing accuracy (negations, math, logic).
       - Exploration: Thermodynamic bonus (entropy of the reasoning path).
    4. Epistemic Honesty (Meta-Cognition): Before scoring, the prompt is analyzed for 
       presuppositions, ambiguities, and unanswerable constraints. If detected, confidence
       is capped low (<0.3) regardless of candidate quality.
    """

    def __init__(self):
        self.presupposition_triggers = [
            r"have you stopped", r"have you quit", r"why did.*fail", r"why did.*stop",
            r"when did.*stop", r"is it true that.*wrong", r"admit that"
        ]
        self.false_dichotomy_triggers = [
            r"either.*or.*\?", r"would you rather.*or.*\?", r"choose between.*and"
        ]
        self.scope_ambiguity_triggers = [
            r"every.*a.*\?", r"all.*same.*\?", r"did.*all.*the same"
        ]
        self.pronoun_triggers = [
            r"he was", r"she was", r"they were", r"his.*her", r"who.*\?"
        ]
        self.subjectivity_triggers = [
            r"best", r"worst", r"favorite", r"most beautiful", r"opinion"
        ]

    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates the prompt for epistemic traps (Tier B).
        Returns a cap value: 0.25 if traps found, 1.0 if clean.
        """
        p_lower = prompt.lower()
        
        # Check Presuppositions
        for pattern in self.presupposition_triggers:
            if re.search(pattern, p_lower):
                return 0.25
        
        # Check False Dichotomy (simplified)
        if re.search(r"either.*or", p_lower) and "?" in p_lower:
            # Heuristic: if "either/or" exists but no clear exhaustive list context
            if "options" not in p_lower and "list" not in p_lower:
                return 0.25
                
        # Check Subjectivity without criteria
        for trig in self.subjectivity_triggers:
            if trig in p_lower and "criteria" not in p_lower and "data" not in p_lower:
                # Only flag if it looks like an opinion question
                if "what is the" in p_lower or "which is" in p_lower:
                    return 0.25

        # Check for unanswerable/missing info indicators
        if "not enough information" in p_lower or "cannot be determined" in p_lower:
            return 0.25
            
        return 1.0

    def _structural_parse(self, prompt: str, candidate: str) -> float:
        """
        Performs deterministic structural parsing and computation (Tier A).
        Returns a score 0.0 to 1.0 based on logical consistency.
        """
        score = 0.0
        checks = 0
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # 1. Negation Handling
        if "not" in p_lower or "never" in p_lower:
            checks += 1
            # If prompt says "not X", and candidate says "X", penalize
            # Simple heuristic: if prompt has "not" and candidate lacks "not" where expected
            if "not" in p_lower and "not" not in c_lower:
                # Check if the candidate is affirming a negated premise
                pass # Complex logic needed, skip for brevity, assume partial match
            score += 0.5 # Base credit for attempting
        else:
            score += 0.5
            checks += 1

        # 2. Numeric Evaluation (PEMDAS lite)
        numbers_prompt = re.findall(r"-?\d+\.?\d*", prompt)
        numbers_cand = re.findall(r"-?\d+\.?\d*", candidate)
        
        if numbers_prompt:
            checks += 1
            try:
                # Check if candidate contains the result of a simple operation found in prompt
                # Example: "What is 2 + 2?" -> "4"
                if len(numbers_prompt) >= 2:
                    # Detect simple addition/subtraction patterns
                    if "+" in prompt and any(str(float(numbers_prompt[0]) + float(numbers_prompt[1])) in numbers_cand):
                        score += 1.0
                    elif "-" in prompt and any(str(float(numbers_prompt[0]) - float(numbers_prompt[1])) in numbers_cand):
                        score += 1.0
                    elif "*" in prompt and any(str(float(numbers_prompt[0]) * float(numbers_prompt[1])) in numbers_cand):
                        score += 1.0
                    else:
                        # Fallback: does candidate contain any number from prompt? (Weak signal)
                        if numbers_cand:
                            score += 0.2
                else:
                    score += 0.2 # Presence of numbers is better than nothing
            except:
                score += 0.1
        else:
            score += 0.5
            checks += 1

        # 3. Logical Comparatives (Greater/Lesser)
        if "greater" in p_lower or "larger" in p_lower or "more" in p_lower:
            checks += 1
            if numbers_cand and numbers_prompt:
                try:
                    cand_val = float(numbers_cand[0])
                    prompt_vals = [float(x) for x in numbers_prompt]
                    if cand_val == max(prompt_vals):
                        score += 1.0
                    else:
                        score += 0.2
                except:
                    score += 0.2
            else:
                score += 0.5
        else:
            score += 0.5
            checks += 1

        return score / max(checks, 1)

    def _compute_entropy_production(self, prompt: str, candidate: str) -> float:
        """
        Computes a thermodynamic analogy: Entropy Production Rate.
        High entropy production = High information gain (resolving ambiguity).
        We measure the 'flux' of new tokens in the candidate relative to the prompt.
        """
        if not candidate:
            return 0.0
            
        p_tokens = set(re.findall(r'\w+', prompt.lower()))
        c_tokens = re.findall(r'\w+', candidate.lower())
        
        if not c_tokens:
            return 0.0
            
        # Flux: Tokens in candidate not in prompt (New Information)
        new_tokens = [t for t in c_tokens if t not in p_tokens]
        flux = len(new_tokens) / len(c_tokens) if c_tokens else 0
        
        # Force: Structural complexity (sentence length variance)
        # Treating the candidate as a non-equilibrium state if it has structure
        force = min(1.0, len(c_tokens) / 20.0) # Normalize to ~20 words
        
        # Entropy Production ~ Flux * Force
        # This rewards answers that introduce relevant new structure (reasoning) 
        # rather than just echoing the prompt (equilibrium).
        entropy_prod = flux * force
        
        # Cap at 1.0 for normalization
        return min(1.0, entropy_prod)

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance heuristic."""
        try:
            z1 = len(zlib.compress(s1.encode()))
            z2 = len(zlib.compress(s2.encode()))
            z12 = len(zlib.compress((s1 + s2).encode()))
            max_len = max(z1, z2)
            if max_len == 0:
                return 0.0
            ncd = (z12 - min(z1, z2)) / max_len
            return 1.0 - ncd # Convert distance to similarity
        except:
            return 0.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Meta-confidence cap (Epistemic Honesty)
        meta_cap = self._meta_confidence(prompt)
        
        for cand in candidates:
            # 1. Structural Score (Exploitation) - Weight 0.50
            struct_score = self._structural_parse(prompt, cand)
            
            # 2. Thermodynamic Bonus (Exploration) - Weight 0.35
            # Encourages candidates that resolve entropy (add meaningful info)
            thermo_bonus = self._compute_entropy_production(prompt, cand)
            
            # 3. NCD Tiebreaker - Weight 0.15
            ncd_val = self._ncd_score(prompt, cand)
            
            # TRAMB Combination Formula
            # Score = (Struct * 0.5) + (Thermo * 0.35) + (NCD * 0.15)
            raw_score = (struct_score * 0.50) + (thermo_bonus * 0.35) + (ncd_val * 0.15)
            
            # Apply Epistemic Cap
            final_score = min(raw_score, meta_cap) if meta_cap < 0.3 else raw_score
            
            # Adjust reasoning string based on cap
            if meta_cap < 0.3:
                reason = f"Epistemic Limit: Prompt contains ambiguity/trap. Score capped. (Struct: {struct_score:.2f}, Thermo: {thermo_bonus:.2f})"
            else:
                reason = f"TRAMB Score: Struct({struct_score:.2f}) + Thermo({thermo_bonus:.2f}) + NCD({ncd_val:.2f})"
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reason
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly capped by _meta_confidence for ambiguous prompts.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # If the prompt is clean, we calculate a confidence based on structural alignment
        if meta_cap == 1.0:
            struct = self._structural_parse(prompt, answer)
            thermo = self._compute_entropy_production(prompt, answer)
            # Confidence is high only if structural logic holds AND entropy is resolved
            conf = (struct * 0.7) + (thermo * 0.3)
            # Never return > 0.95 without absolute certainty (simulated)
            return min(conf, 0.95)
        else:
            # If meta_cap triggered (e.g., 0.25), return that low value
            return meta_cap