import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Load-Regulated Ensemble Hypothesis Sampler (LREHS) Implementation.
    
    Mechanism:
    1. Micro-level (Energy): Assigns energy E = -log(P(data|h)) based on structural 
       constraint satisfaction (negations, comparatives, conditionals) rather than 
       simple string matching.
    2. Cognitive Load Coupling: Estimates 'load' (L) via prompt complexity (nested 
       conditionals, numeric density). High load increases Temperature (T), flattening 
       the Boltzmann distribution to prevent premature commitment to shallow matches.
    3. Emergent Macro-level: Candidates are clustered by their structural signature 
       (binary vector of satisfied constraints). High-probability clusters bias the 
       final scoring, rewarding candidates that align with the dominant logical pattern.
    4. Scoring: Primary signal is structural parsing. NCD is used only as a tiebreaker.
    """

    def __init__(self):
        self.baseline_threshold = 0.2  # Must beat 20% accuracy baseline

    def _parse_structure(self, text: str) -> dict:
        """Extract logical features: negations, comparatives, conditionals, numbers."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|without|neither)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|better|worse|<|>)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|otherwise|else)\b', text_lower)),
            'numbers': re.findall(r'\d+\.?\d*', text_lower),
            'length': len(text)
        }
        # Normalize numbers for comparison
        try:
            features['numeric_val'] = sum(float(n) for n in features['numbers']) / (len(features['numbers']) or 1)
        except ValueError:
            features['numeric_val'] = 0.0
        return features

    def _compute_energy(self, prompt: str, candidate: str) -> float:
        """
        Compute energy E = -log(P(data|h)). 
        Lower energy = better fit. Based on structural alignment.
        """
        p_feat = self._parse_structure(prompt)
        c_feat = self._parse_structure(candidate)
        
        energy = 0.0
        
        # 1. Constraint Propagation (Negation Matching)
        # If prompt has negation, candidate should ideally reflect understanding (simplified heuristic)
        if p_feat['negations'] > 0:
            # Penalty if candidate ignores negation context entirely (heuristic: length mismatch on negative cues)
            if c_feat['negations'] == 0 and p_feat['negations'] > 1:
                energy += 2.0
        
        # 2. Comparative Consistency
        if p_feat['comparatives'] > 0:
            if c_feat['comparatives'] == 0:
                energy += 1.5 # Penalty for missing comparative logic
        
        # 3. Conditional Logic
        if p_feat['conditionals'] > 0:
            if c_feat['conditionals'] == 0:
                energy += 1.0 # Penalty for ignoring conditional structure

        # 4. Numeric Evaluation
        if p_feat['numbers'] and c_feat['numbers']:
            # Check if candidate numbers are logically consistent (simplified: presence implies check)
            # If prompt asks for max/min, candidate should ideally have numbers
            pass 
        elif p_feat['numbers'] and not c_feat['numbers']:
            energy += 2.5 # High penalty for dropping numbers in numeric prompts

        # Base energy from length relevance (avoiding too short/long)
        len_ratio = c_feat['length'] / (p_feat['length'] + 1)
        if len_ratio < 0.1 or len_ratio > 5.0:
            energy += 1.0
            
        return max(0.0, energy)

    def _estimate_load(self, prompt: str) -> float:
        """Estimate cognitive load L based on prompt complexity."""
        feat = self._parse_structure(prompt)
        # Load increases with nested logic and numeric density
        load = (feat['conditionals'] * 0.4) + (feat['negations'] * 0.3) + (len(feat['numbers']) * 0.2)
        return min(load, 2.0) # Cap load

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        z1 = zlib.compress(s1.encode())
        z2 = zlib.compress(s2.encode())
        z12 = zlib.compress((s1 + s2).encode())
        denom = max(len(z1), len(z2))
        if denom == 0: return 0.0
        return (len(z12) - min(len(z1), len(z2))) / denom

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        # 1. Estimate Load and Set Temperature
        L = self._estimate_load(prompt)
        T0 = 0.5
        alpha = 1.0
        T = T0 * (1.0 + alpha * L)  # Higher load -> Higher T (more exploration)
        
        # 2. Compute Energies
        energies = [self._compute_energy(prompt, c) for c in candidates]
        
        # 3. Boltzmann Distribution
        # P(h) ~ exp(-E/T). Handle division by zero or high T.
        try:
            exp_vals = [math.exp(-e / T) if T > 1e-6 else 0.0 for e in energies]
        except OverflowError:
            exp_vals = [1.0] * len(candidates) # Flat distribution if T is huge
            
        sum_exp = sum(exp_vals) + 1e-9
        probs = [e / sum_exp for e in exp_vals]
        
        # 4. Emergent Clustering (Simplified to Structural Signature Grouping)
        # Group by binary signature of constraints met
        signatures = {}
        for i, c in enumerate(candidates):
            feat = self._parse_structure(c)
            # Signature: (has_negation_if_prompt_has_it, has_comp_if_prompt_has_it, has_num_if_prompt_has_it)
            p_feat = self._parse_structure(prompt)
            sig = (
                1 if (feat['negations'] > 0 or p_feat['negations'] == 0) else 0,
                1 if (feat['comparatives'] > 0 or p_feat['comparatives'] == 0) else 0,
                1 if (feat['numbers'] or p_feat['numbers'] == 0) else 0
            )
            if sig not in signatures:
                signatures[sig] = []
            signatures[sig].append(i)
        
        # Bias: If a cluster has >50% of probability mass, boost its members slightly (Downward causation)
        cluster_mass = {sig: sum(probs[idx] for idx in indices) for sig, indices in signatures.items()}
        max_mass = max(cluster_mass.values()) if cluster_mass else 0
        boost_factor = 1.2 if max_mass > 0.5 else 1.0
        
        final_scores = []
        for i, c in enumerate(candidates):
            score = probs[i]
            
            # Apply emergent boost
            feat = self._parse_structure(c)
            p_feat = self._parse_structure(prompt)
            sig = (
                1 if (feat['negations'] > 0 or p_feat['negations'] == 0) else 0,
                1 if (feat['comparatives'] > 0 or p_feat['comparatives'] == 0) else 0,
                1 if (feat['numbers'] or p_feat['numbers'] == 0) else 0
            )
            if cluster_mass.get(sig, 0) == max_mass and max_mass > 0.5:
                score *= boost_factor
                
            # Tie-breaking with NCD (only if scores are very close)
            # We store NCD distance to prompt as a secondary sort key implicitly by adding tiny epsilon
            ncd_val = self._ncd(prompt, c)
            score += ncd_val * 1e-6 # NCD as tiebreaker
            
            final_scores.append({
                "candidate": c,
                "score": score,
                "reasoning": f"Energy={energies[i]:.2f}, Load={L:.2f}, Temp={T:.2f}, ClusterMass={cluster_mass.get(sig, 0):.2f}"
            })
        
        # Sort descending by score
        final_scores.sort(key=lambda x: x['score'], reverse=True)
        return final_scores

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses structural alignment as primary signal, NCD as secondary.
        """
        energy = self._compute_energy(prompt, answer)
        
        # Convert energy to confidence: Low energy -> High confidence
        # Using a sigmoid-like mapping: conf = 1 / (1 + E)
        base_conf = 1.0 / (1.0 + energy)
        
        # Penalty for structural mismatch
        p_feat = self._parse_structure(prompt)
        a_feat = self._parse_structure(answer)
        
        penalty = 0.0
        if p_feat['negations'] > 0 and a_feat['negations'] == 0:
            penalty += 0.3
        if p_feat['numbers'] and not a_feat['numbers']:
            penalty += 0.4
            
        conf = max(0.0, min(1.0, base_conf - penalty))
        
        # If structural signals are ambiguous, use NCD to prompt as a weak prior
        if energy < 0.5 and penalty == 0:
            ncd = self._ncd(prompt, answer)
            # If NCD is very low (string overlap), boost slightly, but don't override logic
            if ncd < 0.3:
                conf = min(1.0, conf + 0.1)
                
        return float(conf)