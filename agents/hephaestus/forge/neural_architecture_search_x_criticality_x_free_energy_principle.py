import numpy as np
import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a computational analogy of NAS x Criticality x Free Energy Principle.
    
    Mechanism:
    1. Predictive Coding (FEP): Models the 'expected' answer structure based on prompt constraints.
       Calculates 'Free Energy' as the divergence between candidate content and prompt constraints.
    2. Criticality: Evaluates the 'susceptibility' of the answer. Answers containing specific 
       logical operators (negations, comparatives) or numeric precision are treated as being 
       near the 'edge of chaos' (high information density), receiving a criticality bonus.
    3. NAS (Topology Search): Treats the weighting of evidence types (numeric, logical, lexical) 
       as a searchable architecture. It dynamically selects the best weighting strategy (sub-architecture) 
       that minimizes Free Energy while maximizing Criticality for the specific prompt type.
    """
    
    def __init__(self):
        self.rng = np.random.default_rng(42) # Deterministic seed
        
    def _extract_features(self, text: str) -> Dict:
        """Extract structural features for criticality analysis."""
        text_lower = text.lower()
        has_negation = bool(re.search(r'\b(not|no|never|neither|none)\b', text_lower))
        has_comparative = bool(re.search(r'\b(more|less|greater|smaller|better|worse|<|>)\b', text_lower))
        has_conditional = bool(re.search(r'\b(if|then|unless|provided)\b', text_lower))
        
        # Numeric extraction
        nums = re.findall(r'-?\d+\.?\d*', text)
        numbers = [float(n) for n in nums] if nums else []
        
        return {
            'length': len(text),
            'negation': int(has_negation),
            'comparative': int(has_comparative),
            'conditional': int(has_conditional),
            'numbers': numbers,
            'complexity': len(set(text.split())) # Vocabulary richness
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(c1, c2)
        if denom == 0: return 1.0
        return (c12 - min(c1, c2)) / denom

    def _calculate_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Surrogate for Variational Free Energy.
        Measures divergence between candidate and prompt constraints.
        Low energy = high consistency with prompt context.
        """
        # 1. Lexical divergence (NCD component)
        ncd = self._compute_ncd(prompt, candidate)
        
        # 2. Constraint satisfaction (Simple heuristic: does candidate contain prompt keywords?)
        p_words = set(re.findall(r'\w+', prompt.lower()))
        c_words = set(re.findall(r'\w+', candidate.lower()))
        overlap = len(p_words.intersection(c_words))
        coverage = overlap / len(p_words) if p_words else 0
        
        # Energy is high if NCD is high (dissimilar) or coverage is low
        # We invert coverage so high overlap = low energy
        energy = (ncd * 0.7) + ((1.0 - coverage) * 0.3)
        return energy

    def _calculate_criticality(self, candidate: str) -> float:
        """
        Criticality Bonus.
        Rewards candidates with high 'susceptibility' features (logic, numbers, structure).
        Analogous to operating near the edge of chaos where information processing is maximal.
        """
        feats = self._extract_features(candidate)
        score = 0.0
        
        # Logical operators increase susceptibility (criticality)
        score += feats['negation'] * 0.4
        score += feats['comparative'] * 0.4
        score += feats['conditional'] * 0.3
        
        # Numeric precision implies high sensitivity
        if feats['numbers']:
            score += 0.2
            
        # Normalize roughly to 0-1 range based on typical lengths
        # Longer, structured answers tend to be more 'critical' in reasoning tasks
        length_factor = min(1.0, feats['length'] / 50.0) 
        return min(1.0, score + (length_factor * 0.2))

    def _nas_architecture_search(self, prompt: str, candidates: List[str]) -> Tuple[float, float, float]:
        """
        Simulates Neural Architecture Search.
        Selects the optimal weighting (architecture) of evidence types for this specific prompt.
        Returns weights for (Energy, Criticality, Complexity).
        """
        p_feats = self._extract_features(prompt)
        
        # Define discrete architecture candidates (weight tuples)
        architectures = [
            (0.6, 0.3, 0.1), # Balanced
            (0.8, 0.1, 0.1), # Energy dominant (factual match)
            (0.3, 0.6, 0.1), # Criticality dominant (logic heavy)
            (0.4, 0.4, 0.2), # Hybrid
        ]
        
        best_score = -np.inf
        best_weights = (0.4, 0.4, 0.2)
        
        # Evaluate architectures on a proxy task: separation of candidate scores
        # We want an architecture that maximizes the gap between 'good' and 'bad' candidates
        # assuming 'good' candidates have lower energy and higher criticality.
        
        if not candidates:
            return best_weights[0], best_weights[1], best_weights[2]

        # Precompute metrics
        metrics = []
        for c in candidates:
            e = self._calculate_free_energy(prompt, c)
            crit = self._calculate_criticality(c)
            comp = 1.0 / (1.0 + len(c)) # Simple complexity penalty
            metrics.append((e, crit, comp))
        
        for arch in architectures:
            w_e, w_c, w_x = arch
            scores = []
            for (e, crit, comp) in metrics:
                # Objective: Minimize Energy, Maximize Criticality
                # Score = -Energy + Criticality
                s = (-w_e * e) + (w_c * crit) - (w_x * comp)
                scores.append(s)
            
            # Heuristic for 'best' architecture: highest variance (separability) 
            # or highest mean score if we assume at least one good answer exists.
            # Here we use Mean + Variance to encourage distinct rankings.
            if len(scores) > 1:
                quality = np.mean(scores) + np.std(scores)
            else:
                quality = scores[0] if scores else 0
                
            if quality > best_score:
                best_score = quality
                best_weights = arch
                
        return best_weights

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # 1. NAS Phase: Determine optimal weighting for this prompt
        w_energy, w_crit, w_comp = self._nas_architecture_search(prompt, candidates)
        
        results = []
        for cand in candidates:
            # 2. Compute Components
            energy = self._calculate_free_energy(prompt, cand)
            criticality = self._calculate_criticality(cand)
            complexity = 1.0 / (1.0 + len(cand)) # Penalty for excessive length without content
            
            # 3. Final Score (Free Energy Minimization + Criticality Bonus)
            # Lower energy is better, Higher criticality is better
            raw_score = (-w_energy * energy) + (w_crit * criticality) - (w_comp * complexity)
            
            # Add small deterministic noise based on content to break ties consistently
            hash_noise = (hash(cand) % 1000) / 1e6 
            
            final_score = float(raw_score + hash_noise)
            
            # Generate reasoning string
            reason_parts = []
            if energy < 0.3: reason_parts.append("high consistency")
            if criticality > 0.3: reason_parts.append("logical structure detected")
            if not reason_parts: reason_parts.append("baseline match")
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"NAS-weighted evaluation: {', '.join(reason_parts)}. Energy={energy:.2f}, Criticality={criticality:.2f}"
            })
            
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        # Use the same mechanism to score the single answer relative to the prompt
        # Treat the answer as a candidate list of one, but we need a baseline.
        # We simulate a 'null' candidate to gauge relative energy.
        
        # Calculate raw metrics
        energy = self._calculate_free_energy(prompt, answer)
        criticality = self._calculate_criticality(answer)
        
        # Get weights for this prompt type (using a dummy candidate list for NAS stability)
        w_energy, w_crit, _ = self._nas_architecture_search(prompt, [answer, "No"])
        
        # Normalized score 0-1
        # Energy is 0-1 (lower better), Criticality 0-1 (higher better)
        # Score = (1 - Energy) * Weight + Criticality * Weight
        base_score = ((1.0 - energy) * w_energy) + (criticality * w_crit)
        
        # Clamp and smooth
        confidence = max(0.0, min(1.0, base_score))
        return float(confidence)