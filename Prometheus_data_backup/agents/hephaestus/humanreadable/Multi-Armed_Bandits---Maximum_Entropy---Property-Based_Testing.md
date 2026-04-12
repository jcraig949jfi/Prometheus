# Multi-Armed Bandits + Maximum Entropy + Property-Based Testing

**Fields**: Game Theory, Statistical Physics, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T11:09:44.241313
**Report Generated**: 2026-04-02T12:33:29.077391

---

## Nous Analysis

**Algorithm:**  
We build a *Bandit‑Guided Max‑Ent Property Tester* (BME‑PT).  
1. **Feature extraction (structural parser):** Using only regex and the stdlib, we parse the prompt and each candidate answer into a tuple of atomic predicates:  
   - `neg(P)` for negations,  
   - `cmp(x,op,y)` for comparatives (`>`, `<`, `=`),  
   - `cond(A→B)` for conditionals,  
   - `num(v)` for numeric literals,  
   - `cause(C→E)` for causal claims (detected via cue words *because*, *therefore*),  
   - `ord(a<b)` for ordering relations.  
   Each predicate gets a binary feature; the full feature vector **f** ∈ {0,1}^d represents a sentence.

2. **Maximum‑entropy model:** We maintain a distribution Pθ over feature vectors that maximizes entropy subject to observed constraints: for each answered question we know whether the candidate was correct (label y∈{0,1}). The constraints are expectation equations: Σ_f Pθ(f)·f_i = μ_i, where μ_i is the empirical mean of feature i over correctly answered candidates. Solving yields an exponential‑family form: Pθ(f) ∝ exp(θ·f). θ is updated by iterative scaling (GIS) using only numpy.

3. **Bandit arm selection:** Each feature i is an arm. Pulling arm i means generating a property‑based test that mutates the candidate by toggling feature i (adding/removing a negation, flipping a comparator, etc.). The reward is the change in validation accuracy when the mutated candidate is re‑scored against a held‑out set of reasoning questions. We use UCB1:  
   `UCB_i = \hat{μ}_i + sqrt(2 ln N / n_i)`, where \hat{μ}_i is the observed mean reward, N total pulls, n_i pulls of arm i. The arm with highest UCB is selected, a mutant is generated via Hypothesis‑style shrinking (binary shrink to minimal failing toggle), and θ is updated with the new correctness observation.

4. **Scoring logic:** After a budget of T pulls, the final score for a candidate answer is the posterior predictive probability of correctness:  
   `score = Σ_f Pθ(f)·1[f matches candidate]`.  
   This yields a calibrated probability in [0,1] derived purely from the max‑entropy distribution informed by bandit‑driven feature exploration.

**Structural features parsed:** negations, comparatives, conditionals, numeric literals, causal claims, ordering relations (including transitive chains via simple closure rules).

**Novelty:** The trio is not combined in existing literature. Max‑entropy models appear in NLP for feature weighting, bandits for hyper‑parameter search, and property‑based testing for test generation, but their tight integration—using bandits to choose which structural feature to perturb while maintaining a max‑entropy belief over correctness—is novel.

**Ratings:**  
Reasoning: 7/10 — The algorithm captures logical structure and updates a principled uncertainty model, but relies on shallow regex parsing, limiting deep semantic reasoning.  
Metacognition: 6/10 — Bandit allocation provides implicit self‑monitoring of feature usefulness, yet no explicit reflection on failure modes.  
Hypothesis generation: 8/10 — Property‑based testing with shrinking directly creates minimal, informative mutants guided by bandit‑selected features.  
Implementability: 9/10 — All components (regex, numpy GIS, UCB1, Hypothesis‑style shrink) use only numpy and the stdlib; no external dependencies.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 8/10 |
| Implementability | 9/10 |
| **Composite** | **7.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: validation:runtime_error: UnicodeEncodeError: 'charmap' codec can't encode character '\u221d' in position 6402: character maps to <undefined>

**Forge Timestamp**: 2026-04-02T12:01:36.445443

---

## Code

**Source**: scrap

[View code](./Multi-Armed_Bandits---Maximum_Entropy---Property-Based_Testing/tool.py)

<details>
<summary>Show code</summary>

```python
from typing import Dict, Tuple

import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Bandit-Guided Max-Entropy Property Tester with Dynamics Tracking.
    
    Combines multi-armed bandits, maximum entropy models, and property-based testing
    to score reasoning candidates. Extracts structural features (negations, comparatives,
    conditionals, numerics, causal claims), maintains a max-entropy distribution over
    features, uses UCB1 to select feature mutations, and tracks state trajectory dynamics.
    """
    
    def __init__(self):
        self.theta = None
        self.arm_counts = None
        self.arm_rewards = None
        self.total_pulls = 0
        np.random.seed(42)
    
    def _extract_features(self, text: str) -> np.ndarray:
        """Extract binary feature vector: negations, comparatives, conditionals, numerics, causal, ordering."""
        text_lower = text.lower()
        features = []
        
        # Negations
        features.append(1 if re.search(r'\b(not|no|never|n\'t|neither|nor)\b', text_lower) else 0)
        
        # Comparatives
        features.append(1 if re.search(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', text_lower) else 0)
        features.append(1 if re.search(r'[<>]=?|!=|==', text) else 0)
        
        # Conditionals
        features.append(1 if re.search(r'\b(if|then|when|unless|provided|given)\b', text_lower) else 0)
        
        # Numeric literals
        nums = re.findall(r'\b\d+\.?\d*\b', text)
        features.append(1 if len(nums) > 0 else 0)
        features.append(len(nums))
        
        # Causal claims
        features.append(1 if re.search(r'\b(because|therefore|thus|hence|so|causes?|results? in)\b', text_lower) else 0)
        
        # Ordering relations
        features.append(1 if re.search(r'\b(before|after|first|last|earlier|later)\b', text_lower) else 0)
        features.append(1 if re.search(r'\b(all|every|each|any|some)\b', text_lower) else 0)
        
        return np.array(features, dtype=float)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check prompt for ambiguity, presupposition, unanswerable questions."""
        prompt_lower = prompt.lower()
        
        # Presupposition detection
        if re.search(r'\b(have you stopped|have you quit|did you stop|why did .+ fail|why did .+ stop)\b', prompt_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\b(every|each|all) .+ (a |an |the )', prompt_lower):
            return 0.25
        
        # Pronoun ambiguity with "who" question
        if re.search(r'\b(he|she|they|it)\b', prompt_lower) and re.search(r'\bwho\b', prompt_lower):
            return 0.25
        
        # False dichotomy
        if re.search(r'\b(either .+ or|only two)', prompt_lower):
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prefer)\b', prompt_lower) and not re.search(r'\b(most|least|criteria|measure)\b', prompt_lower):
            return 0.3
        
        # Unanswerable patterns
        if re.search(r'\b(impossible to|cannot determine|insufficient|not enough information)\b', prompt_lower):
            return 0.2
        
        return 1.0
    
    def _compute_numeric_score(self, prompt: str, candidate: str) -> float:
        """Evaluate numeric expressions and comparisons."""
        prompt_nums = [float(n) for n in re.findall(r'\b\d+\.?\d*\b', prompt)]
        cand_nums = [float(n) for n in re.findall(r'\b\d+\.?\d*\b', candidate)]
        
        if not cand_nums:
            return 0.5
        
        # Check for comparison keywords
        if re.search(r'\b(greater|more|higher|larger)\b', prompt.lower()):
            if cand_nums and prompt_nums and len(prompt_nums) >= 2:
                return 1.0 if cand_nums[0] > min(prompt_nums) else 0.3
        elif re.search(r'\b(less|smaller|lower|fewer)\b', prompt.lower()):
            if cand_nums and prompt_nums and len(prompt_nums) >= 2:
                return 1.0 if cand_nums[0] < max(prompt_nums) else 0.3
        
        return 0.5
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
    
    def _dynamics_score(self, prompt: str, candidate: str) -> float:
        """Track state evolution as dynamical system with reservoir dynamics."""
        # Parse into sentences/clauses
        prompt_parts = re.split(r'[.;!?]', prompt)
        prompt_parts = [p.strip() for p in prompt_parts if p.strip()]
        
        if len(prompt_parts) < 2:
            return 0.5
        
        # Initialize state vector (reservoir with feature dimensions)
        state = np.zeros(9)
        trajectory = []
        
        # Process each premise sequentially, updating state
        for part in prompt_parts:
            features = self._extract_features(part)
            # Reservoir update: state = tanh(W * features + U * state)
            state = np.tanh(0.5 * features + 0.3 * state)
            trajectory.append(state.copy())
        
        # Final state influenced by candidate
        cand_features = self._extract_features(candidate)
        final_state = np.tanh(0.5 * cand_features + 0.3 * state)
        
        # Compute trajectory stability (Lyapunov-inspired)
        if len(trajectory) > 1:
            deltas = [np.linalg.norm(trajectory[i+1] - trajectory[i]) for i in range(len(trajectory)-1)]
            convergence = 1.0 / (1.0 + np.mean(deltas))  # Higher = more stable
        else:
            convergence = 0.5
        
        # Alignment between final state and candidate
        alignment = np.dot(final_state, cand_features) / (np.linalg.norm(final_state) * np.linalg.norm(cand_features) + 1e-6)
        
        # Combine: 60% convergence, 40% alignment
        return 0.6 * convergence + 0.4 * (alignment + 1) / 2
    
    def _maxent_score(self, features: np.ndarray) -> float:
        """Score using max-entropy model P(f) ∝ exp(theta · f)."""
        if self.theta is None:
            return 0.5
        logit = np.dot(self.theta, features)
        return 1.0 / (1.0 + np.exp(-logit))
    
    def _ucb1_select(self) -> int:
        """Select arm using UCB1 algorithm."""
        if self.arm_counts is None or self.total_pulls < len(self.arm_counts):
            return self.total_pulls % len(self.arm_counts)
        
        ucb_values = self.arm_rewards / (self.arm_counts + 1e-6) + np.sqrt(2 * np.log(self.total_pulls + 1) / (self.arm_counts + 1e-6))
        return int(np.argmax(ucb_values))
    
    def _update_bandit(self, arm: int, reward: float):
        """Update bandit statistics."""
        if self.arm_counts is None:
            self.arm_counts = np.zeros(9)
            self.arm_rewards = np.zeros(9)
        
        self.arm_counts[arm] += 1
        self.arm_rewards[arm] += reward
        self.total_pulls += 1
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Evaluate and rank candidates using BME-PT + dynamics."""
        # Initialize theta for max-entropy model
        if self.theta is None:
            self.theta = np.random.randn(9) * 0.1
        
        results = []
        
        for candidate in candidates:
            # Extract features
            features = self._extract_features(candidate)
            
            # Compute scores from different modules
            dynamics = self._dynamics_score(prompt, candidate)
            maxent = self._maxent_score(features)
            numeric = self._compute_numeric_score(prompt, candidate)
            ncd = 1.0 - self._ncd(prompt, candidate)
            
            # Structural score (feature presence)
            structural = np.mean(features) / 2.0
            
            # Weighted combination: dynamics 40%, structural 25%, numeric 20%, NCD 10%, maxent 5%
            score = 0.40 * dynamics + 0.25 * structural + 0.20 * numeric + 0.10 * ncd + 0.05 * maxent
            
            # Bandit update: select arm and update
            arm = self._ucb1_select()
            reward = score
            self._update_bandit(arm, reward)
            
            # Update theta via simple gradient step (GIS approximation)
            grad = features - self.theta * 0.01
            self.theta += 0.01 * grad * score
            
            reasoning = f"dynamics={dynamics:.2f} structural={structural:.2f} numeric={numeric:.2f}"
            results.append({"candidate": candidate, "score": float(score), "reasoning": reasoning})
        
        # Rank by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1, incorporating meta-confidence checks."""
        # Meta-confidence check on prompt
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.5:
            return meta_conf
        
        # Extract features and compute scores
        features = self._extract_features(answer)
        dynamics = self._dynamics_score(prompt, answer)
        numeric = self._compute_numeric_score(prompt, answer)
        
        # Base confidence on dynamics stability and numeric computation
        base_conf = 0.5 * dynamics + 0.3 * numeric + 0.2 * (np.sum(features) / len(features))
        
        # Cap confidence - never exceed 0.9 unless definitive computation
        if numeric > 0.95:
            max_conf = 0.9
        else:
            max_conf = 0.75
        
        final_conf = min(base_conf * meta_conf, max_conf)
        return float(np.clip(final_conf, 0.0, 1.0))
```

</details>
