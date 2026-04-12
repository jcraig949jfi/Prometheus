from typing import Dict, Set, Tuple

import re
import zlib
import numpy as np
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    """
    Typed Entailment Category with Prime Encoding + Hoare Logic
    
    Atomic propositions -> primes via hash. Conjunctions -> products.
    Horn rules form category morphisms. Forward chain for closure,
    backward chain for wp. Score via Jaccard(wp, prompt_closure).
    """
    
    def __init__(self):
        self.primes = self._generate_primes(10000)
        self.prop_to_prime = {}
        self.prime_counter = 0
        
    def _generate_primes(self, n):
        """Sieve of Eratosthenes"""
        sieve = np.ones(n, dtype=bool)
        sieve[:2] = False
        for i in range(2, int(n**0.5) + 1):
            if sieve[i]:
                sieve[i*i::i] = False
        return np.nonzero(sieve)[0]
    
    def _get_prime(self, prop: str) -> int:
        """Map proposition to unique prime"""
        if prop not in self.prop_to_prime:
            self.prop_to_prime[prop] = int(self.primes[self.prime_counter])
            self.prime_counter += 1
        return self.prop_to_prime[prop]
    
    def _parse_text(self, text: str) -> Tuple[Set[str], List[Tuple[str, str]]]:
        """Extract atomic propositions and Horn rules"""
        text = text.lower()
        atoms = set()
        rules = []
        
        # Numeric comparisons
        for m in re.finditer(r'(\w+)\s*(>|<|>=|<=|=|equals?)\s*(\d+\.?\d*)', text):
            prop = f"{m.group(1)}{m.group(2)}{m.group(3)}"
            atoms.add(prop)
        
        # Conditionals: if A then B
        for m in re.finditer(r'if\s+(.+?)\s+then\s+(.+?)(?:\.|,|;|$)', text):
            ant = m.group(1).strip()
            cons = m.group(2).strip()
            atoms.add(ant)
            atoms.add(cons)
            rules.append((ant, cons))
        
        # Negations
        for m in re.finditer(r'(not|no|never)\s+(\w+)', text):
            prop = f"not_{m.group(2)}"
            atoms.add(prop)
        
        # Causal: X causes Y
        for m in re.finditer(r'(\w+)\s+(causes?|leads? to|results? in|produces?)\s+(\w+)', text):
            atoms.add(m.group(1))
            atoms.add(m.group(3))
            rules.append((m.group(1), m.group(3)))
        
        # Comparatives
        for m in re.finditer(r'(\w+)\s+(greater|less|more|fewer)\s+than\s+(\w+)', text):
            prop = f"{m.group(1)}_{m.group(2)}_{m.group(3)}"
            atoms.add(prop)
        
        # Extract sentences as atoms
        sentences = re.split(r'[.!?;]', text)
        for s in sentences:
            s = s.strip()
            if s and len(s) > 5:
                atoms.add(s)
        
        # Transitivity detection: A>B and B>C implies A>C
        comparisons = list(re.finditer(r'(\w+)\s*([><])\s*(\w+)', text))
        for i, m1 in enumerate(comparisons):
            for m2 in comparisons[i+1:]:
                if m1.group(3) == m2.group(1) and m1.group(2) == m2.group(2):
                    ant = f"{m1.group(1)}{m1.group(2)}{m1.group(3)},{m2.group(1)}{m2.group(2)}{m2.group(3)}"
                    cons = f"{m1.group(1)}{m1.group(2)}{m2.group(3)}"
                    rules.append((ant, cons))
        
        return atoms, rules
    
    def _encode_set(self, props: Set[str]) -> int:
        """Encode proposition set as product of primes"""
        if not props:
            return 1
        result = 1
        for p in props:
            result *= self._get_prime(p)
        return result
    
    def _forward_chain(self, atoms: Set[str], rules: List[Tuple[str, str]], max_iter=10) -> Set[str]:
        """Compute deductive closure via BFS"""
        closure = set(atoms)
        for _ in range(max_iter):
            new_props = set()
            for ant, cons in rules:
                # Simple subset check
                ant_props = set(ant.split(','))
                if ant_props.issubset(closure):
                    new_props.add(cons)
            if not new_props - closure:
                break
            closure.update(new_props)
        return closure
    
    def _backward_chain(self, goal: str, rules: List[Tuple[str, str]], max_iter=5) -> Set[str]:
        """Compute weakest precondition"""
        wp = {goal}
        for _ in range(max_iter):
            new_wp = set()
            for ant, cons in rules:
                if cons in wp:
                    new_wp.update(ant.split(','))
            if not new_wp - wp:
                break
            wp.update(new_wp)
        return wp
    
    def _jaccard(self, set1: Set[str], set2: Set[str]) -> float:
        """Jaccard similarity"""
        if not set1 and not set2:
            return 1.0
        inter = len(set1 & set2)
        union = len(set1 | set2)
        return inter / union if union > 0 else 0.0
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized compression distance"""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
    
    def _numeric_eval(self, prompt: str, candidate: str) -> float:
        """Evaluate numeric comparisons directly"""
        nums_p = re.findall(r'\d+\.?\d*', prompt)
        nums_c = re.findall(r'\d+\.?\d*', candidate)
        
        # Check if candidate correctly orders numbers from prompt
        if len(nums_p) >= 2 and len(nums_c) >= 2:
            try:
                p_vals = [float(n) for n in nums_p[:2]]
                c_vals = [float(n) for n in nums_c[:2]]
                if sorted(p_vals) == sorted(c_vals):
                    return 0.8
            except:
                pass
        return 0.0
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check prompt for ambiguity/unanswerability markers"""
        p = prompt.lower()
        
        # Presupposition
        if re.search(r'(have you|did you)\s+(stop|quit|cease)', p):
            return 0.2
        if re.search(r'why\s+did\s+\w+\s+(fail|stop|end)', p):
            return 0.25
        
        # Scope ambiguity
        if re.search(r'every\s+\w+.*?\sa\s+\w+', p):
            return 0.3
        
        # Pronoun ambiguity
        if re.search(r'\w+\s+told\s+\w+\s+(he|she|they)', p) and 'who' in p:
            return 0.25
        
        # False dichotomy
        if re.search(r'either\s+\w+\s+or\s+\w+', p) and '?' in p:
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'(best|worst|favorite|prefer)', p) and not re.search(r'(because|criteria|measure)', p):
            return 0.25
        
        return 1.0
    
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        """Rank candidates via Hoare-style scoring"""
        prompt_atoms, prompt_rules = self._parse_text(prompt)
        prompt_closure = self._forward_chain(prompt_atoms, prompt_rules)
        
        results = []
        for cand in candidates:
            cand_atoms, cand_rules = self._parse_text(cand)
            
            # Compute wp for candidate's claims
            cand_goals = cand_atoms - prompt_closure
            wp = set()
            for goal in cand_goals:
                wp.update(self._backward_chain(goal, prompt_rules + cand_rules))
            
            # Structural score: Jaccard between wp and prompt closure
            struct_score = self._jaccard(wp, prompt_closure) if wp else self._jaccard(cand_atoms, prompt_closure)
            
            # Numeric computation score
            num_score = self._numeric_eval(prompt, cand)
            
            # NCD as tiebreaker
            ncd_score = 1.0 - self._ncd(prompt, cand)
            
            # Combine: 60% structure, 25% numeric, 15% NCD
            final_score = 0.6 * struct_score + 0.25 * num_score + 0.15 * ncd_score
            
            reasoning = f"Struct={struct_score:.2f} Num={num_score:.2f} NCD={ncd_score:.2f}"
            results.append({"candidate": cand, "score": final_score, "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x['score'], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1, capped by meta-confidence"""
        meta_conf = self._meta_confidence(prompt)
        
        if meta_conf < 0.5:
            return meta_conf
        
        prompt_atoms, prompt_rules = self._parse_text(prompt)
        ans_atoms, ans_rules = self._parse_text(answer)
        
        prompt_closure = self._forward_chain(prompt_atoms, prompt_rules)
        
        # If answer atoms are subset of closure, high confidence
        overlap = len(ans_atoms & prompt_closure) / len(ans_atoms) if ans_atoms else 0.0
        
        # Numeric check
        num_score = self._numeric_eval(prompt, answer)
        
        # Combine
        base_conf = max(overlap, num_score)
        
        # Cap at 0.85 unless perfect numeric match
        if num_score < 0.9:
            base_conf = min(base_conf, 0.85)
        
        return min(base_conf, meta_conf)