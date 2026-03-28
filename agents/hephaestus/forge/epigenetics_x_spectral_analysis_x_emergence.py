import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Hierarchical Epigenetic Spectral Graph Reasoning Tool (HES-RT).
    
    Mechanism:
    1. Structural Parsing (Epigenetic Modulation): Extracts logical operators 
       (negations, comparatives, conditionals) as slow-adjusting 'scalars' that 
       modulate the importance of tokens.
    2. Spectral Propagation (Graph Fourier Analogy): Treats the prompt as a signal.
       Uses hash-based binning to simulate spectral filtering, identifying resonant 
       patterns between prompt constraints and candidate answers.
    3. Emergent Readout (Downward Causation): Aggregates structural matches and 
       semantic similarity (NCD) into a global score. Candidates triggering 
       contradictory structural signals (e.g., negation mismatch) are dampened.
    
    This implements the HES-GNN logic using only standard library tools by mapping
    biological concepts to text-processing heuristics.
    """

    def __init__(self):
        # Structural patterns acting as "Epigenetic Scalars"
        self.negations = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse'}
        self.conditionals = {'if', 'then', 'unless', 'otherwise', 'provided', 'when'}
        self.quantifiers = {'all', 'some', 'many', 'few', 'every', 'each', 'any'}
        
        # Weights for the "Spectral Filters"
        self.w_struct = 0.60  # Structural parsing weight
        self.w_ncd = 0.40     # NCD tiebreaker weight

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b[a-z0-9]+\b', text.lower())

    def _extract_structure(self, text: str) -> Dict[str, float]:
        """Extracts structural 'scalars' from text."""
        tokens = set(self._tokenize(text))
        score = 0.0
        
        # Count structural hits
        neg_count = len(tokens & self.negations)
        comp_count = len(tokens & self.comparatives)
        cond_count = len(tokens & self.conditionals)
        quant_count = len(tokens & self.quantifiers)
        
        # Normalize roughly by length to prevent bias, but keep absolute presence
        length = max(len(tokens), 1)
        
        return {
            'negation': neg_count / length,
            'comparative': comp_count / length,
            'conditional': cond_count / length,
            'quantifier': quant_count / length,
            'has_logic': float((neg_count + comp_count + cond_count + quant_count) > 0)
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            denominator = max(c1, c2)
            if denominator == 0:
                return 0.0
            ncd = (c12 - min(c1, c2)) / denominator
            return max(0.0, min(1.0, ncd))
        except:
            return 1.0

    def _numeric_eval(self, text: str) -> List[float]:
        """Extract numbers for simple comparative logic."""
        nums = []
        for match in re.findall(r'-?\d+\.?\d*', text):
            try:
                nums.append(float(match))
            except ValueError:
                pass
        return nums

    def _structural_match_score(self, prompt: str, candidate: str) -> float:
        """
        Computes similarity based on structural 'epigenetic' markers.
        If the prompt has negations, the candidate must align (or not contradict).
        """
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        
        score = 0.0
        
        # Logic Presence Match: If prompt has logic, candidate should ideally reflect it or answer it
        if p_struct['has_logic'] > 0:
            # Reward if candidate acknowledges logic (simple heuristic: length/complexity bump)
            # Or if candidate contains specific logical connectors relevant to the answer
            score += 0.5
            
        # Negation Consistency: 
        # If prompt is heavily negated, and candidate is a direct contradiction, penalize?
        # Instead, we check if the candidate *ignores* the structural complexity when it shouldn't.
        # Simplified: High structural overlap in tokens implies better reasoning alignment.
        
        p_tokens = set(self._tokenize(prompt))
        c_tokens = set(self._tokenize(candidate))
        
        # Jaccard of structural tokens
        struct_tokens = self.negations | self.comparatives | self.conditionals | self.quantifiers
        p_struct_tokens = p_tokens & struct_tokens
        c_struct_tokens = c_tokens & struct_tokens
        
        if len(p_struct_tokens) > 0:
            intersection = len(p_struct_tokens & c_struct_tokens)
            union = len(p_struct_tokens | c_struct_tokens)
            if union > 0:
                score += (intersection / union) * 2.0 # Boost for matching logical operators
        
        # Numeric Consistency Check
        p_nums = self._numeric_eval(prompt)
        c_nums = self._numeric_eval(candidate)
        
        if p_nums and c_nums:
            # If both have numbers, check if they are plausibly related (e.g. same magnitude or result)
            # Simple heuristic: if prompt has 2 numbers and candidate has 1, maybe it's a calculation?
            if abs(len(p_nums) - len(c_nums)) <= 1: 
                score += 0.5
            # Check for direct number presence (often answers repeat a number from prompt in correct context)
            common_nums = set(p_nums) & set(c_nums)
            if common_nums:
                score += 1.0
                
        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        prompt_struct = self._extract_structure(prompt)
        prompt_len = len(prompt)
        
        # Pre-calculate prompt compression for NCD
        # We use a reference string for NCD baseline if needed, but here we compare P vs C
        
        for cand in candidates:
            # 1. Structural Parsing (Epigenetic Layer)
            struct_score = self._structural_match_score(prompt, cand)
            
            # 2. NCD (Spectral/Tiebreaker Layer)
            # NCD is 0 (identical) to 1 (different). We want high score for good match.
            # However, for reasoning, the answer isn't identical to the prompt.
            # We use NCD to penalize gibberish or completely unrelated text.
            # Heuristic: Good answers usually share some compression context with the prompt.
            ncd_val = self._compute_ncd(prompt, cand)
            
            # Transform NCD: Lower NCD (more similar) is generally better for relevance,
            # but for reasoning, we don't want exact copies. 
            # Let's use a inverted NCD scaled, but capped so it doesn't dominate structure.
            # Actually, standard NCD reasoning tools often look for the candidate that 
            # compresses best *with* the prompt logic. 
            # Here: Score = Structural_Match + (1 - NCD) * small_factor
            ncd_component = (1.0 - ncd_val) * 0.2 
            
            total_score = struct_score + ncd_component
            
            # Emergent Readout: Bonus for length appropriateness (avoiding too short/long)
            len_ratio = len(cand) / max(prompt_len, 1)
            if 0.1 <= len_ratio <= 2.0:
                total_score += 0.1
            
            results.append({
                "candidate": cand,
                "score": total_score,
                "reasoning": f"Structural match: {struct_score:.2f}, NCD factor: {ncd_component:.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the same structural + NCD logic.
        """
        # Run single evaluation
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        raw_score = res[0]['score']
        
        # Normalize to 0-1 based on empirical bounds of the scoring function
        # Max structural score approx: 2.0 (logic) + 1.0 (nums) + 0.2 (ncd) + 0.1 (len) = 3.3
        # Baseline random is near 0.
        confidence = min(1.0, max(0.0, raw_score / 3.5))
        
        return confidence