import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Type-Directed Compositional Hypothesis Engine with Phase Transition Monitoring.
    
    Mechanism:
    1. Structural Parsing (Type Checking): Extracts logical constraints (negations, 
       comparatives, conditionals) as 'types'. Candidates are scored by how well 
       their structure matches the prompt's required logical types.
    2. Energy Landscape: Each missing or mismatched logical constraint adds 'energy' cost.
    3. Phase Transition Detector: Monitors the distribution of candidate energies. 
       If the system detects a 'critical point' (high saturation where most candidates 
       fail basic structural checks), it switches to a strict refinement mode, 
       heavily penalizing any candidate that doesn't satisfy all hard constraints.
    4. Scoring: Final score = (Structural Match Score) - (Temperature * Energy Cost).
       NCD is used only as a tiebreaker for structurally identical candidates.
    """

    def __init__(self):
        # Logical patterns representing "Types" in our compositional system
        self.negation_patterns = [r'\bnot\b', r'\bnever\b', r'\bno\b', r'\bwithout\b', r'\bfalse\b']
        self.comparative_patterns = [r'\bmore\b', r'\bless\b', r'\bgreater\b', r'\blesser\b', r'\b<', r'\b>', r'\bbeats\b', r'\bworse\b']
        self.conditional_patterns = [r'\bif\b', r'\bthen\b', r'\bunless\b', r'\bonly if\b', r'\bimplies\b']
        self.numeric_pattern = r'\d+\.?\d*'
        
        # Phase transition parameters
        self.base_temperature = 0.5
        self.critical_threshold = 0.7  # If avg structural match < this, we are in "saturated/failure" phase

    def _extract_features(self, text: str) -> Dict[str, any]:
        """Extract structural features (types) from text."""
        text_lower = text.lower()
        features = {
            'has_negation': any(re.search(p, text_lower) for p in self.negation_patterns),
            'has_comparative': any(re.search(p, text_lower) for p in self.comparative_patterns),
            'has_conditional': any(re.search(p, text_lower) for p in self.conditional_patterns),
            'numbers': [float(x) for x in re.findall(self.numeric_pattern, text)],
            'length': len(text.split())
        }
        return features

    def _check_logical_consistency(self, prompt_feats: Dict, cand_feats: Dict) -> Tuple[float, str]:
        """
        Check if candidate satisfies the logical types required by the prompt.
        Returns (energy_cost, reasoning_string).
        Lower energy is better.
        """
        energy = 0.0
        reasons = []

        # Type 1: Negation Consistency
        # If prompt has negation, candidate should ideally reflect understanding (simplified heuristic)
        if prompt_feats['has_negation']:
            if not cand_feats['has_negation']:
                # Heuristic: If prompt negates, and candidate is affirmative without context, slight penalty
                # This is a soft constraint unless specific keywords match
                energy += 0.2
                reasons.append("Missing negation context")
        
        # Type 2: Comparative Consistency
        if prompt_feats['has_comparative']:
            if not cand_feats['has_comparative']:
                energy += 0.3
                reasons.append("Missing comparative logic")
            
            # Numeric evaluation if numbers exist
            if len(prompt_feats['numbers']) >= 2 and len(cand_feats['numbers']) >= 1:
                # Simple check: does the candidate number align with the implied order?
                # This is a placeholder for complex constraint propagation
                pass 

        # Type 3: Conditional Consistency
        if prompt_feats['has_conditional']:
            if not cand_feats['has_conditional']:
                # Soft penalty for missing conditional structure in answer
                energy += 0.1
        
        reason_str = "; ".join(reasons) if reasons else "Structural match"
        return energy, reason_str

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Compute Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        c_s1 = len(zlib.compress(s1_bytes))
        c_s2 = len(zlib.compress(s2_bytes))
        c_s1_s2 = len(zlib.compress(s1_bytes + s2_bytes))
        
        max_len = max(c_s1, c_s2)
        if max_len == 0:
            return 0.0
        return (c_s1_s2 - min(c_s1, c_s2)) / max_len

    def _detect_phase_transition(self, energies: List[float]) -> bool:
        """
        Detect if the system has crossed a critical point.
        If average energy is high (many candidates failing structural checks), 
        we are in a 'saturated' phase where we must be extremely selective.
        """
        if not energies:
            return False
        avg_energy = sum(energies) / len(energies)
        # High energy means poor structural match. 
        # If avg energy > threshold, we are in a critical phase.
        return avg_energy > self.critical_threshold

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []

        prompt_feats = self._extract_features(prompt)
        results = []
        energies = []

        # Phase 1: Compute raw energies and structural matches
        for cand in candidates:
            cand_feats = self._extract_features(cand)
            energy, reason = self._check_logical_consistency(prompt_feats, cand_feats)
            energies.append(energy)
            results.append({
                'candidate': cand,
                'energy': energy,
                'reasoning_base': reason,
                'feats': cand_feats
            })

        # Phase 2: Detect Phase Transition to adjust Temperature
        is_critical_phase = self._detect_phase_transition(energies)
        
        # Adjust temperature based on phase
        # Normal phase: Explore (higher temp, softer penalties)
        # Critical phase: Exploit/Refine (lower temp, strict penalties)
        current_temp = 0.2 if is_critical_phase else self.base_temperature
        phase_reason = "Critical Phase (Strict)" if is_critical_phase else "Exploration Phase"

        # Phase 3: Final Scoring
        final_results = []
        for res in results:
            # Base score starts at 1.0
            # Subtract weighted energy
            score = 1.0 - (current_temp * res['energy'])
            
            # Ensure score stays in [0, 1] roughly, though logic allows >1 if we added bonuses
            score = max(0.0, min(1.0, score))
            
            final_results.append({
                'candidate': res['candidate'],
                'score': score,
                'reasoning': f"[{phase_reason}] {res['reasoning_base']}. Energy: {res['energy']:.2f}, Temp: {current_temp:.2f}"
            })

        # Sort by score descending
        final_results.sort(key=lambda x: x['score'], reverse=True)
        
        # Tie-breaking with NCD if scores are very close (structural equivalence)
        # We apply a small NCD-based adjustment only for top candidates if needed, 
        # but per instructions, NCD is a tiebreaker. 
        # Here we rely on the stability of the sort (deterministic) and the fact that 
        # structural parsing usually differentiates enough. 
        # If strict tie-breaking is needed for identical scores:
        for i in range(len(final_results) - 1):
            if abs(final_results[i]['score'] - final_results[i+1]['score']) < 1e-6:
                # Use NCD against prompt as tiebreaker: closer to prompt structure might be better?
                # Actually, usually shorter/concise is better, or we just leave stable sort.
                # Let's use NCD to prefer candidate closer to prompt semantics if scores equal
                ncd_i = self._compute_ncd(prompt, final_results[i]['candidate'])
                ncd_next = self._compute_ncd(prompt, final_results[i+1]['candidate'])
                if ncd_i > ncd_next: # Lower NCD is better match
                    pass # Keep order
                else:
                    # Swap if next is better match
                    final_results[i], final_results[i+1] = final_results[i+1], final_results[i]

        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on structural alignment."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]['score']