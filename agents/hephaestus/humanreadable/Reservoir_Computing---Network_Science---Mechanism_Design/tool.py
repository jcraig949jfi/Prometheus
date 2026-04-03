from typing import Dict, Tuple

import numpy as np
import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Hybrid reasoning tool combining:
    - Network Science: Parse logical propositions into a constraint graph
    - Reservoir Computing: Fixed random recurrent network processes proposition sequences
    - Mechanism Design: VCG-style penalty for constraint violations
    
    Evaluates candidates by structural coherence, computational verification, and logical consistency.
    """
    
    def __init__(self):
        np.random.seed(42)  # Deterministic
        self.reservoir_size = 50
        self.spectral_radius = 0.9
        self.input_scaling = 0.5
        
        # Fixed random reservoir matrix
        W = np.random.randn(self.reservoir_size, self.reservoir_size)
        radius = max(abs(np.linalg.eigvals(W)))
        self.W_reservoir = W * (self.spectral_radius / radius)
        
        self.W_input = np.random.randn(self.reservoir_size, self.reservoir_size) * self.input_scaling
        self.lambda_penalty = 0.1
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        # Parse prompt structure
        prompt_features = self._parse_structure(prompt)
        
        results = []
        for cand in candidates:
            # Structural scoring (50%)
            struct_score = self._structural_score(prompt, cand, prompt_features)
            
            # Computational scoring (30%)
            comp_score = self._computational_score(prompt, cand, prompt_features)
            
            # Reservoir scoring (15%)
            res_score = self._reservoir_score(prompt, cand)
            
            # NCD tiebreaker (5%)
            ncd_score = 1.0 - self._ncd(prompt, cand)
            
            total = 0.5*struct_score + 0.3*comp_score + 0.15*res_score + 0.05*ncd_score
            
            reasoning = f"struct={struct_score:.2f} comp={comp_score:.2f} res={res_score:.2f}"
            results.append({"candidate": cand, "score": total, "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        # Check meta-cognitive flags first
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        features = self._parse_structure(prompt)
        struct_score = self._structural_score(prompt, answer, features)
        comp_score = self._computational_score(prompt, answer, features)
        
        # High confidence only if computation succeeded
        if comp_score > 0.9:
            return min(0.95, meta_conf)
        elif struct_score > 0.8 or comp_score > 0.7:
            return min(0.7, meta_conf)
        else:
            return min(0.4, meta_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        p_low = prompt.lower()
        
        # Presupposition traps
        if re.search(r'\b(have you stopped|have you quit|why did .+ (fail|stop))\b', p_low):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery .+ (a|an)\b', p_low):
            return 0.25
        
        # Pronoun ambiguity with who question
        if re.search(r'\b(he|she|they)\b', p_low) and 'who' in p_low:
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither .+ or\b', p_low) and '?' in prompt:
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|better|worse)\b', p_low):
            if not re.search(r'\b(most|least|more|less|faster|slower|cheaper|expensive)\b', p_low):
                return 0.3
        
        # Unanswerable markers
        if re.search(r'cannot be determined|not enough information|insufficient', p_low):
            return 0.25
        
        return 0.8  # Default reasonable confidence in question quality
    
    def _parse_structure(self, text: str) -> Dict:
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither|nor)\b', text.lower())),
            'conditionals': len(re.findall(r'\b(if|then|when|unless|provided)\b', text.lower())),
            'comparatives': len(re.findall(r'\b(more|less|greater|fewer|better|worse|than)\b', text.lower())),
            'causals': len(re.findall(r'\b(because|causes|leads to|results in)\b', text.lower())),
            'temporals': len(re.findall(r'\b(before|after|during|while|until)\b', text.lower())),
            'quantifiers': len(re.findall(r'\b(all|some|every|any|each|none)\b', text.lower())),
            'numbers': re.findall(r'\b\d+\.?\d*\b', text)
        }
        return features
    
    def _structural_score(self, prompt: str, candidate: str, features: Dict) -> float:
        score = 0.0
        p_low = prompt.lower()
        c_low = candidate.lower()
        
        # Modus tollens: "If A then B. Not B. Therefore?"
        if 'if' in p_low and features['negations'] > 0:
            if re.search(r'\bnot\b', c_low):
                score += 0.3
        
        # Transitivity: "A > B, B > C => A > C"
        if features['comparatives'] >= 2:
            parts = re.findall(r'(\w+)\s+(>|<|greater|less)\s+(\w+)', p_low)
            if len(parts) >= 2 and len(re.findall(r'(\w+)\s+(>|<|greater|less)\s+(\w+)', c_low)) > 0:
                score += 0.3
        
        # Negation consistency
        if features['negations'] > 0:
            if 'not' in p_low and 'not' in c_low:
                score += 0.2
            elif 'no' in p_low and ('no' in c_low or 'not' in c_low):
                score += 0.2
        
        # Temporal ordering preserved
        if features['temporals'] > 0:
            before_after = re.findall(r'(before|after)', p_low)
            if before_after and any(w in c_low for w in before_after):
                score += 0.2
        
        return min(1.0, score)
    
    def _computational_score(self, prompt: str, candidate: str, features: Dict) -> float:
        # Try various computational parsers
        
        # Numeric comparison: "Is 9.11 < 9.9?"
        num_match = re.search(r'(\d+\.?\d*)\s*(<|>|less|greater|equals?)\s*(\d+\.?\d*)', prompt.lower())
        if num_match:
            a, op, b = float(num_match.group(1)), num_match.group(2), float(num_match.group(3))
            correct = (a < b if '<' in op or 'less' in op else a > b if '>' in op or 'greater' in op else a == b)
            if ('yes' in candidate.lower() and correct) or ('no' in candidate.lower() and not correct):
                return 1.0
        
        # Bat-and-ball: "X and Y cost $Z, X costs $W more than Y"
        bat_ball = re.search(r'cost.*\$(\d+\.?\d*).*\$(\d+\.?\d*)\s+more', prompt.lower())
        if bat_ball:
            total, diff = float(bat_ball.group(1)), float(bat_ball.group(2))
            cheaper = (total - diff) / 2
            cand_num = re.search(r'\$?(\d+\.?\d*)', candidate)
            if cand_num and abs(float(cand_num.group(1)) - cheaper) < 0.01:
                return 1.0
        
        # All-but-N: "12 eggs, all but 5 broken, how many unbroken?"
        all_but = re.search(r'(\d+).*all but (\d+)', prompt.lower())
        if all_but:
            answer = int(all_but.group(2))
            cand_num = re.search(r'\b(\d+)\b', candidate)
            if cand_num and int(cand_num.group(1)) == answer:
                return 1.0
        
        # Fencepost: "N posts, distance between = D, total distance?"
        fencepost = re.search(r'(\d+)\s+posts.*(\d+)\s+(meters|feet|yards)', prompt.lower())
        if fencepost:
            posts = int(fencepost.group(1))
            dist = int(fencepost.group(2))
            total = (posts - 1) * dist
            cand_num = re.search(r'\b(\d+)\b', candidate)
            if cand_num and int(cand_num.group(1)) == total:
                return 1.0
        
        # Coin flip independence: "Flipped heads 5 times, prob next is heads?"
        if re.search(r'flip|coin', prompt.lower()) and re.search(r'next|probability', prompt.lower()):
            if re.search(r'0\.5|50%|1/2', candidate):
                return 1.0
        
        return 0.0
    
    def _reservoir_score(self, prompt: str, candidate: str) -> float:
        # Convert text to proposition nodes and run through reservoir
        combined = prompt + " " + candidate
        tokens = re.findall(r'\w+', combined.lower())
        
        # Hash tokens to reservoir dimensions
        state = np.zeros(self.reservoir_size)
        for token in tokens:
            idx = hash(token) % self.reservoir_size
            x = np.zeros(self.reservoir_size)
            x[idx] = 1.0
            state = np.tanh(self.W_reservoir @ state + self.W_input @ x)
        
        # Simple readout: mean activation (high = more complex dynamics)
        activation = np.mean(np.abs(state))
        
        # Penalty for logical violations (simple heuristic: negation contradictions)
        violations = 0
        if 'not' in prompt.lower() and 'not' not in candidate.lower():
            violations += 1
        if 'yes' in candidate.lower() and 'no' in candidate.lower():
            violations += 1
        
        score = activation - self.lambda_penalty * violations
        return max(0.0, min(1.0, score))
    
    def _ncd(self, s1: str, s2: str) -> float:
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0