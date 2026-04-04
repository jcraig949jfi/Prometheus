import re
import zlib
from typing import Dict, List, Any, Tuple

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
    """Decision theory x SAT/Constraint solving - liar_detection"""

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
        """Extract agents, statements, truth policies, and the question."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        agents = []
        statements = []
        policies = {}  # agent -> policy (e.g., "always lies", "alternates")
        question = lines[-1] if lines else ""

        # Pattern to find agent declarations
        agent_pattern = re.compile(
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:always tells the truth|always lies|alternates|says)',
            re.IGNORECASE
        )
        # Pattern to find quoted statements
        statement_pattern = re.compile(r'"([^"]+)"')

        for line in lines:
            # Find agents
            agent_matches = agent_pattern.findall(line)
            for agent in agent_matches:
                if agent not in agents:
                    agents.append(agent)
                # Determine policy
                if 'always tells the truth' in line.lower():
                    policies[agent] = 'truth'
                elif 'always lies' in line.lower():
                    policies[agent] = 'lie'
                elif 'alternates' in line.lower():
                    policies[agent] = 'alternate'
                elif 'says' in line.lower() and agent in line:
                    # Default if not explicitly stated
                    if agent not in policies:
                        policies[agent] = 'unknown'

            # Find statements
            statement_matches = statement_pattern.findall(line)
            for stmt in statement_matches:
                if stmt not in statements:
                    statements.append(stmt)

        # Associate statements with agents (simple proximity)
        agent_statements = {}
        for agent in agents:
            agent_statements[agent] = []
            for line in lines:
                if agent in line:
                    stmts = statement_pattern.findall(line)
                    for stmt in stmts:
                        if stmt not in agent_statements[agent]:
                            agent_statements[agent].append(stmt)

        return {
            "agents": agents,
            "statements": statements,
            "policies": policies,
            "agent_statements": agent_statements,
            "question": question,
            "raw_lines": lines
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use decision theory and logical constraints to resolve the puzzle."""
        agents = structure["agents"]
        policies = structure["policies"]
        agent_statements = structure["agent_statements"]
        question = structure["question"]

        # Decision theory: model agents as rational players with fixed strategies (truth policies)
        # Their statements are moves in a game of information transmission.
        # We compute the equilibrium of beliefs (what must be true) given their strategies.

        # Step 1: Encode as SAT variables
        # Each statement gets a boolean variable (True = statement is factually true)
        stmt_vars = {}
        for i, stmt in enumerate(structure["statements"]):
            stmt_vars[stmt] = i + 1  # SAT variables start at 1

        # Step 2: Build constraints from agent policies
        clauses = []
        for agent, policy in policies.items():
            for stmt in agent_statements.get(agent, []):
                var = stmt_vars[stmt]
                if policy == 'truth':
                    # If agent tells truth, statement is true
                    clauses.append([var])
                elif policy == 'lie':
                    # If agent lies, statement is false
                    clauses.append([-var])
                elif policy == 'alternate':
                    # Alternating: we need context. For simplicity, treat as unknown.
                    # We'll use a Bayesian update later.
                    pass

        # Use T1 primitive: solve_sat to check consistency
        sat_assignment = solve_sat(clauses, len(stmt_vars))
        if sat_assignment is None:
            # Contradiction detected
            paradox_result = detect_paradox(clauses)
            if paradox_result is not None:
                # Use amino acid to confirm paradox
                is_paradox = paradox_result.get("is_paradox", False)
                if is_paradox:
                    # If paradoxical, no consistent truth assignment
                    return {
                        "answer": "No consistent solution",
                        "confidence": 0.9,
                        "reasoning": "Statements form a logical paradox"
                    }

        # Step 3: Use Bayesian update to handle uncertainty (decision theory: beliefs under partial info)
        # Prior: uniform over possible worlds (each statement equally likely true/false)
        n_statements = len(structure["statements"])
        prior = 0.5
        # Likelihood: given agent's policy, probability of observing their statements
        # For truth-teller: P(stmt | truth) = 1 if stmt true, 0 if false
        # For liar: P(stmt | lie) = 0 if stmt true, 1 if false
        # We'll compute a simple aggregated belief score
        belief_scores = {}
        for stmt in structure["statements"]:
            # Start with prior
            belief = prior
            for agent, policy in policies.items():
                if stmt in agent_statements.get(agent, []):
                    if policy == 'truth':
                        likelihood = 1.0 if sat_assignment and sat_assignment.get(stmt_vars[stmt], False) else 0.0
                    elif policy == 'lie':
                        likelihood = 0.0 if sat_assignment and sat_assignment.get(stmt_vars[stmt], False) else 1.0
                    else:
                        likelihood = 0.5  # unknown
                    # Update belief using T1 primitive
                    new_belief = bayesian_update(belief, likelihood)
                    if new_belief is not None:
                        belief = new_belief
            belief_scores[stmt] = belief

        # Step 4: Determine which statement is the answer to the question
        # The question often asks "What is true?" or "Who is the liar?"
        answer = None
        reasoning = ""

        # Look for keywords in question
        if "true" in question.lower():
            # Find the statement with highest belief score
            if belief_scores:
                best_stmt = max(belief_scores.items(), key=lambda x: x[1])
                answer = best_stmt[0]
                reasoning = f"Statement '{answer}' has highest posterior belief ({best_stmt[1]:.2f})"
        elif "liar" in question.lower() or "who lies" in question.lower():
            # Find agent most likely lying
            agent_truth_scores = {}
            for agent, policy in policies.items():
                if policy == 'lie':
                    # If explicitly marked liar, that's the answer
                    answer = agent
                    reasoning = f"Agent {agent} is explicitly stated to always lie"
                    break
                else:
                    # Estimate truthfulness from statements
                    scores = []
                    for stmt in agent_statements.get(agent, []):
                        if stmt in belief_scores:
                            scores.append(belief_scores[stmt])
                    if scores:
                        # Use T1 primitive: confidence_from_agreement
                        conf = confidence_from_agreement(scores)
                        agent_truth_scores[agent] = conf
            if not answer and agent_truth_scores:
                # Agent with lowest confidence (most inconsistent with beliefs) is likely liar
                worst_agent = min(agent_truth_scores.items(), key=lambda x: x[1])
                answer = worst_agent[0]
                reasoning = f"Agent {answer} has lowest consistency score ({worst_agent[1]:.2f})"
        elif "truth" in question.lower() or "who tells the truth" in question.lower():
            # Similar to liar detection but reversed
            for agent, policy in policies.items():
                if policy == 'truth':
                    answer = agent
                    reasoning = f"Agent {agent} is explicitly stated to always tell truth"
                    break

        # Fallback: if no specific answer found, use constraint solving
        if answer is None:
            # Use amino acid: solve_first to find a consistent assignment
            variables = list(stmt_vars.keys())
            domains = {var: [True, False] for var in variables}
            # Constraints: for each agent with known policy
            constraints = []
            for agent, policy in policies.items():
                for stmt in agent_statements.get(agent, []):
                    if policy == 'truth':
                        constraints.append(([stmt], lambda s: s[0] == True))
                    elif policy == 'lie':
                        constraints.append(([stmt], lambda s: s[0] == False))
            if constraints:
                solution = solve_first(variables, domains, constraints)
                if solution:
                    # Pick the first true statement as answer
                    for stmt, val in solution.items():
                        if val:
                            answer = stmt
                            reasoning = "First consistent solution yields true statement"
                            break

        # Final fallback: use entropy of belief distribution
        if answer is None and belief_scores:
            # Use T1 primitive: entropy
            probs = list(belief_scores.values())
            ent = entropy(probs)
            # Low entropy means one statement is clearly true/false
            if ent < 0.5:
                # Find statement with belief farthest from 0.5
                best_stmt = max(belief_scores.items(), key=lambda x: abs(x[1] - 0.5))
                answer = best_stmt[0]
                reasoning = f"Low entropy ({ent:.2f}) suggests '{answer}' is decisive"
            else:
                # High entropy: ambiguous
                answer = "Ambiguous"
                reasoning = f"High entropy ({ent:.2f}): no clear answer"

        if answer is None:
            answer = "Cannot determine"
            reasoning = "Insufficient information"

        # Compute confidence using agreement among methods
        confidence_sources = []
        if sat_assignment:
            # Consistency gives confidence
            confidence_sources.append(0.8)
        if belief_scores:
            # Belief strength gives confidence
            max_belief = max(belief_scores.values()) if belief_scores else 0
            confidence_sources.append(max_belief)
        # Use T1 primitive: confidence_from_agreement
        confidence = confidence_from_agreement(confidence_sources) if confidence_sources else 0.5

        return {
            "answer": str(answer),
            "confidence": float(confidence),
            "reasoning": reasoning
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        results = []
        for c in candidates:
            # Primary: check if computed answer appears in candidate text
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
        """Calibrate scores using reasoning confidence."""
        confidence = 0.7  # Default if not passed (in real use, would come from reasoning_result)
        for item in scored:
            # Adjust score by confidence: high confidence strengthens good matches
            item["score"] = item["raw_score"] * confidence + (1 - confidence) * 0.5
        return scored

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