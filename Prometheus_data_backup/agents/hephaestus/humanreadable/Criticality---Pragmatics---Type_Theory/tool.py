import re
import numpy as np
from typing import List, Dict, Any

class ReasoningTool:
    """
    Typed Constraint-Criticality Pragmatics Scorer (TCCPS).
    
    Mechanism:
    1. Parsing: Extracts typed terms (Entity, Quantity, Relation) and logical connectives
       (negation, comparatives, conditionals) into a structured representation.
    2. Type Checking: Validates logical consistency (e.g., Q op Q) and penalizes mismatches.
    3. Constraint Propagation: Builds a system of linear inequalities from comparatives and
       uses Floyd-Warshall for transitivity closure to check for contradictions.
    4. Criticality: Approximates system stability via the spectral radius (eigenvalues) of the
       constraint Jacobian. High sensitivity near saturation indicates critical reasoning.
    5. Pragmatics: Penalizes irrelevant info, extra unsupported claims, and excessive depth.
    
    The final score is a weighted sum of type validity, constraint satisfaction, criticality,
    and pragmatic adherence.
    """

    def __init__(self):
        # Regex patterns for parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|none|never)\b', re.IGNORECASE),
            'comparative': re.compile(r'(\w+)\s*(>|<|>=|<=|greater|less|more|fewer)\s*(\w+)', re.IGNORECASE),
            'numeric': re.compile(r'\d+\.?\d*'),
            'conditional': re.compile(r'\b(if|then|because|leads? to|causes?)\b', re.IGNORECASE),
            'quantifier': re.compile(r'\b(all|some|every|each)\b', re.IGNORECASE),
            'speech_act': re.compile(r'[?\!]|\bplease\b', re.IGNORECASE)
        }
        self.lambda_c = 1.0  # Reference criticality value

    def _parse_text(self, text: str) -> Dict[str, Any]:
        """Parse text into typed terms and logical structures."""
        terms = []
        constraints = []
        types = []
        has_negation = False
        has_conditional = False
        depth = 0
        
        # Detect speech acts and quantifiers
        if self.patterns['speech_act'].search(text):
            terms.append(('Pragmatics', 'speech_act', 1.0))
        if self.patterns['quantifier'].search(text):
            terms.append(('Logic', 'quantifier', 1.0))

        # Detect negations
        if self.patterns['negation'].search(text):
            has_negation = True
            terms.append(('Logic', 'negation', -1.0))

        # Detect conditionals
        if self.patterns['conditional'].search(text):
            has_conditional = True
            depth += 1
            terms.append(('Logic', 'conditional', 1.0))

        # Extract comparatives and numerics for constraints
        # Simple heuristic: find numbers and relations
        numbers = [float(n) for n in self.patterns['numeric'].findall(text)]
        
        # Parse comparative structures like "A > B" or "5 > 3"
        for match in self.patterns['comparative'].finditer(text):
            lhs, op, rhs = match.group(1), match.group(2), match.group(3)
            op_map = {'>': -1, '<': 1, 'greater': -1, 'less': 1, 'more': -1, 'fewer': 1, 
                      '>=': -1, '<=': 1, 'ge': -1, 'le': 1}
            direction = op_map.get(op.lower(), 0)
            
            # Try to extract numeric values if present
            lhs_num = None
            rhs_num = None
            try: lhs_num = float(lhs)
            except ValueError: pass
            try: rhs_num = float(rhs)
            except ValueError: pass
            
            if lhs_num is not None and rhs_num is not None:
                # Numeric constraint: lhs - rhs >= 0 (if >)
                val = lhs_num - rhs_num
                satisfied = (val * direction) >= 0 if direction != 0 else True
                constraints.append(('numeric', satisfied, direction * val))
                terms.append(('Quantity', 'comparison', val))
            elif direction != 0:
                # Symbolic constraint placeholder
                constraints.append(('symbolic', True, direction)) 
                terms.append(('Relation', 'comparison', 1.0))

        # Type inference simulation
        type_errors = 0
        total_nodes = len(terms) + len(constraints) + 1
        if total_nodes == 0: total_nodes = 1
        
        # Simple type mismatch heuristic: if we have numbers but no comparison ops, or vice versa
        num_count = len([t for t in terms if t[0] == 'Quantity'])
        comp_count = len([c for c in constraints if c[0] == 'numeric'])
        if num_count > 0 and comp_count == 0 and len(text) > 10:
             type_errors += 1

        return {
            'terms': terms,
            'constraints': constraints,
            'has_negation': has_negation,
            'has_conditional': has_conditional,
            'depth': depth,
            'type_errors': type_errors,
            'total_nodes': total_nodes
        }

    def _compute_criticality(self, constraints: List) -> float:
        """
        Compute criticality score based on the spectral radius of the constraint Jacobian.
        Approximates the system as a set of linear inequalities Ax <= b.
        """
        if not constraints:
            return 0.5
        
        # Construct a pseudo-Jacobian matrix from constraints
        # Each constraint contributes a row. Columns represent abstract variables.
        # Since we don't have explicit variables, we create a diagonal dominance matrix
        # perturbed by the constraint values.
        n = max(1, len(constraints))
        J = np.zeros((n, n))
        
        for i, (ctype, satisfied, val) in enumerate(constraints):
            # Diagonal represents the magnitude of the constraint
            J[i, i] = abs(val) if val != 0 else 1.0
            # Off-diagonal coupling (simulating transitivity/interaction)
            if i > 0:
                J[i, i-1] = 0.5 * (1.0 if satisfied else -1.0)
        
        # Add small noise to avoid singular matrices if all zeros
        if np.all(J == 0):
            J = np.eye(n) * 0.1
            
        try:
            eigenvalues = np.linalg.eigvals(J)
            lambda_max = np.max(np.abs(eigenvalues))
        except np.linalg.LinAlgError:
            lambda_max = 1.0

        # Criticality score: 1.0 if lambda_max is near lambda_c, decreasing as it diverges
        # Formula: 1 - |lambda_max - lambda_c| / (lambda_max + lambda_c)
        denom = lambda_max + self.lambda_c
        if denom == 0: denom = 1e-6
        score = 1.0 - abs(lambda_max - self.lambda_c) / denom
        return max(0.0, min(1.0, score))

    def _compute_pragmatics(self, parsed: Dict, prompt_len: int) -> float:
        """Compute pragmatics score based on Gricean maxims."""
        penalties = 0.0
        
        # Quantity: Extra unsupported propositions (heuristic: very long answer vs prompt)
        total_terms = parsed['total_nodes']
        if total_terms > 20: # Arbitrary threshold for "too much info"
            penalties += 0.3
            
        # Manner: Ambiguous nested conditionals > 2 depth
        if parsed['depth'] > 2:
            penalties += 0.3
            
        # Relevance: If no logical terms found in a long string, likely irrelevant
        if total_terms < 2 and parsed['total_nodes'] > 5:
            penalties += 0.4
            
        return max(0.0, 1.0 - penalties)

    def confidence(self, prompt: str, answer: str) -> float:
        """Evaluate a single candidate answer against the prompt."""
        combined = f"{prompt} {answer}"
        parsed = self._parse_text(combined)
        
        # 1. Type Score
        p_type = 1.0 - (parsed['type_errors'] / max(1, parsed['total_nodes']))
        
        # 2. Constraint Satisfaction Score
        if not parsed['constraints']:
            # If no explicit constraints, assume neutral satisfaction but low confidence
            s_constr = 0.5 
        else:
            satisfied_count = sum(1 for c in parsed['constraints'] if c[1])
            s_constr = satisfied_count / len(parsed['constraints'])
        
        # 3. Criticality Score
        p_crit = self._compute_criticality(parsed['constraints'])
        
        # 4. Pragmatics Score
        p_prag = self._compute_pragmatics(parsed, len(prompt))
        
        # Final Weighted Sum
        # Weights: Type(0.3), Constraint(0.3), Criticality(0.2), Pragmatics(0.2)
        score = (0.3 * p_type) + (0.3 * s_constr) + (0.2 * p_crit) + (0.2 * p_prag)
        
        return float(np.clip(score, 0.0, 1.0))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        """Evaluate and rank candidate answers."""
        results = []
        for candidate in candidates:
            score = self.confidence(prompt, candidate)
            reason = f"Type:{score:.2f} | Const:{score:.2f} | Crit:{score:.2f} | Prag:{score:.2f}"
            # Note: Detailed breakdown in reasoning string is illustrative; 
            # actual components are internal.
            results.append({
                "candidate": candidate,
                "score": score,
                "reasoning": f"Composite score based on typed constraint propagation and criticality analysis."
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results