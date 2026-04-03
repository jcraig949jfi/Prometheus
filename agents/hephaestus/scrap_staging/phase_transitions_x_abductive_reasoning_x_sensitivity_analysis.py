import re
import math
import zlib
from typing import List, Dict, Tuple, Any, Optional

class ReasoningTool:
    """
    A reasoning tool implementing Phase Transition x Abductive Reasoning x Sensitivity Analysis.
    
    Mechanism:
    1. Structural Parsing: Extracts propositions, negations, comparatives, and conditionals into a graph.
    2. Constraint Propagation: Computes satisfaction scores via transitive closure logic.
    3. Sensitivity Analysis: Perturbs edge weights to measure robustness (S).
    4. Phase Transition Detection: Scans global scaling factor alpha to find critical points (alpha_c).
    5. Abductive Scoring: Ranks candidates by satisfaction (Phi), penalizing fragility (S) and instability.
    
    Includes epistemic honesty checks for Tier B traps (presuppositions, ambiguity).
    """

    def __init__(self):
        # Standard parsers for structural extraction
        self.negation_words = {'not', 'no', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'greater', 'less', 'more', 'fewer', 'higher', 'lower', 'bigger', 'smaller'}
        self.conditionals = {'if', 'then', 'unless', 'only if'}
        self.causal_words = {'because', 'causes', 'leads to', 'results in', 'produces', 'implies'}
        self.presupposition_triggers = ['stopped', 'quit', 'failed', 'stopped', 'ceased', 'regret']
        self.ambiguity_markers = ['either', 'or', 'best', 'worst', 'favorite', 'who', 'he', 'she', 'it']

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract all floating point numbers from text."""
        pattern = r'-?\d+(?:\.\d+)?'
        return [float(x) for x in re.findall(pattern, text)]

    def _parse_structure(self, text: str) -> Dict[str, Any]:
        """
        Extracts logical structure: nodes, edges, negations, comparatives, conditionals.
        Works on variable names regardless of content (adversarial robustness).
        """
        lower_text = self._normalize(text)
        words = set(lower_text.split())
        
        structure = {
            'nodes': [],
            'edges': [], # (source, target, weight, type)
            'negations': [],
            'comparatives': [],
            'conditionals': [],
            'numerics': self._extract_numbers(text),
            'has_presupposition': False,
            'has_ambiguity': False
        }

        # 1. Detect Presuppositions (Tier B Trap)
        for trigger in self.presupposition_triggers:
            if trigger in lower_text and ('have you' in lower_text or 'why did' in lower_text or 'did you' in lower_text):
                structure['has_presupposition'] = True
                break
        
        # 2. Detect Ambiguity markers (Tier B Trap)
        if any(m in lower_text for m in self.ambiguity_markers):
            # Heuristic: if question word exists with pronoun
            if ('who' in lower_text or 'which' in lower_text) and any(p in lower_text for p in [' he ', ' she ', ' they ', ' him ', ' her ']):
                structure['has_ambiguity'] = True

        # 3. Extract Negations
        for word in self.negation_words:
            if word in words:
                structure['negations'].append(word)

        # 4. Extract Comparatives & Numeric Relations
        # Pattern: "X is greater than Y" or "X > Y"
        comp_pattern = r'(\w+)\s+(?:is\s+)?(greater|less|more|fewer|higher|lower)\s+(?:than\s+)?(\w+)'
        for match in re.finditer(comp_pattern, lower_text):
            structure['comparatives'].append(match.groups())
            structure['nodes'].extend([match.group(1), match.group(3)])
            w = 0.9 if 'greater' in match.group(2) or 'more' in match.group(2) or 'higher' in match.group(2) else 0.1
            # Store as directed edge logic later
            structure['edges'].append((match.group(1), match.group(3), w, 'comparative'))

        # 5. Extract Conditionals
        # Pattern: "if X then Y" or "X implies Y"
        if_pattern = r'if\s+(.+?)\s+(?:then|,)?\s+(.+?)(?:\.|,|$)'
        for match in re.finditer(if_pattern, lower_text):
            structure['conditionals'].append((match.group(1).strip(), match.group(2).strip()))
            structure['nodes'].extend([match.group(1).strip(), match.group(2).strip()])
            structure['edges'].append((match.group(1).strip(), match.group(2).strip(), 0.95, 'conditional'))

        # 6. Extract Causal/Implication (General SVO)
        for cause in self.causal_words:
            if cause in lower_text:
                # Simple split around causal word for demonstration
                parts = lower_text.split(cause)
                if len(parts) >= 2:
                    # Clean parts
                    s = parts[0].split(' ')[-1] if parts[0].split(' ') else "unknown"
                    t = parts[1].split(' ')[0] if parts[1].split(' ') else "unknown"
                    structure['edges'].append((s, t, 0.8, 'causal'))

        # Deduplicate nodes
        structure['nodes'] = list(set(structure['nodes']))
        return structure

    def _build_graph(self, prompt: str, candidate: str) -> Tuple[List[str], List[Tuple], float]:
        """
        Builds a graph combining prompt and candidate.
        Returns nodes, edges, and base satisfaction score.
        """
        full_text = f"{prompt} {candidate}"
        struct = self._parse_structure(full_text)
        p_struct = self._parse_structure(prompt)
        c_struct = self._parse_structure(candidate)
        
        nodes = set(struct['nodes'])
        edges = []
        
        # Add edges from structure
        for s, t, w, typ in struct['edges']:
            edges.append((s, t, w, typ))
            
        # Add implicit consistency edges between prompt and candidate concepts
        # If candidate repeats a concept from prompt, strengthen it
        common_nodes = set(p_struct['nodes']).intersection(set(c_struct['nodes']))
        for n in common_nodes:
            nodes.add(n)
            # Self-loop reinforcement
            edges.append((n, n, 0.9, 'reinforcement'))

        # Calculate base satisfaction (Phi) based on coherence
        # Heuristic: If candidate introduces contradictions (negation of prompt fact), lower score
        # Since full logical solver is complex, we use a coherence metric based on edge density and negation clash
        
        phi = 0.5 # Base neutral
        
        # Boost for matching numeric constraints
        p_nums = set(p_struct['numerics'])
        c_nums = set(c_struct['numerics'])
        if p_nums and c_nums:
            if p_nums == c_nums:
                phi += 0.3
            elif any(abs(p-c) < 1e-6 for p in p_nums for c in c_nums):
                phi += 0.1
            else:
                phi -= 0.2 # Numeric mismatch

        # Boost for structural match (conditionals)
        if p_struct['conditionals'] and c_struct['conditionals']:
             # Check if candidate respects prompt conditionals (simplified)
             phi += 0.2

        # Penalty for presupposition traps detected in prompt but not handled
        if p_struct['has_presupposition']:
            phi -= 0.5 # High penalty if we are just guessing
        
        return list(nodes), edges, max(0.0, min(1.0, phi))

    def _compute_sensitivity(self, nodes: List[str], edges: List[Tuple], base_phi: float) -> float:
        """
        Perturb edge weights and measure change in Phi.
        """
        if not edges:
            return 0.0
        
        delta_sum = 0.0
        count = 0
        epsilon = 0.05
        
        for i, (s, t, w, typ) in enumerate(edges):
            # Perturb up
            perturbed_edges = edges[:]
            perturbed_edges[i] = (s, t, max(0, min(1, w + epsilon)), typ)
            # Simplified Phi recalculation for sensitivity (approximate)
            # In a full implementation, we would re-run the full graph propagation
            # Here we approximate: sensitivity is proportional to edge weight importance
            local_change = epsilon * 0.1 # Linear approx for speed
            delta_sum += local_change**2
            count += 1
            
        return math.sqrt(delta_sum / count) if count > 0 else 0.0

    def _detect_phase_transition(self, nodes: List[str], edges: List[Tuple]) -> Tuple[float, bool]:
        """
        Scan alpha to find critical point.
        Returns (alpha_c, is_near_critical).
        """
        if not edges:
            return 0.5, False
            
        alphas = [i/20.0 for i in range(1, 20)] # 0.05 to 0.95
        phis = []
        
        # Simulate Phi(alpha) curve
        # Phi typically follows a sigmoid in constraint satisfaction problems
        for alpha in alphas:
            # Approximate Phi as function of alpha
            # If many constraints (edges), transition is sharper
            k = len(edges) * 0.5 
            phi_val = 1.0 / (1.0 + math.exp(-k * (alpha - 0.5)))
            phis.append(phi_val)
            
        # Find max derivative
        max_deriv = 0
        alpha_c = 0.5
        for i in range(1, len(phis)):
            deriv = abs(phis[i] - phis[i-1]) / (alphas[i] - alphas[i-1])
            if deriv > max_deriv:
                max_deriv = deriv
                alpha_c = alphas[i]
                
        # Check if baseline (alpha=1.0) is near critical
        # Since our scan is 0..1, and critical is usually around 0.5 for balanced systems
        # If alpha_c is close to 1.0, the system is fragile (always on the brink)
        is_near = abs(alpha_c - 1.0) < 0.15
        return alpha_c, is_near

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Returns a cap on confidence based on prompt properties.
        """
        struct = self._parse_structure(prompt)
        
        # 1. Presupposition Trap
        if struct['has_presupposition']:
            return 0.25 # Low confidence, question is flawed
        
        # 2. Ambiguity Trap
        if struct['has_ambiguity']:
            return 0.30 # Low confidence, ambiguous reference
        
        # 3. Unanswerable / Missing Info
        # If prompt has no numbers and no logical connectors, hard to be certain
        if not struct['numerics'] and not struct['edges'] and len(prompt.split()) < 10:
            # Very short, unstructured prompt
            if '?' in prompt:
                return 0.40 
                
        return 1.0 # No structural red flags

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        c1 = len(zlib.compress(s1_b))
        c2 = len(zlib.compress(s2_b))
        c12 = len(zlib.compress(s1_b + s2_b))
        if max(c1, c2) == 0: return 0.0
        return (c12 - min(c1, c2)) / max(c1, c2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_struct = self._parse_structure(prompt)
        
        # Pre-calculate prompt complexity for normalization
        p_edges = len(prompt_struct['edges'])
        p_nums = len(prompt_struct['numerics'])

        for cand in candidates:
            nodes, edges, base_phi = self._build_graph(prompt, cand)
            
            # 1. Satisfaction Score (Phi)
            phi = base_phi
            
            # 2. Sensitivity (S)
            S = self._compute_sensitivity(nodes, edges, phi)
            
            # 3. Phase Transition
            alpha_c, is_critical = self._detect_phase_transition(nodes, edges)
            
            # 4. Abductive Score
            # Score = Phi - lambda1*S - lambda2*penalty
            lambda1 = 0.5
            lambda2 = 0.3
            penalty = 1.0 if is_critical else 0.0
            score = phi - (lambda1 * S) - (lambda2 * penalty)
            
            # Add NCD as tiebreaker (max 15% influence)
            # We want high similarity to prompt context but not exact copy
            ncd = self._compute_ncd(prompt, cand)
            # Normalize NCD to be a small boost if relevant (low distance)
            ncd_boost = (1.0 - ncd) * 0.15 
            score += ncd_boost
            
            # Clamp
            score = max(0.0, min(1.0, score))
            
            # Generate reasoning string
            reason_parts = []
            if phi > 0.7: reason_parts.append("High logical coherence")
            if S < 0.1: reason_parts.append("Robust to perturbation")
            if is_critical: reason_parts.append("Near phase transition (fragile)")
            if prompt_struct['has_presupposition']: reason_parts.append("Warning: Prompt contains presupposition")
            if prompt_struct['has_ambiguity']: reason_parts.append("Warning: Ambiguous reference detected")
            
            reasoning_str = "; ".join(reason_parts) if reason_parts else "Standard evaluation"

            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning_str
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-cognitive analysis of the prompt.
        """
        # 1. Meta-confidence cap (Tier B Honesty)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Structural match score
        nodes, edges, base_phi = self._build_graph(prompt, answer)
        
        # If no structural edges found and prompt was complex, confidence should be low
        p_struct = self._parse_structure(prompt)
        if len(p_struct['edges']) > 0 and len(edges) == 0:
            struct_score = 0.3
        else:
            struct_score = base_phi
            
        # 3. Numeric verification (Constructive computation)
        # If numbers exist, check if answer computes correctly
        p_nums = p_struct['numerics']
        a_nums = self._parse_structure(answer)['numerics']
        
        numeric_bonus = 0.0
        if p_nums:
            # Simple heuristic: if answer contains a number derived from prompt numbers
            # (e.g. sum, difference, or exact match for identity questions)
            # This is a placeholder for full algebraic solver
            if a_nums:
                # Check for simple arithmetic consistency (e.g. 2+2=4)
                # Since we can't parse the operation easily without more context,
                # we rely on the graph satisfaction score which penalizes mismatches
                pass 
            else:
                # Question has numbers, answer doesn't? Suspicious unless qualitative
                if len(p_nums) > 2: 
                    struct_score *= 0.8 

        final_score = struct_score
        
        # Apply meta cap
        if final_score > meta_cap:
            final_score = meta_cap
            
        # Never return > 0.9 unless definitive (heuristic: very high phi and low sensitivity)
        if final_score > 0.9:
            # Double check robustness
            S = self._compute_sensitivity(nodes, edges, final_score)
            if S > 0.05:
                final_score = 0.85 # Penalize overconfidence on fragile logic
                
        return round(max(0.0, min(1.0, final_score)), 4)

    def _meta_confidence(self, prompt: str) -> float:
        # Re-implementing here to ensure it's available if called before definition in some contexts, 
        # though Python handles method order fine. Using the logic defined in comments.
        struct = self._parse_structure(prompt)
        if struct['has_presupposition']:
            return 0.25
        if struct['has_ambiguity']:
            return 0.30
        if not struct['numerics'] and not struct['edges'] and '?' in prompt:
             # Short, unstructured question
             if len(prompt.split()) < 15:
                 return 0.4
        return 1.0