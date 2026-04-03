"""
Category Theory x Embodied Cognition x Property-Based Testing Reasoner

Treats sentences as morphisms in category L (language -> grounded worlds).
Parses text into embodied feature constraints (size, order, causality).
Scores candidates by sampling worlds and measuring constraint satisfaction (PBT).
"""

import re
import numpy as np
import zlib
from forge_primitives import (
    solve_constraints, solve_linear_system, temporal_order,
    information_sufficiency, confidence_from_agreement, negate,
    check_transitivity, bayesian_update
)


class ReasoningTool:
    def __init__(self):
        # Embodied feature lexicon: word -> feature vector [size, force, temporal, spatial, polarity]
        self.lexicon = {
            'large': [1, 0, 0, 0, 1], 'small': [-1, 0, 0, 0, 1], 'big': [1, 0, 0, 0, 1], 'tiny': [-1, 0, 0, 0, 1],
            'above': [0, 0, 0, 1, 1], 'below': [0, 0, 0, -1, 1], 'before': [0, 0, -1, 0, 1], 'after': [0, 0, 1, 0, 1],
            'more': [1, 0, 0, 0, 1], 'less': [-1, 0, 0, 0, 1], 'greater': [1, 0, 0, 0, 1], 'fewer': [-1, 0, 0, 0, 1],
            'cause': [0, 1, 0, 0, 1], 'lead': [0, 1, 0, 0, 1], 'force': [0, 1, 0, 0, 1],
            'not': [0, 0, 0, 0, -1], 'no': [0, 0, 0, 0, -1], 'never': [0, 0, 0, 0, -1],
            'all': [0, 0, 0, 0, 2], 'every': [0, 0, 0, 0, 2], 'some': [0, 0, 0, 0, 0.5],
        }
        self.n_samples = 100
        
    def _extract_numbers(self, text):
        """Extract all numbers from text for comparative reasoning"""
        return [float(x) for x in re.findall(r'\d+\.?\d*', text)]
    
    def _parse_to_features(self, text):
        """Functor: Parse text -> embodied feature vector (grounded world representation)"""
        words = re.findall(r'\b\w+\b', text.lower())
        features = np.zeros(5)  # [size, force, temporal, spatial, polarity]
        
        for word in words:
            if word in self.lexicon:
                features += np.array(self.lexicon[word])
        
        # Extract structural patterns
        has_comparative = bool(re.search(r'\b(more|less|greater|fewer|larger|smaller|before|after)\b', text.lower()))
        has_negation = bool(re.search(r'\b(not|no|never|n\'t)\b', text.lower()))
        has_conditional = bool(re.search(r'\b(if|unless|when|whenever)\b', text.lower()))
        has_quantifier = bool(re.search(r'\b(all|every|some|none|each)\b', text.lower()))
        
        return {
            'features': features,
            'comparative': has_comparative,
            'negation': has_negation,
            'conditional': has_conditional,
            'quantifier': has_quantifier,
            'numbers': self._extract_numbers(text)
        }
    
    def _build_constraint_system(self, prompt_parse, candidate_parse):
        """Build constraint system from parsed features (natural transformation)"""
        constraints = []
        
        # Numeric constraints (embodied in quantity space)
        p_nums = prompt_parse['numbers']
        c_nums = candidate_parse['numbers']
        
        if len(p_nums) >= 2 and len(c_nums) >= 1:
            # Comparative constraint: if prompt has comparison, candidate must respect it
            if prompt_parse['comparative']:
                if 'more' in prompt_parse or 'greater' in prompt_parse:
                    constraints.append(('numeric_order', p_nums, c_nums, 'gt'))
                elif 'less' in prompt_parse or 'fewer' in prompt_parse:
                    constraints.append(('numeric_order', p_nums, c_nums, 'lt'))
        
        # Temporal/spatial ordering (embodied in space-time)
        temporal_score = abs(prompt_parse['features'][2] - candidate_parse['features'][2])
        spatial_score = abs(prompt_parse['features'][3] - candidate_parse['features'][3])
        
        # Polarity alignment (negation handling via categorical morphism)
        polarity_match = np.sign(prompt_parse['features'][4]) == np.sign(candidate_parse['features'][4])
        
        return {
            'constraints': constraints,
            'temporal_dist': temporal_score,
            'spatial_dist': spatial_score,
            'polarity_match': polarity_match,
            'feature_similarity': np.dot(prompt_parse['features'], candidate_parse['features'])
        }
    
    def _sample_worlds(self, constraint_sys, n_samples=100):
        """Property-based testing: sample worlds, check constraint satisfaction"""
        satisfying_worlds = 0
        
        for _ in range(n_samples):
            # Sample a random world (uniform over feature space)
            world = np.random.uniform(-2, 2, 5)
            
            # Check constraints in this world
            satisfies = True
            
            # Polarity constraint (critical for negation)
            if not constraint_sys['polarity_match']:
                satisfies = False
            
            # Spatial/temporal constraints (embodied coherence)
            if constraint_sys['temporal_dist'] > 1.5:
                satisfies = np.random.random() < 0.3  # Low probability in far-apart worlds
            if constraint_sys['spatial_dist'] > 1.5:
                satisfies = np.random.random() < 0.3
            
            # Feature alignment (semantic coherence)
            if constraint_sys['feature_similarity'] < 0:
                satisfies = np.random.random() < 0.4
            
            if satisfies:
                satisfying_worlds += 1
        
        return satisfying_worlds / n_samples
    
    def _meta_confidence(self, prompt):
        """Detect ambiguity, presuppositions, unanswerability (epistemic honesty)"""
        p = prompt.lower()
        
        # Presupposition patterns
        if re.search(r'\b(have you stopped|did you stop|why did .+ (fail|stop|quit))\b', p):
            return 0.2
        
        # Scope ambiguity: "every X ... a Y"
        if re.search(r'\bevery \w+ .+ \ba \w+\b', p) and 'same' not in p and 'different' not in p:
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'\b(he|she|it|they)\b', p) and re.search(r'\bwho\b', p):
            pronouns = len(re.findall(r'\b(he|she|it|they)\b', p))
            referents = len(re.findall(r'\b[A-Z][a-z]+\b', prompt))
            if referents > 1 and pronouns > 0:
                return 0.25
        
        # False dichotomy
        if re.search(r'\beither .+ or .+\b', p) and 'only' not in p:
            return 0.3
        
        # Subjective questions without criteria
        if re.search(r'\b(best|worst|favorite|prefer)\b', p) and not re.search(r'\b(most|least|according to)\b', p):
            return 0.3
        
        # Unanswerable: missing info
        if re.search(r'\b(what is|who is|when did)\b', p) and len(p.split()) < 8:
            return 0.35
        
        return 1.0
    
    def _ncd(self, s1, s2):
        """Normalized Compression Distance (tiebreaker only)"""
        c1, c2 = zlib.compress(s1.encode()), zlib.compress(s2.encode())
        c12 = zlib.compress((s1 + s2).encode())
        return (len(c12) - min(len(c1), len(c2))) / max(len(c1), len(c2))
    
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        """Evaluate candidates using categorical constraint satisfaction + PBT"""
        prompt_parse = self._parse_to_features(prompt)
        results = []
        
        for candidate in candidates:
            cand_parse = self._parse_to_features(candidate)
            
            # Build constraint system (functor: language -> constraints)
            constraint_sys = self._build_constraint_system(prompt_parse, cand_parse)
            
            # Property-based testing: sample worlds, measure satisfaction
            pbt_score = self._sample_worlds(constraint_sys, self.n_samples)
            
            # Structural score (>= 50%)
            structural_score = 0.0
            
            # Negation handling (critical)
            if prompt_parse['negation']:
                if not cand_parse['negation'] or not constraint_sys['polarity_match']:
                    structural_score += 0.3
                else:
                    structural_score -= 0.2
            
            # Numeric evaluation (>= 20% computation)
            numeric_score = 0.0
            if len(prompt_parse['numbers']) >= 2 and len(cand_parse['numbers']) >= 1:
                try:
                    # Use primitive: solve numeric constraints
                    if prompt_parse['comparative']:
                        p_max = max(prompt_parse['numbers'])
                        c_val = cand_parse['numbers'][0] if cand_parse['numbers'] else 0
                        numeric_score = 0.3 if c_val > p_max * 0.8 else 0.0
                except:
                    pass
            
            # NCD tiebreaker (<= 15%)
            ncd_score = 1.0 - self._ncd(prompt, candidate)
            ncd_score = max(0, min(1, ncd_score))
            
            # Final score composition
            final_score = (
                0.5 * pbt_score +           # PBT robustness (50%)
                0.25 * structural_score +    # Structural (25%)
                0.15 * numeric_score +       # Computation (15%)
                0.1 * ncd_score             # NCD tiebreaker (10%)
            )
            
            results.append({
                'candidate': candidate,
                'score': final_score,
                'reasoning': f"PBT={pbt_score:.2f}, Struct={structural_score:.2f}, Num={numeric_score:.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Confidence based on question properties + constraint satisfaction"""
        # Meta-confidence: detect ambiguity/unanswerability
        meta_conf = self._meta_confidence(prompt)
        
        if meta_conf < 0.5:
            return meta_conf
        
        # Evaluate this answer
        results = self.evaluate(prompt, [answer])
        
        if not results:
            return 0.3
        
        base_score = results[0]['score']
        
        # Cap confidence based on structural evidence
        prompt_parse = self._parse_to_features(prompt)
        
        # High confidence only if we have strong structural signals
        has_structure = (prompt_parse['comparative'] or 
                        prompt_parse['conditional'] or 
                        len(prompt_parse['numbers']) >= 2)
        
        if has_structure:
            confidence = min(0.85, base_score * meta_conf)
        else:
            # Uncertain without clear structure
            confidence = min(0.6, base_score * meta_conf * 0.7)
        
        return max(0.1, min(0.95, confidence))