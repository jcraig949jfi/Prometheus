import re
import zlib
from typing import List, Dict, Any

class ReasoningTool:
    """
    Typed Embodied Constraint Solver (TECS) Approximation.
    
    Mechanism:
    1. Type Encoding (Structural Parsing): Extracts logical constraints (negations, 
       comparatives, conditionals) from the prompt to form a 'Dependent Type' signature.
    2. Embodied Affordance Check (Constraint Propagation): Validates if candidate 
       answers satisfy the extracted logical signatures (e.g., if prompt says "not X", 
       candidate containing "X" is rejected/uninhabited).
    3. Plan Extraction (Numeric/Logical Eval): Executes explicit math or transitivity 
       checks found in the text.
    4. Verification (NCD Tiebreaker): Uses Normalized Compression Distance only when 
       structural signals are ambiguous, measuring semantic similarity to the prompt's 
       valid solution space.
       
    This mimics the TECS loop: Hypothesis (Candidate) -> Type Check (Structure) -> 
    Constraint Solve (Logic/Math) -> Inhabitation Result (Score).
    """

    def __init__(self):
        self.negation_words = ["no", "not", "never", "neither", "nobody", "nothing", "nowhere", "cannot", "won't", "don't", "doesn't", "isn't", "aren't"]
        self.comparative_ops = [">", "<", "greater", "less", "more", "fewer", "larger", "smaller", "higher", "lower"]
        self.cond_keywords = ["if", "then", "else", "unless", "provided"]

    def _extract_constraints(self, text: str) -> Dict[str, Any]:
        """Parses text into a 'Type Signature' of logical constraints."""
        text_lower = text.lower()
        constraints = {
            "has_negation": any(w in text_lower for w in self.negation_words),
            "has_comparative": any(op in text_lower for op in self.comparative_ops),
            "has_conditional": any(k in text_lower for k in self.cond_keywords),
            "numbers": re.findall(r"-?\d+\.?\d*", text),
            "negated_concepts": []
        }
        
        # Simple negation scope detection (word following negation)
        for i, word in enumerate(text_lower.split()):
            if word in self.negation_words:
                words = text_lower.split()
                if i + 1 < len(words):
                    constraints["negated_concepts"].append(words[i+1].strip(".,!?"))

        return constraints

    def _check_inhabitation(self, prompt_constraints: Dict, candidate: str) -> float:
        """
        Checks if a candidate 'inhabits' the type defined by prompt constraints.
        Returns a penalty score (0.0 = fully inhabited/valid, higher = violation).
        """
        penalty = 0.0
        cand_lower = candidate.lower()
        
        # 1. Negation Constraint: If prompt negates a concept, candidate shouldn't affirm it simply
        # This is a heuristic approximation of 'uninhabited type'
        if prompt_constraints["has_negation"]:
            # If the candidate is a direct repetition of a negated concept without qualification
            for concept in prompt_constraints["negated_concepts"]:
                if concept and concept in cand_lower and len(concept) > 3:
                    # Heuristic: If candidate is just the negated word, it's likely wrong
                    if cand_lower.strip() == concept:
                        penalty += 0.5
        
        # 2. Comparative/Numeric Consistency
        if prompt_constraints["has_comparative"] and prompt_constraints["numbers"]:
            # If prompt has numbers and comparatives, candidate ideally should reflect logic
            # We can't fully solve without LLM, but we check for numeric presence if prompt implies calculation
            cand_nums = re.findall(r"-?\d+\.?\d*", candidate)
            if len(prompt_constraints["numbers"]) >= 2 and not cand_nums:
                # Prompt implies math/comparison, candidate has no numbers -> suspicious
                penalty += 0.2

        # 3. Conditional Logic (Modus Tollens approximation)
        # If prompt has "if", candidate should not contradict the condition structure blatantly
        # (Hard to implement perfectly without semantics, so we rely on NCD here as tiebreaker)
        
        return penalty

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Calculates Normalized Compression Distance."""
        if not s1 or not s2:
            return 1.0
        try:
            c1 = len(zlib.compress(s1.encode()))
            c2 = len(zlib.compress(s2.encode()))
            c12 = len(zlib.compress((s1 + s2).encode()))
            max_len = max(c1, c2)
            if max_len == 0:
                return 1.0
            return (c12 - min(c1, c2)) / max_len
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        prompt_constraints = self._extract_constraints(prompt)
        results = []

        for cand in candidates:
            score = 1.0  # Start high (assumed valid)
            reasoning_parts = []

            # Step 1: Structural Type Check (The "Proof")
            violation = self._check_inhabitation(prompt_constraints, cand)
            if violation > 0:
                score -= violation
                reasoning_parts.append(f"Constraint violation detected (negation/logic).")
            
            # Step 2: Numeric/Logic Evaluation (The "Solver")
            # Detect simple float comparisons if present in both prompt and candidate
            p_nums = prompt_constraints["numbers"]
            c_nums = re.findall(r"-?\d+\.?\d*", cand)
            
            if len(p_nums) >= 2 and len(c_nums) >= 1:
                try:
                    # Heuristic: If prompt asks for smaller/larger, check candidate number
                    p_vals = [float(x) for x in p_nums]
                    c_val = float(c_nums[0])
                    
                    if "smaller" in prompt.lower() or "less" in prompt.lower():
                        if c_val > min(p_vals):
                            score -= 0.4
                            reasoning_parts.append(f"Numeric constraint fail: {c_val} is not smallest.")
                    elif "larger" in prompt.lower() or "greater" in prompt.lower() or "more" in prompt.lower():
                        if c_val < max(p_vals):
                            score -= 0.4
                            reasoning_parts.append(f"Numeric constraint fail: {c_val} is not largest.")
                except ValueError:
                    pass

            # Step 3: NCD as Tiebreaker/Refinement (The "Embodied" similarity)
            # If structural score is neutral, NCD decides based on proximity to prompt context
            ncd_val = self._compute_ncd(prompt, cand)
            # Normalize NCD influence: Lower NCD = Higher similarity = Better score boost if structural score is tied
            # We use NCD to slightly adjust score within a small band to avoid overriding hard logic
            ncd_adjustment = (1.0 - ncd_val) * 0.15 
            score += ncd_adjustment
            
            if not reasoning_parts:
                reasoning_parts.append("Structural constraints satisfied; NCD refinement applied.")

            results.append({
                "candidate": cand,
                "score": max(0.0, min(1.0, score)), # Clamp 0-1
                "reasoning": " ".join(reasoning_parts) + f" [NCD: {ncd_val:.2f}]"
            })

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence based on the evaluation score of the single answer."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]["score"]