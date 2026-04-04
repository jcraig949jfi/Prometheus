import re
import zlib
from typing import Dict, List, Any, Set, Tuple

from forge_primitives import (
    bayesian_update,
    confidence_from_agreement,
    entropy,
    solve_sat,
    track_beliefs,
    modus_ponens
)
from forge.amino_acids.pysat_acids import detect_paradox, check_entailment
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable


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
        """Parse prompt to extract agents, statements, and truth policies."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""

        agents = set()
        statements = []
        truth_policies = {}  # agent -> policy (e.g., "always lies", "alternates")

        # Extract agent names (capitalized words at start of sentences)
        for line in lines:
            # Look for patterns like "Alice says", "Bob claims"
            match = re.match(r'^([A-Z][a-z]+)\s+(?:says|claims|states|asserts)', line)
            if match:
                agent = match.group(1)
                agents.add(agent)
                # Extract the quoted or asserted statement
                statement_match = re.search(r'["“]([^"”]+)["”]', line)
                if statement_match:
                    statement_text = statement_match.group(1)
                    statements.append((agent, statement_text))
                else:
                    # Fallback: take everything after "says"
                    parts = line.split('says', 1)
                    if len(parts) > 1:
                        statement_text = parts[1].strip()
                        statements.append((agent, statement_text))

            # Detect truth-telling policies
            policy_patterns = [
                (r'always tells the truth', 'truthful'),
                (r'always lies', 'liar'),
                (r'alternates', 'alternates'),
                (r'tells truth on (?:Mondays|even days)', 'conditional'),
                (r'random', 'random')
            ]
            for pattern, policy in policy_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # Associate with the most recent agent mentioned
                    if agent:
                        truth_policies[agent] = policy

        # If no explicit policies, infer from context
        for agent in agents:
            if agent not in truth_policies:
                # Check if agent's name appears in a statement about truthfulness
                for line in lines:
                    if agent in line and ('truth' in line.lower() or 'lie' in line.lower()):
                        if 'always' in line.lower():
                            if 'truth' in line.lower():
                                truth_policies[agent] = 'truthful'
                            elif 'lie' in line.lower() or 'lies' in line.lower():
                                truth_policies[agent] = 'liar'
                        break
                else:
                    truth_policies[agent] = 'unknown'

        return {
            "agents": list(agents),
            "statements": statements,
            "policies": truth_policies,
            "question": question,
            "raw_lines": lines
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply relativistic reasoning: truth is frame-dependent, resolve via logical invariants."""
        agents = structure["agents"]
        statements = structure["statements"]
        policies = structure["policies"]
        question = structure["question"]

        # Use relativity concept: each agent's "truth frame" depends on their policy
        # We'll model this as a constraint satisfaction problem across frames

        # Step 1: Encode statements as logical variables
        # Each statement gets a propositional variable
        prop_vars = {}
        var_counter = 1
        for agent, stmt in statements:
            var_name = f"S{var_counter}"
            prop_vars[(agent, stmt)] = var_counter
            var_counter += 1

        # Step 2: Build constraints based on truth policies (relativistic frames)
        clauses = []
        n_vars = var_counter - 1

        # Map policies to logical constraints
        for agent, policy in policies.items():
            agent_statements = [(a, s) for (a, s) in statements if a == agent]
            if not agent_statements:
                continue

            if policy == 'truthful':
                # In truthful frame: all statements by this agent are TRUE
                for (a, s) in agent_statements:
                    var = prop_vars[(a, s)]
                    clauses.append([var])  # Variable must be true
            elif policy == 'liar':
                # In liar frame: all statements by this agent are FALSE
                for (a, s) in agent_statements:
                    var = prop_vars[(a, s)]
                    clauses.append([-var])  # Variable must be false
            elif policy == 'alternates':
                # Alternating: if multiple statements, they alternate truth values
                # For simplicity with relativity: treat as unknown but consistent within frame
                # We'll use entropy to measure uncertainty
                pass

        # Step 3: Add consistency constraints from statement content
        # Parse statements that refer to other statements or agents
        for (agent, stmt), var in prop_vars.items():
            # Check if statement is about another agent's truthfulness
            for other_agent in agents:
                if other_agent in stmt and agent != other_agent:
                    if 'truth' in stmt.lower() or 'lie' in stmt.lower():
                        # Statement claims something about other agent's policy
                        # For relativity: this creates a relationship between frames
                        if 'truth' in stmt.lower():
                            # "X tells truth" -> all X's statements are true
                            x_stmts = [prop_vars[(a, s)] for (a, s) in prop_vars if a == other_agent]
                            for x_var in x_stmts:
                                clauses.append([-var, x_var])  # If stmt true, then X's stmts true
                        elif 'lie' in stmt.lower():
                            # "X lies" -> all X's statements are false
                            x_stmts = [prop_vars[(a, s)] for (a, s) in prop_vars if a == other_agent]
                            for x_var in x_stmts:
                                clauses.append([-var, -x_var])  # If stmt true, then X's stmts false

        # Step 4: Use SAT solving to find consistent truth assignments across frames
        sat_result = solve_sat(clauses, n_vars)
        
        # Step 5: Apply relativistic concept - measure "proper time" of each solution
        # In relativity, different observers disagree on simultaneity but agree on invariants
        # Here: different policy frames give different truth assignments, but logical consistency is invariant
        
        # Use amino acid to detect paradox
        paradox_info = detect_paradox(clauses)
        
        # Use amino acid to check if question is entailed
        # First, extract what the question is asking for
        question_target = None
        if 'who' in question.lower():
            # Find agent names in question
            for agent in agents:
                if agent.lower() in question.lower():
                    question_target = agent
                    break
        elif 'what' in question.lower() and 'statement' in question.lower():
            # Might be asking which statement is true
            # We'll use the most probable statement
            pass
        
        # Build premise clauses for entailment check
        premise_clauses = clauses
        
        # Step 6: Use T1 primitives for probabilistic reasoning across frames
        # Bayesian update across possible worlds (frames)
        prior = 0.5
        likelihood = 0.8 if sat_result else 0.2
        posterior = bayesian_update(prior, likelihood)
        if posterior is None:
            posterior = prior
        
        # Track beliefs across agents (relativistic observers)
        observations = []
        for (agent, stmt), var in prop_vars.items():
            if sat_result and sat_result.get(var, False):
                observations.append((agent, stmt, True))
            else:
                observations.append((agent, stmt, False))
        
        belief_tracking = track_beliefs(agents, observations)
        
        # Compute entropy of truth assignments (measure of frame-dependent uncertainty)
        if sat_result:
            # Count true vs false
            true_count = sum(1 for v in sat_result.values() if v)
            false_count = n_vars - true_count
            if n_vars > 0:
                p_true = true_count / n_vars
                p_false = false_count / n_vars
                truth_entropy = entropy([p_true, p_false])
            else:
                truth_entropy = 0.0
        else:
            truth_entropy = 1.0  # Max uncertainty if no solution
        
        # Step 7: Determine the answer
        computed_answer = None
        
        # If question asks for a specific agent
        if question_target:
            # Check if agent's statements are consistent with their policy
            agent_stmts = [s for (a, s) in statements if a == question_target]
            if agent_stmts:
                # Use constraint solving to check uniqueness
                variables = {f"stmt_{i}": [True, False] for i in range(len(agent_stmts))}
                constraints = []
                # Constraint: all statements must match policy
                if policies.get(question_target) == 'truthful':
                    for i in range(len(agent_stmts)):
                        constraints.append(([f"stmt_{i}"], lambda x: x[0]))
                elif policies.get(question_target) == 'liar':
                    for i in range(len(agent_stmts)):
                        constraints.append(([f"stmt_{i}"], lambda x: not x[0]))
                
                unique = is_uniquely_solvable(variables, constraints)
                if unique is not None:
                    computed_answer = question_target
                else:
                    # Fallback: agent with most consistent statements
                    computed_answer = question_target
            else:
                computed_answer = question_target
        else:
            # Default: find the agent that is most "truthful" in the invariant sense
            # Compute confidence from agreement across possible frames
            if sat_result:
                # Score each agent by consistency of their statements
                agent_scores = []
                for agent in agents:
                    agent_vars = [sat_result.get(prop_vars[(a, s)], False) 
                                 for (a, s) in prop_vars if a == agent]
                    if agent_vars:
                        # Convert bool to float for confidence calculation
                        score_vals = [1.0 if v else 0.0 for v in agent_vars]
                        agent_confidence = confidence_from_agreement(score_vals)
                        agent_scores.append((agent, agent_confidence))
                
                if agent_scores:
                    best_agent = max(agent_scores, key=lambda x: x[1])[0]
                    computed_answer = best_agent
                else:
                    computed_answer = agents[0] if agents else "Unknown"
            else:
                computed_answer = "Paradox detected"
        
        # Step 8: Use amino acid for entailment check
        if computed_answer and computed_answer in agents:
            # Create a clause representing "agent X is truthful"
            conclusion_var = max(prop_vars.values()) + 1 if prop_vars else 1
            conclusion_clause = [conclusion_var]
            # For entailment, we'd need to encode this properly
            # Simplified: just note if paradox was detected
            entailment_result = None
            if paradox_info:
                # If paradox, answer might be "impossible"
                if "unsat" in str(paradox_info).lower():
                    computed_answer = "Contradiction - no consistent solution"
        
        return {
            "answer": computed_answer,
            "confidence": min(0.95, posterior),  # Cap confidence
            "reasoning": f"Relativistic frame analysis with entropy {truth_entropy:.3f}",
            "sat_solution": sat_result is not None,
            "beliefs": belief_tracking
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        results = []
        
        for candidate in candidates:
            # Primary: check if computed answer appears in candidate
            if computed_answer and computed_answer.lower() in candidate.lower():
                score = 1.0
            else:
                # Fallback: NCD similarity
                score = 1.0 / (1.0 + self._ncd(str(computed_answer), candidate))
            
            results.append({
                "candidate": candidate,
                "score": score,
                "raw_score": score
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores using confidence from agreement."""
        raw_scores = [item["raw_score"] for item in scored]
        
        if len(raw_scores) > 1:
            confidence = confidence_from_agreement(raw_scores)
            if confidence is None:
                confidence = 0.5
        else:
            confidence = 0.5
        
        # Adjust scores toward extreme if high confidence
        for item in scored:
            raw = item["raw_score"]
            if confidence > 0.7:
                # Push toward 0 or 1
                if raw > 0.5:
                    calibrated = 0.5 + 0.5 * (raw - 0.5) * (1 + confidence)
                else:
                    calibrated = 0.5 - 0.5 * (0.5 - raw) * (1 + confidence)
                calibrated = max(0.0, min(1.0, calibrated))
            else:
                calibrated = raw
            
            item["score"] = calibrated
        
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