import re
import math
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Gauge-Connected Propositional Network with Metacognitive Free Energy Minimization.
    
    Mechanism:
    1. Structural Parsing: Extracts atomic propositions, negations, comparatives, and conditionals.
    2. Gauge Connection: Models logical relations as edges with weights. Belief transport uses 
       sigmoidal activation to simulate parallel transport of confidence.
    3. Free Energy (F): Computed as Complexity (entropy of beliefs) + Accuracy (KL-divergence error 
       between transported beliefs and observed candidate assertions).
    4. Metacognition: Monitors residual errors during belief propagation. If the prompt contains 
       Tier B traps (ambiguity, presupposition), confidence is capped low regardless of score.
    5. Scoring: S = -F. Lower Free Energy = Higher Score.
    """
    
    def __init__(self):
        self.lambda_acc = 1.0  # Weight for accuracy term in Free Energy
        self.eta = 0.1         # Learning rate for metacognitive update
        self.tier_b_triggers = [
            r"\bhave you stopped\b", r"\bwhy did.*fail\b", r"\bwhy did.*stop\b",
            r"\bevery.*a.*\b", r"\btold.*he was\b", r"\btold.*she was\b",
            r"\beither.*or\b", r"\bbest\b", r"\bworst\b", r"\bfavorite\b",
            r"\bwho was it\b", r"\bwhich one\b"
        ]

    def _sigmoid(self, x: float) -> float:
        return 1.0 / (1.0 + math.exp(-x)) if -700 < x < 700 else 0.0 if x < 0 else 1.0

    def _logit(self, p: float) -> float:
        p = max(1e-9, min(1 - 1e-9, p))
        return math.log(p / (1 - p))

    def _kl_div(self, p: float, q: float) -> float:
        """KL(Bern(p) || Bern(q))"""
        if p == 0: return 0.0
        if q == 0 or q == 1: return 1e9 # Penalty for certainty mismatch
        return p * math.log(p/q) + (1-p) * math.log((1-p)/(1-q))

    def _entropy(self, p: float) -> float:
        if p == 0 or p == 1: return 0.0
        return -(p * math.log(p) + (1-p) * math.log(1-p))

    def _meta_confidence(self, text: str) -> float:
        """Check for Tier B traps: ambiguity, presupposition, unanswerability."""
        text_lower = text.lower()
        for pattern in self.tier_b_triggers:
            if re.search(pattern, text_lower):
                return 0.25 # Cap confidence for ambiguous/trap prompts
        if len(text.strip().split()) < 3:
            return 0.3 # Too short to reason about
        return 1.0 # No immediate traps detected

    def _parse_structure(self, text: str) -> List[Dict]:
        """Extract atomic propositions and logical features."""
        nodes = []
        text_lower = text.lower()
        
        # Detect numeric comparisons
        nums = re.findall(r"[-+]?\d*\.?\d+", text)
        for n in nums:
            nodes.append({"type": "numeric", "value": float(n), "c": 0.9})
            
        # Detect negations
        if re.search(r"\b(not|no|never|none)\b", text_lower):
            nodes.append({"type": "negation", "value": 1.0, "c": 0.8})
            
        # Detect conditionals
        if re.search(r"\b(if|then|implies|leads to)\b", text_lower):
            nodes.append({"type": "conditional", "value": 1.0, "c": 0.8})
            
        # Detect comparatives
        if re.search(r"\b(more|less|greater|smaller|before|after)\b", text_lower):
            nodes.append({"type": "comparative", "value": 1.0, "c": 0.8})

        # Default generic node if nothing specific found
        if not nodes:
            nodes.append({"type": "generic", "value": 1.0, "c": 0.5})
            
        return nodes

    def _compute_free_energy(self, prompt_nodes: List[Dict], candidate: str) -> Tuple[float, float]:
        """
        Compute Variational Free Energy F = Complexity + lambda * Accuracy.
        Returns (F, final_confidence).
        """
        # 1. Initialize Network
        # Nodes from prompt
        p_nodes = prompt_nodes.copy()
        # Nodes from candidate (treated as observations with c=1.0)
        c_nodes = self._parse_structure(candidate)
        
        all_nodes = p_nodes + c_nodes
        if not all_nodes:
            return 100.0, 0.1 # High energy, low confidence
            
        # Initialize confidences (c_i) and posteriors (q_i ~ c_i initially)
        c_vals = [n.get("c", 0.5) for n in all_nodes]
        q_vals = c_vals.copy()
        
        # Build adjacency (simplified: fully connected for small N, or logical links)
        # In this implementation, we simulate gauge transport between prompt structure and candidate assertions
        n_total = len(all_nodes)
        total_error = 0.0
        edge_count = 0
        
        # Metacognitive loop: Propagate beliefs
        for _ in range(2): # 2 rounds of propagation
            delta_sum = 0.0
            c_old = c_vals.copy()
            
            for i in range(n_total):
                # Simulate transport from neighbors (simplified to global context for robustness)
                # In a full gauge theory, this would be path-specific. 
                # Here we approximate by checking consistency between prompt features and candidate features.
                
                # If node i is a candidate observation, its target is 1.0 (or its asserted value)
                # If node i is prompt, its target is consistency with the whole.
                
                is_candidate_node = i >= len(p_nodes)
                target_val = 1.0 if is_candidate_node else 0.5 # Candidate asserts truth; Prompt is prior
                
                # Transport from average context (simplified gauge connection)
                context_c = sum(c_vals) / n_total if n_total > 0 else 0.5
                
                # Gauge transport: w_ij represents logical compatibility
                # If types match, w is positive. If negation involved, w flips.
                w_ij = 0.5 
                if all_nodes[i].get("type") == "negation":
                    w_ij = -0.5
                
                # Transported belief
                transported = self._sigmoid(w_ij + self._logit(context_c))
                
                # Prediction Error (KL)
                # Treat candidate assertions as fixed observations
                if is_candidate_node:
                    obs_val = 1.0 # Candidate claims this is true
                    err = self._kl_div(transported, obs_val)
                    total_error += err
                    edge_count += 1
                else:
                    # Prompt internal consistency
                    err = self._kl_div(transported, q_vals[i])
                    total_error += err * 0.5 # Lower weight for internal prompt logic
                    edge_count += 1

                # Metacognitive Update
                delta = abs(transported - c_vals[i])
                delta_sum += delta
                # Precision weighted update
                c_vals[i] = c_vals[i] + self.eta * (delta / (1 + delta))
                c_vals[i] = max(0.01, min(0.99, c_vals[i])) # Clamp
            
            if delta_sum < 1e-4:
                break
                
        # Compute Complexity (Entropy of final posteriors)
        complexity = sum(self._entropy(c) for c in c_vals)
        
        # Average Accuracy Error
        accuracy_err = (total_error / edge_count) if edge_count > 0 else 0.0
        
        F = complexity + self.lambda_acc * accuracy_err
        final_conf = sum(c_vals[len(p_nodes):]) / len(c_nodes) if c_nodes else 0.5
        
        return F, final_conf

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
        z = zlib.compress
        l1 = len(z(s1.encode()))
        l2 = len(z(s2.encode()))
        l12 = len(z((s1 + s2).encode()))
        if min(l1, l2) == 0: return 1.0
        return (l12 - min(l1, l2)) / max(l1, l2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        meta_conf = self._meta_confidence(prompt)
        prompt_nodes = self._parse_structure(prompt)
        results = []
        
        scores = []
        for cand in candidates:
            F, conf_prop = self._compute_free_energy(prompt_nodes, cand)
            # Score is negative Free Energy
            base_score = -F
            
            # NCD Tiebreaker (max 15% influence)
            ncd = self._ncd_score(prompt, cand)
            # Normalize NCD to similar scale (lower is better, so invert)
            ncd_contrib = (1.0 - ncd) * 0.5 
            
            final_score = 0.85 * base_score + 0.15 * ncd_contrib
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"F={F:.4f}, MetaConf={meta_conf:.2f}",
                "raw_conf": conf_prop
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        
        # Apply Metacognitive Cap to Confidence in the reasoning string if needed
        if meta_conf < 0.5:
            for r in results:
                r["reasoning"] += " [WARNING: Ambiguity Detected]"
                
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at 0.3 if Tier B traps are detected.
        Caps at 0.9 unless computation is definitive.
        """
        meta_conf = self._meta_confidence(prompt)
        
        # If prompt is ambiguous/trap, return low confidence immediately
        if meta_conf < 0.5:
            return 0.25
            
        prompt_nodes = self._parse_structure(prompt)
        F, conf_prop = self._compute_free_energy(prompt_nodes, answer)
        
        # Map Free Energy to confidence
        # Low F -> High Conf. F is roughly positive. 
        # Heuristic mapping: conf = 1 / (1 + F)
        calc_conf = 1.0 / (1.0 + F)
        
        # Blend with structural confidence
        final_conf = 0.7 * calc_conf + 0.3 * conf_prop
        
        # Hard caps for epistemic honesty
        if final_conf > 0.9:
            # Only allow >0.9 if numeric/computational nodes were heavily involved
            has_nums = any(n["type"] == "numeric" for n in prompt_nodes)
            if not has_nums:
                final_conf = 0.85 # Cap for non-computational reasoning
                
        return max(0.0, min(1.0, final_conf))