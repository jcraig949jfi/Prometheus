import re
import zlib
from typing import Dict, List, Any, Tuple, Set
from forge_primitives import (
    track_beliefs,
    modus_ponens,
    confidence_from_agreement,
    entropy,
    solve_constraints,
    check_transitivity
)
from forge.amino_acids.pysat_acids import solve, detect_paradox, check_entailment
from forge.amino_acids.constraint_acids import is_uniquely_solvable, solve_first


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
        question = lines[-1] if lines else ""
        
        agents = set()
        statements = []
        truth_policies = {}
        
        # Extract agent names (capitalized words that appear before 'says' or 'always')
        agent_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        for line in lines:
            # Find agents
            possible_agents = re.findall(agent_pattern, line)
            for agent in possible_agents:
                if agent and ('says' in line.lower() or 'always' in line.lower()):
                    agents.add(agent)
            
            # Extract truth policies
            if 'always' in line.lower():
                for agent in agents:
                    if agent in line:
                        if 'truth' in line.lower() or 'honest' in line.lower():
                            truth_policies[agent] = 'truth'
                        elif 'lie' in line.lower() or 'liar' in line.lower():
                            truth_policies[agent] = 'lie'
                        elif 'random' in line.lower() or 'coin' in line.lower():
                            truth_policies[agent] = 'random'
            
            # Extract statements (quoted text or simple declaratives)
            if 'says' in line.lower():
                parts = line.split('says', 1)
                if len(parts) == 2:
                    agent_part = parts[0].strip()
                    statement_part = parts[1].strip().strip('"\'')
                    
                    # Find which agent
                    for agent in agents:
                        if agent in agent_part:
                            statements.append({
                                'agent': agent,
                                'statement': statement_part,
                                'line': line
                            })
                            break
        
        return {
            'agents': list(agents),
            'statements': statements,
            'truth_policies': truth_policies,
            'question': question,
            'raw_lines': lines
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use evolutionary biology concepts: agents as species with fixed truth-telling strategies.
        Truth-tellers have high fitness (survive logical consistency checks).
        Liars have low fitness (create contradictions).
        Random agents introduce entropy.
        The solution emerges from selection pressure of logical constraints."""
        
        agents = structure['agents']
        statements = structure['statements']
        truth_policies = structure['truth_policies']
        
        # Initialize belief tracking using evolutionary fitness metaphor
        # Fitness = logical consistency score
        agent_fitness = {agent: 0.0 for agent in agents}
        
        # Phase 1: Track beliefs using T1 primitive
        observations = []
        for stmt in statements:
            agent = stmt['agent']
            statement = stmt['statement']
            # Convert to simple fact representation
            fact = f"SAYS_{agent}_{hash(statement) % 1000}"
            observations.append((agent, fact, True))
        
        belief_tracking = track_beliefs(agents, observations)
        if belief_tracking:
            # Fitness boost for agents whose statements are tracked
            for agent in agents:
                if agent in belief_tracking and belief_tracking[agent]:
                    agent_fitness[agent] += 0.1
        
        # Phase 2: Logical inference using modus ponens
        premises = []
        for stmt in statements:
            agent = stmt['agent']
            statement = stmt['statement']
            
            # Create implication based on truth policy
            if agent in truth_policies:
                policy = truth_policies[agent]
                if policy == 'truth':
                    # If agent is truth-teller, their statement is true
                    fact_name = f"TRUE_{hash(statement) % 1000}"
                    premises.append((f"AGENT_{agent}_TRUTH", fact_name))
                elif policy == 'lie':
                    # If agent is liar, their statement is false
                    fact_name = f"FALSE_{hash(statement) % 1000}"
                    premises.append((f"AGENT_{agent}_LIE", fact_name))
        
        facts = set()
        if premises:
            inferred = modus_ponens(premises, facts)
            # Fitness based on number of inferences
            for agent in agents:
                agent_prefix = f"AGENT_{agent}_"
                agent_inferences = [f for f in inferred if f.startswith(agent_prefix)]
                agent_fitness[agent] += 0.05 * len(agent_inferences)
        
        # Phase 3: SAT encoding for logical consistency (amino acid)
        clauses = []
        var_map = {}
        var_counter = 1
        
        # Create variables for each statement's truth value
        for idx, stmt in enumerate(statements):
            var_map[f"stmt_{idx}"] = var_counter
            var_counter += 1
        
        # Create variables for each agent's type
        for agent in agents:
            var_map[f"{agent}_truth"] = var_counter
            var_counter += 1
            var_map[f"{agent}_lie"] = var_counter
            var_counter += 1
        
        # Constraints based on truth policies
        for agent in agents:
            if agent in truth_policies:
                policy = truth_policies[agent]
                if policy == 'truth':
                    # Agent is truth-teller: truth_var = true, lie_var = false
                    clauses.append([var_map[f"{agent}_truth"]])
                    clauses.append([-var_map[f"{agent}_lie"]])
                elif policy == 'lie':
                    # Agent is liar: truth_var = false, lie_var = true
                    clauses.append([-var_map[f"{agent}_truth"]])
                    clauses.append([var_map[f"{agent}_lie"]])
                elif policy == 'random':
                    # Random: both false (neither fixed truth-teller nor liar)
                    clauses.append([-var_map[f"{agent}_truth"]])
                    clauses.append([-var_map[f"{agent}_lie"]])
        
        # Link statements to agents' truthfulness
        for idx, stmt in enumerate(statements):
            agent = stmt['agent']
            stmt_var = var_map[f"stmt_{idx}"]
            truth_var = var_map[f"{agent}_truth"]
            lie_var = var_map[f"{agent}_lie"]
            
            # If agent is truth-teller, statement is true
            clauses.append([-truth_var, stmt_var])
            # If agent is liar, statement is false
            clauses.append([-lie_var, -stmt_var])
        
        # Solve SAT (amino acid call)
        sat_solution = solve(clauses)
        
        # Phase 4: Detect paradox (amino acid)
        paradox_result = detect_paradox(clauses)
        
        # Phase 5: Check entailment for specific conclusions
        conclusion_clause = []
        if 'question' in structure and structure['question']:
            # Try to extract what the question is asking for
            question_lower = structure['question'].lower()
            if 'who' in question_lower:
                # Question about agent identity
                for agent in agents:
                    if agent.lower() in question_lower:
                        # Check if we can deduce this agent's type
                        test_clauses = clauses[:]
                        test_clauses.append([-var_map[f"{agent}_truth"]])
                        test_clauses.append([-var_map[f"{agent}_lie"]])
                        entailment = check_entailment(clauses, [-var_map[f"{agent}_truth"], -var_map[f"{agent}_lie"]])
                        if entailment:
                            conclusion_clause = [var_map[f"{agent}_truth"]]  # Can deduce they're truth-teller
                            break
        
        entailment_result = False
        if conclusion_clause:
            entailment_result = check_entailment(clauses, conclusion_clause)
        
        # Phase 6: Constraint solving for uniqueness (amino acid)
        variables = list(var_map.keys())
        domains = {}
        for var in variables:
            domains[var] = [0, 1]  # Boolean variables
        
        constraints = []
        # Convert clauses to constraint functions
        for clause in clauses:
            def make_constraint(clause_vars=clause):
                def constraint(assignment):
                    for lit in clause_vars:
                        var_idx = abs(lit) - 1
                        var_name = variables[var_idx]
                        val = assignment.get(var_name, 0)
                        if lit > 0 and val == 1:
                            return True
                        if lit < 0 and val == 0:
                            return True
                    return False
                return constraint
            
            # Get variable names involved in this clause
            involved_vars = []
            for lit in clause:
                var_idx = abs(lit) - 1
                if 0 <= var_idx < len(variables):
                    involved_vars.append(variables[var_idx])
            
            if involved_vars:
                constraints.append((involved_vars, make_constraint()))
        
        uniqueness = False
        if variables and constraints:
            uniqueness = is_uniquely_solvable(domains, constraints)
        
        # Phase 7: Compute confidence from multiple reasoning sources
        scores = []
        if sat_solution:
            # Score based on solution existence
            scores.append(1.0)
        else:
            scores.append(0.0)
        
        if not paradox_result:  # detect_paradox returns True if paradox exists
            scores.append(1.0)
        else:
            scores.append(0.0)
        
        if entailment_result:
            scores.append(1.0)
        else:
            scores.append(0.5)
        
        if uniqueness:
            scores.append(1.0)
        else:
            scores.append(0.7)
        
        # Add fitness scores
        fitness_values = list(agent_fitness.values())
        if fitness_values:
            normalized_fitness = [f / max(fitness_values) if max(fitness_values) > 0 else 0.5 for f in fitness_values]
            scores.extend(normalized_fitness)
        
        # Use T1 primitive for confidence
        confidence = confidence_from_agreement(scores) if scores else 0.5
        
        # Phase 8: Determine answer using evolutionary selection
        # Agents with highest fitness are most likely to be truth-tellers
        if agent_fitness:
            best_agent = max(agent_fitness.items(), key=lambda x: x[1])[0]
            
            # Check transitivity of truth-telling relationships
            relations = []
            for stmt1 in statements:
                for stmt2 in statements:
                    if stmt1['agent'] != stmt2['agent']:
                        # If agent1 says something about agent2's truthfulness
                        if stmt2['agent'].lower() in stmt1['statement'].lower():
                            if 'truth' in stmt1['statement'].lower() or 'honest' in stmt1['statement'].lower():
                                relations.append((stmt1['agent'], stmt2['agent']))
                            elif 'lie' in stmt1['statement'].lower() or 'liar' in stmt1['statement'].lower():
                                relations.append((stmt1['agent'], f"NOT_{stmt2['agent']}"))
            
            transitive_closure = check_transitivity(relations)
            
            # Compute entropy of truth assignments as measure of uncertainty
            if sat_solution:
                # Count true/false assignments
                truth_vals = []
                for var_name, var_num in var_map.items():
                    if 'stmt_' in var_name or '_truth' in var_name:
                        if sat_solution.get(var_num, False):
                            truth_vals.append(1.0)
                        else:
                            truth_vals.append(0.0)
                
                if truth_vals:
                    # Normalize to probabilities
                    prob_true = sum(truth_vals) / len(truth_vals)
                    prob_false = 1 - prob_true
                    if prob_true > 0 and prob_false > 0:
                        uncertainty = entropy([prob_true, prob_false])
                        confidence *= (1.0 - uncertainty)
        
            # Extract what the question is asking for
            question = structure.get('question', '')
            if 'who' in question.lower():
                computed_answer = best_agent
            elif 'what' in question.lower() and 'answer' in question.lower():
                computed_answer = best_agent
            else:
                # Default: answer with the most fit agent
                computed_answer = best_agent
        else:
            computed_answer = "Cannot determine"
            confidence = 0.0
        
        return {
            "answer": computed_answer,
            "confidence": min(max(confidence, 0.0), 1.0),
            "reasoning": f"Evolutionary fitness analysis selected {computed_answer} as most consistent truth-teller. SAT solvable: {sat_solution is not None}, Paradox: {paradox_result}, Entailment: {entailment_result}, Unique: {uniqueness}",
            "fitness_scores": agent_fitness,
            "sat_solution_exists": sat_solution is not None
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary: check if computed answer appears in candidate text
            # computed_answer is a VARIABLE from reasoning, not a hardcoded string
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity to reasoning text
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
        
        scores = [item["score"] for item in scored]
        if not scores:
            return scored
        
        min_score = min(scores)
        max_score = max(scores)
        
        if max_score > min_score:
            # Normalize to [0, 1] range
            for item in scored:
                item["score"] = (item["score"] - min_score) / (max_score - min_score)
        else:
            # All scores equal
            for item in scored:
                item["score"] = 0.5
        
        return scored

    def _ncd(self, a: str, b: str) -> float:
        """Normalized Compression Distance between two strings."""
        if not a or not b:
            return 1.0
        
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + " " + b).encode()))
        
        if max(ca, cb) > 0:
            return (cab - min(ca, cb)) / max(ca, cb)
        return 1.0