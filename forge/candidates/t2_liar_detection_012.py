import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import (
    bayesian_update,
    confidence_from_agreement,
    entropy,
    solve_sat,
    modus_ponens,
    track_beliefs
)
from forge.amino_acids.pysat_acids import detect_paradox, check_entailment
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable


class ReasoningTool:
    """quantum_mechanics x pysat_acids - liar_detection"""

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
        """Parse the prompt to extract agents, statements, and truth policies."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        agents = []
        statements = []
        truth_policies = {}  # agent -> policy (e.g., "always lies", "alternates")
        question = lines[-1] if lines else ""

        # Extract agent names (capitalized words that appear before colons or as subjects)
        for line in lines:
            # Look for patterns like "Alice says: ..." or "Bob claims ..."
            colon_match = re.match(r'^([A-Z][a-z]+)(?:\s+says?|claims?|states?)?:', line)
            if colon_match:
                agent = colon_match.group(1)
                if agent not in agents:
                    agents.append(agent)
                # Extract statement after colon
                statement_part = line.split(':', 1)[1].strip()
                if statement_part:
                    statements.append((agent, statement_part))

            # Also look for policy descriptions
            lower_line = line.lower()
            for agent in agents:
                if agent.lower() in lower_line:
                    if "always lies" in lower_line or "never tells the truth" in lower_line:
                        truth_policies[agent] = "always_lies"
                    elif "always tells the truth" in lower_line or "never lies" in lower_line:
                        truth_policies[agent] = "always_truth"
                    elif "alternates" in lower_line:
                        truth_policies[agent] = "alternates"
                    elif "random" in lower_line:
                        truth_policies[agent] = "random"

        # If no explicit policies, infer from statements about truthfulness
        for agent in agents:
            if agent not in truth_policies:
                # Check if any statement mentions the agent's truthfulness
                for _, stmt in statements:
                    if agent.lower() in stmt.lower() and ("lies" in stmt.lower() or "truth" in stmt.lower()):
                        if "lies" in stmt.lower():
                            truth_policies[agent] = "always_lies"
                        elif "truth" in stmt.lower():
                            truth_policies[agent] = "always_truth"
                        break
                else:
                    truth_policies[agent] = "unknown"

        return {
            "agents": agents,
            "statements": statements,
            "truth_policies": truth_policies,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use quantum superposition and entanglement as a scaffold for liar puzzles."""
        agents = structure["agents"]
        statements = structure["statements"]
        policies = structure["truth_policies"]

        # Quantum mechanics scaffold: treat each agent's truth-value as a qubit in superposition
        # The system state is entangled across agents due to mutual statements
        # Measurement (answering the question) collapses to a classical truth assignment

        # Step 1: Encode as SAT problem (quantum superposition of all possible worlds)
        clauses = []
        var_map = {}  # (agent, statement_idx) -> SAT variable number
        next_var = 1

        # Create variables for each statement's truth value
        for i, (agent, stmt) in enumerate(statements):
            var_map[(agent, i)] = next_var
            next_var += 1

        # Add constraints based on truth policies (collapse possibilities)
        for agent, policy in policies.items():
            agent_vars = [var_map[(a, idx)] for (a, idx) in var_map.keys() if a == agent]
            if policy == "always_lies":
                # All statements by this agent are false
                for v in agent_vars:
                    clauses.append([-v])
            elif policy == "always_truth":
                # All statements by this agent are true
                for v in agent_vars:
                    clauses.append([v])
            elif policy == "alternates":
                # Alternate truth values (simplify: first statement true, second false, etc.)
                for idx, v in enumerate(agent_vars):
                    if idx % 2 == 0:
                        clauses.append([v])
                    else:
                        clauses.append([-v])

        # Add constraints from statement content (entanglement)
        # Parse simple logical relationships: "A says B is lying" etc.
        for i, (agent, stmt) in enumerate(statements):
            stmt_lower = stmt.lower()
            # Check if statement is about another agent's truthfulness
            for other_agent in agents:
                if other_agent.lower() in stmt_lower and other_agent != agent:
                    if "lying" in stmt_lower or "lies" in stmt_lower:
                        # "A says B is lying" means: A's statement is true iff B's next statement is false
                        # Find B's next statement index
                        b_stmts = [(a, idx) for (a, idx) in var_map.keys() if a == other_agent]
                        if b_stmts:
                            # Use the first statement by B for simplicity
                            b_var = var_map[b_stmts[0]]
                            a_var = var_map[(agent, i)]
                            # Encoding: (A_var ↔ ¬B_var) -> two clauses
                            clauses.append([-a_var, -b_var])  # If A true then B false
                            clauses.append([a_var, b_var])    # If A false then B true
                    elif "truth" in stmt_lower or "honest" in stmt_lower:
                        # "A says B tells truth" means: A's statement is true iff B's next statement is true
                        b_stmts = [(a, idx) for (a, idx) in var_map.keys() if a == other_agent]
                        if b_stmts:
                            b_var = var_map[b_stmts[0]]
                            a_var = var_map[(agent, i)]
                            clauses.append([-a_var, b_var])   # If A true then B true
                            clauses.append([a_var, -b_var])   # If A false then B false

        # Use T1 primitive: solve_sat to find a consistent assignment (collapsed quantum state)
        sat_assignment = solve_sat(clauses, next_var - 1)

        # Use amino acid: detect_paradox to check for contradictions (quantum interference)
        paradox_result = detect_paradox(clauses)
        has_paradox = paradox_result is not None and paradox_result

        # Use T1 primitive: entropy to measure uncertainty in the system
        if sat_assignment:
            # Count true/false assignments
            true_count = sum(1 for v in sat_assignment.values() if v)
            total = len(sat_assignment)
            if total > 0:
                p_true = true_count / total
                p_false = 1 - p_true
                system_entropy = entropy([p_true, p_false]) if p_true > 0 and p_false > 0 else 0.0
            else:
                system_entropy = 0.0
        else:
            system_entropy = 1.0  # Max entropy if no consistent assignment

        # Use amino acid: check_entailment to see if question answer follows logically
        # Parse question to extract what's being asked
        question = structure["question"].lower()
        answer_entity = None

        # Look for "who" questions
        if "who" in question:
            # Find agent mentioned in question
            for agent in agents:
                if agent.lower() in question:
                    answer_entity = agent
                    break
            if not answer_entity and agents:
                # Default to first agent if specific not found
                answer_entity = agents[0]

        # Look for "what" questions about statements
        elif "what" in question and "say" in question:
            # Find the most probable statement truth value
            if sat_assignment and statements:
                # Find statement with highest confidence
                stmt_truths = []
                for (agent, stmt), var in [(stmt, var_map.get((agent, i))) for i, (agent, stmt) in enumerate(statements)]:
                    if var and var in sat_assignment:
                        stmt_truths.append((stmt, sat_assignment[var]))
                if stmt_truths:
                    # Use T1 primitive: confidence_from_agreement on truth values
                    truth_scores = [1.0 if truth else 0.0 for _, truth in stmt_truths]
                    if truth_scores:
                        conf = confidence_from_agreement(truth_scores)
                        # Select statement with truth value matching highest confidence
                        if conf > 0.5:
                            true_stmts = [stmt for stmt, truth in stmt_truths if truth]
                            if true_stmts:
                                answer_entity = true_stmts[0]
                            else:
                                answer_entity = stmt_truths[0][0]
                        else:
                            answer_entity = stmt_truths[0][0]

        # If no specific entity found, determine the actual liar/truth-teller
        if not answer_entity:
            # Use quantum-inspired reasoning: collapse to most probable consistent world
            if sat_assignment:
                # Count lies per agent
                agent_lie_count = {agent: 0 for agent in agents}
                for (agent, i), var in var_map.items():
                    if var in sat_assignment:
                        # If agent's statement is false, it's a lie (unless policy forces it)
                        if not sat_assignment[var]:
                            agent_lie_count[agent] += 1
                
                # Use T1 primitive: bayesian_update to refine confidence
                prior = 0.5
                # Likelihood: more lies -> more likely to be designated liar in question
                total_lies = sum(agent_lie_count.values())
                if total_lies > 0:
                    for agent in agents:
                        likelihood = agent_lie_count[agent] / total_lies if total_lies > 0 else 0.5
                        posterior = bayesian_update(prior, likelihood)
                        if posterior > 0.7:  # High confidence threshold
                            answer_entity = agent
                            break
                
                if not answer_entity:
                    # Fallback: agent with most lies
                    answer_entity = max(agent_lie_count.items(), key=lambda x: x[1])[0]
            else:
                # No consistent assignment, use first agent
                answer_entity = agents[0] if agents else "Unknown"

        # Use amino acid: is_uniquely_solvable to check if solution is unique (quantum degeneracy)
        # Convert to CSP for uniqueness check
        if var_map:
            variables = list(var_map.keys())
            domains = {v: [True, False] for v in variables}
            constraints = []
            # Convert clauses to CSP constraints
            for clause in clauses:
                def make_constraint(clause_vars, clause_lits):
                    def constraint(assignment):
                        for var, lit in zip(clause_vars, clause_lits):
                            if var in assignment:
                                if lit > 0 and assignment[var] == True:
                                    return True
                                if lit < 0 and assignment[var] == False:
                                    return True
                        return False
                    return constraint
                
                clause_vars = []
                clause_lits = []
                for lit in clause:
                    abs_lit = abs(lit)
                    var = next((v for v, num in var_map.items() if num == abs_lit), None)
                    if var:
                        clause_vars.append(var)
                        clause_lits.append(lit)
                if clause_vars:
                    constraints.append((clause_vars, make_constraint(clause_vars, clause_lits)))
            
            unique = is_uniquely_solvable(domains, constraints)
        else:
            unique = False

        confidence = 0.8 if not has_paradox and unique else 0.5
        confidence = min(confidence, 1.0 - system_entropy)  # Quantum uncertainty principle

        return {
            "answer": answer_entity,
            "confidence": confidence,
            "reasoning": f"Quantum collapse to consistent assignment. Paradox: {has_paradox}, Unique: {unique}, Entropy: {system_entropy:.2f}",
            "has_paradox": has_paradox,
            "is_unique": unique,
            "system_entropy": system_entropy
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = str(reasoning_result["answer"])
        results = []
        
        for candidate in candidates:
            # Primary: check if computed answer appears in candidate text
            if computed_answer.lower() in candidate.lower():
                score = 1.0
            else:
                # Fallback: NCD similarity
                score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
            
            results.append({
                "candidate": candidate,
                "raw_score": score,
                "confidence": reasoning_result["confidence"]
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores with confidence and reasoning metrics."""
        calibrated = []
        for item in scored:
            # Adjust score by confidence
            adjusted = item["raw_score"] * item["confidence"]
            # Add small boost for high confidence
            if item["confidence"] > 0.8:
                adjusted = min(1.0, adjusted * 1.1)
            
            calibrated.append({
                "candidate": item["candidate"],
                "score": adjusted,
                "raw_score": item["raw_score"],
                "confidence": item["confidence"]
            })
        
        return calibrated

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