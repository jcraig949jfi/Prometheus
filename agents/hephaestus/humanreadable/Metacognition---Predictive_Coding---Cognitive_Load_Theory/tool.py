"""
Metacognition x Predictive Coding x Cognitive Load Theory Reasoning Tool

Pipeline:
1. Parse prompt & candidates into propositions using regex
2. Build predictive model from prompt (expected types, values)
3. Compute prediction error for each candidate proposition
4. Calibrate confidence via Bayesian update on error signals
5. Assess cognitive load (complexity penalty)
6. Propagate constraints via transitivity/modus ponens
7. Aggregate scores weighted by metacognitive agreement
"""

import re
import zlib
import numpy as np
from forge_primitives import (
    modus_ponens, check_transitivity, bayesian_update,
    confidence_from_agreement, information_sufficiency, entropy
)


class ReasoningTool:
    def __init__(self):
        self.w1, self.w2, self.w3, self.w4 = 0.4, 0.3, 0.2, 0.1
        self.alpha, self.beta, self.gamma = 0.3, 0.2, 0.5
        self.lam = 0.1
        
    def _parse_propositions(self, text):
        """Extract structured propositions with type, polarity, value."""
        props = []
        sentences = re.split(r'[.!?;]', text.lower())
        
        for s in sentences:
            s = s.strip()
            if not s:
                continue
                
            prop = {'text': s, 'polarity': 1, 'type': 'fact', 'value': None, 'confidence': 0.8}
            
            # Negation
            if re.search(r'\b(not|no|never|neither|nor)\b', s):
                prop['polarity'] = -1
                
            # Modal hedges (reduce confidence)
            if re.search(r'\b(might|may|could|possibly|perhaps|probably)\b', s):
                prop['confidence'] = 0.5
                
            # Comparatives
            comp_match = re.search(r'(\w+)\s+(>|<|greater|less|more|fewer)\s+(\w+)', s)
            if comp_match:
                prop['type'] = 'comparison'
                prop['value'] = (comp_match.group(1), comp_match.group(2), comp_match.group(3))
                
            # Conditionals
            if re.search(r'\b(if|when|whenever)\b.*\b(then|thus|therefore)\b', s):
                prop['type'] = 'implication'
                parts = re.split(r'\b(then|thus|therefore)\b', s)
                if len(parts) >= 2:
                    prop['value'] = (parts[0].strip(), parts[-1].strip())
                    
            # Causal
            if re.search(r'\b(because|due to|leads to|causes|results in)\b', s):
                prop['type'] = 'causal'
                
            # Numeric
            nums = re.findall(r'\b\d+\.?\d*\b', s)
            if nums:
                prop['value'] = [float(n) for n in nums]
                
            props.append(prop)
            
        return props
    
    def _predictive_features(self, prop):
        """Convert proposition to feature vector."""
        feat = np.zeros(6)
        feat[0] = prop['polarity']
        feat[1] = 1 if prop['type'] == 'fact' else 0
        feat[2] = 1 if prop['type'] == 'comparison' else 0
        feat[3] = 1 if prop['type'] == 'implication' else 0
        feat[4] = 1 if prop['type'] == 'causal' else 0
        if prop['value'] and isinstance(prop['value'], list):
            feat[5] = np.mean(prop['value']) / 100.0  # Normalize
        return feat
    
    def _prediction_error(self, candidate_props, expected_props):
        """Compute surprise scores via predictive coding."""
        if not expected_props:
            return [0.5] * len(candidate_props)
            
        expected_feats = [self._predictive_features(p) for p in expected_props]
        expected_mean = np.mean(expected_feats, axis=0)
        
        errors = []
        for cp in candidate_props:
            feat = self._predictive_features(cp)
            error = np.linalg.norm(feat - expected_mean)
            errors.append(error)
            
        return errors
    
    def _cognitive_load(self, props):
        """Compute load penalty per Cognitive Load Theory."""
        types = set(p['type'] for p in props)
        negations = sum(1 for p in props if p['polarity'] == -1)
        hedges = sum(1 for p in props if p['confidence'] < 0.7)
        
        # Constraint satisfaction via transitivity
        relations = [(p['value'][0], p['value'][2]) for p in props 
                     if p['type'] == 'comparison' and p['value']]
        satisfied = check_transitivity(relations) if relations else 0
        
        intrinsic = self.alpha * len(types)
        extraneous = self.beta * (negations + hedges)
        germane = self.gamma * satisfied
        
        return intrinsic + extraneous - germane
    
    def _constraint_propagation(self, props):
        """Derive implied facts via modus ponens."""
        facts = [p['text'] for p in props if p['type'] == 'fact']
        premises = [p['value'] for p in props if p['type'] == 'implication' and p['value']]
        
        if not premises:
            return 0.0
            
        derived = modus_ponens(premises, facts)
        entailment_ratio = len(derived) / max(len(props), 1)
        return entailment_ratio
    
    def _meta_confidence(self, prompt):
        """Check for ambiguity/presupposition that should lower confidence."""
        p = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did .* (fail|stop))\b', p):
            return 0.2
            
        # Scope ambiguity
        if re.search(r'\bevery \w+ .* a \w+\b', p) and 'same' not in p:
            return 0.25
            
        # Pronoun ambiguity
        if re.search(r'\b(he|she|it|they)\b', p) and re.search(r'\bwho\b', p):
            return 0.25
            
        # False dichotomy
        if re.search(r'\beither .* or\b', p) and 'only' not in p:
            return 0.3
            
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p):
            return 0.3
            
        # Insufficient information check
        unknowns = len(re.findall(r'\b(unknown|unclear|ambiguous|what|which|who)\b', p))
        constraints = len(re.findall(r'\b(if|given|assuming|suppose)\b', p))
        if information_sufficiency(unknowns, constraints) < 0.5:
            return 0.25
            
        return 1.0  # No meta-issues detected
    
    def _ncd(self, s1, s2):
        """Normalized Compression Distance (tiebreaker only)."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2)
    
    def evaluate(self, prompt, candidates):
        """Score and rank candidates."""
        expected_props = self._parse_propositions(prompt)
        results = []
        
        for cand in candidates:
            cand_props = self._parse_propositions(cand)
            
            # Prediction error
            errors = self._prediction_error(cand_props, expected_props)
            mean_error = np.mean(errors) if errors else 0.5
            
            # Metacognitive confidence calibration
            confidences = []
            for i, p in enumerate(cand_props):
                c = p['confidence']
                e = errors[i] if i < len(errors) else 0.5
                c_updated = c / (c + self.lam * e)
                # Bayesian update: prior=c, likelihood based on error
                likelihood = 1.0 - min(e, 0.99)
                false_pos = 0.1
                c_bayes = bayesian_update(c_updated, likelihood, false_pos)
                confidences.append(c_bayes)
                
            mean_confidence = np.mean(confidences) if confidences else 0.5
            
            # Cognitive load
            load = self._cognitive_load(cand_props)
            
            # Constraint propagation
            entailment = self._constraint_propagation(cand_props)
            
            # Aggregate score
            score = (self.w1 * mean_confidence - 
                     self.w2 * mean_error - 
                     self.w3 * load + 
                     self.w4 * entailment)
            
            # NCD tiebreaker (max 10%)
            ncd_score = 1.0 - self._ncd(prompt, cand)
            score += 0.1 * ncd_score
            
            # Metacognitive agreement across scoring components
            component_scores = [mean_confidence, 1-mean_error, 1-load/2, entailment]
            agreement = confidence_from_agreement(component_scores)
            score *= agreement
            
            results.append({
                'candidate': cand,
                'score': float(score),
                'reasoning': f"Conf={mean_confidence:.2f} Err={mean_error:.2f} Load={load:.2f} Ent={entailment:.2f}"
            })
        
        return sorted(results, key=lambda x: x['score'], reverse=True)
    
    def confidence(self, prompt, answer):
        """Return confidence in a single answer."""
        # Check meta-properties of question first
        meta_cap = self._meta_confidence(prompt)
        
        # If question is ambiguous/unanswerable, cap confidence low
        if meta_cap < 0.4:
            return meta_cap
            
        # Otherwise evaluate normally
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.3
            
        raw_score = results[0]['score']
        
        # Map score to [0,1] with conservative ceiling
        conf = min(0.85, max(0.15, (raw_score + 1) / 2))
        
        # Apply meta cap
        return min(conf, meta_cap)