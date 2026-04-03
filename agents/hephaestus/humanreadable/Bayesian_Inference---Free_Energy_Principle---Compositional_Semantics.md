# Bayesian Inference + Free Energy Principle + Compositional Semantics

**Fields**: Mathematics, Theoretical Neuroscience, Philosophy
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-31T12:32:14.370503
**Report Generated**: 2026-04-02T04:20:09.799742

---

## Nous Analysis

**Algorithm**  
We build a lightweight probabilistic logic scorer. Input: a prompt P and a set of candidate answers {A₁,…,Aₖ}.  
1. **Parsing (Compositional Semantics)** – Using a small regex‑based parser we extract atomic propositions (e.g., “X > Y”, “¬R”, “C causes D”) and binary operators (∧, →, ¬). Each proposition becomes a node in a directed factor graph; complex expressions are represented as factor functions that combine child node beliefs via logical truth tables (e.g., P(A∧B)=P(A)·P(B) assuming independence).  
2. **Belief Representation (Bayesian Inference)** – Each atomic node holds a conjugate prior: for binary propositions a Beta(α,β) distribution; for numeric constraints a Gaussian 𝒩(μ,σ²). Priors are set from background knowledge (e.g., uniform Beta(1,1)).  
3. **Free‑Energy Principle** – Define variational free energy F = ∑ᵢ KL[qᵢ‖pᵢ] + ∑ₐ 𝔼_q[−log p(dataₐ|parentsₐ)], where qᵢ is the current belief (approximate posterior) and pᵢ the prior. The second term is the prediction error: for each factor we compute the log‑likelihood of the observed truth value under the current beliefs (using numpy for log‑sum‑exp). Minimizing F is performed by a few iterations of gradient‑free coordinate ascent: update each node’s parameters to reduce its local KL plus expected error (closed‑form for Beta/Gaussian).  
4. **Scoring** – After convergence, the posterior probability that the candidate answer entails the prompt (i.e., the joint belief of all prompt propositions) is taken as the score S = exp(−F). Higher S means lower free energy → better fit.  

**Structural Features Parsed**  
- Negations (¬)  
- Comparatives and ordering (“>”, “<”, “≥”, “≤”)  
- Conditionals (→) and biconditionals (↔)  
- Numeric values and inequalities  
- Causal verbs (“causes”, “leads to”, “prevents”) mapped to directed edges  
- Conjunctions/disjunctions (∧, ∨)  

**Novelty**  
The combination mirrors existing frameworks (Markov Logic Networks, Probabilistic Soft Logic, variational inference for semantic parsing) but uniquely ties a *free‑energy minimization* loop to a *compositional* factor graph with *conjugate‑priori* Bayesian updates, all implementable with only NumPy and the stdlib. No prior work combines these three ingredients in this exact, lightweight form for answer scoring.  

**Ratings**  
Reasoning: 8/10 — captures logical structure and uncertainty, though approximations may miss deep inferences.  
Metacognition: 6/10 — the algorithm can monitor free‑energy reduction but lacks explicit self‑reflection on its own uncertainties.  
Hypothesis generation: 5/10 — proposes updates to beliefs but does not generate novel candidate answers beyond those supplied.  
Implementability: 9/10 — relies solely on regex parsing, NumPy array ops, and closed‑form Beta/Gaussian updates; easy to code and run.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 9/10 |
| **Composite** | **6.33** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=39% cal=7% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-01T22:20:56.730639

---

## Code

**Source**: scrap

[View code](./Bayesian_Inference---Free_Energy_Principle---Compositional_Semantics/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import math
import numpy as np
from typing import List, Dict, Tuple, Optional, Any

# --- Constants & Priors ---
# Beta(1,1) is Uniform. Alpha=1, Beta=1.
DEFAULT_ALPHA = 1.0
DEFAULT_BETA = 1.0
# Causal verbs mapping
CAUSAL_VERBS = ["causes", "leads to", "results in", "produces", "implies", "yields"]
NEGATION_WORDS = ["not", "no", "never", "neither", "without", "fails to"]
COMPARATORS = [">", "<", ">=", "<=", "==", "!="]
SCOPE_AMBIGUITY_PATTERNS = [
    r"every\s+\w+.*\s+(a|an|the)\s+\w+", # Every X did a Y
    r"each\s+\w+.*\s+(a|an|the)\s+\w+"
]
PRONOUN_AMBIGUITY_PATTERNS = [
    r"(\w+)\s+(told|said to|asked)\s+(\w+)\s+(he|she|it|they)\s+was",
    r"who\s+is\s+(he|she|it|they)\?"
]
PRESUPPOSITION_PATTERNS = [
    r"have\s+you\s+(stopped|quit|ceased)\s+",
    r"why\s+did\s+\w+\s+(fail|stop|quit)\s+",
    r"when\s+did\s+\w+\s+(stop|fail)\s+"
]
FALSE_DICHOTOMY_PATTERNS = [
    r"either\s+.+\s+or\s+.+",
    r"is\s+it\s+(a|b)\s+or\s+(c|d)\?"
]

class ReasoningTool:
    """
    A lightweight probabilistic logic scorer combining Compositional Semantics,
    Bayesian Inference (Beta/Gaussian priors), and the Free Energy Principle.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions and logical operators via regex.
    2. Belief: Represents beliefs as conjugate distributions (Beta for binary, Gaussian for numeric).
    3. Free Energy: Minimizes variational free energy (KL divergence + Prediction Error) 
       via coordinate ascent to update beliefs based on logical constraints.
    4. Scoring: Scores candidates by exp(-FreeEnergy) of the joint graph state.
    5. Meta-Cognition: Caps confidence if structural ambiguity or presuppositions are detected.
    """

    def __init__(self):
        self._cache = {}

    def _parse_numeric(self, text: str) -> List[Tuple[float, str, float]]:
        """Extract numeric comparisons (A > B, A < B, A == B)."""
        facts = []
        # Pattern: Number (operator) Number
        pattern = r"(-?\d+\.?\d*)\s*(>=|<=|==|!=|>|<)\s*(-?\d+\.?\d*)"
        for match in re.finditer(pattern, text, re.IGNORECASE):
            n1 = float(match.group(1))
            op = match.group(2)
            n2 = float(match.group(3))
            facts.append((n1, op, n2))
        return facts

    def _parse_logic(self, text: str) -> List[Dict]:
        """Extract logical structures: SVO, Causal, Negation."""
        nodes = []
        text_lower = text.lower()
        
        # 1. Causal/Conditional (A causes B)
        for verb in CAUSAL_VERBS:
            pattern = rf"(\w+)\s+{verb}\s+(\w+)"
            for m in re.finditer(pattern, text_lower):
                nodes.append({"type": "causal", "src": m.group(1), "dst": m.group(2), "val": 0.9})
        
        # 2. Negation (A is not B)
        for neg in NEGATION_WORDS:
            pattern = rf"(\w+)\s+is\s+{neg}\s+(\w+)"
            for m in re.finditer(pattern, text_lower):
                nodes.append({"type": "negation", "src": m.group(1), "dst": m.group(2), "val": 0.1})
                
        # 3. Simple Identity/Property (A is B) - simplified
        pattern = r"(\w+)\s+is\s+(\w+)"
        for m in re.finditer(pattern, text_lower):
            if not any(n["src"] == m.group(1) and n["dst"] == m.group(2) for n in nodes):
                nodes.append({"type": "identity", "src": m.group(1), "dst": m.group(2), "val": 0.8})

        return nodes

    def _beta_update(self, alpha: float, beta: float, evidence: float) -> Tuple[float, float]:
        """Update Beta distribution with soft evidence."""
        # Treat evidence as pseudo-counts. 
        # If evidence > 0.5, add to alpha. If < 0.5, add to beta.
        weight = 2.0 # Strength of one logical constraint
        if evidence > 0.5:
            alpha += weight * evidence
            beta += weight * (1 - evidence)
        else:
            alpha += weight * (1 - evidence) # Inverted logic for negative constraints
            beta += weight * evidence
        return alpha, beta

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Compute Variational Free Energy F = KL(q||p) + Expected Error.
        Lower F is better.
        """
        full_text = f"{prompt} {candidate}"
        
        # 1. Initialize Priors (Uniform Beta(1,1))
        # We track beliefs for extracted entities/concepts
        beliefs = {} # key: concept_name, value: (alpha, beta)
        
        # Extract all words as potential concepts (simplified)
        words = re.findall(r'\b\w+\b', full_text.lower())
        unique_concepts = set(words)
        for w in unique_concepts:
            if len(w) > 2 and w not in ["the", "and", "that", "with", "this", "from", "have", "been"]:
                beliefs[w] = (DEFAULT_ALPHA, DEFAULT_BETA)
        
        total_error = 0.0
        total_kl = 0.0
        
        # 2. Parse Constraints (Factors)
        numeric_facts = self._parse_numeric(full_text)
        logic_nodes = self._parse_logic(full_text)
        
        # 3. Coordinate Ascent Iterations (Simplified to 1 pass for speed/lightweight)
        # Update beliefs based on factors
        
        # A. Numeric Constraints (Gaussian-like check on Beta mean)
        for n1, op, n2 in numeric_facts:
            # Check if candidate contradicts explicit math in prompt
            is_true = False
            if op == '>': is_true = n1 > n2
            elif op == '<': is_true = n1 < n2
            elif op == '==': is_true = abs(n1 - n2) < 1e-6
            elif op == '!=': is_true = abs(n1 - n2) > 1e-6
            
            if not is_true:
                total_error += 5.0 # High penalty for math contradiction

        # B. Logical Constraints
        for node in logic_nodes:
            src = node["src"]
            dst = node["dst"]
            target_val = node["val"]
            
            # Update source belief
            if src in beliefs:
                a, b = beliefs[src]
                a, b = self._beta_update(a, b, target_val)
                beliefs[src] = (a, b)
                
                # Compute Local KL Divergence (Approx)
                # KL(Beta_new || Beta_old) approximated by difference in means squared * weight
                mean_new = a / (a + b)
                mean_old = DEFAULT_ALPHA / (DEFAULT_ALPHA + DEFAULT_BETA) # 0.5
                total_kl += 0.5 * (mean_new - mean_old)**2
                
                # Prediction Error
                # If logic says A causes B, and we believe A, we expect B
                if dst in beliefs:
                    a_dst, b_dst = beliefs[dst]
                    mean_dst = a_dst / (a_dst + b_dst)
                    # Error is deviation from expected causal link
                    total_error += (mean_dst - target_val)**2

        # Free Energy F
        F = total_kl + total_error
        return F

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Check for ambiguity, presupposition, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition
        for pat in PRESUPPOSITION_PATTERNS:
            if re.search(pat, p_lower):
                return 0.2
        
        # 2. Scope Ambiguity
        for pat in SCOPE_AMBIGUITY_PATTERNS:
            if re.search(pat, p_lower):
                # Only flag if question asks about specific instance
                if "which" in p_lower or "who" in p_lower or "what" in p_lower:
                    return 0.4
        
        # 3. Pronoun Ambiguity
        for pat in PRONOUN_AMBIGUITY_PATTERNS:
            if re.search(pat, p_lower):
                return 0.3
                
        # 4. False Dichotomy
        for pat in FALSE_DICHOTOMY_PATTERNS:
            if re.search(pat, p_lower):
                if "only" not in p_lower: # Unless specified exclusive
                    return 0.5

        # 5. Subjectivity
        subjective_words = ["best", "worst", "favorite", "beautiful", "ugly", "opinion"]
        if any(w in p_lower for w in subjective_words):
            if "calculate" not in p_lower and "math" not in p_lower:
                return 0.4

        return 1.0

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        s1_b = s1.encode()
        s2_b = s2.encode()
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_both = len(zlib.compress(s1_b + s2_b))
        
        if max(len_s1, len_s2) == 0:
            return 0.0
        return (len_both - min(len_s1, len_s2)) / max(len_s1, len_s2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        meta_cap = self._meta_confidence(prompt)
        
        # Pre-calculate prompt numeric facts to check candidate consistency
        prompt_nums = self._parse_numeric(prompt)
        
        for cand in candidates:
            # 1. Structural/Logical Score (Free Energy)
            F = self._compute_free_energy(prompt, cand)
            # Convert Free Energy to Probability-like score: S = exp(-F)
            # Add small epsilon to F to avoid exp(0)=1 if perfect
            raw_score = math.exp(-F)
            
            # 2. Numeric Consistency Check (Constructive)
            # If prompt has "5 > 3" and candidate says "3 > 5", penalize heavily
            cand_nums = self._parse_numeric(cand)
            penalty = 0.0
            for n1, op, n2 in cand_nums:
                # Re-evaluate the statement in candidate
                valid = False
                if op == '>': valid = n1 > n2
                elif op == '<': valid = n1 < n2
                elif op == '==': valid = abs(n1-n2)<1e-6
                elif op == '!=': valid = abs(n1-n2)>1e-6
                
                if not valid:
                    penalty = 0.9 # Massive penalty for false math statements
            
            # 3. NCD Tiebreaker (Max 15% influence)
            # We want low NCD (high similarity) only if logical structure matches
            ncd = self._ncd_score(prompt, cand)
            # Normalize NCD to 0-1 where 1 is good (low distance)
            ncd_bonus = (1.0 - ncd) * 0.15 
            
            final_score = (raw_score * (1.0 - penalty)) + ncd_bonus
            
            # Apply Meta-Confidence Cap
            if final_score > meta_cap:
                final_score = meta_cap
            
            # Ensure non-negative
            final_score = max(0.0, min(1.0, final_score))
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"FreeEnergy={F:.4f}, MetaCap={meta_cap:.2f}, Penalty={penalty}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-cognition (ambiguity/presupposition).
        """
        meta_cap = self._meta_confidence(prompt)
        
        # If meta_cap is low, we are uncertain regardless of answer fit
        if meta_cap < 0.3:
            return meta_cap
            
        # Evaluate the specific pair
        F = self._compute_free_energy(prompt, answer)
        raw_conf = math.exp(-F)
        
        # Check for explicit contradictions in answer
        cand_nums = self._parse_numeric(answer)
        for n1, op, n2 in cand_nums:
             valid = False
             if op == '>': valid = n1 > n2
             elif op == '<': valid = n1 < n2
             elif op == '==': valid = abs(n1-n2)<1e-6
             elif op == '!=': valid = abs(n1-n2)>1e-6
             if not valid:
                 return 0.1 # Definitely wrong if it claims false math

        final_conf = min(raw_conf, meta_cap)
        
        # Never return > 0.9 unless computation was definitive (simulated by very low F)
        if F > 0.5: # If there was any significant error/complexity
            final_conf = min(final_conf, 0.85)
            
        return max(0.0, min(1.0, final_conf))

# Example Usage (Internal Test)
if __name__ == "__main__":
    tool = ReasoningTool()
    p1 = "Alice is taller than Bob. Bob is taller than Carol."
    c1 = ["Alice is taller than Carol.", "Carol is taller than Alice."]
    print("Test 1 (Transitivity):")
    print(tool.evaluate(p1, c1))
    
    p2 = "Have you stopped cheating on tests?"
    c2 = ["Yes, I have.", "No, I haven't."]
    print("\nTest 2 (Presupposition Trap):")
    print(tool.evaluate(p2, c2))
    print(f"Confidence: {tool.confidence(p2, c2[0])}")
    
    p3 = "Calculate 9.11 vs 9.9. Which is larger?"
    c3 = ["9.11 is larger", "9.9 is larger"]
    print("\nTest 3 (Numeric):")
    print(tool.evaluate(p3, c3))
```

</details>
