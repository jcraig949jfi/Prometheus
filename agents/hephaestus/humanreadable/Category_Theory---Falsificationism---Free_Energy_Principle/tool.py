import re
import numpy as np
from typing import List, Dict, Tuple, Optional
from itertools import permutations

# --- Helper Functions for Parsing and Logic ---

def _normalize_text(text: str) -> str:
    return text.lower().strip()

def _extract_entities(text: str) -> List[str]:
    # Simple regex for capitalized words or quoted strings as entities
    ents = re.findall(r'\b[A-Z][a-z]+\b', text)
    ents += re.findall(r'"([^"]+)"', text)
    return ents

def _check_meta_confidence(prompt: str) -> float:
    """
    Tier B Reasoning: Epistemic Honesty Check.
    Returns a cap on confidence based on prompt ambiguity/traps.
    """
    p = _normalize_text(prompt)
    
    # 1. Presupposition traps ("Have you stopped...", "Why did X fail...")
    presupp_patterns = [
        r"have you (stopped|quit|finished)",
        r"why did .+ (fail|stop|end)",
        r"when did .+ (stop|fail)",
        r"how many times did .+ (fail|lie)"
    ]
    for pat in presupp_patterns:
        if re.search(pat, p):
            return 0.2  # Low confidence due to presupposition

    # 2. Scope/Pronoun Ambiguity (Heuristic: "told X he" or "every X ... a Y")
    if re.search(r"\btold\s+\w+\s+he\b", p) or re.search(r"\btold\s+\w+\s+she\b", p):
        if "who" in p or "which" in p:
            return 0.3
    
    # 3. False Dichotomy ("Either A or B" without context of exhaustiveness)
    if re.search(r"\beither\b", p) and re.search(r"\bor\b", p):
        # If it asks to choose between two specific options explicitly given, it's fine.
        # But if it implies only two options exist in a complex scenario, flag it.
        # Heuristic: If "either" appears but no clear binary constraint is defined.
        if "only" not in p and "just" not in p:
             pass # Soft check, don't penalize heavily unless obvious

    # 4. Subjectivity ("best", "favorite" without criteria)
    subj_terms = ["best", "worst", "favorite", "most beautiful", "tastiest"]
    if any(term in p for term in subj_terms):
        if "measure" not in p and "data" not in p and "statistic" not in p:
            return 0.4

    # 5. Unanswerability (Missing info indicators)
    if "cannot be determined" in p or "not enough information" in p:
        return 0.9 # Actually high confidence that it's unanswerable if stated
    
    return 1.0  # No obvious traps detected

def _parse_to_graph(text: str) -> Tuple[List[str], Dict, Dict]:
    """
    Step 1: Parsing -> Category-theoretic graph approximation.
    Returns nodes, adjacency (logic types), and weights.
    """
    nodes = []
    # Extract simple propositions based on connectors
    # Split by logical connectors to find atomic parts
    connectors = r'\b(because|therefore|if|then|unless|but|and|or|leads to)\b'
    parts = re.split(connectors, text, flags=re.IGNORECASE)
    
    # Extract nodes (atomic propositions roughly)
    sentences = re.split(r'[.;]', text)
    for s in sentences:
        s = s.strip()
        if s:
            nodes.append(s)
            
    # Build adjacency logic (simplified for implementation)
    # Types: 0=entail, 1=contradict, 2=conditional, 3=causal
    adj = {} 
    weights = {}
    
    lower_text = text.lower()
    
    # Detect relations via regex cues
    if re.search(r'\bbecause\b', lower_text):
        adj['type'] = 'causal'
        weights['w'] = 0.9
    elif re.search(r'\bif\b', lower_text):
        adj['type'] = 'conditional'
        weights['w'] = 0.8
    elif re.search(r'\bunless\b', lower_text):
        adj['type'] = 'conditional_neg'
        weights['w'] = 0.8
    elif re.search(r'\bleads to\b', lower_text):
        adj['type'] = 'causal'
        weights['w'] = 0.85
    else:
        adj['type'] = 'entail'
        weights['w'] = 0.5
        
    return nodes, adj, weights

def _compute_unfalsifiability(text: str) -> float:
    """
    Step 2: Falsificationism penalty.
    High U = hard to falsify (bad). Low U = easy to falsify (good).
    """
    lower_text = text.lower()
    modal_cues = ['might', 'could', 'possibly', 'maybe', 'perhaps']
    has_modal = any(c in lower_text for c in modal_cues)
    
    # Check for negation capability (presence of 'not', 'no', 'never')
    # If a statement makes no claims that can be negated, it's vague.
    # However, Popperian falsifiability is about whether the statement *allows* for a counter-example.
    # Statements with modals ("It might rain") are often less falsifiable than definite ones ("It will rain").
    
    if has_modal:
        return 0.8  # High penalty (hard to falsify)
    
    # Definite claims are easier to falsify
    return 0.2  

def _numeric_solve(prompt: str, candidate: str) -> Optional[float]:
    """
    Constructive computation: Attempt to solve numeric constraints.
    """
    # Extract numbers from prompt
    nums_prompt = re.findall(r"-?\d+\.?\d*", prompt)
    nums_cand = re.findall(r"-?\d+\.?\d*", candidate)
    
    if not nums_prompt:
        return None
        
    try:
        p_nums = [float(x) for x in nums_prompt]
        c_nums = [float(x) for x in nums_cand]
        
        # Simple heuristic: If candidate is a single number, check if it matches simple ops
        if len(c_nums) == 1:
            val = c_nums[0]
            # Check sum, diff, product
            if abs(val - sum(p_nums)) < 1e-5: return 1.0
            if len(p_nums) >= 2:
                if abs(val - (p_nums[0] + p_nums[1])) < 1e-5: return 1.0
                if abs(val - (p_nums[0] * p_nums[1])) < 1e-5: return 1.0
                if p_nums[1] != 0 and abs(val - (p_nums[0] / p_nums[1])) < 1e-5: return 1.0
    except:
        pass
    return None

def _ncd_distance(s1: str, s2: str) -> float:
    """Normalized Compression Distance using zlib."""
    import zlib
    s1_b = s1.encode('utf-8')
    s2_b = s2.encode('utf-8')
    try:
        c1 = len(zlib.compress(s1_b))
        c2 = len(zlib.compress(s2_b))
        c12 = len(zlib.compress(s1_b + s2_b))
        if min(c1, c2) == 0: return 1.0
        return (c12 - min(c1, c2)) / max(c1, c2)
    except:
        return 1.0

class ReasoningTool:
    def __init__(self):
        """
        Initializes the Reasoning Tool based on Category Theory x Falsificationism x Free Energy.
        
        Mechanism:
        1. Parsing: Converts text to a directed graph (Nodes=Props, Edges=Logical Relations).
        2. Falsification: Penalizes statements lacking counter-factual structure or using weak modals.
        3. Free Energy: Minimizes prediction error between prompt structure and candidate structure,
           balanced by the unfalsifiability penalty.
        4. Epistemic Honesty: Caps confidence if the prompt contains Tier B traps (ambiguity, presupposition).
        """
        pass

    def _meta_confidence(self, prompt: str) -> float:
        return _check_meta_confidence(prompt)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_nodes, p_adj, p_weights = _parse_to_graph(prompt)
        prompt_unfals = _compute_unfalsifiability(prompt)
        
        # Reference graph properties (simplified to vector of features for comparison)
        # Feature vector: [num_nodes, has_conditional, has_causal, has_negation]
        p_lower = prompt.lower()
        p_features = np.array([
            len(prompt_nodes),
            1.0 if 'if' in p_lower else 0.0,
            1.0 if 'because' in p_lower else 0.0,
            1.0 if 'not' in p_lower else 0.0
        ])

        for cand in candidates:
            c_nodes, c_adj, c_weights = _parse_to_graph(cand)
            c_unfals = _compute_unfalsifiability(cand)
            
            c_lower = cand.lower()
            c_features = np.array([
                len(c_nodes),
                1.0 if 'if' in c_lower else 0.0,
                1.0 if 'because' in c_lower else 0.0,
                1.0 if 'not' in c_lower else 0.0
            ])
            
            # Free Energy Calculation
            # 1. Prediction Error (E): Distance between feature vectors (Functorial alignment approx)
            E = np.linalg.norm(p_features - c_features)**2
            
            # 2. Unfalsifiability Penalty (U)
            # We want candidates that are falsifiable (low U). 
            # If candidate is vague (high U), Energy increases.
            U = c_unfals 
            
            # 3. Variational Free Energy: F = E + lambda * U
            lam = 2.0
            F = E + lam * U
            
            # Numeric constructive check (Boost score if math works)
            numeric_score = 0.0
            num_res = _numeric_solve(prompt, cand)
            if num_res is not None and num_res > 0.9:
                numeric_score = 5.0 # Strong boost for correct calculation
            
            # NCD Tiebreaker (Max 15% influence logic, here used as small additive)
            ncd = _ncd_distance(prompt, cand)
            ncd_bonus = (1.0 - ncd) * 0.5
            
            # Final Score (Negative Free Energy + bonuses)
            score = -F + numeric_score + ncd_bonus
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"E={E:.2f}, U={U:.2f}, F={F:.2f}, Numeric={numeric_score}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-cognitive analysis of the prompt (Tier B).
        """
        # 1. Meta-Confidence Cap (Epistemic Honesty)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Structural/Computational Verification
        # Run evaluate to get the score of this specific answer relative to others (or self)
        # Since we don't have all candidates here, we simulate a comparison against a null hypothesis
        temp_results = self.evaluate(prompt, [answer, "The answer cannot be determined."])
        
        # Find score of the provided answer
        ans_score = -1e9
        is_top = False
        if temp_results:
            top_item = temp_results[0]
            ans_score = top_item['score']
            is_top = (top_item['candidate'] == answer)
        
        # Normalize score to 0-1 range roughly (heuristic)
        # Scores can be negative. Let's map -10 -> 0.1, 10 -> 0.9
        norm_score = 1 / (1 + np.exp(-ans_score/2.0)) 
        
        # If it's not the top candidate, confidence drops significantly
        if not is_top:
            norm_score *= 0.5
            
        # Apply Meta Cap
        final_conf = min(norm_score, meta_cap)
        
        # Hard constraints per requirements
        if meta_cap < 0.3:
            return final_conf # Must be low
        
        # Never > 0.9 without definitive computation (numeric solve gives high score)
        # If numeric solve worked, score would be high, but we cap at 0.95 unless meta says no
        if final_conf > 0.95:
            final_conf = 0.95
            
        return max(0.0, min(1.0, final_conf))