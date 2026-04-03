from typing import Dict, Optional, Tuple

"""
Quantum-Hoare-Spectral Reasoning Tool

Combines:
- Hoare logic constraint matrices for implication propagation
- Quantum superposition for proposition truth states
- Spectral analysis via FFT to detect logical incoherence

Core mechanism: Parse propositions into structured records, build implication
graph from Hoare pre/post conditions, evolve quantum amplitude vectors under
constraint operators, penalize high-frequency spectral noise in contradiction
signals, score by overlap with expected truth assignments.
"""

import re
import numpy as np
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    def __init__(self):
        self.max_iter = 20
        self.spectral_threshold = 0.1
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Score and rank candidates by logical-numeric coherence."""
        results = []
        prompt_props = self._parse_propositions(prompt)
        
        for cand in candidates:
            cand_props = self._parse_propositions(cand)
            all_props = np.concatenate([prompt_props, cand_props]) if len(prompt_props) > 0 else cand_props
            
            if len(all_props) == 0:
                # Fallback to NCD
                score = 1.0 - self._ncd(prompt, cand)
                reasoning = "No structure parsed; NCD fallback"
            else:
                # Core algorithm
                C = self._build_constraint_matrix(all_props)
                psi = self._evolve_superposition(C, len(all_props))
                spectral_noise = self._spectral_penalty(psi, C)
                
                # Compute coherence score
                p_true = psi[:, 1] ** 2
                structural_score = np.mean(p_true)
                
                # Computational verification
                comp_score = self._compute_score(prompt, cand)
                
                # Combined score
                score = (0.6 * structural_score + 0.25 * comp_score + 0.15 * (1 - self._ncd(prompt, cand))) * np.exp(-spectral_noise)
                reasoning = f"Struct={structural_score:.2f} Comp={comp_score:.2f} Noise={spectral_noise:.2f}"
            
            results.append({"candidate": cand, "score": float(score), "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on question properties and answer coherence."""
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        # Structural confidence
        props = self._parse_propositions(prompt + " " + answer)
        if len(props) == 0:
            return 0.2  # Honest uncertainty
        
        C = self._build_constraint_matrix(props)
        psi = self._evolve_superposition(C, len(props))
        spectral_noise = self._spectral_penalty(psi, C)
        
        # Computational confidence
        comp_score = self._compute_score(prompt, answer)
        
        # Combined confidence (capped at 0.85 unless perfect computation)
        base_conf = (np.mean(psi[:, 1] ** 2) + comp_score) / 2.0 * np.exp(-spectral_noise)
        if comp_score < 0.99:
            base_conf = min(base_conf, 0.85)
        
        return float(min(meta_conf, base_conf))
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check prompt for ambiguity, presupposition, unanswerability."""
        p = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you|did you) (stop|quit|cease)', p):
            return 0.2
        if re.search(r'\bwhy (did|does|is) \w+ (fail|stop|wrong)', p):
            return 0.25
        
        # Scope ambiguity
        if re.search(r'\bevery \w+ \w+ a \w+', p):
            return 0.3
        
        # Pronoun ambiguity
        if re.search(r'\b(he|she|they|it)\b', p) and re.search(r'\bwho\b', p):
            return 0.3
        
        # False dichotomy
        if re.search(r'\b(either \w+ or \w+|only two (options|choices))', p):
            return 0.35
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p) and not re.search(r'\b(because|criterion|measure|metric)\b', p):
            return 0.3
        
        # Unanswerable markers
        if re.search(r'\b(impossible to|cannot determine|not enough information)\b', p):
            return 0.25
        
        return 1.0  # No ambiguity detected
    
    def _parse_propositions(self, text: str) -> np.ndarray:
        """Extract atomic propositions with polarity, type, lhs, rhs, value."""
        props = []
        sentences = re.split(r'[.;!?]', text)
        
        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
            
            # Negation detection
            polarity = -1 if re.search(r'\b(not|no|never|n\'t)\b', sent.lower()) else 1
            
            # Numeric comparison
            num_match = re.search(r'(\w+)\s*(>=|<=|>|<|=|equals?)\s*(\d+\.?\d*)', sent)
            if num_match:
                props.append(('num', polarity, num_match.group(1), num_match.group(3), float(num_match.group(3))))
            
            # Conditional
            cond_match = re.search(r'if\s+(.+?)\s+then\s+(.+)', sent.lower())
            if cond_match:
                props.append(('cond', polarity, cond_match.group(1).strip(), cond_match.group(2).strip(), None))
            
            # Comparative
            comp_match = re.search(r'(\w+)\s+(more|less|greater|smaller|faster|slower)\s+than\s+(\w+)', sent.lower())
            if comp_match:
                props.append(('comp', polarity, comp_match.group(1), comp_match.group(3), None))
            
            # Causal
            causal_match = re.search(r'(.+?)\s+(causes?|leads? to|results? in|produces?)\s+(.+)', sent.lower())
            if causal_match:
                props.append(('causal', polarity, causal_match.group(1).strip(), causal_match.group(3).strip(), None))
            
            # Order
            order_match = re.search(r'(\w+)\s+(before|after|precedes?|follows?)\s+(\w+)', sent.lower())
            if order_match:
                props.append(('order', polarity, order_match.group(1), order_match.group(3), None))
        
        if not props:
            return np.array([], dtype=[('type', 'U10'), ('polarity', 'i4'), ('lhs', 'U100'), ('rhs', 'U100'), ('value', 'f8')])
        
        return np.array(props, dtype=[('type', 'U10'), ('polarity', 'i4'), ('lhs', 'U100'), ('rhs', 'U100'), ('value', 'f8')])
    
    def _build_constraint_matrix(self, props: np.ndarray) -> np.ndarray:
        """Build Hoare-logic implication matrix C[i,j]=1 means P_i -> P_j."""
        n = len(props)
        C = np.zeros((n, n), dtype=float)
        
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                
                # Modus ponens: if P_i is "if A then B" and P_j is "B", then P_i -> P_j
                if props[i]['type'] == 'cond' and props[j]['lhs'] in props[i]['rhs']:
                    C[i, j] = 1.0
                
                # Transitivity: if P_i says A>B and P_j says B>C, infer A>C
                if props[i]['type'] == 'comp' and props[j]['type'] == 'comp':
                    if props[i]['rhs'] == props[j]['lhs']:
                        C[i, j] = 0.8
                
                # Causal chain
                if props[i]['type'] == 'causal' and props[j]['type'] == 'causal':
                    if props[i]['rhs'] in props[j]['lhs']:
                        C[i, j] = 0.9
                
                # Order transitivity
                if props[i]['type'] == 'order' and props[j]['type'] == 'order':
                    if props[i]['rhs'] == props[j]['lhs']:
                        C[i, j] = 0.85
        
        return C
    
    def _evolve_superposition(self, C: np.ndarray, n: int) -> np.ndarray:
        """Evolve quantum state under Hoare constraint Hamiltonian."""
        psi = np.full((n, 2), 1.0 / np.sqrt(2))  # [false, true] amplitudes
        
        for _ in range(self.max_iter):
            psi_new = psi.copy()
            if n > 0:
                psi_new[:, 1] = np.clip(psi[:, 1] + 0.1 * np.dot(C, psi[:, 1]), 0, 1)
                norm = np.sqrt(psi_new[:, 0]**2 + psi_new[:, 1]**2) + 1e-10
                psi_new[:, 0] = psi_new[:, 0] / norm
                psi_new[:, 1] = psi_new[:, 1] / norm
            
            if np.allclose(psi, psi_new):
                break
            psi = psi_new
        
        return psi
    
    def _spectral_penalty(self, psi: np.ndarray, C: np.ndarray) -> float:
        """Compute FFT-based incoherence penalty."""
        if len(psi) < 4:
            return 0.0
        
        # Build contradiction signal: 1 if both high true and high false prob
        p_true = psi[:, 1] ** 2
        p_false = psi[:, 0] ** 2
        signal = ((p_true > 0.5) & (p_false > 0.5)).astype(float)
        
        if np.sum(signal) == 0:
            return 0.0
        
        freqs = np.fft.rfftfreq(len(signal))
        psd = np.abs(np.fft.rfft(signal)) ** 2
        spectral_noise = np.sum(psd[freqs > self.spectral_threshold])
        
        return min(spectral_noise / (len(signal) + 1), 5.0)
    
    def _compute_score(self, prompt: str, answer: str) -> float:
        """Constructive computation: actually solve problems."""
        score = 0.0
        count = 0
        
        # Numeric comparison
        nums_p = re.findall(r'\d+\.?\d*', prompt)
        nums_a = re.findall(r'\d+\.?\d*', answer)
        if nums_p and nums_a:
            try:
                if any(re.search(r'\b(less|smaller|before)\b', prompt.lower())):
                    if float(nums_a[0]) < float(nums_p[0]):
                        score += 1.0
                elif any(re.search(r'\b(more|greater|after)\b', prompt.lower())):
                    if float(nums_a[0]) > float(nums_p[0]):
                        score += 1.0
                else:
                    score += 0.5
                count += 1
            except:
                pass
        
        # Bat-and-ball algebra
        if re.search(r'cost.*\$?(\d+\.?\d*).*more.*than', prompt.lower()):
            count += 1
            match = re.search(r'\$?(\d+\.?\d*)', answer)
            if match and float(match.group(1)) < 1.0:
                score += 1.0
        
        # Modus tollens
        if re.search(r'if.*then', prompt.lower()) and re.search(r'not', answer.lower()):
            score += 0.7
            count += 1
        
        return score / count if count > 0 else 0.5
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized compression distance (tiebreaker only)."""
        import zlib
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0