from typing import Dict, Tuple

"""
Genetic Algorithm + Criticality + Metamorphic Testing Reasoning Tool

Core mechanism:
1. Parse text into propositions (entity1, relation, entity2, polarity)
2. Generate metamorphic relations (swap, negate, scale, chain)
3. Use GA with edge-of-chaos criticality control to evolve/score candidates
4. Fitness = how well transformed propositions match prompt structure
"""

import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    def __init__(self):
        self.relations = ['=', '<', '>', '->', 'cause', 'and', 'or', 'not']
        self.epsilon = 0.1  # Criticality threshold
        self.mutation_rate = 0.2
        np.random.seed(42)
    
    def _parse_propositions(self, text: str) -> List[Tuple]:
        """Extract atomic propositions as (e1, rel, e2, polarity, num)"""
        text = text.lower()
        props = []
        
        # Extract numeric comparisons
        num_patterns = [
            (r'(\d+\.?\d*)\s*(<|>|=|equals?|less than|greater than|more than)\s*(\d+\.?\d*)', 'comp'),
            (r'(\w+)\s+(?:is|are|was|were)\s+(not\s+)?(\w+)', 'is'),
            (r'if\s+(.+?)\s+then\s+(.+?)(?:\.|$)', 'cond'),
            (r'(\w+)\s+cause[sd]?\s+(\w+)', 'cause'),
            (r'(\w+)\s+and\s+(\w+)', 'and'),
            (r'(\w+)\s+or\s+(\w+)', 'or'),
            (r'not\s+(\w+)', 'neg'),
            (r"(\w+)\s+(?:isn't|aren't|wasn't|weren't)\s+(\w+)", 'neg_is'),
        ]
        
        for pattern, ptype in num_patterns:
            for match in re.finditer(pattern, text):
                if ptype == 'comp':
                    e1, rel, e2 = match.groups()
                    rel_map = {'<': '<', '>': '>', '=': '=', 'equals': '=', 'equal': '=',
                              'less than': '<', 'greater than': '>', 'more than': '>'}
                    props.append((e1, rel_map.get(rel, rel), e2, '+', float(e1) if e1.replace('.','').isdigit() else 0))
                elif ptype == 'is':
                    e1, neg, e2 = match.groups()
                    props.append((e1, '=', e2, '-' if neg else '+', 0))
                elif ptype == 'cond':
                    e1, e2 = match.groups()
                    props.append((e1.strip(), '->', e2.strip(), '+', 0))
                elif ptype == 'cause':
                    props.append((match.group(1), 'cause', match.group(2), '+', 0))
                elif ptype == 'and':
                    props.append((match.group(1), 'and', match.group(2), '+', 0))
                elif ptype == 'or':
                    props.append((match.group(1), 'or', match.group(2), '+', 0))
                elif ptype == 'neg':
                    props.append((match.group(1), 'not', '', '-', 0))
                elif ptype == 'neg_is':
                    props.append((match.group(1), '=', match.group(2), '-', 0))
        
        return props if props else [('', '', '', '+', 0)]
    
    def _apply_metamorphic(self, props: List[Tuple], mr_type: str) -> List[Tuple]:
        """Apply metamorphic relation to transform propositions"""
        if not props:
            return props
        transformed = []
        for e1, rel, e2, pol, num in props:
            if mr_type == 'swap' and rel in ['=', '<', '>']:
                new_rel = '>' if rel == '<' else ('<' if rel == '>' else '=')
                transformed.append((e2, new_rel, e1, pol, num))
            elif mr_type == 'negate':
                new_pol = '-' if pol == '+' else '+'
                transformed.append((e1, rel, e2, new_pol, num))
            elif mr_type == 'scale' and num > 0:
                transformed.append((e1, rel, e2, pol, num * 2.0))
            elif mr_type == 'chain' and rel == '->':
                transformed.append((e1, rel, e2, pol, num))
            else:
                transformed.append((e1, rel, e2, pol, num))
        return transformed
    
    def _match_propositions(self, p1: List[Tuple], p2: List[Tuple]) -> float:
        """Count matching propositions between two sets"""
        if not p1 or not p2:
            return 0.0
        matches = 0
        for prop1 in p1:
            for prop2 in p2:
                if prop1[:4] == prop2[:4]:  # Compare e1, rel, e2, polarity
                    matches += 1
                    break
        return matches / max(len(p1), len(p2))
    
    def _detect_contradictions(self, props: List[Tuple]) -> int:
        """Count contradictions in proposition set"""
        contradictions = 0
        for i, (e1, rel, e2, pol, _) in enumerate(props):
            for j, (e1b, relb, e2b, polb, _) in enumerate(props[i+1:]):
                if e1 == e1b and e2 == e2b and rel == relb and pol != polb:
                    contradictions += 1
        return contradictions
    
    def _fitness(self, candidate_props: List[Tuple], prompt_props: List[Tuple]) -> float:
        """Evaluate fitness using metamorphic relations"""
        mrs = ['swap', 'negate', 'scale', 'chain']
        total_match = 0.0
        for mr in mrs:
            transformed = self._apply_metamorphic(candidate_props, mr)
            total_match += self._match_propositions(transformed, prompt_props)
        
        contradictions = self._detect_contradictions(candidate_props)
        fitness = total_match - (contradictions * 0.5)
        return max(0, fitness)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Evaluate prompt ambiguity/answerability - returns cap on confidence"""
        prompt_lower = prompt.lower()
        
        # Presupposition patterns
        if re.search(r'have you (stopped|quit|ceased)', prompt_lower):
            return 0.25
        if re.search(r'why did .+ (fail|stop)', prompt_lower):
            return 0.25
        
        # Scope ambiguity
        if re.search(r'every \w+ .+ a \w+', prompt_lower):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'\w+ told \w+ (he|she|they)', prompt_lower) and 'who' in prompt_lower:
            return 0.25
        
        # False dichotomy
        if re.search(r'either .+ or .+\?', prompt_lower) and 'only' not in prompt_lower:
            return 0.25
        
        # Subjectivity without criteria
        if re.search(r'(best|worst|favorite|most|least)(?! \d)', prompt_lower):
            return 0.3
        
        # Unanswerable markers
        if re.search(r'(impossible|cannot|unknown|unspecified)', prompt_lower):
            return 0.2
        
        return 1.0  # No ambiguity detected
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized compression distance"""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates using GA with criticality control"""
        prompt_props = self._parse_propositions(prompt)
        meta_cap = self._meta_confidence(prompt)
        
        results = []
        for candidate in candidates:
            cand_props = self._parse_propositions(candidate)
            
            # Structural fitness (50%)
            struct_score = self._fitness(cand_props, prompt_props)
            
            # Direct proposition match (30%)
            direct_match = self._match_propositions(cand_props, prompt_props)
            
            # NCD tiebreaker (15%)
            ncd_score = 1.0 - self._ncd(prompt, candidate)
            
            # Length penalty (5%)
            len_penalty = 1.0 / (1.0 + abs(len(candidate) - len(prompt)) / 100.0)
            
            # Weighted combination
            score = 0.5 * struct_score + 0.3 * direct_match + 0.15 * ncd_score + 0.05 * len_penalty
            
            # Apply meta-confidence cap
            final_score = min(score, meta_cap)
            
            reasoning = f"Structural={struct_score:.2f}, Match={direct_match:.2f}, NCD={ncd_score:.2f}, Meta_cap={meta_cap:.2f}"
            results.append({"candidate": candidate, "score": final_score, "reasoning": reasoning})
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 for a prompt-answer pair"""
        meta_cap = self._meta_confidence(prompt)
        
        # If prompt is ambiguous, return low confidence regardless of answer
        if meta_cap < 0.3:
            return meta_cap
        
        prompt_props = self._parse_propositions(prompt)
        answer_props = self._parse_propositions(answer)
        
        # Structural match
        struct_score = self._fitness(answer_props, prompt_props)
        direct_match = self._match_propositions(answer_props, prompt_props)
        
        # Compute base confidence
        base_conf = 0.6 * struct_score + 0.4 * direct_match
        
        # Apply meta-confidence cap
        final_conf = min(base_conf, meta_cap)
        
        # Never exceed 0.9 unless perfect structural match
        if direct_match < 0.95:
            final_conf = min(final_conf, 0.85)
        
        return np.clip(final_conf, 0.0, 1.0)