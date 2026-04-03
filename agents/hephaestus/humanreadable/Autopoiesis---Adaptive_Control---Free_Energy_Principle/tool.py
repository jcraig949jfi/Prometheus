from typing import Dict, Tuple

"""
Autopoietic Free Energy Reasoning Tool

Combines autopoiesis (self-maintaining belief states), adaptive control (online weight tuning),
and the Free Energy Principle (prediction error minimization) for multiple-choice reasoning.

Core mechanism:
1. Parse prompt/answers into symbolic graph with belief states
2. Compute free energy as prediction error between beliefs and candidate assertions
3. Adaptively tune feature weights based on error patterns
4. Constructively compute numeric, probabilistic, and temporal answers
5. Detect ambiguity and return low confidence on unanswerable questions
"""

import re
import numpy as np
from typing import List, Dict, Tuple
import zlib

class ReasoningTool:
    def __init__(self):
        # Adaptive weights for six feature types (sum to 1)
        self.weights = np.array([1.0, 1.0, 1.0, 1.0, 1.5, 1.0])  # [neg, cmp, cond, num, caus, ord]
        self.weights = self.weights / self.weights.sum()
        self.eta = 0.05  # Learning rate
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        # Constructive computation first
        computed = self._compute_answer(prompt, candidates)
        if computed is not None:
            return computed
        
        # Extract graph and beliefs from prompt
        prompt_graph = self._parse_to_graph(prompt)
        
        results = []
        errors_by_flag = np.zeros(6)
        
        for cand in candidates:
            cand_graph = self._parse_to_graph(cand)
            
            # Compute free energy
            fe, contradiction, flag_errors = self._compute_free_energy(prompt_graph, cand_graph)
            errors_by_flag += flag_errors
            
            # Score = -FE - contradiction_penalty
            score = -fe - (1000.0 if contradiction else 0.0)
            
            # Add small NCD component (max 10% influence)
            ncd = self._ncd(prompt, cand)
            score += (1.0 - ncd) * 0.5
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"FE={fe:.2f}, Contra={contradiction}, NCD={ncd:.3f}"
            })
        
        # Adaptive weight update
        if len(candidates) > 0:
            errors_by_flag /= len(candidates)
            self.weights *= (1.0 + self.eta * errors_by_flag)
            self.weights /= self.weights.sum()
        
        # Rank by score (higher is better)
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        # Meta-confidence checks for question quality
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        # Compute structural confidence
        prompt_graph = self._parse_to_graph(prompt)
        answer_graph = self._parse_to_graph(answer)
        
        fe, contradiction, _ = self._compute_free_energy(prompt_graph, answer_graph)
        
        if contradiction:
            return 0.1
        
        # Map FE to confidence (lower FE = higher confidence)
        # Typical FE range: 0-10
        base_conf = max(0.0, min(1.0, 1.0 - fe / 10.0))
        
        # Cap confidence based on meta_conf
        return min(base_conf, meta_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check prompt for ambiguity/unanswerability patterns"""
        p = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did.*fail|why did.*stop)\b', p):
            return 0.2
        
        # Scope ambiguity: "every X ... a Y"
        if re.search(r'\bevery\b.*\b(a|an)\b', p) and '?' in prompt:
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'\b(he|she|it|they)\b', p) and re.search(r'\bwho\b', p):
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither\b.*\bor\b', p) and not re.search(r'\bonly\b', p):
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prefer)\b', p) and not re.search(r'\b(most|least|highest|lowest)\b', p):
            return 0.3
        
        # Insufficient information
        if re.search(r'\b(not enough|insufficient|cannot determine|ambiguous)\b', p):
            return 0.2
        
        return 0.85  # Default: question seems answerable
    
    def _parse_to_graph(self, text: str) -> Dict:
        """Extract clauses with six feature flags"""
        flags = {
            'neg': bool(re.search(r'\b(not|no|never|none|neither)\b', text.lower())),
            'cmp': bool(re.search(r'\b(more|less|greater|smaller|er\b|as\s+\w+\s+as)\b', text.lower())),
            'cond': bool(re.search(r'\b(if|then|unless|provided|when|whenever)\b', text.lower())),
            'num': bool(re.search(r'\b\d+\.?\d*\b', text)),
            'caus': bool(re.search(r'\b(because|leads to|results in|causes|due to|therefore)\b', text.lower())),
            'ord': bool(re.search(r'\b(before|after|greater than|less than|earlier|later)\b', text.lower()))
        }
        
        # Extract numeric values
        numbers = [float(m.group()) for m in re.finditer(r'\b\d+\.?\d*\b', text)]
        
        return {'flags': flags, 'numbers': numbers, 'text': text}
    
    def _compute_free_energy(self, prompt_graph: Dict, answer_graph: Dict) -> Tuple[float, bool, np.ndarray]:
        """Compute prediction error between prompt beliefs and answer assertions"""
        p_flags = prompt_graph['flags']
        a_flags = answer_graph['flags']
        
        # Belief state: 0.5 = uncertain, 1.0 = true, 0.0 = false
        beliefs = np.array([0.5 if p_flags[k] else 0.3 for k in ['neg', 'cmp', 'cond', 'num', 'caus', 'ord']])
        likelihoods = np.array([1.0 if a_flags[k] else 0.0 for k in ['neg', 'cmp', 'cond', 'num', 'caus', 'ord']])
        
        # Squared prediction error weighted by adaptive weights
        errors = (beliefs - likelihoods) ** 2
        fe = np.sum(self.weights * errors)
        
        # Check contradiction (negation mismatch)
        contradiction = p_flags['neg'] != a_flags['neg'] and (p_flags['neg'] or a_flags['neg'])
        
        return fe, contradiction, errors
    
    def _compute_answer(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Constructive computation for numeric/probabilistic/temporal reasoning"""
        p = prompt.lower()
        
        # Numeric comparison
        num_match = re.search(r'(\d+\.?\d*)\s+(?:and|vs|or)\s+(\d+\.?\d*)', prompt)
        if num_match and any(kw in p for kw in ['greater', 'larger', 'bigger', 'smaller', 'less']):
            n1, n2 = float(num_match.group(1)), float(num_match.group(2))
            if 'greater' in p or 'larger' in p or 'bigger' in p:
                correct = str(max(n1, n2))
            else:
                correct = str(min(n1, n2))
            
            return [{"candidate": c, "score": 10.0 if correct in c else -10.0, 
                    "reasoning": f"Numeric: {n1} vs {n2}"} for c in candidates]
        
        # Bayesian reasoning
        if 'probability' in p or 'percent' in p or '%' in prompt:
            probs = [float(m.group()) for m in re.finditer(r'\b\d+\.?\d*(?=%|\s+percent)', prompt)]
            if len(probs) >= 2:
                # Simple base rate computation
                result = probs[0] * probs[1] / 100.0 if probs[1] > 0 else 0.0
                return [{"candidate": c, "score": 10.0 if str(int(result)) in c else -5.0,
                        "reasoning": f"Bayes: {result}"} for c in candidates]
        
        # Temporal ordering
        if re.search(r'\b(before|after|earlier|later)\b', p):
            # Extract time expressions
            times = re.findall(r'\b(\d{1,2}:\d{2}|\d{1,2}\s*(?:am|pm))\b', prompt.lower())
            if len(times) >= 2:
                return [{"candidate": c, "score": 5.0 if times[0] in c.lower() else -5.0,
                        "reasoning": f"Temporal: {times}"} for c in candidates]
        
        return None  # No computational match
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (minor tiebreaker only)"""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0