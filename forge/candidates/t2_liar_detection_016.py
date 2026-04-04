import re
import zlib
from typing import Dict, List, Any, Set, Tuple
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
    """Immunology x SAT/Constraint solving - liar_detection"""

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

    # ========== PHASE 1: EXTRACT ==========
    def _extract(self, prompt: str) -> Dict[str, Any]:
        """Parse prompt to find agents, statements, truth policies, and question."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        agents = set()
        statements = []
        truth_policies = {}
        question = lines[-1] if lines else ""

        # Extract agent names (capitalized words that appear as subjects)
        for line in lines:
            words = re.findall(r'\b([A-Z][a-z]+)\b', line)
            for w in words:
                if w.lower() not in ['the', 'and', 'but', 'or', 'if', 'then', 'always', 'never', 'sometimes']:
                    agents.add(w)

        # Map common truth-telling patterns
        policy_keywords = {
            'always tells the truth': 'truthful',
            'always lies': 'liar',
            'alternates': 'alternating',
            'random': 'random',
            'never': 'liar',
            'only on': 'conditional'
        }

        for line in lines:
            for agent in agents:
                if agent in line:
                    for key, policy in policy_keywords.items():
                        if key in line.lower():
                            truth_policies[agent] = policy
                            break
                    # Look for statements made by agents
                    if 'says' in line.lower() or 'claims' in line.lower():
                        # Extract quoted or colon-separated statement
                        quote_match = re.search(r'["“]([^"”]+)["”]', line)
                        if quote_match:
                            stmt = quote_match.group(1)
                        else:
                            # Try to find part after 'says' or 'claims'
                            parts = re.split(r'says|claims', line, flags=re.IGNORECASE)
                            if len(parts) > 1:
                                stmt = parts[1].strip(' :"\'').split('.')[0]
                            else:
                                stmt = line
                        if stmt and len(stmt) > 3:
                            statements.append((agent, stmt))

        # Clean up agents that have no policy (might not be puzzle agents)
        agents = {a for a in agents if a in truth_policies or any(a == stmt_agent for stmt_agent, _ in statements)}

        return {
            "agents": list(agents),
            "statements": statements,
            "policies": truth_policies,
            "question": question,
            "raw_lines": lines
        }

    # ========== PHASE 2: REASON ==========
    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """
        Immunology-inspired reasoning: agents as antigens, statements as epitopes.
        Truth policies define antigenic profiles. Consistency checking is immune
        system self/non-self discrimination. The correct answer is the antigen
        (agent/statement) that survives the immune tolerance check (logical consistency).
        """
        agents = structure["agents"]
        statements = structure["statements"]
        policies = structure["policies"]
        question = structure["question"]

        # Use immunology concept: belief entropy as immune system activation level
        # Low entropy = high confidence = strong immune response (clear truth)
        # High entropy = low confidence = weak/tolerant response (ambiguity)

        # Step 1: Encode as logical constraints (antigen presentation)
        clauses, var_map = self._encode_as_sat(agents, statements, policies)

        # Step 2: Detect paradox (autoimmunity check)
        paradox_result = detect_paradox(clauses)
        if paradox_result is None:
            paradox_detected = False
        else:
            paradox_detected = paradox_result

        # Step 3: Use SAT solving to find consistent assignments (immune tolerance selection)
        sat_assignment = solve_sat(clauses, len(var_map))
        if sat_assignment is None:
            # No consistent assignment - use constraint solving as fallback
            consistent = False
            computed_answer = "No consistent solution"
            confidence = 0.1
        else:
            consistent = True
            # Step 4: Extract which statements must be true in all models (immunodominant epitopes)
            # Enumerate possibilities with constraint solving
            csp_vars, csp_domains, csp_constraints = self._encode_as_csp(agents, statements, policies)
            unique_check = is_uniquely_solvable(csp_vars, csp_domains, csp_constraints)
            if unique_check is None:
                unique = False
            else:
                unique = unique_check

            # Step 5: Determine answer based on question type
            computed_answer = self._infer_answer_from_question(
                question, agents, statements, policies, sat_assignment, var_map, unique
            )

            # Step 6: Compute confidence using immunological entropy
            # Gather probabilities from Bayesian update of agent reliability
            probs = []
            for agent in agents:
                prior = 0.5
                if policies.get(agent) == 'truthful':
                    likelihood = 0.9
                elif policies.get(agent) == 'liar':
                    likelihood = 0.1
                else:
                    likelihood = 0.5
                updated = bayesian_update(prior, likelihood)
                if updated is not None:
                    probs.append(updated)

            # Entropy of agent reliability distribution
            if probs:
                ent = entropy(probs)
                # Low entropy = high confidence (clear signal)
                confidence = max(0.0, 1.0 - ent)
            else:
                confidence = 0.5

            # Boost confidence if unique solution found
            if unique:
                confidence = min(1.0, confidence * 1.3)

            # Use confidence_from_agreement as additional signal
            if len(probs) >= 2:
                agreement_conf = confidence_from_agreement(probs)
                if agreement_conf is not None:
                    confidence = (confidence + agreement_conf) / 2

        # Step 7: Track beliefs as immune memory
        if consistent and sat_assignment:
            # Map SAT vars back to agent beliefs
            belief_obs = []
            for (agent, stmt), var_idx in var_map.items():
                if var_idx > 0 and var_idx in sat_assignment:
                    is_true = sat_assignment[var_idx]
                    belief_obs.append((agent, stmt, is_true))
            if belief_obs:
                belief_tracking = track_beliefs(agents, belief_obs)
                # Use belief consistency to adjust confidence
                if belief_tracking:
                    consistent_agents = sum(1 for ag in agents if ag in belief_tracking)
                    if consistent_agents == len(agents):
                        confidence = min(1.0, confidence * 1.1)

        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": f"Immunological consistency check: paradox_detected={paradox_detected}, unique_solution={unique if consistent else False}",
            "consistent": consistent,
            "unique": unique if consistent else False
        }

    def _encode_as_sat(self, agents, statements, policies):
        """Encode liar puzzle as SAT clauses."""
        var_map = {}
        clauses = []
        var_idx = 1

        # Create variables: statement_said_by_agent_is_true
        for agent, stmt in statements:
            var_map[(agent, stmt)] = var_idx
            var_idx += 1

        # Add constraints based on truth policies
        for agent in agents:
            policy = policies.get(agent, 'unknown')
            agent_statements = [(a, s) for (a, s) in statements if a == agent]

            if policy == 'truthful':
                # All statements by this agent are true
                for (a, s) in agent_statements:
                    var = var_map[(a, s)]
                    clauses.append([var])  # var must be true
            elif policy == 'liar':
                # All statements by this agent are false
                for (a, s) in agent_statements:
                    var = var_map[(a, s)]
                    clauses.append([-var])  # var must be false
            elif policy == 'alternating':
                # Alternate truth values (simplify: exactly half true if even number)
                if len(agent_statements) >= 2:
                    vars = [var_map[(a, s)] for (a, s) in agent_statements]
                    # Encode XOR between consecutive statements
                    for i in range(len(vars)-1):
                        clauses.append([vars[i], vars[i+1]])
                        clauses.append([-vars[i], -vars[i+1]])

        # Add logical consistency between statements
        # If a statement references another agent's truthfulness
        for agent, stmt in statements:
            stmt_lower = stmt.lower()
            for other_agent in agents:
                if other_agent.lower() in stmt_lower:
                    # Check for claims about truthfulness
                    if 'truth' in stmt_lower or 'lie' in stmt_lower or 'honest' in stmt_lower:
                        # This is a meta-statement about other_agent's policy
                        other_policy = policies.get(other_agent, 'unknown')
                        var = var_map[(agent, stmt)]
                        if other_policy == 'truthful':
                            # If statement says other is truthful, it must be true
                            clauses.append([var])  # Force true
                        elif other_policy == 'liar':
                            # If statement says other is liar, it must be false
                            clauses.append([-var])  # Force false

        return clauses, var_map

    def _encode_as_csp(self, agents, statements, policies):
        """Encode as CSP for uniqueness checking."""
        variables = []
        domains = {}
        constraints = []

        for agent, stmt in statements:
            var_name = f"{agent}_{hash(stmt) % 1000}"
            variables.append(var_name)
            domains[var_name] = [True, False]  # Statement is true or false

        # Policy constraints
        for agent in agents:
            policy = policies.get(agent, 'unknown')
            agent_vars = [v for v in variables if v.startswith(f"{agent}_")]

            if policy == 'truthful':
                for var in agent_vars:
                    constraints.append(([var], lambda x: x[0] == True))
            elif policy == 'liar':
                for var in agent_vars:
                    constraints.append(([var], lambda x: x[0] == False))

        return variables, domains, constraints

    def _infer_answer_from_question(self, question, agents, statements, policies, sat_assignment, var_map, unique):
        """Determine what the answer should be based on question phrasing."""
        q_lower = question.lower()

        # Check if asking for specific agent
        for agent in agents:
            if agent.lower() in q_lower:
                # Question mentions this agent - might be asking if they are truthful
                return agent

        # Check if asking for statement truth value
        for agent, stmt in statements:
            if any(word in q_lower for word in ['statement', 'claim', 'says']):
                if stmt.lower() in q_lower or agent.lower() in q_lower:
                    # Determine truth value from SAT assignment
                    var_idx = var_map.get((agent, stmt))
                    if var_idx and var_idx in sat_assignment:
                        truth_val = sat_assignment[var_idx]
                        return "true" if truth_val else "false"

        # Check if asking which policy
        if 'who' in q_lower and ('truth' in q_lower or 'lie' in q_lower or 'honest' in q_lower):
            # Find agent with specific policy that matches constraints
            for agent in agents:
                policy = policies.get(agent, 'unknown')
                if policy == 'truthful' and 'truth' in q_lower:
                    return agent
                elif policy == 'liar' and ('lie' in q_lower or 'liar' in q_lower):
                    return agent

        # Default: return first agent if nothing else matches
        return agents[0] if agents else "Unknown"

    # ========== PHASE 3: SCORE ==========
    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        reasoning_text = reasoning_result["reasoning"]

        results = []
        for c in candidates:
            # Primary: check if computed answer appears in candidate
            if computed_answer.lower() in c.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity to reasoning text
                base_score = 1.0 / (1.0 + self._ncd(computed_answer, c))

            # Adjust by confidence
            adjusted_score = base_score * confidence
            results.append({
                "candidate": c,
                "score": adjusted_score,
                "base_score": base_score,
                "confidence": confidence
            })

        return results

    def _ncd(self, a: str, b: str) -> float:
        """Normalized Compression Distance."""
        if not a or not b:
            return 1.0
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + " " + b).encode()))
        if max(ca, cb) == 0:
            return 1.0
        return (cab - min(ca, cb)) / max(ca, cb)

    # ========== PHASE 4: CALIBRATE ==========
    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper distribution."""
        if not scored:
            return scored

        scores = [item["score"] for item in scored]
        min_s = min(scores)
        max_s = max(scores)

        if max_s - min_s < 0.001:
            # All scores nearly equal - spread them slightly
            for i, item in enumerate(scored):
                item["score"] = 0.5 + (i * 0.01)
        else:
            # Normalize to [0, 1] range
            for item in scored:
                s = item["score"]
                if max_s > min_s:
                    item["score"] = (s - min_s) / (max_s - min_s)
                else:
                    item["score"] = 0.5

        return scored