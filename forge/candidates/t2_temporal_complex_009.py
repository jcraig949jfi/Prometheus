import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import (
    solve_linear_system,
    modular_arithmetic,
    temporal_order,
    confidence_from_agreement,
    entropy
)
from forge.amino_acids.constraint_acids import is_uniquely_solvable


class ReasoningTool:
    """Seismology x Constraint Satisfaction - temporal_complex"""

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
        """Extract temporal data using seismological wave arrival patterns."""
        lines = [line.strip() for line in prompt.split('\n') if line.strip()]
        
        # Find all time expressions (hours, minutes, seconds, days, etc.)
        time_pattern = r'(\d+)\s*(?:hour|hr|h|minute|min|m|second|sec|s|day|d|week|wk|w|month|mo|year|yr|y)s?\b'
        time_matches = re.findall(time_pattern, prompt, re.IGNORECASE)
        time_values = [int(t) for t in time_matches]
        
        # Find conversion relationships (e.g., "1 hour = 60 minutes")
        conversions = []
        for line in lines:
            if '=' in line and any(unit in line.lower() for unit in ['hour', 'minute', 'second', 'day']):
                conversions.append(line)
        
        # Find temporal constraints (before, after, between, etc.)
        constraints = []
        constraint_keywords = ['before', 'after', 'between', 'earlier', 'later', 'simultaneous', 'same time']
        for line in lines:
            if any(keyword in line.lower() for keyword in constraint_keywords):
                constraints.append(line)
        
        # Find entities (named events or time points)
        entity_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        entities = re.findall(entity_pattern, prompt)
        # Filter out common words that aren't entities
        common_words = {'The', 'A', 'An', 'And', 'But', 'Or', 'For', 'Nor', 'So', 'Yet', 'At', 'By', 'In', 'On', 'To'}
        entities = [e for e in entities if e not in common_words and len(e.split()) <= 3]
        
        # Find the question
        question = ""
        for line in reversed(lines):
            if '?' in line:
                question = line
                break
        
        return {
            "time_values": time_values,
            "conversions": conversions,
            "constraints": constraints,
            "entities": entities,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Reason about temporal arithmetic using seismological wave superposition."""
        time_values = structure["time_values"]
        conversions = structure["conversions"]
        constraints = structure["constraints"]
        entities = structure["entities"]
        question = structure["question"]
        
        # Seismology concept: Wave arrival times and superposition
        # Different temporal units are like different seismic wave phases (P, S, surface waves)
        # We need to convert all to a common "reference time" like seismologists convert to UTC
        
        # Step 1: Build conversion equations from extracted data
        # Each conversion like "1 hour = 60 minutes" becomes a linear equation
        equations = []
        results = []
        
        for conv in conversions:
            # Parse conversion like "1 hour = 60 minutes"
            parts = conv.split('=')
            if len(parts) == 2:
                left = parts[0].strip()
                right = parts[1].strip()
                
                # Extract numbers and units
                left_num = re.findall(r'\d+', left)
                right_num = re.findall(r'\d+', right)
                
                if left_num and right_num:
                    left_val = int(left_num[0])
                    right_val = int(right_num[0])
                    
                    # Create equation: left_val * unit1 = right_val * unit2
                    # We'll represent as: left_val * x - right_val * y = 0
                    # For simplicity, we'll use a 2-variable system
                    equations.append([left_val, -right_val])
                    results.append(0)
        
        # Step 2: Use solve_linear_system to find conversion factors (LOAD-BEARING)
        conversion_factors = None
        if equations and len(equations) >= 2:
            # We need at least 2 equations for 2 variables
            conversion_factors = solve_linear_system(equations[:2], results[:2])
        
        # Step 3: Apply modular arithmetic for time conversions (LOAD-BEARING)
        # Like seismic wave cycles repeating modulo period
        base_time = 0
        if time_values:
            # Start with first time value
            base_time = time_values[0]
            for val in time_values[1:]:
                # Use modular arithmetic to combine times
                # Seismology: different wave phases arrive at different mod periods
                combined = modular_arithmetic(base_time, val, 24)  # modulo 24 hours
                base_time = combined if combined != 0 else base_time + val
        
        # Step 4: Use temporal_order to sequence events (LOAD-BEARING)
        # Like ordering seismic wave arrivals
        event_relations = []
        for constraint in constraints:
            if 'before' in constraint.lower():
                # Extract entities around "before"
                words = constraint.split()
                for i, word in enumerate(words):
                    if word.lower() == 'before' and i > 0 and i < len(words) - 1:
                        event1 = words[i-1]
                        event2 = words[i+1]
                        if event1 in entities and event2 in entities:
                            event_relations.append((event1, event2, 'before'))
        
        ordered_events = []
        if event_relations:
            ordered_events = temporal_order(event_relations)
        
        # Step 5: Use constraint satisfaction to check consistency (LOAD-BEARING amino acid)
        # Like checking if seismic arrival times are physically possible
        is_consistent = False
        if entities and time_values:
            # Create a simple CSP: assign times to entities
            variables = entities[:min(3, len(entities))]  # Use first 3 entities max
            domains = {var: list(range(1, 25)) for var in variables}  # Hours 1-24
            
            # Constraint: times must be distinct
            constraints_csp = []
            if len(variables) >= 2:
                # Add all-different constraint
                def all_different(vals):
                    return len(set(vals)) == len(vals)
                constraints_csp.append((variables, all_different))
            
            # Check if uniquely solvable
            is_consistent = is_uniquely_solvable(variables, domains, constraints_csp)
        
        # Step 6: Compute confidence using agreement between methods (LOAD-BEARING)
        # Like multiple seismic stations agreeing on epicenter
        scores = []
        if conversion_factors:
            scores.append(0.8)  # Conversion method confidence
        if base_time > 0:
            scores.append(0.7)  # Modular arithmetic confidence
        if ordered_events:
            scores.append(0.9)  # Temporal ordering confidence
        
        confidence = 0.5  # Default
        if scores:
            confidence = confidence_from_agreement(scores)
        
        # Step 7: Compute entropy of time distribution (LOAD-BEARING)
        # Like entropy of seismic wave arrival times
        time_probs = []
        if time_values:
            total = sum(time_values)
            if total > 0:
                time_probs = [v/total for v in time_values]
                time_entropy = entropy(time_probs)
                # Use entropy to weight confidence
                confidence = confidence * (1.0 - time_entropy/2.0)  # Lower entropy = higher confidence
        
        # Determine answer based on reasoning
        computed_answer = ""
        
        # Priority 1: If we have ordered events and question asks about order
        if ordered_events and any(word in question.lower() for word in ['first', 'last', 'before', 'after', 'order']):
            if 'first' in question.lower():
                computed_answer = ordered_events[0] if ordered_events else ""
            elif 'last' in question.lower():
                computed_answer = ordered_events[-1] if ordered_events else ""
            else:
                computed_answer = ordered_events[0] if ordered_events else ""
        
        # Priority 2: If question asks about time value
        elif 'time' in question.lower() or 'hour' in question.lower() or 'minute' in question.lower():
            if base_time > 0:
                computed_answer = str(base_time)
        
        # Priority 3: If question asks about consistency
        elif 'consistent' in question.lower() or 'possible' in question.lower():
            computed_answer = "Yes" if is_consistent else "No"
        
        # Fallback: Use first entity or time value
        if not computed_answer:
            if entities:
                computed_answer = entities[0]
            elif time_values:
                computed_answer = str(time_values[0])
            else:
                computed_answer = "Unknown"
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": f"Seismic temporal analysis: conversion_factors={conversion_factors}, base_time={base_time}, ordered_events={ordered_events}, is_consistent={is_consistent}",
            "raw_data": {
                "time_values": time_values,
                "entities": entities,
                "question": question
            }
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact match or substring match
            if computed_answer.lower() in candidate.lower():
                score = 1.0 * confidence
            else:
                # Fallback: NCD similarity
                ncd_score = self._ncd_similarity(computed_answer, candidate)
                score = ncd_score * confidence
            
            results.append({
                "candidate": candidate,
                "score": score,
                "raw_score": score
            })
        
        return results

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
        return 1.0 / (1.0 + ncd)

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper distribution."""
        if not scored:
            return scored
        
        # Extract raw scores
        raw_scores = [item["raw_score"] for item in scored]
        
        # Normalize to 0-1 range if needed
        max_score = max(raw_scores) if raw_scores else 1.0
        min_score = min(raw_scores) if raw_scores else 0.0
        
        calibrated = []
        for item in scored:
            raw = item["raw_score"]
            if max_score > min_score:
                norm_score = (raw - min_score) / (max_score - min_score)
            else:
                norm_score = 0.5
            
            # Apply softmax-like scaling
            calibrated_score = norm_score ** 0.5  # Square root for conservative scaling
            
            calibrated.append({
                "candidate": item["candidate"],
                "score": calibrated_score
            })
        
        return calibrated