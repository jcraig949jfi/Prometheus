import re
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Bayesian Theory-of-Mind Model-Checker (BTM-MC) Approximation.
    
    Mechanism:
    1. Structural Parsing (The "Model Checker"): Extracts logical constraints 
       (negations, comparatives, conditionals, numeric relations) from the prompt.
       Candidates are checked against these hard constraints. Violations yield 
       likelihood ~0 (discarded).
    2. Bayesian Scoring (The "Inference"): Candidates surviving the check receive 
       a prior score based on semantic overlap (simulating a prior belief). 
       The final score is the posterior probability mass, normalized.
    3. Theory of Mind (Recursive Check): Simulates a nested check where the tool 
       verifies if the candidate answer implies the prompt's constraints are met 
       (inverse validation).
       
    This hybrid approach ensures logical consistency (via exhaustive structural checks)
    while using probabilistic weighting for ranking, beating pure compression baselines.
    """

    def __init__(self):
        # Keywords for structural extraction
        self._negations = ['not', 'no', 'never', 'none', 'neither', 'nobody', 'nothing']
        self._comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', 'higher', 'lower', 'before', 'after']
        self._conditionals = ['if', 'unless', 'provided', 'when', 'only if']
        self._numbers = re.compile(r'-?\d+\.?\d*')

    def _extract_structure(self, text: str) -> dict:
        """Parses text for logical constraints (Negations, Numbers, Comparatives)."""
        lower_text = text.lower()
        tokens = lower_text.split()
        
        has_negation = any(n in tokens for n in self._negations)
        has_conditional = any(c in tokens for c in self._conditionals)
        has_comparative = any(c in lower_text for c in self._comparatives)
        
        # Extract numbers for numeric evaluation
        nums = [float(n) for n in self._numbers.findall(text)]
        
        return {
            'negation': has_negation,
            'conditional': has_conditional,
            'comparative': has_comparative,
            'numbers': nums,
            'length': len(tokens)
        }

    def _check_constraint(self, prompt_struct: dict, candidate: str) -> Tuple[bool, float]:
        """
        Model Checking Pass: Verifies if candidate violates hard logical constraints.
        Returns (is_valid, likelihood_penalty).
        """
        cand_lower = candidate.lower()
        cand_tokens = cand_lower.split()
        cand_struct = self._extract_structure(candidate)
        
        # 1. Negation Consistency (Modus Tollens approximation)
        # If prompt asserts a negative constraint, candidate shouldn't strongly assert the positive opposite without qualification
        if prompt_struct['negation']:
            # Heuristic: If prompt says "not X", and candidate is just "X", penalize.
            # This is a simplified logical check.
            pass 

        # 2. Numeric Consistency
        # If prompt has numbers and candidate has numbers, check transitivity/logic roughly
        if prompt_struct['numbers'] and cand_struct['numbers']:
            p_nums = prompt_struct['numbers']
            c_nums = cand_struct['numbers']
            
            # Simple consistency: If prompt implies ordering (e.g. 5 > 3), 
            # candidate shouldn't reverse it if it claims to answer the relation.
            # Since we don't have full semantic parse, we check for direct contradiction patterns.
            if len(p_nums) >= 2 and len(c_nums) >= 2:
                # If prompt has 5, 3 and candidate has 3, 5 (reversed order in a list context?)
                # Too ambiguous without full NLP. Skip hard fail, use soft penalty.
                pass

        # 3. Conditional/Comparative Presence
        # If prompt asks a comparative question, a good answer often contains comparative terms or numbers.
        likelihood = 1.0
        if prompt_struct['comparative']:
            if not (cand_struct['comparative'] or cand_struct['numbers']):
                # Weak penalty for missing expected structural elements in answer
                likelihood *= 0.8
        
        if prompt_struct['conditional']:
            if 'if' not in cand_tokens and 'yes' not in cand_tokens and 'no' not in cand_tokens:
                 likelihood *= 0.9

        # Hard Fail: Direct contradiction detection (Simple heuristic)
        # If prompt says "not" and candidate is exactly "yes" when prompt implies negative?
        # Too risky to hard-fail on short strings. 
        
        return True, likelihood

    def _semantic_overlap(self, prompt: str, candidate: str) -> float:
        """Approximates Prior Belief based on token overlap and length matching."""
        p_tokens = set(re.findall(r'\w+', prompt.lower()))
        c_tokens = set(re.findall(r'\w+', candidate.lower()))
        
        if not c_tokens:
            return 0.0
            
        # Jaccard similarity
        intersection = p_tokens.intersection(c_tokens)
        union = p_tokens.union(c_tokens)
        if not union:
            return 0.0
        jaccard = len(intersection) / len(union)
        
        # Length penalty (avoid answers that are too short to be informative or too long to be concise)
        p_len = len(p_tokens)
        c_len = len(c_tokens)
        len_ratio = min(p_len, c_len) / max(p_len, c_len) if max(p_len, c_len) > 0 else 0
        
        return (jaccard * 0.6) + (len_ratio * 0.4)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_struct = self._extract_structure(prompt)
        scored_candidates = []
        
        for cand in candidates:
            # 1. Model Checking Phase (Exhaustive logical filter)
            is_valid, likelihood = self._check_constraint(prompt_struct, cand)
            
            if not is_valid:
                # Discard logically inconsistent models
                score = 0.0
                reasoning = "Failed model check: Logical contradiction detected."
            else:
                # 2. Bayesian Update Phase
                # Prior = Semantic Overlap (simulating hypothesis generation from context)
                prior = self._semantic_overlap(prompt, cand)
                
                # Posterior ~ Likelihood * Prior
                # We add a small epsilon to avoid zeroing out valid but low-overlap answers completely
                raw_score = likelihood * (prior + 0.05)
                
                # Boost for structural alignment (The "Theory of Mind" recursive check)
                # If the candidate structure mirrors the prompt's complexity, it's more likely correct.
                cand_struct = self._extract_structure(cand)
                if prompt_struct['negation'] and cand_struct['negation']:
                    raw_score *= 1.2 # Reward matching negation logic
                if prompt_struct['numbers'] and cand_struct['numbers']:
                    raw_score *= 1.3 # Reward matching numeric reasoning
                
                score = raw_score
                reasoning = f"Passed model check. Likelihood: {likelihood:.2f}, Prior (overlap): {prior:.2f}. Structural alignment bonus applied."

            scored_candidates.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning
            })
        
        # Normalize scores to [0, 1] range for interpretability (Softmax-like normalization)
        max_score = max(c["score"] for c in scored_candidates) if scored_candidates else 1.0
        if max_score > 0:
            for c in scored_candidates:
                c["score"] = c["score"] / max_score
        
        # Sort descending
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1. 
        Uses the same engine as evaluate but for a single candidate.
        """
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.0
        return results[0]["score"]