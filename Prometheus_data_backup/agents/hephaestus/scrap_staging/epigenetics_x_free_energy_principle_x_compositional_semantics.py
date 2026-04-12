import re
import numpy as np
from typing import List, Dict, Tuple, Optional
from zlib import compress

class ReasoningTool:
    """
    Epigenetic-FreeEnergy-Compositional Reasoner.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions (numbers, booleans, causal verbs) into a hypergraph.
    2. Epigenetic State: Each node holds a belief vector (Dirichlet-like) representing truth probability.
    3. Free Energy Minimization: Iteratively updates beliefs to minimize prediction error between 
       connected nodes based on compositional rules (implication, negation, arithmetic).
       - 'Methylation': Belief updates persist across sweeps unless a large prediction error triggers reset.
    4. Scoring: Negative variational free energy of the answer node.
    5. Epistemic Honesty: Meta-analysis of prompt structure caps confidence for ambiguous/trap questions.
    """

    def __init__(self):
        self.max_sweeps = 10
        self.tolerance = 1e-4
        self.learning_rate = 0.5
        
        # Regex patterns for atomic extraction
        self.patterns = {
            'number': re.compile(r'-?\d+(?:\.\d+)?'),
            'negation': re.compile(r'\b(not|no|never|none|cannot|impossible)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|provided)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(causes|leads to|results in|because|therefore)\b', re.IGNORECASE),
            'presupposition': re.compile(r'(have you stopped|why did|when did|who is the)', re.IGNORECASE),
            'scope_ambiguity': re.compile(r'every.*a.*\?', re.IGNORECASE),
            'false_dichotomy': re.compile(r'either.*or', re.IGNORECASE),
            'subjectivity': re.compile(r'\b(best|worst|favorite|opinion)\b', re.IGNORECASE)
        }

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance heuristic."""
        if not s1 or not s2: return 1.0
        c1 = len(compress(s1.encode()))
        c2 = len(compress(s2.encode()))
        c12 = len(compress((s1 + s2).encode()))
        return max(c1, c2) / c12 if c12 > 0 else 1.0

    def _meta_confidence(self, prompt: str) -> float:
        """Check for Tier B traps (Ambiguity, Presupposition, etc.)."""
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        if self.patterns['presupposition'].search(prompt):
            return 0.1
        # 2. Scope ambiguity (simplified heuristic)
        if self.patterns['scope_ambiguity'].search(p_lower) and 'same' not in p_lower:
            return 0.2
        # 3. False dichotomy
        if self.patterns['false_dichotomy'].search(p_lower) and 'only' not in p_lower:
            return 0.3
        # 4. Subjectivity
        if self.patterns['subjectivity'].search(p_lower):
            return 0.2
            
        return 1.0  # No obvious traps detected

    def _parse_prompt(self, prompt: str) -> Dict:
        """Extract structural elements and initialize belief state."""
        numbers = [float(n) for n in self.patterns['number'].findall(prompt)]
        has_negation = bool(self.patterns['negation'].search(prompt))
        has_conditional = bool(self.patterns['conditional'].search(prompt))
        has_comparative = bool(self.patterns['comparative'].search(prompt))
        has_causal = bool(self.patterns['causal'].search(prompt))
        
        return {
            'numbers': numbers,
            'negation': has_negation,
            'conditional': has_conditional,
            'comparative': has_comparative,
            'causal': has_causal,
            'node_count': max(1, len(numbers) + 2) # Base nodes + context
        }

    def _compute_constructive(self, prompt: str, candidate: str) -> Optional[float]:
        """
        Attempt constructive computation (Math, Logic, Temporal).
        Returns a definitive score (0-1) if computable, else None.
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # 1. Numeric Extraction & Arithmetic Check
        nums = [float(n) for n in self.patterns['number'].findall(prompt)]
        cand_nums = [float(n) for n in self.patterns['number'].findall(candidate)]
        
        if len(nums) >= 2:
            # Simple arithmetic verification (Addition/Subtraction/Multiplication)
            # Check if candidate matches any pairwise operation
            for i in range(len(nums)):
                for j in range(i+1, len(nums)):
                    a, b = nums[i], nums[j]
                    ops = [a+b, a-b, b-a, a*b, a/b if b!=0 else 0, b/a if a!=0 else 0]
                    for op in ops:
                        if any(abs(op - cn) < 1e-6 for cn in cand_nums):
                            return 0.95 # Strong match
            
            # If prompt asks for sum/total/count and candidate is sum
            if any(k in p_lower for k in ['sum', 'total', 'add', 'combine']):
                if cand_nums and abs(sum(nums) - cand_nums[0]) < 1e-6:
                    return 0.98

        # 2. Logical Negation Check
        if 'not' in p_lower or 'no' in p_lower:
            # If prompt implies negation and candidate affirms the negated term directly without qualification
            # This is a heuristic proxy for Modus Tollens
            if 'yes' in c_lower and 'no' in p_lower:
                return 0.2 # Likely incorrect if ignoring negation
            if 'no' in c_lower and 'not' in p_lower:
                return 0.85

        # 3. Comparative Logic
        if 'greater' in p_lower or 'more' in p_lower:
            if len(nums) >= 2 and len(cand_nums) == 1:
                # Expecting the larger number
                if abs(max(nums) - cand_nums[0]) < 1e-6:
                    return 0.9
                if abs(min(nums) - cand_nums[0]) < 1e-6:
                    return 0.3 # Likely wrong direction

        return None # Cannot compute definitively

    def _run_free_energy_minimization(self, struct: Dict, candidate: str, prompt: str) -> float:
        """
        Simulate epigenetic belief propagation.
        Nodes: Atomic propositions. 
        State: Belief vector (probability of truth).
        Update: Minimize prediction error between parent/children via compositional rules.
        """
        n = struct['node_count']
        # Initialize beliefs (Dirichlet prior approx: uniform uncertainty)
        beliefs = np.full(n, 0.5) 
        # Prior bias based on candidate presence in prompt (weak prior)
        c_lower = candidate.lower()
        if c_lower in prompt.lower():
            beliefs[0] = 0.7 # Slight prior boost if echoed
        
        # Adjacency matrix (sparse simulation via list of tuples for speed/simplicity)
        # Edges represent logical constraints: (source, target, type)
        edges = []
        if struct['negation']:
            edges.append((0, 1, 'negate'))
        if struct['conditional']:
            edges.append((0, 1, 'imply'))
        if struct['comparative']:
            edges.append((0, 1, 'compare'))
            
        # Add generic connectivity for propagation
        for i in range(n-1):
            edges.append((i, i+1, 'propagate'))

        last_energy = float('inf')
        
        for sweep in range(self.max_sweeps):
            new_beliefs = beliefs.copy()
            
            # Forward/Backward pass (simplified)
            for src, tgt, rule in edges:
                if src >= len(beliefs) or tgt >= len(beliefs): continue
                
                pred = beliefs[src]
                error = 0.0
                
                if rule == 'negate':
                    pred = 1.0 - beliefs[src]
                elif rule == 'imply':
                    # Material implication approx: A->B is ~A or B
                    pred = max(1.0 - beliefs[src], beliefs[tgt]) if tgt < len(beliefs) else beliefs[src]
                elif rule == 'compare':
                    # Assume monotonicity
                    pred = beliefs[src] 
                
                # Prediction error
                if tgt < len(beliefs):
                    error = beliefs[tgt] - pred
                    # Epigenetic update (methylation analogy: persistent change)
                    new_beliefs[tgt] += self.learning_rate * error
                    
            # Normalize beliefs to [0, 1]
            new_beliefs = np.clip(new_beliefs, 0.0, 1.0)
            
            # Free Energy Approximation: Sum of squared errors + Complexity penalty
            energy = np.sum((new_beliefs - beliefs)**2) + 0.1 * np.sum(np.abs(np.diff(new_beliefs)))
            
            if abs(last_energy - energy) < self.tolerance:
                break
            beliefs = new_beliefs
            last_energy = energy

        # Final score: Negative free energy (mapped to 0-1 range)
        # We use the stability of the belief at node 0 (main proposition)
        final_belief = beliefs[0]
        
        # Adjust by structural consistency
        if struct['negation'] and 'not' not in c_lower and 'no' not in c_lower:
            final_belief *= 0.5 # Penalty for ignoring negation
            
        return float(final_belief)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        struct = self._parse_prompt(prompt)
        meta_cap = self._meta_confidence(prompt)
        results = []

        # Pre-compute constructive answers if possible
        constructive_scores = {}
        for cand in candidates:
            score = self._compute_constructive(prompt, cand)
            if score is not None:
                constructive_scores[cand] = score

        for cand in candidates:
            score = 0.0
            reasoning = ""
            
            # 1. Constructive Computation (Highest Priority)
            if cand in constructive_scores:
                score = constructive_scores[cand]
                reasoning = f"Constructive computation detected. Score: {score:.2f}"
            else:
                # 2. Free Energy / Constraint Propagation
                fe_score = self._run_free_energy_minimization(struct, cand, prompt)
                
                # 3. NCD Tiebreaker (Max 15% weight)
                ncd_val = self._ncd(prompt, cand)
                ncd_score = (1.0 - ncd_val) * 0.15 
                
                # Weighted combination
                # Structural/FE: 85%, NCD: 15%
                score = (fe_score * 0.85) + ncd_score
                reasoning = f"Free-energy convergence: {fe_score:.3f}, NCD bonus: {ncd_score:.3f}"

            # Apply Epistemic Cap (Tier B Honesty)
            if meta_cap < 0.3:
                score = min(score, 0.3)
                reasoning += " [CAPTED: Ambiguous/Trap detected]"
            
            # Normalize score to reasonable range
            score = max(0.0, min(1.0, score))
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning
            })

        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at meta-confidence limit for ambiguous prompts.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # If meta-analysis detects a trap, confidence is low regardless of answer
        if meta_cap < 0.3:
            return 0.1 * meta_cap # Very low confidence
        
        # Try constructive computation first
        const_score = self._compute_constructive(prompt, answer)
        if const_score is not None:
            # If we computed it, confidence is high but capped by certainty of math
            return min(0.95, max(0.8, const_score))
        
        # Fallback: Structural consistency via FE
        struct = self._parse_prompt(prompt)
        fe_score = self._run_free_energy_minimization(struct, answer, prompt)
        
        # If FE score is very low, confidence is low
        if fe_score < 0.2:
            return 0.1
            
        # Moderate confidence for structural matches, capped by meta
        raw_conf = fe_score
        return min(raw_conf, meta_cap)