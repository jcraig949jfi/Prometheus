"""
Thermodynamics x Error Correcting Codes x Mechanism Design Reasoning Tool

Combines:
- Thermodynamic energy: constraint violation as potential energy
- ECC distance: Hamming distance from reference codeword
- Mechanism design: utility functions for incentive compatibility

Uses primitives to build a scoring pipeline that treats reasoning as minimizing
free energy in a constraint satisfaction landscape.
"""

import re
import numpy as np
from collections import defaultdict

# Import primitives
try:
    from forge_primitives import (
        solve_sat, entropy, confidence_from_agreement,
        information_sufficiency, bayesian_update, solve_constraints
    )
    PRIMITIVES_AVAILABLE = True
except ImportError:
    PRIMITIVES_AVAILABLE = False


class ReasoningTool:
    def __init__(self):
        self.proposition_cache = {}
        self.weights = {'thermo': 1.0, 'ecc': 0.5, 'utility': 0.7}
        
    def _extract_propositions(self, text):
        """Extract atomic propositions from text"""
        props = set()
        
        # Negations
        for m in re.finditer(r'\b(not|no|never|none)\s+(\w+)', text.lower()):
            props.add(f"NOT_{m.group(2)}")
        
        # Comparatives with numbers
        for m in re.finditer(r'(\d+\.?\d*)\s*(>|<|>=|<=|=)\s*(\d+\.?\d*)', text):
            props.add(f"CMP_{m.group(1)}_{m.group(2)}_{m.group(3)}")
        
        # Conditionals
        for m in re.finditer(r'if\s+(.+?)\s+then\s+(.+?)[\.,;]', text.lower()):
            props.add(f"IF_{m.group(1)[:20]}_THEN_{m.group(2)[:20]}")
        
        # Causal claims
        for m in re.finditer(r'(\w+)\s+(leads to|causes|results in)\s+(\w+)', text.lower()):
            props.add(f"CAUSE_{m.group(1)}_{m.group(3)}")
        
        # Numeric claims
        for m in re.finditer(r'(\w+)\s+is\s+(\d+\.?\d*)', text.lower()):
            props.add(f"VALUE_{m.group(1)}_{m.group(2)}")
        
        # Temporal ordering
        for m in re.finditer(r'(\w+)\s+(before|after)\s+(\w+)', text.lower()):
            props.add(f"ORDER_{m.group(1)}_{m.group(2)}_{m.group(3)}")
        
        return props
    
    def _encode_as_vector(self, text, prop_index):
        """Encode text as binary vector over proposition space"""
        props = self._extract_propositions(text)
        vec = np.zeros(len(prop_index))
        for p in props:
            if p in prop_index:
                vec[prop_index[p]] = 1
        return vec
    
    def _compute_energy(self, vec, constraint_matrix, b_vec, weights):
        """Thermodynamic energy: sum of weighted constraint violations"""
        violations = np.maximum(0, constraint_matrix @ vec - b_vec)
        return np.sum(weights * violations)
    
    def _compute_utility(self, text, prompt):
        """Mechanism design utility: incentivize correct patterns"""
        utility = 0.0
        
        # Reward numeric accuracy
        prompt_nums = re.findall(r'\d+\.?\d*', prompt)
        text_nums = re.findall(r'\d+\.?\d*', text)
        if prompt_nums and text_nums:
            try:
                for pn in prompt_nums:
                    for tn in text_nums:
                        if abs(float(pn) - float(tn)) < 0.01:
                            utility += 2.0
            except ValueError:
                pass
        
        # Penalize false causal claims (too many causes without conditionals)
        causal = len(re.findall(r'leads to|causes|results in', text.lower()))
        conditionals = len(re.findall(r'if\s+.+\s+then', text.lower()))
        if causal > 2 * (conditionals + 1):
            utility -= 3.0 * (causal - 2 * conditionals)
        
        # Reward structural alignment
        if 'not' in prompt.lower() and 'not' in text.lower():
            utility += 1.0
        
        return utility
    
    def _meta_confidence(self, prompt):
        """Check prompt for ambiguity/unanswerability markers"""
        p_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'(have you|did you) (stop|quit|cease)', p_lower):
            return 0.2
        if re.search(r'why (did|does|is) \w+ (fail|stop|wrong)', p_lower):
            return 0.25
        
        # Scope ambiguity
        if re.search(r'every \w+ \w+ a \w+', p_lower):
            return 0.3
        
        # Pronoun ambiguity
        if 'who?' in p_lower and re.search(r'(he|she|they) (was|were)', p_lower):
            return 0.25
        
        # False dichotomy
        if re.search(r'either \w+ or \w+', p_lower):
            return 0.35
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|prettiest)\b', p_lower):
            return 0.3
        
        # Insufficient info
        if '?' in prompt and len(prompt.split()) < 5:
            return 0.4
        
        return 1.0  # No meta-issues detected
    
    def _ncd(self, s1, s2):
        """Normalized Compression Distance"""
        import zlib
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0
    
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        """Score candidates using thermo + ECC + mechanism design pipeline"""
        if not candidates:
            return []
        
        # Build unified proposition index
        all_props = self._extract_propositions(prompt)
        for cand in candidates:
            all_props.update(self._extract_propositions(cand))
        prop_index = {p: i for i, p in enumerate(sorted(all_props))}
        n_props = len(prop_index)
        
        if n_props == 0:
            # Fallback to NCD only
            scores = []
            for cand in candidates:
                ncd_score = 1.0 - self._ncd(prompt, cand)
                scores.append({
                    'candidate': cand,
                    'score': ncd_score,
                    'reasoning': 'No propositions extracted, using NCD'
                })
            scores.sort(key=lambda x: x['score'], reverse=True)
            return scores
        
        # Encode prompt as reference "gold" vector
        gold_vec = self._encode_as_vector(prompt, prop_index)
        
        # Build constraint matrix from prompt implications
        constraints = []
        weights_list = []
        
        # If-then constraints
        for m in re.finditer(r'if\s+(.+?)\s+then\s+(.+?)[\.,;]', prompt.lower()):
            antecedent_props = self._extract_propositions(m.group(1))
            consequent_props = self._extract_propositions(m.group(2))
            if antecedent_props and consequent_props:
                constraints.append((antecedent_props, consequent_props))
                weights_list.append(2.0)
        
        # Build constraint matrix
        k = max(1, len(constraints))
        C = np.zeros((k, n_props))
        b = np.ones(k)
        w = np.ones(k)
        
        for i, (ant, con) in enumerate(constraints[:k]):
            for p in ant:
                if p in prop_index:
                    C[i, prop_index[p]] = -1  # antecedent
            for p in con:
                if p in prop_index:
                    C[i, prop_index[p]] = 1   # consequent
            w[i] = weights_list[i] if i < len(weights_list) else 1.0
        
        # Score each candidate
        results = []
        all_scores = []
        
        for cand in candidates:
            vec = self._encode_as_vector(cand, prop_index)
            
            # Thermodynamic energy (lower is better)
            E_thermo = self._compute_energy(vec, C, b, w)
            
            # ECC Hamming distance (lower is better)
            d_hamming = np.sum(np.abs(vec - gold_vec))
            E_ecc = self.weights['ecc'] * d_hamming
            
            # Mechanism design utility (higher is better)
            utility = self._compute_utility(cand, prompt)
            
            # Compute entropy of candidate vector as thermodynamic analog
            vec_probs = vec / (vec.sum() + 1e-9)
            if PRIMITIVES_AVAILABLE and vec.sum() > 0:
                try:
                    H = entropy(vec_probs[vec_probs > 0])
                except:
                    H = 0
            else:
                H = -np.sum(vec_probs * np.log(vec_probs + 1e-9))
            
            # Final score (negative free energy)
            score = -(E_thermo + E_ecc) + self.weights['utility'] * utility + 0.1 * H
            
            # Add small NCD component (max 10%)
            ncd_component = 0.1 * (1.0 - self._ncd(prompt, cand))
            score += ncd_component
            
            all_scores.append(score)
            
            reasoning = f"E_thermo={E_thermo:.2f}, d_H={d_hamming:.0f}, U={utility:.2f}, H={H:.2f}"
            results.append({
                'candidate': cand,
                'score': score,
                'reasoning': reasoning
            })
        
        # Normalize scores to 0-1 range
        if len(all_scores) > 1:
            min_s, max_s = min(all_scores), max(all_scores)
            if max_s > min_s:
                for r in results:
                    r['score'] = (r['score'] - min_s) / (max_s - min_s)
        
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on meta-analysis and structural fit"""
        # Check prompt for meta-issues first
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.5:
            return meta_conf
        
        # Evaluate this single answer
        results = self.evaluate(prompt, [answer, ""])
        if not results:
            return 0.5
        
        # Find answer's score
        answer_result = next((r for r in results if r['candidate'] == answer), None)
        if answer_result is None:
            return 0.5
        
        base_conf = answer_result['score']
        
        # Cap confidence - never exceed 0.9 unless perfect match
        props_prompt = self._extract_propositions(prompt)
        props_answer = self._extract_propositions(answer)
        
        if len(props_prompt) == 0:
            return min(0.6, base_conf * meta_conf)
        
        overlap = len(props_prompt & props_answer) / len(props_prompt)
        
        # Scale confidence based on structural overlap
        conf = base_conf * 0.7 + overlap * 0.3
        conf = min(0.85, conf * meta_conf)  # Cap at 0.85
        
        return max(0.1, min(0.85, conf))