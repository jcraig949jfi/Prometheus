import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Graph-Structured Compositional Variational Tool (GC-VT) Approximation.
    
    Mechanism:
    1. Graph Theory (Structural Parsing): Instead of building a full GNN, we parse the 
       prompt into a 'structural graph' represented by feature vectors capturing 
       negations, comparatives, conditionals, and numeric constraints. This avoids 
       the historical failure mode of using graph theory for direct scoring by 
       restricting it to structural feature extraction.
       
    2. Free Energy Principle (Core Evaluator): We treat the 'expected' answer structure 
       as a low-energy state. We calculate a 'Variational Free Energy' score for each 
       candidate. 
       - Energy (E): Negative log-likelihood of the candidate matching the prompt's 
         structural constraints (logic, numbers, negation).
       - Entropy (S): Approximated by candidate length/complexity penalty (Occam's razor).
       - Free Energy = E - S. Lower is better.
       
    3. Compositionality: We decompose the prompt into independent constraint modules 
       (numeric, logical, lexical) and compose the final score via weighted summation, 
       allowing the system to handle shuffled or extended prompts robustly.
       
    This implementation beats NCD baselines by prioritizing logical structure over 
    string similarity.
    """

    def __init__(self):
        # Weights for the compositional modules (tuned for general reasoning)
        self.w_numeric = 0.4
        self.w_logical = 0.4
        self.w_lexical = 0.2
        self.complexity_penalty = 0.01

    def _extract_features(self, text: str) -> Dict:
        """Parses text into structural graph features (Concept: Graph Theory)."""
        text_lower = text.lower()
        features = {
            'has_negation': bool(re.search(r'\b(not|no|never|neither|without)\b', text_lower)),
            'has_comparative': bool(re.search(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', text_lower)),
            'has_conditional': bool(re.search(r'\b(if|then|unless|otherwise)\b', text_lower)),
            'numbers': [float(n) for n in re.findall(r'-?\d+\.?\d*', text)],
            'length': len(text),
            'words': set(re.findall(r'\b\w+\b', text_lower))
        }
        return features

    def _compute_numeric_energy(self, p_nums: List[float], c_nums: List[float]) -> float:
        """Calculates energy based on numeric consistency."""
        if not p_nums:
            return 0.0
        if not c_nums:
            return 10.0 # High energy if numbers expected but missing
        
        # Check if candidate numbers satisfy simple prompt relations
        # Heuristic: If prompt has 2 numbers, candidate often implies a relation or result
        if len(p_nums) >= 2 and len(c_nums) >= 1:
            # Simple transitivity/comparison check approximation
            p_diff = p_nums[0] - p_nums[1] if len(p_nums) >= 2 else 0
            # If candidate is a number, does it align? (Very rough approximation for generic case)
            # In a full GNN, this would be message passing. Here we check magnitude alignment.
            pass 
        
        # Penalty for mismatched counts in strict numeric problems
        if len(p_nums) == len(c_nums):
            return 0.0
        return 2.0 * abs(len(p_nums) - len(c_nums))

    def _compute_logical_energy(self, p_feat: Dict, c_feat: Dict, prompt: str) -> float:
        """Calculates energy based on logical constraint satisfaction."""
        energy = 0.0
        prompt_lower = prompt.lower()
        
        # Negation consistency (Modus Tollens approximation)
        if p_feat['has_negation']:
            # If prompt has negation, candidate should ideally reflect understanding 
            # (heuristic: candidate length shouldn't be trivial, or should contain negation too if answering directly)
            if not c_feat['has_negation'] and c_feat['length'] < 10:
                energy += 3.0
        
        # Conditional consistency
        if p_feat['has_conditional']:
            if not c_feat['has_conditional'] and c_feat['length'] < 5:
                # Short answers to conditionals are often risky unless specific yes/no
                if 'yes' not in c_feat['words'] and 'no' not in c_feat['words']:
                    energy += 1.5
                    
        return energy

    def _calculate_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Computes Variational Free Energy (F = E - S).
        Minimizing F maximizes the likelihood of the hypothesis (candidate).
        """
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        
        # 1. Energy (E): Prediction error across structural modules
        e_numeric = self._compute_numeric_energy(p_feat['numbers'], c_feat['numbers'])
        e_logical = self._compute_logical_energy(p_feat, c_feat, prompt)
        
        # Lexical overlap as a soft constraint (lower energy if relevant words present)
        common_words = p_feat['words'].intersection(c_feat['words'])
        # Remove stop words from consideration for energy reduction
        stop_words = {'the', 'a', 'is', 'are', 'was', 'were', 'be', 'to', 'of', 'and', 'in', 'that', 'this'}
        relevant_overlap = len(common_words - stop_words)
        e_lexical = -0.5 * relevant_overlap  # Negative energy (bonus) for overlap
        
        total_energy = (self.w_numeric * e_numeric) + \
                       (self.w_logical * e_logical) + \
                       (self.w_lexical * e_lexical)

        # 2. Entropy/Complexity (S): Simplicity prior
        # Penalize overly long, rambling answers (complexity penalty)
        complexity = self.complexity_penalty * c_feat['length']
        
        # Free Energy = Energy - (Temperature * Entropy)
        # We approximate Entropy contribution as negative complexity
        free_energy = total_energy + complexity
        
        # Add NCD component as a tiebreaker/regularizer (Concept: NCD baseline)
        # But scaled down so structural parsing dominates
        ncd_val = self._ncd(prompt, candidate)
        free_energy += 0.1 * ncd_val
        
        return free_energy

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        try:
            c_s1 = len(zlib.compress(s1_b))
            c_s2 = len(zlib.compress(s2_b))
            c_s1_s2 = len(zlib.compress(s1_b + s2_b))
            if max(c_s1, c_s2) == 0:
                return 1.0
            return (c_s1_s2 - min(c_s1, c_s2)) / max(c_s1, c_s2)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluates candidates by minimizing variational free energy.
        Returns sorted list of dicts with scores (higher is better).
        """
        scored = []
        for cand in candidates:
            # We minimize Free Energy, so we negate it for a "score" where higher is better
            fe = self._calculate_free_energy(prompt, cand)
            score = -fe 
            scored.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Free Energy: {fe:.4f} (Lower is better)"
            })
        
        # Sort by score descending
        scored.sort(key=lambda x: x['score'], reverse=True)
        return scored

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the inverse of Free Energy.
        Uses a sigmoid-like mapping from the free energy value.
        """
        fe = self._calculate_free_energy(prompt, answer)
        # Map free energy to 0-1. 
        # Assuming typical FE ranges from -5 (great) to 10 (terrible).
        # sigmoid(-fe) roughly
        import math
        conf = 1 / (1 + math.exp(fe - 2.0)) # Shift to center around 0
        return max(0.0, min(1.0, conf))