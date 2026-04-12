import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import (
    bayesian_update,
    entropy,
    confidence_from_agreement,
    topological_sort,
    solve_sat,
    modus_ponens
)
from forge.amino_acids.pysat_acids import check_entailment
from forge.amino_acids.constraint_acids import is_uniquely_solvable


class ReasoningTool:
    """network_engineering x SAT/constraint solving - argument_strength"""

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
        """Extract premises, conclusion, and entities from the argument."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        premises = []
        conclusion = None
        entities = set()
        question = ""
        
        # Look for premise indicators
        premise_indicators = ["if", "since", "because", "given that", "assuming"]
        conclusion_indicators = ["therefore", "thus", "hence", "so", "consequently"]
        
        for line in lines:
            line_lower = line.lower()
            # Extract capitalized entities (propositions, variables)
            found_entities = re.findall(r'\b([A-Z][a-zA-Z0-9]*)\b', line)
            entities.update(found_entities)
            
            # Check if this is a premise or conclusion
            if any(indicator in line_lower for indicator in premise_indicators):
                premises.append(line)
            elif any(indicator in line_lower for indicator in conclusion_indicators):
                conclusion = line
            elif "?" in line:
                question = line
        
        # If no conclusion found via indicators, last line might be conclusion
        if not conclusion and lines:
            conclusion = lines[-1]
        
        # Extract logical operators and relationships
        logical_ops = []
        for line in premises + ([conclusion] if conclusion else []):
            if line:
                if "and" in line.lower():
                    logical_ops.append("AND")
                if "or" in line.lower():
                    logical_ops.append("OR")
                if "not" in line.lower() or "no " in line.lower():
                    logical_ops.append("NOT")
                if "implies" in line.lower() or "if then" in line.lower():
                    logical_ops.append("IMPLIES")
        
        return {
            "premises": premises,
            "conclusion": conclusion,
            "entities": list(entities),
            "logical_ops": list(set(logical_ops)),
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate argument strength using network engineering concepts."""
        premises = structure["premises"]
        conclusion = structure["conclusion"]
        entities = structure["entities"]
        logical_ops = structure["logical_ops"]
        
        if not premises or not conclusion:
            # Fallback: use topological sort on extracted entities
            edges = self._extract_dependencies(structure["raw"])
            sorted_entities = topological_sort(edges)
            computed_answer = sorted_entities[0] if sorted_entities else "Unknown"
            return {
                "answer": computed_answer,
                "confidence": 0.5,
                "reasoning": "Fallback: topological ordering of entities",
                "strength": "weak"
            }
        
        # Convert to SAT clauses for formal validation
        clauses, var_map = self._to_sat_clauses(premises, conclusion, entities)
        
        # CRITICAL PATH 1: SAT-based entailment check (amino acid)
        entailment_result = None
        if clauses and var_map:
            # Separate premise clauses and conclusion clause
            premise_clauses = clauses[:-1] if len(clauses) > 1 else clauses
            conclusion_clause = clauses[-1] if len(clauses) > 1 else []
            
            if premise_clauses and conclusion_clause:
                entailment_result = check_entailment(premise_clauses, conclusion_clause)
        
        # CRITICAL PATH 2: Constraint solving for uniqueness
        uniqueness_result = None
        if var_map:
            # Create a simple CSP to check if premises uniquely determine conclusion
            variables = list(var_map.keys())
            domains = {var: [0, 1] for var in variables}
            
            # Convert premises to constraints
            constraints = self._premises_to_constraints(premises, var_map)
            
            if constraints:
                uniqueness_result = is_uniquely_solvable(domains, constraints)
        
        # CRITICAL PATH 3: Bayesian update for argument strength
        prior_strength = 0.5  # Neutral prior
        likelihood_strong = 0.8 if entailment_result else 0.2
        bayesian_strength = bayesian_update(prior_strength, likelihood_strong)
        
        # CRITICAL PATH 4: Entropy of logical operators
        if logical_ops:
            # Create probability distribution over operator types
            op_counts = {}
            for op in logical_ops:
                op_counts[op] = op_counts.get(op, 0) + 1
            total = sum(op_counts.values())
            probs = [count/total for count in op_counts.values()]
            logical_entropy = entropy(probs) if probs else 0.0
        else:
            logical_entropy = 0.0
        
        # CRITICAL PATH 5: SAT solving for consistency check
        sat_result = None
        if clauses:
            sat_result = solve_sat(clauses, len(var_map))
        
        # CRITICAL PATH 6: Modus ponens forward chaining
        mp_result = None
        if premises and entities:
            # Extract implication rules
            rules = self._extract_implication_rules(premises, var_map)
            facts = set()
            mp_result = modus_ponens(rules, facts)
        
        # Determine argument strength based on multiple factors
        strength_score = 0.0
        
        # Network engineering concept: argument as communication path
        # Reliability = entailment * uniqueness * bayesian_strength
        reliability = 0.0
        if entailment_result is not None:
            reliability += 0.4 if entailment_result else 0.0
        if uniqueness_result is not None:
            reliability += 0.3 if uniqueness_result else 0.1
        reliability += bayesian_strength * 0.3
        
        # Bandwidth = inverse of entropy (lower entropy = clearer signal)
        bandwidth = 1.0 / (1.0 + logical_entropy) if logical_entropy > 0 else 1.0
        
        # Latency = SAT solving complexity (simpler = faster)
        latency_factor = 0.8 if sat_result else 0.2
        
        # Overall network quality metric
        network_quality = reliability * bandwidth * latency_factor
        
        # Determine final strength
        if network_quality > 0.7:
            strength = "strong"
            strength_score = 0.9
        elif network_quality > 0.4:
            strength = "moderate"
            strength_score = 0.6
        else:
            strength = "weak"
            strength_score = 0.3
        
        # Confidence from agreement of multiple reasoning paths
        scores_to_agree = []
        if entailment_result is not None:
            scores_to_agree.append(1.0 if entailment_result else 0.0)
        if uniqueness_result is not None:
            scores_to_agree.append(1.0 if uniqueness_result else 0.0)
        if sat_result is not None:
            scores_to_agree.append(0.8 if sat_result else 0.2)
        
        confidence = confidence_from_agreement(scores_to_agree) if scores_to_agree else 0.5
        
        # The answer is the strength assessment
        computed_answer = strength
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": f"Network reliability={reliability:.2f}, bandwidth={bandwidth:.2f}, latency={latency_factor:.2f}",
            "strength": strength,
            "strength_score": strength_score,
            "network_quality": network_quality
        }

    def _extract_dependencies(self, text: str) -> List[Tuple[str, str]]:
        """Extract dependency edges between entities."""
        edges = []
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        for sentence in sentences:
            # Look for "if A then B" patterns
            if "if " in sentence.lower() and " then " in sentence.lower():
                parts = sentence.lower().split(" then ")
                if len(parts) == 2:
                    antecedent = parts[0].replace("if ", "").strip()
                    consequent = parts[1].strip()
                    # Extract capitalized entities
                    ant_entities = re.findall(r'\b([A-Z][a-zA-Z0-9]*)\b', antecedent)
                    cons_entities = re.findall(r'\b([A-Z][a-zA-Z0-9]*)\b', consequent)
                    if ant_entities and cons_entities:
                        edges.append((ant_entities[0], cons_entities[0]))
            
            # Look for "A implies B" patterns
            elif " implies " in sentence.lower():
                parts = sentence.lower().split(" implies ")
                if len(parts) == 2:
                    left = parts[0].strip()
                    right = parts[1].strip()
                    left_entities = re.findall(r'\b([A-Z][a-zA-Z0-9]*)\b', left)
                    right_entities = re.findall(r'\b([A-Z][a-zA-Z0-9]*)\b', right)
                    if left_entities and right_entities:
                        edges.append((left_entities[0], right_entities[0]))
        
        return edges

    def _to_sat_clauses(self, premises: List[str], conclusion: str, entities: List[str]) -> Tuple[List[List[int]], Dict[str, int]]:
        """Convert natural language argument to SAT clauses."""
        var_map = {}
        clauses = []
        
        # Assign variables to entities
        for i, entity in enumerate(entities):
            var_map[entity] = i + 1  # SAT variables start at 1
        
        # Convert premises to clauses
        for premise in premises:
            premise_clauses = self._sentence_to_clauses(premise, var_map)
            clauses.extend(premise_clauses)
        
        # Convert conclusion to clause (negated for entailment check)
        if conclusion:
            conclusion_clauses = self._sentence_to_clauses(conclusion, var_map, negate=True)
            clauses.extend(conclusion_clauses)
        
        return clauses, var_map

    def _sentence_to_clauses(self, sentence: str, var_map: Dict[str, int], negate: bool = False) -> List[List[int]]:
        """Convert a sentence to CNF clauses."""
        clauses = []
        sentence_lower = sentence.lower()
        
        # Simple patterns
        for entity, var_idx in var_map.items():
            if entity.lower() in sentence_lower:
                # Check for negation
                is_negated = False
                if "not " + entity.lower() in sentence_lower or "no " + entity.lower() in sentence_lower:
                    is_negated = True
                
                var = var_idx if not is_negated else -var_idx
                if negate:
                    var = -var
                
                clauses.append([var])
        
        # Handle conjunctions (AND)
        if " and " in sentence_lower:
            parts = sentence_lower.split(" and ")
            clause = []
            for part in parts:
                for entity, var_idx in var_map.items():
                    if entity.lower() in part:
                        is_negated = "not " + entity.lower() in part or "no " + entity.lower() in part
                        var = var_idx if not is_negated else -var_idx
                        if negate:
                            var = -var
                        clause.append(var)
            if clause:
                clauses.append(clause)
        
        # Handle implications (if A then B)
        if "if " in sentence_lower and " then " in sentence_lower:
            parts = sentence_lower.split(" then ")
            if len(parts) == 2:
                antecedent = parts[0].replace("if ", "").strip()
                consequent = parts[1].strip()
                
                ant_var = None
                cons_var = None
                
                for entity, var_idx in var_map.items():
                    if entity.lower() in antecedent:
                        is_negated = "not " + entity.lower() in antecedent or "no " + entity.lower() in antecedent
                        ant_var = -var_idx if is_negated else var_idx
                    if entity.lower() in consequent:
                        is_negated = "not " + entity.lower() in consequent or "no " + entity.lower() in consequent
                        cons_var = -var_idx if is_negated else var_idx
                
                if ant_var and cons_var:
                    # A → B is equivalent to ¬A ∨ B
                    clause = [-ant_var, cons_var]
                    if negate:
                        clause = [ant_var, -cons_var]
                    clauses.append(clause)
        
        return clauses

    def _premises_to_constraints(self, premises: List[str], var_map: Dict[str, int]) -> List[Tuple[List[str], Any]]:
        """Convert premises to constraint satisfaction problem constraints."""
        constraints = []
        
        for premise in premises:
            premise_lower = premise.lower()
            
            # Simple equality constraints
            for entity, var_idx in var_map.items():
                if entity.lower() in premise_lower:
                    # Check if this is an assignment
                    if "is true" in premise_lower or "must be true" in premise_lower:
                        def make_true_func(var_name=entity):
                            def func(assignment):
                                return assignment.get(var_name, 0) == 1
                            return func
                        constraints.append(([entity], make_true_func()))
                    
                    # Check for negation
                    elif "is false" in premise_lower or "must be false" in premise_lower:
                        def make_false_func(var_name=entity):
                            def func(assignment):
                                return assignment.get(var_name, 0) == 0
                            return func
                        constraints.append(([entity], make_false_func()))
            
            # Conjunction constraints
            if " and " in premise_lower:
                parts = premise_lower.split(" and ")
                entities_in_conjunction = []
                for part in parts:
                    for entity in var_map.keys():
                        if entity.lower() in part:
                            entities_in_conjunction.append(entity)
                
                if len(entities_in_conjunction) >= 2:
                    def conjunction_func(vars_list=entities_in_conjunction):
                        def func(assignment):
                            return all(assignment.get(var, 0) == 1 for var in vars_list)
                        return func
                    constraints.append((entities_in_conjunction, conjunction_func()))
        
        return constraints

    def _extract_implication_rules(self, premises: List[str], var_map: Dict[str, int]) -> List[Tuple[str, str]]:
        """Extract implication rules for modus ponens."""
        rules = []
        
        for premise in premises:
            premise_lower = premise.lower()
            
            if "if " in premise_lower and " then " in premise_lower:
                parts = premise_lower.split(" then ")
                if len(parts) == 2:
                    antecedent = parts[0].replace("if ", "").strip()
                    consequent = parts[1].strip()
                    
                    ant_entity = None
                    cons_entity = None
                    
                    for entity in var_map.keys():
                        if entity.lower() in antecedent and "not " not in antecedent and "no " not in antecedent:
                            ant_entity = entity
                        if entity.lower() in consequent and "not " not in consequent and "no " not in consequent:
                            cons_entity = entity
                    
                    if ant_entity and cons_entity:
                        rules.append((ant_entity, cons_entity))
        
        return rules

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        strength = reasoning_result.get("strength", "")
        strength_score = reasoning_result.get("strength_score", 0.5)
        
        results = []
        for candidate in candidates:
            # Primary scoring: match computed answer
            candidate_lower = candidate.lower()
            computed_lower = computed_answer.lower()
            
            if computed_lower in candidate_lower:
                # Direct match
                base_score = 1.0
            elif strength and strength.lower() in candidate_lower:
                # Match strength description
                base_score = 0.8
            else:
                # Fallback: NCD similarity to reasoning
                base_score = 1.0 / (1.0 + self._ncd(reasoning_text, candidate))
            
            # Adjust by strength score
            adjusted_score = base_score * (0.5 + 0.5 * strength_score)
            
            results.append({
                "candidate": candidate,
                "score": adjusted_score,
                "base_score": base_score,
                "strength_adjustment": strength_score
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
        
        # Extract scores
        scores = [item["score"] for item in scored]
        
        # Normalize to 0-1 range if needed
        min_score = min(scores)
        max_score = max(scores)
        
        if max_score > min_score:
            for item in scored:
                item["score"] = (item["score"] - min_score) / (max_score - min_score)
        
        return scored