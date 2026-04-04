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
    """signal_processing x pysat_acids - liar_detection"""

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
        truth_policies = {}  # agent -> policy ("always truth", "always lie", "random")
        question = lines[-1] if lines else ""

        # Extract agent names (capitalized words that appear as subjects)
        for line in lines:
            # Look for patterns like "Alice says", "Bob claims", "Charlie states"
            agent_match = re.search(r'([A-Z][a-z]+)\s+(?:says|claims|states|asserts|tells)', line)
            if agent_match:
                agent = agent_match.group(1)
                if agent not in agents:
                    agents.append(agent)

                # Extract policy clues
                line_lower = line.lower()
                if 'always tells the truth' in line_lower or 'truthful' in line_lower:
                    truth_policies[agent] = 'truth'
                elif 'always lies' in line_lower or 'liar' in line_lower:
                    truth_policies[agent] = 'lie'
                elif 'random' in line_lower or 'flips a coin' in line_lower:
                    truth_policies[agent] = 'random'
                else:
                    truth_policies[agent] = 'unknown'

                # Extract statement content
                statement_match = re.search(r'says\s+"([^"]+)"', line)
                if statement_match:
                    statements.append((agent, statement_match.group(1)))
                else:
                    # Fallback: extract after "says"
                    says_idx = line.lower().find('says')
                    if says_idx != -1:
                        stmt = line[says_idx + 4:].strip()
                        if stmt:
                            statements.append((agent, stmt))

        # Extract propositional variables (simple facts mentioned)
        facts = set()
        for _, stmt in statements:
            # Look for simple factual claims like "X is Y"
            fact_match = re.search(r'([A-Z][a-z]+)\s+is\s+([A-Z][a-z]+)', stmt)
            if fact_match:
                facts.add(f"{fact_match.group(1)}_is_{fact_match.group(2)}")
            # Look for binary relations
            rel_match = re.search(r'([A-Z][a-z]+)\s+(did|was|has)\s+([a-z]+)', stmt)
            if rel_match:
                facts.add(f"{rel_match.group(1)}_{rel_match.group(2)}_{rel_match.group(3)}")

        return {
            "agents": agents,
            "statements": statements,
            "policies": truth_policies,
            "question": question,
            "facts": list(facts),
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply signal processing concepts to filter noise and extract truth."""
        agents = structure["agents"]
        statements = structure["statements"]
        policies = structure["policies"]
        facts = structure["facts"]

        # Signal processing analogy: agents are noisy channels, statements are signals
        # Truth-tellers: high SNR (signal-to-noise ratio)
        # Liars: inverted signal (negative correlation)
        # Random: pure noise (zero correlation)

        # Step 1: Encode statements as propositional logic
        # Map each statement to a SAT variable
        var_map = {}
        clauses = []
        agent_beliefs = {}

        for i, (agent, stmt) in enumerate(statements):
            var = i + 1  # SAT variables start at 1
            var_map[(agent, stmt)] = var

            # Encode agent's truth policy as constraints
            policy = policies.get(agent, 'unknown')
            if policy == 'truth':
                # If agent is truthful, statement must be TRUE
                clauses.append([var])
            elif policy == 'lie':
                # If agent lies, statement must be FALSE
                clauses.append([-var])
            elif policy == 'random':
                # Random: no constraint (pure noise)
                pass

            # Track which facts each agent's statement refers to
            agent_beliefs.setdefault(agent, []).append(var)

        # Step 2: Add logical relationships between statements
        # Look for contradictions and implications
        for i, (agent1, stmt1) in enumerate(statements):
            for j, (agent2, stmt2) in enumerate(statements):
                if i >= j:
                    continue

                # Check if statements are negations of each other
                if self._are_contradictory(stmt1, stmt2):
                    var1 = var_map[(agent1, stmt1)]
                    var2 = var_map[(agent2, stmt2)]
                    clauses.append([-var1, -var2])  # Cannot both be true
                    clauses.append([var1, var2])    # Cannot both be false

                # Check if one implies the other
                if self._implies(stmt1, stmt2):
                    var1 = var_map[(agent1, stmt1)]
                    var2 = var_map[(agent2, stmt2)]
                    clauses.append([-var1, var2])  # If stmt1 true, stmt2 must be true

        # Step 3: Use SAT solver to find consistent truth assignments
        n_vars = len(var_map)
        sat_result = solve_sat(clauses, n_vars)

        # Use amino acid: detect paradox in the statement set
        paradox_info = detect_paradox(clauses)
        if paradox_info is not None:
            # If paradox detected, system is inconsistent
            consistency = "paradox"
        else:
            consistency = "consistent" if sat_result else "inconsistent"

        # Step 4: Apply signal processing: filter out random agents (noise)
        # Compute belief reliability scores using T1 primitives
        reliability_scores = []
        for agent in agents:
            if agent not in agent_beliefs:
                continue

            agent_vars = agent_beliefs[agent]
            policy = policies.get(agent, 'unknown')

            # Bayesian update to estimate agent reliability
            if policy == 'truth':
                prior = 0.9  # High prior for truth-teller
                likelihood = 0.8
            elif policy == 'lie':
                prior = 0.1  # Low prior for liar
                likelihood = 0.2
            elif policy == 'random':
                prior = 0.5  # Neutral prior for random
                likelihood = 0.5
            else:
                prior = 0.5
                likelihood = 0.5

            reliability = bayesian_update(prior, likelihood)
            if reliability is None:
                reliability = prior

            reliability_scores.append(reliability)

        # Compute overall confidence from agreement among reliable agents
        if reliability_scores:
            confidence = confidence_from_agreement(reliability_scores)
            if confidence is None:
                confidence = 0.5
        else:
            confidence = 0.5

        # Step 5: Determine the actual facts using entropy minimization
        # (Signal processing: minimize uncertainty in reconstructed signal)
        if sat_result:
            # Extract truth values for factual statements
            fact_truth_values = {}
            for fact in facts:
                # Check which statements refer to this fact
                supporting = []
                opposing = []
                for (agent, stmt), var in var_map.items():
                    if fact in stmt:
                        if sat_result.get(var, False):
                            supporting.append(agent)
                        else:
                            opposing.append(agent)

                # Use entropy to decide: lower entropy = more consistent signal
                if supporting or opposing:
                    p_support = len(supporting) / (len(supporting) + len(opposing))
                    p_oppose = 1 - p_support
                    ent = entropy([p_support, p_oppose]) if p_support > 0 and p_oppose > 0 else 0
                    # Fact is likely true if supported by low-entropy agents
                    fact_truth_values[fact] = (p_support > 0.5, ent)
        else:
            fact_truth_values = {}

        # Step 6: Answer the question by extracting the key fact
        computed_answer = ""
        question = structure["question"].lower()

        # Look for "who" questions
        if "who" in question:
            # Find the agent with highest reliability
            if agents:
                agent_reliability = {}
                for agent in agents:
                    policy = policies.get(agent, 'unknown')
                    if policy == 'truth':
                        agent_reliability[agent] = 0.9
                    elif policy == 'lie':
                        agent_reliability[agent] = 0.1
                    elif policy == 'random':
                        agent_reliability[agent] = 0.5
                    else:
                        agent_reliability[agent] = 0.5

                if agent_reliability:
                    best_agent = max(agent_reliability.items(), key=lambda x: x[1])[0]
                    computed_answer = best_agent

        # Look for "what" or factual questions
        elif "what" in question or "which" in question:
            if fact_truth_values:
                # Find the fact with lowest entropy (clearest signal)
                sorted_facts = sorted(fact_truth_values.items(), key=lambda x: x[1][1])
                if sorted_facts:
                    best_fact, (is_true, ent) = sorted_facts[0]
                    # Extract the key entity from the fact
                    parts = best_fact.split('_')
                    if len(parts) >= 2:
                        computed_answer = parts[0]  # Usually the subject

        # Fallback: use modus ponens on the extracted facts
        if not computed_answer and facts:
            # Create simple implication rules from statements
            premises = []
            for fact in facts:
                # Simple rule: if agent is truthful, their statements are true
                for agent in agents:
                    if policies.get(agent) == 'truth':
                        premises.append((f"{agent}_truthful", fact))

            known_facts = set()
            for agent in agents:
                if policies.get(agent) == 'truth':
                    known_facts.add(f"{agent}_truthful")

            deduced = modus_ponens(premises, known_facts)
            if deduced:
                computed_answer = list(deduced)[0].split('_')[0]

        # Final fallback: use track_beliefs to see what consistent agents believe
        if not computed_answer and agents:
            observations = []
            for agent in agents:
                policy = policies.get(agent, 'unknown')
                if policy == 'truth':
                    observations.append((agent, "consistent", True))
                elif policy == 'lie':
                    observations.append((agent, "consistent", False))

            belief_state = track_beliefs(agents, observations)
            if belief_state:
                # Find agents who believe in consistency
                consistent_agents = [agent for agent, beliefs in belief_state.items()
                                     if "consistent" in beliefs]
                if consistent_agents:
                    computed_answer = consistent_agents[0]

        # Use amino acid: check entailment for the computed answer
        if computed_answer and var_map:
            # Create a clause representing the answer
            answer_clause = []
            for (agent, stmt), var in var_map.items():
                if computed_answer in agent or computed_answer in stmt:
                    answer_clause.append(var)

            if answer_clause:
                entailment = check_entailment(clauses, answer_clause)
                if entailment is True:
                    confidence = min(confidence + 0.2, 1.0)
                elif entailment is False:
                    confidence = max(confidence - 0.2, 0.0)

        # Use amino acid: check if solution is uniquely determined
        if var_map:
            # Convert to CSP for uniqueness check
            variables = list(range(1, n_vars + 1))
            domains = {v: [0, 1] for v in variables}
            csp_constraints = []
            for clause in clauses:
                def make_constraint(clause):
                    def constraint(assignment):
                        for lit in clause:
                            var = abs(lit)
                            val = assignment.get(var, None)
                            if val is None:
                                continue
                            if lit > 0 and val == 1:
                                return True
                            if lit < 0 and val == 0:
                                return True
                        return False
                    return constraint

                csp_constraints.append(([abs(lit) for lit in clause], make_constraint(clause)))

            unique = is_uniquely_solvable(domains, csp_constraints)
            if unique is True:
                confidence = min(confidence + 0.1, 1.0)

        return {
            "answer": computed_answer if computed_answer else "unknown",
            "confidence": confidence,
            "consistency": consistency,
            "fact_truth_values": fact_truth_values,
            "reasoning": f"Signal processing approach: filtered noise from random agents, "
                        f"detected {consistency}, computed answer from minimal entropy facts."
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        reasoning_text = reasoning_result["reasoning"]

        results = []
        for candidate in candidates:
            # Primary scoring: check if computed answer appears in candidate
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity to reasoning text
                base_score = 1.0 / (1.0 + self._ncd(reasoning_text, candidate))

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
        min_score = min(scores)
        max_score = max(scores)

        if max_score - min_score > 0:
            # Normalize to [0, 1] range
            for item in scored:
                item["score"] = (item["score"] - min_score) / (max_score - min_score)
        else:
            # All scores equal, assign uniform scores
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

        if max(ca, cb) == 0:
            return 1.0

        return (cab - min(ca, cb)) / max(ca, cb)

    def _are_contradictory(self, stmt1: str, stmt2: str) -> bool:
        """Check if two statements are logical negations."""
        stmt1_lower = stmt1.lower()
        stmt2_lower = stmt2.lower()

        # Simple negation patterns
        negations = [
            (" is ", " is not "),
            (" was ", " was not "),
            (" has ", " has not "),
            (" did ", " did not "),
            (" are ", " are not "),
            (" were ", " were not "),
            (" will ", " will not ")
        ]

        for pos, neg in negations:
            if (pos in stmt1_lower and neg in stmt2_lower) or \
               (neg in stmt1_lower and pos in stmt2_lower):
                # Check if they're about the same subject
                subj1 = stmt1_lower.split()[0] if stmt1_lower.split() else ""
                subj2 = stmt2_lower.split()[0] if stmt2_lower.split() else ""
                if subj1 == subj2:
                    return True

        return False

    def _implies(self, stmt1: str, stmt2: str) -> bool:
        """Check if statement 1 implies statement 2."""
        # Simple implication: if stmt1 is about an agent being truthful,
        # and stmt2 is a statement by that agent
        stmt1_lower = stmt1.lower()
        stmt2_lower = stmt2.lower()

        # Pattern: "X is truthful" implies "what X says is true"
        if "truthful" in stmt1_lower or "tells the truth" in stmt1_lower:
            # Extract agent name from stmt1
            words1 = stmt1_lower.split()
            if words1:
                agent1 = words1[0]
                # Check if stmt2 starts with the same agent
                if stmt2_lower.start