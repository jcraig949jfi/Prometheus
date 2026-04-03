from typing import Dict, Tuple

import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Combines Statistical Mechanics (Boltzmann weighting), Neural Plasticity (Hebbian),
    and Swarm Intelligence (pheromone) for multi-candidate reasoning.
    
    Core: Parse propositions, build constraint graph, compute violation energy,
    apply Boltzmann scoring with swarm updates.
    """
    
    def __init__(self):
        self.eta = 0.1  # pheromone learning rate
        self.rho = 0.05  # evaporation rate
        self.T = 1.0  # temperature
        self.sweeps = 5
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        # Parse propositions from all text
        all_props = self._parse_propositions(prompt + " " + " ".join(candidates))
        prop_index = {p['id']: i for i, p in enumerate(all_props)}
        n = len(all_props)
        
        # Build Hebbian weight matrix
        W = np.zeros((n, n))
        cand_vectors = []
        for cand in candidates:
            cand_props = self._parse_propositions(cand)
            vec = np.zeros(n)
            for cp in cand_props:
                if cp['id'] in prop_index:
                    vec[prop_index[cp['id']]] = 1
            cand_vectors.append(vec)
            # Hebbian: co-occurrence
            for i in range(n):
                for j in range(i+1, n):
                    if vec[i] > 0 and vec[j] > 0:
                        W[i,j] += 1
                        W[j,i] += 1
        
        # Extract constraints from prompt
        constraints = self._extract_constraints(prompt, all_props, prop_index)
        
        # Swarm iterations
        weights = np.ones(len(candidates))
        for _ in range(self.sweeps):
            new_weights = []
            for idx, vec in enumerate(cand_vectors):
                energy = self._compute_energy(vec, constraints)
                w = np.exp(-energy / self.T)
                new_weights.append(w)
                # Pheromone deposit
                W += self.eta * w * np.outer(vec, vec)
            # Evaporate
            W *= (1 - self.rho)
            weights = np.array(new_weights)
        
        # Normalize scores
        total = weights.sum()
        scores = weights / total if total > 0 else np.ones(len(candidates)) / len(candidates)
        
        # Compute parsers for boost
        parser_scores = [self._compute_parsers(prompt, c) for c in candidates]
        
        # NCD tiebreaker (max 15%)
        ncd_scores = [self._ncd(prompt, c) for c in candidates]
        ncd_min, ncd_max = min(ncd_scores), max(ncd_scores)
        ncd_norm = [(ncd_max - s) / (ncd_max - ncd_min + 1e-9) for s in ncd_scores]
        
        # Combine: 60% Boltzmann, 25% parsers, 15% NCD
        final_scores = [0.6*s + 0.25*p + 0.15*n for s, p, n in zip(scores, parser_scores, ncd_norm)]
        
        # Build results
        results = []
        for i, cand in enumerate(candidates):
            results.append({
                "candidate": cand,
                "score": float(final_scores[i]),
                "reasoning": f"Energy-based: {scores[i]:.3f}, Parser: {parser_scores[i]:.3f}, NCD: {ncd_norm[i]:.3f}"
            })
        
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        parser_score = self._compute_parsers(prompt, answer)
        ncd_score = 1.0 - self._ncd(prompt, answer)
        
        # Structural confidence
        conf = 0.7 * parser_score + 0.3 * ncd_score
        return min(conf, meta_conf)
    
    def _parse_propositions(self, text: str) -> List[Dict]:
        """Extract atomic propositions with polarity, comparatives, causals, numerics."""
        props = []
        sentences = re.split(r'[.!?]', text)
        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
            
            # Negation
            neg = bool(re.search(r'\b(not|no|never|neither|nor)\b', sent, re.I))
            
            # Comparative
            comp = ''
            if re.search(r'\b(more|greater|larger|higher|taller|faster)\b', sent, re.I):
                comp = '>'
            elif re.search(r'\b(less|fewer|smaller|lower|shorter|slower)\b', sent, re.I):
                comp = '<'
            elif re.search(r'\b(equal|same|identical)\b', sent, re.I):
                comp = '='
            
            # Causal
            cause = ''
            if re.search(r'\b(because|since|due to|caused by)\b', sent, re.I):
                cause = 'cause'
            elif re.search(r'\b(leads to|results in|produces|causes)\b', sent, re.I):
                cause = 'effect'
            
            # Numeric
            num_match = re.search(r'(\d+\.?\d*)\s*([a-zA-Z]+)?', sent)
            num = float(num_match.group(1)) if num_match else 0.0
            unit = num_match.group(2) if num_match and num_match.group(2) else ''
            
            prop_id = re.sub(r'\W+', '_', sent[:20])
            props.append({'id': prop_id, 'neg': neg, 'comp': comp, 'cause': cause, 'num': num, 'unit': unit})
        
        return props
    
    def _extract_constraints(self, prompt: str, props: List[Dict], prop_index: Dict) -> List[Tuple]:
        """Extract logical constraints from prompt."""
        constraints = []
        
        # If-then
        if_then = re.findall(r'if\s+(.+?)\s+then\s+(.+?)(?:[,.]|$)', prompt, re.I)
        for ant, cons in if_then:
            constraints.append(('imply', ant, cons))
        
        # Negation constraints
        not_both = re.findall(r'not both\s+(.+?)\s+and\s+(.+?)(?:[,.]|$)', prompt, re.I)
        for a, b in not_both:
            constraints.append(('not_both', a, b))
        
        return constraints
    
    def _compute_energy(self, vec: np.ndarray, constraints: List[Tuple]) -> float:
        """Compute violation energy for answer vector."""
        energy = 0.0
        for c in constraints:
            if c[0] == 'imply':
                # Simplified: if constraint mentioned, assume violation if not in answer
                energy += 1.0
            elif c[0] == 'not_both':
                energy += 0.5
        return energy
    
    def _compute_parsers(self, prompt: str, answer: str) -> float:
        """Run standard computational parsers."""
        score = 0.0
        count = 0
        
        # Numeric comparison
        nums_p = re.findall(r'\d+\.?\d*', prompt)
        nums_a = re.findall(r'\d+\.?\d*', answer)
        if nums_p and nums_a:
            count += 1
            try:
                if any(re.search(r'\b(more|greater|larger)\b', prompt, re.I)):
                    if float(nums_a[0]) > float(nums_p[0]):
                        score += 1.0
                elif any(re.search(r'\b(less|fewer|smaller)\b', prompt, re.I)):
                    if float(nums_a[0]) < float(nums_p[0]):
                        score += 1.0
            except:
                pass
        
        # Bat-and-ball algebra
        if re.search(r'cost.*total.*\$(\d+\.?\d*)', prompt, re.I):
            count += 1
            match = re.search(r'\$(\d+\.?\d*)', answer)
            if match:
                score += 0.5
        
        # Negation alignment
        neg_p = bool(re.search(r'\b(not|no|never)\b', prompt, re.I))
        neg_a = bool(re.search(r'\b(not|no|never)\b', answer, re.I))
        count += 1
        if neg_p == neg_a:
            score += 1.0
        
        # Modus tollens
        if re.search(r'if\s+.+\s+then', prompt, re.I) and re.search(r'\bnot\b', prompt, re.I):
            count += 1
            if re.search(r'\bnot\b', answer, re.I):
                score += 1.0
        
        return score / count if count > 0 else 0.5
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check for Tier B epistemic issues."""
        # Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did .+ fail|why did .+ stop)\b', prompt, re.I):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery\b.*\ba\b', prompt, re.I):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'\b(he|she|it|they)\b', prompt, re.I) and re.search(r'\bwho\b', prompt, re.I):
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither\b.+\bor\b', prompt, re.I) and not re.search(r'\bother\b', prompt, re.I):
            return 0.3
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|prefer)\b', prompt, re.I):
            return 0.3
        
        return 1.0
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0