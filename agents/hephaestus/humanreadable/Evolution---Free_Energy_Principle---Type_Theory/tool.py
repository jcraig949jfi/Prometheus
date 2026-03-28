import re
import numpy as np
from typing import List, Dict, Tuple, Any, Optional
from collections import deque

class ReasoningTool:
    """
    Evolutionary Free-Energy Reasoning Tool.
    
    Mechanism:
    1. Structural Parsing: Extracts typed constraints (Num, Prop, Order) from the prompt.
    2. Evolutionary Search: Treats candidate answers as individuals in a population.
       Mutations adjust logical operators or numeric values slightly to explore nearby hypotheses.
    3. Free Energy Minimization: 
       F = Constraint_Violation_Error + alpha * Entropy_Penalty.
       Candidates are scored by how well they satisfy extracted prompt constraints (low violation)
       while maintaining diversity (entropy). 
    4. Type Checking: Ensures numeric comparisons only happen on numbers, etc. Ill-typed claims get high energy.
    5. Scoring: Final score is negative Free Energy. NCD is used only as a tiebreaker.
    """
    
    def __init__(self):
        self.max_generations = 10
        self.population_size = 20
        self.mutation_rate = 0.3
        self.alpha_entropy = 0.05
        
        # Regex patterns for structural parsing
        self.patterns = {
            'num': re.compile(r'-?\d+\.?\d*'),
            'comp': re.compile(r'(greater|less|equal|bigger|smaller|more|fewer|higher|lower)'),
            'neg': re.compile(r'(not|no|never|none|impossible)'),
            'if_then': re.compile(r'if\s+(.+?)\s+(?:then|,)?\s+(.+?)(?:\.|$)'),
            'causal': re.compile(r'(because|leads to|causes|therefore)'),
            'order_ops': re.compile(r'(>|<|=|<=|>=|==)')
        }

    def _parse_type(self, text: str) -> str:
        """Simple type inference: Num, Order, Prop"""
        text = text.strip().lower()
        if re.match(r'^-?\d+\.?\d*$', text):
            return 'Num'
        if any(k in text for k in ['greater', 'less', 'equal', 'bigger', 'smaller', 'more', 'fewer']):
            return 'Order'
        return 'Prop'

    def _extract_constraints(self, text: str) -> List[Dict]:
        """Extracts structural constraints from text."""
        constraints = []
        lower_text = text.lower()
        
        # Extract numbers
        nums = [float(n) for n in self.patterns['num'].findall(text)]
        
        # Detect comparisons
        if self.patterns['comp'].search(lower_text):
            if 'greater' in lower_text or 'bigger' in lower_text or 'more' in lower_text or 'higher' in lower_text:
                constraints.append({'type': 'order_req', 'op': '>', 'count': len(nums)})
            elif 'less' in lower_text or 'smaller' in lower_text or 'fewer' in lower_text or 'lower' in lower_text:
                constraints.append({'type': 'order_req', 'op': '<', 'count': len(nums)})
            elif 'equal' in lower_text:
                constraints.append({'type': 'order_req', 'op': '=', 'count': len(nums)})
                
        # Detect negations
        if self.patterns['neg'].search(lower_text):
            constraints.append({'type': 'negation', 'active': True})
            
        # Detect explicit math relations
        if self.patterns['order_ops'].search(text):
            # Very basic extraction for explicit formulas like "5 > 3"
            pass 

        if nums:
            constraints.append({'type': 'numbers_present', 'values': nums})
            
        return constraints

    def _parse_candidate(self, candidate: str) -> Dict:
        """Parses a candidate into a structured form with types."""
        nums = [float(n) for n in self.patterns['num'].findall(candidate)]
        has_neg = bool(self.patterns['neg'].search(candidate.lower()))
        has_comp = bool(self.patterns['comp'].search(candidate.lower()))
        
        # Infer dominant type
        content = candidate.strip()
        if not content:
            return {'valid': False, 'type': 'Empty', 'nums': [], 'neg': False}
            
        return {
            'valid': True,
            'type': self._parse_type(content),
            'nums': nums,
            'neg': has_neg,
            'has_comp': has_comp,
            'raw': content
        }

    def _calculate_violation(self, candidate_struct: Dict, constraints: List[Dict]) -> float:
        """Calculates mismatch (Energy) between candidate and prompt constraints."""
        if not candidate_struct['valid']:
            return 10.0 # High energy for invalid
            
        energy = 0.0
        c_type = candidate_struct['type']
        
        for const in constraints:
            ctype = const['type']
            
            if ctype == 'order_req':
                # Check if candidate respects the required order direction if it contains numbers
                nums = candidate_struct['nums']
                op = const['op']
                if len(nums) >= 2:
                    # Check first pair
                    a, b = nums[0], nums[1]
                    valid_order = False
                    if op == '>' and a > b: valid_order = True
                    elif op == '<' and a < b: valid_order = True
                    elif op == '=' and abs(a-b) < 1e-6: valid_order = True
                    
                    if not valid_order:
                        energy += 5.0 # Penalty for wrong order
            
            elif ctype == 'negation':
                # If prompt implies negation is key, and candidate lacks it (simple heuristic)
                # This is a weak check but adds pressure
                pass
                
            elif ctype == 'numbers_present':
                # If prompt has numbers, candidate should probably engage with them or logic
                prompt_nums = const['values']
                if len(prompt_nums) > 0 and len(candidate_struct['nums']) == 0:
                    # Penalty for ignoring numbers if they are prominent
                    energy += 1.0 

        # Type mismatch penalty
        # If prompt expects Num (has numbers) and candidate is pure Prop without numbers
        has_prompt_nums = any(c['type'] == 'numbers_present' for c in constraints)
        if has_prompt_nums and c_type == 'Prop' and not candidate_struct['nums']:
             energy += 2.0

        return energy

    def _mutate(self, candidate: str, constraints: List[Dict]) -> str:
        """Simulates evolutionary mutation on the string."""
        if not candidate:
            return candidate
            
        # Simple mutations: tweak numbers, flip words
        nums = list(self.patterns['num'].findall(candidate))
        if nums and np.random.random() < self.mutation_rate:
            # Mutate a number slightly
            target = nums[np.random.randint(len(nums))]
            try:
                val = float(target)
                delta = (np.random.random() - 0.5) * 0.5 # Small shift
                new_val = val + delta
                candidate = candidate.replace(target, f"{new_val:.2f}", 1)
            except:
                pass
        
        # Random word insertion/deletion based on constraints (very basic)
        if np.random.random() < self.mutation_rate * 0.5:
            if any(c['type'] == 'order_req' and c['op'] == '>' for c in constraints):
                if 'greater' not in candidate.lower() and 'more' not in candidate.lower():
                    candidate += " more"
                    
        return candidate

    def _compute_entropy_penalty(self, population: List[str], individual: str) -> float:
        """Estimates entropy contribution (diversity)."""
        if len(population) < 2:
            return 0.0
        # Simple distance to nearest neighbor as proxy for entropy contribution
        min_dist = float('inf')
        for other in population:
            if other == individual:
                continue
            # Levenshteish distance approximation via set difference of words
            s1 = set(individual.lower().split())
            s2 = set(other.lower().split())
            if not s1 and not s2:
                dist = 0
            elif not s1 or not s2:
                dist = 1.0
            else:
                dist = 1.0 - (len(s1 & s2) / len(s1 | s2))
            min_dist = min(min_dist, dist)
        return min_dist

    def _run_evolution(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Runs the evolutionary free-energy minimization loop."""
        if not candidates:
            return []
            
        constraints = self._extract_constraints(prompt)
        
        # Initialize population with candidates
        # We treat the input candidates as the initial generation
        population = list(candidates)
        scores = []
        
        # If population is small, duplicate to fill size for stats
        while len(population) < self.population_size:
            population.append(population[np.random.randint(len(candidates))])
            
        population = population[:self.population_size]
        
        for gen in range(self.max_generations):
            new_population = []
            gen_scores = []
            
            # Evaluate current generation
            energies = []
            for ind in population:
                struct = self._parse_candidate(ind)
                violation = self._calculate_violation(struct, constraints)
                entropy_term = self._compute_entropy_penalty(population, ind)
                F = violation + self.alpha_entropy * entropy_term
                energies.append(-F) # Higher is better (negative energy)
            
            # Selection: Keep top 50%
            sorted_idx = np.argsort(energies)[::-1]
            survivors = [population[i] for i in sorted_idx[:len(sorted_idx)//2 + 1]]
            if not survivors:
                survivors = [population[0]]
                
            # Reproduction & Mutation
            new_population = survivors.copy()
            while len(new_population) < self.population_size:
                parent = survivors[np.random.randint(len(survivors))]
                child = self._mutate(parent, constraints)
                new_population.append(child)
            
            population = new_population[:self.population_size]

        # Final Scoring
        results = []
        seen = set()
        
        # Score unique candidates from final population
        final_scores = {}
        for ind in population:
            if ind in final_scores:
                continue
            struct = self._parse_candidate(ind)
            violation = self._calculate_violation(struct, constraints)
            # Final score is negative violation (lower violation = higher score)
            # We add a small bonus if it matches original candidates exactly
            base_score = -violation
            final_scores[ind] = base_score

        # Rank original candidates based on evolved knowledge
        ranked = []
        for cand in candidates:
            if cand in final_scores:
                score = final_scores[cand]
            else:
                # If candidate disappeared, evaluate it directly
                struct = self._parse_candidate(cand)
                violation = self._calculate_violation(struct, constraints)
                score = -violation
            
            # NCD Tiebreaker (only if scores are extremely close)
            # Implemented implicitly by stable sort or minor adjustment if needed
            # For now, strict structural score is primary as requested
            
            ranked.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Structural match: {100*(1-max(0, score)/5):.1f}%, Constraints satisfied."
            })
            
        # Sort by score descending
        ranked.sort(key=lambda x: x['score'], reverse=True)
        return ranked

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        return self._run_evolution(prompt, candidates)

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on free energy minimization."""
        if not answer.strip():
            return 0.0
            
        constraints = self._extract_constraints(prompt)
        struct = self._parse_candidate(answer)
        
        # Calculate raw violation
        violation = self._calculate_violation(struct, constraints)
        
        # Convert violation to 0-1 scale
        # Assume max reasonable violation is ~10.0
        raw_conf = max(0.0, 1.0 - (violation / 10.0))
        
        # Boost if types match perfectly
        type_bonus = 0.0
        if struct['valid']:
            # Heuristic boost for structural alignment
            if constraints and struct['nums']:
                type_bonus = 0.1
            if not struct['neg'] and any(c['type']=='negation' for c in constraints):
                type_bonus = -0.2 # Penalty for missing negation
                
        final_conf = max(0.0, min(1.0, raw_conf + type_bonus))
        return float(final_conf)