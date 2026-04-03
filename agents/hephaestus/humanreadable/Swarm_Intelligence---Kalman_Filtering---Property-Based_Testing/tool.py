from typing import Dict, Tuple

import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Swarm Intelligence x Kalman Filtering x Property-Based Testing
    
    Maintains a particle swarm where each particle represents a hypothesis about
    proposition truth values. Properties extracted from structure are tested against
    candidates via Kalman-like likelihood updates. Particle diversity (ESS) and
    trajectory convergence measure confidence.
    """
    
    def __init__(self, n_particles=50, n_iterations=5):
        self.n_particles = n_particles
        self.n_iterations = n_iterations
        np.random.seed(42)  # Deterministic
    
    def _parse_propositions(self, text: str) -> List[Dict]:
        """Extract structured propositions from text."""
        props = []
        
        # Negations
        for match in re.finditer(r'\b(not|never|no|n\'t)\s+(\w+)', text.lower()):
            props.append({'type': 'negation', 'value': match.group(2)})
        
        # Numeric comparisons
        for match in re.finditer(r'(\d+\.?\d*)\s*(>|<|>=|<=|equals?)\s*(\d+\.?\d*)', text):
            props.append({
                'type': 'numeric_cmp',
                'left': float(match.group(1)),
                'op': match.group(2),
                'right': float(match.group(3))
            })
        
        # Comparatives
        for match in re.finditer(r'(\w+)\s+(greater|less|more|fewer|better|worse)\s+than\s+(\w+)', text.lower()):
            props.append({'type': 'comparative', 'left': match.group(1), 'right': match.group(3)})
        
        # Conditionals
        for match in re.finditer(r'if\s+(.+?)\s+then\s+(.+?)[\.\?]', text.lower()):
            props.append({'type': 'conditional', 'premise': match.group(1), 'conclusion': match.group(2)})
        
        # Ordering
        for match in re.finditer(r'(before|after|first|last|earlier|later)', text.lower()):
            props.append({'type': 'ordering', 'marker': match.group(1)})
        
        return props
    
    def _evaluate_numeric_prop(self, prop: Dict, text: str) -> float:
        """Compute truth value of numeric proposition in text."""
        if prop['type'] == 'numeric_cmp':
            # Check if candidate contains matching comparison
            nums = re.findall(r'\d+\.?\d*', text)
            if len(nums) >= 2:
                left, right = float(nums[0]), float(nums[1])
                op = prop['op']
                if op in ['>', 'greater']: result = left > right
                elif op in ['<', 'less']: result = left < right
                elif op in ['>=']: result = left >= right
                elif op in ['<=']: result = left <= right
                elif op in ['=', 'equals', 'equal']: result = abs(left - right) < 0.001
                else: return 0.5
                
                # Compare with expected
                expected_result = False
                if prop['op'] == '>': expected_result = prop['left'] > prop['right']
                elif prop['op'] == '<': expected_result = prop['left'] < prop['right']
                elif prop['op'] == '>=': expected_result = prop['left'] >= prop['right']
                elif prop['op'] == '<=': expected_result = prop['left'] <= prop['right']
                
                return 1.0 if result == expected_result else 0.0
        return 0.5
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check for ambiguity/presupposition patterns (Tier B)."""
        prompt_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did.*fail|why did.*stop)', prompt_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery\b.*\ba\b', prompt_lower) and '?' in prompt:
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they).*\?', prompt_lower) and re.search(r'who|which', prompt_lower):
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither\s+\w+\s+or\s+\w+\b', prompt_lower) and not re.search(r'only|must', prompt_lower):
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prettiest|ugliest)\b', prompt_lower) and not re.search(r'(most|least|metric|measure)', prompt_lower):
            return 0.25
        
        # Unanswerable
        if re.search(r'(what is|who is|when did).*\?', prompt_lower) and len(prompt.split()) < 10:
            return 0.4
        
        return 1.0  # No meta issues detected
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
    
    def _trajectory_stability(self, states: np.ndarray) -> float:
        """Measure convergence of state trajectory."""
        if states.shape[0] < 2:
            return 0.5
        diffs = np.diff(states, axis=0)
        variance = np.mean(np.var(diffs, axis=0))
        stability = np.exp(-variance * 10)  # Higher stability = lower variance
        return float(stability)
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates using particle swarm with Kalman updates."""
        props = self._parse_propositions(prompt)
        
        if not props:
            # Fallback: use NCD only
            results = []
            for cand in candidates:
                ncd = 1.0 - self._ncd(prompt, cand)
                results.append({'candidate': cand, 'score': ncd * 0.5, 'reasoning': 'No structure; NCD fallback'})
            results.sort(key=lambda x: x['score'], reverse=True)
            return results
        
        results = []
        m = len(props)
        
        for cand in candidates:
            # Initialize swarm
            particles = np.random.normal(0.5, 0.3, (self.n_particles, m))
            particles = np.clip(particles, 0.01, 0.99)
            
            trajectory = [particles.mean(axis=0)]
            
            # Iterate: prediction + update
            for iteration in range(self.n_iterations):
                # Prediction: random walk
                particles += np.random.normal(0, 0.05, particles.shape)
                particles = np.clip(particles, 0.01, 0.99)
                
                # Update: compute likelihood weights
                weights = np.ones(self.n_particles)
                for i, prop in enumerate(props):
                    if prop['type'] == 'numeric_cmp':
                        observed = self._evaluate_numeric_prop(prop, cand)
                    elif prop['type'] == 'negation':
                        observed = 1.0 if prop['value'] not in cand.lower() else 0.0
                    elif prop['type'] == 'comparative':
                        observed = 0.7 if prop['left'] in cand.lower() else 0.3
                    elif prop['type'] == 'ordering':
                        observed = 0.6 if prop['marker'] in cand.lower() else 0.4
                    else:
                        observed = 0.5
                    
                    # Kalman-like likelihood
                    diff = particles[:, i] - observed
                    weights *= np.exp(-0.5 * diff**2 / 0.1)
                
                weights += 1e-10
                weights /= weights.sum()
                
                # Resample
                indices = np.random.choice(self.n_particles, self.n_particles, p=weights)
                particles = particles[indices]
                
                trajectory.append(particles.mean(axis=0))
            
            # Score computation
            ess = 1.0 / np.sum(weights**2) if np.sum(weights**2) > 0 else 1.0
            ess_norm = ess / self.n_particles
            
            stability = self._trajectory_stability(np.array(trajectory))
            
            # Mean posterior probability
            posterior = particles.mean()
            
            # Structural score
            structural = 0.5 * ess_norm + 0.3 * posterior + 0.2 * stability
            
            # NCD tiebreaker
            ncd_score = 1.0 - self._ncd(prompt, cand)
            
            # Final: 60% structural, 25% dynamics, 15% NCD
            final_score = 0.6 * structural + 0.25 * stability + 0.15 * ncd_score
            
            reasoning = f"ESS={ess_norm:.2f}, stability={stability:.2f}, posterior={posterior:.2f}"
            results.append({'candidate': cand, 'score': float(final_score), 'reasoning': reasoning})
        
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on question properties and answer consistency."""
        # Meta-confidence check (Tier B)
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.5:
            return meta_conf
        
        props = self._parse_propositions(prompt)
        
        if not props:
            # No structure parsed -> honest uncertainty
            return 0.25
        
        # Evaluate answer against properties
        m = len(props)
        particles = np.random.normal(0.5, 0.3, (self.n_particles, m))
        particles = np.clip(particles, 0.01, 0.99)
        
        trajectory = []
        
        for _ in range(self.n_iterations):
            particles += np.random.normal(0, 0.05, particles.shape)
            particles = np.clip(particles, 0.01, 0.99)
            
            weights = np.ones(self.n_particles)
            for i, prop in enumerate(props):
                if prop['type'] == 'numeric_cmp':
                    observed = self._evaluate_numeric_prop(prop, answer)
                elif prop['type'] == 'negation':
                    observed = 1.0 if prop['value'] not in answer.lower() else 0.0
                else:
                    observed = 0.5
                
                diff = particles[:, i] - observed
                weights *= np.exp(-0.5 * diff**2 / 0.1)
            
            weights += 1e-10
            weights /= weights.sum()
            
            indices = np.random.choice(self.n_particles, self.n_particles, p=weights)
            particles = particles[indices]
            trajectory.append(particles.mean())
        
        # Confidence from trajectory stability
        if len(trajectory) > 1:
            variance = np.var(trajectory)
            stability = np.exp(-variance * 5)
        else:
            stability = 0.5
        
        # Cap at 0.85 unless perfect numeric match
        conf = min(0.85, stability * meta_conf)
        
        return float(conf)