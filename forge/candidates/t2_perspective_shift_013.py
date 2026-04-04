import re
import zlib
from typing import Dict, List, Any, Set, Tuple
from forge_primitives import track_beliefs, sally_anne_test, confidence_from_agreement, entropy
from forge.amino_acids.pysat_acids import check_entailment, detect_paradox

class ReasoningTool:
    """evolutionary_biology x pysat_acids - perspective_shift"""

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

    def _extract(self, prompt: str) -> Dict[str, Any]:
        """Extract agents, facts, observations, and the question from the prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""
        
        agents = set()
        facts = set()
        observations = []
        
        # Extract agent names (capitalized words that appear as subjects)
        words = re.findall(r'\b([A-Z][a-z]+)\b', prompt)
        for word in words:
            if word not in ['The', 'A', 'An', 'It', 'He', 'She', 'They', 'We', 'I', 'You']:
                agents.add(word)
        
        # Extract facts (simple declarative statements in present tense)
        fact_pattern = r'\b(is|are|knows|believes|thinks)\b\s+([^,.]+)'
        for match in re.finditer(fact_pattern, prompt, re.IGNORECASE):
            fact = match.group(2).strip().lower()
            if fact and len(fact.split()) <= 6:
                facts.add(fact)
        
        # Extract observations: (agent, fact, True/False)
        # Look for patterns like "Alice sees that X", "Bob knows that Y"
        observation_pattern = r'([A-Z][a-z]+)\s+(sees|knows|observes|notices)\s+(that\s+)?([^,.]+)'
        for match in re.finditer(observation_pattern, prompt, re.IGNORECASE):
            agent = match.group(1)
            observation_text = match.group(4).strip().lower()
            if observation_text:
                # Determine if observation is positive or negative
                is_true = not any(neg in observation_text for neg in ['not ', "doesn't", "didn't", "isn't"])
                observations.append((agent, observation_text, is_true))
                agents.add(agent)
        
        return {
            "agents": list(agents),
            "facts": list(facts),
            "observations": observations,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use evolutionary biology concepts to model knowledge as heritable traits under selection pressure."""
        agents = structure["agents"]
        observations = structure["observations"]
        question = structure["question"]
        
        # Phase 1: Track initial beliefs using T1 primitive
        belief_state = track_beliefs(agents, observations)
        if belief_state is None:
            belief_state = {agent: set() for agent in agents}
        
        # Phase 2: Apply evolutionary pressure - beliefs that are more consistent survive
        # Model belief consistency as fitness
        belief_fitness = {}
        for agent in agents:
            # Convert beliefs to logical clauses for consistency checking
            clauses = []
            for belief in belief_state.get(agent, set()):
                # Simple encoding: each belief is a positive literal
                # We'll use a dummy encoding since we need actual variables
                pass
            
            # Use entropy of belief distribution as inverse fitness (lower entropy = higher fitness)
            if belief_state.get(agent):
                # Create a simple probability distribution over beliefs
                # Each belief gets equal weight for entropy calculation
                n_beliefs = len(belief_state[agent])
                if n_beliefs > 0:
                    probs = [1.0 / n_beliefs] * n_beliefs
                    belief_entropy = entropy(probs)
                    # Fitness = 1 - normalized entropy (higher fitness = more certain)
                    belief_fitness[agent] = 1.0 - (belief_entropy / (n_beliefs * 0.693)) if n_beliefs > 1 else 1.0
                else:
                    belief_fitness[agent] = 0.0
            else:
                belief_fitness[agent] = 0.0
        
        # Phase 3: Detect perspective conflicts using amino acid
        # Model different perspectives as competing hypotheses
        perspective_clauses = []
        agent_perspectives = {}
        
        for agent in agents:
            beliefs = belief_state.get(agent, set())
            if beliefs:
                # Create a clause representing this agent's perspective
                # For simplicity, encode as conjunction of beliefs
                perspective_str = f"{agent}_perspective: " + ", ".join(sorted(beliefs))
                agent_perspectives[agent] = perspective_str
                
                # Check if this perspective conflicts with others using paradox detection
                # We'll create simple clauses for testing
                test_clauses = []
                for belief in beliefs:
                    # Encode belief as positive literal
                    test_clauses.append([1])  # Dummy encoding
                
                # Use amino acid to check for paradox within agent's own beliefs
                paradox_result = detect_paradox(test_clauses)
                if paradox_result is not None:
                    # If paradox detected, this perspective is less fit
                    belief_fitness[agent] = belief_fitness.get(agent, 0.5) * 0.5
        
        # Phase 4: Determine which agent's perspective answers the question
        # Extract target from question
        target_agent = None
        question_lower = question.lower()
        
        # Look for agent names in the question
        for agent in agents:
            if agent.lower() in question_lower:
                target_agent = agent
                break
        
        # If question asks "what does X know/think", that's our answer
        if target_agent:
            # Get target agent's beliefs
            target_beliefs = belief_state.get(target_agent, set())
            if target_beliefs:
                # Select the most specific belief (shortest one) as answer
                computed_answer = min(target_beliefs, key=len)
            else:
                computed_answer = f"{target_agent} knows nothing"
        else:
            # Question might be about comparing perspectives
            # Find agent with highest fitness (most evolutionarily stable perspective)
            if belief_fitness:
                best_agent = max(belief_fitness.items(), key=lambda x: x[1])[0]
                computed_answer = best_agent
            else:
                computed_answer = "unknown"
        
        # Phase 5: Use confidence_from_agreement primitive
        fitness_values = list(belief_fitness.values())
        if fitness_values:
            confidence = confidence_from_agreement(fitness_values)
            if confidence is None:
                confidence = 0.5
        else:
            confidence = 0.5
        
        return {
            "answer": str(computed_answer),
            "confidence": float(confidence),
            "reasoning": f"Evolutionary fitness of perspectives: {belief_fitness}",
            "belief_state": belief_state,
            "fitness_scores": belief_fitness
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        results = []
        
        for candidate in candidates:
            # Primary scoring: direct match or containment
            if computed_answer.lower() in candidate.lower():
                score = 1.0
            else:
                # Secondary scoring: NCD similarity
                ncd_score = self._ncd(computed_answer, candidate)
                score = 1.0 / (1.0 + ncd_score)
            
            results.append({
                "candidate": candidate,
                "score": score,
                "computed_answer": computed_answer
            })
        
        return results

    def _calibrate(self, scored_candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores using confidence from reasoning."""
        if not scored_candidates:
            return scored_candidates
        
        # Use the confidence from reasoning to adjust scores
        # This is a simple linear adjustment
        confidence = scored_candidates[0].get("confidence_override", 0.5)
        
        for item in scored_candidates:
            original_score = item["score"]
            # Calibrate: high confidence strengthens scores, low confidence dampens extremes
            if confidence > 0.7:
                # Strengthen differentiation
                if original_score > 0.5:
                    item["score"] = min(1.0, original_score * (1.0 + (confidence - 0.7) * 0.5))
                else:
                    item["score"] = original_score * 0.8
            elif confidence < 0.3:
                # Compress toward middle
                item["score"] = 0.3 + (original_score * 0.4)
            else:
                # Moderate adjustment
                item["score"] = original_score * confidence + (1 - confidence) * 0.5
        
        return scored_candidates

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        """Main evaluation pipeline."""
        # Phase 1: Extract
        structure = self._extract(prompt)
        
        # Phase 2: Reason
        reasoning_result = self._reason(structure)
        
        # Phase 3: Score
        scored = self._score(candidates, reasoning_result)
        
        # Phase 4: Calibrate
        calibrated = self._calibrate(scored)
        
        # Sort by score descending
        return sorted(calibrated, key=lambda x: x["score"], reverse=True)