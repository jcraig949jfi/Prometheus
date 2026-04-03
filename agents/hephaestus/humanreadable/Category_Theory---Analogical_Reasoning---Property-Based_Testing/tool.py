from typing import Dict, Optional, Tuple

import re
import zlib
import random
from typing import List, Dict, Tuple, Optional
import numpy as np

class ReasoningTool:
    """
    Functorial Analogy-Robust Scoring (FARS) - combines category theory,
    analogical reasoning, and property-based testing.
    
    Parses prompts/answers into relational graphs, finds structure-preserving
    functorial mappings, and validates robustness via perturbations.
    """
    
    def __init__(self):
        self.rel_synonyms = {
            'CAUSE': ['cause', 'lead', 'result', 'produce', 'trigger', 'generate'],
            'GREATER': ['more', 'greater', 'larger', 'bigger', 'exceed', 'above'],
            'LESS': ['less', 'fewer', 'smaller', 'below', 'under'],
            'EQUAL': ['equal', 'same', 'identical', 'equivalent'],
            'BEFORE': ['before', 'prior', 'earlier', 'precede'],
            'AFTER': ['after', 'later', 'follow', 'subsequent']
        }
    
    def _parse_graph(self, text: str) -> Dict:
        """Extract relational graph: nodes (props with polarity) and edges."""
        text_lower = text.lower()
        
        # Extract propositions (entities, numeric values, claims)
        props = []
        
        # Entities (capitalized or noun phrases)
        entities = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b', text)
        for ent in entities:
            props.append({'text': ent, 'polarity': 1, 'value': None})
        
        # Numeric values with optional units
        numbers = re.findall(r'(\d+(?:\.\d+)?)\s*([a-z]+)?', text_lower)
        for num, unit in numbers:
            props.append({'text': f"{num}{unit}", 'polarity': 1, 'value': float(num)})
        
        # Simple claims (subject-verb-object)
        sentences = re.split(r'[.!?;]', text)
        for sent in sentences:
            if sent.strip():
                props.append({'text': sent.strip(), 'polarity': 1, 'value': None})
        
        # Detect negations and flip polarity
        for i, prop in enumerate(props):
            if re.search(r'\b(not|no|never|n\'t)\b', prop['text'].lower()):
                props[i]['polarity'] = -1
        
        # Build adjacency: detect relational edges
        adj = {r: np.zeros((len(props), len(props)), dtype=bool) for r in self.rel_synonyms.keys()}
        
        for i, p1 in enumerate(props):
            for j, p2 in enumerate(props):
                if i == j:
                    continue
                
                # Check text between props for relation cues
                context = text_lower
                
                # CAUSE relations
                if any(w in context for w in self.rel_synonyms['CAUSE']):
                    if p1['text'].lower() in context and p2['text'].lower() in context:
                        adj['CAUSE'][i, j] = True
                
                # Numeric comparisons
                if p1['value'] is not None and p2['value'] is not None:
                    if p1['value'] > p2['value']:
                        adj['GREATER'][i, j] = True
                    elif p1['value'] < p2['value']:
                        adj['LESS'][i, j] = True
                    else:
                        adj['EQUAL'][i, j] = True
        
        return {'nodes': props, 'adj': adj}
    
    def _functorial_score(self, g_prompt: Dict, g_answer: Dict) -> float:
        """Compute structure preservation: how well answer preserves prompt structure."""
        np_nodes = len(g_prompt['nodes'])
        na_nodes = len(g_answer['nodes'])
        
        if np_nodes == 0 or na_nodes == 0:
            return 0.0
        
        # Node similarity matrix (text overlap, polarity match)
        sim_matrix = np.zeros((np_nodes, na_nodes))
        for i, pn in enumerate(g_prompt['nodes']):
            for j, an in enumerate(g_answer['nodes']):
                # Text overlap
                p_words = set(pn['text'].lower().split())
                a_words = set(an['text'].lower().split())
                if p_words and a_words:
                    jaccard = len(p_words & a_words) / len(p_words | a_words)
                else:
                    jaccard = 0.0
                
                # Polarity match
                polarity_match = 1.0 if pn['polarity'] == an['polarity'] else 0.0
                
                sim_matrix[i, j] = 0.7 * jaccard + 0.3 * polarity_match
        
        # Greedy matching (poor man's Hungarian)
        mapping = {}
        for _ in range(min(np_nodes, na_nodes)):
            i, j = np.unravel_index(sim_matrix.argmax(), sim_matrix.shape)
            if sim_matrix[i, j] > 0.1:
                mapping[i] = j
                sim_matrix[i, :] = 0
                sim_matrix[:, j] = 0
        
        # Check edge preservation
        total_edges = sum(adj.sum() for adj in g_prompt['adj'].values())
        if total_edges == 0:
            return np.mean(list(mapping.values())) if mapping else 0.5
        
        preserved = 0
        for rel, adj_p in g_prompt['adj'].items():
            adj_a = g_answer['adj'][rel]
            for i in range(np_nodes):
                for j in range(np_nodes):
                    if adj_p[i, j] and i in mapping and j in mapping:
                        if adj_a[mapping[i], mapping[j]]:
                            preserved += 1
        
        return 1.0 - min(1.0, (total_edges - preserved) / max(1, total_edges))
    
    def _perturb(self, text: str) -> str:
        """Generate a perturbation: flip negation, swap comparative, etc."""
        operations = ['negate', 'swap_comp', 'tweak_number']
        op = random.choice(operations)
        
        if op == 'negate':
            if 'not' in text:
                return text.replace(' not ', ' ', 1)
            else:
                words = text.split()
                if len(words) > 2:
                    idx = random.randint(1, len(words) - 1)
                    words.insert(idx, 'not')
                return ' '.join(words)
        
        elif op == 'swap_comp':
            text = re.sub(r'\bmore\b', 'LESS_TEMP', text)
            text = re.sub(r'\bless\b', 'more', text)
            text = re.sub(r'LESS_TEMP', 'less', text)
            return text
        
        elif op == 'tweak_number':
            match = re.search(r'\d+(\.\d+)?', text)
            if match:
                num = float(match.group())
                new_num = num * random.uniform(0.9, 1.1)
                return text[:match.start()] + f"{new_num:.2f}" + text[match.end():]
        
        return text
    
    def _robustness_score(self, prompt: str, answer: str, n_perturbs: int = 5) -> float:
        """Property-based robustness via perturbations."""
        g_answer = self._parse_graph(answer)
        scores = []
        
        for _ in range(n_perturbs):
            p_perturbed = self._perturb(prompt)
            g_perturbed = self._parse_graph(p_perturbed)
            score = self._functorial_score(g_perturbed, g_answer)
            scores.append(score)
        
        return np.mean(scores) if scores else 0.5
    
    def _computational_score(self, prompt: str, answer: str) -> float:
        """Standard computational parsers for deterministic problems."""
        p_lower, a_lower = prompt.lower(), answer.lower()
        
        # Numeric comparison
        p_nums = [float(x) for x in re.findall(r'\d+\.?\d*', prompt)]
        a_nums = [float(x) for x in re.findall(r'\d+\.?\d*', answer)]
        
        if 'which is' in p_lower and ('greater' in p_lower or 'larger' in p_lower):
            if len(p_nums) >= 2 and len(a_nums) >= 1:
                expected = max(p_nums)
                if abs(a_nums[0] - expected) < 0.01:
                    return 1.0
        
        # Bat-and-ball algebra
        if 'cost' in p_lower and 'total' in p_lower and 'more than' in p_lower:
            if len(p_nums) == 2:
                total, diff = p_nums[0], p_nums[1]
                ball = (total - diff) / 2
                if len(a_nums) >= 1 and abs(a_nums[0] - ball) < 0.01:
                    return 1.0
        
        # Modus tollens
        if 'if' in p_lower and 'then' in p_lower and 'not' in p_lower:
            return 0.7
        
        return 0.0
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
    
    def _meta_confidence(self, prompt: str) -> float:
        """Detect ambiguity, presupposition, unanswerability."""
        p_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|quit|why did.*fail|when did.*stop)', p_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery\b.*\ba\b', p_lower):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'\b(he|she|it)\b', p_lower) and '?' in prompt:
            return 0.3
        
        # False dichotomy
        if re.search(r'\beither\b.*\bor\b', p_lower):
            return 0.35
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|most beautiful)', p_lower):
            return 0.3
        
        return 1.0
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates by FARS score."""
        g_prompt = self._parse_graph(prompt)
        results = []
        
        for cand in candidates:
            g_cand = self._parse_graph(cand)
            
            # Score components
            s_struct = self._functorial_score(g_prompt, g_cand)
            s_robust = self._robustness_score(prompt, cand, n_perturbs=3)
            s_comp = self._computational_score(prompt, cand)
            ncd = 1.0 - self._ncd(prompt, cand)
            
            # Weighted combination
            score = 0.5 * s_struct + 0.25 * s_robust + 0.15 * s_comp + 0.1 * ncd
            
            reasoning = f"Struct:{s_struct:.2f} Robust:{s_robust:.2f} Comp:{s_comp:.2f}"
            results.append({'candidate': cand, 'score': score, 'reasoning': reasoning})
        
        return sorted(results, key=lambda x: x['score'], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Confidence with epistemic honesty."""
        meta_conf = self._meta_confidence(prompt)
        
        if meta_conf < 0.5:
            return meta_conf
        
        g_prompt = self._parse_graph(prompt)
        g_answer = self._parse_graph(answer)
        
        s_struct = self._functorial_score(g_prompt, g_answer)
        s_comp = self._computational_score(prompt, answer)
        
        # High confidence only if computational match
        if s_comp > 0.9:
            return min(0.95, meta_conf)
        
        # Medium confidence on good structure match
        if s_struct > 0.7:
            return min(0.7, meta_conf * 0.8)
        
        # Low confidence otherwise
        return min(0.4, meta_conf * s_struct)