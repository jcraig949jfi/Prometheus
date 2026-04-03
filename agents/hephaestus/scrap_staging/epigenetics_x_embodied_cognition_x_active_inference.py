import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A reasoning tool combining Structural Parsing, Embodied Cognition features,
    and an Active Inference-inspired free energy scorer with an Epigenetic trace.
    
    Mechanism:
    1. Parses SVO triples and extracts logical factors (negation, conditional, causal).
    2. Constructs embodied feature vectors (concreteness, animacy, action) via regex heuristics.
    3. Uses an 'epigenetic' trace vector to modulate priors across the prompt context.
    4. Computes a Free Energy score based on constraint satisfaction (logical consistency)
       and entropy. Lower free energy = higher score.
    5. Falls back to NCD only if structural signals are weak.
    """
    
    def __init__(self):
        # Epigenetic trace vector (d=5): [action_class, concreteness, animacy, spatial, instrument]
        self.w = np.zeros(5)
        self.alpha = 0.7  # Methylation decay factor
        
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|nobody|nothing)\b', re.I),
            'conditional': re.compile(r'\b(if|provided|unless|then)\b', re.I),
            'causal': re.compile(r'\b(because|leads to|results in|causes|due to)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|fewer|better|worse|than)\b', re.I),
            'ordering': re.compile(r'\b(before|after|previously|subsequently|first|last)\b', re.I),
            'quantifier': re.compile(r'\b(all|some|none|every|each)\b', re.I),
            'number': re.compile(r'-?\d+\.?\d*'),
            'sv_triple': re.compile(r'(\w+)\s+(\w+)\s+(\w+)') # Simple Subject-Verb-Object
        }
        
        # Embodied cognition lookup (simplified heuristics)
        self.action_verbs = {'run', 'jump', 'eat', 'build', 'create', 'destroy', 'move', 'push', 'pull'}
        self.spatial_dirs = {'up', 'down', 'left', 'right', 'north', 'south', 'east', 'west', 'above', 'below'}

    def _extract_features(self, text: str) -> Tuple[np.ndarray, List[Dict]]:
        """Extract embodied features and logical factors from text."""
        text_lower = text.lower()
        
        # 1. Feature Vector Aggregation (Embodied Cognition)
        # d=5: [verb_action_class, noun_concreteness, animacy, spatial_hint, instrument_use]
        features = np.zeros(5)
        count = 0
        
        # Scan for SVO-like patterns to populate features
        for match in self.patterns['sv_triple'].finditer(text_lower):
            subj, verb, obj = match.groups()
            vec = np.zeros(5)
            
            # Verb action class (one-hot approx)
            if verb in self.action_verbs:
                vec[0] = 1.0
            
            # Noun concreteness (heuristic: length > 3 and not abstract-ish)
            if len(subj) > 3 and subj not in {'idea', 'thought', 'logic', 'time'}:
                vec[1] = 0.8
            
            # Animacy (heuristic: common pronouns or human-like nouns)
            if subj in {'he', 'she', 'they', 'man', 'woman', 'boy', 'girl', 'person'}:
                vec[2] = 1.0
                
            # Spatial hint
            if any(s in text_lower for s in self.spatial_dirs):
                vec[3] = 1.0
                
            # Instrument use (heuristic: 'with', 'using')
            if 'with' in text_lower or 'using' in text_lower:
                vec[4] = 1.0
                
            features += vec
            count += 1
            
        if count > 0:
            features /= count
        else:
            # Default fallback if no SVO found
            features = np.array([0.2, 0.5, 0.2, 0.0, 0.0])

        # 2. Logical Factors Extraction
        factors = []
        if self.patterns['negation'].search(text_lower): factors.append('negation')
        if self.patterns['conditional'].search(text_lower): factors.append('conditional')
        if self.patterns['causal'].search(text_lower): factors.append('causal')
        if self.patterns['comparative'].search(text_lower): factors.append('comparative')
        if self.patterns['ordering'].search(text_lower): factors.append('ordering')
        if self.patterns['quantifier'].search(text_lower): factors.append('quantifier')
        
        return features, factors

    def _update_epigenetic_trace(self, features: np.ndarray):
        """Update the persistent trace vector mimicking methylation decay."""
        # w <- alpha*w + (1-alpha)*features (simplified error gradient as features)
        self.w = self.alpha * self.w + (1 - self.alpha) * features

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Compute approximate Expected Free Energy (G).
        G = 0.5 * ||penalties||^2 - lambda * Entropy
        Score = -G
        """
        full_text = f"{prompt} {candidate}"
        features, factors = self._extract_features(full_text)
        
        # Update epigenetic state based on current context
        self._update_epigenetic_trace(features)
        
        # 1. Prior belief mu_0 = sigmoid(F . w)
        # Dot product of local features and global trace
        prior_logit = np.dot(features, self.w)
        mu = 1.0 / (1.0 + np.exp(-prior_logit)) # Sigmoid
        
        # 2. Constraint Penalties (Logical Consistency)
        penalties = []
        
        # Negation penalty: If negation exists, truth value should be inverted relative to prior expectation
        if 'negation' in factors:
            # Expectation: if mu is high, negation makes it low. 
            # Penalty if candidate implies high confidence without accounting for negation complexity
            # Simplified: Penalize if mu is close to 0.5 (uncertain) in presence of negation
            penalties.append((mu - 0.5) ** 2) 
            
        # Conditional/Comparative penalty: Enforce ordering logic
        if 'conditional' in factors or 'comparative' in factors:
            # Heuristic: Complex logic requires higher certainty to avoid entropy penalty
            # If features are weak but logic is strong, penalty increases
            if np.sum(features) < 1.0:
                penalties.append(0.5)
                
        # Causal penalty: Check for causal keywords implying directionality
        if 'causal' in factors:
            # Simple check: does candidate contain causal words if prompt does?
            p_has = bool(self.patterns['causal'].search(prompt.lower()))
            c_has = bool(self.patterns['causal'].search(candidate.lower()))
            if p_has and not c_has:
                penalties.append(0.3) # Mismatch penalty

        p_vec = np.array(penalties) if penalties else np.array([0.0])
        
        # 3. Entropy H(mu)
        epsilon = 1e-7
        mu_safe = np.clip(mu, epsilon, 1 - epsilon)
        H = -(mu_safe * np.log(mu_safe) + (1 - mu_safe) * np.log(1 - mu_safe))
        
        # 4. Free Energy G
        # Lambda balances risk vs exploration (set to 0.5 for balance)
        lam = 0.5
        G = 0.5 * np.sum(p_vec ** 2) - lam * H
        
        return -G  # Return Score (higher is better)

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Primary scoring based on structural parsing and numeric evaluation.
        Returns a score where higher is better.
        """
        score = 0.0
        p_low = prompt.lower()
        c_low = candidate.lower()
        
        # 1. Numeric Consistency
        p_nums = [float(x) for x in self.patterns['number'].findall(p_low)]
        c_nums = [float(x) for x in self.patterns['number'].findall(c_low)]
        
        if p_nums and c_nums:
            # Check if candidate numbers logically follow prompt numbers (simple equality or order)
            # If prompt has "9.11" and "9.9", and candidate says "9.11 < 9.9", check validity
            if len(p_nums) >= 2 and len(c_nums) >= 1:
                # Basic sanity: if candidate repeats a number from prompt, slight boost
                if any(abs(c - p) < 1e-6 for c in c_nums for p in p_nums):
                    score += 2.0
        
        # 2. Logical Keyword Matching (Constraint Propagation)
        # If prompt has "not", candidate should ideally reflect negation or contradiction handling
        if self.patterns['negation'].search(p_low):
            if self.patterns['negation'].search(c_low):
                score += 1.5 # Acknowledges negation
            else:
                score -= 1.0 # Ignores negation (potential trap)
                
        if self.patterns['conditional'].search(p_low):
            if any(k in c_low for k in ['if', 'then', 'otherwise', 'else']):
                score += 1.0
                
        # 3. Quantifier Check
        if self.patterns['quantifier'].search(p_low):
            if self.patterns['quantifier'].search(c_low):
                score += 1.0
                
        return score

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance. Lower is more similar."""
        z = zlib.compress
    len_s1 = len(z(s1.encode()))
        len_s2 = len(z(s2.encode()))
        len_both = len(z((s1 + s2).encode()))
        if len_both == 0: return 0.0
        return (len_both - min(len_s1, len_s2)) / max(len_s1, len_s2, 1)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Reset epigenetic trace for each new evaluation batch to avoid cross-contamination
        self.w = np.zeros(5)
        
        for cand in candidates:
            # 1. Structural Score (Primary Signal)
            struct_score = self._structural_score(prompt, cand)
            
            # 2. Active Inference / Free Energy Score (Secondary Signal)
            # Only run if structural score is neutral (tie-breaker) or to refine
            fi_score = self._compute_free_energy(prompt, cand)
            
            # 3. NCD (Tie breaker only)
            ncd_val = 0.0
            if abs(struct_score) < 0.1: 
                # If structural signal is weak, use NCD to check relevance
                ncd_val = -self._ncd_score(prompt, cand) # Negative because lower NCD is better
            
            # Combined Score: Structural dominates, FI refines, NCD breaks ties
            total_score = struct_score * 10.0 + fi_score * 2.0 + ncd_val
            
            # Generate reasoning string
            reasoning_parts = []
            if struct_score > 0: reasoning_parts.append("Structural alignment detected.")
            if struct_score < 0: reasoning_parts.append("Logical mismatch (e.g., ignored negation).")
            if fi_score > -0.5: reasoning_parts.append("Low free energy state.")
            if ncd_val != 0: reasoning_parts.append("Relevance confirmed via compression.")
            if not reasoning_parts: reasoning_parts.append("Baseline evaluation.")
            
            results.append({
                "candidate": cand,
                "score": float(total_score),
                "reasoning": " ".join(reasoning_parts)
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the internal scoring mechanism normalized to [0, 1].
        """
        # Evaluate single candidate against a dummy list to get score
        # We simulate a comparison with a known bad answer to normalize
        res = self.evaluate(prompt, [answer, "The opposite is true."])
        
        if not res:
            return 0.0
            
        top = res[0]
        score = top['score']
        
        # Map score to 0-1. 
        # Heuristic: Structural scores are usually > 1.0 for good matches, < 0 for bad.
        # Sigmoid mapping
        conf = 1.0 / (1.0 + np.exp(-score))
        return float(np.clip(conf, 0.0, 1.0))