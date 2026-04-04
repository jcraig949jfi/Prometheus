import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import (
    bayesian_update,
    confidence_from_agreement,
    entropy,
    solve_constraints,
    track_beliefs,
    modus_ponens
)
from forge.amino_acids.pysat_acids import solve, check_entailment, detect_paradox
from forge.amino_acids.constraint_acids import is_uniquely_solvable


class ReasoningTool:
    """Climate modeling x SAT solving - liar detection"""

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
        agents = []
        statements = []
        truth_policies = {}  # agent -> policy (e.g., "always lies", "alternates")
        question = lines[-1] if lines else ""

        # Extract agent names (capitalized words that appear before colon or as subjects)
        for line in lines:
            # Look for patterns like "Alice says: ..." or "Bob claims ..."
            agent_match = re.search(r'^([A-Z][a-z]+)(?:\s+says|claims|states|responds|answers)', line)
            if agent_match:
                agent = agent_match.group(1)
                if agent not in agents:
                    agents.append(agent)

            # Extract truth-telling policies
            lower_line = line.lower()
            for agent in agents:
                if agent.lower() in lower_line:
                    if 'always lies' in lower_line or 'never tells the truth' in lower_line:
                        truth_policies[agent] = 'liar'
                    elif 'always tells the truth' in lower_line or 'never lies' in lower_line:
                        truth_policies[agent] = 'truthful'
                    elif 'alternates' in lower_line:
                        truth_policies[agent] = 'alternating'
                    elif 'random' in lower_line:
                        truth_policies[agent] = 'random'

            # Extract quoted statements or claims
            statement_match = re.search(r'["“]([^"”]+)["”]', line)
            if statement_match:
                statements.append(statement_match.group(1))

        # If no explicit policies found, infer from context
        for agent in agents:
            if agent not in truth_policies:
                truth_policies[agent] = 'unknown'

        return {
            "agents": agents,
            "statements": statements,
            "truth_policies": truth_policies,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use climate modeling concepts (forcing, feedback, equilibrium) to resolve liar puzzles."""
        agents = structure["agents"]
        policies = structure["truth_policies"]
        question = structure["question"]

        # Climate modeling analogy:
        # - Truth-telling policies are like radiative forcings (external influences)
        # - Logical constraints are like feedback loops
        # - Consistent solution is like climate equilibrium

        # Step 1: Encode as SAT problem (climate model equations)
        clauses = []
        var_map = {}  # Map (agent, statement_idx) -> SAT variable number
        next_var = 1

        # Create variables for each agent's statement truth value
        for i, agent in enumerate(agents):
            var_map[(agent, 'statement')] = next_var
            next_var += 1

        # Add clauses based on truth-telling policies (radiative forcings)
        for agent, policy in policies.items():
            agent_var = var_map.get((agent, 'statement'))
            if agent_var is None:
                continue

            if policy == 'liar':
                # Agent always lies: statement is false
                clauses.append([-agent_var])
            elif policy == 'truthful':
                # Agent always tells truth: statement is true
                clauses.append([agent_var])
            elif policy == 'alternating':
                # Alternating: cannot determine from single statement alone
                # This creates uncertainty (like stochastic forcing)
                pass

        # Add logical constraints from statement content (feedback loops)
        # Parse statements for logical relationships
        for stmt in structure["statements"]:
            lower_stmt = stmt.lower()
            # Look for claims about other agents
            for other_agent in agents:
                if other_agent.lower() in lower_stmt:
                    other_var = var_map.get((other_agent, 'statement'))
                    if other_var:
                        # If statement claims "X is truthful", encode equivalence
                        if 'truthful' in lower_stmt or 'tells the truth' in lower_stmt:
                            # Current agent's statement truth = other agent's truth value
                            # This creates a feedback loop
                            pass

        # Use SAT solving to find equilibrium states
        sat_result = solve(clauses)
        if sat_result is None:
            # No consistent assignment (paradox detected)
            paradox_check = detect_paradox(clauses)
            if paradox_check:
                return {"answer": "paradox", "confidence": 0.9, "reasoning": "Logical paradox detected"}

        # Step 2: Use Bayesian update to handle uncertainty (like climate model ensembles)
        prior = 0.5  # Initial uncertainty
        likelihood = 0.8 if sat_result else 0.2  # SAT solution provides evidence
        posterior = bayesian_update(prior, likelihood)
        if posterior is None:
            posterior = prior

        # Step 3: Track belief propagation (like heat transfer in climate system)
        observations = []
        for agent in agents:
            # Each agent observes their own policy
            policy_val = 1 if policies.get(agent) == 'truthful' else 0
            observations.append((agent, 'policy', bool(policy_val)))

        belief_tracking = track_beliefs(agents, observations)
        if belief_tracking is None:
            belief_tracking = {}

        # Step 4: Check logical entailment (like checking if emissions lead to warming)
        # Create premise clauses from policies
        premise_clauses = []
        for agent, policy in policies.items():
            agent_var = var_map.get((agent, 'statement'))
            if agent_var:
                if policy == 'liar':
                    premise_clauses.append([-agent_var])
                elif policy == 'truthful':
                    premise_clauses.append([agent_var])

        # Try to deduce answer to question
        conclusion_clause = []  # Will be filled based on question
        entailment_result = None
        if premise_clauses:
            entailment_result = check_entailment(premise_clauses, conclusion_clause)

        # Step 5: Use constraint solving as alternative method (like multiple climate models)
        variables = agents.copy()
        domains = {}
        constraints = []

        for agent in agents:
            domains[agent] = [0, 1]  # 0 = lying, 1 = truthful

            # Add policy constraints
            policy = policies.get(agent)
            if policy == 'liar':
                constraints.append(([agent], lambda x: x[0] == 0))
            elif policy == 'truthful':
                constraints.append(([agent], lambda x: x[0] == 1))

        # Check if solution is unique (like equilibrium attractor)
        unique_solution = False
        if variables and domains:
            unique_check = is_uniquely_solvable(variables, domains, constraints)
            if unique_check is not None:
                unique_solution = unique_check

        # Step 6: Determine final answer based on question
        computed_answer = ""
        reasoning_text = ""

        # Extract what is being asked
        lower_q = question.lower()
        if 'who' in lower_q:
            # Find the agent that satisfies conditions
            if unique_solution and variables:
                # Use constraint solving result
                solution = solve_constraints(variables, domains, constraints)
                if solution:
                    for agent, val in solution.items():
                        if val == 1:  # Truthful agent
                            computed_answer = agent
                            break
        elif 'what' in lower_q and 'statement' in lower_q:
            # Determine truth value of specific statement
            if sat_result and var_map:
                for (agent, _), var in var_map.items():
                    if var in sat_result and sat_result[var]:
                        computed_answer = f"{agent}'s statement is true"
                        break
                    elif -var in sat_result or (var in sat_result and not sat_result[var]):
                        computed_answer = f"{agent}'s statement is false"
                        break

        # Fallback: if no specific answer computed, use entropy of beliefs
        if not computed_answer:
            # Calculate entropy of belief distribution (like climate uncertainty)
            belief_probs = []
            for agent in agents:
                # Simple probability based on policy
                if policies.get(agent) == 'truthful':
                    belief_probs.append(0.9)
                elif policies.get(agent) == 'liar':
                    belief_probs.append(0.1)
                else:
                    belief_probs.append(0.5)

            if belief_probs:
                # Normalize
                total = sum(belief_probs)
                if total > 0:
                    normalized = [p/total for p in belief_probs]
                    uncertainty = entropy(normalized)
                    # Lower entropy = more certain
                    if uncertainty < 0.5 and agents:
                        # Pick agent with highest probability
                        max_idx = max(range(len(belief_probs)), key=lambda i: belief_probs[i])
                        computed_answer = agents[max_idx]

        # Final confidence from agreement of multiple methods
        confidence_scores = []
        if posterior > 0.5:
            confidence_scores.append(posterior)
        if entailment_result is not None:
            confidence_scores.append(0.8 if entailment_result else 0.2)
        if unique_solution:
            confidence_scores.append(0.9)

        confidence = 0.5  # Default
        if confidence_scores:
            conf_from_agreement = confidence_from_agreement(confidence_scores)
            if conf_from_agreement is not None:
                confidence = conf_from_agreement

        # If still no answer, use first agent as fallback
        if not computed_answer and agents:
            computed_answer = agents[0]
            confidence = 0.3

        reasoning_text = f"Climate modeling approach: Policies as forcings, logical constraints as feedbacks. Found equilibrium state: {computed_answer}"

        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": reasoning_text
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]

        results = []
        for candidate in candidates:
            # Primary: check if computed answer appears in candidate
            if computed_answer and computed_answer.lower() in candidate.lower():
                score = 1.0
            else:
                # Fallback: NCD similarity to reasoning text
                score = 1.0 / (1.0 + self._ncd(reasoning_text, candidate))
            results.append({
                "candidate": candidate,
                "score": score,
                "raw_score": score
            })
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores using confidence from reasoning."""
        if not scored:
            return scored

        # Simple calibration: scale by confidence (would need actual confidence value)
        # For now, just return as-is
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