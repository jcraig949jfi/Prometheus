import re
import zlib
from typing import List, Dict, Any

class ReasoningTool:
    """
    Critical Morphogenetic Sparse Coding (CMSC) Reasoning Tool.
    
    Mechanism:
    This tool implements a computational analogy of the CMSC network to evaluate reasoning candidates.
    1. Structural Parsing (The Reaction-Diffusion Field): Instead of physical diffusion, we model the 
       prompt as a 1D field where logical operators (negations, conditionals) act as morphogens. 
       We compute a "structural tension" score based on the presence and nesting of these operators.
    2. Phase Transition Monitor (Metacognition): The system calculates a 'criticality parameter' (chi).
       - If the candidate length and structural complexity are balanced (near critical point), 
         the system is in the optimal sparse coding regime (high score).
       - If the candidate is too simple (subcritical/homogeneous) or too complex/rambling (supercritical/rigid),
         the score drops.
    3. Sparse Coding Evaluation: Candidates are scored by how well their structural features (negations, 
       numeric comparisons) align with the prompt's requirements. NCD is used strictly as a tiebreaker
       for candidates with identical structural scores, adhering to the constraint that NCD is a weak signal.
    
    This approach prioritizes logical structure over semantic similarity, avoiding the pitfalls of 
    bag-of-words or pure compression metrics.
    """

    def __init__(self):
        # Logical operators act as "morphogens" defining the structure
        self.negations = ['not', 'no', 'never', 'none', 'cannot', 'impossible']
        self.conditionals = ['if', 'then', 'else', 'unless', 'provided']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<']
        self.numeric_pattern = re.compile(r'\d+\.?\d*')

    def _extract_structural_features(self, text: str) -> Dict[str, Any]:
        """Extract logical and numeric features acting as structural morphogens."""
        lower_text = text.lower()
        words = lower_text.split()
        
        has_negation = any(n in words for n in self.negations)
        has_conditional = any(c in words for c in self.conditionals)
        has_comparative = any(c in lower_text for c in self.comparatives)
        
        numbers = [float(n) for n in self.numeric_pattern.findall(text)]
        has_numbers = len(numbers) > 0
        
        # Numeric consistency check (simple transitivity/comparison)
        numeric_valid = True
        if len(numbers) >= 2:
            # Check if text implies a comparison that holds true
            # Since we can't parse full semantics, we flag high numeric density as a structural feature
            pass 
            
        return {
            'negation': has_negation,
            'conditional': has_conditional,
            'comparative': has_comparative,
            'numeric': has_numbers,
            'numbers': numbers,
            'length': len(words),
            'char_count': len(text)
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Compute Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denominator = max(c1, c2)
        if denominator == 0:
            return 0.0
        return (c12 - min(c1, c2)) / denominator

    def _calculate_criticality_score(self, prompt_feats: Dict, cand_feats: Dict) -> float:
        """
        Calculate score based on proximity to criticality.
        The 'order parameter' is the alignment of structural features.
        """
        score = 0.0
        
        # 1. Structural Resonance (Reaction-Diffusion Alignment)
        # If prompt has negation, correct answer often needs to handle it (or explicitly not, but structure must match)
        # We reward structural complexity matching.
        struct_match = 0.0
        if prompt_feats['negation']:
            struct_match += 0.25 if cand_feats['negation'] else -0.1
        if prompt_feats['conditional']:
            struct_match += 0.25 if cand_feats['conditional'] else -0.1
        if prompt_feats['comparative']:
            struct_match += 0.25 if cand_feats['comparative'] else -0.1
        if prompt_feats['numeric']:
            struct_match += 0.25 if cand_feats['numeric'] else -0.1
            
        score += struct_match

        # 2. Phase Transition Check (Sparsity vs. Noise)
        # Optimal zone: Not too short (noise), not too long (rigid/overfit)
        # Heuristic: Ideal length is between 10 and 100 words for reasoning tasks
        length = cand_feats['length']
        if 10 <= length <= 100:
            # Critical zone: Maximal flexibility
            phase_bonus = 0.2
        elif length < 3:
            # Subcritical: Homogeneous, low info
            phase_bonus = -0.2
        else:
            # Supercritical: Rigid, potentially hallucinated
            phase_bonus = -0.1
            
        score += phase_bonus

        # 3. Numeric Consistency (If applicable)
        if prompt_feats['numeric'] and cand_feats['numeric']:
            # Simple heuristic: if prompt has numbers, candidate should probably reference magnitude or logic
            # Since we can't verify truth without external tools, we reward the presence of numeric reasoning structure
            score += 0.1
            
        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        prompt_feats = self._extract_structural_features(prompt)
        results = []
        
        for cand in candidates:
            cand_feats = self._extract_structural_features(cand)
            
            # Primary Score: Structural/Criticality analysis
            base_score = self._calculate_criticality_score(prompt_feats, cand_feats)
            
            results.append({
                'candidate': cand,
                'base_score': base_score,
                'feats': cand_feats
            })
        
        # Rank by base_score first
        # Use NCD only as a tie-breaker for items with very close scores
        def sort_key(item):
            # Calculate NCD distance from prompt (lower is more similar in compression, 
            # but we use it only if base_scores are equal)
            ncd_val = self._compute_ncd(prompt, item['candidate'])
            # We want high base_score. If tie, we prefer lower NCD (more related content)
            # Inverting base_score for ascending sort, then using NCD
            return (-item['base_score'], ncd_val)

        results.sort(key=sort_key)
        
        # Normalize scores to 0-1 range roughly based on ranking and base_score magnitude
        max_score = results[0]['base_score'] if results else 0
        min_score = results[-1]['base_score'] if results else 0
        range_score = max_score - min_score if (max_score - min_score) != 0 else 1.0
        
        final_output = []
        for i, res in enumerate(results):
            # Linear interpolation to 0.5-1.0 for top candidates, 0.0-0.4 for others if gap is large
            # But strict requirement: beat NCD baseline. 
            # We rely on the structural score primarily.
            normalized = (res['base_score'] - min_score) / range_score
            # Shift to ensure positive and distinct
            final_score = 0.5 + (normalized * 0.49) 
            
            # Add small NCD perturbation only if scores are effectively tied
            if i > 0 and abs(res['base_score'] - results[i-1]['base_score']) < 0.01:
                ncd_penalty = self._compute_ncd(prompt, res['candidate']) * 0.001
                final_score -= ncd_penalty

            final_output.append({
                'candidate': res['candidate'],
                'score': round(final_score, 4),
                'reasoning': f"Structural alignment: {res['base_score']:.2f}, Criticality: {'Optimal' if 10<=res['feats']['length']<=100 else 'Sub/Supercritical'}"
            })
            
        return final_output

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Evaluate confidence based on structural integrity and criticality.
        Returns 0-1.
        """
        prompt_feats = self._extract_structural_features(prompt)
        ans_feats = self._extract_structural_features(answer)
        
        # Calculate structural alignment score
        score = self._calculate_criticality_score(prompt_feats, ans_feats)
        
        # Map score to 0-1 confidence
        # Base confidence starts at 0.5 (uncertain)
        # Strong structural match pushes to 0.9+
        # Strong mismatch pushes to 0.1-
        
        confidence = 0.5 + (score * 0.8) # Scale factor
        
        # Clamp
        confidence = max(0.0, min(1.0, confidence))
        
        # Penalty for empty or trivial answers if prompt is complex
        if prompt_feats['conditional'] or prompt_feats['negation']:
            if ans_feats['length'] < 5:
                confidence *= 0.5 # Heavy penalty for oversimplification in complex prompts
                
        return round(confidence, 4)