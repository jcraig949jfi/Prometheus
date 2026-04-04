import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import (
    confidence_from_agreement,
    entropy,
    modus_ponens,
    track_beliefs,
    solve_constraints,
    information_sufficiency
)
from forge.amino_acids.pysat_acids import detect_paradox, check_entailment
from forge.amino_acids.constraint_acids import is_uniquely_solvable


class ReasoningTool:
    """Control theory x SAT/Constraint solving - liar_detection"""

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
        truth_policies = {}  # agent -> policy (e.g., "always lies", "always tells truth")
        question = lines[-1] if lines else ""

        # Extract agent names (capitalized words that appear before colon or as subjects)
        for line in lines:
            # Look for patterns like "Alice says: ..." or "Bob (always lies) ..."
            agent_match = re.search(r'([A-Z][a-z]+)(?:\s+says|:|\(|\))', line)
            if agent_match:
                agent = agent_match.group(1)
                if agent not in agents:
                    agents.append(agent)

            # Extract truth-telling policies
            if "always lies" in line.lower() or "liar" in line.lower():
                for a in agents:
                    if a in line:
                        truth_policies[a] = "liar"
            elif "always tells the truth" in line.lower() or "truth-teller" in line.lower():
                for a in agents:
                    if a in line:
                        truth_policies[a] = "truth"

            # Extract statements (quoted or after "says")
            if "says" in line.lower():
                parts = line.split('says', 1)
                if len(parts) > 1:
                    statement = parts[1].strip(' "\'')
                    if statement:
                        statements.append(statement)

        # If no explicit policies, infer from context
        for agent in agents:
            if agent not in truth_policies:
                truth_policies[agent] = "unknown"

        return {
            "agents": agents,
            "statements": statements,
            "policies": truth_policies,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply control-theoretic stability analysis to resolve liar puzzles."""
        agents = structure["agents"]
        policies = structure["policies"]
        question = structure["question"]
        raw = structure["raw"]

        # Control theory scaffold: treat truth values as system states,
        # liar/truth-teller policies as feedback controllers with fixed gain.
        # A truth-teller has gain +1 (preserves truth), liar has gain -1 (inverts).
        # The puzzle is stable if there exists a consistent assignment of
        # underlying facts that satisfies all controller equations.

        # Step 1: Encode as SAT using amino acid
        clauses = []
        var_map = {}  # proposition -> SAT variable index
        next_var = 1

        # Create variables for each atomic fact mentioned
        facts = set()
        for stmt in structure["statements"]:
            # Simple extraction: treat each statement as atomic proposition
            facts.add(stmt)
        for f in facts:
            var_map[f] = next_var
            next_var += 1

        # Encode each agent's statement with their policy
        for agent, policy in policies.items():
            # Find what this agent said
            agent_stmt = None
            for line in raw.split('.'):
                if agent.lower() in line.lower() and "says" in line.lower():
                    parts = line.split('says', 1)
                    if len(parts) > 1:
                        agent_stmt = parts[1].strip(' "\'')
                        break

            if agent_stmt and agent_stmt in var_map:
                stmt_var = var_map[agent_stmt]
                if policy == "truth":
                    # Truth-teller: statement ⇔ fact
                    # Encode as (agent_stmt ≡ fact) which is (stmt_var ↔ fact_var)
                    # For now treat as literal truth of the statement
                    clauses.append([stmt_var])  # Truth-teller says true statement
                elif policy == "liar":
                    # Liar: statement ⇔ ¬fact
                    clauses.append([-stmt_var])  # Liar says false statement

        # Use SAT amino acid to check consistency
        sat_result = detect_paradox(clauses)
        if sat_result is None:
            consistency = "unknown"
        else:
            consistency = "consistent" if not sat_result else "paradox"

        # Step 2: Use constraint solving to find possible truth assignments
        # Map to CSP: each fact is a boolean variable
        variables = list(facts)
        domains = {v: [True, False] for v in variables}

        constraints = []
        for agent, policy in policies.items():
            agent_stmt = None
            for line in raw.split('.'):
                if agent.lower() in line.lower() and "says" in line.lower():
                    parts = line.split('says', 1)
                    if len(parts) > 1:
                        agent_stmt = parts[1].strip(' "\'')
                        break

            if agent_stmt and agent_stmt in variables:
                if policy == "truth":
                    # Truth-teller constraint: statement must be True
                    constraints.append(([agent_stmt], lambda vals: vals[0] is True))
                elif policy == "liar":
                    # Liar constraint: statement must be False
                    constraints.append(([agent_stmt], lambda vals: vals[0] is False))

        # Use constraint amino acid to check uniqueness
        unique = is_uniquely_solvable(variables, domains, constraints)
        if unique is None:
            uniqueness = "unknown"
        else:
            uniqueness = "unique" if unique else "multiple"

        # Step 3: Use T1 primitives for additional reasoning

        # Compute entropy of policy distribution (control-theoretic measure of uncertainty)
        policy_counts = {"truth": 0, "liar": 0, "unknown": 0}
        for p in policies.values():
            policy_counts[p] += 1
        total = len(policies)
        if total > 0:
            probs = [c/total for c in policy_counts.values() if c > 0]
            policy_entropy = entropy(probs) if probs else 0.0
        else:
            policy_entropy = 0.0

        # Use modus ponens to derive implications
        premises = []
        derived_facts = set()
        for stmt in structure["statements"]:
            # Simple implication: if statement is true, it's a fact
            premises.append(("statement_true", stmt))
        if premises:
            # Start with known facts from policies
            initial_facts = set()
            for agent, policy in policies.items():
                if policy == "truth":
                    # Find what truth-teller said
                    for line in raw.split('.'):
                        if agent.lower() in line.lower() and "says" in line.lower():
                            parts = line.split('says', 1)
                            if len(parts) > 1:
                                stmt = parts[1].strip(' "\'')
                                initial_facts.add(stmt)
                                break

            derived = modus_ponens(premises, initial_facts)
            if derived:
                derived_facts = derived

        # Track beliefs of agents (simple theory of mind)
        observations = []
        for agent in agents:
            # Each agent observes their own statement's truth value based on policy
            for line in raw.split('.'):
                if agent.lower() in line.lower() and "says" in line.lower():
                    parts = line.split('says', 1)
                    if len(parts) > 1:
                        stmt = parts[1].strip(' "\'')
                        # Truth-teller believes true statement, liar believes false
                        if policies.get(agent) == "truth":
                            observations.append((agent, stmt, True))
                        elif policies.get(agent) == "liar":
                            observations.append((agent, stmt, False))
                        break

        belief_state = track_beliefs(agents, observations)

        # Check information sufficiency
        n_unknowns = len([p for p in policies.values() if p == "unknown"])
        n_constraints = len(constraints)
        info_status = information_sufficiency(n_unknowns, n_constraints)

        # Compute confidence from agreement among derived facts
        if derived_facts:
            # Convert to scores (1.0 for each derived fact)
            scores = [1.0] * len(derived_facts)
            confidence = confidence_from_agreement(scores)
        else:
            confidence = 0.5

        # Determine answer based on control-theoretic stability:
        # If system is consistent and uniquely solvable, we can identify the actual state.
        # The answer is typically which agent has which policy or what is actually true.
        computed_answer = ""
        if consistency == "consistent" and uniqueness == "unique":
            # System is well-posed and stable
            if "who" in question.lower() and "liar" in question.lower():
                # Find the liar(s)
                liars = [a for a, p in policies.items() if p == "liar"]
                if liars:
                    computed_answer = liars[0] if len(liars) == 1 else " and ".join(liars)
            elif "what" in question.lower() and "true" in question.lower():
                # Report a derived fact
                if derived_facts:
                    computed_answer = list(derived_facts)[0]
                else:
                    computed_answer = "Cannot determine"
            else:
                # Default: report consistency result
                computed_answer = "Consistent scenario"
        elif consistency == "paradox":
            computed_answer = "Contradiction detected"
        else:
            computed_answer = "Ambiguous"

        # If no specific answer extracted, use a fallback
        if not computed_answer:
            computed_answer = "Cannot determine"

        return {
            "answer": computed_answer,
            "confidence": min(0.9, confidence * (1.0 - policy_entropy)),  # Control-theoretic: lower entropy → higher confidence
            "reasoning": f"Control analysis: consistency={consistency}, uniqueness={uniqueness}, info={info_status}, entropy={policy_entropy:.3f}",
            "derived_facts": list(derived_facts),
            "belief_state": belief_state
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        results = []

        for candidate in candidates:
            # Primary: check if computed answer appears in candidate
            if computed_answer.lower() in candidate.lower():
                score = 1.0
            else:
                # Fallback: NCD similarity to reasoning text
                score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
            results.append({
                "candidate": candidate,
                "score": score,
                "raw_score": score
            })

        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores using confidence from agreement."""
        raw_scores = [item["raw_score"] for item in scored]
        if raw_scores:
            confidence = confidence_from_agreement(raw_scores)
            # Adjust scores toward confidence
            for item in scored:
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