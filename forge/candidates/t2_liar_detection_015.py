import re
import zlib
from typing import Dict, List, Any

from forge_primitives import (
    bayesian_update,
    entropy,
    confidence_from_agreement,
    solve_sat,
    track_beliefs,
    modus_ponens
)
from forge.amino_acids.pysat_acids import detect_paradox, check_entailment
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable


class ReasoningTool:
    """Thermodynamics x SAT/Constraint Solving - Liar Detection"""

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
        """Extract agents, statements, and truth-telling policies from the prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""

        # Find agent names (capitalized words that appear before 'says' or 'always')
        agent_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        agents = set()
        statements = []
        policies = {}  # agent -> policy: 'truth', 'lie', 'alternate', etc.

        for line in lines:
            # Look for truth-telling policies
            if 'always tells the truth' in line.lower():
                match = re.search(agent_pattern, line)
                if match:
                    agent = match.group(1)
                    agents.add(agent)
                    policies[agent] = 'truth'
            elif 'always lies' in line.lower():
                match = re.search(agent_pattern, line)
                if match:
                    agent = match.group(1)
                    agents.add(agent)
                    policies[agent] = 'lie'
            elif 'alternates' in line.lower() or 'alternately' in line.lower():
                match = re.search(agent_pattern, line)
                if match:
                    agent = match.group(1)
                    agents.add(agent)
                    policies[agent] = 'alternate'
            # Extract statements: "X says: ..."
            if 'says' in line:
                parts = line.split('says', 1)
                if len(parts) == 2:
                    agent_match = re.search(agent_pattern, parts[0].strip())
                    if agent_match:
                        agent = agent_match.group(1)
                        agents.add(agent)
                        statement = parts[1].strip().strip('"\'')
                        statements.append((agent, statement))

        # If policies not explicitly stated, infer from context
        for agent in agents:
            if agent not in policies:
                policies[agent] = 'unknown'

        return {
            "agents": list(agents),
            "statements": statements,
            "policies": policies,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use thermodynamic reasoning to resolve liar puzzles."""
        agents = structure["agents"]
        statements = structure["statements"]
        policies = structure["policies"]
        question = structure["question"]

        # THERMODYNAMIC ANALOGY:
        # - Each possible world state is a microstate with an energy level.
        # - Energy = logical inconsistency (paradox) score.
        # - The ground state (lowest energy) is the most consistent assignment.
        # - Temperature = uncertainty in policy interpretation.

        # Step 1: Encode statements as logical constraints
        # Each statement becomes a propositional variable
        prop_vars = {}
        var_counter = 1
        for agent, stmt in statements:
            prop_vars[(agent, stmt)] = var_counter
            var_counter += 1

        # Step 2: Build SAT clauses based on truth-telling policies
        clauses = []
        for (agent, stmt), var in prop_vars.items():
            policy = policies.get(agent, 'unknown')
            if policy == 'truth':
                # If agent tells truth, statement must be TRUE
                clauses.append([var])
            elif policy == 'lie':
                # If agent lies, statement must be FALSE
                clauses.append([-var])
            elif policy == 'alternate':
                # Alternating: we need to model sequence. For simplicity, treat as unknown.
                # This adds uncertainty (temperature).
                pass

        # Step 3: Add constraints from statement content
        # Parse simple logical relationships in statements
        for (agent, stmt), var in prop_vars.items():
            # Look for negations
            if 'not' in stmt.lower():
                # Find what is being negated
                negated = stmt.lower().replace('not', '').strip()
                # Find if another statement matches the negated content
                for (other_agent, other_stmt), other_var in prop_vars.items():
                    if other_stmt.lower() == negated:
                        clauses.append([-var, -other_var])  # Cannot both be true
                        clauses.append([var, other_var])    # Cannot both be false
                        break

        # Step 4: Use amino acid to detect paradox
        paradox_info = detect_paradox(clauses)
        if paradox_info is None:
            paradox_detected = False
        else:
            paradox_detected = bool(paradox_info)

        # Step 5: Use thermodynamic energy calculation
        # Energy = entropy of possible worlds + paradox penalty
        # First, count possible worlds (satisfying assignments)
        world_count = 0
        try:
            # Use solve_sat primitive to find one solution
            assignment = solve_sat(clauses, len(prop_vars))
            if assignment:
                # Estimate number of solutions by checking uniqueness
                domains = {f"v{i}": [0, 1] for i in range(1, len(prop_vars) + 1)}
                csp_constraints = []
                for clause in clauses:
                    def make_constraint(cl=clause):
                        def constraint(**vals):
                            for lit in cl:
                                var_idx = abs(lit)
                                val = vals[f"v{var_idx}"]
                                if lit > 0:
                                    if val != 1:
                                        return False
                                else:
                                    if val != 0:
                                        return False
                            return True
                        return constraint
                    csp_constraints.append(([f"v{abs(lit)}" for lit in clause], make_constraint()))
                
                unique = is_uniquely_solvable(domains, csp_constraints)
                if unique:
                    world_count = 1
                else:
                    world_count = 2  # Assume at least 2 if not unique
        except Exception:
            world_count = 0

        # Calculate entropy (disorder) of the system
        if world_count > 0:
            probs = [1.0 / world_count] * world_count
            system_entropy = entropy(probs)
        else:
            system_entropy = 1.0  # Max uncertainty

        # Paradox penalty: high energy if contradictory
        paradox_penalty = 10.0 if paradox_detected else 0.0
        energy = system_entropy + paradox_penalty

        # Step 6: Determine the most probable truth values
        # Use Bayesian update to incorporate policy confidence
        prior = 0.5  # Initial belief a random statement is true
        likelihood = 0.8 if not paradox_detected else 0.2
        posterior = bayesian_update(prior, likelihood)
        if posterior is None:
            posterior = prior

        # Step 7: Track agent beliefs using primitive
        observations = []
        for (agent, stmt), var in prop_vars.items():
            # If we had an assignment, use it
            truth_value = True if posterior > 0.5 else False
            observations.append((agent, stmt, truth_value))
        
        belief_tracking = track_beliefs(agents, observations)
        if belief_tracking is None:
            belief_tracking = {}

        # Step 8: Extract answer from question
        # Look for "who", "what", "which" in question
        computed_answer = ""
        if 'who' in question.lower():
            # Find the agent that is the answer
            # In liar puzzles, often the one whose statement is consistent
            consistent_agents = []
            for agent in agents:
                agent_stmts = [stmt for (a, stmt) in statements if a == agent]
                if agent_stmts:
                    # Simple heuristic: agent with truth policy is often answer
                    if policies.get(agent) == 'truth':
                        consistent_agents.append(agent)
            if consistent_agents:
                computed_answer = consistent_agents[0]
            else:
                computed_answer = agents[0] if agents else "Unknown"
        elif 'what' in question.lower() or 'which' in question.lower():
            # Answer might be a statement or fact
            if statements:
                # Pick the first statement that is likely true
                computed_answer = statements[0][1]
            else:
                computed_answer = "Yes" if posterior > 0.5 else "No"
        else:
            computed_answer = "Yes" if posterior > 0.5 else "No"

        # Step 9: Calculate confidence from agreement of multiple methods
        scores = []
        if posterior > 0.5:
            scores.append(0.8)
        else:
            scores.append(0.2)
        if not paradox_detected:
            scores.append(0.7)
        else:
            scores.append(0.3)
        if world_count == 1:
            scores.append(0.9)
        else:
            scores.append(0.5)

        confidence = confidence_from_agreement(scores)
        if confidence is None:
            confidence = 0.5

        return {
            "answer": computed_answer,
            "confidence": confidence,
            "energy": energy,
            "paradox": paradox_detected,
            "worlds": world_count,
            "beliefs": belief_tracking,
            "reasoning": f"Thermodynamic analysis: energy={energy:.2f}, worlds={world_count}, paradox={paradox_detected}"
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        results = []
        
        for c in candidates:
            # Primary: check if computed answer appears in candidate
            if computed_answer.lower() in c.lower():
                score = 1.0
            else:
                # Fallback: NCD similarity
                ncd_val = self._ncd(computed_answer, c)
                score = 1.0 / (1.0 + ncd_val)
            results.append({
                "candidate": c,
                "raw_score": score,
                "confidence": reasoning_result["confidence"]
            })
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores using confidence and energy."""
        calibrated = []
        for item in scored:
            raw = item["raw_score"]
            conf = item["confidence"]
            # Thermodynamic calibration: lower energy -> higher confidence weighting
            # We don't have energy here, but we can use confidence
            calibrated_score = raw * conf
            calibrated.append({
                "candidate": item["candidate"],
                "score": calibrated_score,
                "raw_score": raw,
                "confidence": conf
            })
        return calibrated

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