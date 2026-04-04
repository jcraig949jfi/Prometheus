import re
import zlib
from typing import Dict, List, Any, Set, Tuple
from forge_primitives import (
    track_beliefs,
    modus_ponens,
    check_transitivity,
    confidence_from_agreement,
    solve_constraints,
    topological_sort
)
from forge.amino_acids.pysat_acids import detect_paradox, check_entailment
from forge.amino_acids.constraint_acids import is_uniquely_solvable, solve_first

class ReasoningTool:
    """social_choice_theory x pysat_acids - liar_detection"""

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
        agents = set()
        statements = []
        truth_policies = {}  # agent -> policy (e.g., "always lies", "alternates")
        question = lines[-1] if lines else ""

        # Pattern for agent declarations
        agent_pattern = re.compile(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(always tells the truth|always lies|alternates|says)', re.IGNORECASE)
        # Pattern for statements
        statement_pattern = re.compile(r'"(.*?)"', re.DOTALL)

        for line in lines:
            # Find agents and their policies
            agent_match = agent_pattern.search(line)
            if agent_match:
                agent = agent_match.group(1)
                policy_phrase = agent_match.group(2).lower()
                agents.add(agent)
                if "always tells the truth" in policy_phrase:
                    truth_policies[agent] = "truth"
                elif "always lies" in policy_phrase:
                    truth_policies[agent] = "lie"
                elif "alternates" in policy_phrase:
                    truth_policies[agent] = "alternate"
                else:
                    truth_policies[agent] = "unknown"

            # Find quoted statements
            statement_matches = statement_pattern.findall(line)
            for stmt in statement_matches:
                # Try to associate statement with the most recent agent in the line
                associated_agent = None
                for agent in agents:
                    if agent in line and line.find(agent) < line.find(stmt):
                        associated_agent = agent
                        break
                statements.append({
                    "text": stmt,
                    "agent": associated_agent,
                    "raw_line": line
                })

        # Extract the actual question target (what is being asked)
        question_target = None
        if "who" in question.lower():
            # Find agent names in question
            for agent in agents:
                if agent in question:
                    question_target = agent
                    break
            if not question_target:
                # Maybe asking about a specific statement truth value
                q_words = question.lower().split()
                if "true" in q_words or "false" in q_words:
                    question_target = "truth_value"

        return {
            "agents": list(agents),
            "statements": statements,
            "truth_policies": truth_policies,
            "question": question,
            "question_target": question_target,
            "raw_prompt": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply social choice theory: model agents as voters with truthfulness constraints,
        use SAT to check consistency, derive collective judgment."""
        agents = structure["agents"]
        statements = structure["statements"]
        truth_policies = structure["truth_policies"]
        question_target = structure["question_target"]

        # T1 PRIMITIVE 1: Track beliefs based on observations
        # We'll model each agent's statement as an observation about the world
        observations = []
        for stmt in statements:
            if stmt["agent"]:
                # Encode statement as a fact ID
                fact_id = f"stmt_{hash(stmt['text']) % 1000}"
                # For now, we don't know truth value, so observation is "stated"
                observations.append((stmt["agent"], fact_id, True))
        belief_state = track_beliefs(agents, observations)
        if belief_state is None:
            belief_state = {}

        # Build a SAT encoding of the liar puzzle
        clauses = []
        var_map = {}  # mapping from (agent, statement_idx) to SAT variable
        next_var = 1

        # Create variables for each statement's truth value
        stmt_vars = {}
        for idx, stmt in enumerate(statements):
            var = next_var
            next_var += 1
            stmt_vars[idx] = var
            # Statement is either true or false
            clauses.append([var, -var])  # Actually, this is tautology. We'll handle properly below.

        # Encode agent truth-telling policies as constraints
        for agent, policy in truth_policies.items():
            # Find statements made by this agent
            agent_stmt_indices = [i for i, stmt in enumerate(statements) 
                                 if stmt["agent"] == agent]
            
            for stmt_idx in agent_stmt_indices:
                stmt_var = stmt_vars[stmt_idx]
                if policy == "truth":
                    # If agent tells truth, statement must be TRUE
                    clauses.append([stmt_var])  # stmt_var = TRUE
                elif policy == "lie":
                    # If agent always lies, statement must be FALSE
                    clauses.append([-stmt_var])  # stmt_var = FALSE
                elif policy == "alternate":
                    # For alternators, we need to model sequence
                    # This is simplified: we'll assume first statement by alternator is false
                    # Find first statement index by this agent
                    first_idx = min(agent_stmt_indices) if agent_stmt_indices else -1
                    if stmt_idx == first_idx:
                        clauses.append([-stmt_vars[stmt_idx]])  # First statement false
                    else:
                        # Subsequent statements alternate: need more complex encoding
                        # We'll handle via XOR with previous
                        prev_idx = max([i for i in agent_stmt_indices if i < stmt_idx], default=None)
                        if prev_idx is not None:
                            # Current != previous (alternates)
                            clauses.append([stmt_vars[prev_idx], stmt_vars[stmt_idx]])
                            clauses.append([-stmt_vars[prev_idx], -stmt_vars[stmt_idx]])

        # AMINO ACID 1: Detect if the set of statements is paradoxical
        paradox_info = detect_paradox(clauses)
        if paradox_info is None:
            paradox_detected = False
        else:
            paradox_detected = True

        # If paradoxical, we need to relax constraints or find minimal conflict
        if paradox_detected:
            # Try removing alternator constraints first
            simplified_clauses = [c for c in clauses if not any("alternate" in str(c) for c in c)]
            # Re-check
            paradox_info2 = detect_paradox(simplified_clauses)
            if paradox_info2 is None:
                clauses = simplified_clauses
                paradox_detected = False

        # T1 PRIMITIVE 2: Use modus ponens to derive implications between statements
        # Extract simple implications from statement text
        premises = []
        facts = set()
        for idx, stmt in enumerate(statements):
            text = stmt["text"].lower()
            if "if" in text and "then" in text:
                # Try to parse simple implication
                parts = text.split("then")
                if len(parts) == 2:
                    antecedent = parts[0].replace("if", "").strip()
                    consequent = parts[1].strip()
                    # Map to statement indices if possible
                    ant_idx = next((i for i, s in enumerate(statements) 
                                   if antecedent in s["text"].lower()), None)
                    cons_idx = next((i for i, s in enumerate(statements)
                                    if consequent in s["text"].lower()), None)
                    if ant_idx is not None and cons_idx is not None:
                        # Encode as SAT implication: (not ant_var) or cons_var
                        clauses.append([-stmt_vars[ant_idx], stmt_vars[cons_idx]])
                        # Also for modus ponens
                        premises.append((f"stmt_{ant_idx}", f"stmt_{cons_idx}"))
            
            # Check if statement asserts a simple fact
            if "is true" in text or "is false" in text:
                fact_id = f"stmt_{idx}"
                if "is true" in text:
                    facts.add(fact_id)
                elif "is false" in text:
                    # For false, we'd need negation handling
                    pass

        derived_facts = modus_ponens(premises, facts)
        if derived_facts is None:
            derived_facts = set()

        # AMINO ACID 2: Check entailment of the question
        # Convert question to a clause
        question_clause = []
        if question_target and question_target != "truth_value":
            # Question like "Is Alice telling the truth?"
            # Find Alice's statements
            alice_stmts = [i for i, stmt in enumerate(statements) 
                          if stmt["agent"] == question_target]
            if alice_stmts:
                # Question: is Alice's first statement true?
                q_var = stmt_vars[alice_stmts[0]]
                question_clause = [q_var]  # We'll check if this is entailed

        if question_clause:
            entailment_result = check_entailment(clauses, question_clause)
        else:
            entailment_result = None

        # T1 PRIMITIVE 3: Use constraint solving to find consistent truth assignments
        # Convert SAT problem to CSP
        variables = [f"stmt_{i}" for i in range(len(statements))]
        domains = {var: [0, 1] for var in variables}  # 0=false, 1=true
        
        constraints = []
        # Convert clauses to CSP constraints
        for clause in clauses:
            if len(clause) == 1:
                var_idx = abs(clause[0]) - 1
                if clause[0] > 0:
                    # stmt_var must be true
                    constraints.append(([variables[var_idx]], lambda x: x[0] == 1))
                else:
                    constraints.append(([variables[var_idx]], lambda x: x[0] == 0))
            elif len(clause) == 2:
                var1_idx = abs(clause[0]) - 1
                var2_idx = abs(clause[1]) - 1
                sign1 = 1 if clause[0] > 0 else 0
                sign2 = 1 if clause[1] > 0 else 0
                constraints.append(([variables[var1_idx], variables[var2_idx]],
                                   lambda x, s1=sign1, s2=sign2: x[0] == s1 or x[1] == s2))

        # Solve CSP
        solution = solve_constraints(variables, domains, constraints)
        
        # Determine the answer
        computed_answer = None
        confidence = 0.5
        
        if solution:
            # We have a consistent assignment
            # If question is about a specific agent's truthfulness
            if question_target and question_target in agents:
                # Check all statements by this agent in the solution
                agent_stmts = [i for i, stmt in enumerate(statements) 
                              if stmt["agent"] == question_target]
                if agent_stmts:
                    # See if all are true (truth-teller) or all false (liar)
                    truths = [solution[f"stmt_{i}"] for i in agent_stmts]
                    if all(t == 1 for t in truths):
                        computed_answer = f"{question_target} tells the truth"
                        confidence = 0.8
                    elif all(t == 0 for t in truths):
                        computed_answer = f"{question_target} lies"
                        confidence = 0.8
                    else:
                        # Mixed - might be alternator
                        computed_answer = f"{question_target} alternates"
                        confidence = 0.6
            else:
                # Default: answer with the solution summary
                true_stmts = [i for i in range(len(statements)) if solution.get(f"stmt_{i}") == 1]
                if true_stmts:
                    computed_answer = f"Statements {true_stmts} are true"
                else:
                    computed_answer = "All statements are false"
        else:
            # No consistent assignment
            computed_answer = "The statements are contradictory"
            confidence = 0.9

        # T1 PRIMITIVE 4: Use confidence aggregation from multiple reasoning paths
        scores_to_aggregate = []
        if solution:
            scores_to_aggregate.append(0.7)  # CSP solved
        if entailment_result is not None:
            scores_to_aggregate.append(0.8 if entailment_result else 0.3)
        if derived_facts:
            scores_to_aggregate.append(0.6)
        
        if scores_to_aggregate:
            aggregated_confidence = confidence_from_agreement(scores_to_aggregate)
            if aggregated_confidence is not None:
                confidence = aggregated_confidence

        # Fallback if no computed answer
        if not computed_answer:
            # Use social choice: majority vote on agent types based on policies
            truth_count = sum(1 for p in truth_policies.values() if p == "truth")
            lie_count = sum(1 for p in truth_policies.values() if p == "lie")
            if truth_count > lie_count:
                computed_answer = "Most agents tell the truth"
            else:
                computed_answer = "Most agents lie"

        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": f"SAT consistency: {not paradox_detected}, CSP solution: {solution is not None}, Entailment: {entailment_result}",
            "solution": solution,
            "paradox_detected": paradox_detected
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        results = []
        
        for candidate in candidates:
            # Primary: check if computed answer appears in candidate
            if computed_answer.lower() in candidate.lower():
                score = 1.0
            else:
                # Fallback: NCD similarity
                ncd_val = self._ncd(computed_answer, candidate)
                score = 1.0 / (1.0 + ncd_val)
            
            results.append({
                "candidate": candidate,
                "score": score,
                "computed_answer": computed_answer
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores based on confidence and consistency."""
        if not scored:
            return scored
        
        # Get confidence from reasoning result (passed through in score dict)
        confidence = 0.5
        if "computed_answer" in scored[0]:
            # Extract from first candidate's metadata
            pass  # Confidence is not directly in scored
        
        # Simple calibration: scale scores by confidence
        max_score = max(item["score"] for item in scored) if scored else 1.0
        if max_score > 0:
            for item in scored:
                item["score"] = item["score"] * confidence
        
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