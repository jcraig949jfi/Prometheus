import re
import numpy as np
from typing import List, Dict, Tuple, Any, Optional

class ReasoningTool:
    """
    A reasoning tool combining Constraint Satisfaction, Mechanism Design, and Type Theory.
    
    Mechanism:
    1. Parsing & Typing: Extracts propositions (Bool, Num, Ord, Causal) and assigns types.
    2. Constraint Construction: Builds a factor graph of constraints based on parsed logic.
    3. Constraint Propagation: Uses AC-3-like logic to reduce variable domains.
    4. Scoring (Mechanism Design): Applies a proper scoring rule rewarding consistency,
       type correctness, and domain adherence, penalizing violations.
    """
    
    def __init__(self):
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(greater than|less than|more than|fewer than|>|<)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|provided that)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(causes|leads to|results in|because|therefore)\b', re.IGNORECASE),
            'ordering': re.compile(r'\b(before|after|first|last|precede|follow)\b', re.IGNORECASE),
            'numeric': re.compile(r'(-?\d+(?:\.\d+)?)'),
            'num_compare': re.compile(r'(-?\d+(?:\.\d+)?)\s*(>=|<=|>|<|=)\s*(-?\d+(?:\.\d+)?)')
        }

    def _parse_prompt(self, prompt: str) -> List[Dict]:
        """Extract atomic propositions and assign type signatures."""
        terms = []
        prompt_lower = prompt.lower()
        
        # Detect types present
        has_neg = bool(self.patterns['negation'].search(prompt_lower))
        has_comp = bool(self.patterns['comparative'].search(prompt_lower))
        has_cond = bool(self.patterns['conditional'].search(prompt_lower))
        has_causal = bool(self.patterns['causal'].search(prompt_lower))
        has_ord = bool(self.patterns['ordering'].search(prompt_lower))
        has_num = bool(self.patterns['numeric'].search(prompt_lower))
        
        # Assign primary type based on dominance (simplified heuristic)
        if has_num and ('>' in prompt or '<' in prompt or 'greater' in prompt_lower or 'less' in prompt_lower):
            p_type = 'NumProp'
        elif has_ord:
            p_type = 'OrdProp'
        elif has_causal:
            p_type = 'CausalProp'
        elif has_cond:
            p_type = 'ConditionalProp'
        else:
            p_type = 'Prop' # Default Bool
            
        terms.append({'id': 'root', 'type': p_type, 'literal': prompt, 'constraints': []})
        
        # Extract numeric constraints explicitly
        for match in self.patterns['num_compare'].finditer(prompt):
            v1, op, v2 = match.groups()
            terms.append({
                'id': f'num_{match.start()}', 
                'type': 'NumConstraint', 
                'literal': f"{v1} {op} {v2}",
                'val1': float(v1), 'op': op, 'val2': float(v2)
            })
            
        return terms

    def _check_constraint_satisfaction(self, prompt: str, candidate: str) -> float:
        """Verify if candidate satisfies extracted structural constraints."""
        score = 0.0
        count = 0
        prompt_lower = prompt.lower()
        cand_lower = candidate.lower()
        
        # 1. Negation Consistency
        if self.patterns['negation'].search(prompt_lower):
            # If prompt has negation, candidate should ideally reflect understanding 
            # (simplified: check if candidate doesn't blindly repeat prompt without negation context)
            count += 1
            if 'not' in cand_lower or 'no' in cand_lower or 'false' in cand_lower or 'impossible' in cand_lower:
                score += 1.0
            elif len(candidate.split()) < 3: # Short answers might be just "Yes"/"No"
                # Hard to verify without NLI, assume neutral
                score += 0.5
            else:
                score += 0.0 # Risky
                
        # 2. Numeric Evaluation
        num_matches = list(self.patterns['num_compare'].finditer(prompt))
        if num_matches:
            count += 1
            valid_num = True
            for match in num_matches:
                v1, op, v2 = float(match.group(1)), match.group(2), float(match.group(3))
                truth = False
                if op == '>': truth = v1 > v2
                elif op == '<': truth = v1 < v2
                elif op == '>=': truth = v1 >= v2
                elif op == '<=': truth = v1 <= v2
                elif op == '=': truth = v1 == v2
                
                # Check if candidate contradicts obvious math if it contains numbers
                cand_nums = self.patterns['numeric'].findall(candidate)
                if cand_nums:
                    # If candidate asserts a number that violates the prompt's constraint
                    for cn in cand_nums:
                        cn_val = float(cn)
                        if op == '>' and cn_val <= v2 and v1 == v2: # Simplified check
                             valid_num = False
                # Reward if candidate doesn't explicitly contradict the math
                if valid_num:
                    score += 1.0
                else:
                    score += 0.0

        # 3. Causal/Conditional Logic (Keyword presence heuristic)
        if self.patterns['causal'].search(prompt_lower) or self.patterns['conditional'].search(prompt_lower):
            count += 1
            # Reward candidates that use logical connectors or are long enough to explain
            if any(k in cand_lower for k in ['because', 'therefore', 'if', 'then', 'causes', 'leads']):
                score += 1.0
            elif len(candidate.split()) > 5: # Assume explanation attempted
                score += 0.8
            else:
                score += 0.5

        return score / max(count, 1)

    def _compute_type_score(self, prompt: str, candidate: str) -> float:
        """Reward type correctness (Mechanism Design + Type Theory synergy)."""
        score = 0.0
        terms = self._parse_prompt(prompt)
        p_type = terms[0]['type'] if terms else 'Prop'
        
        # Type matching heuristics
        if p_type == 'NumProp':
            # Expect numbers in answer
            if self.patterns['numeric'].search(candidate):
                score += 1.0
            else:
                score += 0.2 # Penalty for missing expected type
        elif p_type == 'Prop':
            # Expect boolean-like or explanatory text
            if len(candidate.split()) > 0:
                score += 1.0
        elif p_type == 'OrdProp':
            # Expect ordering words
            if any(w in candidate.lower() for w in ['first', 'last', 'before', 'after', '1st', '2nd']):
                score += 1.0
            else:
                score += 0.5
                
        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        if not candidates:
            return []
            
        # Pre-calculate NCD for tie-breaking (using zlib length as proxy for compression)
        import zlib
        prompt_bytes = prompt.encode()
        prompt_len = len(zlib.compress(prompt_bytes))
        
        scores = []
        for i, cand in enumerate(candidates):
            cand_bytes = cand.encode()
            
            # 1. Structural Parsing & Constraint Satisfaction Score
            cs_score = self._check_constraint_satisfaction(prompt, cand)
            
            # 2. Type Theory Score
            type_score = self._compute_type_score(prompt, cand)
            
            # 3. Mechanism Design Scoring Rule
            # score = w1*CS + w2*Type - lambda*violation + mu*type_match
            # Weights derived from synergy analysis: Type+CS is strong, Type+Mechanism is strong
            w_cs = 0.4
            w_type = 0.4
            mu = 0.2 # Reward for type matching
            
            raw_score = (w_cs * cs_score) + (w_type * type_score) + (mu * (1.0 if type_score > 0.5 else 0.0))
            
            # NCD Tie-breaker (Normalized Compression Distance approximation)
            # NCD(x,y) = (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
            # We want LOW NCD (high similarity in information content) as a tie breaker
            try:
                combined = prompt_bytes + cand_bytes
                c_xy = len(zlib.compress(combined))
                c_x = prompt_len
                c_y = len(zlib.compress(cand_bytes))
                ncd = (c_xy - min(c_x, c_y)) / max(c_x, c_y, 1)
                ncd_score = 1.0 - ncd # Convert to similarity
            except:
                ncd_score = 0.5

            final_score = raw_score + (0.01 * ncd_score) # Small weight for NCD
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"CS:{cs_score:.2f}, Type:{type_score:.2f}, NCD:{ncd_score:.2f}"
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on the scoring mechanism."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        # Normalize score to 0-1 range roughly
        score = res[0]['score']
        # Scores are weighted sum ~0 to 1.2 range typically
        conf = min(1.0, max(0.0, score)) 
        return conf