import re
import math
import numpy as np
from collections import defaultdict
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A reasoning evaluator combining structural logic parsing, wavelet-based 
    multi-resolution analysis, and thermodynamic scoring with mechanism design penalties.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions (negations, comparatives, conditionals, causals).
    2. Graph: Builds a dependency graph to detect contradictions (cycles with opposing polarity).
    3. Wavelet: Linearizes logic into a binary signal, applies Haar transform for energy/entropy.
    4. Thermodynamics: Scores candidates via KL-divergence from a reference distribution.
    5. Mechanism Design: Penalizes self-contradictory candidates to ensure incentive compatibility.
    """

    def __init__(self):
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|nobody|nothing)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|before|after)\b|\b[<>=]+\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|otherwise|provided)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|therefore|thus|hence|leads to|results in|causes)\b', re.IGNORECASE),
            'numeric': re.compile(r'-?\d+(\.\d+)?\s*(?:kg|m|s|J|K|%)?'),
            'unit': re.compile(r'\d+\s*([a-zA-Z%]+)')
        }
        self.lambda_penalty = 2.0  # Weight for mechanism design penalty
        self.contradiction_penalty = 5.0  # Constant C for cycles

    def _extract_propositions(self, text: str) -> List[Dict]:
        """Extract atomic propositions with polarity and type."""
        props = []
        text_lower = text.lower()
        
        # Check negations
        if self.patterns['negation'].search(text_lower):
            props.append({'type': 'negation', 'polarity': -1, 'text': 'negation_found'})
            
        # Check comparatives
        if self.patterns['comparative'].search(text_lower):
            props.append({'type': 'comparative', 'polarity': 1, 'text': 'comparative_found'})
            
        # Check conditionals
        if self.patterns['conditional'].search(text_lower):
            props.append({'type': 'conditional', 'polarity': 1, 'text': 'conditional_found'})
            
        # Check causals
        if self.patterns['causal'].search(text_lower):
            props.append({'type': 'causal', 'polarity': 1, 'text': 'causal_found'})

        # Numeric extraction and evaluation
        nums = self.patterns['numeric'].findall(text_lower)
        if len(nums) >= 2:
            try:
                # Simple heuristic: if numbers appear, check ordering implied by text
                val1 = float(nums[0].replace(',', ''))
                val2 = float(nums[1].replace(',', ''))
                if ('less' in text_lower or '<' in text) and val1 > val2:
                     props.append({'type': 'numeric_contradiction', 'polarity': -1, 'text': 'num_error'})
                elif ('more' in text_lower or '>' in text) and val1 < val2:
                     props.append({'type': 'numeric_contradiction', 'polarity': -1, 'text': 'num_error'})
            except ValueError:
                pass

        if not props:
            # Fallback for empty logic: treat as neutral node
            props.append({'type': 'default', 'polarity': 1, 'text': 'default'})
            
        return props

    def _build_graph(self, props: List[Dict]) -> Tuple[List, List]:
        """Build adjacency list and detect cycles with opposing polarities."""
        nodes = list(range(len(props)))
        edges = []
        
        # Infer edges: sequential dependency + causal/conditional links
        for i in range(len(props) - 1):
            edges.append((i, i + 1, 1.0)) # Sequential flow
            
        # Check for explicit causal links (simplified: connect causal nodes to next)
        for i, p in enumerate(props):
            if p['type'] in ['conditional', 'causal']:
                if i + 1 < len(props):
                    edges.append((i, i + 1, 0.5)) # Probabilistic cue

        # Cycle detection with polarity check (Simplified for linear text)
        # In a linear parse, a "cycle" implies a direct contradiction in close proximity 
        # or a negation of a previous assertion.
        has_contradiction = False
        polarities = [p['polarity'] for p in props]
        
        # Heuristic: If we have mixed polarities in a small window, flag as potential contradiction
        if len(polarities) > 1:
            if any(polarities[i] * polarities[i+1] == -1 for i in range(len(polarities)-1)):
                has_contradiction = True
            # Global contradiction: explicit negation found alongside positive assertions of same type?
            if -1 in polarities and 1 in polarities:
                 # Only if specific contradiction types found
                 if any(p['type'] == 'numeric_contradiction' for p in props):
                     has_contradiction = True

        return nodes, edges, has_contradiction

    def _wavelet_transform(self, signal: np.ndarray) -> Tuple[np.ndarray, float, float]:
        """Apply Haar wavelet transform and compute energy/entropy."""
        if len(signal) == 0:
            return np.array([0]), 0.0, 0.0
            
        # Pad to power of 2
        n = len(signal)
        pad_len = int(2**math.ceil(math.log2(n))) - n if n > 0 else 1
        signal = np.pad(signal, (0, pad_len), mode='constant')
        
        coeffs = []
        current = signal.astype(float)
        
        # Haar transform iteration
        while len(current) > 1:
            avg = (current[0::2] + current[1::2]) / 2
            diff = (current[0::2] - current[1::2]) / 2
            coeffs.append(diff)
            current = avg
        
        coeffs.append(current) # Approximation
        all_coeffs = np.concatenate(coeffs)
        
        # Energy per scale (simplified: sum of squares of detail coeffs per level)
        energies = [np.sum(c**2) for c in coeffs]
        total_energy = sum(energies) + 1e-9
        probs = np.array(energies) / total_energy
        
        # Entropy
        entropy = -np.sum(probs * np.log2(probs + 1e-9))
        
        return all_coeffs, total_energy, entropy

    def _kl_divergence(self, p: np.ndarray, q: np.ndarray) -> float:
        """Compute KL divergence D_KL(P || Q)."""
        p = np.array(p) + 1e-9
        q = np.array(q) + 1e-9
        p = p / np.sum(p)
        q = q / np.sum(q)
        return np.sum(p * np.log(p / q))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_props = self._extract_propositions(prompt)
        _, _, prompt_has_contra = self._build_graph(prompt_props)
        
        # Create a synthetic "ideal" reference signal based on prompt structure
        # We assume the prompt contains the necessary logical atoms.
        ref_signal = np.ones(len(prompt_props)) if prompt_props else np.array([1.0])
        ref_coeffs, ref_energy, ref_entropy = self._wavelet_transform(ref_signal)
        
        # Normalize reference distribution for KL
        ref_dist = np.abs(ref_coeffs)
        ref_dist = ref_dist / (np.sum(ref_dist) + 1e-9) if np.sum(ref_dist) > 0 else ref_dist

        results = []
        
        for cand in candidates:
            cand_props = self._extract_propositions(cand)
            nodes, edges, has_contra = self._build_graph(cand_props)
            
            # Binary signal: 1 if node present
            signal = np.ones(len(cand_props)) if cand_props else np.array([0.0])
            
            if len(signal) == 0:
                signal = np.array([0.0])
                
            coeffs, energy, entropy = self._wavelet_transform(signal)
            
            # Thermodynamic Scoring
            # Align dimensions for KL (simple truncation or padding)
            min_len = min(len(ref_dist), len(coeffs))
            cand_dist = np.abs(coeffs[:min_len])
            ref_sub = ref_dist[:min_len]
            
            if np.sum(cand_dist) == 0:
                cand_dist = np.ones_like(ref_sub) * 1e-9
            
            cand_dist = cand_dist / (np.sum(cand_dist) + 1e-9)
            ref_sub = ref_sub / (np.sum(ref_sub) + 1e-9)
            
            try:
                kl_div = self._kl_divergence(cand_dist, ref_sub)
            except:
                kl_div = 10.0 # High penalty for failure
                
            s_t = math.exp(-kl_div)
            
            # Mechanism Design Penalty
            v_penalty = self.contradiction_penalty if has_contra else 0.0
            utility = s_t - (self.lambda_penalty * v_penalty)
            
            results.append({
                "candidate": cand,
                "score": utility,
                "reasoning": f"Wavelet Energy={energy:.2f}, Entropy={entropy:.2f}, Contradiction={has_contra}, KL_Div={kl_div:.2f}"
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on structural alignment and lack of contradictions."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        score = res[0]['score']
        # Map score to 0-1. 
        # Theoretical max S_T is 1.0 (if KL=0). Penalties reduce it.
        # If score < 0, confidence is 0.
        conf = max(0.0, min(1.0, score))
        return conf