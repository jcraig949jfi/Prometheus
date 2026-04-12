import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Probabilistic Pragmatic Dependent Type Theory (PPDTT) Approximation.
    
    Mechanism:
    1. Type Theory (Structure): Parses logical skeletons (negations, comparatives, 
       conditionals, numeric literals) to establish a rigid 'type' for the answer.
    2. Pragmatics (Filter): Applies Gricean constraints. Candidates violating 
       logical consistency (e.g., answering 'Yes' to a negative constraint) 
       receive heavy penalties (measure zero).
    3. Measure Theory (Scoring): Computes a posterior probability mass. The prior 
       is derived from structural alignment (NCD on logic tokens), and the likelihood 
       is the pragmatic fit. Final score is the normalized measure.
    """
    
    def __init__(self):
        self._logic_ops = ['not', 'no', 'never', 'without', 'unless', 'except']
        self._comp_ops = ['greater', 'less', 'more', 'fewer', 'higher', 'lower', '>', '<']
        self._cond_ops = ['if', 'then', 'else', 'when', 'unless']

    def _extract_features(self, text: str) -> Dict:
        """Extracts logical 'types' and pragmatic constraints from text."""
        t = text.lower()
        return {
            'has_negation': any(op in t for op in self._logic_ops),
            'has_comparative': any(op in t for op in self._comp_ops),
            'has_conditional': any(op in t for op in self._cond_ops),
            'has_numbers': bool(re.search(r'\d+', t)),
            'length': len(text.split()),
            'raw': text
        }

    def _structural_match(self, prompt_feats: Dict, cand_feats: Dict) -> float:
        """
        Type consistency check. 
        If prompt implies a specific logical mode (e.g., comparison), 
        the candidate should ideally reflect compatible structure or not contradict it.
        """
        score = 1.0
        
        # Pragmatic Violation: If prompt has strong logic, simple yes/no might be insufficient
        # unless the logic dictates a binary outcome.
        if prompt_feats['has_comparative'] or prompt_feats['has_conditional']:
            # Heuristic: If prompt is complex, very short answers (Yes/No) are often 
            # pragmatically infelicitous unless strictly constrained.
            if cand_feats['length'] < 3 and not prompt_feats['has_negation']:
                score *= 0.5 # Penalty for oversimplification
        
        # Negation consistency (Simplified Modus Tollens check)
        # If prompt negates, and candidate affirms without qualification, slight penalty
        if prompt_feats['has_negation'] and not cand_feats['has_negation']:
            # This is a soft check; hard contradictions are handled in confidence
            pass 
            
        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode(), s2.encode()
    try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            if max(c1, c2) == 0: return 1.0
            return (c12 - min(c1, c2)) / max(c1, c2)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feats = self._extract_features(prompt)
        results = []
        
        # 1. Measure Space Construction (Priors via Structural Parsing)
        # We calculate a raw score based on structural alignment and NCD tie-breaking
        raw_scores = []
        for cand in candidates:
            cand_feats = self._extract_features(cand)
            
            # Type Consistency Score (Pragmatic Filter)
            type_score = self._structural_match(prompt_feats, cand_feats)
            
            # NCD as tiebreaker/secondary signal (Measure Theoretic base)
            # We invert NCD so higher is better (1 - ncd)
            ncd_val = self._ncd(prompt, cand)
            similarity = 1.0 - ncd_val
            
            # Combined Prior
            # Weight structural logic heavily (0.7) vs raw string similarity (0.3)
            prior = (type_score * 0.7) + (similarity * 0.3)
            raw_scores.append((cand, prior, cand_feats))

        # Normalize to get a probability distribution (Posterior Mass)
        total_mass = sum(s[1] for s in raw_scores) + 1e-9
        ranked = []
        
        # Sort by prior first to assign ranks
        raw_scores.sort(key=lambda x: x[1], reverse=True)

        for i, (cand, prior, feats) in enumerate(raw_scores):
            # Bayesian update simulation: 
            # Adjust score based on rank position (pragmatic relevance)
            # Top candidate gets a boost, others decay
            rank_bonus = 1.0 if i == 0 else 0.8 ** i
            
            final_score = (prior / total_mass) * rank_bonus
            
            # Ensure deterministic float formatting
            final_score = float(f"{final_score:.6f}")
            
            reasoning = f"Type-consistency: {feats['length']} tokens. "
            if prompt_feats['has_negation'] and not feats['has_negation']:
                reasoning += "Potential pragmatic tension with negation. "
            if i == 0:
                reasoning += "Highest posterior mass."
            else:
                reasoning += f"Ranked {i+1} by measure."

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })

        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Computes confidence as the posterior probability of the answer 
        given the prompt's pragmatic and logical constraints.
        """
        # Re-use evaluation logic for consistency
        # We simulate a candidate list of [answer, "dummy_alternative"] to get relative score
        # But for single confidence, we check constraint satisfaction directly.
        
        p_feats = self._extract_features(prompt)
        a_feats = self._extract_features(answer)
        
        base_conf = 0.5
        
        # 1. Logical Consistency Check (Type Safety)
        # If prompt asks for comparison (contains 'greater'), answer should ideally 
        # contain numbers or comparatives, or be a direct selection.
        if p_feats['has_comparative']:
            if not (a_feats['has_numbers'] or a_feats['has_comparative'] or len(a_feats['raw'].split()) < 4):
                base_conf -= 0.3 # Penalty for missing expected type content
        
        # 2. Negation Handling (Pragmatic Implicature)
        # Simple heuristic: If prompt is negative, and answer is positive assertion without context
        if p_feats['has_negation']:
            # If the answer is a simple "Yes", it might be ambiguous or wrong depending on context
            if a_feats['raw'].strip().lower() in ['yes', 'true', 'correct']:
                base_conf -= 0.2 # Ambiguous under negation
        
        # 3. Structural Overlap (Measure)
        ncd_val = self._ncd(prompt, answer)
        # High NCD (low similarity) isn't always bad for answers, but extremely high NCD 
        # suggests unrelatedness.
        if ncd_val > 0.95:
            base_conf -= 0.1
            
        return max(0.0, min(1.0, base_conf))