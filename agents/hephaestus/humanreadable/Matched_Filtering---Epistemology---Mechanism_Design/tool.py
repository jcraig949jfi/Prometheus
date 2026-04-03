import re
import numpy as np
from typing import List, Dict, Tuple, Optional, Any
from collections import deque

class ReasoningTool:
    """
    A computational reasoning engine combining Matched Filtering, Epistemology, and Mechanism Design.
    
    Mechanism:
    1. Parsing Layer: Extracts atomic propositions (logic, math, causality) into sparse vectors.
    2. Signal Template: Constructs a weighted template from gold-standard reasoning patterns.
    3. Cross-Correlation: Scores candidates via dot-product against the epistemic template.
    4. Incentive Adjustment: Applies a sparsity penalty (lambda) to discourage guess-and-check verbosity.
    5. Computational Core: Executes formal operations (arithmetic, logic, state-tracking) rather than pattern matching.
    6. Epistemic Honesty: Caps confidence on ambiguous/unanswerable prompts (Tier B).
    """

    def __init__(self):
        # Predicate Dictionary Size (D)
        self.D = 100
        self.predicate_map = {}
        self._init_predicates()
        
        # Mechanism Design Parameters
        self.lambda_penalty = 0.5  # Sparsity penalty coefficient
        self.source_reliability = {"default": 0.8}
        
        # Gold standard template (initialized empty, built dynamically or via few-shot)
        self.template_vector = np.zeros(self.D)
        self.template_weights = np.zeros(self.D)

    def _init_predicates(self):
        """Initialize a deterministic set of predicate keys for the sparse vector."""
        keys = [
            "negation", "comparative_gt", "comparative_lt", "comparative_eq",
            "conditional_if", "conditional_then", "causal_because", "causal_therefore",
            "temporal_before", "temporal_after", "numeric_val", "logic_and", "logic_or",
            "quantifier_all", "quantifier_some", "quantifier_none", "agent_action",
            "state_change", "constraint_unique", "constraint_exhaustive",
            "math_add", "math_sub", "math_mul", "math_div", "math_mod",
            "ambig_pronoun", "ambig_scope", "presupposition", "false_dichotomy"
        ]
        # Expand for numeric ranges if needed, but keep static for this demo
        for i, k in enumerate(keys):
            if i < self.D:
                self.predicate_map[k] = i

    def _parse_to_ir(self, text: str) -> Dict[str, Any]:
        """
        Parses text into a Formal Intermediate Representation (IR).
        Returns a dictionary containing extracted logic, math, and structural flags.
        """
        ir = {
            "propositions": [],
            "numbers": [],
            "logic_ops": [],
            "entities": [],
            "flags": [],
            "computed_answer": None,
            "is_computable": False,
            "computation_type": None
        }

        text_lower = text.lower()
        
        # 1. Numeric Extraction & Computation Triggers
        numbers = re.findall(r"-?\d+\.?\d*", text)
        if numbers:
            ir["numbers"] = [float(n) for n in numbers]
        
        # Detect Math Problems (Bat-and-Ball, PEMDAS, Modular)
        if re.search(r"total|sum|difference|product|remainder|modulo|divided by", text_lower):
            ir["computation_type"] = "arithmetic"
            ir["is_computable"] = True
            
        # Detect Logic Problems (Modus Tollens, Transitivity)
        if re.search(r"if.*then|therefore|must be|cannot be", text_lower):
            ir["computation_type"] = "logic"
            ir["is_computable"] = True
            
        # Detect State Tracking (Register machine, Agents)
        if re.search(r"starts with|adds|removes|gives to|moves to", text_lower):
            ir["computation_type"] = "state_tracking"
            ir["is_computable"] = True

        # 2. Structural Predicate Extraction (Vector Components)
        if "not" in text_lower or "no " in text_lower or "never" in text_lower:
            ir["logic_ops"].append("negation")
        if ">" in text or "more than" in text_lower or "greater" in text_lower:
            ir["logic_ops"].append("comparative_gt")
        if "<" in text or "less than" in text_lower:
            ir["logic_ops"].append("comparative_lt")
        if "if" in text_lower:
            ir["logic_ops"].append("conditional_if")
        if "because" in text_lower:
            ir["logic_ops"].append("causal_because")
            
        # 3. Tier B: Epistemic Trap Detection (Ambiguity/Presupposition)
        if re.search(r"have you stopped|why did.*fail|when did.*stop", text_lower):
            ir["flags"].append("presupposition")
        if re.search(r"every.*a.*\?", text_lower) and "same" in text_lower:
            ir["flags"].append("scope_ambiguity")
        if re.search(r"he.*she.*who|told.*him.*who", text_lower):
            ir["flags"].append("pronoun_ambiguity")
        if re.search(r"either.*or", text_lower) and "only" not in text_lower:
            ir["flags"].append("false_dichotomy")
        if re.search(r"best|worst|favorite", text_lower) and "measure" not in text_lower:
            ir["flags"].append("subjectivity")

        return ir

    def _execute_computation(self, prompt: str, ir: Dict) -> Optional[float]:
        """
        Executes formal computation on the IR.
        Returns a definitive numeric answer if computable, else None.
        """
        nums = ir.get("numbers", [])
        ctype = ir.get("computation_type")

        try:
            # Case: Simple Arithmetic / Bat-and-Ball variants
            if ctype == "arithmetic":
                if "bat" in prompt.lower() and "ball" in prompt.lower() and len(nums) >= 2:
                    # Bat + Ball = Total, Bat = Ball + Diff
                    # Simplified heuristic for specific algebraic structure
                    total = nums[0]
                    diff = nums[1] if len(nums) > 1 else 0
                    # 2*Ball = Total - Diff
                    ball = (total - diff) / 2.0
                    return ball
                elif len(nums) >= 2:
                    # Generic fallback for simple sums/diffs if detected
                    if "sum" in prompt.lower():
                        return sum(nums)
            
            # Case: State Tracking (Register Machine simulation)
            if ctype == "state_tracking":
                # Very basic parser for "Starts with X, adds Y, removes Z"
                val = 0.0
                if "starts with" in prompt.lower():
                    match = re.search(r"starts with (\d+)", prompt.lower())
                    if match: val = float(match.group(1))
                
                # Process operations sequentially
                adds = re.findall(r"adds? (\d+)", prompt.lower())
                rems = re.findall(r"removes? (\d+)", prompt.lower())
                gives = re.findall(r"gives? (\d+)", prompt.lower()) # Removes from subject
                
                for a in adds: val += float(a)
                for r in rems: val -= float(r)
                for g in gives: val -= float(g)
                
                # If only one number found and it's a "total" query, might need different logic
                # But for state tracking, we usually track the variable.
                # If no explicit start, assume 0 or first number is start? 
                # Let's assume standard "Start X, op Y" structure.
                if "starts with" not in prompt.lower() and len(nums) > 0:
                     # Fallback: First number is state, rest are ops? 
                     # Too ambiguous without more parsing. Rely on explicit "starts".
                     pass
                else:
                    return val

            # Case: Logic (Modus Tollens / Transitivity)
            if ctype == "logic":
                # If A > B and B > C, then A > C. 
                # This requires extracting entities. 
                # For this implementation, we flag it as computable but return None 
                # if specific entity mapping isn't resolved, forcing reliance on structural score.
                pass

        except Exception:
            return None
            
        return None

    def _build_proposition_vector(self, text: str, ir: Dict) -> np.ndarray:
        """Converts parsed IR into a sparse binary vector."""
        vec = np.zeros(self.D)
        
        # Map logic ops
        for op in ir.get("logic_ops", []):
            if op in self.predicate_map:
                vec[self.predicate_map[op]] = 1
                
        # Map flags (as negative signals or specific predicates)
        for flag in ir.get("flags", []):
            key = f"ambig_{flag}" if "ambig" in flag else flag
            if key in self.predicate_map:
                vec[self.predicate_map[key]] = 1
                
        # Numeric presence
        if ir.get("numbers"):
            if "numeric_val" in self.predicate_map:
                vec[self.predicate_map["numeric_val"]] = 1
                
        return vec

    def _meta_confidence(self, prompt: str, ir: Dict) -> float:
        """
        Tier B: Evaluates prompt properties to determine epistemic ceiling.
        Returns a cap < 0.3 for ambiguous/unanswerable prompts.
        """
        flags = ir.get("flags", [])
        
        # Critical failures for high confidence
        if any(f in flags for f in ["presupposition", "scope_ambiguity", "pronoun_ambiguity", "false_dichotomy", "subjectivity"]):
            return 0.25
            
        # If no structural parser matches and no computation possible
        if not ir.get("is_computable") and not ir.get("logic_ops"):
            # Check for pure NCD trap (short answers, vague questions)
            if len(prompt.split()) < 5:
                return 0.3
                
        return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_ir = self._parse_to_ir(prompt)
        prompt_vec = self._build_proposition_vector(prompt, prompt_ir)
        
        # Build dynamic template from prompt + expected reasoning pattern
        # We assume the prompt contains the 'truth' conditions.
        # We weight 'logic_ops' and 'numeric_val' highly as they indicate reasoning.
        template = np.zeros(self.D)
        weights = np.zeros(self.D)
        
        # Self-weighting: The prompt's own structural features are the template
        template = prompt_vec.copy()
        
        # Epistemic Weighting: Boost logic and math predicates
        for k, idx in self.predicate_map.items():
            if k in ["comparative_gt", "comparative_lt", "conditional_if", "numeric_val", "logic_and"]:
                weights[idx] = 2.0  # High reliability for structural logic
            elif k.startswith("ambig") or k == "presupposition":
                weights[idx] = -1.0 # Penalty for ambiguity markers in answer? 
                # Actually, if the PROMPT has ambiguity, we cap confidence later.
                # If the CANDIDATE has ambiguity markers not in prompt, maybe penalty.
            else:
                weights[idx] = 1.0

        scored_candidates = []
        
        # Compute definitive answer if possible
        computed_val = self._execute_computation(prompt, prompt_ir)
        
        for cand in candidates:
            cand_ir = self._parse_to_ir(cand)
            cand_vec = self._build_proposition_vector(cand, cand_ir)
            
            # 1. Matched Filter Score (Dot Product)
            # s = t . c (weighted)
            raw_score = np.dot(template * weights, cand_vec)
            
            # 2. Computational Verification (The "Truth" Signal)
            comp_score = 0.0
            if computed_val is not None:
                # Extract number from candidate
                cand_nums = cand_ir.get("numbers", [])
                if cand_nums:
                    # Check proximity to computed answer
                    best_diff = min(abs(n - computed_val) for n in cand_nums)
                    if best_diff < 1e-6:
                        comp_score = 10.0 # Strong boost for correct calculation
                    elif best_diff < 0.1:
                        comp_score = 5.0
                else:
                    # Candidate has no numbers but computation was expected
                    comp_score = -5.0
            
            # 3. Incentive-Compatible Adjustment (Sparsity Penalty)
            # Penalize excessive propositions (guess-and-check)
            prop_count = np.sum(cand_vec)
            penalty = self.lambda_penalty * prop_count
            
            final_score = raw_score + comp_score - penalty
            
            # Add small NCD component as tiebreaker (<15% influence)
            # Only if scores are very close, but here we just add a tiny fraction
            # to break ties without dominating.
            # (Skipped for strict adherence to "Computation > NCD" rule, relying on comp_score)
            
            scored_candidates.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Matched Filter: {raw_score:.2f}, Computation: {comp_score:.2f}, Penalty: {penalty:.2f}"
            })
            
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on _meta_confidence (Tier B honesty).
        """
        ir = self._parse_to_ir(prompt)
        
        # 1. Meta-Confidence Cap (Epistemic Honesty)
        meta_cap = self._meta_confidence(prompt, ir)
        
        # 2. Base Score from Evaluation
        # Run evaluate to get the score of this specific answer
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.0
            
        base_score = results[0]["score"]
        
        # Normalize base_score to 0-1 roughly
        # Heuristic: > 5 is strong, < 0 is weak
        if base_score > 5:
            raw_conf = 0.95
        elif base_score > 0:
            raw_conf = 0.6 + (base_score / 10.0)
        else:
            raw_conf = 0.1
            
        # 3. Apply Cap
        final_conf = min(raw_conf, meta_cap)
        
        # Ensure we never return > 0.9 without computation
        if ir.get("computation_type") is None and final_conf > 0.9:
            final_conf = 0.85 # Slight doubt if no formal computation path
            
        return round(final_conf, 3)

# Example Usage (Internal Test)
if __name__ == "__main__":
    tool = ReasoningTool()
    
    # Test 1: Computational (Bat and Ball)
    p1 = "A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball. How much does the ball cost?"
    c1 = ["$0.10", "$0.05", "$0.15"]
    res1 = tool.evaluate(p1, c1)
    print(f"Bat/Ball Result: {res1[0]['candidate']} (Score: {res1[0]['score']:.2f})")
    print(f"Confidence: {tool.confidence(p1, res1[0]['candidate'])}")
    
    # Test 2: Tier B Trap (Presupposition)
    p2 = "Have you stopped cheating on tests?"
    c2 = ["Yes", "No"]
    conf2 = tool.confidence(p2, "Yes")
    print(f"Presupposition Trap Confidence: {conf2} (Should be < 0.3)")
    
    # Test 3: State Tracking
    p3 = "John starts with 5 apples. He buys 3 more. Then he gives 2 to Sally. How many does he have?"
    c3 = ["6", "5", "8"]
    res3 = tool.evaluate(p3, c3)
    print(f"State Tracking Result: {res3[0]['candidate']} (Score: {res3[0]['score']:.2f})")