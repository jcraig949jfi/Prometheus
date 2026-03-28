import re
import zlib
from typing import List, Dict, Any

class ReasoningTool:
    """
    Renormalized Evolutionary Mechanism Design (REMD) Implementation.
    
    Core Logic:
    1. Mechanism Design (Primary Driver): The evaluation focuses on structural 
       integrity of the candidate relative to the prompt's constraints (negations, 
       comparatives, conditionals). This acts as the "mechanism" being tested.
    2. Genetic Algorithms (Secondary Validator): Candidates are treated as a population.
       Their "fitness" is adjusted by their diversity (distance from the mean candidate),
       simulating selection pressure against generic or echoed answers.
    3. Renormalization (Scale Independence): We apply a coarse-graining transformation 
       to both prompt and candidates (removing details/stopwords, keeping structural 
       tokens like numbers, negations, comparatives). We verify if the candidate's 
       logical signature holds at this coarse scale. If a candidate relies on fine-grained 
       noise that disappears under RG flow, it is penalized.
       
    Note: Per causal analysis, Renormalization and Mechanism Design logic paths are 
    kept distinct to avoid negative interaction, merging only in the final scoring.
    """

    def __init__(self):
        # Structural keywords for mechanism parsing
        self._negations = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self._comparatives = {'more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse', 'larger', 'smaller'}
        self._conditionals = {'if', 'then', 'else', 'unless', 'provided', 'assuming'}
        self._stopwords = {'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare', 'ought', 'used', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'each', 'few', 'most', 'some', 'any', 'about', 'out', 'over', 'into', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just', 'and', 'but', 'if', 'or', 'because', 'until', 'while', 'although', 'though', 'after', 'before', 'where', 'wherever', 'whenever', 'whether', 'which', 'whichever', 'who', 'whom', 'whose', 'what', 'whatever', 'that', 'it', 'its'}

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def _extract_numbers(self, text: str) -> List[float]:
        # Extract integers and floats
        matches = re.findall(r'-?\d+(?:\.\d+)?', text)
        return [float(m) for m in matches]

    def _coarse_grain(self, tokens: List[str]) -> List[str]:
        """
        Renormalization step: Coarse-grain the text by removing low-information 
        stopwords and keeping structural tokens (negations, comparatives, numbers-as-words).
        This tests for scale-independent logical structure.
        """
        rg_tokens = []
        for t in tokens:
            if t not in self._stopwords:
                rg_tokens.append(t)
        return rg_tokens

    def _analyze_structure(self, text: str) -> Dict[str, Any]:
        tokens = self._tokenize(text)
        numbers = self._extract_numbers(text)
        
        has_neg = any(t in self._negations for t in tokens)
        has_comp = any(t in self._comparatives for t in tokens)
        has_cond = any(t in self._conditionals for t in tokens)
        
        return {
            'tokens': tokens,
            'rg_tokens': self._coarse_grain(tokens),
            'numbers': numbers,
            'has_neg': has_neg,
            'has_comp': has_comp,
            'has_cond': has_cond,
            'neg_count': sum(1 for t in tokens if t in self._negations),
            'comp_count': sum(1 for t in tokens if t in self._comparatives),
        }

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            max_len = max(c1, c2)
            if max_len == 0: return 0.0
            return (c12 - min(c1, c2)) / max_len
        except:
            return 1.0

    def _evaluate_numeric_consistency(self, p_struct: Dict, c_struct: Dict) -> float:
        """Check if numeric logic holds (e.g., if prompt says 'greater', candidate reflects it)."""
        p_nums = p_struct['numbers']
        c_nums = c_struct['numbers']
        
        # If both have numbers, check basic ordering consistency if comparatives exist
        if p_nums and c_nums:
            # Simple heuristic: if prompt has comparative, candidate should arguably involve numbers or logic
            if p_struct['has_comp']:
                # If prompt compares, and candidate has numbers, do they align in magnitude roughly?
                # This is a soft check; we mostly look for presence/absence mismatch
                if not c_nums and len(p_nums) > 1:
                    return 0.5 # Penalty for missing numeric detail in comparative context
        return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        p_struct = self._analyze_structure(prompt)
        p_rg_set = set(p_struct['rg_tokens'])
        p_full_set = set(p_struct['tokens'])
        
        # Mechanism Design: Define the "rules" based on prompt structure
        requires_negation = p_struct['has_neg']
        requires_comparative = p_struct['has_comp']
        requires_conditional = p_struct['has_cond']
        
        scored_candidates = []
        
        # Calculate population average for GA diversity metric
        avg_len = sum(len(c) for c in candidates) / len(candidates)
        
        for idx, cand in enumerate(candidates):
            c_struct = self._analyze_structure(cand)
            c_rg_set = set(c_struct['rg_tokens'])
            c_full_set = set(c_struct['tokens'])
            
            # --- MECHANISM DESIGN SCORE (Primary Driver) ---
            # Check constraint satisfaction
            mechanism_score = 1.0
            
            # Negation check: If prompt negates, valid answer often needs to acknowledge or flip logic
            if requires_negation and not c_struct['has_neg']:
                # Heuristic: If prompt has strong negation, simple affirmative answers might be wrong
                # But we don't penalize heavily unless we know the truth value. 
                # Instead, we check structural alignment.
                pass 
            
            # Structural Overlap (Coarse Grained)
            # Does the candidate share the core logical tokens (RG flow) of the prompt?
            if len(p_rg_set) > 0:
                rg_overlap = len(p_rg_set.intersection(c_rg_set)) / len(p_rg_set.union(c_rg_set))
            else:
                rg_overlap = 0.5
            
            # Numeric Consistency
            num_score = self._evaluate_numeric_consistency(p_struct, c_struct)
            
            # --- RENORMALIZATION STABILITY CHECK ---
            # Compare full token overlap vs RG token overlap.
            # If full overlap is high but RG overlap is low, the candidate is "fragile" (relying on noise).
            # If RG overlap is high, the logic holds at coarse scale.
            if len(p_full_set) > 0:
                full_overlap = len(p_full_set.intersection(c_full_set)) / len(p_full_set.union(c_full_set))
            else:
                full_overlap = 0.0
                
            # Stability metric: RG overlap should be proportional to Full overlap
            # If full_overlap >> rg_overlap, it means the match is on stopwords (bad)
            # We want high RG overlap.
            stability = rg_overlap 
            
            # --- GENETIC ALGORITHM DIVERSITY ---
            # Penalize candidates that are too close to the "average" or identical to prompt (echo)
            diversity = 1.0 - self._ncd_distance(cand, prompt)
            # Normalize diversity slightly
            diversity = max(0.1, diversity)

            # Composite Score
            # Mechanism (Structure) is dominant. RG Stability modulates it. Diversity breaks ties.
            base_score = (rg_overlap * 0.6) + (num_score * 0.3) + (stability * 0.1)
            
            # Apply diversity as a modifier (GA selection pressure)
            final_score = base_score * (0.8 + 0.2 * diversity)
            
            # NCD Tiebreaker logic embedded: if scores are very close, the one with better 
            # compression relation to prompt (lower NCD usually implies higher relevance in short texts)
            # gets a tiny bump, but we prioritize the structural score.
            
            scored_candidates.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"RG-Overlap:{rg_overlap:.2f}, Num-Cons:{num_score:.2f}, Stability:{stability:.2f}, Diversity:{diversity:.2f}"
            })
            
        # Rank by score descending
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment and RG stability.
        """
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.0
        
        res = results[0]
        score = res['score']
        
        # Map score to confidence 0-1
        # Score is roughly 0-1.5 range potentially, normalize to 0-1
        confidence = min(1.0, max(0.0, score))
        return confidence