import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Falsification-Driven Embodied Active Inference Tool.
    
    Mechanism:
    1. HYPOTHESIS (Conjecture): Treats each candidate answer as a provisional hypothesis 
       about the correct completion of the prompt.
    2. EMBODIED AFFORDANCE (Structural Parsing): Instead of physical sensors, the agent 
       uses structural parsing (negations, comparatives, conditionals, numeric logic) 
       as its "sensory affordances." These are the only valid probes into the problem space.
    3. FALSIFICATION (KL-Divergence Approximation): 
       - The agent constructs a "rival" hypothesis by logically inverting the structural 
         constraints found in the prompt (e.g., if prompt says "A > B", the rival assumes "B >= A").
       - It scores the candidate by how well it survives this falsification test. 
       - Candidates that contradict the parsed structural constraints receive a heavy penalty 
         (high expected KL-divergence from reality), effectively falsifying them.
       - Candidates consistent with constraints gain score based on NCD (compression) as a 
         secondary measure of coherence (low surprise).
    
    This implements Popperian falsification by actively seeking to disprove candidates 
    via logical constraint violation rather than just matching patterns.
    """

    def __init__(self):
        self.constraints = []
        self.numeric_baseline = 0.0

    def _parse_structure(self, text: str) -> Dict:
        """Extracts logical affordances: negations, comparatives, conditionals, numbers."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither|none)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|unless|provided|when)\b', text_lower)),
            'numbers': re.findall(r'-?\d+\.?\d*', text),
            'logic_ops': len(re.findall(r'\b(and|or|but|however|therefore)\b', text_lower))
        }
        return features

    def _check_constraint_violation(self, prompt: str, candidate: str) -> float:
        """
        Falsification Step: Checks if the candidate contradicts explicit structural 
        constraints in the prompt. Returns a penalty score (0.0 = no violation, 1.0 = falsified).
        """
        penalty = 0.0
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # 1. Negation Falsification
        # If prompt says "X is not Y" and candidate implies "X is Y"
        neg_matches = re.findall(r'(\w+)\s+is\s+not\s+(\w+)', p_lower)
        for subj, obj in neg_matches:
            if subj in c_lower and obj in c_lower:
                # Simple heuristic: if both subject and object appear in candidate without 'not',
                # it might be a contradiction. 
                # Refinement: Check if 'not' is absent in candidate near these words.
                if re.search(rf'{subj}.*{obj}', c_lower) and 'not' not in c_lower:
                    penalty += 0.5

        # 2. Comparative Falsification
        # If prompt says "A > B" and candidate suggests "B > A" or "A < B"
        comp_patterns = [
            (r'(\w+)\s+is\s+greater\s+than\s+(\w+)', lambda a, b: (a, b, 'gt')),
            (r'(\w+)\s+is\s+less\s+than\s+(\w+)', lambda a, b: (a, b, 'lt')),
            (r'(\w+)\s+>\s+(\w+)', lambda a, b: (a, b, 'gt')),
            (r'(\w+)\s+<\s+(\w+)', lambda a, b: (a, b, 'lt')),
        ]
        
        for pattern, extractor in comp_patterns:
            matches = re.findall(pattern, p_lower)
            for m in matches:
                a, b, op = extractor(*m) if len(m) == 2 else (*m, 'gt') # Simplified extraction
                
                # Check candidate for reverse logic
                if op == 'gt': # Prompt: A > B. Falsified if candidate says B > A or A < B
                    if re.search(rf'{b}.*{a}', c_lower) and re.search(r'(greater|more|>)', c_lower):
                        penalty += 0.4
                    if re.search(rf'{a}.*{b}', c_lower) and re.search(r'(less|smaller|<)', c_lower):
                        penalty += 0.4
                elif op == 'lt': # Prompt: A < B. Falsified if candidate says A > B
                    if re.search(rf'{a}.*{b}', c_lower) and re.search(r'(greater|more|>)', c_lower):
                        penalty += 0.4

        # 3. Numeric Consistency (Basic)
        p_nums = re.findall(r'-?\d+\.?\d*', prompt)
        c_nums = re.findall(r'-?\d+\.?\d*', candidate)
        
        if p_nums and c_nums:
            # If prompt defines a range or limit, check candidate
            # Example heuristic: If prompt has "max 10" and candidate has "15"
            if 'max' in p_lower or 'limit' in p_lower:
                try:
                    limit = float(p_nums[-1])
                    cand_val = float(c_nums[-1])
                    if cand_val > limit:
                        penalty += 0.6
                except ValueError:
                    pass

        return min(penalty, 1.0)

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            if c1 == 0 or c2 == 0: return 1.0
            return (c12 - min(c1, c2)) / max(c1, c2)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        results = []
        prompt_features = self._parse_structure(prompt)
        
        # Calculate baseline NCD among candidates to normalize scores slightly
        # This acts as the "prior" distribution over the hypothesis space
        
        for cand in candidates:
            # 1. Falsification Test (Primary Driver)
            # How much does this candidate violate the structural constraints?
            falsification_penalty = self._check_constraint_violation(prompt, cand)
            
            # 2. Information Gain / Coherence (Secondary)
            # Low NCD between prompt and candidate suggests high relevance (low surprise)
            # We invert NCD so higher is better. 
            ncd_val = self._compute_ncd(prompt, cand)
            coherence_score = 1.0 - ncd_val
            
            # 3. Structural Alignment Bonus
            # Does the candidate share structural features (e.g. numbers, logic words)?
            cand_features = self._parse_structure(cand)
            struct_match = 0.0
            if prompt_features['numbers'] and cand_features['numbers']:
                struct_match += 0.1
            if prompt_features['negations'] > 0 and cand_features['negations'] > 0:
                struct_match += 0.05
            if prompt_features['comparatives'] > 0 and cand_features['comparatives'] > 0:
                struct_match += 0.05

            # Final Score: Coherence - Falsification Penalty + Structural Bonus
            # Falsification is the hard filter (multiplicative or heavy subtractive)
            base_score = coherence_score + struct_match
            final_score = base_score * (1.0 - falsification_penalty * 0.8) # Strong penalty
            
            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": f"Falsification penalty: {falsification_penalty:.2f}, Coherence: {coherence_score:.2f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on falsification survival.
        If the answer is falsified by structural parsing, confidence is near 0.
        Otherwise, it scales with NCD coherence.
        """
        penalty = self._check_constraint_violation(prompt, answer)
        if penalty >= 0.5:
            return 0.05 # Strongly falsified
        
        ncd_val = self._compute_ncd(prompt, answer)
        coherence = 1.0 - ncd_val
        
        # Adjust coherence by penalty
        conf = coherence * (1.0 - penalty)
        return round(max(0.0, min(1.0, conf)), 4)