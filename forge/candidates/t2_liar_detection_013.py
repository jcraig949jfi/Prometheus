import re
import zlib
from typing import Dict, List, Any, Tuple, Set
from forge_primitives import (
    bayesian_update,
    confidence_from_agreement,
    entropy,
    modus_ponens,
    track_beliefs,
    solve_sat
)
from forge.amino_acids.pysat_acids import detect_paradox, check_entailment
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable


class ReasoningTool:
    """evolutionary_biology x pysat_acids - liar_detection"""

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
        """Parse prompt to extract agents, statements, and truth policies."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        agents = set()
        statements = []
        truth_policies = {}
        question = lines[-1] if lines else ""

        # Find agent names (capitalized words that appear as subjects)
        for line in lines:
            words = line.split()
            for i, word in enumerate(words):
                if word[0].isupper() and len(word) > 1:
                    # Check if it's followed by "says", "claims", "always", etc.
                    next_words = words[i+1:i+3] if i+1 < len(words) else []
                    if any(key in ' '.join(next_words).lower() for key in ['says', 'claims', 'states', 'always', 'never']):
                        agents.add(word)

        # Extract statements and policies
        for line in lines:
            line_lower = line.lower()
            for agent in agents:
                if agent.lower() in line_lower:
                    # Look for truth-telling patterns
                    if 'always tells the truth' in line_lower or 'truth-teller' in line_lower:
                        truth_policies[agent] = 'truth'
                    elif 'always lies' in line_lower or 'liar' in line_lower:
                        truth_policies[agent] = 'lie'
                    elif 'alternates' in line_lower or 'sometimes' in line_lower:
                        truth_policies[agent] = 'alternating'
                    
                    # Extract quoted statements or simple declaratives
                    if 'says' in line_lower or 'claims' in line_lower:
                        # Find the statement after "says" or similar
                        parts = line.split('says' if 'says' in line_lower else 'claims', 1)
                        if len(parts) > 1:
                            statement = parts[1].strip(' "\'')
                            if statement:
                                statements.append((agent, statement))

        return {
            "agents": list(agents),
            "statements": statements,
            "policies": truth_policies,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use evolutionary biology as scaffold: agents as species with fixed truth-telling traits.
        Truth-tellers have high fitness (reliable information), liars have low fitness (unreliable).
        The puzzle is an evolutionary game where statements compete for survival under selection pressure.
        The solution is the statement/agent that survives logical consistency checks."""
        
        agents = structure["agents"]
        statements = structure["statements"]
        policies = structure["policies"]
        
        # Evolutionary biology concepts:
        # 1. Fitness = logical consistency score
        # 2. Selection pressure = SAT solving eliminates inconsistent assignments
        # 3. Evolutionary stable strategy = truth assignment that survives all constraints
        
        # Build SAT clauses from statements and policies
        clauses = []
        var_map = {}
        var_counter = 1
        
        # Create variables for each statement's truth value
        for agent, stmt in statements:
            var_name = f"S_{agent}_{hash(stmt) % 1000}"
            var_map[(agent, stmt)] = var_counter
            var_counter += 1
        
        # Create variables for each agent's type
        agent_vars = {}
        for agent in agents:
            agent_vars[agent] = var_counter
            var_counter += 1
        
        # Add constraints based on truth policies
        for agent, policy in policies.items():
            agent_var = agent_vars[agent]
            if policy == 'truth':
                # If agent is truth-teller, all their statements must be true
                for (a, stmt), stmt_var in var_map.items():
                    if a == agent:
                        # agent_var -> stmt_var (if truth-teller, statement is true)
                        clauses.append([-agent_var, stmt_var])
            elif policy == 'lie':
                # If agent is liar, all their statements must be false
                for (a, stmt), stmt_var in var_map.items():
                    if a == agent:
                        # agent_var -> -stmt_var (if liar, statement is false)
                        clauses.append([-agent_var, -stmt_var])
        
        # Add constraints for statement relationships
        # Parse simple logical relationships from statements
        for agent, stmt in statements:
            stmt_var = var_map.get((agent, stmt))
            if not stmt_var:
                continue
            
            # Check for negations or contradictions
            stmt_lower = stmt.lower()
            for other_agent, other_stmt in statements:
                other_var = var_map.get((other_agent, other_stmt))
                if not other_var:
                    continue
                
                # If one statement negates another
                if ('not' in stmt_lower and other_stmt.lower() in stmt_lower.replace('not', '')) or \
                   ('false' in stmt_lower and other_agent in stmt_lower):
                    clauses.append([-stmt_var, -other_var])
                    clauses.append([stmt_var, other_var])
        
        # Use T1 primitives for evolutionary reasoning
        
        # 1. Bayesian update to adjust belief in agent types based on statement consistency
        prior_truth = 0.5
        likelihood_consistent = 0.9  # High likelihood if statements are consistent
        posterior = bayesian_update(prior_truth, likelihood_consistent)
        if posterior is None:
            posterior = prior_truth
        
        # 2. Track beliefs of a meta-observer (evolutionary pressure)
        meta_observations = []
        for agent in agents:
            # Observer sees if agent's statements are consistent
            consistent = len([s for a, s in statements if a == agent]) > 0
            meta_observations.append(('MetaObserver', agent, consistent))
        
        belief_tracking = track_beliefs(['MetaObserver'] + agents, meta_observations)
        
        # 3. Compute entropy of possible truth assignments (evolutionary diversity)
        if clauses:
            sat_result = solve_sat(clauses, var_counter - 1)
            if sat_result:
                # Count true assignments for each agent type
                agent_assignments = []
                for agent in agents:
                    agent_var = agent_vars[agent]
                    if agent_var in sat_result and sat_result[agent_var]:
                        agent_assignments.append(1.0)
                    else:
                        agent_assignments.append(0.0)
                
                if agent_assignments:
                    diversity_entropy = entropy([a/sum(agent_assignments) for a in agent_assignments] if sum(agent_assignments) > 0 else [1/len(agent_assignments)]*len(agent_assignments))
                else:
                    diversity_entropy = 0.0
            else:
                diversity_entropy = 0.0
        else:
            diversity_entropy = 0.0
        
        # 4. Use amino acid to detect paradox (evolutionary dead end)
        paradox_info = None
        if clauses:
            paradox_info = detect_paradox(clauses)
        
        # 5. Use amino acid to check entailment of the question
        question_entailment = None
        if structure["question"] and clauses:
            # Create a dummy clause for the question
            question_clause = [1]  # Placeholder
            question_entailment = check_entailment(clauses, question_clause)
        
        # 6. Confidence from agreement of multiple reasoning paths
        confidence_scores = []
        if posterior > 0.5:
            confidence_scores.append(posterior)
        if diversity_entropy > 0:
            confidence_scores.append(1.0 - diversity_entropy)
        if paradox_info is False:  # No paradox means more confidence
            confidence_scores.append(0.8)
        
        confidence = confidence_from_agreement(confidence_scores) if confidence_scores else 0.5
        
        # Determine the answer: which agent or statement is correct?
        # Evolutionary stable solution: the one that survives all constraints
        computed_answer = ""
        
        # Try to solve the constraint satisfaction problem
        if clauses:
            # Use amino acid to find first solution
            # Convert to CSP format
            variables = []
            domains = {}
            for i in range(1, var_counter):
                variables.append(str(i))
                domains[str(i)] = [0, 1]  # Boolean
            
            # Convert clauses to constraints
            csp_constraints = []
            for clause in clauses:
                def make_constraint(clause_vars):
                    def constraint(assignment):
                        for var in clause_vars:
                            val = assignment.get(var, 0)
                            if var.startswith('-'):
                                var_name = var[1:]
                                if assignment.get(var_name, 0) == 0:
                                    return True
                            else:
                                if assignment.get(var, 0) == 1:
                                    return True
                        return False
                    return constraint
                
                clause_vars = []
                for lit in clause:
                    if lit > 0:
                        clause_vars.append(str(lit))
                    else:
                        clause_vars.append(f"-{abs(lit)}")
                
                csp_constraints.append((clause_vars, make_constraint(clause_vars)))
            
            solution = solve_first(variables, domains, csp_constraints)
            
            if solution:
                # Find which agent is truth-teller in the solution
                truth_tellers = []
                for agent, var_idx in agent_vars.items():
                    if solution.get(str(var_idx), 0) == 1:
                        truth_tellers.append(agent)
                
                if truth_tellers:
                    computed_answer = truth_tellers[0]
                else:
                    # Fallback: agent mentioned in question
                    for agent in agents:
                        if agent.lower() in structure["question"].lower():
                            computed_answer = agent
                            break
                    
                    if not computed_answer and agents:
                        computed_answer = agents[0]
            else:
                # No solution found
                computed_answer = "No consistent assignment"
        else:
            computed_answer = "Insufficient constraints"
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": f"Evolutionary stability analysis with entropy {diversity_entropy:.2f}, posterior {posterior:.2f}",
            "clauses": len(clauses),
            "agents": agents,
            "policies": policies
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        results = []
        
        for candidate in candidates:
            # Primary: check if computed answer appears in candidate
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity
                base_score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
            
            # Adjust by confidence
            adjusted_score = base_score * reasoning_result["confidence"]
            
            results.append({
                "candidate": candidate,
                "score": adjusted_score,
                "base_score": base_score,
                "confidence": reasoning_result["confidence"]
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper distribution."""
        if not scored:
            return scored
        
        # Simple normalization to [0, 1] range
        scores = [item["score"] for item in scored]
        if max(scores) > 0:
            for item in scored:
                item["score"] = item["score"] / max(scores)
        
        return scored

    def _ncd(self, a: str, b: str) -> float:
        """Normalized Compression Distance."""
        if not a or not b:
            return 1.0
        
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + " " + b).encode()))
        
        if max(ca, cb) > 0:
            return (cab - min(ca, cb)) / max(ca, cb)
        return 1.0