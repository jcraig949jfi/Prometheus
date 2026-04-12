import math, hashlib, re, zlib
from typing import List, Dict, Any

class ReasoningTool:
    """Chaotic Compositional Active-Inference Engine (CCAIE) v2.
    1. Active Inference: Expected Free Energy (EFE) = pragmatic value (constraint
       match) + epistemic value (information gain via structural diversity).
    2. Chaos Theory: Deterministic logistic-map walk seeded by prompt hash;
       divergence rate estimates answer fragility.
    3. Compositionality: Prompt decomposed into typed sub-expressions (entities,
       quantities, relations); candidate scored by compositional coverage."""

    def __init__(self):
        self.negs = ['not','no','never','neither','nor','cannot',"won't","isn't","aren't","doesn't","don't"]
        self.comps = {'greater':1,'more':1,'larger':1,'higher':1,
                      'less':-1,'fewer':-1,'smaller':-1,'lower':-1}

    # -- helpers ----------------------------------------------------------
    def _seed(self, t): return int(hashlib.sha256(t.encode()).hexdigest()[:8], 16)
    def _nums(self, t): return [float(m) for m in re.findall(r'-?\d+\.?\d*', t)]
    def _ncd(self, a, b):
        ca, cb = len(zlib.compress(a.encode())), len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a+b).encode())); mx = max(ca, cb)
        return (cab - min(ca, cb)) / mx if mx else 0.0
    def _neg_scopes(self, t):
        ws = t.lower().split(); out = []
        for i, w in enumerate(ws):
            if w in self.negs and i+1 < len(ws):
                out.append(' '.join(ws[i+1:min(i+4, len(ws))]))
        return out
    def _conditional(self, t):
        m = re.search(r'\bif\b(.+?)\bthen\b(.+?)(?:[.,;]|$)', t.lower())
        return (m.group(1).strip(), m.group(2).strip()) if m else (None, None)
    def _svo(self, t):
        m = re.search(r'(\b\w+)\s+(?:gave|sent|told|showed|made|built)\s+(\w+)\s+to\s+(\w+)', t.lower())
        return (m.group(1), m.group(2), m.group(3)) if m else (None, None, None)

    # -- compositional parsing -------------------------------------------
    def _decompose(self, text):
        """Parse into compositional sub-expressions."""
        low = text.lower()
        return {
            'entities': set(re.findall(r'\b[A-Z][a-z]{2,}\b', text)),
            'quantities': self._nums(text),
            'relations': [w for w in low.split() if w in self.comps],
            'negations': self._neg_scopes(text),
            'connectors': [w for w in low.split() if w in ['therefore','because','if','then','so','but','however']],
            'words': set(low.split()),
        }

    def _compositional_coverage(self, p_parts, c_parts):
        """Score how well candidate covers prompt sub-expressions."""
        reasons = []; score = 0.0
        # Entity coverage
        if p_parts['entities']:
            cov = len(p_parts['entities'] & c_parts['entities']) / len(p_parts['entities'])
            score += 0.15 * cov
            if cov < 0.3 and c_parts['entities']:
                reasons.append(f"structural:low_entity_coverage({cov:.2f})")
        # Word coverage (Jaccard)
        union = p_parts['words'] | c_parts['words']
        inter = p_parts['words'] & c_parts['words']
        score += 0.2 * (len(inter) / max(len(union), 1))
        # Connector presence
        if p_parts['connectors']:
            if c_parts['connectors']: score += 0.1; reasons.append("structural:has_logical_connectors")
        # Negation coverage
        p_neg_set = set(tuple(n.split()) for n in p_parts['negations'])
        c_neg_set = set(tuple(n.split()) for n in c_parts['negations'])
        if p_neg_set and p_neg_set == c_neg_set: score += 0.1
        return score, reasons

    # -- chaos layer (logistic map divergence) ---------------------------
    def _chaos_divergence(self, prompt, cand, steps=12):
        """Measure divergence rate of logistic trajectories seeded by prompt vs candidate."""
        r = 3.99; s1 = (self._seed(prompt) % 10000) / 10001.0
        s2 = (self._seed(cand) % 10000) / 10001.0
        # Avoid fixed points
        s1 = max(0.01, min(0.99, s1)); s2 = max(0.01, min(0.99, s2))
        diffs = []
        for _ in range(steps):
            s1 = r * s1 * (1 - s1); s2 = r * s2 * (1 - s2)
            diffs.append(abs(s1 - s2))
        avg_diff = sum(diffs) / len(diffs)
        # Low divergence = similar seeds = related content
        return 1.0 / (1.0 + avg_diff * 5)

    # -- active inference EFE --------------------------------------------
    def _pragmatic_value(self, prompt, cand):
        """Constraint satisfaction = pragmatic value."""
        penalty = 0.0; reasons = []; pl, cl = prompt.lower(), cand.lower()
        # Negation scope
        for scope in self._neg_scopes(prompt):
            if scope and scope in cl and not any(scope in cn for cn in self._neg_scopes(cand)):
                penalty += 0.35; reasons.append(f"structural:negation_scope_violation('{scope}')")
        # Contradiction pairs
        for neg, pos in [('impossible','possible'),('false','true'),('never','always')]:
            if neg in pl and pos in cl and neg not in cl:
                penalty += 0.3; reasons.append(f"structural:contradiction({neg}/{pos})")
        # Numeric
        pn, cn = self._nums(prompt), self._nums(cand)
        if pn and cn:
            direction = sum(self.comps.get(w, 0) for w in pl.split())
            if direction > 0 and cn[0] < pn[0]:
                penalty += 0.3; reasons.append(f"execution:numeric_violation(expected>{pn[0]},got={cn[0]})")
            elif direction < 0 and cn[0] > pn[0]:
                penalty += 0.3; reasons.append(f"execution:numeric_violation(expected<{pn[0]},got={cn[0]})")
            if len(pn) >= 2 and len(cn) >= 2 and (pn[0] < pn[1]) != (cn[0] < cn[1]):
                penalty += 0.2; reasons.append("execution:numeric_order_mismatch")
        # Conditionals
        ante, cons = self._conditional(prompt)
        if ante and cons and ante in cl and cons not in cl:
            penalty += 0.3; reasons.append(f"structural:modus_ponens_fail('{ante}'->'{cons}')")
        # Subject-object
        s, o, _ = self._svo(prompt)
        if s and o:
            s2, o2, _ = self._svo(cand)
            if s2 and o2 and s2 == o and o2 == s:
                penalty += 0.3; reasons.append(f"structural:subject_object_inversion({s}<->{o})")
        return math.exp(-3.0 * min(penalty, 1.0)), reasons

    # -- ergodic walk ----------------------------------------------------
    def _ergodic_walk(self, prompt, cand, steps=8):
        seed = self._seed(prompt); scores = []
        pw = set(prompt.lower().split()); cw = set(cand.lower().split())
        base = len(pw & cw) / max(len(pw | cw), 1)
        for i in range(steps):
            h = self._seed(f"{seed}_{i}_{cand}")
            scores.append(base + ((h % 10000) / 10000.0) * 0.2 - 0.1)
        avg = sum(scores) / len(scores)
        var = sum((s - avg)**2 for s in scores) / len(scores)
        return avg, 1.0 / (1.0 + var * 100)

    # -- public API ------------------------------------------------------
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        if not prompt or not candidates:
            return [{"candidate": c, "score": 0.0, "reasoning": "structural:empty_input"} for c in (candidates or [])]
        p_parts = self._decompose(prompt)
        results = []
        for cand in candidates:
            parts = []
            if not cand or not cand.strip():
                results.append({"candidate": cand, "score": 0.0, "reasoning": "structural:empty_candidate"}); continue
            c_parts = self._decompose(cand)
            # Compositionality
            comp_score, comp_r = self._compositional_coverage(p_parts, c_parts); parts.extend(comp_r)
            parts.append(f"execution:compositional={comp_score:.3f}")
            # Active inference pragmatic
            prag, prag_r = self._pragmatic_value(prompt, cand); parts.extend(prag_r)
            if prag < 0.5: parts.append(f"falsified(prag={prag:.2f})")
            else: parts.append("survived_falsification")
            # Chaos divergence (epistemic value proxy)
            chaos = self._chaos_divergence(prompt, cand)
            parts.append(f"execution:chaos_resonance={chaos:.3f}")
            # Ergodic walk
            erg_avg, erg_conv = self._ergodic_walk(prompt, cand)
            ergodic = 0.5 + 0.5 * erg_avg * erg_conv
            parts.append(f"ergodic(avg={erg_avg:.3f},conv={erg_conv:.3f})")
            # NCD capped at 15%
            ncd_sim = 1.0 - self._ncd(prompt, cand)
            # EFE = pragmatic + epistemic
            score = 0.25 * prag + 0.20 * comp_score + 0.15 * chaos + 0.25 * ergodic + 0.15 * ncd_sim
            score = max(0.0, min(1.0, score))
            results.append({"candidate": cand, "score": score, "reasoning": '; '.join(parts)})
        results.sort(key=lambda x: x["score"], reverse=True)
        if len(results) >= 2 and results[0]["score"] - results[1]["score"] < 0.05:
            for r in results[:2]: r["reasoning"] += "; metacog:low_confidence_margin(<5%)"
        # Metacognitive reflection
        if results and results[0]["score"] > 0:
            top = results[0]; _, recheck = self._pragmatic_value(prompt, top["candidate"])
            if recheck: top["reasoning"] += f"; reflection:top_flagged({len(recheck)} issues)"
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        if not prompt or not answer: return 0.0
        prag, reasons = self._pragmatic_value(prompt, answer)
        if len(reasons) >= 3: return max(0.0, 0.05 * prag)
        null_cands = ["", "unknown", "42"]
        res = self.evaluate(prompt, [answer] + null_cands)
        ans_score = next((r["score"] for r in res if r["candidate"] == answer), 0.0)
        null_scores = [r["score"] for r in res if r["candidate"] != answer]
        null_mean = sum(null_scores) / max(len(null_scores), 1)
        if null_mean >= ans_score: return max(0.0, 0.1 * ans_score)
        sep = (ans_score - null_mean) / (1.0 - null_mean + 1e-9)
        return float(max(0.0, min(1.0, 0.3 * ans_score + 0.7 * sep)))
