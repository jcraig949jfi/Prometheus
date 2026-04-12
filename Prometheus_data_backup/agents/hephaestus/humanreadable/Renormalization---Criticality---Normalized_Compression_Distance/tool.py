from typing import Dict, Tuple

import re
import zlib
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Combines Renormalization Group coarse-graining, Criticality analysis,
    and Normalized Compression Distance with constructive computation.
    
    Core mechanism:
    1. Parse structural features (negations, comparatives, conditionals, numerics)
    2. Compute answers via Bayesian reasoning, arithmetic, temporal logic
    3. Apply RG coarse-graining at multiple scales
    4. Calculate NCD and susceptibility chi at each scale
    5. Score = computation_match * structural_match * exp(-NCD_mean) * (1+chi/(chi+1))
    """
    
    def __init__(self):
        self.R = 3  # Number of RG scales
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            comp_score = self._compute_score(prompt, cand)
            struct_score = self._structural_score(prompt, cand)
            ncd_score, chi = self._rg_ncd_criticality(prompt, cand)
            
            # Weight: 40% computation, 40% structural, 20% NCD+criticality
            score = 0.4 * comp_score + 0.4 * struct_score + 0.2 * ncd_score
            
            reasoning = f"Comp:{comp_score:.2f} Struct:{struct_score:.2f} NCD:{ncd_score:.2f} Chi:{chi:.3f}"
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        candidates = [answer]
        results = self.evaluate(prompt, candidates)
        score = results[0]["score"] if results else 0.5
        
        # Cap confidence based on meta-analysis
        return min(score, meta_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        p_lower = prompt.lower()
        
        # Presupposition detection
        presup_patterns = [r'have you (stopped|quit)', r'why did.*fail', r'when did.*stop']
        if any(re.search(pat, p_lower) for pat in presup_patterns):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'every.*\b(a|an)\b', p_lower):
            return 0.25
        
        # Pronoun ambiguity with "who" question
        if re.search(r'(he|she).*who', p_lower) or re.search(r'who.*(he|she)', p_lower):
            return 0.25
        
        # False dichotomy
        if re.search(r'either.*or', p_lower) and 'only' not in p_lower:
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prefer)\b', p_lower):
            if not re.search(r'\b(most|least|highest|lowest|measure)\b', p_lower):
                return 0.25
        
        # Insufficient information
        if re.search(r'(not enough|insufficient|cannot determine|ambiguous)', p_lower):
            return 0.2
        
        return 0.95
    
    def _compute_score(self, prompt: str, candidate: str) -> float:
        score = 0.0
        
        # Numeric comparison
        num_score = self._numeric_computation(prompt, candidate)
        if num_score > 0:
            return num_score
        
        # Bayesian reasoning
        bayes_score = self._bayesian_computation(prompt, candidate)
        if bayes_score > 0:
            return bayes_score
        
        # Temporal ordering
        temp_score = self._temporal_computation(prompt, candidate)
        if temp_score > 0:
            return temp_score
        
        # Arithmetic expressions
        arith_score = self._arithmetic_computation(prompt, candidate)
        if arith_score > 0:
            return arith_score
        
        return 0.3  # Low default if no computation pathway matches
    
    def _numeric_computation(self, prompt: str, candidate: str) -> float:
        # Extract numbers and compare
        p_nums = [float(x) for x in re.findall(r'\d+\.?\d*', prompt)]
        c_nums = [float(x) for x in re.findall(r'\d+\.?\d*', candidate)]
        
        if len(p_nums) >= 2 and len(c_nums) >= 1:
            if re.search(r'(greater|larger|more|higher)', prompt.lower()):
                expected = max(p_nums)
                if any(abs(cn - expected) < 0.01 for cn in c_nums):
                    return 0.95
            elif re.search(r'(less|smaller|fewer|lower)', prompt.lower()):
                expected = min(p_nums)
                if any(abs(cn - expected) < 0.01 for cn in c_nums):
                    return 0.95
        
        return 0.0
    
    def _bayesian_computation(self, prompt: str, candidate: str) -> float:
        # Detect Bayesian questions
        if not re.search(r'(probability|likely|chance|given)', prompt.lower()):
            return 0.0
        
        # Extract fractions/percentages
        fracs = re.findall(r'(\d+)/(\d+)', prompt)
        percs = re.findall(r'(\d+)%', prompt)
        
        if fracs and len(fracs) >= 2:
            # Simple base rate problem: P(A|B) = P(B|A)*P(A)/P(B)
            try:
                vals = [float(n)/float(d) for n, d in fracs[:3]]
                if len(vals) >= 2:
                    # Heuristic Bayesian posterior
                    posterior = vals[0] * vals[1] / (vals[0] * vals[1] + (1-vals[1]) * (1-vals[0]))
                    c_nums = [float(x) for x in re.findall(r'\d+\.?\d*', candidate)]
                    if c_nums and abs(c_nums[0] - posterior * 100) < 5:
                        return 0.9
            except:
                pass
        
        return 0.0
    
    def _temporal_computation(self, prompt: str, candidate: str) -> float:
        # Detect temporal ordering
        temporal_words = ['before', 'after', 'first', 'then', 'next', 'finally']
        if not any(w in prompt.lower() for w in temporal_words):
            return 0.0
        
        # Extract order from prompt and candidate
        p_order = re.findall(r'([A-Z][a-z]+|[A-Z])\s+(before|after|then)', prompt)
        c_order = re.findall(r'([A-Z][a-z]+|[A-Z])', candidate)
        
        if p_order and c_order:
            # Simple ordering check
            return 0.7
        
        return 0.0
    
    def _arithmetic_computation(self, prompt: str, candidate: str) -> float:
        # Detect arithmetic expressions
        if not re.search(r'[\+\-\*/]', prompt):
            return 0.0
        
        try:
            # Extract simple expression
            expr = re.search(r'(\d+)\s*([+\-*/])\s*(\d+)', prompt)
            if expr:
                a, op, b = float(expr.group(1)), expr.group(2), float(expr.group(3))
                result = {'+'
: a+b, '-': a-b, '*': a*b, '/': a/b if b!=0 else 0}[op]
                c_nums = [float(x) for x in re.findall(r'\d+\.?\d*', candidate)]
                if c_nums and abs(c_nums[0] - result) < 0.01:
                    return 0.95
        except:
            pass
        
        return 0.0
    
    def _structural_score(self, prompt: str, candidate: str) -> float:
        p_atoms = self._parse_atoms(prompt)
        c_atoms = self._parse_atoms(candidate)
        
        if not p_atoms:
            return 0.5
        
        # Match atoms
        matches = sum(1 for pa in p_atoms if any(self._atom_match(pa, ca) for ca in c_atoms))
        return matches / len(p_atoms) if p_atoms else 0.5
    
    def _parse_atoms(self, text: str) -> List[Tuple]:
        atoms = []
        t_lower = text.lower()
        
        # Negations
        if re.search(r'\b(not|no|n\'t)\b', t_lower):
            atoms.append(('neg',))
        
        # Comparatives
        for match in re.finditer(r'(\w+)\s+(greater|less|more|fewer)\s+than\s+(\w+)', t_lower):
            atoms.append(('cmp', match.group(1), match.group(2), match.group(3)))
        
        # Conditionals
        for match in re.finditer(r'if\s+(.+?)\s+then\s+(.+)', t_lower):
            atoms.append(('cond', match.group(1).strip(), match.group(2).strip()))
        
        # Causal
        for match in re.finditer(r'(\w+)\s+(cause|lead|result)\s+(\w+)', t_lower):
            atoms.append(('causal', match.group(1), match.group(3)))
        
        # Numbers
        for num in re.findall(r'\d+\.?\d*', text):
            atoms.append(('num', float(num)))
        
        return atoms
    
    def _atom_match(self, a1: Tuple, a2: Tuple) -> bool:
        if a1[0] != a2[0]:
            return False
        if a1[0] == 'num':
            return abs(a1[1] - a2[1]) < 0.01
        return a1 == a2
    
    def _rg_ncd_criticality(self, prompt: str, candidate: str) -> Tuple[float, float]:
        # Multi-scale RG coarse-graining
        p_scales = self._rg_coarsen(prompt.encode('utf-8'))
        c_scales = self._rg_coarsen(candidate.encode('utf-8'))
        
        # Compute NCD at each scale
        ncds = []
        for r in range(min(len(p_scales), len(c_scales))):
            ncd = self._ncd(p_scales[r], c_scales[r])
            ncds.append(ncd)
        
        if not ncds:
            return 0.5, 0.0
        
        ncd_array = np.array(ncds)
        mean_ncd = np.mean(ncd_array)
        
        # Susceptibility chi
        if len(ncd_array) > 1:
            chi = np.var(np.diff(ncd_array))
        else:
            chi = 0.0
        
        # Score combining NCD and criticality
        score = np.exp(-mean_ncd) * (1 + chi / (chi + 1))
        
        return score, chi
    
    def _rg_coarsen(self, data: bytes) -> List[bytes]:
        scales = [data]
        current = data.decode('utf-8', errors='ignore')
        
        for _ in range(self.R):
            # Replace most frequent bigram with a symbol
            bigrams = {}
            for i in range(len(current) - 1):
                bg = current[i:i+2]
                bigrams[bg] = bigrams.get(bg, 0) + 1
            
            if not bigrams:
                break
            
            most_common = max(bigrams, key=bigrams.get)
            current = current.replace(most_common, '#')
            scales.append(current.encode('utf-8', errors='ignore'))
        
        return scales
    
    def _ncd(self, a: bytes, b: bytes) -> float:
        ca = len(zlib.compress(a))
        cb = len(zlib.compress(b))
        cab = len(zlib.compress(a + b))
        
        if max(ca, cb) == 0:
            return 0.0
        
        return (cab - min(ca, cb)) / max(ca, cb)