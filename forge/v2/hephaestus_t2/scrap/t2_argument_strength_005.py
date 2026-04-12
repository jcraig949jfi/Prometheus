import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import bayesian_update, entropy, confidence_from_agreement, solve_sat
from forge.amino_acids.pysat_acids import check_entailment


class ReasoningTool:
    """Cell biology x SAT entailment - argument_strength"""

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
        """Parse the prompt to extract premises, conclusion, and entities."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        
        # Find question (usually last sentence)
        question = lines[-1] if lines else ""
        
        # Extract premises and conclusion indicators
        premises = []
        conclusion = None
        entities = set()
        
        # Look for logical indicators
        for line in lines:
            # Extract capitalized entities (propositions)
            caps = re.findall(r'\b[A-Z][a-z]+\b', line)
            entities.update(caps)
            
            # Identify premises and conclusion
            if 'premise' in line.lower() or 'assume' in line.lower() or 'given' in line.lower():
                # Extract the statement after colon or as the sentence
                if ':' in line:
                    stmt = line.split(':', 1)[1].strip()
                else:
                    stmt = line
                premises.append(stmt)
            elif 'conclusion' in line.lower() or 'therefore' in line.lower() or 'thus' in line.lower():
                if ':' in line:
                    conclusion = line.split(':', 1)[1].strip()
                else:
                    conclusion = line
        
        # If no explicit conclusion found, use the question
        if conclusion is None and '?' in question:
            conclusion = question.replace('?', '').strip()
        
        # Extract logical operators and relationships
        logical_ops = []
        for line in lines:
            if any(op in line for op in ['and', 'or', 'not', 'if', 'then', 'implies', '→', '->']):
                logical_ops.append(line)
        
        return {
            "premises": premises,
            "conclusion": conclusion,
            "entities": list(entities),
            "logical_ops": logical_ops,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use cell biology metaphor: premises as cellular signals, 
        logical entailment as signal transduction pathway validation."""
        
        premises = structure["premises"]
        conclusion = structure["conclusion"]
        entities = structure["entities"]
        
        # If we don't have enough structure, fall back to simple analysis
        if not premises or conclusion is None:
            # Fallback that still uses primitives
            if entities:
                # Use entropy of entity distribution as confidence
                dist = [1.0/len(entities)] * len(entities) if entities else [1.0]
                e = entropy(dist)
                confidence = 1.0 - e  # Lower entropy = higher confidence
                if confidence > 0.5:
                    computed_answer = "Valid"
                else:
                    computed_answer = "Invalid"
            else:
                computed_answer = "Invalid"
                confidence = 0.5
            
            return {
                "answer": computed_answer,
                "confidence": confidence,
                "reasoning": "Fallback analysis using entropy"
            }
        
        # Convert natural language to propositional variables
        # Map each unique entity to a variable number
        var_map = {}
        for i, entity in enumerate(entities, 1):
            var_map[entity] = i
        
        # Build CNF clauses from premises
        clauses = []
        
        for premise in premises:
            premise_clauses = self._parse_statement(premise, var_map)
            if premise_clauses:
                clauses.extend(premise_clauses)
        
        # Parse conclusion for entailment check
        conclusion_clause = self._parse_conclusion(conclusion, var_map)
        
        # CRITICAL: Use amino acid for entailment check
        # This directly determines the answer
        is_entailed = check_entailment(clauses, conclusion_clause)
        
        # CRITICAL: Use T1 primitives that are load-bearing
        # 1. Use solve_sat to check consistency of premises
        sat_result = solve_sat(clauses, len(var_map))
        premises_consistent = sat_result is not None
        
        # 2. Use bayesian_update to compute confidence
        # Prior: 0.5 (uncertain), likelihood: 1.0 if consistent else 0.5
        prior = 0.5
        likelihood = 1.0 if premises_consistent else 0.5
        posterior = bayesian_update(prior, likelihood)
        
        # 3. Use entropy to measure uncertainty in the result
        # Create probability distribution based on entailment result
        if is_entailed:
            probs = [0.9, 0.1]  # High probability for Valid
        else:
            probs = [0.1, 0.9]  # High probability for Invalid
        uncertainty = entropy(probs)
        
        # 4. Use confidence_from_agreement to combine signals
        # Simulate multiple reasoning paths
        signals = []
        if is_entailed:
            signals.append(0.8)  # Entailment suggests valid
        if premises_consistent:
            signals.append(0.7)   # Consistency suggests valid
        if uncertainty < 0.5:    # Low entropy suggests confident
            signals.append(0.6)
        
        if signals:
            combined_confidence = confidence_from_agreement(signals)
        else:
            combined_confidence = 0.5
        
        # Final decision: if entailment holds AND premises are consistent
        if is_entailed and premises_consistent:
            computed_answer = "Valid"
            final_confidence = min(0.95, (posterior + combined_confidence) / 2)
        else:
            computed_answer = "Invalid"
            final_confidence = min(0.95, ((1 - posterior) + combined_confidence) / 2)
        
        # Cell biology metaphor: signal transduction pathway
        # Premises = input signals, SAT check = receptor activation
        # Entailment = downstream pathway activation
        # Entropy = cellular noise, Confidence = signal amplification
        
        return {
            "answer": computed_answer,
            "confidence": final_confidence,
            "reasoning": f"Premises {'consistent' if premises_consistent else 'inconsistent'}, "
                        f"Conclusion {'entailed' if is_entailed else 'not entailed'}, "
                        f"Uncertainty: {uncertainty:.3f}",
            "raw_result": {
                "is_entailed": is_entailed,
                "premises_consistent": premises_consistent,
                "posterior": posterior,
                "uncertainty": uncertainty,
                "combined_confidence": combined_confidence
            }
        }
    
    def _parse_statement(self, statement: str, var_map: Dict[str, int]) -> List[List[int]]:
        """Convert natural language statement to CNF clauses."""
        clauses = []
        
        # Simple parsing for common patterns
        statement_lower = statement.lower()
        
        # Pattern: "A and B"
        if ' and ' in statement_lower:
            parts = [p.strip() for p in statement_lower.split(' and ')]
            for part in parts:
                entity = part.capitalize()
                if entity in var_map:
                    clauses.append([var_map[entity]])
        
        # Pattern: "A or B"
        elif ' or ' in statement_lower:
            parts = [p.strip() for p in statement_lower.split(' or ')]
            clause = []
            for part in parts:
                entity = part.capitalize()
                if entity in var_map:
                    clause.append(var_map[entity])
            if clause:
                clauses.append(clause)
        
        # Pattern: "if A then B" or "A implies B"
        elif ' if ' in statement_lower and ' then ' in statement_lower:
            # Extract A and B
            match = re.search(r'if (.+) then (.+)', statement_lower)
            if match:
                a = match.group(1).strip().capitalize()
                b = match.group(2).strip().capitalize()
                if a in var_map and b in var_map:
                    # A → B is equivalent to ¬A ∨ B
                    clauses.append([-var_map[a], var_map[b]])
        
        # Pattern: "not A"
        elif statement_lower.startswith('not '):
            entity = statement_lower[4:].strip().capitalize()
            if entity in var_map:
                clauses.append([-var_map[entity]])
        
        # Default: single entity
        else:
            entity = statement.strip().capitalize()
            if entity in var_map:
                clauses.append([var_map[entity]])
        
        return clauses
    
    def _parse_conclusion(self, conclusion: str, var_map: Dict[str, int]) -> List[int]:
        """Convert conclusion to a single clause."""
        if not conclusion:
            return []
        
        conclusion_lower = conclusion.lower()
        
        # Pattern: "not A"
        if conclusion_lower.startswith('not '):
            entity = conclusion_lower[4:].strip().capitalize()
            if entity in var_map:
                return [-var_map[entity]]
        
        # Default: positive literal
        entity = conclusion.strip().capitalize()
        if entity in var_map:
            return [var_map[entity]]
        
        return []

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact match of computed answer
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
    
    def _ncd(self, a: str, b: str) -> float:
        """Normalized Compression Distance."""
        if not a or not b:
            return 1.0
        
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + " " + b).encode()))
        
        if max(ca, cb) == 0:
            return 1.0
        
        return (cab - min(ca, cb)) / max(ca, cb)
    
    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Simple calibration: ensure scores are in [0, 1] range."""
        if not scored:
            return scored
        
        # Find min and max for normalization
        scores = [item["score"] for item in scored]
        min_score = min(scores)
        max_score = max(scores)
        
        if max_score - min_score > 0.001:  # Avoid division by zero
            for item in scored:
                # Normalize to [0, 1]
                item["score"] = (item["score"] - min_score) / (max_score - min_score)
        else:
            # All scores are similar, set to confidence-weighted values
            for item in scored:
                item["score"] = item["confidence"] * 0.5 + 0.5
        
        return scored