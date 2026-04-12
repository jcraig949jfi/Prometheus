import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import bayesian_update, entropy, confidence_from_agreement, topological_sort
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query
from forge.amino_acids.constraint_acids import is_uniquely_solvable


class ReasoningTool:
    """chemical_kinetics x pgmpy_acids - strategic_deception"""

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        # Phase 1: EXTRACT
        structure = self._extract(prompt)
        # Phase 2: REASON
        reasoning_result = self._reason(structure)
        # Phase 3: SCORE
        scored = self._score(candidates, reasoning_result)
        # Phase 4: CALIBRATE
        calibrated = self._calibrate(scored)
        return sorted(alibrated, key=lambda x: x["score"], reverse=True)

    def _extract(self, prompt: str) -> Dict[str, Any]:
        """Extract entities, statements, and relationships from the prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        entities = {}
        statements = []
        relationships = []
        question = lines[-1] if lines else ""
        
        # Extract entity names (capitalized phrases)
        entity_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        for line in lines:
            # Find entities
            found_entities = re.findall(entity_pattern, line)
            for ent in found_entities:
                if ent not in entities and len(ent) > 1:
                    entities[ent] = {"type": "agent", "statements": []}
            
            # Extract statements about intentions or actions
            if "says" in line.lower() or "claims" in line.lower() or "intends" in line.lower():
                statements.append(line)
            
            # Extract relationships (who interacts with whom)
            if "with" in line.lower() or "against" in line.lower() or "versus" in line.lower():
                # Find pairs of entities mentioned together
                ents_in_line = re.findall(entity_pattern, line)
                if len(ents_in_line) >= 2:
                    for i in range(len(ents_in_line)):
                        for j in range(i+1, len(ents_in_line)):
                            relationships.append((ents_in_line[i], ents_in_line[j]))
        
        # Extract numerical values (probabilities, rates)
        numbers = []
        for line in lines:
            num_matches = re.findall(r'(\d+(?:\.\d+)?)%?', line)
            for match in num_matches:
                try:
                    val = float(match)
                    if 0 <= val <= 100:
                        numbers.append(val / 100.0 if val > 1 else val)
                except:
                    pass
        
        return {
            "entities": entities,
            "statements": statements,
            "relationships": list(set(relationships)),
            "question": question,
            "numerical_values": numbers,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply chemical kinetics framework to model strategic deception."""
        entities = structure["entities"]
        relationships = structure["relationships"]
        statements = structure["statements"]
        question = structure["question"]
        
        if not entities:
            return {"answer": "Unknown", "confidence": 0.0, "reasoning": "No entities found"}
        
        # Chemical kinetics analogy: agents as chemical species, deception as reaction pathway
        # Higher deception probability = faster reaction rate away from stated intention
        
        # Build reaction network from relationships
        edges = []
        for rel in relationships:
            edges.append(rel)  # bidirectional interaction
            edges.append((rel[1], rel[0]))
        
        # T1 PRIMITIVE 1: topological_sort to find strategic ordering
        # In kinetics, reaction order matters - who acts first influences outcome
        try:
            sorted_agents = topological_sort(edges)
            if sorted_agents is None:
                # Graph has cycles - use alphabetical as fallback
                sorted_agents = sorted(entities.keys())
        except:
            sorted_agents = sorted(entities.keys())
        
        # Extract deception probabilities from statements
        deception_probs = {}
        for agent in entities.keys():
            # Count deceptive indicators in statements about this agent
            deceptive_indicators = 0
            total_indicators = 0
            
            for stmt in statements:
                if agent.lower() in stmt.lower():
                    total_indicators += 1
                    if any(word in stmt.lower() for word in ["but", "however", "actually", "secretly", "lies", "deceives"]):
                        deceptive_indicators += 1
            
            if total_indicators > 0:
                base_prob = deceptive_indicators / total_indicators
            else:
                base_prob = 0.3  # default suspicion
            
            deception_probs[agent] = base_prob
        
        # Use numerical values from prompt if available
        if structure["numerical_values"]:
            # Distribute numerical values among agents
            for i, agent in enumerate(sorted_agents):
                if i < len(structure["numerical_values"]):
                    # Adjust deception probability with extracted value
                    deception_probs[agent] = (deception_probs[agent] + structure["numerical_values"][i]) / 2.0
        
        # Build Bayesian network for strategic reasoning
        # Nodes: Agent intentions (stated vs actual)
        bn_edges = []
        for agent in entities.keys():
            bn_edges.append((f"{agent}_stated", f"{agent}_actual"))
        
        # Add influence edges based on relationships
        for rel in relationships:
            bn_edges.append((f"{rel[0]}_actual", f"{rel[1]}_actual"))
        
        # AMINO ACID 1: build_bn to model deception dynamics
        try:
            model = build_bn(bn_edges)
            bn_built = True
        except:
            model = None
            bn_built = False
        
        # Calculate deception equilibrium using kinetics analogy
        # Reaction: Stated → Actual, rate = deception probability
        # Equilibrium favors actual intention when deception rate is high
        
        equilibrium_scores = {}
        for agent in entities.keys():
            if bn_built:
                # AMINO ACID 2: conditional_query to estimate actual intention
                try:
                    # Query P(actual=True | stated=True) - lower means more deceptive
                    query_result = conditional_query(
                        model, 
                        [f"{agent}_actual"], 
                        {f"{agent}_stated": True}
                    )
                    if query_result and isinstance(query_result, dict):
                        # Get probability of actual matching stated
                        match_prob = query_result.get(True, 0.5)
                        deception_level = 1.0 - match_prob
                    else:
                        deception_level = deception_probs[agent]
                except:
                    deception_level = deception_probs[agent]
            else:
                deception_level = deception_probs[agent]
            
            # T1 PRIMITIVE 2: entropy to measure uncertainty in agent's behavior
            # High entropy = unpredictable = potentially deceptive
            behavior_probs = [deception_level, 1.0 - deception_level]
            agent_entropy = entropy(behavior_probs)
            
            # T1 PRIMITIVE 3: bayesian_update to incorporate strategic position
            # Agents earlier in topological order have more influence
            try:
                position = sorted_agents.index(agent)
                strategic_weight = 1.0 - (position / max(len(sorted_agents), 1))
            except:
                strategic_weight = 0.5
            
            # Update deception score with strategic position
            updated_score = bayesian_update(
                prior=deception_level,
                likelihood=strategic_weight,
                false_positive=0.1
            )
            
            # Combine with entropy (higher entropy = more deceptive)
            final_score = (updated_score + agent_entropy) / 2.0
            equilibrium_scores[agent] = final_score
        
        # T1 PRIMITIVE 4: confidence_from_agreement on deception scores
        score_values = list(equilibrium_scores.values())
        confidence = confidence_from_agreement(score_values) if score_values else 0.5
        
        # Determine most deceptive agent
        if equilibrium_scores:
            most_deceptive = max(equilibrium_scores.items(), key=lambda x: x[1])
            answer = most_deceptive[0]
        else:
            answer = sorted(entities.keys())[0] if entities else "Unknown"
        
        # AMINO ACID 3: is_uniquely_solvable to check if deception pattern is unambiguous
        # Create constraint satisfaction problem: which agent is deceptive
        variables = list(entities.keys())
        domains = {agent: [True, False] for agent in variables}  # True = deceptive
        
        # Constraints based on relationships
        constraints = []
        for rel in relationships:
            # If A deceives B, then A is deceptive
            def deception_constraint(a_val, b_val, a_name=rel[0], b_name=rel[1]):
                # This is a simplified constraint: if relationship exists, at least one is deceptive
                return a_val or b_val
            
            constraints.append(([rel[0], rel[1]], deception_constraint))
        
        uniqueness_check = False
        try:
            uniqueness_check = is_uniquely_solvable(variables, domains, constraints)
        except:
            pass
        
        # Adjust confidence based on uniqueness
        if not uniqueness_check:
            confidence = confidence * 0.8  # Reduce confidence if multiple solutions possible
        
        return {
            "answer": answer,
            "confidence": min(max(confidence, 0.0), 1.0),
            "reasoning": f"Chemical kinetics analysis: {answer} has highest deception equilibrium score",
            "scores": equilibrium_scores,
            "uniquely_solvable": uniqueness_check
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        scores = []
        
        for candidate in candidates:
            # Primary scoring: exact or partial match of computed answer
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity
                base_score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
            
            # Adjust with confidence from reasoning
            adjusted_score = base_score * reasoning_result["confidence"]
            
            scores.append({
                "candidate": candidate,
                "score": adjusted_score,
                "base_score": base_score
            })
        
        return scores

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper distribution."""
        if not scored:
            return scored
        
        # Simple min-max normalization
        scores = [item["score"] for item in scored]
        if not scores:
            return scored
        
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
        
        if max(ca, cb) == 0:
            return 1.0
        
        return (cab - min(ca, cb)) / max(ca, cb)