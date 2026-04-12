from typing import Dict, Tuple

import re
import numpy as np
from typing import List, Dict, Tuple
import zlib

class ReasoningTool:
    """
    Ecosystem-Embodied-Abductive Reasoner
    
    Combines three mechanisms:
    1. Ecosystem Dynamics: Causal propositions form a weighted flow network
    2. Embodied Cognition: Sensorimotor grounding scores weight edges
    3. Abductive Reasoning: Transitive closure generates explanatory hypotheses
    
    Core algorithm:
    - Parse text into SVO triples with structural markers (negation, causal cues, etc.)
    - Compute embodied grounding score from sensorimotor vocabulary
    - Build causal adjacency matrix weighted by grounding
    - Generate abductive hypotheses via matrix power convergence
    - Score candidates by incoming flow through their propositions
    """
    
    def __init__(self):
        self.sensorimotor_lexicon = set([
            'grasp', 'push', 'pull', 'move', 'walk', 'run', 'jump', 'see', 'hear', 
            'touch', 'feel', 'hold', 'lift', 'drop', 'throw', 'catch', 'up', 'down',
            'left', 'right', 'near', 'far', 'above', 'below', 'inside', 'outside',
            'open', 'close', 'turn', 'reach', 'point', 'look', 'listen', 'taste'
        ])
        self.causal_cues = ['because', 'leads to', 'results in', 'causes', 'due to', 'so', 'therefore']
    
    def _extract_propositions(self, text: str) -> List[Dict]:
        """Extract SVO triples with structural markers using regex."""
        text = text.lower()
        sentences = re.split(r'[.!?]', text)
        propositions = []
        
        for sent in sentences:
            if len(sent.strip()) < 3:
                continue
            
            # Check for negation
            polarity = -1 if re.search(r'\b(not|no|never|neither)\b', sent) else 1
            
            # Check for causal cues
            has_causal = any(cue in sent for cue in self.causal_cues)
            
            # Check for comparatives
            has_comparative = bool(re.search(r'\b(more|less|greater|smaller|better|worse)\s+than\b', sent))
            
            # Check for conditionals
            has_conditional = bool(re.search(r'\b(if|when|unless)\b.*\b(then|,)\b', sent))
            
            propositions.append({
                'text': sent.strip(),
                'polarity': polarity,
                'has_causal': has_causal,
                'has_comparative': has_comparative,
                'has_conditional': has_conditional,
                'grounding': self._compute_grounding(sent)
            })
        
        return propositions
    
    def _compute_grounding(self, text: str) -> float:
        """Compute embodied grounding score from sensorimotor vocabulary."""
        words = re.findall(r'\b[a-z]+\b', text.lower())
        if not words:
            return 0.0
        
        content_words = [w for w in words if len(w) > 2]
        if not content_words:
            return 0.0
        
        sensory_count = sum(1 for w in content_words if w in self.sensorimotor_lexicon)
        L = len(content_words)
        C = sensory_count
        
        # Check if verb is perception/motion
        motion_verbs = {'move', 'walk', 'run', 'jump', 'push', 'pull', 'grasp'}
        perception_verbs = {'see', 'hear', 'touch', 'feel', 'look', 'listen'}
        M = 1.0 if any(v in words for v in motion_verbs | perception_verbs) else 0.5
        
        return (C / L) * M if L > 0 else 0.0
    
    def _build_causal_matrix(self, props: List[Dict]) -> np.ndarray:
        """Build weighted causal adjacency matrix."""
        n = len(props)
        if n == 0:
            return np.zeros((1, 1))
        
        W = np.zeros((n, n), dtype=np.float64)
        
        for i, p_i in enumerate(props):
            if p_i['has_causal']:
                # Connect to propositions within sliding window
                for j in range(max(0, i-3), min(n, i+4)):
                    if i != j:
                        W[i, j] = p_i['grounding'] * props[j]['grounding']
        
        return W
    
    def _abductive_closure(self, W: np.ndarray) -> np.ndarray:
        """Generate abductive hypotheses via transitive closure."""
        n = W.shape[0]
        W_prev = W.copy()
        
        for iteration in range(10):  # Max 10 iterations
            W_next = W_prev @ W_prev
            W_next = np.clip(W_next, 0, 1)  # Keep in [0,1]
            
            if np.linalg.norm(W_next - W_prev, 'fro') < 1e-4:
                break
            
            # Add new hypothetical edges with decay
            W_prev = 0.7 * W_prev + 0.3 * W_next
        
        return W_prev
    
    def _compute_numeric(self, prompt: str, candidate: str) -> Tuple[bool, float]:
        """Parse and compute numeric comparisons."""
        # Extract numbers from prompt
        prompt_nums = re.findall(r'\d+\.?\d*', prompt)
        cand_nums = re.findall(r'\d+\.?\d*', candidate)
        
        if not cand_nums:
            return False, 0.0
        
        # Bat-and-ball style algebra
        if 'cost' in prompt.lower() and 'total' in prompt.lower():
            if len(prompt_nums) >= 2:
                total = float(prompt_nums[0])
                diff = float(prompt_nums[1])
                answer = (total - diff) / 2
                if cand_nums and abs(float(cand_nums[0]) - answer) < 0.01:
                    return True, 1.0
        
        # Numeric comparison: "9.11 vs 9.9"
        if any(w in prompt.lower() for w in ['larger', 'smaller', 'greater', 'less', 'more']):
            if len(prompt_nums) >= 2:
                a, b = float(prompt_nums[0]), float(prompt_nums[1])
                if 'larger' in prompt.lower() or 'greater' in prompt.lower():
                    correct = str(max(a, b))
                else:
                    correct = str(min(a, b))
                if any(correct in candidate for correct in [str(a), str(b)]):
                    return True, 0.8
        
        return False, 0.0
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check prompt for ambiguity markers that require low confidence."""
        prompt_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did .* (fail|stop))\b', prompt_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery\b.*\ba\b', prompt_lower) and '?' in prompt:
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they)\s+was', prompt_lower) and 'who' in prompt_lower:
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither\b.*\bor\b', prompt_lower) and not 'both' in prompt_lower:
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', prompt_lower):
            if not any(m in prompt_lower for m in ['criterion', 'measure', 'metric', 'by']):
                return 0.3
        
        # Unanswerable markers
        if any(phrase in prompt_lower for phrase in ['not enough information', 'cannot determine', 'insufficient']):
            return 0.2
        
        return 1.0  # No ambiguity detected
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Evaluate and rank candidates."""
        # Extract propositions from prompt
        prompt_props = self._extract_propositions(prompt)
        
        results = []
        for cand in candidates:
            # Try numeric computation first
            is_numeric, num_score = self._compute_numeric(prompt, cand)
            if is_numeric and num_score > 0.7:
                results.append({
                    'candidate': cand,
                    'score': num_score,
                    'reasoning': 'Numeric computation match'
                })
                continue
            
            # Extract candidate propositions
            cand_props = self._extract_propositions(cand)
            
            # Build and close causal matrix
            all_props = prompt_props + cand_props
            W = self._build_causal_matrix(all_props)
            W_closed = self._abductive_closure(W)
            
            # Compute incoming flow to candidate propositions
            n_prompt = len(prompt_props)
            if len(all_props) > n_prompt:
                cand_indices = list(range(n_prompt, len(all_props)))
                flow = np.sum(W_closed[:, cand_indices], axis=0)
                
                # Weight by polarity
                raw_score = 0.0
                for idx, prop_idx in enumerate(cand_indices):
                    raw_score += flow[idx] * all_props[prop_idx]['polarity']
                
                # Normalize
                max_flow = np.sum(W_closed) + 1e-6
                flow_score = (raw_score / max_flow + 1.0) / 2.0  # Map to [0,1]
            else:
                flow_score = 0.3
            
            # NCD tiebreaker (max 15% weight)
            ncd_score = 1.0 - self._ncd(prompt, cand)
            
            # Final score: 70% flow, 15% NCD, 15% grounding
            avg_grounding = np.mean([p['grounding'] for p in cand_props]) if cand_props else 0.0
            final_score = 0.7 * flow_score + 0.15 * ncd_score + 0.15 * avg_grounding
            
            results.append({
                'candidate': cand,
                'score': final_score,
                'reasoning': f'Flow={flow_score:.2f}, NCD={ncd_score:.2f}, Ground={avg_grounding:.2f}'
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence in answer given prompt."""
        # Check for prompt ambiguity first
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.5:
            return meta_conf
        
        # Try numeric computation
        is_numeric, num_score = self._compute_numeric(prompt, answer)
        if is_numeric:
            return min(0.95, num_score * meta_conf)
        
        # Use ecosystem flow model
        results = self.evaluate(prompt, [answer])
        if results:
            base_confidence = results[0]['score']
            # Cap at 0.85 unless we have numeric certainty
            return min(0.85, base_confidence * meta_conf)
        
        return 0.3  # Default low confidence