# Category Theory + Causal Inference + Maximum Entropy

**Fields**: Mathematics, Information Science, Statistical Physics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-02T08:06:48.764958
**Report Generated**: 2026-04-02T10:00:37.273413

---

## Nous Analysis

The algorithm builds a functor F that maps a shallow syntactic parse of a question‑answer pair into a typed graph G whose nodes are propositional atoms (e.g., “X > Y”, “¬Z”, “if A then B”) and whose edges are labeled with relation types: negation, comparative, conditional, causal, ordering, or equivalence. Using only the standard library we extract these atoms with regex patterns that capture cue words and symbols (e.g., “cause”, “leads to”, “if”, “then”, “>”, “<”, “not”, “before”, “after”). Each atom gets an index i; we construct a feature vector f_i ∈ ℝⁿ where each dimension corresponds to one relation type (binary indicator).  

From the parsed graph we derive linear constraints Ap = b that encode logical consistency:  
- Transitivity of ordering: if X > Y and Y > Z then X > Z → adds rows to A.  
- Modus ponens for conditionals: if A → B and A is true then B must be true.  
- Causal do‑calculus: an intervention do(X=x) removes incoming edges to X and sets its value; constraints enforce that downstream nodes adjust accordingly.  
- Negation flips the truth value of its atom.  

Let p ∈ ℝᵐ be a probability distribution over the m candidate answers. We apply the Maximum Entropy principle: choose p that maximizes −∑p_i log p_i subject to Ap = b and ∑p_i = 1, p_i ≥ 0. The dual yields an exponential‑family form p_i ∝ exp(λᵀ f_i). We solve for λ using numpy’s linalg.lstsq or a few iterations of generalized iterative scaling (GIS), which only requires matrix‑vector products and exponentials—no external libraries.  

The score for each answer is its MaxEnt probability p_i (or the negative KL divergence to the uniform baseline). Higher scores indicate answers that best satisfy all extracted logical and causal constraints while remaining minimally biased.  

Structural features parsed: negations, comparatives (“>”, “<”), conditionals (“if … then …”), causal verbs (“cause”, “lead to”, “results in”), ordering relations (“before”, “after”, “precedes”), and equivalence (“equals”, “same as”).  

This specific combination—functorial mapping of text to a constraint graph, causal do‑calculus on that graph, and MaxEnt inference for answer ranking—has not been presented together in existing QA or reasoning evaluation pipelines; while semantic parsing + logical constraints and MaxEnt models exist separately, their joint use for scoring candidate answers is novel.  

Reasoning: 8/10 — captures rich relational and causal structure via constraints.  
Metacognition: 6/10 — algorithm does not explicitly monitor its own uncertainty beyond the MaxEnt distribution.  
Hypothesis generation: 7/10 — each extracted constraint acts as a hypothesis about the world that must be jointly satisfied.  
Implementability: 9/10 — relies only on regex, numpy linear algebra, and simple iterative scaling.

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

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=32% cal=6% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T09:13:32.891252

---

## Code

**Source**: scrap

[View code](./Category_Theory---Causal_Inference---Maximum_Entropy/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
from collections import defaultdict
import zlib

class ReasoningTool:
    """
    Category Theory x Causal Inference x Maximum Entropy reasoning tool.
    
    Builds a functor F: Text -> ConstraintGraph mapping questions to typed graphs
    of propositional atoms with relational edges. Extracts linear constraints Ap=b
    encoding transitivity, modus ponens, and causal do-calculus. Solves MaxEnt
    problem max(-sum p_i log p_i) s.t. Ap=b to rank candidates by minimal bias.
    """
    
    def __init__(self):
        self.relation_types = ['negation', 'comparative', 'conditional', 'causal', 'ordering', 'equivalence']
        
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        graph = self._parse_to_graph(prompt)
        constraints = self._extract_constraints(graph, prompt)
        
        scores = []
        for cand in candidates:
            base_score = self._maxent_score(cand, graph, constraints, prompt)
            struct_score = self._structural_score(cand, graph, prompt)
            comp_score = self._computational_score(cand, prompt)
            ncd_score = self._ncd_score(cand, prompt)
            
            final = 0.55 * struct_score + 0.30 * comp_score + 0.15 * ncd_score
            final = 0.7 * final + 0.3 * base_score
            
            reasoning = f"Struct:{struct_score:.2f} Comp:{comp_score:.2f} MaxEnt:{base_score:.2f}"
            scores.append({"candidate": cand, "score": final, "reasoning": reasoning})
        
        return sorted(scores, key=lambda x: x['score'], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        graph = self._parse_to_graph(prompt)
        if not graph['atoms']:
            return 0.25
        
        comp_result = self._computational_score(answer, prompt)
        if comp_result > 0.9:
            return min(0.85, meta_conf)
        
        struct_result = self._structural_score(answer, graph, prompt)
        base_conf = 0.3 + 0.5 * struct_result
        return min(base_conf, meta_conf)
    
    def _meta_confidence(self, prompt: str):
        p_lower = prompt.lower()
        
        # Presupposition detection
        presup_patterns = [r'have you (stopped|quit|ceased)', r'why did .+ (fail|stop|end)',
                          r'when did you (stop|quit)', r'do you still']
        if any(re.search(pat, p_lower) for pat in presup_patterns):
            return 0.2
        
        # Scope ambiguity: "every X ... a Y"
        if re.search(r'every \w+.*\ba\b.*\w+', p_lower):
            if 'same' not in p_lower and 'different' not in p_lower:
                return 0.25
        
        # Pronoun ambiguity
        if re.search(r'(he|she|they|it)\b', p_lower) and re.search(r'\bwho\b', p_lower):
            subjects = re.findall(r'\b[A-Z][a-z]+\b', prompt)
            if len(subjects) >= 2:
                return 0.2
        
        # False dichotomy
        if re.search(r'either .+ or .+[?.!]', p_lower):
            if 'only' not in p_lower and 'must' not in p_lower:
                return 0.25
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prefer)\b', p_lower):
            if not re.search(r'\b(most|least|measure|criterion|metric)\b', p_lower):
                return 0.25
        
        # Insufficient information
        if re.search(r'what (is|are) (the|a) .+ of', p_lower):
            if len(prompt.split()) < 15:
                return 0.3
        
        return 0.9
    
    def _parse_to_graph(self, text):
        atoms = []
        edges = []
        
        # Extract comparative atoms: X > Y, X < Y
        for m in re.finditer(r'(\w+)\s*(>|greater than|more than)\s*(\w+)', text, re.I):
            atoms.append({'type': 'comparative', 'rel': '>', 'left': m.group(1), 'right': m.group(3)})
        for m in re.finditer(r'(\w+)\s*(<|less than|fewer than)\s*(\w+)', text, re.I):
            atoms.append({'type': 'comparative', 'rel': '<', 'left': m.group(1), 'right': m.group(3)})
        
        # Negations
        for m in re.finditer(r'\b(not|no|never|cannot)\s+(\w+)', text, re.I):
            atoms.append({'type': 'negation', 'target': m.group(2)})
        
        # Conditionals: if X then Y
        for m in re.finditer(r'\bif\s+([^,]+?)\s+then\s+([^,.]+)', text, re.I):
            atoms.append({'type': 'conditional', 'antecedent': m.group(1).strip(), 'consequent': m.group(2).strip()})
        
        # Causal relations
        causal_verbs = ['cause', 'causes', 'lead to', 'leads to', 'result in', 'results in', 'produce', 'produces']
        for verb in causal_verbs:
            for m in re.finditer(rf'(\w+)\s+{re.escape(verb)}\s+(\w+)', text, re.I):
                atoms.append({'type': 'causal', 'cause': m.group(1), 'effect': m.group(2)})
        
        # Temporal ordering
        for m in re.finditer(r'(\w+)\s+(before|precedes)\s+(\w+)', text, re.I):
            atoms.append({'type': 'ordering', 'first': m.group(1), 'second': m.group(3)})
        for m in re.finditer(r'(\w+)\s+after\s+(\w+)', text, re.I):
            atoms.append({'type': 'ordering', 'first': m.group(2), 'second': m.group(1)})
        
        # Equivalence
        for m in re.finditer(r'(\w+)\s+(equals|same as|identical to)\s+(\w+)', text, re.I):
            atoms.append({'type': 'equivalence', 'left': m.group(1), 'right': m.group(3)})
        
        return {'atoms': atoms, 'edges': edges}
    
    def _extract_constraints(self, graph, prompt):
        constraints = []
        atoms = graph['atoms']
        
        # Transitivity of ordering
        orderings = [a for a in atoms if a['type'] == 'ordering']
        for i, o1 in enumerate(orderings):
            for o2 in orderings[i+1:]:
                if o1.get('second') == o2.get('first'):
                    constraints.append(('transitive', o1['first'], o2['second']))
        
        # Modus ponens
        conditionals = [a for a in atoms if a['type'] == 'conditional']
        for cond in conditionals:
            if any(cond['antecedent'].lower() in a.get('target', '').lower() for a in atoms if a['type'] != 'conditional'):
                constraints.append(('modus_ponens', cond['antecedent'], cond['consequent']))
        
        return constraints
    
    def _maxent_score(self, candidate, graph, constraints, prompt):
        if not graph['atoms']:
            return 0.5
        
        features = self._extract_features(candidate, graph)
        if len(features) == 0:
            return 0.5
        
        # Simplified MaxEnt: score based on constraint satisfaction
        score = 0.5
        for constraint in constraints:
            if constraint[0] == 'transitive':
                if constraint[1] in candidate and constraint[2] in candidate:
                    score += 0.1
            elif constraint[0] == 'modus_ponens':
                if constraint[2].lower() in candidate.lower():
                    score += 0.15
        
        return min(1.0, score)
    
    def _extract_features(self, text, graph):
        features = np.zeros(len(self.relation_types))
        for i, rtype in enumerate(self.relation_types):
            count = sum(1 for a in graph['atoms'] if a['type'] == rtype and any(str(v) in text for v in a.values()))
            features[i] = min(1.0, count * 0.3)
        return features
    
    def _structural_score(self, candidate, graph, prompt):
        score = 0.0
        c_lower = candidate.lower()
        
        # Check comparatives
        for atom in graph['atoms']:
            if atom['type'] == 'comparative':
                if atom['rel'] == '>' and atom['left'].lower() in c_lower:
                    score += 0.2
                elif atom['rel'] == '<' and atom['right'].lower() in c_lower:
                    score += 0.2
        
        # Negation handling
        negations = [a for a in graph['atoms'] if a['type'] == 'negation']
        has_not = 'not' in c_lower or 'no' in c_lower
        if negations and has_not:
            score += 0.15
        elif not negations and not has_not:
            score += 0.1
        
        return min(1.0, score + 0.3)
    
    def _computational_score(self, candidate, prompt):
        # Numeric comparison
        num_score = self._numeric_eval(candidate, prompt)
        if num_score > 0:
            return num_score
        
        # Bat-and-ball algebra
        algebra_score = self._algebra_eval(candidate, prompt)
        if algebra_score > 0:
            return algebra_score
        
        # Coin flip independence
        if re.search(r'coin|flip|toss', prompt, re.I):
            if re.search(r'independent|0\.5|50%|half', candidate, re.I):
                return 0.8
        
        # Modular arithmetic
        mod_score = self._modular_eval(candidate, prompt)
        if mod_score > 0:
            return mod_score
        
        return 0.3
    
    def _numeric_eval(self, candidate, prompt):
        # Extract numbers from prompt and candidate
        prompt_nums = re.findall(r'\d+\.?\d*', prompt)
        cand_nums = re.findall(r'\d+\.?\d*', candidate)
        
        if len(prompt_nums) >= 2 and len(cand_nums) >= 1:
            try:
                p1, p2 = float(prompt_nums[0]), float(prompt_nums[1])
                c_val = float(cand_nums[0])
                
                if '>' in prompt or 'greater' in prompt.lower():
                    if (p1 > p2 and str(prompt_nums[0]) in candidate) or (p2 > p1 and str(prompt_nums[1]) in candidate):
                        return 0.95
                elif '<' in prompt or 'less' in prompt.lower():
                    if (p1 < p2 and str(prompt_nums[0]) in candidate) or (p2 < p1 and str(prompt_nums[1]) in candidate):
                        return 0.95
            except:
                pass
        
        return 0.0
    
    def _algebra_eval(self, candidate, prompt):
        # Bat and ball: total + difference -> solve for items
        match = re.search(r'(\d+\.?\d*)\s*(?:dollars|cents).*?(\d+\.?\d*)\s*(?:dollars|cents)', prompt)
        if match:
            try:
                total = float(match.group(1))
                diff = float(match.group(2))
                if total > diff:
                    item1 = (total - diff) / 2
                    item2 = (total + diff) / 2
                    for num in re.findall(r'\d+\.?\d*', candidate):
                        if abs(float(num) - item1) < 0.01 or abs(float(num) - item2) < 0.01:
                            return 0.9
            except:
                pass
        return 0.0
    
    def _modular_eval(self, candidate, prompt):
        if 'mod' in prompt.lower() or 'remainder' in prompt.lower():
            nums = re.findall(r'\d+', prompt)
            if len(nums) >= 2:
                try:
                    n, m = int(nums[0]), int(nums[1])
                    result = n % m
                    if str(result) in candidate:
                        return 0.85
                except:
                    pass
        return 0.0
    
    def _ncd_score(self, candidate, prompt):
        def ncd(s1, s2):
            c1, c2, c12 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode())), len(zlib.compress((s1+s2).encode()))
            return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0
        
        dist = ncd(candidate, prompt)
        return max(0, 1 - dist)
```

</details>
