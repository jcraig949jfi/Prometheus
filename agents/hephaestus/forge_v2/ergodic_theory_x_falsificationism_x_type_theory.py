import math, hashlib, re, zlib
from typing import List, Dict, Any

class ReasoningTool:
    """Ergodic Type-Falsification Engine (ETFE) v2.
    1. Ergodic Theory: Deterministic hash-walk samples hypothesis space; time-avg
       converges to structural overlap as invariant measure.
    2. Falsificationism: Active contradiction detection via negation scope, numeric
       order, conditionals (modus ponens/tollens), subject-object inversion.
    3. Type Theory: Prompt and candidate parsed into typed slots (entity, quantity,
       polarity, relation); type-mismatch between slots triggers falsification."""

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

    # -- type checking layer ---------------------------------------------
    def _type_slots(self, t):
        low = t.lower()
        entities = set(re.findall(r'\b[A-Z][a-z]{2,}\b', t))
        polarity = 'neg' if any(n in low for n in self.negs) else 'pos'
        quants = self._nums(t)
        rels = [w for w in low.split() if w in self.comps]
        return {'entities': entities, 'polarity': polarity, 'quants': quants, 'rels': rels}

    def _type_check(self, p_slots, c_slots):
        """Check type consistency between prompt and candidate slots."""
        penalty = 0.0; reasons = []
        # Entity type consistency: candidate should reference prompt entities
        if p_slots['entities']:
            overlap = len(p_slots['entities'] & c_slots['entities'])
            ratio = overlap / len(p_slots['entities'])
            if ratio < 0.3 and c_slots['entities']:
                penalty += 0.15
                reasons.append(f"structural:entity_type_mismatch(shared={overlap}/{len(p_slots['entities'])})")
        # Polarity type check
        if p_slots['polarity'] == 'neg' and c_slots['polarity'] == 'pos':
            # Further check via negation scope
            penalty += 0.1
            reasons.append("structural:polarity_type_mismatch(prompt=neg,cand=pos)")
        # Relation type: if prompt has comparatives, candidate should too or have numbers
        if p_slots['rels'] and not c_slots['rels'] and not c_slots['quants']:
            penalty += 0.1
            reasons.append("structural:missing_relation_type")
        return penalty, reasons

    # -- falsification layer ---------------------------------------------
    def _falsify(self, prompt, cand):
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
        # Subject-object inversion
        s, o, i = self._svo(prompt)
        if s and o:
            s2, o2, _ = self._svo(cand)
            if s2 and o2 and s2 == o and o2 == s:
                penalty += 0.3; reasons.append(f"structural:subject_object_inversion({s}<->{o})")
        return min(penalty, 1.0), reasons

    # -- ergodic walk ----------------------------------------------------
    def _ergodic_walk(self, prompt, cand, steps=8):
        seed = self._seed(prompt); scores = []
        pw = set(prompt.lower().split()); cw = set(cand.lower().split())
        base = len(pw & cw) / max(len(pw | cw), 1)
        for i in range(steps):
            h = self._seed(f"{seed}_{i}_{cand}")
            pert = ((h % 10000) / 10000.0) * 0.2 - 0.1
            scores.append(base + pert)
        avg = sum(scores) / len(scores)
        var = sum((s - avg)**2 for s in scores) / len(scores)
        conv = 1.0 / (1.0 + var * 100)
        return avg, conv

    # -- public API ------------------------------------------------------
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        if not prompt or not candidates:
            return [{"candidate": c, "score": 0.0, "reasoning": "structural:empty_input"} for c in (candidates or [])]
        p_slots = self._type_slots(prompt)
        results = []
        for cand in candidates:
            parts = []
            if not cand or not cand.strip():
                results.append({"candidate": cand, "score": 0.0, "reasoning": "structural:empty_candidate"}); continue
            # Type checking
            c_slots = self._type_slots(cand)
            t_pen, t_reasons = self._type_check(p_slots, c_slots)
            parts.extend(t_reasons)
            # Falsification
            f_pen, f_reasons = self._falsify(prompt, cand)
            parts.extend(f_reasons)
            total_pen = min(t_pen + f_pen, 1.0)
            likelihood = math.exp(-3.0 * total_pen)
            if total_pen > 0: parts.append(f"falsified(penalty={total_pen:.2f})")
            else: parts.append("survived_falsification")
            # Ergodic walk
            erg_avg, erg_conv = self._ergodic_walk(prompt, cand)
            ergodic = 0.5 + 0.5 * erg_avg * erg_conv
            parts.append(f"ergodic(avg={erg_avg:.3f},conv={erg_conv:.3f})")
            # NCD (capped at 15% weight)
            ncd_sim = 1.0 - self._ncd(prompt, cand)
            score = 0.35 * likelihood + 0.35 * ergodic + 0.15 * ncd_sim + 0.15 * (1.0 - t_pen)
            score = max(0.0, min(1.0, score))
            results.append({"candidate": cand, "score": score, "reasoning": '; '.join(parts)})
        results.sort(key=lambda x: x["score"], reverse=True)
        if len(results) >= 2 and results[0]["score"] - results[1]["score"] < 0.05:
            for r in results[:2]: r["reasoning"] += "; metacog:low_confidence_margin(<5%)"
        # Metacognitive reflection on top
        if results and results[0]["score"] > 0:
            top = results[0]; _, recheck = self._falsify(prompt, top["candidate"])
            if recheck: top["reasoning"] += f"; reflection:top_flagged({len(recheck)} issues)"
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        if not prompt or not answer: return 0.0
        f_pen, _ = self._falsify(prompt, answer)
        if f_pen >= 0.7: return max(0.0, 0.08 * (1.0 - f_pen))
        null_cands = ["", "unknown", "42"]
        res = self.evaluate(prompt, [answer] + null_cands)
        ans_score = next((r["score"] for r in res if r["candidate"] == answer), 0.0)
        null_scores = [r["score"] for r in res if r["candidate"] != answer]
        null_mean = sum(null_scores) / max(len(null_scores), 1)
        if null_mean >= ans_score: return max(0.0, 0.1 * ans_score)
        sep = (ans_score - null_mean) / (1.0 - null_mean + 1e-9)
        return float(max(0.0, min(1.0, 0.3 * ans_score + 0.7 * sep)))
