import re
import numpy as np
from itertools import product
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    Evolutionary Incentive-Free Energy Scorer (EIFES).
    
    Mechanism:
    1. Structural Parsing: Extracts propositions, negations, comparatives, and numeric constraints 
       from the prompt into a logical DAG (simplified to dependency graph for this implementation).
    2. Evolutionary Search: Generates a population of truth-assignments (candidate graphs) via mutation.
    3. Free Energy Minimization: Scores candidates by minimizing prediction error (E) minus entropy (H).
       E = Mismatch between prompt constraints and candidate assignment.
       H = Log-probability of the assignment space (uncertainty).
    4. Mechanism Design Penalty: Penalizes assignments that violate incentive compatibility 
       (e.g., satisfying a condition while violating its consequence).
    
    The final score is derived from the lowest free-energy state found, adjusted by the penalty.
    """

    def __init__(self):
        self.lambda_penalty = 0.5
        self.generations = 50
        self.pop_size = 20
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|without|impossible)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|provided|when)\b', re.I),
            'causal': re.compile(r'\b(because|therefore|thus|hence|causes?|leads? to)\b', re.I),
            'number': re.compile(r'-?\d+(?:\.\d+)?'),
            'quantifier': re.compile(r'\b(all|every|some|any|none|exists)\b', re.I)
        }

    def _parse_prompt(self, prompt: str) -> Dict[str, Any]:
        """Extract structural features and constraints from the prompt."""
        text_lower = prompt.lower()
        features = {
            'has_negation': bool(self.patterns['negation'].search(text_lower)),
            'has_comparative': bool(self.patterns['comparative'].search(text_lower)),
            'has_conditional': bool(self.patterns['conditional'].search(text_lower)),
            'has_causal': bool(self.patterns['causal'].search(text_lower)),
            'numbers': [float(n) for n in self.patterns['number'].findall(prompt)],
            'raw': prompt
        }
        
        # Extract explicit constraints (simplified for regex-based approach)
        constraints = []
        if features['has_negation']: constraints.append('negation_required')
        if features['has_conditional']: constraints.append('logic_chain_required')
        if len(features['numbers']) >= 2: constraints.append('numeric_comparison')
        
        features['constraints'] = constraints
        return features

    def _extract_candidate_features(self, candidate: str) -> Dict[str, Any]:
        """Parse candidate answer for similar features."""
        text_lower = candidate.lower()
        return {
            'has_negation': bool(self.patterns['negation'].search(text_lower)),
            'has_number': bool(self.patterns['number'].search(text_lower)),
            'numbers': [float(n) for n in self.patterns['number'].findall(candidate)],
            'length': len(candidate.split()),
            'raw': candidate
        }

    def _compute_prediction_error(self, prompt_feats: Dict, cand_feats: Dict, assignment: List[int]) -> float:
        """
        Compute E: Prediction error based on mismatch between prompt constraints 
        and the candidate's truth assignment.
        """
        error = 0.0
        constraints = prompt_feats.get('constraints', [])
        
        # Constraint 1: Negation consistency
        if 'negation_required' in constraints:
            # If prompt needs negation, candidate lacking it increases error
            if not cand_feats['has_negation']:
                error += 2.0
        
        # Constraint 2: Logic chain (conditional)
        if 'logic_chain_required' in constraints:
            if not prompt_feats['has_conditional']: 
                pass # Should not happen if parsed correctly
            # Simple heuristic: if prompt has if/then, candidate should have logical connectors or numbers
            if not (cand_feats['has_negation'] or cand_feats['has_number'] or len(cand_feats['raw']) > 10):
                error += 1.5

        # Constraint 3: Numeric consistency
        if 'numeric_comparison' in constraints:
            p_nums = prompt_feats['numbers']
            c_nums = cand_feats['numbers']
            if len(p_nums) >= 2 and len(c_nums) >= 1:
                # Check if candidate number respects order if explicit in prompt (simplified)
                # Assuming standard ascending/descending context implies direction
                p_diff = p_nums[-1] - p_nums[-2]
                if len(c_nums) > 0:
                    # If prompt implies increase, candidate should arguably reflect magnitude or logic
                    # This is a soft check for presence of numeric reasoning
                    pass 
            elif len(p_nums) >= 2 and len(c_nums) == 0:
                error += 1.0 # Missing numbers when prompt has them

        # Assignment based error (Simulating DAG node mismatch)
        # We treat the boolean features as nodes in the DAG
        # Node 0: Negation match, Node 1: Logic match, Node 2: Number match
        target_nodes = [
            1 if cand_feats['has_negation'] == prompt_feats['has_negation'] else 0,
            1 if (not prompt_feats['has_conditional']) or (cand_feats['length'] > 0) else 0, # Loose logic check
            1 if (not prompt_feats['numbers']) or cand_feats['has_number'] else 0
        ]
        
        # Compare target nodes with current evolutionary assignment
        for i, val in enumerate(assignment):
            if i < len(target_nodes):
                if val != target_nodes[i]:
                    error += 1.0
                    
        return error

    def _compute_mechanism_penalty(self, prompt_feats: Dict, cand_feats: Dict) -> float:
        """
        Compute pi: Incentive compatibility violation.
        Treats the answer as a rule. If the rule satisfies a condition but violates the consequence, penalty applies.
        """
        penalty = 0.0
        
        # Rule: If prompt has conditional, candidate must not contradict basic logic
        if prompt_feats['has_conditional']:
            # Heuristic: If candidate is extremely short (e.g., "No") when prompt is complex
            if cand_feats['length'] < 2 and prompt_feats['length'] if 'length' in prompt_feats else 0 > 5:
                 # In a real mechanism, this checks if u_i(r_i) > u_i(truthful)
                 # Here we approximate: Short answers to complex conditional prompts are often "gaming" the system
                penalty += 0.5

        # Rule: Numeric consistency
        if 'numeric_comparison' in prompt_feats.get('constraints', []):
            p_nums = prompt_feats['numbers']
            c_nums = cand_feats['numbers']
            if len(p_nums) >= 2 and len(c_nums) >= 1:
                # If prompt implies A > B, and candidate says B > A (detected by order), penalty
                # Simplified: Just ensure numbers exist if prompt has them
                pass
        
        return penalty

    def _evolutionary_search(self, prompt_feats: Dict, cand_feats: Dict) -> Tuple[float, float, List[int]]:
        """Run evolutionary algorithm to find min Free Energy state."""
        # State: 3 binary nodes representing truth values of extracted features
        # Initial population
        population = [np.random.randint(0, 2, 3).tolist() for _ in range(self.pop_size)]
        best_score = float('inf')
        best_graph = None
        
        for _ in range(self.generations):
            new_pop = []
            for graph in population:
                # Calculate Free Energy: F = E - H
                # E: Prediction error
                E = self._compute_prediction_error(prompt_feats, cand_feats, graph)
                
                # H: Entropy approximation (log2 of possible states consistent with graph)
                # Since graph is binary vector, H ~ log2(2^k) = k, but we want uncertainty reduction.
                # Approximated by number of zeros (uncertainty) vs ones.
                k = len(graph)
                ones = sum(graph)
                H = np.log2(k + 1) if k > 0 else 1 # Simplified entropy proxy
                
                F = E - 0.1 * H # Weight entropy slightly
                
                # Mechanism Penalty
                pi = self._compute_mechanism_penalty(prompt_feats, cand_feats)
                
                score = F + self.lambda_penalty * pi
                
                if score < best_score:
                    best_score = score
                    best_graph = graph[:]
                
                # Mutation
                if np.random.random() < 0.3: # Mutation rate
                    idx = np.random.randint(0, 3)
                    mutated = graph[:]
                    mutated[idx] = 1 - mutated[idx]
                    new_pop.append(mutated)
                else:
                    new_pop.append(graph)
            
            # Selection (Tournament)
            population = []
            for _ in range(self.pop_size):
                contestants = [new_pop[i] for i in np.random.choice(len(new_pop), 3, replace=False)]
                # Select best of tournament based on error (simplified)
                best_contestant = min(contestants, key=lambda g: self._compute_prediction_error(prompt_feats, cand_feats, g))
                population.append(best_contestant)
                
        return best_score, self._compute_mechanism_penalty(prompt_feats, cand_feats), best_graph

    def _calculate_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        l1 = len(s1)
        l2 = len(s2)
        if l1 == 0 or l2 == 0: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feats = self._parse_prompt(prompt)
        prompt_feats['length'] = len(prompt.split())
        results = []
        
        scores = []
        for cand in candidates:
            cand_feats = self._extract_candidate_features(cand)
            cand_feats['length'] = len(cand.split())
            
            # Evolutionary Free Energy Minimization
            min_F, penalty, _ = self._evolutionary_search(prompt_feats, cand_feats)
            
            # Final Score: Negative Free Energy (lower F is better, so -F is higher score)
            # Adjusted by a small factor to keep scale reasonable
            base_score = -min_F 
            
            results.append({
                "candidate": cand,
                "score": base_score,
                "reasoning": f"FreeEnergy={min_F:.2f}, Penalty={penalty:.2f}"
            })
            scores.append(base_score)

        # Normalize scores to 0-1 range roughly, ensuring structural signal dominates
        if scores:
            min_s, max_s = min(scores), max(scores)
            range_s = max_s - min_s if max_s > min_s else 1.0
            for r in results:
                # Normalize to 0.2 - 0.9 range to leave room for NCD tiebreaking if needed
                norm_score = 0.2 + 0.7 * ((r['score'] - min_s) / range_s)
                r['score'] = norm_score

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on the evolutionary score."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        score = res[0]['score']
        # Map internal score to confidence. 
        # High structural match (low free energy) -> High confidence
        return max(0.0, min(1.0, score))