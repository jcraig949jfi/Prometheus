import re
import numpy as np
from typing import List, Dict, Tuple, Any, Optional

class ReasoningTool:
    """
    A reasoning evaluator combining Type Theory (parsing), Category Theory (constraint graphs),
    and Error Correcting Codes (syndrome scoring).
    
    Mechanism:
    1. Type Theory: Parses text into typed atomic predicates (Bool, Nat, Order, Caus).
    2. Category Theory: Builds a directed multigraph of constraints; maps to a constraint matrix.
    3. ECC: Treats satisfied constraints as a codeword. Computes syndrome distance from ideal.
    4. Metacognition: Detects ambiguity/presupposition to cap confidence (Epistemic Honesty).
    """

    def __init__(self):
        # Regex patterns for structural extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|cannot|impossible)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|only if)\b', re.I),
            'causal': re.compile(r'\b(because|causes|leads to|due to|since)\b', re.I),
            'quantifier': re.compile(r'\b(all|every|some|any|no|none)\b', re.I),
            'comparative': re.compile(r'\b(greater|less|more|fewer|before|after)\b', re.I),
            'number': re.compile(r'-?\d+\.?\d*'),
            'operator': re.compile(r'[<>=]'),
            # Ambiguity triggers
            'presupposition': re.compile(r'\b(stopped|quit|failed|regret|continue)\b.*\b(you|he|she|they|it)\b', re.I),
            'false_dichotomy': re.compile(r'\b(either|or)\b', re.I),
            'subjectivity': re.compile(r'\b(best|worst|favorite|beautiful|ugly)\b', re.I),
            'pronoun_ambiguity': re.compile(r'\b(he|she|they|him|her)\b.*\b(who|whom|which one)\b', re.I)
        }
        self.types = {'Bool', 'Nat', 'Order', 'Caus'}

    def _tokenize_and_type(self, text: str) -> List[Dict[str, Any]]:
        """Step 1: Parsing & Typing (Type Theory)"""
        tokens = []
        text_lower = text.lower()
        
        # Extract numbers
        nums = [float(n) for n in self.patterns['number'].findall(text)]
        
        # Simple typing heuristics
        if any(self.patterns['comparative'].search(text)):
            t_type = 'Order'
        elif any(self.patterns['causal'].search(text)):
            t_type = 'Caus'
        elif nums:
            t_type = 'Nat'
        else:
            t_type = 'Bool'

        # Create atomic predicates
        predicates = []
        if self.patterns['conditional'].search(text):
            predicates.append({'term': 'conditional_rule', 'type': 'Bool'})
        if self.patterns['negation'].search(text):
            predicates.append({'term': 'negation_present', 'type': 'Bool'})
        if nums:
            predicates.append({'term': f'nums:{nums}', 'type': 'Nat'})
            
        # Fallback if nothing specific found
        if not predicates:
            predicates.append({'term': text[:50], 'type': t_type})
            
        return predicates

    def _build_constraint_graph(self, prompt: str, candidate: str) -> Tuple[List[str], np.ndarray]:
        """Step 2: Constraint Diagram (Category Theory)"""
        # Vertices: Combined propositions from prompt and candidate
        p_preds = self._tokenize_and_type(prompt)
        c_preds = self._tokenize_and_type(candidate)
        
        all_preds = p_preds + c_preds
        n = len(all_preds)
        if n == 0:
            return [], np.array([])

        # Edges (Morphisms): Inference rules
        # We construct a constraint matrix C where rows are constraints and cols are propositions
        # Simplified: We check consistency between Prompt constraints and Candidate assertions
        
        constraints = []
        data = []
        
        # Rule 1: If prompt has negation, candidate must not contradict directly (simplified)
        # Rule 2: Numeric consistency
        p_nums = [float(x) for x in self.patterns['number'].findall(prompt)]
        c_nums = [float(x) for float(x) in self.patterns['number'].findall(candidate)]
        
        # Generate constraints based on structural overlap
        # Constraint: Candidate numbers must logically follow prompt numbers if operators exist
        if p_nums and c_nums:
            constraints.append("numeric_consistency")
            # Dummy row for numeric check
            row = [0] * n
            # Mark involved nodes
            for i in range(len(p_preds)): row[i] = 1 
            for i in range(len(c_preds)): row[len(p_preds)+i] = 1
            data.append(row)
            
        # Constraint: Logical flow (If prompt implies X, candidate must support X)
        if self.patterns['conditional'].search(prompt):
            constraints.append("logical_implication")
            row = [1] * n
            data.append(row)
            
        if not data:
            # Default single constraint: semantic overlap
            constraints.append("semantic_overlap")
            data.append([1] * n)
            
        return constraints, np.array(data)

    def _compute_syndrome_score(self, prompt: str, candidate: str) -> float:
        """Step 3: Error-Correcting Scoring (ECC)"""
        constraints, C = self._build_constraint_graph(prompt, candidate)
        if C.size == 0:
            return 0.5
            
        m, n = C.shape
        # Ideal codeword b: All constraints satisfied (1s)
        b = np.ones(m)
        
        # Evaluate candidate satisfaction vector v
        # Heuristic evaluation of constraints
        v = np.zeros(m)
        p_text = prompt.lower()
        c_text = candidate.lower()
        
        for i, cons in enumerate(constraints):
            if cons == "numeric_consistency":
                # Check if candidate numbers are derived from prompt or consistent
                p_nums = [float(x) for x in self.patterns['number'].findall(prompt)]
                c_nums = [float(x) for x in self.patterns['number'].findall(candidate)]
                if not p_nums:
                    v[i] = 1.0
                elif not c_nums:
                    v[i] = 0.0
                else:
                    # Simple arithmetic check: does candidate contain result of prompt ops?
                    # Or just presence of related numbers
                    v[i] = 1.0 if any(abs(p - c) < 0.01 for p in p_nums for c in c_nums) else 0.5
            elif cons == "logical_implication":
                # Check if candidate contains key terms from prompt
                common = set(p_text.split()) & set(c_text.split())
                v[i] = min(1.0, len(common) / max(1, len(set(p_text.split()))))
            else:
                # Semantic overlap baseline
                v[i] = 1.0 if any(word in c_text for word in p_text.split() if len(word)>3) else 0.0

        # Syndrome s = b XOR v (conceptually, here float difference)
        # Distance
        dist = np.sum(np.abs(b - v))
        max_dist = m
        score = 1.0 - (dist / max_dist) if max_dist > 0 else 0.5
        return float(score)

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty.
        Checks for ambiguity, presupposition, and unanswerability.
        Returns a cap value (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        if self.patterns['presupposition'].search(p_lower):
            return 0.2
        
        # 2. False Dichotomy
        if self.patterns['false_dichotomy'].search(p_lower) and 'or' in p_lower:
            # Check if options are exhaustive (hard to know, so penalize)
            return 0.4
            
        # 3. Subjectivity without criteria
        if self.patterns['subjectivity'].search(p_lower):
            if 'calculate' not in p_lower and 'math' not in p_lower:
                return 0.3
                
        # 4. Pronoun Ambiguity in questions
        if 'who' in p_lower and self.patterns['pronoun_ambiguity'].search(p_lower):
            return 0.2
            
        # 5. Unanswerable / Missing Info
        if 'impossible' in p_lower or 'unknown' in p_lower:
            return 0.1
            
        return 1.0

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (Tiebreaker only)"""
        try:
            z1 = len(repr(s1.encode('utf-8'))) # Approx compression size
            z2 = len(repr(s2.encode('utf-8')))
            z12 = len(repr((s1 + s2).encode('utf-8')))
            max_len = max(z1, z2)
            if max_len == 0: return 1.0
            return (z12 - min(z1, z2)) / max_len
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        p_nums = [float(x) for x in self.patterns['number'].findall(prompt)]
        has_math = bool(p_nums) and any(op in prompt for op in ['+', '-', '*', '/', 'sum', 'total', 'average'])
        
        for cand in candidates:
            # 1. Structural/ECC Score (Primary Signal)
            ecc_score = self._compute_syndrome_score(prompt, cand)
            
            # 2. Constructive Computation (If math detected)
            comp_score = 0.0
            if has_math:
                # Attempt to evaluate simple expressions if candidate looks like a number
                c_nums = [float(x) for x in self.patterns['number'].findall(cand)]
                if c_nums:
                    # Heuristic: If prompt asks for sum, check if candidate matches sum
                    # This is a simplified constructive check
                    if 'sum' in prompt.lower() or 'total' in prompt.lower():
                        expected = sum(p_nums)
                        if any(abs(c - expected) < 0.01 for c in c_nums):
                            comp_score = 1.0
                    else:
                        # Generic numeric presence boost
                        comp_score = 0.5
            
            # Weighted Score: Structural (50%) + Computation (35%) + NCD (15%)
            # NCD calculation (expensive, only if needed for tie-breaking or low structural)
            ncd_val = self._ncd_score(prompt, cand)
            ncd_score = 1.0 - ncd_val # Higher is better
            
            final_score = (ecc_score * 0.50) + (comp_score * 0.35) + (ncd_score * 0.15)
            
            # Reasoning string
            reason = f"ECC:{ecc_score:.2f}, Comp:{comp_score:.2f}, NCD:{ncd_score:.2f}"
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reason
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-analysis of the prompt (Tier B).
        """
        # 1. Calculate base score
        res_list = self.evaluate(prompt, [answer])
        base_score = res_list[0]['score'] if res_list else 0.0
        
        # 2. Apply Meta-Confidence Cap (Epistemic Honesty)
        meta_cap = self._meta_confidence(prompt)
        
        # If prompt is ambiguous/trap, confidence cannot exceed cap
        if meta_cap < 0.5:
            return min(base_score, meta_cap)
            
        # 3. Penalize low structural signal
        # If no structural matches found (score derived mostly from NCD), keep confidence low
        if base_score < 0.4:
            return base_score * 0.8
            
        # 4. Never overconfident without computation
        # Unless it's a clear structural match
        if base_score > 0.9:
            # Require strong structural evidence
            if "numeric_consistency" in prompt or "logical_implication" in prompt:
                 return min(base_score, 0.95)
            return min(base_score, 0.85)
            
        return base_score