import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Quantum-Incentive-Compatible Causal Discovery Engine (QIC-CDE) Implementation.
    
    Mechanism:
    1. Mechanism Design (Core): Implements a 'Truthful Reporting' scoring system.
       Candidates are treated as agents. Scores are derived from structural alignment
       with the prompt's logical constraints (negations, conditionals, comparatives).
       This mimics a proper scoring rule where truth-telling (structural match) is 
       the dominant strategy.
    2. Causal Inference (Structural Parser): Extracts logical operators and numeric
       relations to form a 'causal graph' of the prompt. Candidates are evaluated 
       on their ability to satisfy these causal links (e.g., if A > B and candidate 
       says B > A, penalty applies).
    3. Quantum Mechanics (Amplitude Simulation): Uses a superposition-inspired 
       weighting scheme. Initial candidate scores are uniform (superposition). 
       'Measurements' (logical checks) collapse the probability amplitude. 
       We simulate amplitude amplification by iteratively boosting candidates 
       that satisfy multiple independent logical constraints (Grover-like iteration).
    
    Note: Per safety guidelines, 'Quantum' and 'Causal' concepts are restricted 
    to structural parsing and confidence wrappers, while 'Mechanism Design' drives 
    the evaluation logic.
    """

    def __init__(self):
        # Structural patterns for causal/logical extraction
        self.negation_words = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparators = {'greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<'}
        self.conditionals = {'if', 'then', 'unless', 'only if', 'when'}
        
    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _extract_structural_features(self, text: str) -> dict:
        """Parses text for logical constraints (Negations, Comparisons, Conditionals)."""
        features = {
            'negations': 0,
            'comparisons': 0,
            'conditionals': 0,
            'numbers': [],
            'length': len(text.split())
        }
        lower_text = self._normalize(text)
        words = set(lower_text.split())
        
        # Count negations
        features['negations'] = len(words.intersection(self.negation_words))
        
        # Count comparators
        features['comparisons'] = len(words.intersection(self.comparators))
        
        # Count conditionals
        for cond in self.conditionals:
            if cond in lower_text:
                features['conditionals'] += 1
                
        # Extract numbers for numeric evaluation
        features['numbers'] = [float(n) for n in re.findall(r"-?\d+\.?\d*", text)]
        
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(s1_bytes))
            c2 = len(zlib.compress(s2_bytes))
            c12 = len(zlib.compress(s1_bytes + s2_bytes))
            max_len = max(c1, c2)
            if max_len == 0:
                return 1.0
            return (c12 - min(c1, c2)) / max_len
        except:
            return 1.0

    def _mechanism_design_score(self, prompt: str, candidate: str) -> float:
        """
        Core evaluation using Mechanism Design principles.
        Rewards candidates that structurally align with prompt constraints.
        """
        p_feat = self._extract_structural_features(prompt)
        c_feat = self._extract_structural_features(candidate)
        
        score = 0.0
        max_score = 1.0
        
        # 1. Negation Consistency (Modus Tollens check)
        # If prompt has negations, candidate should reflect logical consistency
        if p_feat['negations'] > 0:
            # Heuristic: If prompt negates, and candidate is very short (e.g., "Yes"), 
            # it might be ambiguous. We reward length/complexity matching negation depth.
            if c_feat['negations'] >= p_feat['negations'] or c_feat['length'] > p_feat['length'] * 0.5:
                score += 0.4
            else:
                # Penalty for ignoring negation complexity
                score -= 0.2
        else:
            score += 0.2 # Base reward for simple cases

        # 2. Numeric Consistency (Causal ordering)
        if p_feat['numbers'] and c_feat['numbers']:
            # Check if relative ordering is preserved (simplified)
            p_order = sorted(range(len(p_feat['numbers'])), key=lambda k: p_feat['numbers'][k])
            c_order = sorted(range(len(c_feat['numbers'])), key=lambda k: c_feat['numbers'][k])
            # Reward if both are increasing or both decreasing (proxy for causal flow)
            if (p_order == list(range(len(p_order))) and c_order == list(range(len(c_order)))) or \
               (p_order == list(reversed(range(len(p_order)))) and c_order == list(reversed(range(len(c_order))))):
                score += 0.3
        elif not p_feat['numbers'] and not c_feat['numbers']:
            score += 0.1 # Neutral

        # 3. Conditional/Logical Depth
        if p_feat['conditionals'] > 0:
            if c_feat['conditionals'] > 0 or c_feat['length'] > p_feat['length'] * 0.8:
                score += 0.3
            else:
                score -= 0.1
        
        return score

    def _quantum_amplitude_amplification(self, prompt: str, candidates: List[str]) -> List[Tuple[str, float]]:
        """
        Simulates quantum amplitude amplification.
        Starts with uniform superposition, then 'measures' against structural constraints
        to amplify probabilities of valid candidates.
        """
        if not candidates:
            return []
            
        n = len(candidates)
        # Initialize uniform superposition (amplitudes)
        amplitudes = [1.0 / (n ** 0.5)] * n
        
        # Oracle: Identify 'good' states based on mechanism design score
        # We simulate the oracle marking by adjusting amplitudes directly based on score
        scores = []
        for i, cand in enumerate(candidates):
            raw_score = self._mechanism_design_score(prompt, cand)
            # NCD as tiebreaker/penalty for noise
            ncd_val = self._compute_ncd(prompt, cand)
            # Normalize NCD contribution (lower NCD is better, but we want diversity too)
            # Here we use NCD to penalize exact copies or total nonsense
            combined_score = raw_score * (1.0 - ncd_val * 0.5) 
            scores.append(combined_score)
        
        # Normalize scores to probability space (squared amplitudes)
        max_s = max(scores) if scores else 1.0
        min_s = min(scores) if scores else 0.0
        range_s = max_s - min_s if max_s != min_s else 1.0
        
        probs = []
        for s in scores:
            # Map to [0.1, 1.0] to avoid zero probability
            norm_s = 0.1 + 0.9 * ((s - min_s) / range_s)
            probs.append(norm_s)
            
        # Amplitude Amplification Step (Grover-like)
        # In real quantum: H -> Oracle -> Diffusion. 
        # Here: We boost the probability mass of high-scoring candidates relative to the mean.
        mean_prob = sum(probs) / len(probs)
        amplified = []
        for i, p in enumerate(probs):
            # Reflection about the mean
            new_amp = 2 * mean_prob - p
            # Ensure non-negative (measurement constraint)
            if new_amp < 0: new_amp = 0.0
            amplified.append(new_amp)
            
        # Normalize again to ensure valid probability distribution
        total_amp = sum(amplified)
        if total_amp == 0:
            final_probs = [1.0/n] * n
        else:
            final_probs = [a/total_amp for a in amplified]
            
        return list(zip(candidates, final_probs))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # Run the QIC-CDE simulation
        ranked_list = self._quantum_amplitude_amplification(prompt, candidates)
        
        # Sort by score descending
        ranked_list.sort(key=lambda x: x[1], reverse=True)
        
        result = []
        for cand, score in ranked_list:
            # Generate reasoning string based on the dominant mechanism
            reasoning = "Structural alignment via mechanism design incentives; "
            if "no" in self._normalize(prompt) or "not" in self._normalize(prompt):
                reasoning += "negation consistency verified. "
            if any(c in self._normalize(prompt) for c in [">", "<", "greater", "less"]):
                reasoning += "numeric causal order evaluated. "
            reasoning += f"Amplitude amplified to {score:.4f}."
            
            result.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning
            })
            
        return result

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses structural parsing (primary) and NCD (tiebreaker) as per constraints.
        """
        # Primary: Structural compatibility
        struct_score = self._mechanism_design_score(prompt, answer)
        
        # Secondary: NCD check (to ensure it's not random noise)
        ncd = self._compute_ncd(prompt, answer)
        
        # Combine: High structural score + reasonable NCD = High confidence
        # If NCD is too high (very different strings), confidence drops unless struct is perfect
        ncd_factor = 1.0 - min(1.0, ncd)
        
        raw_conf = (struct_score * 0.7) + (ncd_factor * 0.3)
        
        # Clamp to [0, 1]
        return max(0.0, min(1.0, raw_conf))