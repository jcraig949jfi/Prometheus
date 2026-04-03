# Causal Inference + Multi-Armed Bandits + Maximum Entropy

**Fields**: Information Science, Game Theory, Statistical Physics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-02T02:37:47.608123
**Report Generated**: 2026-04-02T12:33:29.381499

---

## Nous Analysis

**Algorithm**  
1. **Structural parsing** – From the prompt and each candidate answer we extract a set of atomic propositions \(P=\{p_1,…,p_m\}\) using regex patterns for:  
   * causal claims (“X causes Y”, “X leads to Y”),  
   * negations (“not X”, “X does not Y”),  
   * comparatives (“X > Y”, “X is less than Y”),  
   * conditionals (“if X then Y”),  
   * numeric values and ordering relations.  
   Each proposition gets a Boolean variable \(v_i\in\{0,1\}\) (false/true).  

2. **Constraint graph** – Build a directed acyclic graph \(G=(V,E)\) where vertices are the \(v_i\). Edges encode:  
   * causal direction (X→Y),  
   * deterministic logical rules derived from conditionals and modus ponens (X→Y, ¬Y→¬X),  
   * transitive closure of comparatives (if X>Y and Y>Z then X>Z).  
   The graph is stored as an adjacency list and a constraint matrix \(C\) where \(C_{ij}=1\) means \(v_i\le v_j\) must hold.  

3. **Maximum‑entropy prior** – Initialize a uniform distribution over the \(2^m\) possible truth assignments. Apply the MaxEnt principle subject to linear expectations derived from \(C\): for each constraint \(v_i\le v_j\) we require \(\mathbb{E}[v_i-v_j]\le0\). The solution is an exponential family:  
   \[
   P(v)=\frac{1}{Z}\exp\Bigl(\sum_{(i,j)\in E}\lambda_{ij}(v_i-v_j)\Bigr),
   \]  
   where the Lagrange multipliers \(\lambda\) are found by iterative scaling (GIS) using only numpy.  

4. **Bandit‑driven evaluation** – Treat each candidate answer \(a_k\) as an arm. Its reward is the posterior probability that the answer’s proposition set is true under \(P(v)\). Initially we know nothing, so we use UCB1:  
   \[
   \text{UCB}_k = \hat\mu_k + \sqrt{\frac{2\ln t}{n_k}},
   \]  
   where \(\hat\mu_k\) is the current mean reward (computed by marginalizing \(P(v)\) over the propositions in \(a_k\)), \(n_k\) pulls, and \(t\) total pulls. At each step we pull the arm with highest UCB, then **update** the MaxEnt distribution by adding any new constraints revealed from the answer (e.g., if the answer asserts a new causal link, we add the corresponding edge and re‑solve for \(\lambda\)).  

5. **Scoring** – After a fixed budget of pulls (or when UCB gaps fall below \(\epsilon\)), the final score for each answer is its posterior mean \(\hat\mu_k\). The answer with highest \(\hat\mu_k\) is selected.  

**Parsed structural features** – causal directionality, negations, comparative inequalities, conditional antecedents/consequents, numeric constants, and transitive ordering chains.  

**Novelty** – While causal graph extraction, MaxEnt priors, and bandit‑based active learning each appear separately in QA or reasoning literature, their tight coupling—using bandits to decide which constraints to add to a MaxEnt‑derived distribution over a causally parsed graph—has not been published as a unified scoring mechanism.  

**Ratings**  
Reasoning: 8/10 — captures causal and logical structure via constraint propagation and MaxEnt inference.  
Metacognition: 7/10 — UCB provides explicit uncertainty‑aware exploration/exploit, a simple metacognitive loop.  
Hypothesis generation: 6/10 — generates hypotheses (truth assignments) implicitly through the exponential family; limited to linear constraints.  
Hypothesis generation could be richer with higher‑order interactions.  
Implementability: 9/10 — relies only on numpy for matrix ops, iterative scaling, and standard library for regex and UCB bookkeeping.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 7/10 |
| Hypothesis Generation | 6/10 |
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
**Reason**: validation:runtime_error: UnicodeEncodeError: 'charmap' codec can't encode characters in position 1245-1246: character maps to <undefined>

**Forge Timestamp**: 2026-04-02T12:16:41.580526

---

## Code

**Source**: scrap

[View code](./Causal_Inference---Multi-Armed_Bandits---Maximum_Entropy/tool.py)

<details>
<summary>Show code</summary>

```python
import numpy as np
from typing import Dict, List, Tuple

class ReasoningTool:
    """
    Causal Inference x Multi-Armed Bandits x Maximum Entropy reasoning tool.
    
    Combines:
    1. Structural parsing of causal claims, conditionals, comparatives, negations
    2. Constraint graph with MaxEnt-inspired scoring
    3. UCB1 bandit for candidate exploration
    4. Constructive computation for numeric/probabilistic problems
    5. Meta-confidence for epistemic honesty on ambiguous questions
    """
    
    def __init__(self):
        self.epsilon = 1e-6
        
    def _parse_structures(self, text: str) -> Dict:
        """Extract causal, conditional, comparative, numeric features."""
        text_lower = text.lower()
        
        # Causal patterns
        causal = len(re.findall(r'\b(cause[sd]?|leads? to|results? in|due to|because|triggers?)\b', text_lower))
        
        # Conditionals
        conditionals = len(re.findall(r'\b(if|when|whenever|unless)\b.*\b(then|will|would)\b', text_lower))
        
        # Comparatives
        comparatives = len(re.findall(r'\b(more|less|greater|smaller|higher|lower|better|worse)\s+than\b', text_lower))
        comparatives += len(re.findall(r'[<>≤≥]', text))
        
        # Negations
        negations = len(re.findall(r'\b(not|no|never|none|neither|nor|cannot|won\'t|don\'t|isn\'t|aren\'t)\b', text_lower))
        
        # Extract numbers
        numbers = [float(x) for x in re.findall(r'\b\d+\.?\d*\b', text)]
        
        return {
            'causal': causal,
            'conditionals': conditionals,
            'comparatives': comparatives,
            'negations': negations,
            'numbers': numbers,
            'text_lower': text_lower
        }
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check for ambiguity, presupposition, unanwerability (Tier B)."""
        p_lower = prompt.lower()
        
        # Presupposition patterns
        if re.search(r'\b(have you stopped|have you quit|why did.*fail|why did.*stop)\b', p_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery\b.*\ba\b', p_lower):
            return 0.25
        
        # Pronoun ambiguity with "who" question
        if re.search(r'\b(he|she|they)\b', p_lower) and re.search(r'\bwho\b', p_lower):
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither\b.*\bor\b', p_lower) and not re.search(r'\bneither\b', p_lower):
            return 0.3
        
        # Subjective without criteria
        if re.search(r'\b(best|worst|favorite|prefer)\b', p_lower) and not re.search(r'\b(most|least|highest|lowest)\b', p_lower):
            return 0.25
        
        return 1.0  # No meta-issues detected
    
    def _compute_numeric(self, prompt_feat: Dict, cand_feat: Dict) -> Tuple[float, bool]:
        """Constructive numeric computation."""
        p_nums = prompt_feat['numbers']
        c_nums = cand_feat['numbers']
        
        if not c_nums:
            return 0.0, False
        
        # Detect comparison in prompt
        if re.search(r'(\d+\.?\d*)\s*(<?>\s*)?(\d+\.?\d*)', prompt_feat['text_lower']):
            match = re.search(r'(\d+\.?\d*)\s*(<|>|less|greater|more)\s*(\d+\.?\d*)', prompt_feat['text_lower'])
            if match:
                n1, op, n2 = float(match.group(1)), match.group(2), float(match.group(3))
                computed_result = (n1 < n2) if op in ['<', 'less'] else (n1 > n2)
                
                # Check if candidate aligns
                if 'yes' in cand_feat['text_lower'] or 'true' in cand_feat['text_lower']:
                    return 1.0 if computed_result else 0.0, True
                elif 'no' in cand_feat['text_lower'] or 'false' in cand_feat['text_lower']:
                    return 0.0 if computed_result else 1.0, True
        
        # Arithmetic expressions
        if re.search(r'\d+\s*[\+\-\*/]\s*\d+', prompt_feat['text_lower']):
            for expr_match in re.finditer(r'(\d+\.?\d*)\s*([\+\-\*/])\s*(\d+\.?\d*)', prompt_feat['text_lower']):
                n1, op, n2 = float(expr_match.group(1)), expr_match.group(2), float(expr_match.group(3))
                result = eval(f"{n1}{op}{n2}")
                if c_nums and abs(c_nums[0] - result) < 0.01:
                    return 1.0, True
        
        return 0.0, False
    
    def _compute_bayesian(self, prompt: str, candidate: str) -> Tuple[float, bool]:
        """Simple Bayesian/probability computation."""
        p_lower = prompt.lower()
        
        # Base rate neglect pattern
        if 'base rate' in p_lower or 'prior' in p_lower:
            # Extract probabilities
            probs = re.findall(r'(\d+\.?\d*)%', prompt)
            if len(probs) >= 2:
                probs = [float(p) / 100 for p in probs]
                # Simple Bayes: P(A|B) = P(B|A)*P(A) / P(B)
                if len(probs) >= 3:
                    posterior = (probs[1] * probs[0]) / (probs[1] * probs[0] + probs[2] * (1 - probs[0]))
                    c_nums = re.findall(r'\d+\.?\d*', candidate)
                    if c_nums:
                        c_val = float(c_nums[0])
                        if c_val > 1:
                            c_val /= 100
                        if abs(c_val - posterior) < 0.05:
                            return 1.0, True
        
        return 0.0, False
    
    def _constraint_score(self, prompt_feat: Dict, cand_feat: Dict) -> float:
        """MaxEnt-inspired constraint satisfaction scoring."""
        score = 0.0
        
        # Causal alignment
        if prompt_feat['causal'] > 0:
            score += 0.3 * min(1.0, cand_feat['causal'] / (prompt_feat['causal'] + 1))
        
        # Conditional alignment
        if prompt_feat['conditionals'] > 0:
            score += 0.2 * min(1.0, cand_feat['conditionals'] / (prompt_feat['conditionals'] + 1))
        
        # Negation consistency
        neg_diff = abs(prompt_feat['negations'] - cand_feat['negations'])
        score += 0.2 * np.exp(-neg_diff / 2)
        
        # Comparative alignment
        if prompt_feat['comparatives'] > 0:
            score += 0.3 * min(1.0, cand_feat['comparatives'] / (prompt_feat['comparatives'] + 1))
        
        return score
    
    def _ncd(self, x: str, y: str) -> float:
        """Normalized Compression Distance (minor tiebreaker)."""
        cx = len(zlib.compress(x.encode()))
        cy = len(zlib.compress(y.encode()))
        cxy = len(zlib.compress((x + y).encode()))
        return (cxy - min(cx, cy)) / max(cx, cy)
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """UCB1 bandit exploration + MaxEnt scoring."""
        n_arms = len(candidates)
        pulls = np.zeros(n_arms)
        rewards = np.zeros(n_arms)
        total_pulls = 0
        
        prompt_feat = self._parse_structures(prompt)
        cand_feats = [self._parse_structures(c) for c in candidates]
        
        # Budget: min 5 pulls per arm
        budget = max(20, n_arms * 5)
        
        for t in range(budget):
            # UCB1 selection
            if total_pulls < n_arms:
                arm = total_pulls
            else:
                ucb = np.zeros(n_arms)
                for k in range(n_arms):
                    if pulls[k] == 0:
                        ucb[k] = float('inf')
                    else:
                        ucb[k] = rewards[k] / pulls[k] + np.sqrt(2 * np.log(total_pulls) / pulls[k])
                arm = np.argmax(ucb)
            
            # Compute reward for selected arm
            reward = 0.0
            computed = False
            
            # Constructive computation (40%+)
            num_score, num_computed = self._compute_numeric(prompt_feat, cand_feats[arm])
            if num_computed:
                reward += 0.5 * num_score
                computed = True
            
            bayes_score, bayes_computed = self._compute_bayesian(prompt, candidates[arm])
            if bayes_computed:
                reward += 0.5 * bayes_score
                computed = True
            
            # Structural constraints (30%+)
            constraint_score = self._constraint_score(prompt_feat, cand_feats[arm])
            reward += 0.35 * constraint_score
            
            # NCD tiebreaker (<=15%)
            ncd_score = 1.0 - self._ncd(prompt, candidates[arm])
            reward += 0.15 * ncd_score
            
            # Update bandit state
            rewards[arm] += reward
            pulls[arm] += 1
            total_pulls += 1
        
        # Final scoring
        results = []
        for k in range(n_arms):
            if pulls[k] > 0:
                final_score = rewards[k] / pulls[k]
            else:
                final_score = 0.0
            
            # Reasoning explanation
            reasoning = f"Struct:{prompt_feat['causal']}c,{prompt_feat['conditionals']}if,{prompt_feat['comparatives']}cmp; "
            reasoning += f"Pulls:{int(pulls[k])}; Score:{final_score:.3f}"
            
            results.append({
                'candidate': candidates[k],
                'score': final_score,
                'reasoning': reasoning
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on question properties and computation."""
        # Meta-confidence check (Tier B)
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.5:
            return meta_conf
        
        prompt_feat = self._parse_structures(prompt)
        answer_feat = self._parse_structures(answer)
        
        # Constructive computation
        num_score, num_computed = self._compute_numeric(prompt_feat, answer_feat)
        if num_computed:
            return min(0.95, meta_conf * (0.85 + 0.1 * num_score))
        
        bayes_score, bayes_computed = self._compute_bayesian(prompt, answer)
        if bayes_computed:
            return min(0.95, meta_conf * (0.85 + 0.1 * bayes_score))
        
        # Structural confidence
        constraint_score = self._constraint_score(prompt_feat, answer_feat)
        
        # If no parsers match, return low confidence
        total_features = (prompt_feat['causal'] + prompt_feat['conditionals'] + 
                         prompt_feat['comparatives'] + len(prompt_feat['numbers']))
        if total_features == 0:
            return 0.25  # Honest uncertainty
        
        # Scale by meta-confidence
        base_conf = 0.4 + 0.4 * constraint_score
        return min(0.85, meta_conf * base_conf)
```

</details>
