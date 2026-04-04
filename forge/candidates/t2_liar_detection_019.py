import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import (
    bayesian_update,
    entropy,
    confidence_from_agreement,
    solve_sat,
    modus_ponens,
    track_beliefs
)
from forge.amino_acids.pysat_acids import detect_paradox, check_entailment
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable


class ReasoningTool:
    """Information theory x SAT/Constraint solving - liar_detection"""

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
        """Parse prompt to extract agents, statements, truth policies, and question."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        agents = []
        statements = []
        truth_policies = {}  # agent -> policy (e.g., "always lies", "alternates")
        question = lines[-1] if lines else ""

        # Extract agent names (capitalized words, often followed by colon or quotes)
        agent_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        for line in lines:
            # Find potential agent mentions
            matches = re.findall(agent_pattern, line)
            for match in matches:
                if len(match.split()) <= 3:  # Likely a name, not a long phrase
                    if match not in agents and match.lower() not in ['always', 'never', 'sometimes', 'truth']:
                        agents.append(match)

            # Detect truth-telling policies
            lower_line = line.lower()
            for agent in agents:
                if agent in line:
                    if 'always lies' in lower_line or 'liar' in lower_line:
                        truth_policies[agent] = 'always_lies'
                    elif 'always tells the truth' in lower_line or 'truth-teller' in lower_line:
                        truth_policies[agent] = 'always_truth'
                    elif 'alternates' in lower_line:
                        truth_policies[agent] = 'alternates'
                    elif 'random' in lower_line:
                        truth_policies[agent] = 'random'

            # Extract quoted statements
            quoted = re.findall(r'\"([^\"]+)\"', line)
            statements.extend(quoted)

        # Clean agents: remove duplicates and non-agent words
        agents = list(set(agents))
        agents = [a for a in agents if a not in ['I', 'You', 'He', 'She', 'They', 'We']]

        return {
            "agents": agents,
            "statements": statements,
            "truth_policies": truth_policies,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use information-theoretic and logical reasoning to resolve liar puzzles."""
        agents = structure["agents"]
        policies = structure["truth_policies"]
        statements = structure["statements"]
        question = structure["question"]

        # Information-theoretic scaffold: treat truth value as a random variable
        # with entropy measuring uncertainty. Policies constrain the distribution.
        # We'll compute the most information-efficient consistent assignment.

        # Step 1: Encode as SAT using T1 primitive
        # Map agents to boolean variables: True = tells truth at relevant moment
        n_agents = len(agents)
        if n_agents == 0:
            # Fallback: no agents extracted, use simple text analysis
            return {"answer": "unknown", "confidence": 0.0, "reasoning": "No agents identified"}

        # Build clauses based on policies
        clauses = []
        var_map = {agent: i+1 for i, agent in enumerate(agents)}  # SAT variables start at 1

        for agent, policy in policies.items():
            idx = var_map.get(agent)
            if idx is None:
                continue
            if policy == 'always_lies':
                clauses.append([-idx])  # variable always false
            elif policy == 'always_truth':
                clauses.append([idx])   # variable always true
            elif policy == 'alternates':
                # For alternation, we need temporal context; simplify to unknown
                # We'll handle via constraint solving later
                pass

        # Use T1 primitive: solve_sat
        sat_assignment = solve_sat(clauses, n_agents)
        if sat_assignment is None:
            # Contradiction detected
            paradox_check = detect_paradox(clauses)
            if paradox_check:
                reasoning = "Policies lead to logical contradiction (paradox)."
            else:
                reasoning = "No consistent truth assignment found."
            # Use entropy to measure uncertainty
            uncertainty = entropy([0.5, 0.5])  # max entropy for binary
            return {"answer": "contradiction", "confidence": 0.7, "reasoning": reasoning, "uncertainty": uncertainty}

        # Step 2: Use amino acid for deeper logical analysis
        # Check if statements entail a specific answer to the question
        # Encode statements as implications between agent variables
        statement_clauses = []
        for stmt in statements:
            # Simple parsing: "A says B" -> if A is truthful then B's truth value matches
            # This is a simplification; real parsing would be more complex
            for agent in agents:
                if agent in stmt and ' says ' in stmt:
                    parts = stmt.split(' says ')
                    if parts[0].strip() == agent:
                        # We'll treat this as A -> (B is true) for some B
                        # For demonstration, we'll create a dummy clause
                        # In full implementation, we'd extract the claim
                        pass

        # Use amino acid: check_entailment
        # We'll create a dummy conclusion to test consistency
        conclusion = [var_map[agents[0]]] if agents else [1]
        entailment_result = check_entailment(clauses, conclusion)
        logical_force = 1.0 if entailment_result else 0.0

        # Step 3: Constraint solving for more complex policies (alternates, etc.)
        # Use amino acid: is_uniquely_solvable
        variables = list(var_map.keys())
        domains = {agent: [0, 1] for agent in variables}  # 0=lies, 1=truth
        constraints = []
        for agent, policy in policies.items():
            if policy == 'always_lies':
                constraints.append(([agent], lambda a: a == 0))
            elif policy == 'always_truth':
                constraints.append(([agent], lambda a: a == 1))

        unique_solvable = is_uniquely_solvable(domains, constraints)
        uniqueness_bonus = 1.0 if unique_solvable else 0.5

        # Step 4: Information-theoretic confidence
        # Compute entropy of truth assignment distribution
        if sat_assignment:
            # Estimate distribution from SAT solution
            truth_count = sum(1 for v in sat_assignment.values() if v)
            p_truth = truth_count / n_agents if n_agents > 0 else 0.5
            dist = [p_truth, 1 - p_truth]
            info_entropy = entropy(dist) if 0 < p_truth < 1 else 0.0
            # Lower entropy -> higher confidence
            confidence_base = 1.0 - info_entropy  # normalize since max entropy ~1.0
        else:
            confidence_base = 0.5

        # Use T1 primitive: confidence_from_agreement
        agreement_scores = [confidence_base, logical_force, uniqueness_bonus]
        confidence = confidence_from_agreement(agreement_scores)

        # Step 5: Determine answer entity
        # The answer is typically an agent name or a statement about who is lying
        # We'll infer from question and consistent assignment
        answer = "unknown"
        if " who " in question.lower():
            # Question asks about identity
            if sat_assignment:
                # Find agents with specific truth values
                liar_agents = [agent for agent, idx in var_map.items() if sat_assignment.get(idx) is False]
                truth_agents = [agent for agent, idx in var_map.items() if sat_assignment.get(idx) is True]
                if "liar" in question.lower() or "lying" in question.lower():
                    answer = liar_agents[0] if liar_agents else "nobody"
                elif "truth" in question.lower():
                    answer = truth_agents[0] if truth_agents else "nobody"
                else:
                    answer = agents[0]  # default to first agent
        elif " what " in question.lower():
            # Question asks about statement truth
            answer = "true" if confidence > 0.6 else "false"

        # Use T1 primitive: bayesian_update to refine confidence
        prior = confidence
        likelihood = 0.8 if answer != "unknown" else 0.5
        updated_confidence = bayesian_update(prior, likelihood)
        if updated_confidence is None:
            updated_confidence = confidence

        return {
            "answer": answer,
            "confidence": updated_confidence,
            "reasoning": f"Logical consistency with policies, entropy={info_entropy:.2f}",
            "assignment": sat_assignment
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = str(reasoning_result["answer"])
        confidence = reasoning_result["confidence"]
        reasoning_text = reasoning_result.get("reasoning", "")

        results = []
        for c in candidates:
            # Primary: direct match of computed answer (case-insensitive)
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

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to improve discrimination."""
        if not scored:
            return scored

        # Simple normalization: softmax with temperature
        scores = [item["score"] for item in scored]
        max_score = max(scores) if scores else 1.0
        min_score = min(scores) if scores else 0.0
        range_score = max_score - min_score if max_score > min_score else 1.0

        for item in scored:
            # Linear stretch to [0,1] then square to emphasize differences
            normalized = (item["score"] - min_score) / range_score
            item["score"] = normalized ** 2

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