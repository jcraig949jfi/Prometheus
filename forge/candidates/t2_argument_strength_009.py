import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import (
    bayesian_update,
    entropy,
    confidence_from_agreement,
    solve_sat,
    modus_ponens,
    check_transitivity
)
from forge.amino_acids.pysat_acids import check_entailment


class ReasoningTool:
    """Cryptography x SAT entailment - argument_strength"""

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        # Phase 1: EXTRACT
        structure = self._extract(prompt)
        # Phase 2: REASON
        reasoning_result = self._reason(structure)
        # Phase 3: SCORE
        scored = self._score(candidates, reasoning_result)
        # Phase 4: CALIBRATE
        calibrated = self._calibrate(scored)
        return sorted(calibrated, key=lambda x: x["score"], reverse=True)

    def _extract(self, prompt: str) -> Dict[str, Any]:
        """Extract premises, conclusion, and logical structure from prompt."""
        lines = [line.strip() for line in prompt.split('\n') if line.strip()]
        
        premises = []
        conclusion = None
        entities = {}
        
        # Find premises (usually statements before "Therefore", "Thus", "Hence")
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(marker in line_lower for marker in ["therefore", "thus", "hence", "so", "conclusion"]):
                # Everything before this line is premises
                premises = [l.strip(' .') for l in lines[:i] if l.strip(' .')]
                # This line or next contains conclusion
                conclusion_line = line
                # Remove conclusion markers
                for marker in ["therefore", "thus", "hence", "so", "conclusion:"]:
                    conclusion_line = re.sub(marker, '', conclusion_line, flags=re.IGNORECASE)
                conclusion = conclusion_line.strip(' .')
                break
        
        # If no conclusion marker found, last line is conclusion
        if not conclusion and lines:
            conclusion = lines[-1].strip(' .')
            premises = [l.strip(' .') for l in lines[:-1] if l.strip(' .')]
        
        # Extract propositional variables (capital letters or quoted phrases)
        all_text = ' '.join(premises + [conclusion] if conclusion else premises)
        variables = set(re.findall(r'\b[A-Z]\b', all_text))
        
        # Also look for quoted entities
        quoted = set(re.findall(r'"([^"]+)"', all_text))
        
        # Build entity mapping
        for var in variables:
            entities[var] = {"type": "variable", "mentions": []}
        
        for q in quoted:
            entities[q] = {"type": "quoted_entity", "mentions": []}
        
        # Find which entities appear in which premises
        for i, prem in enumerate(premises):
            for var in variables:
                if var in prem:
                    entities[var]["mentions"].append(i)
            for q in quoted:
                if q in prem:
                    entities[q]["mentions"].append(i)
        
        return {
            "premises": premises,
            "conclusion": conclusion,
            "entities": entities,
            "variables": list(variables),
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use cryptographic proof verification framework to evaluate argument validity."""
        premises = structure["premises"]
        conclusion = structure["conclusion"]
        variables = structure["variables"]
        
        if not premises or not conclusion:
            return {"answer": "Invalid", "confidence": 0.0, "reasoning": "Missing premises or conclusion"}
        
        # Step 1: Convert to propositional logic using cryptographic commitment analogy
        # Each premise is a "commitment", conclusion is the "opening"
        # We'll use SAT to check if premises ∧ ¬conclusion is unsatisfiable
        
        # Map variables to integers for SAT encoding
        var_map = {var: i+1 for i, var in enumerate(variables)}
        
        # Convert natural language to simple logical forms
        # This is a simplified parser - assumes "if P then Q", "P and Q", "P or Q", "not P"
        premise_clauses = []
        
        for prem in premises:
            clauses = self._parse_to_clauses(prem, var_map)
            if clauses:
                premise_clauses.extend(clauses)
        
        # Parse conclusion
        conclusion_clause = self._parse_conclusion(conclusion, var_map)
        
        # CRITICAL PRIMITIVE 1: Use check_entailment amino acid
        # This directly determines if argument is valid
        entailment_result = check_entailment(premise_clauses, conclusion_clause)
        
        # CRITICAL PRIMITIVE 2: Use solve_sat to check consistency of premises
        # This determines if premises are self-consistent (affects confidence)
        premises_sat = solve_sat(premise_clauses, len(var_map))
        
        # CRITICAL PRIMITIVE 3: Use entropy to measure information content
        # Cryptographic analogy: high entropy = more "uncertainty" in argument
        if premises_sat:
            # Count models to estimate probability distribution
            # Simplified: assume uniform over possible worlds
            n_vars = len(var_map)
            possible_worlds = 2 ** n_vars
            # Estimate probability of conclusion being true given premises
            # For valid arguments, P(conclusion|premises) = 1
            if entailment_result:
                prob_conclusion = 1.0
            else:
                # If not entailed, need to estimate
                # Create clauses for premises AND conclusion
                test_clauses = premise_clauses + [conclusion_clause]
                test_sat = solve_sat(test_clauses, n_vars)
                prob_conclusion = 0.5  # Default if we can't compute
                if test_sat:
                    # Conclusion is consistent with premises but not entailed
                    prob_conclusion = 0.7  # Arbitrary but > 0.5
                else:
                    prob_conclusion = 0.3  # Less likely
            dist = [prob_conclusion, 1.0 - prob_conclusion]
            info_entropy = entropy(dist)
        else:
            info_entropy = 1.0  # Max entropy for inconsistent premises
        
        # CRITICAL PRIMITIVE 4: Use modus_ponens to check for simple derivations
        # Cryptographic analogy: checking for direct "key" derivations
        derived = set()
        if variables:
            # Convert premises to implication form for modus_ponens
            mp_premises = []
            for prem in premises:
                # Look for "if P then Q" patterns
                if "if" in prem.lower() and "then" in prem.lower():
                    parts = prem.lower().split("then")
                    if len(parts) == 2:
                        antecedent = parts[0].replace("if", "").strip()
                        consequent = parts[1].strip()
                        # Map to variables if possible
                        ant_vars = [v for v in variables if v.lower() in antecedent]
                        cons_vars = [v for v in variables if v.lower() in consequent]
                        if ant_vars and cons_vars:
                            mp_premises.append((ant_vars[0], cons_vars[0]))
            
            # Start with known facts (atomic propositions in premises)
            facts = set()
            for prem in premises:
                # Look for standalone variables
                for var in variables:
                    if var in prem and "if" not in prem.lower() and "not" not in prem.lower():
                        # Simple heuristic: if variable appears alone or with "and"
                        words = prem.split()
                        if var in words and len(words) < 4:
                            facts.add(var)
            
            if mp_premises and facts:
                derived_facts = modus_ponens(mp_premises, facts)
                derived = derived_facts - facts
        
        # CRITICAL PRIMITIVE 5: Use check_transitivity for relational reasoning
        # Cryptographic analogy: checking transitive trust relationships
        relations = []
        for prem in premises:
            # Look for comparative relations
            if "implies" in prem.lower():
                parts = prem.lower().split("implies")
                if len(parts) == 2:
                    left = parts[0].strip()
                    right = parts[1].strip()
                    left_vars = [v for v in variables if v.lower() in left]
                    right_vars = [v for v in variables if v.lower() in right]
                    if left_vars and right_vars:
                        relations.append((left_vars[0], right_vars[0]))
        
        transitive_closure = {}
        if relations:
            transitive_closure = check_transitivity(relations)
        
        # Determine if conclusion is in transitive closure of premises
        transitive_support = False
        if conclusion and variables:
            # Check if any variable in conclusion is reachable from known facts
            conc_vars = [v for v in variables if v in conclusion]
            for start in facts:
                if start in transitive_closure:
                    for conc_var in conc_vars:
                        if conc_var in transitive_closure[start]:
                            transitive_support = True
                            break
        
        # CRITICAL PRIMITIVE 6: Use confidence_from_agreement
        # Cryptographic analogy: multiple witnesses agreeing on validity
        validity_scores = []
        
        # Score 1: SAT entailment result
        validity_scores.append(1.0 if entailment_result else 0.0)
        
        # Score 2: Modus ponens support
        if conclusion and variables:
            conc_vars = [v for v in variables if v in conclusion]
            mp_support = any(v in derived for v in conc_vars)
            validity_scores.append(1.0 if mp_support else 0.0)
        
        # Score 3: Transitive support
        validity_scores.append(1.0 if transitive_support else 0.0)
        
        # Score 4: Premises consistency
        validity_scores.append(1.0 if premises_sat else 0.0)
        
        confidence = confidence_from_agreement(validity_scores)
        
        # Cryptographic strength metric: combine validity with information-theoretic measures
        # Strong arguments have high validity and low entropy (deterministic conclusion)
        if entailment_result:
            strength = confidence * (1.0 - info_entropy)  # High confidence, low entropy
        else:
            strength = confidence * info_entropy  # High entropy weakens invalid arguments
        
        # Determine final answer
        if entailment_result:
            computed_answer = "Valid"
            reasoning_text = f"Premises entail conclusion (cryptographic proof verified). Strength: {strength:.2f}"
        else:
            computed_answer = "Invalid"
            reasoning_text = f"Premises do not entail conclusion. Strength: {strength:.2f}"
        
        # If premises are inconsistent, argument is technically valid but unsound
        if not premises_sat:
            computed_answer = "Valid (but premises inconsistent)"
            reasoning_text = "Premises are inconsistent, so argument is vacuously valid but unsound."
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "strength": strength,
            "entropy": info_entropy,
            "reasoning": reasoning_text,
            "entailment": entailment_result,
            "premises_consistent": bool(premises_sat)
        }

    def _parse_to_clauses(self, sentence: str, var_map: Dict[str, int]) -> List[List[int]]:
        """Convert natural language sentence to CNF clauses (simplified)."""
        sentence_lower = sentence.lower()
        clauses = []
        
        # Handle negation
        if "not" in sentence_lower:
            # Find the variable after "not"
            words = sentence.split()
            for i, word in enumerate(words):
                if word.lower() == "not" and i+1 < len(words):
                    next_word = words[i+1]
                    if next_word in var_map:
                        clauses.append([-var_map[next_word]])
                        return clauses
        
        # Handle conjunction "and"
        if " and " in sentence_lower:
            parts = sentence.split(" and ")
            for part in parts:
                part = part.strip()
                for var in var_map:
                    if var in part:
                        clauses.append([var_map[var]])
                        break
            return clauses
        
        # Handle disjunction "or"
        if " or " in sentence_lower:
            parts = sentence.split(" or ")
            clause = []
            for part in parts:
                part = part.strip()
                for var in var_map:
                    if var in part:
                        clause.append(var_map[var])
                        break
            if clause:
                clauses.append(clause)
            return clauses
        
        # Handle implication "if...then" or "implies"
        if "if" in sentence_lower and "then" in sentence_lower:
            # Convert P → Q to ¬P ∨ Q
            parts = sentence_lower.split("then")
            if len(parts) == 2:
                antecedent = parts[0].replace("if", "").strip()
                consequent = parts[1].strip()
                
                ant_var = None
                cons_var = None
                
                for var in var_map:
                    if var.lower() in antecedent:
                        ant_var = var
                    if var.lower() in consequent:
                        cons_var = var
                
                if ant_var and cons_var:
                    clauses.append([-var_map[ant_var], var_map[cons_var]])
                    return clauses
        
        # Handle simple atomic proposition
        for var in var_map:
            if var in sentence:
                clauses.append([var_map[var]])
                return clauses
        
        return clauses

    def _parse_conclusion(self, conclusion: str, var_map: Dict[str, int]) -> List[int]:
        """Parse conclusion to a single clause."""
        conclusion_lower = conclusion.lower()
        
        # Handle negation
        if "not" in conclusion_lower:
            words = conclusion.split()
            for i, word in enumerate(words):
                if word.lower() == "not" and i+1 < len(words):
                    next_word = words[i+1]
                    if next_word in var_map:
                        return [-var_map[next_word]]
        
        # Handle simple atomic conclusion
        for var in var_map:
            if var in conclusion:
                return [var_map[var]]
        
        # Default: positive literal of first variable mentioned
        for var in var_map:
            if var.lower() in conclusion_lower:
                return [var_map[var]]
        
        # Fallback
        if var_map:
            return [list(var_map.values())[0]]
        return [1]

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact match or containment of computed answer
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity to reasoning text
                base_score = 1.0 / (1.0 + self._ncd(reasoning_text, candidate))
            
            # Adjust based on confidence
            confidence = reasoning_result.get("confidence", 0.5)
            strength = reasoning_result.get("strength", 0.5)
            
            # Final score combines base match with argument strength
            final_score = base_score * strength
            
            results.append({
                "candidate": candidate,
                "score": final_score,
                "base_score": base_score,
                "strength": strength,
                "confidence": confidence
            })
        
        return results

    def _ncd(self, a: str, b: str) -> float:
        """Normalized Compression Distance between two strings."""
        if not a or not b:
            return 1.0
        
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + " " + b).encode()))
        
        if max(ca, cb) == 0:
            return 1.0
        
        return (cab - min(ca, cb)) / max(ca, cb)

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper distribution."""
        if not scored:
            return scored
        
        # Simple min-max normalization
        scores = [item["score"] for item in scored]
        if not scores:
            return scored
        
        min_score = min(scores)
        max_score = max(scores)
        
        if max_score - min_score > 0.001:
            for item in scored:
                item["score"] = (item["score"] - min_score) / (max_score - min_score)
        else:
            # All scores are similar, keep as is
            pass
        
        return scored