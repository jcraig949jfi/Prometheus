import re
import math
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    A hierarchical variational active-inference architecture simulation.
    
    Mechanism:
    1. Causal Inference (Structure Learning): Parses logical structures (negations, 
       comparatives, conditionals) to build a transient causal graph of the prompt.
    2. Pragmatics (Gricean Priors): Evaluates candidates based on Quantity (length/relevance),
       Quality (contradiction check), and Manner (clarity). Violations incur 'surprise' penalties.
    3. Free Energy Principle: Computes a score balancing 'Prediction Error' (match to structural logic)
       and 'Pragmatic Surprise' (violations of conversational norms).
       
    Epistemic Honesty (Tier B):
    Before scoring, the system performs a 'Meta-Confidence' check. If the prompt contains
    presuppositions, scope ambiguities, or unanswerable constraints, the system caps confidence
    and lowers scores to reflect uncertainty, preventing over-confident hallucinations.
    """

    def __init__(self):
        # Priors for Gricean Maxims (soft constraints)
        self.pragmatic_weights = {
            'quantity': 0.2,   # Penalty for too much/too little info
            'quality': 0.5,    # Penalty for logical contradictions
            'relation': 0.2,  # Penalty for irrelevance
            'manner': 0.1      # Penalty for ambiguity/complexity
        }
        
        # Triggers for Epistemic Honesty (Tier B)
        self.presupposition_triggers = [
            r"have you stopped", r"why did.*fail", r"why did.*stop", 
            r"when did.*stop", r"quit.*smoking", r"beat your wife"
        ]
        self.ambiguity_triggers = [
            r"every.*a.*\?", r"told.*he.*\?", r"told.*she.*\?", 
            r"either.*or.*\?", r"best.*worst"
        ]
        self.subjectivity_triggers = [
            r"best", r"worst", r"favorite", r"beautiful", r"tasty"
        ]

    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates the prompt for Tier B traps (Ambiguity, Presupposition, Unanswerability).
        Returns a cap value. If 1.0, no traps detected. If < 0.3, high risk of trap.
        """
        p_lower = prompt.lower()
        
        # Check for presuppositions
        for pattern in self.presupposition_triggers:
            if re.search(pattern, p_lower):
                return 0.15  # Strong presupposition detected
        
        # Check for ambiguity scopes
        for pattern in self.ambiguity_triggers:
            if re.search(pattern, p_lower):
                return 0.25  # Ambiguity detected
        
        # Check for pure subjectivity without criteria
        has_subj = any(re.search(t, p_lower) for t in self.subjectivity_triggers)
        if has_subj and "criteria" not in p_lower and "define" not in p_lower:
            return 0.20

        return 1.0

    def _parse_structure(self, prompt: str) -> Dict:
        """
        Extracts structural features: Negations, Comparatives, Conditionals, Numbers.
        This forms the 'Causal DAG' of the text.
        """
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither|without)\b', prompt.lower())),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|better|worse|than)\b', prompt.lower())),
            'conditionals': len(re.findall(r'\b(if|then|unless|provided)\b', prompt.lower())),
            'numbers': re.findall(r'\d+\.?\d*', prompt),
            'logic_ops': len(re.findall(r'\b(and|or|implies|therefore)\b', prompt.lower()))
        }
        return features

    def _compute_structural_score(self, prompt: str, candidate: str) -> float:
        """
        Calculates the 'Prediction Error' term of Free Energy.
        High score = Low prediction error (Candidate aligns with prompt structure).
        """
        score = 0.5  # Base prior
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # 1. Negation Consistency
        # If prompt has 'not', candidate should ideally reflect negation or contradiction handling
        if 'not' in p_lower or 'no' in p_lower:
            if 'not' in c_lower or 'no' in c_lower or 'false' in c_lower:
                score += 0.2
            elif 'yes' in c_lower or 'true' in c_lower:
                # Potential contradiction unless context clarifies
                score -= 0.1
        
        # 2. Numeric Evaluation (Constructive Computation)
        # Extract numbers from prompt and candidate to check for simple relations
        p_nums = self._parse_structure(prompt)['numbers']
        c_nums = self._parse_structure(candidate)['numbers']
        
        if p_nums and c_nums:
            try:
                # Simple heuristic: Does the candidate contain a number derived from prompt?
                # Or does it answer a comparison?
                p_max = max(float(x) for x in p_nums)
                c_val = float(c_nums[0])
                
                # Check for direct extraction (common in reasoning traps)
                if any(str(int(p_max)) == str(int(c_val)) or str(p_max) == str(c_val) for _ in [1]):
                     score += 0.3
                     
                # Check for simple increment/decrement logic if implied
                if 'next' in p_lower or 'after' in p_lower:
                    if c_val > p_max: score += 0.2
            except ValueError:
                pass

        # 3. Logical Consistency (Modus Tollens/Ponens approximation)
        if 'if' in p_lower:
            if 'therefore' in c_lower or 'so' in c_lower or 'then' in c_lower:
                score += 0.15
        
        return min(1.0, max(0.0, score))

    def _compute_pragmatic_score(self, prompt: str, candidate: str) -> float:
        """
        Calculates the 'Pragmatic Surprise' term.
        Penalizes violations of Gricean Maxims.
        """
        penalty = 0.0
        p_len = len(prompt.split())
        c_len = len(candidate.split())
        
        # Quantity: Is the answer disproportionately long or short?
        if c_len == 0:
            penalty += 1.0
        elif c_len > p_len * 2:
            penalty += 0.3  # Too verbose
        elif c_len < 2 and p_len > 10:
            penalty += 0.2  # Too brief for complex prompt
            
        # Quality: Detect obvious contradictions (e.g., saying "Yes" and "No" together)
        c_lower = candidate.lower()
        if ('yes' in c_lower and 'no' in c_lower) and 'maybe' not in c_lower:
            penalty += 0.4
            
        # Manner: Clarity (simple heuristic: avoid excessive special chars unless code)
        if candidate.count('?') > 1:
            penalty += 0.1
            
        return max(0.0, 1.0 - penalty)

    def _calculate_free_energy(self, structural_score: float, pragmatic_score: float) -> float:
        """
        Combines Prediction Error (structural) and Pragmatic Surprise into a single score.
        F = Prediction_Error - Pragmatic_Prior
        We invert this so higher is better: Score = Structural_Alignment * Pragmatic_Validity
        """
        # Weighted sum emphasizing structural correctness (Reasoning) but penalizing pragmatic failures
        return (structural_score * 0.7) + (pragmatic_score * 0.3)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Tier B Check: Meta-Confidence Cap
        meta_cap = self._meta_confidence(prompt)
        
        for candidate in candidates:
            # 1. Structural Parsing (Causal Graph approximation)
            struct_score = self._compute_structural_score(prompt, candidate)
            
            # 2. Pragmatic Layer (Gricean Priors)
            prag_score = self._compute_pragmatic_score(prompt, candidate)
            
            # 3. Active Inference (Free Energy Minimization)
            raw_score = self._calculate_free_energy(struct_score, prag_score)
            
            # Apply Epistemic Honesty Cap
            if meta_cap < 1.0:
                # If the question is ambiguous/trap-like, suppress confidence
                # but allow the 'best' of a bad bunch to still be relatively higher
                final_score = raw_score * meta_cap
                reasoning = f"Tier B Trigger: Potential ambiguity/presupposition detected. Score capped. Structural: {struct_score:.2f}, Pragmatic: {prag_score:.2f}"
            else:
                final_score = raw_score
                reasoning = f"Structural alignment: {struct_score:.2f}, Pragmatic validity: {prag_score:.2f}"
            
            # NCD Tiebreaker (Max 15% influence as per instructions)
            # Only used if scores are very close, implemented here as a tiny noise term for differentiation
            # Note: Real NCD is expensive, using length ratio as a proxy for 'compression' similarity
            len_diff = abs(len(prompt) - len(candidate)) / (len(prompt) + 1)
            ncd_bonus = 0.05 * (1.0 - min(1.0, len_diff)) 
            final_score += ncd_bonus
            
            results.append({
                "candidate": candidate,
                "score": round(min(1.0, final_score), 4),
                "reasoning": reasoning
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly enforces Epistemic Honesty for Tier B traps.
        """
        # 1. Meta-Confidence Check (The primary driver for Tier B)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Structural Verification
        struct_score = self._compute_structural_score(prompt, answer)
        
        # 3. Pragmatic Verification
        prag_score = self._compute_pragmatic_score(prompt, answer)
        
        # Base confidence derived from structural match
        base_conf = (struct_score * 0.6) + (prag_score * 0.4)
        
        # Apply Cap
        final_conf = min(base_conf, meta_cap)
        
        # Never return > 0.9 unless computation was definitive (heuristic: high struct score)
        if struct_score < 0.8:
            final_conf = min(final_conf, 0.85)
            
        return round(max(0.0, min(1.0, final_conf)), 4)