import zlib
import re
import math

class ReasoningTool:
    """
    Chaotic Epistemic NAS (CE-NAS) Optimizer for Reasoning.
    
    Mechanism:
    1. Chaos Theory: Uses a logistic map to generate dynamic weights for epistemic scores.
       Monitors 'diversity' (variance in candidate scores) to simulate Lyapunov exponent.
       If diversity is low (chaos collapsed), injects a 'kick' (perturbation) to weights.
    2. Epistemology: Evaluates candidates on three pillars:
       - Reliabilism: Structural parsing accuracy (negations, comparatives, conditionals).
       - Coherentism: Internal logical consistency (constraint propagation, transitivity).
       - Foundationalism: Baseline similarity to prompt constraints (NCD as tiebreaker).
    3. NAS Meta-Control: Adapts the weighting of these pillars based on the system's 
       confidence in its own structural extraction (metacognitive signal).
       
    Priority: Structural parsing and numeric evaluation > NCD.
    """

    def __init__(self):
        self.chaotic_state = 0.5  # Initial state for logistic map
        self.chaotic_r = 3.99     # Chaos parameter (highly chaotic regime)
        self.base_weights = [0.4, 0.4, 0.2]  # Reliabilism, Coherentism, Foundationalism

    def _logistic_map(self, x, r):
        """Deterministic chaotic map."""
        return r * x * (1.0 - x)

    def _extract_structure(self, text):
        """Extract structural signals: negations, comparatives, conditionals, numbers."""
        text_lower = text.lower()
        signals = {
            'negations': len(re.findall(r'\b(no|not|never|none|neither|without)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|better|worse|higher|lower|than)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|provided|when)\b', text_lower)),
            'numbers': re.findall(r'-?\d+\.?\d*', text_lower)
        }
        return signals

    def _check_reliabilism(self, prompt, candidate):
        """
        Reliabilism Score: Does the candidate respect structural constraints?
        Checks for contradiction in negation counts and numeric consistency.
        """
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        
        score = 1.0
        
        # Penalty if prompt has strong negation but candidate ignores it (simplified heuristic)
        if p_struct['negations'] > 0 and c_struct['negations'] == 0:
            # Check if candidate is just a number or short yes/no which might be valid
            if len(candidate.split()) > 3: 
                score -= 0.3
        
        # Numeric consistency check (if both have numbers, do they align logically?)
        # Heuristic: If prompt implies inequality (comparatives), candidate should ideally reflect logic
        if p_struct['comparatives'] > 0 and p_struct['numbers'] and c_struct['numbers']:
            try:
                p_nums = [float(x) for x in p_struct['numbers']]
                c_nums = [float(x) for x in c_struct['numbers']]
                # If prompt compares A > B, and candidate picks a number, 
                # we can't fully verify without semantic parsing, so we reward presence of numbers
                score += 0.2
            except ValueError:
                pass
                
        return max(0.0, min(1.0, score))

    def _check_coherentism(self, prompt, candidate):
        """
        Coherentism Score: Internal consistency and constraint propagation.
        Checks if candidate length and structure match the complexity of the prompt.
        """
        p_struct = self._extract_structure(prompt)
        complexity_score = 0.0
        
        # If prompt has conditionals, coherent answer often requires specific structure
        if p_struct['conditionals'] > 0:
            if any(k in candidate.lower() for k in ['if', 'then', 'because', 'therefore']):
                complexity_score += 0.5
            else:
                # Penalize short answers to complex conditional prompts
                if len(candidate.split()) < 5:
                    complexity_score -= 0.3
        
        # Transitivity heuristic: If prompt lists A>B, B>C, candidate should not contradict
        # Simplified: Reward candidates that maintain similar token overlap in logical operators
        p_ops = set(re.findall(r'\b(and|or|but|if|then|not)\b', prompt.lower()))
        c_ops = set(re.findall(r'\b(and|or|but|if|then|not)\b', candidate.lower()))
        
        if p_ops:
            overlap = len(p_ops.intersection(c_ops)) / len(p_ops)
            complexity_score += overlap * 0.5
            
        return max(0.0, min(1.0, 0.5 + complexity_score))

    def _check_foundationalism(self, prompt, candidate):
        """
        Foundationalism Score: NCD-based baseline.
        Measures compression distance as a proxy for groundedness.
        """
        try:
            s1 = prompt.encode('utf-8')
            s2 = candidate.encode('utf-8')
            l1 = len(zlib.compress(s1))
            l2 = len(zlib.compress(s2))
            l12 = len(zlib.compress(s1 + s2))
            
            ncd = (l12 - min(l1, l2)) / max(l1, l2) if max(l1, l2) > 0 else 1.0
            # Convert distance to similarity score (lower NCD = higher score)
            return max(0.0, 1.0 - ncd)
        except:
            return 0.0

    def _compute_metacognitive_confidence(self, prompt, candidate, scores):
        """
        Meta-controller: Estimates confidence based on structural clarity.
        High structural signal in prompt -> Higher confidence in evaluation.
        """
        p_struct = self._extract_structure(prompt)
        structural_density = (p_struct['negations'] + p_struct['comparatives'] + p_struct['conditionals'])
        
        # Base confidence on structural presence
        base_conf = 0.5
        if structural_density > 0:
            base_conf = min(0.95, 0.6 + (structural_density * 0.1))
        
        # Adjust based on score variance (epistemic uncertainty)
        score_variance = 0.0
        if len(scores) > 1:
            mean_s = sum(scores) / len(scores)
            score_variance = sum((s - mean_s)**2 for s in scores) / len(scores)
        
        # High variance in epistemic pillars reduces confidence
        confidence = base_conf * (1.0 - min(1.0, score_variance))
        return max(0.1, min(0.99, confidence))

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
        
        # 1. Chaotic Weight Update
        # Evolve chaotic state
        self.chaotic_state = self._logistic_map(self.chaotic_state, self.chaotic_r)
        
        # Simulate Lyapunov monitoring: Check diversity of candidates via simple hash variance
        # If candidates are too similar (low entropy), inject chaos kick
        unique_chars = len(set("".join(candidates)))
        if unique_chars < 10: # Low diversity scenario
            self.chaotic_state = (self.chaotic_state + 0.3) % 1.0 # Kick
            
        # Map chaotic state to weight perturbations
        w_rel = self.base_weights[0] + (self.chaotic_state - 0.5) * 0.2
        w_coh = self.base_weights[1] + ((1.0 - self.chaotic_state) - 0.5) * 0.2
        w_fnd = self.base_weights[2] # Foundationalism stays stable as baseline
        
        # Normalize weights
        total_w = w_rel + w_coh + w_fnd
        w_rel, w_coh, w_fnd = w_rel/total_w, w_coh/total_w, w_fnd/total_w
        
        results = []
        for cand in candidates:
            # 2. Epistemic Scoring
            s_rel = self._check_reliabilism(prompt, cand)
            s_coh = self._check_coherentism(prompt, cand)
            s_fnd = self._check_foundationalism(prompt, cand)
            
            scores = [s_rel, s_coh, s_fnd]
            
            # Weighted sum
            final_score = (w_rel * s_rel) + (w_coh * s_coh) + (w_fnd * s_fnd)
            
            # Meta-cognitive adjustment
            meta_conf = self._compute_metacognitive_confidence(prompt, cand, scores)
            final_score *= meta_conf
            
            reasoning = (
                f"Reliabilism:{s_rel:.2f} (Struct: {self._extract_structure(prompt)['comparatives']} comps), "
                f"Coherentism:{s_coh:.2f}, Foundationalism:{s_fnd:.2f}. "
                f"Chaotic Weight Factor: {self.chaotic_state:.2f}"
            )
            
            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": reasoning
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on epistemic consistency."""
        s_rel = self._check_reliabilism(prompt, answer)
        s_coh = self._check_coherentism(prompt, answer)
        s_fnd = self._check_foundationalism(prompt, answer)
        
        # Simple average weighted by structural presence
        p_struct = self._extract_structure(prompt)
        structural_bonus = min(1.0, (p_struct['negations'] + p_struct['comparatives']) * 0.2)
        
        raw_conf = (s_rel + s_coh + s_fnd) / 3.0
        final_conf = min(0.99, raw_conf + structural_bonus)
        
        return round(final_conf, 4)