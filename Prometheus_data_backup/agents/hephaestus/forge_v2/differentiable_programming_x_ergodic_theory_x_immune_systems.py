import math, hashlib, re, zlib
from typing import List, Dict, Any

class ReasoningTool:
    """Immune-Ergodic Differentiable Selector (IEDS) v2.
    1. Immune Systems: Self/non-self discrimination -- prompt defines 'self';
       candidates matching prompt context = self, contradictions = non-self.
       Clonal selection ranks by affinity; memory stores nothing (stateless).
    2. Ergodic Theory: Hash-walk samples overlap space; time-avg as invariant
       measure for structural similarity.
    3. Differentiable Programming: Finite-difference sensitivity analysis on
       candidate perturbations; high gradient = fragile answer."""

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

    # -- self/non-self discrimination ------------------------------------
    def _build_self_profile(self, prompt):
        """Extract the prompt's 'self' signature: entities, polarity, numbers, topics."""
        pl = prompt.lower()
        entities = set(re.findall(r'\b[A-Z][a-z]{2,}\b', prompt))
        topics = set(w for w in pl.split() if len(w) > 4)
        polarity = 'neg' if any(n in pl for n in self.negs) else 'pos'
        nums = self._nums(prompt)
        return {'entities': entities, 'topics': topics, 'polarity': polarity, 'nums': nums}

    def _self_nonself(self, self_profile, cand):
        """Score how well candidate matches the prompt's self-context."""
        cl = cand.lower(); reasons = []; affinity = 0.0
        c_ents = set(re.findall(r'\b[A-Z][a-z]{2,}\b', cand))
        c_topics = set(w for w in cl.split() if len(w) > 4)
        # Entity overlap
        if self_profile['entities']:
            ent_overlap = len(self_profile['entities'] & c_ents) / len(self_profile['entities'])
            affinity += 0.2 * ent_overlap
            if ent_overlap < 0.3 and c_ents:
                reasons.append(f"structural:nonself_entities(overlap={ent_overlap:.2f})")
        # Topic overlap
        if self_profile['topics']:
            top_overlap = len(self_profile['topics'] & c_topics) / len(self_profile['topics'])
            affinity += 0.15 * top_overlap
        # Polarity consistency
        c_pol = 'neg' if any(n in cl for n in self.negs) else 'pos'
        if self_profile['polarity'] == c_pol:
            affinity += 0.1
        elif self_profile['polarity'] == 'neg' and c_pol == 'pos':
            reasons.append("structural:nonself_polarity(prompt=neg,cand=pos)")
        # Numeric context consistency
        c_nums = self._nums(cand)
        if self_profile['nums'] and c_nums:
            if any(abs(p - c) < 1e-6 for p in self_profile['nums'] for c in c_nums):
                affinity += 0.15
            else:
                affinity += 0.05
        elif not self_profile['nums'] and not c_nums:
            affinity += 0.1
        return affinity, reasons

    # -- falsification ---------------------------------------------------
    def _falsify(self, prompt, cand):
        penalty = 0.0; reasons = []; pl, cl = prompt.lower(), cand.lower()
        for scope in self._neg_scopes(prompt):
            if scope and scope in cl and not any(scope in cn for cn in self._neg_scopes(cand)):
                penalty += 0.35; reasons.append(f"structural:negation_scope_violation('{scope}')")
        for neg, pos in [('impossible','possible'),('false','true'),('never','always')]:
            if neg in pl and pos in cl and neg not in cl:
                penalty += 0.3; reasons.append(f"structural:contradiction({neg}/{pos})")
        pn, cn = self._nums(prompt), self._nums(cand)
        if pn and cn:
            direction = sum(self.comps.get(w, 0) for w in pl.split())
            if direction > 0 and cn[0] < pn[0]:
                penalty += 0.3; reasons.append(f"execution:numeric_violation(expected>{pn[0]},got={cn[0]})")
            elif direction < 0 and cn[0] > pn[0]:
                penalty += 0.3; reasons.append(f"execution:numeric_violation(expected<{pn[0]},got={cn[0]})")
            if len(pn) >= 2 and len(cn) >= 2 and (pn[0] < pn[1]) != (cn[0] < cn[1]):
                penalty += 0.2; reasons.append("execution:numeric_order_mismatch")
        ante, cons = self._conditional(prompt)
        if ante and cons and ante in cl and cons not in cl:
            penalty += 0.3; reasons.append(f"structural:modus_ponens_fail('{ante}'->'{cons}')")
        s, o, _ = self._svo(prompt)
        if s and o:
            s2, o2, _ = self._svo(cand)
            if s2 and o2 and s2 == o and o2 == s:
                penalty += 0.3; reasons.append(f"structural:subject_object_inversion({s}<->{o})")
        return min(penalty, 1.0), reasons

    # -- sensitivity analysis (differentiable programming) ---------------
    def _sensitivity(self, prompt, cand, base_score):
        words = cand.split()
        if len(words) < 2: return 0.0
        perturbed = ' '.join(words[:-1])
        p_aff, _ = self._self_nonself(self._build_self_profile(prompt), perturbed)
        return abs(base_score - p_aff)

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
        self_profile = self._build_self_profile(prompt)
        results = []
        for cand in candidates:
            parts = []
            if not cand or not cand.strip():
                results.append({"candidate": cand, "score": 0.0, "reasoning": "structural:empty_candidate"}); continue
            # Immune self/non-self
            affinity, imm_reasons = self._self_nonself(self_profile, cand); parts.extend(imm_reasons)
            parts.append(f"execution:immune_affinity={affinity:.3f}")
            # Falsification
            f_pen, f_reasons = self._falsify(prompt, cand); parts.extend(f_reasons)
            likelihood = math.exp(-3.0 * f_pen)
            if f_pen > 0: parts.append(f"falsified(penalty={f_pen:.2f})")
            else: parts.append("survived_falsification")
            # Sensitivity
            grad = self._sensitivity(prompt, cand, affinity)
            stability = 1.0 / (1.0 + grad * 5)
            if grad > 0.15: parts.append(f"execution:high_sensitivity(grad={grad:.3f})")
            # Ergodic walk
            erg_avg, erg_conv = self._ergodic_walk(prompt, cand)
            ergodic = 0.5 + 0.5 * erg_avg * erg_conv
            parts.append(f"ergodic(avg={erg_avg:.3f},conv={erg_conv:.3f})")
            # NCD capped at 15%
            ncd_sim = 1.0 - self._ncd(prompt, cand)
            score = 0.25 * affinity + 0.25 * likelihood + 0.15 * stability + 0.20 * ergodic + 0.15 * ncd_sim
            score = max(0.0, min(1.0, score))
            results.append({"candidate": cand, "score": score, "reasoning": '; '.join(parts)})
        results.sort(key=lambda x: x["score"], reverse=True)
        if len(results) >= 2 and results[0]["score"] - results[1]["score"] < 0.05:
            for r in results[:2]: r["reasoning"] += "; metacog:low_confidence_margin(<5%)"
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
        grad = self._sensitivity(prompt, answer, ans_score)
        stab = 1.0 / (1.0 + grad * 5)
        return float(max(0.0, min(1.0, 0.3 * ans_score + 0.4 * sep + 0.3 * stab)))
