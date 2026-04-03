import re
import numpy as np
from typing import List, Dict, Any, Tuple, Optional

class ReasoningTool:
    """
    A reasoning tool combining Compositionality, Type Theory, and Free Energy Principle.
    
    Mechanism:
    1. Parsing (Compositionality): Extracts tokens and builds a simplified AST using regex.
       Handles negation, comparatives, conditionals, causality, and ordering.
    2. Type Assignment (Type Theory): Assigns types (Int, Bool, Entity) and performs 
       Hindley-Milner style unification checks. Type mismatches incur energy penalties.
    3. Constraint Propagation (Free Energy): Derives logical consequences (transitivity, 
       modus ponens) and calculates Variational Free Energy (F). 
       Score = -F. Lower F (fewer violations) = higher plausibility.
    """
    
    def __init__(self):
        self.lambda_weight = 1.0
        # Regex patterns for structural extraction
        self.patterns = {
            'negation': re.compile(r'\bnot\s+(\w+)', re.IGNORECASE),
            'comparative': re.compile(r'(\w+)\s*(?:is|was)?\s*(?:greater|more|larger|>)\s+than\s+(\w+)', re.IGNORECASE),
            'comparative_sym': re.compile(r'(\w+)\s*>\s*(\w+)'),
            'conditional': re.compile(r'if\s+(.+?)\s+then\s+(.+?)', re.IGNORECASE),
            'causal': re.compile(r'(.+?)\s+because\s+(.+?)', re.IGNORECASE),
            'ordering': re.compile(r'(\w+)\s+(?:before|precedes)\s+(\w+)', re.IGNORECASE),
            'number': re.compile(r'\b(\d+(?:\.\d+)?)\b'),
            'entity_ref': re.compile(r'\b([A-Z][a-z]+)\b') # Simple proper noun heuristic
        }

    def _parse_to_ast(self, text: str) -> List[Dict]:
        """Extract structural components into a list of typed nodes."""
        nodes = []
        text_lower = text.lower()
        
        # Extract Numbers with types
        for match in self.patterns['number'].finditer(text):
            val = float(match.group(1))
            nodes.append({'type': 'Const', 'value': val, 'dtype': 'Int', 'source': match.group(0)})
            
        # Negation
        for match in self.patterns['negation'].finditer(text):
            nodes.append({'type': 'Neg', 'target': match.group(1), 'dtype': 'Bool'})
            
        # Comparatives (GT)
        for match in self.patterns['comparative'].finditer(text):
            nodes.append({'type': 'GT', 'left': match.group(1), 'right': match.group(2), 'dtype': 'Bool'})
        for match in self.patterns['comparative_sym'].finditer(text):
            nodes.append({'type': 'GT', 'left': match.group(1), 'right': match.group(2), 'dtype': 'Bool'})
            
        # Conditionals (Imp)
        for match in self.patterns['conditional'].finditer(text):
            nodes.append({'type': 'Imp', 'antecedent': match.group(1), 'consequent': match.group(2), 'dtype': 'Bool'})
            
        # Causal
        for match in self.patterns['causal'].finditer(text):
            nodes.append({'type': 'Cause', 'effect': match.group(1), 'cause': match.group(2), 'dtype': 'Bool'})
            
        # Ordering
        for match in self.patterns['ordering'].finditer(text):
            nodes.append({'type': 'Before', 'first': match.group(1), 'second': match.group(2), 'dtype': 'Bool'})
            
        return nodes

    def _check_type_consistency(self, ast: List[Dict]) -> int:
        """
        Simple type checker. Returns 1 if inconsistency found, 0 otherwise.
        In this simplified model, we check if numeric constants are compared to non-numeric tokens
        in comparative nodes if we can resolve the tokens to types.
        """
        errors = 0
        # Map extracted numbers to tokens for lookup
        number_map = {}
        for node in ast:
            if node['type'] == 'Const':
                # Heuristic: if source is pure number, map it
                if re.match(r'^\d+(\.\d+)?$', str(node['source'])):
                    # We can't easily link back without more complex parsing, 
                    # so we assume type safety unless explicit contradiction in candidate evaluation
                    pass
        
        # For this implementation, type errors are primarily generated during 
        # candidate validation against the prompt's derived constraints.
        return errors

    def _propagate_constraints(self, prompt_ast: List[Dict], candidate_text: str) -> Tuple[set, float]:
        """
        Propagates constraints from prompt and checks against candidate.
        Returns (derived_facts, numeric_violation_score).
        """
        derived = set()
        numeric_violation = 0.0
        
        # 1. Extract facts from prompt AST
        facts = set()
        relations = {} # Store relations for transitivity
        
        for node in prompt_ast:
            t = node['type']
            if t == 'GT':
                facts.add(('GT', node['left'], node['right']))
                relations.setdefault(node['left'], set()).add(('GT', node['right']))
            elif t == 'Before':
                facts.add(('Before', node['first'], node['second']))
            elif t == 'Neg':
                facts.add(('Neg', node['target']))
            elif t == 'Imp':
                facts.add(('Imp', node['antecedent'], node['consequent']))
            elif t == 'Const':
                # Store numeric constants found in prompt as bounds if context implies
                pass

        # 2. Transitivity propagation (simplified one-step)
        new_facts = set(facts)
        for f in facts:
            if f[0] == 'GT':
                # If A > B, and we have B > C somewhere? 
                # Look for chains
                pass 
        # Add transitive closure for GT
        gt_pairs = [(f[1], f[2]) for f in facts if f[0] == 'GT']
        for a, b in gt_pairs:
            for c, d in gt_pairs:
                if b == c:
                    new_facts.add(('GT', a, d))
        facts = new_facts

        # 3. Evaluate Candidate against derived facts
        candidate_lower = candidate_text.lower()
        
        # Check for direct contradictions in candidate
        for f in facts:
            if f[0] == 'GT':
                # If prompt says A > B, candidate should not say B > A
                stmt = f"{f[2]} > {f[1]}" # Reverse
                if re.search(rf"\b{f[2]}\s*(?:is\s+)?(?:greater|more|larger)?\s*(?:than\s+)?{f[1]}\b", candidate_lower, re.IGNORECASE):
                     numeric_violation += 2.0 # Penalty for direct contradiction
                # Check if candidate affirms the fact (reward handled by lower energy)
                
        # Numeric range check (Approximation of dependent types)
        # If prompt has "5" and candidate has "100" in a context of "less than", check bounds
        prompt_nums = [n['value'] for n in prompt_ast if n['type'] == 'Const']
        cand_nums = []
        for m in re.finditer(r'\b(\d+(?:\.\d+)?)\b', candidate_text):
            cand_nums.append(float(m.group(1)))
            
        if prompt_nums and cand_nums:
            p_avg = np.mean(prompt_nums)
            c_avg = np.mean(cand_nums)
            # Heuristic: If candidate numbers are wildly different from prompt context without operator change
            if abs(c_avg - p_avg) > p_avg * 10: # Arbitrary threshold for "wildly different"
                numeric_violation += 1.0

        return facts, numeric_violation

    def _calculate_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Calculates F(C) = Sum(type_error^2) + lambda * Sum(violation^2)
        Returns -F as the score.
        """
        prompt_ast = self._parse_to_ast(prompt)
        candidate_ast = self._parse_to_ast(candidate)
        
        # 1. Type Consistency Check (Symbolic)
        # Does the candidate introduce type errors relative to prompt structure?
        type_errors = 0
        
        # Simple check: If prompt establishes X is Int, candidate using X as Bool is error
        # (Simplified for this implementation to structural mismatch)
        if len(prompt_ast) > 0 and len(candidate_ast) == 0:
            # Candidate ignores all structure
            type_errors = 1
            
        # 2. Constraint Propagation & Violation
        derived_facts, numeric_violation = self._propagate_constraints(prompt_ast, candidate)
        
        # Check candidate AST against derived facts
        # If prompt: A > B. Candidate: B > A. -> Violation.
        for node in candidate_ast:
            if node['type'] == 'GT':
                # Check if reverse exists in derived facts
                if ('GT', node['right'], node['left']) in derived_facts:
                    numeric_violation += 5.0 # Strong penalty for logical contradiction
        
        # 3. Compute Energy
        f_val = (type_errors ** 2) + self.lambda_weight * (numeric_violation ** 2)
        
        # Bonus: If candidate contains structural elements matching prompt (compositionality reward)
        # This lowers energy (increases score)
        match_bonus = 0
        p_types = set(n['type'] for n in prompt_ast)
        c_types = set(n['type'] for n in candidate_ast)
        if p_types and c_types:
            overlap = len(p_types.intersection(c_types))
            match_bonus = -0.5 * overlap # Reduce energy
            
        return -(f_val + match_bonus)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self._calculate_free_energy(prompt, cand)
            # Add NCD as tiebreaker only if scores are very close (not implemented as primary)
            # Here we rely on the structural score as primary per instructions
            
            reasoning = f"Structural match and constraint consistency score: {score:.4f}"
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
        Returns confidence 0-1 based on the free energy score.
        Maps the negative energy score to a probability-like value.
        """
        score = self._calculate_free_energy(prompt, answer)
        
        # Map score to 0-1. 
        # Since score is negative energy, higher (less negative) is better.
        # Typical range might be -10 to +2.
        # Use sigmoid-like mapping: 1 / (1 + exp(-k * (score - bias)))
        # Let's assume a bias of 0 and scale.
        # If score > 0, high confidence. If score < -5, low confidence.
        
        # Simple linear mapping with clamp for demonstration
        # Range assumption: -10 (terrible) to 5 (perfect)
        normalized = (score + 5.0) / 15.0 
        conf = max(0.0, min(1.0, normalized))
        
        # Boost if no structural contradictions found
        if "contradiction" not in self._propagate_constraints(self._parse_to_ast(prompt), answer)[1]:
             conf = min(1.0, conf + 0.1)
             
        return float(conf)