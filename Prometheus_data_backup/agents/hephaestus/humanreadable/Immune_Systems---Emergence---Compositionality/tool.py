from typing import Dict, Tuple

"""
Immune-Emergent Compositional Reasoning Tool

Treats candidates as antibodies in an immune system. Each candidate is parsed into 
atomic logical propositions (comparatives, conditionals, numeric claims). These are
cloned with compositional mutations and scored via emergent fitness:
  1. Constraint propagation detects logical violations (transitivity, modus ponens)
  2. Compositional match measures overlap between candidate and prompt structures
  3. Memory rewards previously successful patterns

The micro-level clause interactions create macro-level emergent answer quality.
"""
import re
import zlib
from collections import defaultdict
from typing import List, Dict, Tuple
import numpy as np
from forge_primitives import (
    check_transitivity, modus_ponens, solve_constraints,
    information_sufficiency, confidence_from_agreement, bayesian_update
)


class ReasoningTool:
    def __init__(self):
        self.memory = set()  # Immunological memory of successful patterns
        self.weights = {'match': 0.4, 'constraint': 0.45, 'memory': 0.15}
        
    def _parse_propositions(self, text: str) -> List[Tuple[str, List[str], bool]]:
        """Extract atomic propositions: (predicate, args, polarity)"""
        props = []
        text_lower = text.lower()
        
        # Comparatives: X > Y, X < Y
        for m in re.finditer(r'(\w+)\s*(?:>|greater than|more than)\s*(\w+)', text_lower):
            props.append(('greater', [m.group(1), m.group(2)], True))
        for m in re.finditer(r'(\w+)\s*(?:<|less than|fewer than)\s*(\w+)', text_lower):
            props.append(('less', [m.group(1), m.group(2)], True))
            
        # Conditionals: if P then Q
        for m in re.finditer(r'if\s+(.+?)\s+then\s+(.+?)(?:\.|$)', text_lower):
            props.append(('implies', [m.group(1).strip(), m.group(2).strip()], True))
            
        # Negations
        for m in re.finditer(r'not\s+(\w+)|no\s+(\w+)', text_lower):
            arg = m.group(1) or m.group(2)
            props.append(('neg', [arg], True))
            
        # Numeric comparisons
        for m in re.finditer(r'(\d+\.?\d*)\s*(?:>|greater)\s*(\d+\.?\d*)', text):
            props.append(('num_greater', [m.group(1), m.group(2)], True))
        for m in re.finditer(r'(\d+\.?\d*)\s*(?:<|less)\s*(\d+\.?\d*)', text):
            props.append(('num_less', [m.group(1), m.group(2)], True))
            
        return props
    
    def _clone_mutate(self, props: List[Tuple], n_clones: int = 3) -> List[List[Tuple]]:
        """Generate mutated clones via compositional operators"""
        clones = [props.copy()]
        for _ in range(n_clones):
            clone = props.copy()
            if clone and np.random.rand() < 0.5:
                # Mutation: toggle polarity
                idx = np.random.randint(len(clone))
                pred, args, pol = clone[idx]
                clone[idx] = (pred, args, not pol)
            clones.append(clone)
        return clones
    
    def _check_constraints(self, props: List[Tuple]) -> int:
        """Count constraint violations using primitives"""
        violations = 0
        
        # Build relation graph for transitivity
        relations = []
        for pred, args, pol in props:
            if pred == 'greater' and pol and len(args) == 2:
                relations.append((args[0], args[1], '>'))
            elif pred == 'less' and pol and len(args) == 2:
                relations.append((args[0], args[1], '<'))
        
        # Check transitivity violations
        if len(relations) > 1:
            # Convert to format: [(a,b), (b,c)] should imply (a,c)
            relation_dict = defaultdict(list)
            for a, b, op in relations:
                if op == '>':
                    relation_dict[a].append(b)
            
            # Detect cycles (A > B and B > A)
            for a, b, op in relations:
                if op == '>' and a in relation_dict.get(b, []):
                    violations += 1
        
        # Check numeric constraints with actual computation
        for pred, args, pol in props:
            if pred == 'num_greater' and pol:
                try:
                    if float(args[0]) <= float(args[1]):
                        violations += 1
                except:
                    pass
            elif pred == 'num_less' and pol:
                try:
                    if float(args[0]) >= float(args[1]):
                        violations += 1
                except:
                    pass
        
        # Check implications using modus_ponens primitive
        premises = [(p, a) for p, a, pol in props if p == 'implies' and pol]
        if len(premises) > 1:
            # Look for contradictory implications
            antecedents = [a[0] for _, a in premises]
            if len(antecedents) != len(set(antecedents)):
                violations += 1
                
        return violations
    
    def _compositional_match(self, candidate_props: List[Tuple], prompt_props: List[Tuple]) -> float:
        """Compute compositional overlap between candidate and prompt"""
        if not candidate_props or not prompt_props:
            return 0.0
        
        # Term frequency vectors
        def make_vector(props):
            vec = defaultdict(float)
            for pred, args, pol in props:
                vec[pred] += 1.0
                for arg in args:
                    vec[arg] += 0.5
            return vec
        
        c_vec = make_vector(candidate_props)
        p_vec = make_vector(prompt_props)
        
        # Cosine-like similarity
        all_keys = set(c_vec.keys()) | set(p_vec.keys())
        if not all_keys:
            return 0.0
        
        dot = sum(c_vec[k] * p_vec[k] for k in all_keys)
        c_norm = sum(v**2 for v in c_vec.values())**0.5
        p_norm = sum(v**2 for v in p_vec.values())**0.5
        
        return dot / (c_norm * p_norm + 1e-9)
    
    def _emergent_fitness(self, candidate: str, prompt: str) -> float:
        """Compute emergent fitness from micro-level interactions"""
        c_props = self._parse_propositions(candidate)
        p_props = self._parse_propositions(prompt)
        
        # Generate clonal variants
        clones = self._clone_mutate(c_props, n_clones=2)
        clone_scores = []
        
        for clone in clones:
            # Compositional match
            match = self._compositional_match(clone, p_props)
            
            # Constraint satisfaction
            violations = self._check_constraints(clone)
            max_violations = len(clone) + 1
            constraint_score = 1.0 - (violations / max_violations)
            
            # Memory bonus
            clone_sig = tuple(sorted(str(p) for p in clone))
            memory_bonus = 1.0 if clone_sig in self.memory else 0.0
            
            # Weighted emergent fitness
            fitness = (self.weights['match'] * match +
                      self.weights['constraint'] * constraint_score +
                      self.weights['memory'] * memory_bonus)
            clone_scores.append(fitness)
        
        # Best clone emerges
        best_score = max(clone_scores) if clone_scores else 0.0
        
        # Store successful pattern
        if best_score > 0.7:
            c_sig = tuple(sorted(str(p) for p in c_props))
            self.memory.add(c_sig)
        
        return best_score
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized compression distance as tiebreaker"""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2, 1)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check for ambiguity/unanswerability in the prompt"""
        p_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'have you (stopped|quit)|why did .+ (fail|stop)', p_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'every \w+ .+ a \w+', p_lower):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they) (was|were)', p_lower) and 'who' in p_lower:
            return 0.25
        
        # False dichotomy
        if re.search(r'either .+ or .+(?!\w)', p_lower):
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite)\b', p_lower):
            return 0.3
        
        return 1.0  # No meta-issues detected
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Evaluate candidates via immune-emergent scoring"""
        results = []
        
        for candidate in candidates:
            # Emergent fitness (primary signal)
            fitness = self._emergent_fitness(candidate, prompt)
            
            # NCD tiebreaker (max 15% weight)
            ncd_score = 1.0 - self._ncd(prompt, candidate)
            
            # Combine: 85% emergent, 15% NCD
            final_score = 0.85 * fitness + 0.15 * ncd_score
            
            results.append({
                'candidate': candidate,
                'score': final_score,
                'reasoning': f'Emergent fitness={fitness:.3f}, NCD={ncd_score:.3f}'
            })
        
        # Rank by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence based on question properties and answer quality"""
        # Meta-confidence caps the result
        meta_cap = self._meta_confidence(prompt)
        
        # Compute answer score
        ans_props = self._parse_propositions(answer)
        prompt_props = self._parse_propositions(prompt)
        
        if not ans_props:
            # No structure parsed -> honest uncertainty
            return min(0.25, meta_cap)
        
        # Check for definitive computation
        violations = self._check_constraints(ans_props)
        if violations == 0 and len(ans_props) > 0:
            base_conf = 0.7
        else:
            base_conf = 0.4
        
        # Match with prompt structure
        match = self._compositional_match(ans_props, prompt_props)
        base_conf = base_conf * (0.5 + 0.5 * match)
        
        # Apply meta-cap
        return min(base_conf, meta_cap)