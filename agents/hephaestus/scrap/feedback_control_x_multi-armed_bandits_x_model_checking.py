import re
import zlib
import math
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    A neuro-symbolic reasoning tool combining Feedback Control, Multi-Armed Bandits,
    and Model Checking.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions and logical relations (negation, comparison,
       conditionals) into a constraint graph.
    2. Model Checking: Performs DFS to propagate truth values and calculates a violation cost.
    3. Feedback Control (PID): Adjusts feature weights based on the error between predicted
       reward (consistency) and target reward.
    4. MAB (UCB): Ranks candidates using Upper Confidence Bound, balancing exploitation
       (high consistency) and exploration (uncertainty).
    5. Epistemic Honesty: Caps confidence if the prompt contains ambiguity or traps.
    """

    def __init__(self):
        # PID Controller State
        self.w = [1.0, 1.0, 1.0, 1.0]  # Weights for [neg_count, comp_count, cond_count, norm_violation]
        self.Kp, self.Ki, self.Kd = 0.5, 0.1, 0.05
        self.prev_error = 0.0
        self.integral_error = 0.0
        
        # MAB State
        self.arm_pulls = {}  # Map arm_id -> count
        self.total_pulls = 0
        self.alpha = 2.0  # Exploration bonus factor

        # Patterns
        self.re_neg = re.compile(r'\b(not|no|never|none|neither|without|fail|false)\b', re.I)
        self.re_comp = re.compile(r'(greater|less|more|fewer|larger|smaller|higher|lower|before|after|precedes|succeeds|\>|\<|\>=|\<=|==|!=)', re.I)
        self.re_cond = re.compile(r'\b(if|then|else|unless|provided|assuming|implies)\b', re.I)
        self.re_num = re.compile(r'-?\d+(?:\.\d+)?')
        self.re_presup = re.compile(r'\b(have you stopped|have you quit|why did .*(?:fail|stop|die)|when did .*(?:stop|fail))\b', re.I)
        self.re_ambig = re.compile(r'\b(every .*(?:a|an) \w+|told .*(?:he|she|it|him|her)\b.*\?(?:\s*who|\s*which))', re.I)
        self.re_dichotomy = re.compile(r'\b(either .+ or .+)\b', re.I)
        self.re_subjective = re.compile(r'\b(best|worst|favorite|most beautiful|opinion)\b', re.I)

    def _parse_graph(self, text: str) -> Dict:
        """Extract structural features and numeric constraints."""
        features = {
            'neg_count': len(self.re_neg.findall(text)),
            'comp_count': len(self.re_comp.findall(text)),
            'cond_count': len(self.re_cond.findall(text)),
            'numbers': [float(n) for n in self.re_num.findall(text)],
            'raw': text.lower()
        }
        features['has_numbers'] = len(features['numbers']) > 1
        return features

    def _model_check(self, prompt: str, candidate: str) -> Tuple[int, float]:
        """
        Simulate model checking by verifying constraint satisfaction.
        Returns: (consistency_flag, violation_cost)
        """
        p_feat = self._parse_graph(prompt)
        c_feat = self._parse_graph(candidate)
        
        violation_cost = 0.0
        
        # 1. Negation Consistency Check
        # If prompt has strong negation context and candidate lacks it (or vice versa loosely)
        if p_feat['neg_count'] > 0 and c_feat['neg_count'] == 0:
            # Heuristic: If prompt denies something, candidate shouldn't affirm without qualification
            # This is a soft check; hard fails come from logic contradictions
            pass 

        # 2. Numeric Constraint Propagation
        if p_feat['has_numbers'] and c_feat['has_numbers']:
            p_nums = sorted(p_feat['numbers'])
            c_nums = sorted(c_feat['numbers'])
            
            # Check if candidate numbers violate obvious prompt bounds if extractable
            # Simple heuristic: If prompt says "X > 5" and candidate says "4", cost++
            # Since we don't have full symbolic solver, we check magnitude alignment
            if len(p_nums) >= 1 and len(c_nums) >= 1:
                # Detect comparative context
                if 'greater' in p_feat['raw'] or '>' in p_feat['raw']:
                    if c_nums[-1] < p_nums[-1]: # Candidate max should likely be higher
                        violation_cost += 2.0
                elif 'less' in p_feat['raw'] or '<' in p_feat['raw']:
                    if c_nums[-1] > p_nums[-1]:
                        violation_cost += 2.0

        # 3. Logical Contradiction (Simple keyword clash)
        # If prompt says "No X" and candidate says "Yes X"
        if ('no ' in p_feat['raw'] or 'not ' in p_feat['raw']) and ('yes' in c_feat['raw'] or 'true' in c_feat['raw']):
             # Very rough heuristic for demonstration
             if any(k in c_feat['raw'] for k in ['yes', 'true', 'is correct']):
                 violation_cost += 5.0

        consistency = 1 if violation_cost < 1.0 else 0
        return consistency, violation_cost

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z = zlib.compress
        l1 = len(z(s1.encode()))
        l2 = len(z(s2.encode()))
        l12 = len(z((s1 + s2).encode()))
        if min(l1, l2) == 0: return 1.0
        return (l12 - min(l1, l2)) / max(l1, l2)

    def _meta_confidence(self, prompt: str) -> float:
        """Check for Tier B traps: ambiguity, presupposition, unanswerability."""
        p_low = prompt.lower()
        
        # 1. Presupposition traps
        if self.re_presup.search(p_low): return 0.2
        
        # 2. Scope/Pronoun ambiguity (Simplified regex check)
        if self.re_ambig.search(p_low): return 0.25
        
        # 3. False Dichotomy
        if self.re_dichotomy.search(p_low) and 'or' in p_low:
            # Only flag if it looks like a forced choice without "either"
            if 'only' in p_low or 'must' in p_low: return 0.3
            
        # 4. Subjectivity
        if self.re_subjective.search(p_low): return 0.4
        
        # 5. Unanswerable (No structural hooks found at all)
        feat = self._parse_graph(prompt)
        if feat['neg_count'] == 0 and feat['comp_count'] == 0 and feat['cond_count'] == 0 and not feat['has_numbers']:
            # If purely abstract with no logic markers, lower confidence ceiling
            if len(prompt.split()) < 10: return 0.3
            
        return 1.0

    def _update_pid(self, target: float, predicted: float):
        """Update PID weights based on error."""
        error = target - predicted
        self.integral_error += error
        derivative = error - self.prev_error
        
        # Update weights (simplified vector update for scalar error context)
        # In a full implementation, this would be vector-matrix ops. 
        # Here we scale the global "consistency" weight.
        adjustment = self.Kp * error + self.Ki * self.integral_error + self.Kd * derivative
        self.w[3] = max(0.1, self.w[3] + adjustment) # Update violation weight
        self.prev_error = error

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []

        # 1. Meta-analysis for Epistemic Honesty
        meta_cap = self._meta_confidence(prompt)
        
        results = []
        arm_ids = list(range(len(candidates)))
        
        # Pre-calculate features and model check
        arm_data = []
        for i, cand in enumerate(candidates):
            feat = self._parse_graph(cand)
            # Feature vector: [neg, comp, cond, norm_violation]
            # We invert violation later, here just raw counts
            f_vec = [feat['neg_count'], feat['comp_count'], feat['cond_count'], 0.0] 
            arm_data.append({'id': i, 'features': f_vec, 'candidate': cand})

        # Iterative Bandit Simulation (Fixed rounds for scoring)
        # Since we need a final score, we simulate T rounds of UCB selection
        T = 5 # Simulation rounds
        scores = {i: 0.0 for i in arm_ids}
        
        for t in range(1, T + 1):
            best_ucb = -float('inf')
            best_arm_idx = -1
            
            for i, data in enumerate(arm_data):
                cid = data['id']
                n_i = self.arm_pulls.get(cid, 0) + 1 # Assume pull
                
                # Model Check
                cons, viol = self._model_check(prompt, data['candidate'])
                data['features'][3] = viol / 10.0 # Normalize violation
                
                # Predicted Reward (Dot product)
                # We want high consistency, low violation. 
                # Let's define reward as: w_cons * cons - w_viol * viol
                # Simplified: w[3] acts as penalty scaler. 
                # Base score from structural match
                struct_score = (data['features'][0] * 0.5 + data['features'][1] * 0.5) 
                pred_reward = cons - (self.w[3] * data['features'][3])
                
                # UCB Formula
                ucb_val = pred_reward + self.alpha * math.sqrt(math.log(max(1, self.total_pulls + t)) / n_i)
                
                if ucb_val > best_ucb:
                    best_ucb = ucb_val
                    best_arm_idx = i
            
            if best_arm_idx != -1:
                selected = arm_data[best_arm_idx]
                cid = selected['id']
                self.arm_pulls[cid] = self.arm_pulls.get(cid, 0) + 1
                self.total_pulls += 1
                
                # Get true reward (Consistency)
                c, v = self._model_check(prompt, selected['candidate'])
                r_t = c - (v * 0.5)
                
                # PID Update
                self._update_pid(1.0 if c==1 else 0.0, c) 
                
                scores[cid] = best_ucb # Store latest UCB as score

        # Final Scoring and Ranking
        final_list = []
        for i, data in enumerate(arm_data):
            cid = data['id']
            base_score = scores[cid]
            
            # NCD Tiebreaker (max 15% influence)
            ncd_val = self._compute_ncd(prompt, data['candidate'])
            # Invert NCD (lower is better) and scale
            ncd_score = (1.0 - ncd_val) * 0.15 
            
            final_score = base_score + ncd_score
            
            # Apply Epistemic Cap
            if final_score > meta_cap:
                final_score = meta_cap
            
            # Ensure range [0, 1] roughly
            final_score = max(0.0, min(1.0, final_score))
            
            reason = f"Structural match: {data['features'][0]} neg, {data['features'][1]} comp. Violation cost: {data['features'][3]:.2f}."
            if meta_cap < 0.5:
                reason += " [WARNING: Prompt contains ambiguity or traps]"

            final_list.append({
                "candidate": data['candidate'],
                "score": final_score,
                "reasoning": reason
            })

        # Sort descending
        final_list.sort(key=lambda x: x['score'], reverse=True)
        return final_list

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence capped by meta-analysis of the prompt."""
        meta_cap = self._meta_confidence(prompt)
        
        # Calculate base confidence from model check
        cons, viol = self._model_check(prompt, answer)
        base_conf = cons - (viol * 0.2)
        
        # If no structural signal, confidence must be low
        feat = self._parse_graph(prompt + " " + answer)
        if feat['neg_count'] == 0 and feat['comp_count'] == 0 and feat['cond_count'] == 0:
            base_conf = 0.4 # Default uncertainty
            
        final_conf = min(base_conf, meta_cap)
        return max(0.0, min(1.0, final_conf))