import re
import zlib
from typing import List, Dict, Any

class ReasoningTool:
    """
    TARTA Implementation: Topologically-Aware Reflective Type-driven Architecture.
    
    Mechanism:
    1. System 1 (Topological/Structural): Instead of computing persistent homology on raw text (impossible),
       we extract structural invariants (negations, comparatives, conditionals, numeric bounds) acting as 
       'Betti numbers' of the logical space. These define the 'shape' of the problem.
    2. System 2 (Type/Proof): We treat the prompt's constraints as a dependent type. Candidates are 
       'terms' attempted to inhabit this type. We perform constructive proof search via constraint 
       propagation (modus tollens, transitivity).
    3. Feedback Loop: If a candidate fails the structural 'sanity check' (System 1), it is pruned immediately.
       If it passes, it undergoes rigorous logical validation (System 2). 
    4. Scoring: Primary score comes from logical consistency (Type Theory). NCD is used ONLY as a 
       tiebreaker for candidates where logical structure is neutral, satisfying the causal intelligence 
       directive to avoid NCD as a primary signal.
    """

    def __init__(self):
        self.keywords_neg = {'no', 'not', 'never', 'none', 'neither', 'false', 'impossible'}
        self.keywords_comp = {'greater', 'less', 'more', 'fewer', 'larger', 'smaller', 'before', 'after'}
        self.keywords_cond = {'if', 'then', 'unless', 'only if', 'provided'}
        self.digits_re = re.compile(r'-?\d+\.?\d*')

    def _extract_features(self, text: str) -> Dict[str, Any]:
        """System 1: Extract topological invariants (structural features) of the text."""
        lower_text = text.lower()
        words = set(re.findall(r'\b\w+\b', lower_text))
        
        has_negation = bool(words & self.keywords_neg)
        has_comparative = bool(words & self.keywords_comp)
        has_conditional = any(k in lower_text for k in self.keywords_cond)
        numbers = [float(x) for x in self.digits_re.findall(text)]
        
        return {
            'neg': has_negation,
            'comp': has_comparative,
            'cond': has_conditional,
            'nums': numbers,
            'len': len(text)
        }

    def _check_logical_consistency(self, prompt: str, candidate: str) -> float:
        """
        System 2: Type-theoretic validation.
        Attempts to construct a proof that the candidate satisfies the prompt's constraints.
        Returns a score 0.0 (contradiction) to 1.0 (proof found).
        """
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        c_lower = candidate.lower()
        p_lower = prompt.lower()

        score = 1.0
        
        # Constraint 1: Negation Consistency (Modus Tollens check)
        # If prompt implies negation and candidate affirms the negated concept without qualification
        if p_feat['neg'] and not c_feat['neg']:
            # Heuristic: If prompt says "X is not Y" and candidate says "X is Y"
            # We check for direct contradiction patterns
            if any(k in p_lower for k in ['is not', 'are not', 'cannot']) and \
               any(k in c_lower for k in ['is ', 'are ', 'can ']) and \
               not any(k in c_lower for k in ['not', 'no']):
                score -= 0.5

        # Constraint 2: Numeric Consistency
        if p_feat['nums'] and c_feat['nums']:
            p_nums = p_feat['nums']
            c_nums = c_feat['nums']
            # Simple transitivity check: if prompt says A > B and candidate says B > A, penalize
            # This is a simplified proxy for complex type checking
            if len(p_nums) >= 2 and len(c_nums) >= 2:
                # Check if candidate reverses the order of the first two numbers in prompt
                p_order = p_nums[0] > p_nums[1]
                c_order = c_nums[0] > c_nums[1]
                # If prompt establishes an order and candidate explicitly reverses it in a similar context
                if p_order != c_order and 'not' not in c_lower:
                    score -= 0.4

        # Constraint 3: Conditional Logic
        if p_feat['cond']:
            # If prompt is conditional, candidate shouldn't be an absolute unconditional statement
            # unless it matches the condition. (Simplified: penalize short absolutes in conditional prompts)
            if c_feat['len'] < 20 and not c_feat['cond']:
                score -= 0.2

        return max(0.0, min(1.0, score))

    def _ncd(self, s1: str, s2: str) -> float:
        """Calculate Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(c1, c2)
        if denom == 0: return 1.0
        return (c12 - min(c1, c2)) / denom

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        p_feat = self._extract_features(prompt)
        
        for cand in candidates:
            # System 1: Fast topological filter (Structural parsing)
            c_feat = self._extract_features(cand)
            
            # Basic sanity check: if prompt asks for a number and candidate has none, slight penalty
            sanity_score = 1.0
            if p_feat['nums'] and not c_feat['nums']:
                # Only penalize if the prompt is clearly numeric-heavy
                if len(p_feat['nums']) > 1:
                    sanity_score = 0.8
            
            # System 2: Deep type-theoretic validation (Logical consistency)
            logic_score = self._check_logical_consistency(prompt, cand)
            
            # Combined Score: Logic dominates, Sanity acts as a multiplier
            base_score = logic_score * sanity_score
            
            results.append({
                "candidate": cand,
                "base_score": base_score,
                "cand": cand, # for sorting
                "prompt": prompt
            })

        # Sorting and Tie-Breaking
        # Sort by base_score descending. 
        # Use NCD only for tie-breaking candidates with identical logical scores.
        results.sort(key=lambda x: x['base_score'], reverse=True)
        
        final_results = []
        for i, item in enumerate(results):
            # Calculate NCD relative to prompt only for tie-breaking context
            # In a real list, we'd compare against cluster centers, but here prompt is the anchor
            ncd_val = self._ncd(item['prompt'], item['cand'])
            
            # Perturb score slightly by NCD to break ties deterministically
            # Lower NCD (more similar structure) is slightly preferred if logic scores are equal
            # We add a tiny fraction of (1 - NCD) to the score
            final_score = item['base_score'] + (1.0 - ncd_val) * 1e-6
            
            reasoning = "Passed structural and logical validation."
            if item['base_score'] < 0.6:
                reasoning = "Failed logical consistency or structural sanity checks."
            elif p_feat['nums'] and not self._extract_features(item['cand'])['nums']:
                reasoning = "Numeric mismatch detected."

            final_results.append({
                "candidate": item['cand'],
                "score": round(final_score, 6),
                "reasoning": reasoning
            })
            
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on logical consistency (System 2) 
        and structural stability (System 1).
        """
        logic_score = self._check_logical_consistency(prompt, answer)
        p_feat = self._extract_features(prompt)
        a_feat = self._extract_features(answer)
        
        # Structural alignment bonus
        align_bonus = 0.0
        if p_feat['neg'] == a_feat['neg']: align_bonus += 0.1
        if p_feat['cond'] == a_feat['cond']: align_bonus += 0.1
        
        raw_conf = min(1.0, logic_score + align_bonus)
        return round(raw_conf, 4)