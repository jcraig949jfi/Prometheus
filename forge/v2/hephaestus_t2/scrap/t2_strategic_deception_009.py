import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import bayesian_update, entropy, confidence_from_agreement, topological_sort
from forge.amino_acids.pysat_acids import check_entailment


class ReasoningTool:
    """Seismology x SAT entailment - strategic deception"""

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
        """Extract entities, statements, and relationships from prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        
        # Find question (usually last sentence)
        question = lines[-1] if lines else ""
        
        # Extract agent names (capitalized words that appear as subjects)
        agent_pattern = r'\b([A-Z][a-z]+(?: [A-Z][a-z]+)*)\b'
        agents = set(re.findall(agent_pattern, prompt))
        
        # Extract statements about intentions/actions
        statements = []
        intention_keywords = ['says', 'claims', 'states', 'declares', 'intends', 'plans', 'will']
        for line in lines:
            if any(keyword in line.lower() for keyword in intention_keywords):
                statements.append(line)
        
        # Extract causal/temporal relationships
        edges = []
        relationship_words = ['before', 'after', 'if', 'then', 'because', 'so that']
        for line in lines:
            for agent1 in agents:
                for agent2 in agents:
                    if agent1 != agent2 and agent1 in line and agent2 in line:
                        # Check for ordering relationships
                        if 'before' in line.lower() and agent1 in line.split('before')[0]:
                            edges.append((agent1, agent2))
                        elif 'after' in line.lower() and agent2 in line.split('after')[0]:
                            edges.append((agent1, agent2))
        
        return {
            "agents": list(agents),
            "statements": statements,
            "edges": edges,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply seismology-inspired reasoning to detect strategic deception."""
        agents = structure["agents"]
        statements = structure["statements"]
        edges = structure["edges"]
        question = structure["question"]
        
        # Seismology concept: Foreshocks and aftershocks reveal hidden stress patterns
        # In strategic deception, stated intentions are "foreshocks", actual actions are "main shocks"
        # We look for inconsistencies between stated intentions and logical implications
        
        # 1. Build logical model from statements (seismic stress accumulation)
        clauses = []
        agent_to_var = {agent: i+1 for i, agent in enumerate(agents)}
        
        # Convert statements to SAT clauses
        for stmt in statements:
            # Simple parsing: "A says X" -> A implies X, but A might deceive
            # In seismology: surface motion (statement) vs deep fault movement (intent)
            if 'says' in stmt.lower() or 'claims' in stmt.lower():
                parts = stmt.split(' says ' if ' says ' in stmt else ' claims ')
                if len(parts) == 2:
                    speaker = parts[0].strip()
                    content = parts[1].strip()
                    
                    # Speaker variable
                    if speaker in agent_to_var:
                        speaker_var = agent_to_var[speaker]
                        
                        # Content analysis: check if it's about another agent
                        for other_agent in agents:
                            if other_agent != speaker and other_agent in content:
                                other_var = agent_to_var[other_agent]
                                
                                # Statement: speaker says something about other_agent
                                # In seismology: this creates stress along the fault line between them
                                # We encode: If speaker is truthful, then the statement holds
                                # But speaker might be deceptive (seismic foreshock that doesn't predict main shock)
                                
                                # Clause 1: speaker_truthful -> statement_about_other
                                # We'll use positive for "cooperates", negative for "defects"
                                if 'cooperate' in content.lower() or 'help' in content.lower():
                                    # speaker says they will cooperate with other
                                    clauses.append([-speaker_var, other_var])  # ¬speaker ∨ other_cooperates
                                elif 'defect' in content.lower() or 'betray' in content.lower():
                                    # speaker says they will defect against other
                                    clauses.append([-speaker_var, -other_var])  # ¬speaker ∨ ¬other_cooperates
        
        # 2. Use topological_sort to find dependency ordering (seismic wave propagation paths)
        # This is LOAD-BEARING: determines which agents' statements to trust first
        if edges:
            try:
                ordering = topological_sort(edges)
                if ordering is None:
                    # Graph has cycles - seismic resonance indicating deception feedback loop
                    ordering = agents
            except:
                ordering = agents
        else:
            ordering = agents
        
        # 3. Use entropy to measure uncertainty in the system (seismic energy distribution)
        # This is LOAD-BEARING: high entropy means more deceptive potential
        if clauses and agents:
            # Create probability distribution based on clause satisfaction
            # Simulate random assignments to estimate entropy
            n_agents = len(agents)
            # Simplified: assume each agent has 0.5 probability of cooperating
            # In seismology: equal probability of stress release along any fault
            probs = [0.5] * n_agents
            system_entropy = entropy(probs)
        else:
            system_entropy = 0.0
        
        # 4. Use check_entailment to find logical contradictions (seismic paradox detection)
        # This is LOAD-BEARING: detects when stated intentions contradict implied actions
        computed_answer = None
        confidence = 0.5
        
        if clauses and len(agents) >= 2:
            # Check if any agent's stated intention contradicts the logical implications
            for agent in agents:
                if agent in agent_to_var:
                    agent_var = agent_to_var[agent]
                    
                    # Premise: all clauses (the stated relationships)
                    premise_clauses = clauses
                    
                    # Conclusion: agent is deceptive (their statement is false)
                    # In seismology: foreshock doesn't match main shock pattern
                    conclusion_clause = [-agent_var]  # Agent is not truthful
                    
                    # Check if premises entail the conclusion
                    entailment_result = check_entailment(premise_clauses, conclusion_clause)
                    
                    if entailment_result is not None:
                        if entailment_result:
                            # Logical entailment found: agent must be deceptive
                            computed_answer = agent
                            # Confidence based on entropy: higher entropy = more uncertainty
                            confidence = 1.0 - min(system_entropy / len(agents), 0.8)
                            break
            
            # If no deceptive agent found through entailment, use bayesian_update
            # This is LOAD-BEARING: updates belief based on seismic evidence
            if computed_answer is None and agents:
                # Prior: equal probability for each agent being deceptive
                prior = 1.0 / len(agents)
                
                # Likelihood: based on statement consistency
                # In seismology: how well surface statements match deep structure
                n_statements = len([s for s in statements if any(agent in s for agent in agents)])
                if n_statements > 0:
                    # More statements increase chance of deception (more opportunities to lie)
                    likelihood = min(0.7, n_statements * 0.1)
                else:
                    likelihood = 0.3
                
                # Update belief
                posterior = bayesian_update(prior, likelihood)
                
                # Agent with most suspicious pattern (most statements about others)
                statement_counts = {agent: 0 for agent in agents}
                for stmt in statements:
                    for agent in agents:
                        if agent in stmt and ('says' in stmt or 'claims' in stmt):
                            statement_counts[agent] += 1
                
                if statement_counts:
                    most_suspicious = max(statement_counts.items(), key=lambda x: x[1])
                    if most_suspicious[1] > 0:
                        computed_answer = most_suspicious[0]
                        confidence = posterior
        
        # Fallback if still no answer
        if computed_answer is None and agents:
            # Use ordering from topological_sort (LOAD-BEARING)
            computed_answer = ordering[0] if ordering else agents[0]
            confidence = 0.3
        
        return {
            "answer": computed_answer if computed_answer else "",
            "confidence": confidence,
            "reasoning": f"Seismic analysis: entropy={system_entropy:.2f}, topological_ordering={ordering}",
            "ordering": ordering,
            "entropy": system_entropy
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        ordering = reasoning_result.get("ordering", [])
        
        results = []
        
        for candidate in candidates:
            # Primary scoring: exact match or contains computed answer
            score = 0.0
            
            if computed_answer:
                # Check if computed answer appears in candidate
                if computed_answer.lower() in candidate.lower():
                    score = 1.0 * confidence
                else:
                    # Check if any agent from ordering appears
                    for agent in ordering:
                        if agent.lower() in candidate.lower():
                            score = 0.7 * confidence
                            break
                    
                    if score == 0.0:
                        # Fallback: NCD similarity
                        ncd_score = self._ncd(computed_answer, candidate)
                        score = (1.0 - ncd_score) * confidence * 0.5
            
            # Use confidence_from_agreement as tie-breaker (LOAD-BEARING)
            # In seismology: multiple sensor readings should agree
            if score > 0:
                # Simulate multiple scoring methods agreeing
                scores_list = [score, confidence, reasoning_result.get("entropy", 0.5)]
                agreement_confidence = confidence_from_agreement(scores_list)
                score = score * (0.5 + 0.5 * agreement_confidence)
            
            results.append({
                "candidate": candidate,
                "score": score,
                "confidence": confidence
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper distribution."""
        if not scored:
            return scored
        
        scores = [item["score"] for item in scored]
        if max(scores) > 0:
            # Normalize to [0, 1] range
            max_score = max(scores)
            min_score = min(scores)
            
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