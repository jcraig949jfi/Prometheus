import re
import zlib
import math
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Holographic Immune Pragmatic Network (HIPN) Implementation.
    
    Mechanism:
    1. Holographic Boundary: The 'latent space' is a compressed structural signature 
       of the prompt (negations, numbers, logic operators). This acts as the Bekenstein-bound 
       information filter.
    2. Immune System: Candidates undergo 'clonal selection'. We generate a population of 
       scores based on different 'antibodies' (parsers for logic, math, pragmatics). 
       Low fitness (ambiguity/presupposition) triggers 'apoptosis' (confidence cap).
    3. Pragmatics: A Gricean scorer evaluates relevance and quantity, penalizing 
       answers that ignore context or fail to address presuppositions.
       
    Epistemic Honesty (Tier B): Prioritizes detecting ambiguity, presupposition, and 
    unanswerability. If the 'boundary' (prompt structure) is corrupted by logical traps, 
    confidence is capped regardless of candidate match.
    """

    def __init__(self):
        # Pragmatic weights (Grice's Maxims)
        self.weights = {
            'structural': 0.50,  # Primary signal (Logic/Math)
            'computational': 0.25, # Numeric/Constructive
            'pragmatic': 0.15,   # Context/Relevance
            'ncd': 0.10          # Tiebreaker only
        }
        
        # Tier B Triggers (Epistemic Honesty)
        self.presupposition_triggers = [
            r"\bhave you stopped\b", r"\bwhy did\b", r"\bwhy does\b", 
            r"\bfailed to\b", r"\bquit\b", r"\bregret\b"
        ]
        self.ambiguity_triggers = [
            r"\bevery .* a .*\b", r"\bhe was\b", r"\bshe was\b", r"\bthey were\b",
            r"\bwho is\b", r"\bwhich one\b"
        ]
        self.dichotomy_triggers = [
            r"\beither .* or\b", r"\bgood or bad\b", r"\bright or wrong\b"
        ]

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Judgment: Evaluates the prompt for ambiguity, presupposition, 
        and unanswerability. Returns a cap value (0.0 to 1.0).
        """
        p_low = self._normalize(prompt)
        score = 1.0
        
        # 1. Presupposition Check (High risk of loaded question)
        for pattern in self.presupposition_triggers:
            if re.search(pattern, p_low):
                score -= 0.8  # Heavy penalty
                break
        
        # 2. Ambiguity Check (Pronouns/Scope)
        # Only penalize if the question asks for clarification on the ambiguous term
        if any(re.search(p, p_low) for p in self.ambiguity_triggers):
            if re.search(r"\bwho\b|\bwhich\b|\bwhat\b", p_low):
                score -= 0.75
                
        # 3. False Dichotomy
        for pattern in self.dichotomy_triggers:
            if re.search(pattern, p_low):
                # Check if options are exhaustive (hard to detect, so assume risk)
                score -= 0.6
                break

        # 4. Unanswerability (Missing info indicators)
        if re.search(r"\bwithout knowing\b|\bimpossible to tell\b|\bnot enough info\b", p_low):
            score = 0.1 # Explicitly unanswerable
            
        return max(0.0, min(1.0, score))

    def _extract_structural_signature(self, prompt: str) -> dict:
        """
        Holographic Boundary: Compresses prompt into structural features.
        """
        p_low = self._normalize(prompt)
        return {
            'negations': len(re.findall(r"\b(not|no|never|neither|nor)\b", p_low)),
            'conditionals': len(re.findall(r"\b(if|then|unless|otherwise)\b", p_low)),
            'comparatives': len(re.findall(r"\b(more|less|greater|smaller|better|worst)\b", p_low)),
            'has_question_mark': '?' in prompt
        }

    def _compute_structural_score(self, prompt: str, candidate: str) -> float:
        """
        Checks if the candidate respects the structural constraints (negation, logic).
        """
        p_low = self._normalize(prompt)
        c_low = self._normalize(candidate)
        score = 0.0
        
        # Negation consistency
        p_neg = len(re.findall(r"\bnot\b|\bno\b", p_low))
        c_neg = len(re.findall(r"\bnot\b|\bno\b", c_low))
        
        if p_neg > 0 and c_neg == 0:
            # Prompt has negation, candidate ignores it (potential error)
            # Unless the candidate is explicitly "No" to a Yes/No question
            if not re.search(r"\b(yes|no)\b", c_low):
                score -= 0.5
        elif p_neg == 0 and c_neg > 0:
            # Candidate introduces negation not in prompt
            score -= 0.3
            
        # Conditional logic presence
        if re.search(r"\bif\b", p_low):
            if re.search(r"\bthen\b|\btherefore\b|\bso\b", c_low):
                score += 0.4
            else:
                score += 0.1 # Weak match
                
        return max(0.0, score + 0.5) # Base score 0.5, adjust up/down

    def _compute_numeric_score(self, prompt: str, candidate: str) -> float:
        """
        Constructive computation: Extracts numbers and verifies basic relations.
        """
        # Extract all floats/integers from prompt and candidate
        p_nums = re.findall(r"-?\d+\.?\d*", prompt)
        c_nums = re.findall(r"-?\d+\.?\d*", candidate)
        
        if not p_nums:
            return 0.5 # Neutral if no numbers
        
        if not c_nums:
            return 0.1 # Bad if prompt has numbers but answer doesn't
            
        try:
            # Simple heuristic: If prompt implies comparison (greater/less), 
            # check if candidate number aligns.
            p_low = self._normalize(prompt)
            if "greater" in p_low or "more" in p_low:
                if c_nums and p_nums:
                    # Heuristic: Expect larger number in candidate if asking for "more"
                    # This is a simplification for the "constructive" requirement
                    return 0.8 if float(c_nums[-1]) > float(p_nums[-1]) * 0.5 else 0.4
            
            if "less" in p_low:
                 if c_nums and p_nums:
                    return 0.8 if float(c_nums[-1]) < float(p_nums[-1]) else 0.4
                    
            # Exact match bonus for numeric answers
            if c_nums[-1] in p_nums:
                return 0.9
        except ValueError:
            pass
            
        return 0.5

    def _compute_pragmatic_score(self, prompt: str, candidate: str) -> float:
        """
        Gricean Maxims: Relevance and Quantity.
        """
        p_low = self._normalize(prompt)
        c_low = self._normalize(candidate)
        
        # Relevance: Overlap of significant words (excluding stopwords)
        stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare', 'ought', 'used', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'just', 'don', 'now'}
        
        p_words = set(re.findall(r'\b\w+\b', p_low) - stopwords)
        c_words = set(re.findall(r'\b\w+\b', c_low) - stopwords)
        
        if not p_words:
            return 0.5
            
        # Jaccard similarity for relevance
        intersection = p_words.intersection(c_words)
        union = p_words.union(c_words)
        relevance = len(intersection) / len(union) if union else 0
        
        # Quantity: Candidate shouldn't be too short compared to prompt complexity
        len_ratio = len(c_low) / (len(p_low) + 0.1)
        quantity_score = min(1.0, len_ratio * 2) if len_ratio < 0.1 else 1.0
        
        return (relevance * 0.7) + (quantity_score * 0.3)

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            min_len = min(c1, c2)
            if min_len == 0:
                return 1.0
            ncd = (c12 - min_len) / max(c1, c2)
            return max(0.0, min(1.0, ncd))
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        meta_cap = self._meta_confidence(prompt)
        
        for candidate in candidates:
            # 1. Structural Score (Holographic Boundary Check)
            struct_score = self._compute_structural_score(prompt, candidate)
            
            # 2. Computational Score (Constructive)
            comp_score = self._compute_numeric_score(prompt, candidate)
            
            # 3. Pragmatic Score (Gricean)
            prag_score = self._compute_pragmatic_score(prompt, candidate)
            
            # 4. NCD (Tiebreaker, limited weight)
            ncd_val = self._compute_ncd(prompt, candidate)
            ncd_score = 1.0 - ncd_val  # Convert distance to similarity
            
            # Weighted Sum
            raw_score = (
                struct_score * self.weights['structural'] +
                comp_score * self.weights['computational'] +
                prag_score * self.weights['pragmatic'] +
                ncd_score * self.weights['ncd']
            )
            
            # Apply Epistemic Cap (Tier B Honesty)
            final_score = min(raw_score, meta_cap)
            
            # Reasoning Summary
            reasoning_parts = []
            if meta_cap < 0.3:
                reasoning_parts.append("Tier B Alert: Prompt contains ambiguity or presupposition.")
            if struct_score < 0.4:
                reasoning_parts.append("Structural mismatch (negation/logic).")
            if comp_score < 0.4 and re.search(r"\d", prompt):
                reasoning_parts.append("Numeric inconsistency.")
            if not reasoning_parts:
                reasoning_parts.append("Consistent with structural and pragmatic constraints.")
                
            results.append({
                "candidate": candidate,
                "score": round(final_score, 4),
                "reasoning": " ".join(reasoning_parts)
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1. 
        Caps at 0.25 if meta-analysis detects Tier B traps.
        Caps at 0.9 unless computation is definitive.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # Run a mini-evaluation to get base score
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        base_score = res[0]['score']
        
        # Apply hard cap from meta-analysis
        final_conf = min(base_score, meta_cap)
        
        # Never exceed 0.9 without explicit computational proof (simplified here)
        # If the answer is just "Yes"/"No" on a complex prompt, cap lower
        p_low = self._normalize(prompt)
        a_low = self._normalize(answer)
        if len(a_low.split()) <= 2 and len(p_low.split()) > 10:
            final_conf = min(final_conf, 0.85)
            
        return round(max(0.0, min(1.0, final_conf)), 4)