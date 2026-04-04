import re
import zlib
from typing import Dict, List, Any, Tuple, Set

from forge_primitives import (
    check_transitivity,
    modus_ponens,
    solve_sat,
    confidence_from_agreement,
    entropy,
    topological_sort
)
from forge.amino_acids.pysat_acids import check_entailment, detect_paradox
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable


class ReasoningTool:
    """Topology x SAT/Constraint Solving - liar_detection"""

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
        """Extract agents, statements, and truth-telling policies from prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        
        agents = set()
        statements = {}
        truth_policies = {}  # "always lies", "always tells truth", "alternates", etc.
        question = lines[-1] if lines else ""
        
        # Extract agents (typically capitalized names or A, B, C)
        agent_pattern = r'\b([A-Z][a-z]+|[A-Z])\b'
        for line in lines:
            found_agents = re.findall(agent_pattern, line)
            agents.update(found_agents)
        
        # Extract statements and policies
        for line in lines:
            line_lower = line.lower()
            
            # Look for truth-telling policies
            if 'always lies' in line_lower or 'liar' in line_lower:
                for agent in re.findall(agent_pattern, line):
                    truth_policies[agent] = 'liar'
            elif 'always tells the truth' in line_lower or 'truth-teller' in line_lower:
                for agent in re.findall(agent_pattern, line):
                    truth_policies[agent] = 'truth'
            elif 'alternates' in line_lower or 'random' in line_lower:
                for agent in re.findall(agent_pattern, line):
                    truth_policies[agent] = 'alternating'
            
            # Extract statements in the form "X says: ..."
            says_match = re.search(r'([A-Z][a-z]?|[A-Z])\s+says[:\s]+["\']?(.+?)["\']?[\.\?]?$', line, re.IGNORECASE)
            if says_match:
                agent = says_match.group(1)
                statement = says_match.group(2).strip()
                if agent in agents:
                    statements[agent] = statement
        
        return {
            "agents": list(agents),
            "statements": statements,
            "truth_policies": truth_policies,
            "question": question,
            "raw_lines": lines
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use topological reasoning and SAT solving to resolve liar puzzles."""
        agents = structure["agents"]
        statements = structure["statements"]
        truth_policies = structure["truth_policies"]
        question = structure["question"]
        
        # CRITICAL: Use topological_sort to analyze dependency structure
        # Build edges based on statements referencing other agents
        edges = []
        for agent, stmt in statements.items():
            # Check if statement mentions other agents
            for other_agent in agents:
                if other_agent != agent and other_agent in stmt:
                    edges.append((agent, other_agent))
        
        # T1 PRIMITIVE 1: topological_sort - determines reasoning order
        topo_order = topological_sort(edges)
        if topo_order is None:
            # Graph has cycles, use original agent order
            topo_order = agents
        
        # Convert statements to logical constraints
        clauses = []
        var_map = {}
        var_counter = 1
        
        # Create variables for agent truth values and statement truth values
        for agent in agents:
            var_map[f"{agent}_truth"] = var_counter  # True if agent tells truth
            var_counter += 1
        
        for agent, stmt in statements.items():
            var_map[f"stmt_{agent}"] = var_counter  # True if statement is factually true
            var_counter += 1
        
        # Add constraints based on truth policies
        for agent, policy in truth_policies.items():
            agent_var = var_map[f"{agent}_truth"]
            if policy == 'liar':
                # Agent always lies: agent_truth = False
                clauses.append([-agent_var])
            elif policy == 'truth':
                # Agent always tells truth: agent_truth = True
                clauses.append([agent_var])
            # Alternating policy handled later with statement constraints
        
        # Add constraints linking agent truth to statement truth
        for agent, stmt in statements.items():
            agent_var = var_map[f"{agent}_truth"]
            stmt_var = var_map[f"stmt_{agent}"]
            
            # If agent tells truth, statement must be true
            clauses.append([-agent_var, stmt_var])  # agent_truth → stmt_true
            # If agent lies, statement must be false
            clauses.append([agent_var, -stmt_var])  # ¬agent_truth → ¬stmt_true
        
        # Parse statements for logical content
        # Simple parsing: statements about other agents' truthfulness
        for agent, stmt in statements.items():
            stmt_var = var_map[f"stmt_{agent}"]
            
            # Check for "X is a liar" or "X tells the truth"
            for other_agent in agents:
                if other_agent != agent:
                    if f"{other_agent} is a liar" in stmt.lower() or f"{other_agent} lies" in stmt.lower():
                        other_var = var_map[f"{other_agent}_truth"]
                        # Statement "X is a liar" means other_agent_truth = False
                        clauses.append([-stmt_var, -other_var])  # stmt_true → ¬other_truth
                        clauses.append([stmt_var, other_var])    # ¬stmt_true → other_truth
                    
                    if f"{other_agent} tells the truth" in stmt.lower() or f"{other_agent} is truthful" in stmt.lower():
                        other_var = var_map[f"{other_agent}_truth"]
                        # Statement "X tells truth" means other_agent_truth = True
                        clauses.append([-stmt_var, other_var])   # stmt_true → other_truth
                        clauses.append([stmt_var, -other_var])   # ¬stmt_true → ¬other_truth
        
        # AMINO ACID 1: detect_paradox - check if statements are self-contradictory
        paradox_info = detect_paradox(clauses)
        
        # T1 PRIMITIVE 2: solve_sat - find satisfying assignment
        sat_assignment = solve_sat(clauses, len(var_map))
        
        # Determine answer based on SAT solution and topological order
        computed_answer = ""
        confidence = 0.5
        
        if sat_assignment is not None:
            # Extract truth values for agents
            agent_truth_values = {}
            for agent in agents:
                var = var_map[f"{agent}_truth"]
                agent_truth_values[agent] = sat_assignment.get(var, False)
            
            # T1 PRIMITIVE 3: check_transitivity - analyze consistency relationships
            # Build relations based on truth values and statements
            relations = []
            for agent in agents:
                if agent_truth_values.get(agent, False):
                    # Truth-teller's statements are reliable
                    for other_agent in agents:
                        if other_agent != agent:
                            stmt = statements.get(agent, "")
                            if f"{other_agent} is a liar" in stmt.lower():
                                relations.append((other_agent, "liar"))
                            elif f"{other_agent} tells the truth" in stmt.lower():
                                relations.append((other_agent, "truth"))
            
            transitivity_result = check_transitivity(relations)
            
            # Determine which agent the question is asking about
            # Look for agent names in the question
            question_agents = []
            for agent in agents:
                if agent in question:
                    question_agents.append(agent)
            
            if question_agents:
                # Answer is typically the first agent mentioned in question
                target_agent = question_agents[0]
                
                # Determine answer based on agent's truth value
                if agent_truth_values.get(target_agent, False):
                    computed_answer = f"{target_agent} tells the truth"
                else:
                    computed_answer = f"{target_agent} lies"
                
                # AMINO ACID 2: check_entailment - verify conclusion follows from premises
                # Create conclusion clause based on computed answer
                if "tells the truth" in computed_answer:
                    concl_var = var_map[f"{target_agent}_truth"]
                    conclusion_clause = [concl_var]
                else:
                    concl_var = var_map[f"{target_agent}_truth"]
                    conclusion_clause = [-concl_var]
                
                entailment = check_entailment(clauses, conclusion_clause)
                
                # T1 PRIMITIVE 4: confidence_from_agreement
                # Create multiple scoring perspectives
                scores = []
                
                # Perspective 1: SAT assignment consistency
                scores.append(1.0 if sat_assignment else 0.0)
                
                # Perspective 2: Transitivity consistency
                trans_consistent = len(transitivity_result.get("inconsistent", [])) == 0
                scores.append(1.0 if trans_consistent else 0.0)
                
                # Perspective 3: Entailment result
                scores.append(1.0 if entailment else 0.5)
                
                # Perspective 4: Paradox detection
                paradox_score = 0.0 if paradox_info and paradox_info.get("is_paradox", False) else 1.0
                scores.append(paradox_score)
                
                confidence = confidence_from_agreement(scores)
                
                # T1 PRIMITIVE 5: entropy - measure uncertainty in possible assignments
                # Consider alternative SAT solutions
                alt_clauses = clauses[:]
                # Add negation of current conclusion to see if alternatives exist
                alt_clauses.append([-c for c in conclusion_clause])
                alt_solution = solve_sat(alt_clauses, len(var_map))
                
                if alt_solution is None:
                    # Current conclusion is forced
                    prob_dist = [0.9, 0.1]  # High certainty
                else:
                    # Multiple solutions possible
                    prob_dist = [0.6, 0.4]  # Some uncertainty
                
                uncertainty = entropy(prob_dist)
                confidence = confidence * (1.0 - uncertainty * 0.5)
            
            else:
                # No specific agent in question, use topological reasoning
                # Follow topological order to determine most reliable agent
                reliable_agents = []
                for agent in topo_order:
                    if agent_truth_values.get(agent, False):
                        reliable_agents.append(agent)
                
                if reliable_agents:
                    computed_answer = reliable_agents[0]
                else:
                    computed_answer = "Inconsistent statements"
        else:
            # UNSAT - statements are contradictory
            computed_answer = "Contradiction detected"
            confidence = 0.9 if paradox_info and paradox_info.get("is_paradox", False) else 0.7
        
        # AMINO ACID 3: is_uniquely_solvable - check if CSP has unique solution
        # Convert to CSP format for uniqueness check
        variables = list(var_map.keys())
        domains = {}
        for var in variables:
            domains[var] = [0, 1]  # Boolean variables
        
        # Convert clauses to CSP constraints
        csp_constraints = []
        for clause in clauses:
            def make_constraint(clause_vars, clause_lits):
                def constraint(assignment):
                    for var, lit in zip(clause_vars, clause_lits):
                        val = assignment.get(var, None)
                        if val is not None:
                            if lit > 0 and val == 1:
                                return True
                            if lit < 0 and val == 0:
                                return True
                    # Check if all literals false
                    all_false = True
                    for var, lit in zip(clause_vars, clause_lits):
                        val = assignment.get(var, None)
                        if val is None:
                            all_false = False
                            break
                        if lit > 0 and val == 1:
                            all_false = False
                            break
                        if lit < 0 and val == 0:
                            all_false = False
                            break
                    return not all_false
                return constraint
            
            clause_vars = []
            clause_lits = []
            for lit in clause:
                abs_lit = abs(lit)
                # Find variable name for this literal
                for var_name, var_num in var_map.items():
                    if var_num == abs_lit:
                        clause_vars.append(var_name)
                        clause_lits.append(lit)
                        break
            
            if clause_vars:
                csp_constraints.append((clause_vars, make_constraint(clause_vars, clause_lits)))
        
        uniqueness = is_uniquely_solvable(variables, domains, csp_constraints)
        if uniqueness:
            confidence = min(confidence * 1.2, 1.0)
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": f"Topological order: {topo_order}, SAT: {sat_assignment is not None}, Paradox: {paradox_info}",
            "agent_truth_values": {agent: sat_assignment.get(var_map.get(f"{agent}_truth", 0), False) 
                                  for agent in agents} if sat_assignment else {}
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
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
        """Calibrate scores to ensure proper distribution."""
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