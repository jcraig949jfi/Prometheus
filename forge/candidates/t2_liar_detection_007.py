import re
import zlib
from typing import Dict, List, Any, Tuple, Set
from forge_primitives import (
    bayesian_update,
    entropy,
    confidence_from_agreement,
    solve_sat,
    track_beliefs,
    modus_ponens
)
from forge.amino_acids.pysat_acids import detect_paradox, check_entailment
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable


class ReasoningTool:
    """Information theory x SAT solving - liar detection"""

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
        """Extract agents, statements, truth policies, and question from prompt."""
        lines = [line.strip() for line in prompt.split('\n') if line.strip()]
        agents = []
        statements = []
        policies = {}
        question = ""
        
        # Find agents (typically capitalized names or roles)
        agent_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        for line in lines:
            # Look for agent declarations
            if 'always tells the truth' in line.lower() or 'always lies' in line.lower() or 'alternates' in line.lower():
                matches = re.findall(agent_pattern, line)
                if matches:
                    agent = matches[0]
                    agents.append(agent)
                    if 'always tells the truth' in line.lower():
                        policies[agent] = 'truth'
                    elif 'always lies' in line.lower():
                        policies[agent] = 'lie'
                    elif 'alternates' in line.lower():
                        policies[agent] = 'alternate'
        
        # Extract statements (quoted or following "says")
        statement_pattern = r'["\'“]([^"\'”]+)["\'”]|says[:,\s]+["\'“]([^"\'”]+)["\'”]|says[:,\s]+([^\.]+)\.'
        for line in lines:
            matches = re.findall(statement_pattern, line)
            for match in matches:
                # Combine the three capture groups
                statement = match[0] or match[1] or match[2]
                if statement and len(statement.strip()) > 3:
                    statements.append(statement.strip())
        
        # Find question (usually last sentence with ?)
        for line in reversed(lines):
            if '?' in line:
                question = line.strip()
                break
        
        # Extract any numerical constraints or counts
        numbers = re.findall(r'\b(\d+)\b', prompt)
        numeric_constraints = [int(n) for n in numbers]
        
        return {
            "agents": agents,
            "statements": statements,
            "policies": policies,
            "question": question,
            "numeric_constraints": numeric_constraints,
            "raw_prompt": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use information theory and SAT to resolve liar puzzles."""
        agents = structure["agents"]
        statements = structure["statements"]
        policies = structure["policies"]
        question = structure["question"]
        
        # Phase 2a: Build logical model using information theory concepts
        # Treat truth values as information sources with entropy
        agent_entropies = {}
        for agent in agents:
            policy = policies.get(agent, 'unknown')
            if policy == 'truth':
                # Always true: entropy 0 (deterministic)
                agent_entropies[agent] = 0.0
            elif policy == 'lie':
                # Always false: entropy 0 (deterministic)
                agent_entropies[agent] = 0.0
            elif policy == 'alternate':
                # Alternating: maximum entropy for binary variable
                agent_entropies[agent] = 1.0
            else:
                # Unknown: assume maximum uncertainty
                agent_entropies[agent] = 1.0
        
        # Use entropy primitive to compute overall uncertainty
        entropy_values = list(agent_entropies.values())
        if entropy_values:
            system_entropy = entropy([v/2.0 for v in entropy_values] + [1.0 - sum(v/2.0 for v in entropy_values)/len(entropy_values)]) if len(entropy_values) > 1 else entropy_values[0]
        else:
            system_entropy = 1.0
        
        # Phase 2b: Encode as SAT problem using amino acids
        # Map agents and statements to boolean variables
        var_map = {}
        clauses = []
        var_counter = 1
        
        for i, agent in enumerate(agents):
            var_map[f"A_{agent}_truthful"] = var_counter
            var_counter += 1
        
        for i, stmt in enumerate(statements):
            var_map[f"S_{i}"] = var_counter
            var_counter += 1
        
        # Add constraints based on policies
        for agent in agents:
            policy = policies.get(agent, 'unknown')
            agent_var = var_map[f"A_{agent}_truthful"]
            
            if policy == 'truth':
                # Agent always truthful: their statement variable equals statement truth
                # For simplicity, if agent makes statement S_i, then A_truthful -> S_i
                # We'll handle this in statement-agent mapping
                pass
            elif policy == 'lie':
                # Agent always lies: their statement variable is opposite of statement truth
                pass
            elif policy == 'alternate':
                # Alternating: need sequence tracking - simplified to unknown for SAT
                pass
        
        # Create simple constraints: if we have statements, assume they're about each other
        # For liar puzzles, often statements refer to other agents' truthfulness
        if len(statements) >= 2 and len(agents) >= 2:
            # Common pattern: "X says Y is a liar" or similar
            # Encode as: (X_truthful <-> (Y_truthful XOR statement_meaning))
            # Simplified version for demonstration
            clause1 = [var_map[f"A_{agents[0]}_truthful"], -var_map[f"A_{agents[1]}_truthful"]]
            clause2 = [-var_map[f"A_{agents[0]}_truthful"], var_map[f"A_{agents[1]}_truthful"]]
            clauses.extend([clause1, clause2])
        
        # Use SAT solving amino acid
        sat_result = None
        if clauses and var_counter > 1:
            sat_result = solve_sat(clauses, var_counter - 1)
        
        # Use paradox detection amino acid
        paradox_info = None
        if clauses:
            paradox_info = detect_paradox(clauses)
        
        # Phase 2c: Bayesian update on agent reliability
        prior = 0.5  # Initial belief agent is truthful
        likelihood = 0.8 if policies.get(agents[0] if agents else '', '') == 'truth' else 0.2
        posterior = bayesian_update(prior, likelihood)
        if posterior is None:
            posterior = prior
        
        # Phase 2d: Track beliefs using primitive
        observations = []
        if len(agents) >= 2:
            # Simulate observation: agent1 observes agent2's statement
            observations.append((agents[0], f"{agents[1]}_statement", True))
        belief_tracking = track_beliefs(agents, observations)
        
        # Phase 2e: Determine answer based on question
        computed_answer = ""
        confidence = 0.5
        
        # Parse question to determine what's being asked
        if "who" in question.lower() and agents:
            # Question about agent identity
            if sat_result:
                # Find which agent is truthful based on SAT solution
                truthful_agents = []
                for agent in agents:
                    var_name = f"A_{agent}_truthful"
                    if var_name in var_map:
                        var_idx = var_map[var_name]
                        if var_idx in sat_result and sat_result[var_idx]:
                            truthful_agents.append(agent)
                
                if truthful_agents:
                    computed_answer = truthful_agents[0]
                    confidence = 0.7
                else:
                    # Fallback: agent with highest posterior
                    computed_answer = agents[0]
                    confidence = posterior
            else:
                # Use entropy: lower entropy means more certain
                if agent_entropies:
                    min_entropy_agent = min(agent_entropies.items(), key=lambda x: x[1])[0]
                    computed_answer = min_entropy_agent
                    confidence = 1.0 - (agent_entropies[min_entropy_agent] / 2.0)
                else:
                    computed_answer = agents[0] if agents else "Unknown"
        
        elif "what" in question.lower() and statements:
            # Question about statement truth value
            if sat_result and len(statements) > 0:
                stmt_var = var_map.get("S_0", 0)
                if stmt_var in sat_result:
                    is_true = sat_result[stmt_var]
                    computed_answer = "true" if is_true else "false"
                    confidence = 0.8
            else:
                computed_answer = "true" if posterior > 0.5 else "false"
                confidence = abs(posterior - 0.5) * 2
        
        elif "how many" in question.lower():
            # Question about count
            if structure["numeric_constraints"]:
                computed_answer = str(structure["numeric_constraints"][0])
                confidence = 0.6
            else:
                computed_answer = str(len(truthful_agents) if 'truthful_agents' in locals() else len(agents))
        
        else:
            # Default: first agent
            computed_answer = agents[0] if agents else "No solution"
        
        # Use confidence_from_agreement primitive
        confidence_scores = [confidence, posterior, 1.0 - system_entropy]
        final_confidence = confidence_from_agreement(confidence_scores)
        if final_confidence is None:
            final_confidence = confidence
        
        return {
            "answer": computed_answer,
            "confidence": final_confidence,
            "reasoning": f"SAT solvable: {sat_result is not None}, Paradox detected: {paradox_info}, System entropy: {system_entropy:.3f}",
            "sat_result": sat_result,
            "entropy": system_entropy
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact match or substring of computed answer
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            elif candidate.lower() in computed_answer.lower():
                base_score = 0.9
            else:
                # Use NCD similarity
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
        if scores:
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