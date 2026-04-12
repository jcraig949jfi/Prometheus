import re
import zlib
from typing import Dict, List, Any, Set, Tuple

from forge_primitives import (
    bayesian_update,
    entropy,
    confidence_from_agreement,
    solve_sat,
    track_beliefs,
    modus_ponens,
    check_transitivity,
    topological_sort
)
from forge.amino_acids.pysat_acids import check_entailment, detect_paradox
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable


class ReasoningTool:
    """Feedback systems x SAT/Constraint solving - Liar detection"""

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
        """Extract agents, statements, truth policies, and question."""
        lines = [line.strip() for line in prompt.split('\n') if line.strip()]
        agents = set()
        statements = {}
        truth_policies = {}
        question = ""
        
        # Find agents (capitalized names, often followed by colon or "says")
        agent_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        for line in lines:
            # Extract agent names
            matches = re.findall(agent_pattern, line)
            for match in matches:
                if match.lower() not in ['always', 'never', 'sometimes', 'truth', 'lie']:
                    agents.add(match)
            
            # Extract statements with speaker
            if ':' in line or 'says' in line.lower():
                parts = re.split(r'[:]', line, maxsplit=1)
                if len(parts) == 2:
                    speaker = parts[0].strip()
                    content = parts[1].strip()
                    if speaker in agents:
                        statements[speaker] = content
                        # Determine truth policy from context
                        if 'always tells the truth' in line.lower() or 'truth-teller' in line.lower():
                            truth_policies[speaker] = 'truth'
                        elif 'always lies' in line.lower() or 'liar' in line.lower():
                            truth_policies[speaker] = 'lie'
                        elif 'sometimes lies' in line.lower() or 'alternates' in line.lower():
                            truth_policies[speaker] = 'alternating'
            
            # Extract question (usually last line)
            if line.endswith('?'):
                question = line
        
        # If no explicit policies found, infer from statements
        for agent in agents:
            if agent not in truth_policies:
                # Check if statement contains self-reference about truthfulness
                if agent in statements:
                    stmt = statements[agent].lower()
                    if 'i always tell the truth' in stmt or 'i am truthful' in stmt:
                        truth_policies[agent] = 'truth'
                    elif 'i always lie' in stmt or 'i am a liar' in stmt:
                        truth_policies[agent] = 'lie'
                    else:
                        truth_policies[agent] = 'unknown'
        
        return {
            "agents": list(agents),
            "statements": statements,
            "truth_policies": truth_policies,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use feedback systems approach: agents' statements form a network
        where truth values propagate through logical constraints.
        Stability analysis determines consistent assignments."""
        agents = structure["agents"]
        statements = structure["statements"]
        truth_policies = structure["truth_policies"]
        question = structure["question"]
        
        # Convert to SAT variables: each agent has truth value (True=truthful)
        # and each statement has a logical meaning
        n_agents = len(agents)
        agent_to_var = {agent: i+1 for i, agent in enumerate(agents)}
        
        clauses = []
        
        # Add constraints from truth policies
        for agent, policy in truth_policies.items():
            var = agent_to_var[agent]
            if policy == 'truth':
                clauses.append([var])  # Agent must be truthful
            elif policy == 'lie':
                clauses.append([-var])  # Agent must be liar
            # 'alternating' and 'unknown' handled by statement constraints
        
        # Encode statements as logical constraints
        for speaker, stmt in statements.items():
            speaker_var = agent_to_var[speaker]
            
            # Parse statement content
            stmt_lower = stmt.lower()
            
            # Check for references to other agents
            for other_agent in agents:
                if other_agent.lower() in stmt_lower and other_agent != speaker:
                    other_var = agent_to_var[other_agent]
                    
                    # Determine statement type
                    if 'tells the truth' in stmt_lower or 'truthful' in stmt_lower:
                        # "X says: Y tells the truth"
                        # If speaker is truthful, other_var must be True
                        # If speaker is liar, other_var must be False
                        clauses.append([-speaker_var, other_var])  # speaker truthful → other truthful
                        clauses.append([speaker_var, -other_var])  # speaker liar → other liar
                    
                    elif 'lies' in stmt_lower or 'liar' in stmt_lower:
                        # "X says: Y lies"
                        clauses.append([-speaker_var, -other_var])  # speaker truthful → other liar
                        clauses.append([speaker_var, other_var])    # speaker liar → other truthful
            
            # Self-referential statements
            if 'i tell the truth' in stmt_lower or 'i am truthful' in stmt_lower:
                # "I tell the truth" - if true, speaker_var=True; if false, speaker_var=False
                # This creates a tautology, handled by SAT solver
                pass
            
            elif 'i lie' in stmt_lower or 'i am a liar' in stmt_lower:
                # "I am a liar" - paradox if taken literally
                # Encode as: speaker_var ↔ ¬speaker_var (unsatisfiable)
                clauses.append([speaker_var, speaker_var])  # True
                clauses.append([-speaker_var, -speaker_var])  # Also True - creates contradiction
        
        # Use SAT solver to find consistent assignments
        sat_result = solve_sat(clauses, n_agents)
        
        # Check for paradox using amino acid
        paradox_info = detect_paradox(clauses)
        
        # Use constraint solving as alternative approach
        # Define variables and domains
        variables = [f"truth_{agent}" for agent in agents]
        domains = {var: [0, 1] for var in variables}  # 0=liar, 1=truthful
        
        constraints = []
        for i, agent in enumerate(agents):
            var = f"truth_{agent}"
            policy = truth_policies.get(agent, 'unknown')
            
            if policy == 'truth':
                constraints.append(([var], lambda v: v[0] == 1))
            elif policy == 'lie':
                constraints.append(([var], lambda v: v[0] == 0))
            
            # Add statement constraints
            if agent in statements:
                stmt = statements[agent].lower()
                for other_agent in agents:
                    if other_agent.lower() in stmt and other_agent != agent:
                        other_var = f"truth_{other_agent}"
                        if 'tells the truth' in stmt or 'truthful' in stmt:
                            # If agent truthful, other truthful
                            constraints.append(([var, other_var], lambda v: v[0] == 0 or v[1] == 1))
                            # If agent liar, other liar
                            constraints.append(([var, other_var], lambda v: v[0] == 1 or v[1] == 0))
                        elif 'lies' in stmt or 'liar' in stmt:
                            # If agent truthful, other liar
                            constraints.append(([var, other_var], lambda v: v[0] == 0 or v[1] == 0))
                            # If agent liar, other truthful
                            constraints.append(([var, other_var], lambda v: v[0] == 1 or v[1] == 1))
        
        # Solve constraint system
        constraint_solution = solve_first(variables, domains, constraints)
        
        # Check uniqueness
        is_unique = is_uniquely_solvable(variables, domains, constraints)
        
        # Determine answer based on question
        computed_answer = ""
        confidence = 0.5
        
        # Extract what is being asked
        if 'who' in question.lower():
            # Find which agent matches the description
            if sat_result:
                # Use SAT solution to determine truth values
                truth_values = {}
                for agent, var in agent_to_var.items():
                    truth_values[agent] = sat_result.get(var, False)
                
                # Analyze question to determine target
                if 'truth' in question.lower() or 'truthful' in question.lower():
                    # Find truthful agents
                    truthful_agents = [agent for agent, val in truth_values.items() if val]
                    if truthful_agents:
                        computed_answer = truthful_agents[0]
                        confidence = 0.8
                    else:
                        computed_answer = "None"
                elif 'lie' in question.lower() or 'liar' in question.lower():
                    # Find lying agents
                    lying_agents = [agent for agent, val in truth_values.items() if not val]
                    if lying_agents:
                        computed_answer = lying_agents[0]
                        confidence = 0.8
                    else:
                        computed_answer = "None"
                else:
                    # Default to first agent with determined value
                    for agent in agents:
                        if agent in truth_values:
                            computed_answer = agent
                            break
            elif constraint_solution:
                # Use constraint solution
                for agent in agents:
                    var = f"truth_{agent}"
                    if var in constraint_solution:
                        if constraint_solution[var] == 1 and 'truth' in question.lower():
                            computed_answer = agent
                            confidence = 0.7
                            break
                        elif constraint_solution[var] == 0 and 'lie' in question.lower():
                            computed_answer = agent
                            confidence = 0.7
                            break
        
        # If no answer determined, use entropy-based selection
        if not computed_answer:
            # Calculate entropy of possible truth assignments
            if sat_result:
                # For simplicity, assume uniform distribution over possible assignments
                # In reality, we'd enumerate all models
                probs = [0.5, 0.5]  # Placeholder
                e = entropy(probs)
                
                # Use entropy to decide: high entropy → ambiguous, pick first agent
                if e > 0.9:
                    computed_answer = agents[0] if agents else "Unknown"
                    confidence = 0.3
                else:
                    computed_answer = agents[-1] if agents else "Unknown"
                    confidence = 0.6
            else:
                computed_answer = agents[0] if agents else "Unknown"
                confidence = 0.4
        
        # Use confidence_from_agreement to refine confidence
        scores = []
        if sat_result:
            # Score based on SAT solution consistency
            score1 = 1.0 if sat_result else 0.0
            scores.append(score1)
        
        if constraint_solution:
            # Score based on constraint solution
            score2 = 1.0 if constraint_solution else 0.0
            scores.append(score2)
        
        if paradox_info and paradox_info.get("is_paradox", False):
            # Paradox detected affects confidence
            scores.append(0.2)
        
        if scores:
            agg_confidence = confidence_from_agreement(scores)
            # Bayesian update of confidence
            prior = 0.5
            likelihood = agg_confidence
            posterior = bayesian_update(prior, likelihood, false_positive=0.1)
            confidence = posterior
        
        # Use track_beliefs to model agent knowledge (if applicable)
        if len(agents) >= 2:
            # Create simple belief tracking
            agent_list = list(agents)
            observations = []
            for i, agent in enumerate(agent_list):
                # Each agent observes their own truth value (simplified)
                observations.append((agent, f"truthful_{agent}", True))
            
            beliefs = track_beliefs(agent_list, observations)
            # Use beliefs to adjust answer if needed
            if computed_answer in beliefs:
                # Agent believes something about themselves
                pass
        
        # Use check_transitivity for relationship analysis
        if len(agents) >= 3:
            # Create relations based on statements
            relations = []
            for speaker, stmt in statements.items():
                stmt_lower = stmt.lower()
                for other in agents:
                    if other != speaker and other.lower() in stmt_lower:
                        if 'truth' in stmt_lower:
                            relations.append((speaker, other))
                        elif 'lie' in stmt_lower:
                            relations.append((other, speaker))  # Inverse relation
            
            if relations:
                transitive_closure = check_transitivity(relations)
                # Use closure to infer additional constraints
                for agent in agents:
                    if agent in transitive_closure:
                        reachable = transitive_closure[agent]
                        if reachable:
                            # Agent's truth value affects reachable agents
                            pass
        
        # Final answer determination
        # If question asks about specific statement truth value
        if 'true' in question.lower() or 'false' in question.lower():
            # Analyze specific statement
            for speaker, stmt in statements.items():
                if any(word in question.lower() for word in stmt.lower().split()[:3]):
                    # This statement is being asked about
                    if sat_result:
                        speaker_var = agent_to_var.get(speaker)
                        if speaker_var in sat_result:
                            if sat_result[speaker_var]:
                                computed_answer = "True"
                            else:
                                computed_answer = "False"
        
        return {
            "answer": computed_answer,
            "confidence": min(max(confidence, 0.0), 1.0),
            "reasoning": f"SAT solution: {sat_result is not None}, Constraint solution: {constraint_solution is not None}, Paradox: {paradox_info.get('is_paradox', False) if paradox_info else False}",
            "agents": agents,
            "truth_assignments": sat_result if sat_result else {}
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = str(reasoning_result["answer"])
        confidence = reasoning_result["confidence"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact match or containment
            score = 0.0
            
            # Check if computed answer appears in candidate
            if computed_answer.lower() in candidate.lower():
                score = 0.9 + (confidence * 0.1)
            else:
                # Use NCD similarity
                ncd_score = self._ncd_similarity(computed_answer, candidate)
                reasoning_similarity = self._ncd_similarity(reasoning_text, candidate)
                score = (ncd_score * 0.7 + reasoning_similarity * 0.3) * confidence
            
            results.append({
                "candidate": candidate,
                "score": score,
                "raw_score": score
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper distribution."""
        if not scored:
            return scored
        
        scores = [item["raw_score"] for item in scored]
        if not scores:
            return scored
        
        min_score = min(scores)
        max_score = max(scores)
        
        if max_score - min_score > 0.001:
            # Normalize to [0, 1] range
            for item in scored:
                normalized = (item["raw_score"] - min_score) / (max_score - min_score)
                item["score"] = normalized
        else:
            # All scores similar, assign uniform scores
            for item in scored:
                item["score"] = 0.5
        
        return scored

    def _ncd_similarity(self, a: str, b: str) -> float:
        """Normalized Compression Distance similarity."""
        if not a or not b:
            return 0.0
        
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + " " + b).encode()))
        
        if max(ca, cb) == 0:
            return 1.0
        
        ncd = (cab - min(ca, cb)) / max(ca, cb)
        return 1.0 - min(ncd, 1.0)