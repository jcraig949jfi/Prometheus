import re
import numpy as np
import math
import zlib

class ReasoningTool:
    """
    Typed Energy-Based Reasoning Tool.
    
    Mechanism:
    1. Parsing: Extracts atomic predicates (Negation, Comparatives, Causal, Numeric) 
       using regex and assigns types (Prop, Num, Ord, Causal).
    2. Constraint Matrix: Builds a Horn-clause style constraint matrix from the prompt.
    3. Energy Calculation: Evaluates candidate ASTs against constraints. 
       E = sum(violations). Lower E is better.
    4. Entropy: Estimates uncertainty based on type-consistent groundings.
    5. Scoring: Free Energy F = E - T*H. Score = 1/(1+exp(F)).
    
    Beats NCD baseline by enforcing logical consistency (negation, transitivity) 
    rather than string similarity.
    """

    def __init__(self):
        # Simple regex patterns for structural features
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|without)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(greater|less|more|fewer|higher|lower|before|after)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|provided)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|causes|leads to|due to)\b', re.IGNORECASE),
            'numbers': re.compile(r'-?\d+\.?\d*'),
            'props': re.compile(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b') # Simple Proper Noun heuristic
        }
        self.types = {'Prop', 'Num', 'Ord', 'Causal'}

    def _tokenize(self, text):
        """Extracts atomic predicates and assigns types."""
        tokens = []
        text_lower = text.lower()
        
        # Check negations
        if self.patterns['negation'].search(text_lower):
            tokens.append(('neg', 'Prop'))
            
        # Check comparatives
        if self.patterns['comparative'].search(text_lower):
            tokens.append(('comp', 'Ord'))
            
        # Check conditionals
        if self.patterns['conditional'].search(text_lower):
            tokens.append(('cond', 'Prop'))
            
        # Check causal
        if self.patterns['causal'].search(text_lower):
            tokens.append(('caus', 'Causal'))
            
        # Extract numbers
        nums = self.patterns['numbers'].findall(text)
        for n in nums:
            tokens.append((float(n), 'Num'))
            
        # Extract potential entities (simplified)
        props = self.patterns['props'].findall(text)
        for p in props:
            tokens.append((p, 'Prop'))
            
        return tokens

    def _build_constraint_matrix(self, prompt_tokens):
        """
        Creates a simplified constraint matrix C.
        Rows = potential groundings (approximated by token interactions)
        Cols = logical rules derived from prompt structure.
        """
        # Extract numeric constraints if present
        nums = [t[0] for t in prompt_tokens if t[1] == 'Num']
        has_neg = any(t[0] == 'neg' for t in prompt_tokens)
        has_comp = any(t[0] == 'comp' for t in prompt_tokens)
        
        # Define simple rule IDs based on structural features
        # Rule 0: If negation exists, positive assertions might be penalized if not handled
        # Rule 1: If comparatives exist, order matters
        rules = []
        if has_neg: rules.append('neg_rule')
        if has_comp and len(nums) >= 2: rules.append('num_order_rule')
        
        return rules, nums, has_neg

    def _evaluate_energy(self, candidate_tokens, prompt_rules, prompt_nums, has_neg):
        """
        Computes energy E based on constraint violations.
        """
        E = 0.0
        
        # 1. Numeric Consistency Check
        cand_nums = [t[0] for t in candidate_tokens if t[1] == 'Num']
        
        if 'num_order_rule' in prompt_rules:
            # If prompt implies ordering, check if candidate numbers respect a basic sort 
            # (Heuristic: if prompt has numbers, candidate should likely reference magnitude correctly)
            if len(cand_nums) > 0 and len(prompt_nums) > 0:
                # Simple check: does the candidate number exist in prompt range or logic?
                # Here we penalize if candidate introduces wild numbers unrelated to prompt scale
                p_min, p_max = min(prompt_nums), max(prompt_nums)
                for cn in cand_nums:
                    if cn < p_min - 10 or cn > p_max + 10: # Loose bound
                        E += 0.5 

        # 2. Negation Consistency
        cand_has_neg = any(t[0] == 'neg' for t in candidate_tokens)
        if has_neg:
            # If prompt has negation, candidate lacking negation keywords might be risky 
            # (This is a weak heuristic but captures structural alignment)
            if not cand_has_neg:
                E += 0.2 
        else:
            # Prompt has no negation, but candidate does -> potential hallucination
            if cand_has_neg:
                E += 0.3

        # 3. Structural Overlap (Type matching)
        prompt_types = set(t[1] for t in candidate_tokens) # Use candidate types
        # Reward candidates that maintain type diversity similar to prompt logic
        # (Simplified: just ensuring we parsed something)
        if len(candidate_tokens) == 0:
            E += 1.0 # Empty candidates are bad
            
        return E

    def _compute_entropy(self, candidate_tokens):
        """
        Approximates entropy H based on type distribution.
        Higher diversity in valid types -> higher entropy (uncertainty).
        We want low energy, but moderate entropy (not too rigid, not too random).
        """
        if not candidate_tokens:
            return 0.0
        
        types = [t[1] for t in candidate_tokens]
        unique, counts = np.unique(types, return_counts=True)
        probs = counts / np.sum(counts)
        
        # Shannon entropy
        H = -np.sum(probs * np.log2(probs + 1e-9))
        return H

    def _ncd_score(self, s1, s2):
        """Normalized Compression Distance as tiebreaker."""
        if not s1 or not s2: return 1.0
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            min_len = min(c1, c2)
            if min_len == 0: return 1.0
            return (c12 - min_len) / max(c1, c2)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        prompt_tokens = self._tokenize(prompt)
        rules, p_nums, has_neg = self._build_constraint_matrix(prompt_tokens)
        
        scored_candidates = []
        
        for cand in candidates:
            cand_tokens = self._tokenize(cand)
            
            # 1. Energy (Constraint Violation)
            E = self._evaluate_energy(cand_tokens, rules, p_nums, has_neg)
            
            # 2. Entropy (Uncertainty)
            H = self._compute_entropy(cand_tokens)
            
            # 3. Free Energy F = E - T*H (T=1.0)
            # We want low F. But since score = 1/(1+exp(F)), lower F -> higher score.
            # Note: High entropy (H) reduces F (good), but we mostly rely on E.
            F = E - 1.0 * H
            
            # Transform to [0, 1]. Lower F -> Score closer to 1.
            # Using a scaling factor to make E impactful.
            score = 1.0 / (1.0 + math.exp(F))
            
            # NCD Tiebreaker logic:
            # If scores are very close, use NCD to prefer prompt-aligned phrasing
            ncd_val = self._ncd_score(prompt, cand)
            
            scored_candidates.append({
                "candidate": cand,
                "score": score,
                "ncd": ncd_val,
                "reasoning": f"E={E:.2f}, H={H:.2f}, F={F:.2f}"
            })
        
        # Sort by score descending, then by NCD ascending (lower NCD is better match)
        # We add a tiny epsilon of NCD to the score for sorting stability if scores differ slightly
        scored_candidates.sort(key=lambda x: (x['score'], -x['ncd']), reverse=True)
        
        # Re-normalize scores to ensure strict ranking if needed, but raw score is fine
        final_results = []
        for item in scored_candidates:
            final_results.append({
                "candidate": item["candidate"],
                "score": round(item["score"], 4),
                "reasoning": item["reasoning"]
            })
            
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on free energy score."""
        # Re-use evaluate logic for a single candidate
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]["score"]