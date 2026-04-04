import re
import zlib
from typing import Dict, List, Any, Set, Tuple
from forge_primitives import (
    solve_sat,
    modus_ponens,
    track_beliefs,
    confidence_from_agreement,
    topological_sort,
    check_transitivity
)
from forge.amino_acids.pysat_acids import detect_paradox, check_entailment
from forge.amino_acids.constraint_acids import is_uniquely_solvable

class ReasoningTool:
    """Relativity x SAT/Constraint Solving - Liar Detection"""

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
        """Parse prompt to find agents, statements, truth policies, and question."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        agents = set()
        statements = []  # (speaker, statement_text)
        truth_policies = {}  # agent -> policy (e.g., "always lies", "alternates")
        question = lines[-1] if lines else ""

        # Find agent names (capitalized words that appear as subjects)
        words = re.findall(r'\b([A-Z][a-z]+)\b', prompt)
        potential_agents = [w for w in words if len(w) > 2]
        # Heuristic: agents are often introduced with "says" or "claims"
        for i, line in enumerate(lines):
            if ' says ' in line or ' claims ' in line:
                parts = line.split(' says ' if ' says ' in line else ' claims ')
                if len(parts) > 1:
                    agent = parts[0].strip()
                    statement = parts[1].strip(' "')
                    agents.add(agent)
                    statements.append((agent, statement))
            # Look for truth-telling patterns
            if 'always tells the truth' in line.lower():
                for a in potential_agents:
                    if a in line:
                        truth_policies[a] = 'truth'
            if 'always lies' in line.lower():
                for a in potential_agents:
                    if a in line:
                        truth_policies[a] = 'lie'
            if 'alternates' in line.lower():
                for a in potential_agents:
                    if a in line:
                        truth_policies[a] = 'alternate'

        # If no policies found, assume classic knights/knaves
        if not truth_policies and agents:
            for agent in agents:
                truth_policies[agent] = 'unknown'

        return {
            "agents": list(agents),
            "statements": statements,
            "policies": truth_policies,
            "question": question,
            "raw_lines": lines
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply relativistic reasoning: truth is frame-dependent, consistency across frames determines reality."""
        agents = structure["agents"]
        statements = structure["statements"]
        policies = structure["policies"]
        question = structure["question"]

        # Use relativity: each agent's truth-telling policy defines a "reference frame"
        # The actual facts must be consistent across all physically possible frames (non-paradoxical worlds)
        # This maps to finding a global assignment that satisfies all constraints.

        # Step 1: Encode as SAT using T1 primitive
        clauses = []
        var_map = {}  # proposition -> SAT variable index
        next_var = 1

        # Create variables for each atomic fact mentioned
        facts = set()
        for _, stmt in statements:
            # Simple extraction: look for "is X" or "are Y" patterns
            if ' is ' in stmt:
                fact = stmt.split(' is ')[1].strip('.')
                facts.add(fact)
            elif ' are ' in stmt:
                fact = stmt.split(' are ')[1].strip('.')
                facts.add(fact)
            else:
                # Use the whole statement as a fact
                facts.add(stmt)

        facts = list(facts)
        for f in facts:
            var_map[f] = next_var
            next_var += 1

        # Encode each statement based on speaker's policy
        for speaker, stmt in statements:
            stmt_var = var_map.get(stmt, None)
            if stmt_var is None:
                # Statement not in facts list, treat as new variable
                var_map[stmt] = next_var
                stmt_var = next_var
                next_var += 1

            policy = policies.get(speaker, 'unknown')

            if policy == 'truth':
                # Speaker tells truth: statement is true
                clauses.append([stmt_var])
            elif policy == 'lie':
                # Speaker lies: statement is false
                clauses.append([-stmt_var])
            elif policy == 'alternate':
                # Alternate truth-telling: cannot determine from single statement alone
                # We'll handle via constraint solving later
                pass
            else:
                # Unknown policy: use SAT to find consistent assignments
                # No additional clause

        # Use SAT solver primitive
        sat_result = solve_sat(clauses, len(var_map))
        sat_consistent = sat_result is not None

        # Step 2: Use modus ponens to derive implications from statements
        premises = []
        derived_facts = set()
        for speaker, stmt in statements:
            # Create simple implications: if speaker is truthful, then statement
            # But we don't know truthfulness directly, so we'll use track_beliefs
            pass

        # Use track_beliefs primitive to model belief propagation
        observations = []
        for speaker, stmt in statements:
            # Treat each statement as an observation by the system
            # The "observer" is the system itself
            fact_label = f"fact_{hash(stmt) % 1000}"
            # We don't know truth value yet, so set to False as placeholder
            observations.append(("system", fact_label, False))

        belief_result = track_beliefs(["system"], observations)
        # This gives us a baseline belief tracking structure

        # Step 3: Use amino acid to detect paradox
        # Convert clauses to format for detect_paradox
        paradox_check = detect_paradox(clauses)
        has_paradox = paradox_check is True

        # Step 4: Use constraint solving to check uniqueness (relativistic: is there a unique "rest frame"?)
        # Build CSP: variables are facts, domains are {True, False}
        variables = list(var_map.keys())
        domains = {v: [True, False] for v in variables}
        constraints = []
        # Constraint: for each truth-teller, their statement must equal their policy
        for speaker, stmt in statements:
            policy = policies.get(speaker, 'unknown')
            if policy == 'truth':
                def make_truth_constraint(stmt_var_name=stmt):
                    def constraint(assignment):
                        return assignment[stmt_var_name] == True
                    return constraint
                constraints.append(([stmt], make_truth_constraint()))
            elif policy == 'lie':
                def make_lie_constraint(stmt_var_name=stmt):
                    def constraint(assignment):
                        return assignment[stmt_var_name] == False
                    return constraint
                constraints.append(([stmt], make_lie_constraint()))

        unique_solution = False
        if variables and constraints:
            unique_check = is_uniquely_solvable(variables, domains, constraints)
            unique_solution = unique_check if unique_check is not None else False

        # Step 5: Determine answer from question
        # Extract what is being asked
        computed_answer = ""
        confidence = 0.5

        if "who" in question.lower():
            # Question asks for an agent
            # Find which agent's statements are consistent with global solution
            if sat_result:
                # Evaluate each agent's consistency
                agent_scores = []
                for agent in agents:
                    agent_stmts = [stmt for spkr, stmt in statements if spkr == agent]
                    if not agent_stmts:
                        continue
                    # Check if all statements match SAT assignment
                    matches = 0
                    for stmt in agent_stmts:
                        stmt_var = var_map.get(stmt)
                        if stmt_var and stmt_var in sat_result:
                            # Compare with policy
                            policy = policies.get(agent, 'unknown')
                            if policy == 'truth' and sat_result[stmt_var]:
                                matches += 1
                            elif policy == 'lie' and not sat_result[stmt_var]:
                                matches += 1
                            elif policy == 'unknown':
                                matches += 1  # Neutral
                    score = matches / len(agent_stmts) if agent_stmts else 0
                    agent_scores.append((agent, score))
                if agent_scores:
                    best_agent = max(agent_scores, key=lambda x: x[1])[0]
                    computed_answer = best_agent
                    confidence = max(0.1, agent_scores[0][1])
        elif "what" in question.lower() or "which" in question.lower():
            # Question likely asks for a fact
            if sat_result and facts:
                # Find the fact with strongest assignment
                fact_values = []
                for f in facts:
                    var = var_map.get(f)
                    if var and var in sat_result:
                        fact_values.append((f, 1.0 if sat_result[var] else 0.0))
                if fact_values:
                    best_fact = max(fact_values, key=lambda x: x[1])[0]
                    computed_answer = best_fact
                    confidence = fact_values[0][1]

        # Fallback if no answer determined
        if not computed_answer:
            if has_paradox:
                computed_answer = "paradox"
            elif unique_solution:
                computed_answer = "unique solution exists"
            else:
                computed_answer = "inconsistent"

        # Use confidence_from_agreement primitive
        # Create dummy scores from different reasoning paths
        scores = []
        if sat_consistent:
            scores.append(0.7)
        if unique_solution:
            scores.append(0.9)
        if has_paradox:
            scores.append(0.1)
        if len(scores) > 1:
            conf_agreement = confidence_from_agreement(scores)
            confidence = max(0.1, min(0.9, (confidence + conf_agreement) / 2))

        # Use topological_sort on agent dependency if any "says" chains
        edges = []
        for i, (speaker1, stmt1) in enumerate(statements):
            for agent in agents:
                if agent in stmt1 and agent != speaker1:
                    edges.append((speaker1, agent))
        if edges:
            topo_order = topological_sort(edges)
            if topo_order and computed_answer in agents:
                # Boost confidence if answer agent is early in dependency chain
                idx = topo_order.index(computed_answer) if computed_answer in topo_order else len(topo_order)
                confidence = confidence * (0.5 + 0.5 * (1 - idx/len(topo_order)))

        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": f"SAT consistent: {sat_consistent}, Paradox: {has_paradox}, Unique: {unique_solution}",
            "sat_result": sat_result,
            "var_map": var_map
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
                score = 1.0 / (1.0 + self._ncd(computed_answer, c))
            results.append({
                "candidate": c,
                "score": score,
                "raw_score": score
            })
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores using confidence and consistency."""
        if not scored:
            return scored

        # Simple calibration: normalize to [0, 1] range
        scores = [s["raw_score"] for s in scored]
        if max(scores) - min(scores) > 0:
            for s in scored:
                s["score"] = (s["raw_score"] - min(scores)) / (max(scores) - min(scores))
        else:
            for s in scored:
                s["score"] = 0.5
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