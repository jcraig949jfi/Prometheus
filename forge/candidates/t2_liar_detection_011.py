import re
import zlib
from typing import Dict, List, Any, Tuple, Set

from forge_primitives import (
    bayesian_update,
    confidence_from_agreement,
    entropy,
    solve_sat,
    modus_ponens,
    track_beliefs
)
from forge.amino_acids.pysat_acids import solve, detect_paradox, check_entailment
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable


class ReasoningTool:
    """Electromagnetism x SAT/Constraint solving - liar_detection"""

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
        """Parse prompt to find agents, statements, and truth policies."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        agents = []
        statements = []
        truth_policies = {}  # agent -> policy (e.g., "always lies", "alternates")
        question = lines[-1] if lines else ""

        # Find agent names (capitalized words that appear as subjects)
        words = re.findall(r'\b([A-Z][a-z]+)\b', prompt)
        potential_agents = [w for w in words if len(w) > 2]
        # Heuristic: agents are often followed by "says", "claims", "always", "never"
        for i, line in enumerate(lines):
            lower_line = line.lower()
            # Look for policy patterns
            if "always tells the truth" in lower_line or "always truthful" in lower_line:
                for agent in potential_agents:
                    if agent in line:
                        truth_policies[agent] = "truth"
            elif "always lies" in lower_line or "always false" in lower_line:
                for agent in potential_agents:
                    if agent in line:
                        truth_policies[agent] = "lie"
            elif "alternates" in lower_line or "alternately" in lower_line:
                for agent in potential_agents:
                    if agent in line:
                        truth_policies[agent] = "alternate"
            # Extract quoted statements or claims
            if "says" in lower_line or "claims" in lower_line:
                # Find the agent before "says"
                match = re.search(r'([A-Z][a-z]+)\s+(?:says|claims)', line)
                if match:
                    agent = match.group(1)
                    if agent not in agents:
                        agents.append(agent)
                    # Extract the statement content (after colon or quote)
                    statement_part = line.split('says')[-1].split('claims')[-1].strip(' "\'')
                    if statement_part:
                        statements.append((agent, statement_part))

        # If no explicit policies found, infer from common patterns
        for agent in agents:
            if agent not in truth_policies:
                # Check if agent appears in context of truth/lie keywords
                agent_context = " ".join([line for line in lines if agent in line])
                if any(word in agent_context.lower() for word in ["truth", "honest", "correct"]):
                    truth_policies[agent] = "truth"
                elif any(word in agent_context.lower() for word in ["lie", "false", "wrong"]):
                    truth_policies[agent] = "lie"
                else:
                    truth_policies[agent] = "unknown"

        return {
            "agents": agents,
            "statements": statements,
            "policies": truth_policies,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use electromagnetic field analogy: agents as charged particles,
        truth values as charges (+1 for true, -1 for false),
        logical constraints as field equations.
        """
        agents = structure["agents"]
        statements = structure["statements"]
        policies = structure["policies"]
        question = structure["question"]

        # Electromagnetic analogy: each agent has a "truth charge" (+1 for truth-teller, -1 for liar)
        # Unknown policies create superposition states (entropy)
        # Logical constraints create "field lines" that must be satisfied

        # Step 1: Map policies to initial charges
        initial_charges = {}
        policy_entropy = []
        for agent, policy in policies.items():
            if policy == "truth":
                initial_charges[agent] = +1.0
                policy_entropy.append(0.0)  # Certain
            elif policy == "lie":
                initial_charges[agent] = -1.0
                policy_entropy.append(0.0)
            elif policy == "alternate":
                # Alternating: superposition of +1 and -1
                initial_charges[agent] = 0.0  # Neutral charge
                policy_entropy.append(1.0)    # High entropy
            else:  # unknown
                initial_charges[agent] = 0.0
                policy_entropy.append(0.5)    # Moderate entropy

        # Use T1 primitive: entropy of policy distribution
        policy_uncertainty = entropy(policy_entropy) if policy_entropy else 0.0

        # Step 2: Convert statements to logical constraints (SAT clauses)
        # Each statement is a proposition that may be true or false
        # Agent's truth policy determines whether the statement matches reality
        
        # Create proposition variables
        prop_vars = {}
        var_counter = 1
        for agent, stmt in statements:
            prop_name = f"S_{agent}_{var_counter}"
            prop_vars[(agent, stmt)] = var_counter
            var_counter += 1

        # Build SAT clauses based on policies
        clauses = []
        for (agent, stmt), var in prop_vars.items():
            policy = policies.get(agent, "unknown")
            if policy == "truth":
                # If agent tells truth, statement is TRUE
                clauses.append([var])  # var must be true
            elif policy == "lie":
                # If agent lies, statement is FALSE
                clauses.append([-var])  # var must be false
            elif policy == "alternate":
                # Alternating: cannot determine directly - will be constrained by consistency
                pass
            # unknown: no constraint from policy alone

        # Add consistency constraints: statements about other agents' truthfulness
        # Example: "Alice says Bob is lying" creates relation between Alice's truth and Bob's statement
        for agent, stmt in statements:
            # Check if statement references another agent's truth value
            for other_agent in agents:
                if other_agent in stmt and other_agent != agent:
                    # Patterns like "X is lying", "X tells the truth"
                    lower_stmt = stmt.lower()
                    if "lying" in lower_stmt or "lies" in lower_stmt or "false" in lower_stmt:
                        # Statement: "other_agent is lying"
                        # This means: other_agent's statements are false
                        # We need to encode this as a constraint
                        # For simplicity, we'll create a relation variable
                        rel_var = var_counter
                        var_counter += 1
                        # If agent tells truth, rel_var is true (other_agent lies)
                        # If agent lies, rel_var is false (other_agent tells truth)
                        policy = policies.get(agent, "unknown")
                        if policy == "truth":
                            clauses.append([rel_var])
                        elif policy == "lie":
                            clauses.append([-rel_var])
                        # rel_var implies constraints on other_agent's statements
                        for (oa, o_stmt), o_var in prop_vars.items():
                            if oa == other_agent:
                                # If other_agent lies, all their statements are false
                                clauses.append([-rel_var, -o_var])  # rel_var → ¬o_var
                                # Also need: ¬rel_var → ? (if other_agent tells truth)
                                # This gets complex - we'll use amino acid for full SAT solving

        # Use amino acid: SAT solving to check consistency
        sat_result = None
        if clauses:
            sat_result = solve(clauses)
        
        # Use T1 primitive: solve_sat as alternative/verification
        t1_sat_result = None
        if clauses:
            t1_sat_result = solve_sat(clauses, var_counter - 1)

        # Step 3: Determine answer to the question
        # Common question patterns: "Who is telling the truth?", "What is the actual situation?"
        computed_answer = ""
        confidence = 0.5
        
        # Analyze question to determine what is being asked
        lower_q = question.lower()
        if "who" in lower_q and ("truth" in lower_q or "lying" in lower_q):
            # Question about identity of truth-teller/liar
            # Use the SAT model to infer agent truth values
            if sat_result is not None:
                # Count agents with consistent truth assignments
                truth_tellers = []
                for agent in agents:
                    # Check if agent's statements are all true in the model
                    agent_stmts = [(a, s) for (a, s) in prop_vars.keys() if a == agent]
                    if agent_stmts:
                        # For truth-teller, all statements should be true
                        all_true = all(sat_result.get(prop_vars[(a, s)], False) for (a, s) in agent_stmts)
                        if all_true:
                            truth_tellers.append(agent)
                
                if truth_tellers:
                    computed_answer = truth_tellers[0]  # First truth-teller found
                else:
                    # No clear truth-teller, use policy information
                    for agent, policy in policies.items():
                        if policy == "truth":
                            computed_answer = agent
                            break
                    if not computed_answer:
                        computed_answer = agents[0] if agents else "Unknown"
            else:
                # SAT failed, use policy-based answer
                for agent, policy in policies.items():
                    if policy == "truth":
                        computed_answer = agent
                        break
                if not computed_answer:
                    computed_answer = agents[0] if agents else "Unknown"
        
        elif "what" in lower_q or "actual" in lower_q or "true" in lower_q:
            # Question about the actual state of affairs
            # Try to extract a specific fact from statements
            factual_statements = []
            for agent, stmt in statements:
                # Look for statements about facts (not about other agents)
                if not any(a in stmt for a in agents if a != agent):
                    factual_statements.append(stmt)
            
            if factual_statements:
                # Use the most frequently mentioned fact
                from collections import Counter
                fact_counts = Counter(factual_statements)
                computed_answer = fact_counts.most_common(1)[0][0] if fact_counts else "Unknown"
            else:
                computed_answer = "Cannot determine"
        
        else:
            # Generic fallback
            computed_answer = " ".join(agents) if agents else "No agents found"

        # Use T1 primitive: confidence from agreement between SAT solvers
        agreement_scores = []
        if sat_result is not None and t1_sat_result is not None:
            # Compare assignments for overlapping variables
            common_vars = set(sat_result.keys()) & set(t1_sat_result.keys())
            if common_vars:
                matches = sum(1 for v in common_vars if sat_result[v] == t1_sat_result[v])
                agreement = matches / len(common_vars) if common_vars else 0.0
                agreement_scores.append(agreement)
        
        # Use T1 primitive: bayesian update on confidence
        prior_confidence = 0.5
        likelihood = 0.8 if sat_result is not None else 0.3
        updated_confidence = bayesian_update(prior_confidence, likelihood)
        if updated_confidence is None:
            updated_confidence = prior_confidence
        
        # Use T1 primitive: final confidence from agreement
        if agreement_scores:
            final_confidence = confidence_from_agreement(agreement_scores)
            if final_confidence is not None:
                confidence = final_confidence
            else:
                confidence = updated_confidence
        else:
            confidence = updated_confidence

        # Use amino acid: detect paradox in the statements
        paradox_info = None
        if clauses:
            paradox_info = detect_paradox(clauses)
        
        # Adjust confidence based on paradox detection
        if paradox_info is not None:
            if paradox_info:  # Paradox detected
                confidence *= 0.7  # Reduce confidence due to inconsistency
            else:
                confidence *= 1.1  # Slight boost for consistency

        return {
            "answer": computed_answer,
            "confidence": min(max(confidence, 0.0), 1.0),
            "reasoning": f"Electromagnetic charge model with SAT consistency check. Policies: {policies}. Paradox detected: {paradox_info}",
            "agents": agents,
            "policies": policies
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        
        results = []
        for candidate in candidates:
            # Primary: check if computed answer appears in candidate
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity
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
        
        # Simple normalization to [0, 1] range
        scores = [item["score"] for item in scored]
        min_score = min(scores)
        max_score = max(scores)
        
        if max_score > min_score:
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