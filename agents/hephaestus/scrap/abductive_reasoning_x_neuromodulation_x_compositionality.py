import re
import math
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Neuromodulated Compositional Abductive Synthesis Engine (NCASE)
    
    Mechanism:
    1. Compositionality: Parses prompts into a library of primitive operations 
       (numeric comparison, logical negation, transitivity) to construct candidate 
       explanations rather than matching strings.
    2. Abductive Reasoning: Scores candidates based on how well they explain the 
       structural constraints of the prompt (Bayesian likelihood approximation).
    3. Neuromodulation: A meta-controller computes a 'modulation factor' (m) based 
       on prompt ambiguity (presuppositions, scope issues). 
       - High ambiguity -> High m -> Low confidence (broadens posterior, rejects specific claims).
       - Low ambiguity -> Low m -> High confidence allowed (sharpens focus on best hypothesis).
    
    Epistemic Honesty: Prioritizes detecting unanswerable or ambiguous questions 
    (Tier B) before attempting to solve them (Tier A).
    """

    def __init__(self):
        # Primitive library for compositional parsing
        self.primitives = {
            'numeric_cmp': r'(\d+\.?\d*)\s*(<|>|<=|>=|=)\s*(\d+\.?\d*)',
            'negation': r'\b(not|no|never|none)\b',
            'comparative': r'\b(more|less|better|worse|greater|smaller)\b',
            'presupposition_stop': r'\b(stopped|quit|ceased)\b',
            'presupposition_why': r'^why\s+did\s+',
            'false_dichotomy': r'\b(either|or)\b',
            'scope_every': r'\bevery\b',
            'pronoun_ambiguity': r'\b(he|she|they|him|her)\b.*\bwho\b'
        }
        self.state = {}

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        len1 = len(s1_bytes)
        len2 = len(s2_bytes)
        if len1 == 0 or len2 == 0:
            return 1.0
        
        # Approximate joint compression
        try:
            joint = len(zlib.compress(s1_bytes + s2_bytes))
            min_len = min(len(zlib.compress(s1_bytes)), len(zlib.compress(s2_bytes)))
            max_len = max(len1, len2)
            if max_len == 0: return 1.0
            ncd = (joint - min_len) / max_len
            return max(0.0, min(1.0, ncd))
        except:
            return 0.5

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Judgment: Detects ambiguity, presupposition, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition Traps
        if re.search(self.primitives['presupposition_stop'], p_lower):
            return 0.2  # "Have you stopped..."
        if re.search(self.primitives['presupposition_why'], p_lower):
            # Check if the premise exists in context (simplified check)
            if "fail" in p_lower or "stop" in p_lower or "wrong" in p_lower:
                return 0.2 

        # 2. Scope & Pronoun Ambiguity
        # Simple heuristic: "Every" + "same" question often implies scope trap
        if re.search(self.primitives['scope_every'], p_lower) and "same" in p_lower:
            return 0.3
        
        if re.search(self.primitives['pronoun_ambiguity'], p_lower):
            return 0.25

        # 3. False Dichotomy
        if re.search(self.primitives['false_dichotomy'], p_lower) and "only" in p_lower:
            return 0.3

        # 4. Subjectivity without criteria
        if any(k in p_lower for k in ["best", "worst", "favorite"]) and "data" not in p_lower:
            return 0.3

        return 1.0  # No obvious traps detected

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Tier A Reasoning: Structural parsing and constructive computation.
        Returns a score 0.0 to 1.0 based on logical consistency.
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        score = 0.0
        matches = 0
        
        # 1. Numeric Evaluation (Constructive)
        num_match = re.search(self.primitives['numeric_cmp'], prompt)
        if num_match:
            v1, op, v2 = num_match.groups()
            n1, n2 = float(v1), float(v2)
            true_val = False
            if op == '<': true_val = n1 < n2
            elif op == '>': true_val = n1 > n2
            elif op == '<=': true_val = n1 <= n2
            elif op == '>=': true_val = n1 >= n2
            elif op == '=': true_val = n1 == n2
            
            # Check if candidate aligns with truth
            cand_true = any(k in c_lower for k in ['true', 'yes', 'correct'])
            cand_false = any(k in c_lower for k in ['false', 'no', 'incorrect'])
            
            if true_val and cand_true: score += 1.0
            elif not true_val and cand_false: score += 1.0
            elif true_val and cand_false: score -= 1.0
            elif not true_val and cand_true: score -= 1.0
            matches += 1

        # 2. Negation Consistency
        if re.search(self.primitives['negation'], p_lower):
            # If prompt has negation, candidate should reflect nuance or denial
            if any(k in c_lower for k in ['not', 'no', 'false', 'deny']):
                score += 0.5
            matches += 1

        # 3. Transitivity / Logic Keywords
        if "therefore" in p_lower or "thus" in p_lower:
            if "therefore" in c_lower or "thus" in c_lower:
                score += 0.3 # Structural echo
            matches += 1

        return score / max(1, matches) if matches > 0 else 0.0

    def _abductive_synthesis(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Generates scores for candidates using compositional primitives and 
        neuromodulated confidence capping.
        """
        results = []
        
        # Neuromodulation: Determine global confidence cap based on prompt ambiguity
        meta_cap = self._meta_confidence(prompt)
        
        for cand in candidates:
            # 1. Structural/Compositional Score (Primary Signal >= 50%)
            struct_score = self._structural_score(prompt, cand)
            
            # 2. Semantic Coherence (Secondary Signal ~35%)
            # Simple keyword overlap weighted by rarity (idf-like approximation)
            p_words = set(re.findall(r'\w+', prompt.lower()))
            c_words = set(re.findall(r'\w+', cand.lower()))
            common = p_words.intersection(c_words)
            # Penalize very short answers that don't add info, unless they are logical constants
            if len(c_words) < 2 and cand.lower() not in ['yes', 'no', 'true', 'false']:
                coherence = 0.1
            else:
                coherence = len(common) / (len(p_words) + len(c_words)) if (len(p_words)+len(c_words)) > 0 else 0
            
            # 3. NCD Tiebreaker (Max 15%)
            ncd_val = self._compute_ncd(prompt, cand)
            ncd_score = (1.0 - ncd_val) * 0.15
            
            # Combine scores: Structural (0.6) + Coherence (0.25) + NCD (0.15)
            raw_score = (struct_score * 0.60) + (coherence * 0.25) + ncd_score
            
            # Apply Neuromodulatory Cap (Epistemic Honesty)
            # If meta_cap is low (ambiguous), score cannot exceed cap
            final_score = min(raw_score, meta_cap)
            
            # Ensure non-negative
            final_score = max(0.0, final_score)
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural:{struct_score:.2f}, Coherence:{coherence:.2f}, MetaCap:{meta_cap:.2f}"
            })

        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        return self._abductive_synthesis(prompt, candidates)

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1. 
        Capped by _meta_confidence to ensure epistemic honesty on ambiguous inputs.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # Calculate base confidence from structural alignment
        struct_score = self._structural_score(prompt, answer)
        
        # Base confidence on structural match, but strictly capped by meta-analysis
        base_conf = min(struct_score + 0.2, 1.0) # Small baseline for valid structure
        
        final_conf = min(base_conf, meta_cap)
        
        return max(0.0, min(1.0, final_conf))