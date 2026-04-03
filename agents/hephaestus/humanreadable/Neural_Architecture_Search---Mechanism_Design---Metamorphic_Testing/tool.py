from typing import Dict, Tuple

import re
import random
import zlib
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Constraint-Driven Architecture Search for Metamorphic Scoring (CDAS-MS).
    
    Combines NAS (evolutionary search over reasoning modules), mechanism design
    (utility-weighted MR scoring), and metamorphic testing (consistency checks).
    """
    
    def __init__(self):
        self.modules = ['modus_ponens', 'transitivity', 'numeric_bound', 'negation_flip', 'comparative_swap']
        random.seed(42)
        np.random.seed(42)
    
    def _parse_clause_graph(self, text: str) -> Dict:
        """Extract logical structures into a clause graph."""
        text_lower = text.lower()
        graph = {
            'negations': len(re.findall(r'\b(not|no|never|none)\b', text_lower)),
            'conditionals': re.findall(r'if\s+(.+?)\s+then\s+(.+?)(?:\.|$)', text_lower),
            'comparatives': re.findall(r'(\w+)\s+(greater|less|more|fewer|higher|lower)\s+than\s+(\w+)', text_lower),
            'numbers': [float(m) for m in re.findall(r'\d+\.?\d*', text)],
            'causal': len(re.findall(r'\b(causes?|leads?\s+to|results?\s+in)\b', text_lower)),
            'equivalence': len(re.findall(r'\b(same\s+as|identical|equals?)\b', text_lower)),
        }
        return graph
    
    def _apply_metamorphic_relation(self, graph: Dict, mr_type: str) -> Dict:
        """Apply a metamorphic transformation to the clause graph."""
        transformed = graph.copy()
        if mr_type == 'negate':
            transformed['negations'] = 1 - transformed['negations'] % 2
        elif mr_type == 'numeric_double':
            transformed['numbers'] = [n * 2 for n in transformed['numbers']]
        elif mr_type == 'comparative_swap':
            transformed['comparatives'] = [(c, 'greater' if 'less' in b else 'less', a) 
                                          for a, b, c in transformed['comparatives']]
        elif mr_type == 'conditional_reverse':
            transformed['conditionals'] = [(cons, ant) for ant, cons in transformed['conditionals']]
        return transformed
    
    def _compute_consistency(self, prompt_graph: Dict, candidate: str, mr_type: str) -> float:
        """Compute metamorphic consistency for a candidate under a transformation."""
        cand_graph = self._parse_clause_graph(candidate)
        
        # Structural alignment score
        align_score = 0.0
        
        if mr_type == 'negate' and prompt_graph['negations'] > 0:
            has_neg = cand_graph['negations'] > 0
            align_score = 1.0 if has_neg else 0.3
        
        elif mr_type == 'numeric_double' and prompt_graph['numbers']:
            p_nums = sorted(prompt_graph['numbers'])
            c_nums = sorted(cand_graph['numbers'])
            if c_nums:
                ratios = [c / p if p > 0 else 0 for p, c in zip(p_nums[:len(c_nums)], c_nums)]
                align_score = 1.0 / (1.0 + abs(np.mean(ratios) - 1.0)) if ratios else 0.5
        
        elif mr_type == 'comparative_swap' and prompt_graph['comparatives']:
            align_score = 0.7 if cand_graph['comparatives'] else 0.4
        
        elif mr_type == 'conditional_reverse' and prompt_graph['conditionals']:
            align_score = 0.8 if cand_graph['conditionals'] else 0.3
        
        else:
            align_score = 0.5  # neutral
        
        return align_score
    
    def _evolve_architecture(self, prompt_graph: Dict, candidates: List[str], generations: int = 5) -> np.ndarray:
        """Evolutionary NAS to find optimal module weights."""
        n_modules = len(self.modules)
        n_candidates = len(candidates)
        population_size = 10
        
        # Initialize population
        population = [np.random.rand(n_modules) for _ in range(population_size)]
        
        for gen in range(generations):
            fitness_scores = []
            for genome in population:
                # Compute fitness: consistency across MRs weighted by genome
                mr_types = ['negate', 'numeric_double', 'comparative_swap', 'conditional_reverse']
                total_fitness = 0.0
                for mr in mr_types:
                    consistencies = [self._compute_consistency(prompt_graph, c, mr) for c in candidates]
                    variance = np.var(consistencies) if len(consistencies) > 1 else 0.1
                    weight = 1.0 + variance  # Higher weight to discriminative MRs
                    total_fitness += weight * np.mean(consistencies)
                fitness_scores.append(total_fitness)
            
            # Select top half
            sorted_pop = [g for _, g in sorted(zip(fitness_scores, population), reverse=True)]
            population = sorted_pop[:population_size // 2]
            
            # Mutate and repopulate
            while len(population) < population_size:
                parent = random.choice(population[:population_size // 2])
                child = parent + np.random.randn(n_modules) * 0.1
                child = np.clip(child, 0, 1)
                population.append(child)
        
        return population[0]  # Best genome
    
    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check prompt quality for epistemic honesty."""
        p_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|did you quit|why did .+ fail|when did .+ stop)\b', p_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery\s+\w+\s+.+\s+a\s+\w+\b', p_lower):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'\b(he|she|it|they)\b', p_lower) and 'who' in p_lower:
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither\s+.+\s+or\s+.+\b', p_lower) and 'only' not in p_lower:
            return 0.3
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|prefer)\b', p_lower):
            return 0.3
        
        # Unanswerable markers
        if re.search(r'\b(cannot determine|not enough information|impossible to)\b', p_lower):
            return 0.2
        
        return 1.0  # No red flags
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Score and rank candidates using CDAS-MS."""
        if not candidates:
            return []
        
        prompt_graph = self._parse_clause_graph(prompt)
        best_genome = self._evolve_architecture(prompt_graph, candidates)
        
        results = []
        for cand in candidates:
            cand_graph = self._parse_clause_graph(cand)
            
            # Structural score (50%+)
            struct_score = 0.0
            if prompt_graph['numbers'] and cand_graph['numbers']:
                p_nums = sorted(prompt_graph['numbers'])
                c_nums = sorted(cand_graph['numbers'])
                struct_score += 0.3 * (1.0 / (1.0 + abs(len(p_nums) - len(c_nums))))
            
            struct_score += 0.2 * (1.0 / (1.0 + abs(prompt_graph['negations'] - cand_graph['negations'])))
            struct_score += 0.2 if (prompt_graph['conditionals'] and cand_graph['conditionals']) else 0.0
            struct_score += 0.1 if (prompt_graph['comparatives'] and cand_graph['comparatives']) else 0.0
            
            # Computational score (20%+)
            comp_score = 0.0
            if prompt_graph['numbers'] and cand_graph['numbers']:
                # Simple numeric check: do candidate numbers relate to prompt numbers?
                p_max = max(prompt_graph['numbers']) if prompt_graph['numbers'] else 1
                c_max = max(cand_graph['numbers']) if cand_graph['numbers'] else 1
                comp_score = 1.0 / (1.0 + abs(np.log1p(p_max) - np.log1p(c_max)))
            else:
                comp_score = 0.5
            
            # Metamorphic consistency (genome-weighted)
            mr_score = 0.0
            mr_types = ['negate', 'numeric_double', 'comparative_swap', 'conditional_reverse']
            for i, mr in enumerate(mr_types[:len(best_genome)]):
                consistency = self._compute_consistency(prompt_graph, cand, mr)
                mr_score += best_genome[i] * consistency
            mr_score /= (np.sum(best_genome[:len(mr_types)]) + 1e-6)
            
            # NCD (max 15%)
            ncd_score = 1.0 - self._compute_ncd(prompt, cand)
            
            # Final score
            score = 0.5 * struct_score + 0.25 * comp_score + 0.15 * mr_score + 0.1 * ncd_score
            
            reasoning = f"Struct={struct_score:.2f}, Comp={comp_score:.2f}, MR={mr_score:.2f}, NCD={ncd_score:.2f}"
            results.append({'candidate': cand, 'score': score, 'reasoning': reasoning})
        
        return sorted(results, key=lambda x: x['score'], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1, capped by meta-cognitive checks."""
        meta_conf = self._meta_confidence(prompt)
        
        prompt_graph = self._parse_clause_graph(prompt)
        answer_graph = self._parse_clause_graph(answer)
        
        # Structural alignment confidence
        align_conf = 0.5
        if prompt_graph['numbers'] and answer_graph['numbers']:
            align_conf = 0.7
        if prompt_graph['conditionals'] and answer_graph['conditionals']:
            align_conf = min(align_conf + 0.2, 0.9)
        if not prompt_graph['numbers'] and not prompt_graph['conditionals'] and not prompt_graph['comparatives']:
            align_conf = 0.3  # Low structure = low confidence
        
        return min(meta_conf, align_conf)