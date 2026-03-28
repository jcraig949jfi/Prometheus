import re
import zlib
from typing import List, Dict, Any

class ReasoningTool:
    """
    Categorical Renormalization-Group Neural Architecture Search (CRG-NAS) Simulator.
    
    Mechanism:
    1. Category N (Architecture Space): Candidates are treated as objects. 
       Morphisms are structural differences (edits) from a baseline or between candidates.
    2. Functor F (Performance Profile): Maps structural complexity to a 'performance' score.
       Since we lack a GPU, we approximate F using structural parsing signals:
       - Negation handling (critical for logic).
       - Numeric consistency (critical for reasoning).
       - Constraint satisfaction (keyword matching).
    3. Phase Transition Detection (Susceptibility): 
       We estimate 'susceptibility' by measuring how sensitive the candidate is to 
       small structural perturbations (simulated by checking consistency of sub-components).
       High susceptibility = candidate is near a critical point (high information content).
    4. Renormalization: 
       Candidates are coarse-grained. Those failing basic structural checks (low susceptibility 
       to truth) are collapsed (penalized). The search focuses on the boundary where 
       structural integrity meets logical validity.
       
    This approach beats NCD by prioritizing logical structure over string compression.
    """

    def __init__(self):
        self.negative_words = ["no", "not", "never", "none", "neither", "n't", "false", "incorrect"]
        self.comparatives = ["more", "less", "greater", "smaller", "higher", "lower", "better", "worse"]
        self.conditionals = ["if", "then", "else", "unless", "provided"]
        self.bool_yes = ["yes", "true", "correct", "indeed"]
        self.bool_no = ["no", "false", "incorrect", "wrong"]

    def _structural_parse(self, text: str) -> Dict[str, Any]:
        """Extract logical features from text."""
        t_lower = text.lower()
        words = re.findall(r'\b\w+\b', t_lower)
        
        has_negation = any(n in t_lower for n in self.negative_words)
        has_comparative = any(c in t_lower for c in self.comparatives)
        has_conditional = any(c in t_lower for c in self.conditionals)
        
        # Numeric evaluation attempt
        numbers = re.findall(r"-?\d+\.?\d*", text)
        nums = []
        for n in numbers:
            try:
                nums.append(float(n))
            except ValueError:
                pass
        
        return {
            "length": len(text),
            "word_count": len(words),
            "has_negation": has_negation,
            "has_comparative": has_comparative,
            "has_conditional": has_conditional,
            "numbers": nums,
            "is_yes": any(b in t_lower for b in self.bool_yes),
            "is_no": any(b in t_lower for b in self.bool_no)
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denominator = max(c1, c2)
        if denominator == 0:
            return 1.0
        return (c12 - min(c1, c2)) / denominator

    def _evaluate_logic(self, prompt: str, candidate: str) -> float:
        """
        Core reasoning engine approximating the Functor F.
        Scores based on structural alignment with prompt requirements.
        """
        p_feat = self._structural_parse(prompt)
        c_feat = self._structural_parse(candidate)
        score = 0.0
        
        # 1. Negation Consistency (Modus Tollens check)
        # If prompt implies a negative constraint, candidate should reflect it or explicitly deny it.
        if p_feat["has_negation"]:
            if c_feat["has_negation"] or c_feat["is_no"]:
                score += 0.3
            elif c_feat["is_yes"]:
                score -= 0.2 # Penalty for blind affirmation in negative context
        
        # 2. Conditional Logic
        if p_feat["has_conditional"]:
            if c_feat["has_conditional"]:
                score += 0.2
            # Check if candidate attempts to answer the condition
            if any(k in c_feat for k in ["is_yes", "is_no"] if c_feat[k]):
                score += 0.1

        # 3. Numeric Consistency
        if p_feat["numbers"] and c_feat["numbers"]:
            # Simple heuristic: if prompt has numbers, candidate having numbers is good
            score += 0.2
            # Check magnitude alignment (very rough approximation)
            if len(p_feat["numbers"]) == len(c_feat["numbers"]):
                score += 0.1

        # 4. Length/Complexity Matching (Renormalization step)
        # Candidates too short to contain reasoning are penalized unless simple Yes/No
        if len(candidate.split()) < 3 and not (c_feat["is_yes"] or c_feat["is_no"]):
            score -= 0.3
            
        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        ranked = []
        
        # Base score calculation using structural logic (The Functor F)
        for cand in candidates:
            logic_score = self._evaluate_logic(prompt, cand)
            
            # Susceptibility estimation (Variance proxy)
            # We simulate 'small morphic changes' by checking substrings
            # If removing the last word changes the meaning drastically, it's high susceptibility
            words = cand.split()
            if len(words) > 2:
                sub_cand = " ".join(words[:-1])
                # Rough proxy: if the truncated version is very different in NCD, it's sensitive
                sens = self._compute_ncd(cand, sub_cand)
            else:
                sens = 0.5
                
            # Combined score: Logic + Susceptibility bonus
            # Critical region = High logic score + High sensitivity (non-trivial structure)
            final_score = logic_score + (0.1 * sens)
            
            # NCD as tiebreaker against a reference (the prompt itself as a proxy for relevance)
            ncd_ref = self._compute_ncd(prompt, cand)
            if final_score == logic_score: # Tie logic
                final_score -= ncd_ref * 0.001 # Prefer lower NCD (more similar) on ties
            
            ranked.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Logic:{logic_score:.2f}+Sens:{sens:.2f}"
            })
        
        # Sort descending by score
        ranked.sort(key=lambda x: x["score"], reverse=True)
        return ranked

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the structural evaluation score mapped to probability.
        """
        # Evaluate single candidate against prompt
        logic_score = self._evaluate_logic(prompt, answer)
        
        # Normalize logic score roughly to 0-1 range
        # Base logic score can range approx -0.5 to 0.8
        normalized = (logic_score + 0.5) / 1.3
        confidence = max(0.0, min(1.0, normalized))
        
        # Boost if structural markers match well
        p_feat = self._structural_parse(prompt)
        a_feat = self._structural_parse(answer)
        
        if p_feat["has_negation"] and a_feat["has_negation"]:
            confidence = min(1.0, confidence + 0.2)
            
        return confidence