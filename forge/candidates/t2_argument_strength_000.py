import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import (
    check_transitivity,
    entropy,
    confidence_from_agreement,
    solve_sat,
    modus_ponens,
    pigeonhole_check
)
from forge.amino_acids.pysat_acids import check_entailment, detect_paradox
from forge.amino_acids.constraint_acids import is_uniquely_solvable


class ReasoningTool:
    """Topology x SAT entailment - argument_strength"""

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
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        
        premises = []
        conclusion = None
        entities = set()
        
        # Look for premise indicators
        premise_indicators = ["since", "because", "given that", "as", "for"]
        conclusion_indicators = ["therefore", "thus", "hence", "so", "consequently"]
        
        for line in lines:
            line_lower = line.lower()
            
            # Check if this is a conclusion
            is_conclusion = any(ind in line_lower for ind in conclusion_indicators)
            
            # Extract capitalized entities (propositions, variables)
            # This finds things like "P", "Q", "All S are P", etc.
            words = re.findall(r'\b[A-Z][a-z]*\b|\b[A-Z]\b', line)
            entities.update(words)
            
            # Simple classification: last line often contains conclusion
            if is_conclusion or line == lines[-1]:
                if conclusion is None:
                    conclusion = line
            else:
                # Check if it's a premise (contains logical content)
                if any(word in line for word in ['if', 'then', 'and', 'or', 'not', 'all', 'some', 'no']):
                    premises.append(line)
        
        # If no conclusion found, use last line
        if conclusion is None and lines:
            conclusion = lines[-1]
        
        # Extract logical operators and structure
        logical_structure = {
            "has_conditional": any("if" in p.lower() and "then" in p.lower() for p in premises),
            "has_negation": any("not" in p.lower() or "no " in p.lower() for p in premises),
            "has_conjunction": any("and" in p.lower() for p in premises),
            "has_disjunction": any("or" in p.lower() for p in premises),
        }
        
        return {
            "premises": premises,
            "conclusion": conclusion,
            "entities": list(entities),
            "logical_structure": logical_structure,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use topological reasoning about logical space to evaluate argument strength."""
        premises = structure["premises"]
        conclusion = structure["conclusion"]
        entities = structure["entities"]
        logical_structure = structure["logical_structure"]
        
        # PHASE 1: Topological analysis of logical space
        # Represent propositions as points, implications as directed edges
        edges = []
        proposition_points = set()
        
        # Extract implication relations from premises
        for premise in premises:
            if "if" in premise.lower() and "then" in premise.lower():
                # Simple pattern: "If P then Q"
                match = re.search(r'if\s+([^,]+?)\s+then\s+([^.,]+)', premise.lower())
                if match:
                    p = match.group(1).strip().title()
                    q = match.group(2).strip().title()
                    edges.append((p, q))
                    proposition_points.add(p)
                    proposition_points.add(q)
        
        # Use check_transitivity to analyze the implication graph
        # This represents the topological closure of the logical space
        if edges:
            transitive_closure = check_transitivity(edges)
            
            # Compute connectivity in the logical space
            connectivity_scores = []
            for prop in proposition_points:
                reachable = transitive_closure.get(prop, set())
                # In topology, stronger arguments have denser connectivity
                connectivity = len(reachable) / max(1, len(proposition_points) - 1)
                connectivity_scores.append(connectivity)
            
            # Entropy of connectivity measures how evenly distributed logical connections are
            # Low entropy = some propositions are hubs (strong central arguments)
            # High entropy = evenly distributed (weaker, more diffuse argument)
            if connectivity_scores:
                conn_entropy = entropy([c for c in connectivity_scores if c > 0])
            else:
                conn_entropy = 1.0  # Max entropy for disconnected space
        else:
            conn_entropy = 1.0
            transitive_closure = {}
        
        # PHASE 2: SAT-based entailment checking (amino acid)
        # Convert natural language to simple propositional logic
        clauses = []
        var_map = {}
        next_var = 1
        
        # Map entities to SAT variables
        for entity in entities:
            if len(entity) == 1 or entity in ["True", "False"]:
                var_map[entity] = next_var
                next_var += 1
        
        # Create simple clauses from premises
        # For "If P then Q": (¬P ∨ Q)
        for premise in premises:
            if "if" in premise.lower() and "then" in premise.lower():
                match = re.search(r'if\s+([^,]+?)\s+then\s+([^.,]+)', premise.lower())
                if match:
                    p = match.group(1).strip().title()
                    q = match.group(2).strip().title()
                    if p in var_map and q in var_map:
                        clauses.append([-var_map[p], var_map[q]])
        
        # Add any direct assertions
        for premise in premises:
            if "if" not in premise.lower() or "then" not in premise.lower():
                # Simple assertion like "P is true"
                for entity in entities:
                    if entity in premise and entity in var_map:
                        if "not" in premise.lower() or "no " in premise.lower():
                            clauses.append([-var_map[entity]])
                        else:
                            clauses.append([var_map[entity]])
        
        # Check entailment using amino acid
        # This is LOAD-BEARING: determines if conclusion follows
        entailment_result = None
        conclusion_clause = []
        
        # Extract conclusion proposition
        if conclusion:
            # Check for negated conclusion
            is_negated = "not" in conclusion.lower() or "no " in conclusion.lower()
            
            # Find entity in conclusion
            for entity in entities:
                if entity in conclusion:
                    if entity in var_map:
                        if is_negated:
                            conclusion_clause = [-var_map[entity]]
                        else:
                            conclusion_clause = [var_map[entity]]
                    break
        
        if clauses and conclusion_clause:
            entailment_result = check_entailment(clauses, conclusion_clause)
        
        # PHASE 3: Paradox detection (amino acid fallback)
        paradox_detected = False
        if clauses:
            paradox_info = detect_paradox(clauses)
            if paradox_info and paradox_info.get("is_paradox", False):
                paradox_detected = True
        
        # PHASE 4: Constraint satisfaction analysis
        # Represent as CSP to check solution uniqueness
        csp_unique = False
        if var_map:
            # Create simple CSP: variables can be True/False
            variables = list(var_map.keys())
            domains = {var: [0, 1] for var in variables}  # 0=False, 1=True
            
            # Convert clauses to constraints
            constraints = []
            for clause in clauses:
                def make_constraint(clause_vars, clause_lits):
                    def constraint(assignment):
                        # At least one literal must be true
                        for var, lit in zip(clause_vars, clause_lits):
                            val = assignment[var]
                            if lit > 0 and val == 1:
                                return True
                            if lit < 0 and val == 0:
                                return True
                        return False
                    return constraint
                
                # Extract variables from clause
                clause_vars = []
                clause_lits = []
                for lit in clause:
                    var_name = None
                    for var, num in var_map.items():
                        if abs(lit) == num:
                            var_name = var
                            break
                    if var_name:
                        clause_vars.append(var_name)
                        clause_lits.append(lit)
                
                if clause_vars:
                    constraints.append((clause_vars, make_constraint(clause_vars, clause_lits)))
            
            if constraints:
                csp_unique = is_uniquely_solvable(variables, domains, constraints)
        
        # PHASE 5: Compute argument strength using topological measures
        # Strong arguments have: low entropy (focused), entailment true, no paradox, unique solution
        
        # Base strength from topological structure
        # Low entropy = stronger argument (more focused logical space)
        topological_strength = 1.0 - min(conn_entropy, 1.0)
        
        # Entailment contributes significantly
        entailment_strength = 1.0 if entailment_result else 0.0
        
        # Paradox weakens argument
        paradox_penalty = 0.5 if paradox_detected else 1.0
        
        # Unique solution strengthens argument
        uniqueness_boost = 1.2 if csp_unique else 1.0
        
        # Compute final strength
        strength = topological_strength * entailment_strength * paradox_penalty * uniqueness_boost
        
        # Use confidence_from_agreement on multiple strength indicators
        strength_indicators = [
            topological_strength,
            entailment_strength,
            1.0 if not paradox_detected else 0.0,
            1.0 if csp_unique else 0.5
        ]
        confidence = confidence_from_agreement(strength_indicators)
        
        # Determine validity label
        if entailment_result and not paradox_detected:
            validity = "valid"
        elif paradox_detected:
            validity = "paradoxical"
        else:
            validity = "invalid"
        
        # Use modus_ponens to see what can be derived (load-bearing)
        derived_facts = set()
        if edges and proposition_points:
            # Convert edges to premise tuples for modus_ponens
            mp_premises = []
            for p, q in edges:
                mp_premises.append((p, q))
            
            # Start with any direct assertions
            initial_facts = set()
            for premise in premises:
                if "if" not in premise.lower():
                    for prop in proposition_points:
                        if prop in premise:
                            if "not" not in premise.lower() and "no " not in premise.lower():
                                initial_facts.add(prop)
            
            if mp_premises and initial_facts:
                derived_facts = modus_ponens(mp_premises, initial_facts)
        
        # Check pigeonhole principle for categorical arguments
        # If we have more categories than possible truth values, argument may be weak
        pigeonhole_violation = False
        if len(entities) > 0:
            # Simple check: if we have more distinct propositions than binary values allow
            pigeonhole_violation = pigeonhole_check(len(entities), 2)  # 2 truth values
        
        # Final computed answer based on strength and validity
        if strength > 0.7 and validity == "valid":
            computed_answer = "strong valid argument"
        elif strength > 0.4 and validity == "valid":
            computed_answer = "weak valid argument"
        elif paradox_detected:
            computed_answer = "paradoxical argument"
        elif pigeonhole_violation:
            computed_answer = "overconstrained argument"
        else:
            computed_answer = "invalid argument"
        
        return {
            "answer": computed_answer,
            "strength": strength,
            "validity": validity,
            "confidence": confidence,
            "entropy": conn_entropy,
            "entailment": entailment_result,
            "paradox": paradox_detected,
            "unique_solution": csp_unique,
            "derived_facts": list(derived_facts),
            "pigeonhole_violation": pigeonhole_violation,
            "reasoning": f"Topological entropy: {conn_entropy:.3f}, Entailment: {entailment_result}, Paradox: {paradox_detected}, Unique: {csp_unique}"
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: check if computed answer appears in candidate
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity
                base_score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
            
            # Adjust by confidence
            adjusted_score = base_score * confidence
            
            results.append({
                "candidate": candidate,
                "score": adjusted_score,
                "base_score": base_score,
                "confidence": confidence
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper ranking."""
        if not scored:
            return scored
        
        # Simple normalization to [0, 1] range
        scores = [item["score"] for item in scored]
        if scores:
            min_score = min(scores)
            max_score = max(scores)
            if max_score > min_score:
                for item in scored:
                    item["score"] = (item["score"] - min_score) / (max_score - min_score)
            else:
                # All scores equal
                for item in scored:
                    item["score"] = 0.5
        
        return scored

    def _ncd(self, a: str, b: str) -> float:
        """Normalized Compression Distance between two strings."""
        if not a and not b:
            return 0.0
        
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + " " + b).encode()))
        
        if max(ca, cb) == 0:
            return 1.0
        
        return (cab - min(ca, cb)) / max(ca, cb)