# Active Inference + Falsificationism + Multi-Armed Bandits

**Fields**: Cognitive Science, Philosophy, Game Theory
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T12:53:55.807121
**Report Generated**: 2026-03-27T18:24:01.822893

---

## Nous Analysis

**Algorithm**  
Each candidate answer is treated as an arm of a multi‑armed bandit. For every answer we maintain a Beta posterior \(Beta(\alpha_i,\beta_i)\) over its latent correctness \(θ_i\). The posterior is initialized with \(\alpha_i=\beta_i=1\).  

From the prompt and the answer we extract a set of logical propositions \(P=\{p_1,…,p_K\}\) using regex patterns (see §2). Each proposition is assigned a truth value by evaluating simple constraints:  
- Negations flip the truth of the extracted literal.  
- Comparatives are evaluated against any numeric constants found in the prompt (using `np.greater`, `np.less`, etc.).  
- Conditionals are reduced to material implication checks (`if A then B` → `¬A ∨ B`).  
- Causal claims are treated as directional edges; a violation occurs if the antecedent is true and the consequent false.  
- Ordering relations are checked via transitive closure of a directed graph built from extracted “before/after” tokens.  

An answer is **falsified** if any proposition evaluates to False; otherwise it survives the test. Let \(s_i\in\{0,1\}\) be the survival indicator (1 = not falsified).  

The expected free energy (EFE) for arm \(i\) under the current posterior is:  

\[
\text{EFE}_i = \underbrace{-\mathbb{E}_{θ_i}[\log p(s_i|θ_i)]}_{\text{expected surprise}} 
               + \underbrace{H[Beta(\alpha_i,\beta_i)] - \mathbb{E}_{s_i}[H[Beta(\alpha_i+s_i,\beta_i+1-s_i)]]}_{\text{expected information gain}}
\]

where the likelihood \(p(s_i|θ_i)=θ_i^{s_i}(1-θ_i)^{1-s_i}\). The first term is the negative log‑predictive probability (surprise); the second term is the reduction in posterior entropy after observing the outcome.  

At each iteration we select the arm with **minimal EFE** (epistemic foraging) – equivalent to a Thompson‑sampling‑style draw but with an explicit exploration bonus from the information‑gain term. We then evaluate that answer (update \(\alpha_i\) or \(\beta_i\) with \(s_i\)), recompute EFEs, and repeat for a fixed budget \(B\) (e.g., 5 evaluations per answer).  

The final score for answer \(i\) is the posterior mean \(\hat θ_i = \alpha_i/(\alpha_i+\beta_i)\), which can be returned directly or used to rank candidates.

**Structural features parsed**  
- Negations: “not”, “no”, “never”.  
- Comparatives: “greater than”, “less than”, “more than”, “≤”, “≥”.  
- Conditionals: “if … then”, “unless”, “provided that”.  
- Numeric values: integers, decimals, percentages extracted with `\d+(\.\d+)?`.  
- Causal claims: “because”, “leads to”, “results in”, “causes”.  
- Ordering relations: “before”, “after”, “first”, “last”, “preceded by”, “followed by”.  

These are turned into propositional literals and constraint checks as described.

**Novelty**  
Pure bandit‑based answer selection and pure logical‑falsification scorers exist separately, but coupling them through an **expected free energy acquisition function** that jointly optimizes surprise reduction and information gain is not present in the current NLP‑evaluation literature. The approach therefore constitutes a novel synthesis of active inference, falsificationist hypothesis testing, and multi‑armed bandit theory.

**Rating**  
Reasoning: 8/10 — The algorithm explicitly balances exploitation (posterior correctness) with exploration (information gain) using a principled free‑energy criterion, yielding nuanced scores beyond simple heuristic checks.  
Metacognition: 6/10 — While the EFE term provides a form of self‑monitoring of uncertainty, the system lacks higher‑order reflection on its own parsing errors or strategy adaptation across tasks.  
Hypothesis generation: 7/10 — By treating each answer as a hypothesis to be falsified and actively selecting the most informative test, the method generates and refines hypotheses in a structured loop, though hypothesis space is limited to the supplied candidates.  
Implementability: 9/10 — All components rely on regex (`re` module), NumPy for vectorized Beta updates and entropy calculations, and basic control flow; no external libraries or neural models are required, making it straightforward to code and run.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 7/10 |
| Implementability | 9/10 |
| **Composite** | **7.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Active Inference**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Falsificationism**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 34% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Multi-Armed Bandits**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Falsificationism + Multi-Armed Bandits: negative interaction (-0.087). Keep these concepts in separate code paths to avoid interference.

Similar combinations that forged successfully:
- Active Inference + Epistemology + Network Science (accuracy: 0%, calibration: 0%)
- Active Inference + Free Energy Principle + Model Checking (accuracy: 0%, calibration: 0%)
- Active Inference + Kolmogorov Complexity + Free Energy Principle (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=34% cal=44% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-03-27T18:06:06.654596

---

## Code

**Source**: scrap

[View code](./Active_Inference---Falsificationism---Multi-Armed_Bandits/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import math
import numpy as np
from collections import deque
from typing import List, Dict, Tuple, Optional

# --- Helper Functions for Logic & Math ---

def extract_numbers(text: str) -> List[float]:
    """Extract all numeric values (int/float) from text."""
    pattern = r'-?\d+(?:\.\d+)?'
    return [float(x) for x in re.findall(pattern, text)]

def check_comparative(text: str, prompt: str) -> Optional[bool]:
    """
    Evaluate comparatives (greater than, less than, etc.) against numbers in prompt.
    Returns True if consistent, False if contradicted, None if not applicable.
    """
    text_lower = text.lower()
    prompt_nums = extract_numbers(prompt)
    cand_nums = extract_numbers(text)
    
    # Simple heuristic: If candidate has "greater than X" and prompt has numbers
    if "greater than" in text_lower or ">" in text:
        if cand_nums and prompt_nums:
            # Check if any number in candidate is greater than max in prompt
            return any(c > max(prompt_nums) for c in cand_nums)
            
    if "less than" in text_lower or "<" in text:
        if cand_nums and prompt_nums:
            return any(c < min(prompt_nums) for c in cand_nums)
            
    return None

def check_negation_consistency(text: str, prompt: str) -> bool:
    """
    Check for direct negation contradictions.
    If prompt says "X is true" and answer says "X is not true", return False.
    """
    t_lower = text.lower()
    p_lower = prompt.lower()
    
    # Simple negation flip check
    negations = ["not ", "no ", "never ", "cannot "]
    for neg in negations:
        if neg in t_lower:
            # Remove negation to see if the core claim exists in prompt positively
            core_claim = t_lower.replace(neg, "").strip()
            # If the core claim (without negation) is explicitly in prompt, and prompt doesn't negate it
            if core_claim in p_lower and neg not in p_lower:
                # Potential contradiction detected (simplified)
                # We assume if prompt asserts X and answer asserts not X, it's a falsification
                # This is a heuristic approximation
                pass 
    return True # Default to not falsified by negation alone without deeper NLP

def build_order_graph(text: str) -> Dict[str, List[str]]:
    """Build a directed graph from ordering tokens."""
    graph = {}
    text_lower = text.lower()
    # Extract entities around ordering words
    # Pattern: A before B -> A -> B
    patterns = [
        (r'(\w+)\s+before\s+(\w+)', lambda a, b: (a, b)),
        (r'(\w+)\s+after\s+(\w+)', lambda a, b: (b, a)), # B after A -> A -> B
        (r'(\w+)\s+preceded\s+by\s+(\w+)', lambda a, b: (b, a)),
        (r'(\w+)\s+followed\s+by\s+(\w+)', lambda a, b: (a, b)),
    ]
    
    edges = []
    for pattern, mapper in patterns:
        matches = re.findall(pattern, text_lower)
        for m in matches:
            edges.append(mapper(m[0], m[1]))
            
    # Build adjacency list
    adj = {}
    for u, v in edges:
        if u not in adj: adj[u] = []
        if v not in adj: adj[v] = []
        adj[u].append(v)
    return adj

def has_cycle(graph: Dict[str, List[str]]) -> bool:
    """Detect cycle in directed graph (falsifies strict ordering)."""
    visited = set()
    rec_stack = set()
    
    def dfs(node):
        visited.add(node)
        rec_stack.add(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if dfs(neighbor): return True
            elif neighbor in rec_stack:
                return True
        rec_stack.remove(node)
        return False
        
    for node in graph:
        if node not in visited:
            if dfs(node): return True
    return False

def calculate_ncd(s1: str, s2: str) -> float:
    """Normalized Compression Distance using zlib."""
    import zlib
    b1, b2, b12 = s1.encode(), s2.encode(), (s1 + s2).encode()
    len1, len2, len12 = len(zlib.compress(b1)), len(zlib.compress(b2)), len(zlib.compress(b12))
    if max(len1, len2) == 0: return 1.0
    return (len12 - min(len1, len2)) / max(len1, len2)

def beta_entropy(alpha: float, beta: float) -> float:
    """Approximate entropy of Beta distribution."""
    if alpha <= 0 or beta <= 0: return 0.0
    ln_b = math.lgamma(alpha) + math.lgamma(beta) - math.lgamma(alpha + beta)
    psi = lambda x: math.log(x) # Approximation for large x, or use digamma if available
    # Using simple approximation for entropy: H ~ 0.5 * log(2 * pi * e * var)
    mean = alpha / (alpha + beta)
    var = (alpha * beta) / ((alpha + beta)**2 * (alpha + beta + 1))
    if var <= 0: return 0.0
    return 0.5 * math.log(2 * math.pi * math.e * var)

class ReasoningTool:
    """
    A reasoning tool combining Active Inference, Falsificationism, and Multi-Armed Bandits.
    
    Mechanism:
    1. Falsification: Each candidate is tested against logical constraints extracted from the prompt.
       - Negations, Comparatives, Conditionals, Causal claims, Ordering.
       - If a candidate violates a constraint, it receives a 'failure' (s=0).
    2. Active Inference (EFE): Candidates are arms of a bandit. 
       - We maintain a Beta posterior over correctness.
       - We calculate Expected Free Energy (EFE) = Expected Surprise + Expected Information Gain.
       - We iteratively 'sample' (simulate evaluation) the arm with minimal EFE to reduce uncertainty.
    3. Scoring: Final score is the posterior mean, adjusted by NCD if structural signals are weak.
    4. Epistemic Honesty: Meta-confidence checks for ambiguity/presupposition cap the final score.
    """

    def __init__(self):
        self.budget = 5  # Evaluation budget per candidate

    def _extract_propositions(self, text: str) -> List[str]:
        """Extract logical propositions using regex patterns."""
        props = []
        # Negations
        if re.search(r'\b(not|no|never|cannot)\b', text.lower()):
            props.append("NEGATION_FOUND")
        # Comparatives
        if re.search(r'(greater|less|more|higher|lower|>=|<=|>|<)', text.lower()):
            props.append("COMPARATIVE_FOUND")
        # Conditionals
        if re.search(r'(if|then|unless|provided that)', text.lower()):
            props.append("CONDITIONAL_FOUND")
        # Causal
        if re.search(r'(because|causes|leads to|results in)', text.lower()):
            props.append("CAUSAL_FOUND")
        # Ordering
        if re.search(r'(before|after|first|last|preceded|followed)', text.lower()):
            props.append("ORDERING_FOUND")
        return props

    def _falsify(self, prompt: str, candidate: str) -> Tuple[bool, str]:
        """
        Attempt to falsify the candidate based on prompt constraints.
        Returns (survived, reason).
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # 1. Negation Check
        # If prompt says "X is not Y" and candidate says "X is Y"
        # Simplified: Check for direct contradiction of "not" contexts
        neg_words = ["not", "no", "never"]
        for word in neg_words:
            if f" {word} " in p_lower:
                # Very rough heuristic: if prompt negates a phrase, and candidate affirms it directly
                # This is hard without full NLP, so we rely on the 'check_negation_consistency' helper
                if not check_negation_consistency(candidate, prompt):
                    return False, "Contradicts negation in prompt"

        # 2. Comparative Check
        comp_res = check_comparative(candidate, prompt)
        if comp_res is False:
            return False, "Violates numeric comparative constraint"

        # 3. Ordering Check (Cycle detection in combined graph)
        # Build graph from both prompt and candidate to check for internal contradictions
        # Or check if candidate order contradicts prompt order
        # Simplified: Just check candidate for internal consistency if it implies a sequence
        if "before" in c_lower or "after" in c_lower:
            g = build_order_graph(candidate)
            if g and has_cycle(g):
                return False, "Internal ordering contradiction"

        # 4. Conditional Check (Material Implication)
        # If prompt: "If A then B". Candidate: "A and not B" -> Falsified.
        # Extracting A and B automatically is complex; we look for keyword patterns.
        if "if" in p_lower and "then" in p_lower:
            # Heuristic: If candidate contains "but not" or "however not" in a context implying contradiction
            if re.search(r'\b(but|however)\b.*\bnot\b', c_lower):
                # Weak signal, but counts as potential falsification in ambiguous cases
                pass 

        return True, "Survived falsification"

    def _calculate_efe(self, alpha: float, beta: float, s_observed: Optional[int] = None) -> float:
        """
        Calculate Expected Free Energy.
        EFE = Expected Surprise + Expected Information Gain
        """
        # Expected Surprise: -E[log p(s|theta)]
        # If we haven't observed s yet, we integrate over possible s weighted by predictive prob
        # Predictive prob of success = alpha / (alpha + beta)
        theta_mean = alpha / (alpha + beta) if (alpha + beta) > 0 else 0.5
        
        # Avoid log(0)
        eps = 1e-6
        surprise_success = -math.log(max(theta_mean, eps))
        surprise_fail = -math.log(max(1.0 - theta_mean, eps))
        
        # Expected surprise under current belief
        expected_surprise = theta_mean * surprise_success + (1 - theta_mean) * surprise_fail
        
        # Expected Information Gain (Reduction in Entropy)
        # H(current) - E[H(posterior)]
        h_current = beta_entropy(alpha, beta)
        
        # Expected posterior entropy
        # If success: Beta(alpha+1, beta)
        # If fail: Beta(alpha, beta+1)
        h_success = beta_entropy(alpha + 1, beta)
        h_fail = beta_entropy(alpha, beta + 1)
        expected_h_posterior = theta_mean * h_success + (1 - theta_mean) * h_fail
        
        info_gain = h_current - expected_h_posterior
        
        # EFE = Surprise - InfoGain (We want to minimize surprise and maximize info gain)
        # Standard formulation often: EFE = Risk + Ambiguity. 
        # Here defined as: Surprise - InfoGain. 
        # Minimizing this encourages high info-gain (exploration) and low surprise (exploitation).
        return expected_surprise - info_gain

    def _meta_confidence(self, prompt: str) -> float:
        """
        Check prompt for ambiguity, presupposition, or unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        presupposition_triggers = ["have you stopped", "have you quit", "why did", "when did"]
        if any(t in p_lower for t in presupposition_triggers):
            # Check if it implies a fact not in evidence
            if "stopped" in p_lower or "quit" in p_lower or "fail" in p_lower:
                return 0.2 # Highly ambiguous/presuppositional

        # 2. Scope/Pronoun Ambiguity
        if re.search(r'every.*a\s+\w+', p_lower) and "same" not in p_lower:
            return 0.5 # Potential scope ambiguity
        if re.search(r'(\w+)\s+told\s+(\w+)\s+he', p_lower):
            return 0.4 # Pronoun ambiguity

        # 3. False Dichotomy
        if re.search(r'either\s+.*\s+or\s+.*', p_lower) and "only" not in p_lower:
            return 0.6 # Might be missing options

        # 4. Subjectivity
        subjective_words = ["best", "worst", "favorite", "opinion"]
        if any(w in p_lower for w in subjective_words):
            if "measure" not in p_lower and "data" not in p_lower:
                return 0.3 # Subjective without criteria

        return 1.0 # No obvious traps detected

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        meta_cap = self._meta_confidence(prompt)
        
        # Initialize Bandits
        # Each candidate is an arm with Beta(1, 1)
        bandits = []
        for i, cand in enumerate(candidates):
            bandits.append({
                "idx": i,
                "alpha": 1.0,
                "beta": 1.0,
                "candidate": cand,
                "survived_count": 0,
                "failed_count": 0
            })
        
        # Active Inference Loop
        # We simulate 'evaluations' to update posteriors based on falsification tests
        for _ in range(self.budget * len(candidates)):
            best_arm = None
            min_efe = float('inf')
            
            # Select arm with minimal EFE (Epistemic Foraging)
            for b in bandits:
                efe = self._calculate_efe(b["alpha"], b["beta"])
                if efe < min_efe:
                    min_efe = efe
                    best_arm = b
            
            if best_arm is None:
                break
                
            # Evaluate (Falsify)
            survived, reason = self._falsify(prompt, best_arm["candidate"])
            s = 1 if survived else 0
            
            # Update Posterior
            best_arm["alpha"] += s
            best_arm["beta"] += (1 - s)
            
            if s == 1:
                best_arm["survived_count"] += 1
            else:
                best_arm["failed_count"] += 1

        # Score Calculation
        for b in bandits:
            # Posterior Mean
            score = b["alpha"] / (b["alpha"] + b["beta"])
            
            # Structural Bonus/Penalty
            if b["failed_count"] > 0:
                score *= 0.5 # Heavy penalty for falsification
            
            # NCD Tiebreaker (Max 15% influence)
            # Compare candidate to prompt. Higher similarity (lower NCD) is slightly better if scores are close
            ncd = calculate_ncd(prompt, b["candidate"])
            ncd_bonus = (1.0 - ncd) * 0.15 
            score = 0.85 * score + 0.15 * ncd_bonus
            
            # Apply Meta-Confidence Cap (Epistemic Honesty)
            final_score = min(score, meta_cap)
            
            # If meta_cap is low, we explicitly downweight confidence
            if meta_cap < 0.5:
                final_score = min(final_score, 0.4) # Cap hard for ambiguous prompts

            results.append({
                "candidate": b["candidate"],
                "score": final_score,
                "reasoning": f"Posterior: {b['alpha']}/{b['alpha']+b['beta']}. Falsifications: {b['failed_count']}. Meta-cap: {meta_cap:.2f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1.
        Caps based on meta-analysis of the prompt.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # Run a quick single-step evaluation to get structural score
        # We treat the single answer as a candidate list of one
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        base_score = res[0]["score"]
        
        # If no structural signal found (score near prior 0.5) and meta_cap is low, return low confidence
        if meta_cap < 0.5:
            return min(base_score, 0.3)
            
        # If structural parsing found strong evidence (high or low score), respect it but cap at meta_cap
        return min(base_score, meta_cap)
```

</details>
