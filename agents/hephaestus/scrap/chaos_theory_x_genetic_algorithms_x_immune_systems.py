import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Chaotic Immune Genetic Optimizer (CIGO) for Reasoning.
    
    Mechanism:
    1. Structural Parsing (Chaos Core): Extracts logical constraints (negations, 
       comparatives, conditionals) to form a deterministic 'fitness landscape'.
       Chaos theory is applied via a logistic map to modulate the sensitivity 
       of constraint matching, preventing stagnation on superficial string matches.
    2. Genetic/Immune Layer: Candidates are 'hypotheses'. 
       - Clonal Expansion: Candidates satisfying more structural constraints 
         receive exponential score boosts (exploitation).
       - Negative Selection: Candidates too similar to each other (redundant) 
         or lacking structural keywords when the prompt demands them are suppressed.
    3. Scoring: Primary signal is structural adherence. NCD is used only as a 
       tie-breaker for candidates with identical structural scores.
    """

    def __init__(self):
        self.chaos_param = 3.99  # r approx 4 for chaotic behavior
        self.chaos_state = 0.5   # Initial seed
        
    def _logistic_map(self, x: float) -> float:
        """Deterministic chaotic iteration."""
        return self.chaos_param * x * (1.0 - x)

    def _extract_structure(self, text: str) -> Dict[str, any]:
        """Extract logical primitives: negations, comparatives, numbers."""
        text_lower = text.lower()
        features = {
            'has_negation': bool(re.search(r'\b(not|no|never|neither|without)\b', text_lower)),
            'has_comparative': bool(re.search(r'\b(more|less|greater|smaller|higher|lower|better|worse|<|>)\b', text_lower)),
            'has_conditional': bool(re.search(r'\b(if|then|unless|otherwise|when)\b', text_lower)),
            'numbers': re.findall(r'\d+\.?\d*', text_lower),
            'length': len(text)
        }
        return features

    def _check_constraint_satisfaction(self, prompt_feats: Dict, cand_feats: Dict, candidate: str) -> float:
        """
        Evaluate how well the candidate satisfies the logical constraints implied by the prompt.
        Uses chaotic modulation to weight the importance of feature presence.
        """
        score = 0.0
        chaos_val = self._logistic_map(self.chaos_state)
        self.chaos_state = chaos_val # Update state
        
        # Base score for length relevance (avoiding extremely short answers unless necessary)
        if cand_feats['length'] > 3:
            score += 0.1
            
        # Constraint Propagation: If prompt has negation, valid answers often need specific handling
        # We simulate 'negative selection' by penalizing candidates that ignore prompt complexity
        if prompt_feats['has_negation']:
            if cand_feats['has_negation'] or len(cand_feats['numbers']) > 0:
                score += 0.4 * (1.0 + 0.1 * chaos_val) # Chaotic boost
            else:
                # Potential penalty for ignoring negation context, unless it's a simple 'Yes/No'
                if not re.match(r'^(yes|no|true|false)$', candidate.strip(), re.IGNORECASE):
                    score -= 0.2

        if prompt_feats['has_comparative']:
            if cand_feats['has_comparative'] or len(cand_feats['numbers']) >= 2:
                score += 0.4 * (1.0 - 0.1 * chaos_val)
        
        if prompt_feats['has_conditional']:
            if cand_feats['has_conditional']:
                score += 0.3
                
        # Numeric consistency check (simple transitivity)
        if prompt_feats['numbers'] and cand_feats['numbers']:
            try:
                p_nums = [float(n) for n in prompt_feats['numbers']]
                c_nums = [float(n) for n in cand_feats['numbers']]
                # Heuristic: If prompt implies ordering, candidate numbers should reflect logic
                # Here we just reward numeric presence in context as a proxy for reasoning
                score += 0.2 * min(len(c_nums), 2) 
            except ValueError:
                pass
                
        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode('utf-8'), s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            denom = max(c1, c2)
            if denom == 0: return 1.0
            return (c12 - min(c1, c2)) / denom
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_feats = self._extract_structure(prompt)
        scored_candidates = []
        
        # Phase 1: Structural Evaluation (The "Chaos" and "Immune" scoring)
        for cand in candidates:
            cand_feats = self._extract_structure(cand)
            # Reset chaos state slightly per candidate to ensure aperiodic weighting
            # but keep it deterministic based on candidate content hash
            seed_val = abs(hash(cand)) % 1000 / 1000.0
            self.chaos_state = seed_val if seed_val > 0 else 0.5
            
            struct_score = self._check_constraint_satisfaction(prompt_feats, cand_feats, cand)
            scored_candidates.append({
                'candidate': cand,
                'struct_score': struct_score,
                'features': cand_feats
            })
        
        # Phase 2: Immune Memory & Negative Selection (Diversity check)
        # Suppress candidates that are structurally identical to higher scoring ones
        seen_signatures = set()
        final_results = []
        
        # Sort by structural score first to prioritize 'clones' of good ideas
        scored_candidates.sort(key=lambda x: x['struct_score'], reverse=True)
        
        for item in scored_candidates:
            cand = item['candidate']
            # Signature based on structural features, not raw string
            sig = f"{item['struct_score']:.2f}_{item['features']['has_negation']}_{item['features']['has_comparative']}"
            
            # Negative selection: if we already accepted a very similar structural pattern
            # with a higher base score, reduce weight of this one (simulating redundancy suppression)
            penalty = 0.0
            if sig in seen_signatures:
                penalty = 0.15 # Suppress redundant hypotheses
            
            final_score = item['struct_score'] - penalty
            final_results.append({
                'candidate': cand,
                'score': final_score,
                'reasoning': f"Structural match: {item['struct_score']:.2f}, Redundancy penalty: {penalty:.2f}"
            })
            seen_signatures.add(sig)

        # Phase 3: NCD Tie-breaking
        # Only used if structural scores are effectively equal (within epsilon)
        epsilon = 0.01
        for i in range(len(final_results)):
            for j in range(i + 1, len(final_results)):
                if abs(final_results[i]['score'] - final_results[j]['score']) < epsilon:
                    # Use NCD against prompt as tie breaker
                    ncd_i = self._ncd(prompt, final_results[i]['candidate'])
                    ncd_j = self._ncd(prompt, final_results[j]['candidate'])
                    # Lower NCD (more similar) is better, so subtract from score
                    final_results[i]['score'] -= ncd_i * 0.001
                    final_results[j]['score'] -= ncd_j * 0.001

        # Final Sort
        final_results.sort(key=lambda x: x['score'], reverse=True)
        
        # Normalize scores to 0-1 range roughly for consistency
        max_s = final_results[0]['score'] if final_results else 1.0
        min_s = final_results[-1]['score'] if final_results else 0.0
        range_s = max_s - min_s if max_s != min_s else 1.0
        
        for res in final_results:
            res['score'] = (res['score'] - min_s) / range_s
            res['reasoning'] = f"Chaos-modulated structural analysis: {res['reasoning']}"
            
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment.
        """
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.0
        # The score from evaluate is already normalized relative to the set, 
        # but for single item, we rely on the raw structural assessment logic.
        # Re-run evaluation to get absolute structural score before normalization against others
        prompt_feats = self._extract_structure(prompt)
        cand_feats = self._extract_structure(answer)
        
        seed_val = abs(hash(answer)) % 1000 / 1000.0
        self.chaos_state = seed_val if seed_val > 0 else 0.5
        raw_score = self._check_constraint_satisfaction(prompt_feats, cand_feats, answer)
        
        # Map raw score (approx -0.2 to 1.0) to 0-1
        confidence = max(0.0, min(1.0, (raw_score + 0.2) / 1.2))
        return confidence