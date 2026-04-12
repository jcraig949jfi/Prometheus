import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import bayesian_update, entropy, confidence_from_agreement, topological_sort
from forge.amino_acids.pysat_acids import check_entailment


class ReasoningTool:
    """Error Correcting Codes x SAT Entailment - Liar Detection"""

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
        """Extract agents, statements, and truth policies from liar detection puzzle."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        
        agents = []
        statements = []
        truth_policies = {}  # agent -> policy (always_truth, always_lie, random)
        question = ""
        
        # Find agents (capitalized names, often followed by 'says' or 'states')
        agent_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        
        for line in lines:
            # Look for truth-telling policies
            lower_line = line.lower()
            if 'always tells the truth' in lower_line or 'always truthful' in lower_line:
                for match in re.finditer(agent_pattern, line):
                    agent = match.group(1)
                    if agent not in agents:
                        agents.append(agent)
                    truth_policies[agent] = 'truth'
            elif 'always lies' in lower_line or 'always a liar' in lower_line:
                for match in re.finditer(agent_pattern, line):
                    agent = match.group(1)
                    if agent not in agents:
                        agents.append(agent)
                    truth_policies[agent] = 'lie'
            elif 'random' in lower_line or 'coin flip' in lower_line:
                for match in re.finditer(agent_pattern, line):
                    agent = match.group(1)
                    if agent not in agents:
                        agents.append(agent)
                    truth_policies[agent] = 'random'
            
            # Look for statements (X says: "...")
            says_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+says[:\s]+["\']?(.+?)["\']?$', line, re.IGNORECASE)
            if says_match:
                agent = says_match.group(1)
                statement = says_match.group(2).strip()
                if agent not in agents:
                    agents.append(agent)
                statements.append((agent, statement))
            
            # Identify question (usually last line with '?' or starts with 'Who'/'What')
            if '?' in line and ('who' in lower_line or 'what' in lower_line or 'which' in lower_line):
                question = line
        
        # If no explicit policies found, infer from context
        for agent in agents:
            if agent not in truth_policies:
                # Check if mentioned in statement context
                truth_policies[agent] = 'unknown'
        
        return {
            "agents": agents,
            "statements": statements,
            "policies": truth_policies,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use error-correcting codes framework: treat statements as encoded messages,
        truth policies as error patterns, and find the consistent decoding."""
        agents = structure["agents"]
        statements = structure["statements"]
        policies = structure["policies"]
        
        # Build logical constraints from statements
        clauses = []
        var_map = {}  # proposition -> variable number
        next_var = 1
        
        # First, extract atomic propositions from statements
        propositions = set()
        for agent, statement in statements:
            # Simple parsing: look for "X is Y" or "X did Y" patterns
            if ' is ' in statement.lower() or ' was ' in statement.lower() or ' did ' in statement.lower():
                propositions.add(statement)
        
        # Map propositions to SAT variables
        for prop in propositions:
            var_map[prop] = next_var
            next_var += 1
        
        # Encode each statement with truth policy constraints
        # Error-correcting codes perspective: each agent's statement is a transmitted codeword
        # with potential errors based on their truth policy
        for agent, statement in statements:
            policy = policies.get(agent, 'unknown')
            prop_var = var_map.get(statement, None)
            
            if prop_var is not None:
                # Truth-teller: statement must be true
                if policy == 'truth':
                    clauses.append([prop_var])  # statement is true
                # Liar: statement must be false
                elif policy == 'lie':
                    clauses.append([-prop_var])  # statement is false
                # Random: statement could be true or false (no constraint)
                elif policy == 'random':
                    # Add both possibilities as soft constraints?
                    # For error correction, random introduces maximum entropy
                    pass
        
        # CRITICAL PRIMITIVE 1: Use entropy to measure uncertainty in the system
        # Higher entropy = more ambiguous situation (like high error rate in codes)
        policy_counts = {'truth': 0, 'lie': 0, 'random': 0, 'unknown': 0}
        for agent in agents:
            policy = policies.get(agent, 'unknown')
            policy_counts[policy] += 1
        
        total_agents = len(agents)
        if total_agents > 0:
            probs = [count/total_agents for count in policy_counts.values() if count > 0]
            system_entropy = entropy(probs) if probs else 0.0
        else:
            system_entropy = 0.0
        
        # CRITICAL AMINO ACID: Use SAT entailment to find what MUST be true
        # This is like error correction: find the message that must be transmitted
        # given the noisy observations (statements with liar/truth-teller noise)
        
        # Build conclusion clauses based on the question
        # For liar puzzles, we often need to determine which agent said what
        # or what the actual facts are
        
        computed_answer = ""
        confidence = 0.5
        
        if clauses and var_map:
            # Try to find what is entailed by the constraints
            # Check each proposition to see if it's necessarily true or false
            
            true_props = []
            false_props = []
            
            for prop, var in var_map.items():
                # Check if prop is entailed (must be true)
                entailment_true = check_entailment(clauses, [var])
                # Check if ¬prop is entailed (must be false)
                entailment_false = check_entailment(clauses, [-var])
                
                if entailment_true:
                    true_props.append(prop)
                elif entailment_false:
                    false_props.append(prop)
            
            # CRITICAL PRIMITIVE 2: Use topological sort to order agents by reliability
            # In error-correcting codes, some bits are more reliable than others
            # Truth-tellers are reliable, liars are anti-reliable, random is noisy
            
            # Build dependency graph: reliable agents constrain less reliable ones
            edges = []
            for i, agent1 in enumerate(agents):
                for j, agent2 in enumerate(agents):
                    if i != j:
                        policy1 = policies.get(agent1, 'unknown')
                        policy2 = policies.get(agent2, 'unknown')
                        
                        # Truth-tellers are most reliable (source nodes)
                        # Liars are next (they give inverted information)
                        # Random are least reliable (sink nodes)
                        if (policy1 == 'truth' and policy2 in ['lie', 'random', 'unknown']) or \
                           (policy1 == 'lie' and policy2 in ['random', 'unknown']) or \
                           (policy1 == 'random' and policy2 == 'unknown'):
                            edges.append((agent1, agent2))
            
            reliability_order = topological_sort(edges)
            
            # CRITICAL PRIMITIVE 3: Use Bayesian update to combine evidence
            # Each agent's statement provides evidence with different reliability
            # Truth-teller: likelihood = 1.0 if statement matches truth, 0.0 otherwise
            # Liar: likelihood = 0.0 if statement matches truth, 1.0 otherwise
            # Random: likelihood = 0.5
            
            # Start with uniform prior over propositions
            prior = 0.5
            
            # Update based on each agent's statement
            posterior = prior
            for agent, statement in statements:
                policy = policies.get(agent, 'unknown')
                prop_var = var_map.get(statement, None)
                
                if prop_var is not None:
                    if policy == 'truth':
                        # Truth-teller: P(statement|truth) = 1.0
                        likelihood = 1.0
                        false_positive = 0.0
                    elif policy == 'lie':
                        # Liar: P(statement|truth) = 0.0, so we invert
                        likelihood = 0.0
                        false_positive = 1.0  # They always say false things
                    elif policy == 'random':
                        # Random: P(statement|truth) = 0.5
                        likelihood = 0.5
                        false_positive = 0.5
                    else:
                        # Unknown: assume moderate reliability
                        likelihood = 0.7
                        false_positive = 0.3
                    
                    # Update belief about this proposition
                    posterior = bayesian_update(posterior, likelihood, false_positive)
            
            # Determine answer based on what we've deduced
            if true_props:
                # If we found necessarily true propositions, use the first one
                computed_answer = true_props[0]
                # Confidence based on posterior and system entropy
                # Lower entropy (more certain policies) → higher confidence
                confidence = posterior * (1.0 - system_entropy)
            elif false_props:
                # If we found necessarily false propositions, state their negation
                computed_answer = f"Not {false_props[0]}"
                confidence = (1.0 - posterior) * (1.0 - system_entropy)
            elif reliability_order:
                # Fallback: most reliable agent's name
                computed_answer = reliability_order[0]
                confidence = 0.3
            else:
                # Last resort: first agent mentioned
                computed_answer = agents[0] if agents else "Unknown"
                confidence = 0.1
        else:
            # No constraints extracted
            if agents:
                computed_answer = agents[0]
            else:
                computed_answer = "No solution"
            confidence = 0.0
        
        # CRITICAL PRIMITIVE 4: Use confidence_from_agreement to refine confidence
        # Multiple lines of evidence (SAT, topological sort, Bayesian)
        evidence_scores = []
        if clauses:
            # SAT gives binary evidence: either consistent or not
            evidence_scores.append(1.0 if computed_answer != "No solution" else 0.0)
        if system_entropy < 0.9:  # Not completely uncertain
            evidence_scores.append(1.0 - system_entropy)
        if posterior != 0.5:  # Bayesian update moved away from prior
            evidence_scores.append(abs(posterior - 0.5) * 2.0)
        
        if evidence_scores:
            final_confidence = confidence_from_agreement(evidence_scores)
        else:
            final_confidence = confidence
        
        return {
            "answer": computed_answer,
            "confidence": final_confidence,
            "reasoning": f"Error-correcting decoding with entropy {system_entropy:.2f}, posterior {posterior:.2f}",
            "true_props": true_props if 'true_props' in locals() else [],
            "false_props": false_props if 'false_props' in locals() else []
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: check if computed answer appears in candidate
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
        """Simple calibration: ensure scores are in reasonable range."""
        if not scored:
            return scored
        
        # Find max score for normalization
        max_score = max(item["score"] for item in scored)
        if max_score > 0:
            for item in scored:
                item["score"] = item["score"] / max_score
        
        return scored

    def _ncd(self, a: str, b: str) -> float:
        """Normalized Compression Distance between two strings."""
        if not a or not b:
            return 1.0
        
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + " " + b).encode()))
        
        return (cab - min(ca, cb)) / max(ca, cb) if max(ca, cb) > 0 else 1.0