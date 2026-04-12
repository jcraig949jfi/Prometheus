import math, hashlib, re, zlib
from typing import List, Dict, Any

class ReasoningTool:
    """Categorical Ergodic Meta-Functor (CEMF) v2.
    1. Category Theory: Prompt/candidate as objects; structural transforms as
       morphisms (feature extraction). Functorial consistency = morphisms compose.
    2. Ergodic Theory: Hash-walk probes overlap space; time-avg convergence as
       invariant measure of similarity.
    3. Metacognition: Self-evaluation of scoring confidence -- variance across
       sub-scores drives explore/exploit temperature; reflection pass rechecks
       top candidate for violations."""

    def __init__(self):
        self.negs = ['not','no','never','neither','nor','cannot',"won't","isn't","aren't","doesn't","don't"]
        self.comps = {'greater':1,'more':1,'larger':1,'higher':1,
                      'less':-1,'fewer':-1,'smaller':-1,'lower':-1}
        self._meta_uncertainty = 0.5

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

    # -- categorical morphism layer --------------------------------------
    def _extract_object(self, text):
        """Map text to object in category H: feature tuple."""
        low = text.lower(); ws = set(low.split())
        ents = set(re.findall(r'\b[A-Z][a-z]{2,}\b', text))
        has_neg = any(n in low for n in self.negs)
        nums = self._nums(text)
        has_comp = any(w in ws for w in self.comps)
        return {'entities': ents, 'neg': has_neg, 'nums': nums, 'comp': has_comp,
                'words': ws, 'length': len(text)}

    def _morphism_score(self, p_obj, c_obj):
        """Functorial consistency: do morphisms compose (features map coherently)?"""
        reasons = []; score = 0.0
        # Entity functor: F(entities)
        if p_obj['entities']:
            overlap = len(p_obj['entities'] & c_obj['entities']) / len(p_obj['entities'])
            score += 0.2 * overlap
            if overlap < 0.2 and c_obj['entities']:
                reasons.append(f"structural:functor_entity_break(overlap={overlap:.2f})")
        # Content morphism: word overlap (Jaccard)
        union = p_obj['words'] | c_obj['words']
        inter = p_obj['words'] & c_obj['words']
        jaccard = len(inter) / max(len(union), 1)
        score += 0.3 * jaccard
        # Structural morphism: neg/comp consistency
        if p_obj['neg'] and not c_obj['neg'] and not c_obj['nums']:
            score -= 0.1; reasons.append("structural:morphism_polarity_break")
        if p_obj['comp'] and not c_obj['comp'] and not c_obj['nums']:
            score -= 0.05; reasons.append("structural:morphism_relation_break")
        return max(0.0, min(1.0, score)), reasons

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

    # -- metacognitive layer ---------------------------------------------
    def _meta_control(self, sub_scores):
        """Self-evaluate scoring confidence from sub-score variance."""
        if len(sub_scores) < 2: return 1.0, "meta:single_signal"
        mean_s = sum(sub_scores) / len(sub_scores)
        var = sum((s - mean_s)**2 for s in sub_scores) / len(sub_scores)
        self._meta_uncertainty = 0.7 * self._meta_uncertainty + 0.3 * var
        conf = 1.0 / (1.0 + var * 20)
        if var < 0.01: tag = f"meta:high_agreement(var={var:.4f},conf={conf:.2f})"
        elif var > 0.05: tag = f"meta:high_disagreement(var={var:.4f},conf={conf:.2f})"
        else: tag = f"meta:moderate(var={var:.4f},conf={conf:.2f})"
        return conf, tag

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
        p_obj = self._extract_object(prompt)
        results = []
        for cand in candidates:
            parts = []
            if not cand or not cand.strip():
                results.append({"candidate": cand, "score": 0.0, "reasoning": "structural:empty_candidate"}); continue
            c_obj = self._extract_object(cand)
            # Categorical morphism
            morph, m_reasons = self._morphism_score(p_obj, c_obj); parts.extend(m_reasons)
            parts.append(f"execution:morphism={morph:.3f}")
            # Falsification
            f_pen, f_reasons = self._falsify(prompt, cand); parts.extend(f_reasons)
            likelihood = math.exp(-3.0 * f_pen)
            if f_pen > 0: parts.append(f"falsified(penalty={f_pen:.2f})")
            else: parts.append("survived_falsification")
            # Ergodic walk
            erg_avg, erg_conv = self._ergodic_walk(prompt, cand)
            ergodic = 0.5 + 0.5 * erg_avg * erg_conv
            parts.append(f"ergodic(avg={erg_avg:.3f},conv={erg_conv:.3f})")
            # NCD capped at 15%
            ncd_sim = 1.0 - self._ncd(prompt, cand)
            # Metacognitive self-eval of sub-scores
            sub_scores = [morph, likelihood, ergodic, ncd_sim]
            meta_conf, meta_tag = self._meta_control(sub_scores); parts.append(meta_tag)
            score = 0.30 * morph + 0.25 * likelihood + 0.20 * ergodic + 0.15 * ncd_sim + 0.10 * meta_conf
            score = max(0.0, min(1.0, score))
            results.append({"candidate": cand, "score": score, "reasoning": '; '.join(parts)})
        results.sort(key=lambda x: x["score"], reverse=True)
        if len(results) >= 2 and results[0]["score"] - results[1]["score"] < 0.05:
            for r in results[:2]: r["reasoning"] += "; metacog:low_confidence_margin(<5%)"
        # Reflection pass
        if results and results[0]["score"] > 0:
            top = results[0]; _, recheck = self._falsify(prompt, top["candidate"])
            violations = [r for r in recheck if 'violation' in r or 'contradiction' in r or 'fail' in r]
            if violations:
                top["reasoning"] += f"; reflection:top_has_issues({len(violations)} flags)"
                top["score"] = max(0.0, top["score"] - 0.05)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        if not prompt or not answer: return 0.0
        f_pen, reasons = self._falsify(prompt, answer)
        if len([r for r in reasons if 'violation' in r or 'contradiction' in r]) >= 2:
            return max(0.0, 0.05 * (1.0 - f_pen))
        null_cands = ["", "unknown", "42"]
        res = self.evaluate(prompt, [answer] + null_cands)
        ans_score = next((r["score"] for r in res if r["candidate"] == answer), 0.0)
        null_scores = [r["score"] for r in res if r["candidate"] != answer]
        null_mean = sum(null_scores) / max(len(null_scores), 1)
        if null_mean >= ans_score: return max(0.0, 0.1 * ans_score)
        sep = (ans_score - null_mean) / (1.0 - null_mean + 1e-9)
        # Metacognitive confidence adjustment
        morph, _ = self._morphism_score(self._extract_object(prompt), self._extract_object(answer))
        return float(max(0.0, min(1.0, 0.3 * ans_score + 0.4 * sep + 0.3 * morph)))
