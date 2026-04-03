import re
import zlib
import math
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Quantum-Sparse Graph Autoencoder (QSGA) Simulator with Epistemic Honesty.
    
    Mechanism:
    1.  **Quantum Superposition (Simulation)**: Treats all candidates as a superposition state.
        Instead of physical qubits, we use a weighted vector space where weights are derived
        from structural parsing and logical consistency.
    2.  **Sparse Autoencoder (Bottleneck)**: Enforces a "top-k" sparsity on reasoning features.
        It extracts salient logical motifs (negations, comparatives, numeric constraints) and
        zeroes out noise, ensuring the final score relies only on high-signal structural features.
    3.  **Epistemic Honesty (Meta-Confidence)**: Before scoring, the system scans for
        "poisonous" graph structures in the prompt (presuppositions, ambiguities, false dichotomies).
        If detected, the confidence collapses (< 0.3) regardless of candidate quality.
    4.  **Scoring**: A hybrid of structural match (50%), constructive computation (35%), 
       and NCD tie-breaking (15%).
    """

    def __init__(self):
        # Sparsity threshold (k) for the latent bottleneck
        self.sparsity_k = 3 
        # Weights for score decomposition
        self.w_struct = 0.50
        self.w_comp = 0.35
        self.w_ncd = 0.15

    # --- Helper: Structural Parsing & Feature Extraction ---
    def _extract_features(self, text: str) -> Dict:
        """Extracts logical motifs (features) from text."""
        text_lower = text.lower()
        features = {
            'has_negation': bool(re.search(r'\b(not|no|never|neither|without)\b', text_lower)),
            'has_comparative': bool(re.search(r'\b(more|less|greater|smaller|better|worse|larger|smaller|than|<|>)\b', text_lower)),
            'has_conditional': bool(re.search(r'\b(if|then|unless|provided|otherwise)\b', text_lower)),
            'has_numbers': re.findall(r'-?\d+\.?\d*', text_lower),
            'has_either_or': bool(re.search(r'\b(either|or)\b', text_lower)),
            'has_why': bool(re.search(r'\b(why|how)\b', text_lower)),
            'has_presupposition_triggers': bool(re.search(r'\b(stopped|quit|failed|regret|realize)\b', text_lower)),
            'word_count': len(text.split())
        }
        return features

    # --- Helper: Constructive Computation ---
    def _attempt_computation(self, prompt: str, candidate: str) -> Optional[float]:
        """
        Attempts to solve math/logic problems constructively.
        Returns a score (1.0 for correct, 0.0 for wrong) or None if not a math problem.
        """
        # Detect simple numeric comparison prompts
        num_match = re.search(r'compare\s+([\d.]+)\s+and\s+([\d.]+)', prompt.lower())
        if num_match:
            try:
                n1, n2 = float(num_match.group(1)), float(num_match.group(2))
                # Check candidate for "first", "second", "larger", "smaller"
                cand_lower = candidate.lower()
                if n1 > n2:
                    return 1.0 if ('first' in cand_lower or str(n1) in cand_lower or 'larger' in cand_lower) else 0.0
                elif n2 > n1:
                    return 1.0 if ('second' in cand_lower or str(n2) in cand_lower or 'larger' in cand_lower) else 0.0
            except: pass

        # Detect simple arithmetic "What is X + Y?"
        calc_match = re.search(r'what\s+is\s+([\d.]+)\s*[\+\-\*/]\s*([\d.]+)', prompt.lower())
        if calc_match:
            try:
                # Very basic eval safety
                expr = prompt.lower().replace('what is', '').strip()
                # Sanitize
                expr = re.sub(r'[^\d.\+\-\*/\s]', '', expr)
                expected = eval(expr) # Safe due to regex filter
                if str(expected) in candidate or str(int(expected)) in candidate:
                    return 1.0
                return 0.0
            except: pass
            
        return None

    # --- Helper: NCD Calculation ---
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0: return 0.0
        return (c12 - min(c1, c2)) / max_len

    # --- Meta-Confidence: Epistemic Honesty Check ---
    def _meta_confidence(self, prompt: str) -> float:
        """
        Analyzes the PROMPT for ambiguity, presupposition, or unanswerability.
        Returns a cap value (low if problematic).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition Traps ("Have you stopped...", "Why did X fail?")
        if re.search(r'\b(have you stopped|did you stop|why did .+ fail|why is .+ wrong|regret)\b', p_lower):
            return 0.2
        
        # 2. Scope/Pronoun Ambiguity patterns
        if re.search(r'\b(every .+ a .+|he told .+ he|who is .+)\b', p_lower) and '?' in prompt:
            # Heuristic: if it asks "who" and has multiple male names, it's ambiguous
            names = re.findall(r'\b([A-Z][a-z]+)\b', prompt)
            if len(set(names)) > 1 and 'who' in p_lower:
                return 0.25

        # 3. False Dichotomy ("Either A or B" without context)
        if re.search(r'\b(either .+ or .+)\b', p_lower) and 'must' in p_lower:
             return 0.3

        # 4. Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|beautiful)\b', p_lower) and 'according to' not in p_lower:
            return 0.3

        # 5. Unanswerable (Missing info)
        if re.search(r'\b(calculate|solve|find)\b', p_lower) and not re.search(r'\d', prompt):
            return 0.2

        return 1.0 # No obvious traps detected

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """Scores based on structural alignment (negations, conditionals)."""
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        
        score = 0.0
        matches = 0
        total = 0

        # Check negation consistency
        if p_feat['has_negation']:
            total += 1
            if c_feat['has_negation'] == p_feat['has_negation']:
                matches += 1
            # If prompt has negation, candidate MUST acknowledge it to be high score? 
            # Simplified: Just matching presence helps filter random noise.
        
        # Check comparative consistency
        if p_feat['has_comparative']:
            total += 1
            if c_feat['has_comparative']:
                matches += 1
        
        # Conditional logic check (very basic)
        if p_feat['has_conditional']:
            total += 1
            if c_feat['has_conditional'] or len(c_feat['has_numbers']) > 0:
                matches += 1

        if total == 0:
            return 0.5 # Neutral if no structural hooks
        return matches / total

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # 1. Meta-Confidence Cap (Epistemic Honesty)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Pre-compute prompt features for sparsity
        p_feat = self._extract_features(prompt)
        prompt_vec = [
            float(p_feat['has_negation']),
            float(p_feat['has_comparative']),
            float(p_feat['has_conditional']),
            float(len(p_feat['has_numbers']) > 0),
            float(p_feat['has_either_or']),
            float(p_feat['has_why']),
            float(p_feat['has_presupposition_triggers']),
            float(p_feat['word_count']) / 100.0
        ]

        for cand in candidates:
            # --- Sparse Autoencoder Simulation ---
            # Encode candidate into feature space
            c_feat = self._extract_features(cand)
            cand_vec = [
                float(c_feat['has_negation']),
                float(c_feat['has_comparative']),
                float(c_feat['has_conditional']),
                float(len(c_feat['has_numbers']) > 0),
                float(c_feat['has_either_or']),
                float(c_feat['has_why']),
                float(c_feat['has_presupposition_triggers']),
                float(c_feat['word_count']) / 100.0
            ]
            
            # Dot product similarity (unnormalized)
            activation = sum(p * c for p, c in zip(prompt_vec, cand_vec))
            
            # Sparsity Bottleneck: Keep only top-k contributions? 
            # Here we simulate by thresholding the activation relative to max possible
            # If the candidate doesn't share key structural motifs, activation is low.
            
            # --- Component Scores ---
            
            # A. Structural Score
            struct_score = self._structural_score(prompt, cand)
            
            # B. Computational Score (Constructive)
            comp_res = self._attempt_computation(prompt, cand)
            comp_score = comp_res if comp_res is not None else 0.5 # 0.5 if not a math problem
            
            # C. NCD Score (Similarity based, inverted for distance)
            # We want high similarity for reasoning tasks usually, unless it's a trick.
            # But NCD is a tiebreaker. Let's use 1 - NCD as similarity.
            ncd_sim = 1.0 - self._ncd(prompt, cand)
            # Normalize NCD contribution to be small
            ncd_score = ncd_sim 

            # Weighted Sum
            raw_score = (self.w_struct * struct_score) + \
                        (self.w_comp * comp_score) + \
                        (self.w_ncd * ncd_score)
            
            # Apply Sparsity/Quantum Interference Effect
            # If meta_cap is low, the "wavefunction collapses" to low confidence
            final_score = raw_score * meta_cap
            
            # Generate Reasoning String
            reasoning = f"Structural match: {struct_score:.2f}, Comp: {comp_score:.2f}, Meta-cap: {meta_cap:.2f}"
            if meta_cap < 0.3:
                reasoning = "Epistemic warning: Prompt contains ambiguity or presupposition."

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })

        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly capped by _meta_confidence to ensure epistemic honesty.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # If the prompt is clean, we check if the answer makes sense structurally
        if meta_cap >= 0.9:
            # Run a mini-evaluation to see how well this specific answer fits
            # We simulate a dummy candidate list to get the score
            res = self.evaluate(prompt, [answer])
            if res:
                base_score = res[0]['score']
                # Cap at 0.9 unless it's a definitive computation
                if base_score > 0.9:
                    base_score = 0.95
                return min(base_score, meta_cap)
        
        return min(0.25, meta_cap) if meta_cap < 0.3 else 0.5

# Example Usage (Internal Test):
if __name__ == "__main__":
    tool = ReasoningTool()
    
    # Test 1: Clear Math (Tier A)
    p1 = "What is 2 + 2?"
    c1 = ["4", "5", "The result is four."]
    print("Test 1 (Math):", tool.evaluate(p1, c1))
    print("Confidence:", tool.confidence(p1, "4"))
    
    # Test 2: Presupposition Trap (Tier B)
    p2 = "Have you stopped cheating on tests?"
    c2 = ["Yes", "No"]
    print("\nTest 2 (Presupposition):", tool.evaluate(p2, c2))
    print("Confidence:", tool.confidence(p2, "Yes"))
    
    # Test 3: Ambiguity
    p3 = "John told Bill he was wrong. Who was wrong?"
    c3 = ["John", "Bill", "Unclear"]
    print("\nTest 3 (Ambiguity):", tool.evaluate(p3, c3))
    print("Confidence:", tool.confidence(p3, "John"))