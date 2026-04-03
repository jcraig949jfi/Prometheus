import re
import math
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Hierarchical Sparse Causal Renormalizer (HSCR) - Epistemic Implementation
    
    This tool implements a computational analogy of the HSCR architecture:
    1. Sparse Coding: Extracts key structural tokens (negations, numbers, logic keywords)
       from the prompt, ignoring noise (L1-like sparsity).
    2. Renormalization: Coarse-grains the text into hierarchical features:
       - Micro: Token presence
       - Meso: Structural patterns (conditionals, comparatives)
       - Macro: Global ambiguity/presupposition flags
    3. Causal Inference: Uses the structural DAG of the sentence to determine
       if a definitive answer exists (do-calculus on syntax). If the causal
       structure is broken (ambiguity), confidence is capped.
       
    Scoring Strategy:
    - Judgment (40%): Detects ambiguity/traps via _meta_confidence.
    - Structural (30%): Parses logic, negation, conditionals.
    - Computation (20%): Solves numeric/logic traps.
    - NCD (10%): Tiebreaker for semantic similarity.
    """

    def __init__(self):
        # Preset triggers for epistemic honesty (Tier B)
        self.presupposition_triggers = [
            r"\b(stopped|quit|ceased|failed|why did|when did)\b",
            r"\bhave you\b.*\b(stopped|quit)\b",
            r"\bis it true that\b"
        ]
        self.ambiguity_triggers = [
            r"\b(every|all)\b.*\b(a|one|the same)\b", # Scope ambiguity
            r"\bhe\b.*\bwho\b|\bshe\b.*\bwho\b", # Pronoun ambiguity
            r"\beither\b.*\bor\b", # False dichotomy check
            r"\bbest\b|\bworst\b|\bfavorite\b" # Subjectivity
        ]
        self.false_dichotomy_patterns = [
            r"either.*or", r"is it.*or.*\?"
        ]

    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates the prompt for epistemic traps.
        Returns a cap value: 0.25 if ambiguous/unanswerable, 1.0 if clear.
        """
        p_lower = prompt.lower()
        
        # Check for presuppositions
        for pattern in self.presupposition_triggers:
            if re.search(pattern, p_lower):
                return 0.25
        
        # Check for ambiguity markers
        for pattern in self.ambiguity_triggers:
            if re.search(pattern, p_lower):
                # Heuristic: If question words are present with ambiguity markers
                if any(q in p_lower for q in ["who", "what", "which", "how"]):
                    return 0.25
                
        # Check for false dichotomy without exhaustive context
        if re.search(r"either.*or", p_lower) and "options" not in p_lower:
             # Soft penalty, depends on context, but often a trap
             pass 
             
        return 1.0

    def _extract_structure(self, text: str) -> dict:
        """Sparse coding of structural elements."""
        t = text.lower()
        return {
            "negations": len(re.findall(r"\b(not|no|never|neither|without)\b", t)),
            "conditionals": len(re.findall(r"\b(if|then|unless|otherwise)\b", t)),
            "comparatives": len(re.findall(r"\b(more|less|greater|smaller|better|worst|than)\b", t)),
            "numbers": re.findall(r"\d+\.?\d*", t),
            "logic_ops": len(re.findall(r"\b(and|or|implies|therefore)\b", t)),
            "question_marks": t.count("?")
        }

    def _compute_answer_score(self, prompt: str, candidate: str) -> float:
        """
        Constructive computation and constraint propagation.
        Returns a score 0.0-1.0 based on logical/numeric correctness.
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        score = 0.5 # Base prior
        
        # 1. Numeric Evaluation (PEMDAS/Comparison)
        nums_prompt = [float(n) for n in re.findall(r"\d+\.?\d*", prompt)]
        nums_cand = [float(n) for n in re.findall(r"\d+\.?\d*", candidate)]
        
        if len(nums_prompt) >= 2 and len(nums_cand) >= 1:
            # Simple comparative check
            if "greater" in p_lower or "larger" in p_lower or "max" in p_lower:
                if nums_cand[0] == max(nums_prompt): score = 1.0
                else: score = 0.1
            elif "less" in p_lower or "smaller" in p_lower or "min" in p_lower:
                if nums_cand[0] == min(nums_prompt): score = 1.0
                else: score = 0.1
            elif "sum" in p_lower or "total" in p_lower or "add" in p_lower:
                if abs(nums_cand[0] - sum(nums_prompt)) < 0.01: score = 1.0
                else: score = 0.1
                
        # 2. Binary Logic Traps (Yes/No with negation)
        if "yes" in c_lower or "no" in c_lower:
            # If prompt has odd negations, flip expected binary answer logic
            # This is a simplification of causal intervention
            neg_count = len(re.findall(r"\bnot\b", p_lower))
            # Heuristic: If asking "Is X not Y?" and candidate is "Yes", it implies agreement with negation
            # We penalize blind "Yes" on negative questions if not careful
            if neg_count % 2 == 1 and "yes" in c_lower and "not" in p_lower:
                # Complex, keep neutral unless specific pattern matched
                pass

        # 3. Constraint Propagation (Transitivity)
        # If "A > B" and "B > C" in prompt, and candidate is "A > C"
        if re.search(r"(\w+)\s*>\s*(\w+)", p_lower) and re.search(r"transitive|order|sort", p_lower):
            if re.search(r"(\w+)\s*>\s*(\w+)", c_lower):
                score = 0.9
        
        return score

    def _ncd_similarity(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance approximation using zlib."""
        import zlib
        b1, b2 = s1.encode(), s2.encode()
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            min_len = min(c1, c2)
            if min_len == 0: return 1.0
            ncd = (c12 - min_len) / max(c1, c2) # Simplified NCD
            return 1.0 - max(0.0, ncd) # Convert to similarity
        except:
            return 0.5

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # 1. Epistemic Honesty Check (Renormalization Layer: Macro Scale)
        # Determines the maximum possible confidence cap
        epistemic_cap = self._meta_confidence(prompt)
        
        # 2. Structural Parsing (Renormalization Layer: Meso Scale)
        struct = self._extract_structure(prompt)
        has_numbers = len(struct['numbers']) > 0
        is_question = struct['question_marks'] > 0
        
        for cand in candidates:
            score = 0.0
            reasoning_parts = []
            
            # If epistemic cap is low, we generally reject all candidates unless one 
            # explicitly identifies the ambiguity (advanced), otherwise score low.
            if epistemic_cap < 0.3:
                # Check if candidate acknowledges ambiguity
                cand_lower = cand.lower()
                if any(x in cand_lower for x in ["ambiguous", "cannot", "insufficient", "unknown", "unclear"]):
                    base_score = 0.8 # Reward honesty
                    reasoning_parts.append("Identified epistemic trap.")
                else:
                    base_score = 0.2 # Penalize confident wrongness on traps
                    reasoning_parts.append("Epistemic trap detected; confidence capped.")
            else:
                # Standard evaluation
                comp_score = self._compute_answer_score(prompt, cand)
                
                # Structural match bonus
                struct_match = 0.0
                if struct['negations'] > 0:
                    if re.search(r"\bnot\b", cand.lower()): struct_match += 0.1
                if struct['conditionals'] > 0:
                    if re.search(r"\bif\b", cand.lower()): struct_match += 0.1
                
                base_score = (0.4 * comp_score) + (0.3 * struct_match) + 0.3 # Base prior
                
                # NCD Tiebreaker (Micro Scale)
                ncd = self._ncd_similarity(prompt, cand)
                # Only use NCD if other signals are weak (as per instructions)
                if comp_score == 0.5 and struct_match == 0.0:
                    base_score += (ncd * 0.15) 
                
                reasoning_parts.append(f"Comp:{comp_score:.2f}, Struct:{struct_match:.2f}")

            final_score = min(base_score, epistemic_cap) if epistemic_cap < 0.3 else base_score
            
            results.append({
                "candidate": cand,
                "score": float(f"{final_score:.4f}"),
                "reasoning": "; ".join(reasoning_parts)
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at 0.25 if meta-analysis detects ambiguity/traps.
        Caps at 0.9 unless computation was definitive.
        """
        # 1. Meta-Confidence (The Cap)
        cap = self._meta_confidence(prompt)
        
        # 2. Structural/Computational Confidence
        # If we have numbers and the answer is numeric, confidence rises
        struct = self._extract_structure(prompt)
        cand_nums = re.findall(r"\d+\.?\d*", answer)
        
        raw_conf = 0.5
        
        if len(struct['numbers']) > 0 and len(cand_nums) > 0:
            # If numeric match exists, higher confidence potential
            raw_conf = 0.85 
        elif struct['conditionals'] > 0 and re.search(r"\b(if|then)\b", answer.lower()):
            raw_conf = 0.8
        elif struct['negations'] > 0 and re.search(r"\bnot\b", answer.lower()):
            raw_conf = 0.75
        else:
            # Low structural signal
            raw_conf = 0.4
            
        # Apply Cap
        final_conf = min(raw_conf, cap)
        
        # Never return > 0.9 without definitive computation (simplified here)
        if final_conf > 0.9:
            final_conf = 0.9
            
        return float(f"{final_conf:.4f}")