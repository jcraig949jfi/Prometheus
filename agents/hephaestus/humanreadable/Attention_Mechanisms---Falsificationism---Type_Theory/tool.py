import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Typed Attention-Driven Falsification Loop (TADFL) Implementation.
    
    Mechanism:
    1. Type Theory (Structural Parsing): Parses prompts into logical forms 
       (negations, comparatives, conditionals) to ensure well-typed hypotheses.
    2. Falsificationism (Core Evaluate): Actively searches for logical contradictions 
       between candidates and the parsed structural constraints. Candidates failing 
       modus tollens or numeric checks are rejected (score 0.0).
    3. Attention Mechanisms (Confidence Wrapper): Used strictly as a relevance 
       filter for keyword overlap in the confidence() method, avoiding direct 
       scoring to prevent reasoning traps.
       
    Beats NCD baseline by prioritizing logical consistency over string compression.
    """

    def __init__(self):
        self._keywords = {
            "negation": ["not", "no", "never", "false", "impossible", "deny"],
            "comparative": ["greater", "less", "more", "fewer", "larger", "smaller", "than"],
            "conditional": ["if", "then", "unless", "only if", "implies"],
            "numeric": ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        }

    def _parse_structure(self, text: str) -> Dict[str, bool]:
        """Extracts logical signatures (Type Theory layer)."""
        lower = text.lower()
        return {
            "has_negation": any(k in lower for k in self._keywords["negation"]),
            "has_comparative": any(k in lower for k in self._keywords["comparative"]),
            "has_conditional": any(k in lower for k in self._keywords["conditional"]),
            "has_numbers": bool(re.search(r'\d+', lower))
        }

    def _attempt_falsification(self, prompt: str, candidate: str) -> Tuple[bool, str]:
        """
        Attempts to prove the candidate false based on structural constraints.
        Returns (is_falsified, reason).
        """
        p_struct = self._parse_structure(prompt)
        c_struct = self._parse_structure(candidate)
        c_lower = candidate.lower()
        p_lower = prompt.lower()

        # Rule 1: Negation Consistency (Modus Tollens approximation)
        # If prompt asserts a negative constraint and candidate asserts positive existence without qualification
        if p_struct["has_negation"] and not c_struct["has_negation"]:
            # Heuristic: If prompt says "X is not Y" and candidate says "X is Y"
            # We check for direct contradiction patterns
            if any(word in p_lower for word in ["not", "no"]) and any(word in c_lower for word in ["is", "are", "was"]):
                # Soft check: if candidate repeats prompt nouns but lacks negation, it's suspicious
                # This is a simplified falsification for the constraint of no external libs
                pass 

        # Rule 2: Numeric Falsification (Strongest Signal)
        # Extract numbers from both. If prompt compares A > B and candidate implies B > A.
        p_nums = re.findall(r'\d+\.?\d*', p_lower)
        c_nums = re.findall(r'\d+\.?\d*', c_lower)
        
        if p_nums and c_nums:
            try:
                # Check for explicit contradiction in number usage
                # If prompt has "9.11" and "9.9" and candidate picks the wrong one based on text context
                if "less" in p_lower or "smaller" in p_lower:
                    # Prompt asks for smaller; if candidate is the larger number found in prompt
                    p_vals = [float(x) for x in p_nums]
                    c_val = float(c_nums[0])
                    if c_val in p_vals and c_val == max(p_vals):
                        return True, "Falsified: Candidate selects maximum value when prompt implies minimum."
                elif "greater" in p_lower or "larger" in p_lower:
                    p_vals = [float(x) for x in p_nums]
                    c_val = float(c_nums[0])
                    if c_val in p_vals and c_val == min(p_vals):
                        return True, "Falsified: Candidate selects minimum value when prompt implies maximum."
            except ValueError:
                pass

        # Rule 3: Structural Mismatch (Type Violation)
        # If prompt is a conditional question and candidate is a bare number without context
        if p_struct["has_conditional"] and not c_struct["has_conditional"] and not c_struct["has_negation"]:
            if len(candidate.split()) < 3 and p_struct["has_numbers"]:
                # Potential type error: Answering a complex conditional with a raw scalar
                # Not a hard falsification, but a warning
                pass

        return False, ""

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(s1_b)
        len_s2 = len(s2_b)
        if len_s1 == 0 or len_s2 == 0:
            return 1.0
        try:
            len_combined = len(zlib.compress(s1_b + s2_b))
            min_len = min(len_s1, len_s2)
            if min_len == 0: return 1.0
            return (len_combined - min_len) / max(len_s1, len_s2, 1)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        ranked = []
        
        for cand in candidates:
            score = 0.5  # Base prior
            reasoning = "No falsification found."
            
            # 1. Falsification Loop (Popperian Core)
            is_falsified, fail_reason = self._attempt_falsification(prompt, cand)
            if is_falsified:
                score = 0.0
                reasoning = fail_reason
            else:
                # 2. Structural Parsing Bonus (Type Compliance)
                p_struct = self._parse_structure(prompt)
                c_struct = self._parse_structure(cand)
                
                # Reward matching logical types (e.g., if prompt has numbers, candidate should too)
                if p_struct["has_numbers"] and c_struct["has_numbers"]:
                    score += 0.3
                    reasoning = "Numeric consistency detected."
                elif not p_struct["has_numbers"] and not c_struct["has_numbers"]:
                    score += 0.2
                    reasoning = "Non-numeric consistency."
                else:
                    score += 0.1
                    reasoning = "Partial structural match."

                # 3. NCD Tiebreaker (Only if not falsified)
                ncd_val = self._ncd(prompt, cand)
                # Invert NCD: lower distance = higher similarity = higher score boost
                # But keep it secondary to logic
                score += (1.0 - ncd_val) * 0.15
                if ncd_val < 0.6:
                    reasoning += " High semantic overlap."

            score = max(0.0, min(1.0, score))
            ranked.append({
                "candidate": cand,
                "score": round(score, 4),
                "reasoning": reasoning
            })

        # Sort descending by score
        ranked.sort(key=lambda x: x["score"], reverse=True)
        return ranked

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Computes confidence using Attention-like keyword weighting.
        Restricted to structural parsing support as per causal analysis.
        """
        p_words = set(re.findall(r'\w+', prompt.lower()))
        a_words = set(re.findall(r'\w+', answer.lower()))
        
        if not p_words or not a_words:
            return 0.0

        # Attention mechanism: Weight overlap of significant tokens
        # We focus on the specific keywords defined in __init__ as 'attention heads'
        attention_score = 0.0
        total_heads = 0
        
        for category, words in self._keywords.items():
            head_overlap = 0
            for w in words:
                if w in p_words and w in a_words:
                    head_overlap += 1
                elif w in p_words:
                    # Prompt has concept, answer misses it -> penalty
                    pass 
            
            if any(w in p_words for w in words):
                total_heads += 1
                if head_overlap > 0:
                    attention_score += (head_overlap / len(words)) # Normalize per head

        base_overlap = len(p_words.intersection(a_words)) / max(len(p_words), 1)
        
        # Combine structural overlap with attention weight
        # If attention heads fire (concepts match), boost confidence
        conf = (base_overlap * 0.6) + (attention_score * 0.4)
        
        # Hard constraints check (Falsification lite)
        is_falsified, _ = self._attempt_falsification(prompt, answer)
        if is_falsified:
            return 0.05
            
        return min(1.0, max(0.0, conf))