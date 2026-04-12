import math, hashlib, re, zlib
from typing import List, Dict, Any

class ReasoningTool:
    """Dynamical Belief-Trajectory Estimator (DBTE) v2.
    1. Dynamical Systems: Candidate scored via discrete trajectory simulation --
       state vector evolves under constraint map; divergence = poor answer.
    2. Ergodic Theory: Hash-seeded walk samples overlap space; time-avg converges
       to structural similarity as invariant measure.
    3. Theory of Mind: Infers prompt intent (question type, expected polarity)
       and checks if candidate aligns with inferred communicative goal."""

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

    # -- trajectory simulation -------------------------------------------
    def _trajectory_sim(self, prompt, cand, steps=6):
        """Simulate discrete dynamical system: state = [overlap, neg_match, num_match].
        Evolve under constraint map; measure final distance from target attractor."""
        pw = set(prompt.lower().split()); cw = set(cand.lower().split())
        overlap = len(pw & cw) / max(len(pw | cw), 1)
        pn_scopes = set(self._neg_scopes(prompt)); cn_scopes = set(self._neg_scopes(cand))
        neg_match = 1.0 if pn_scopes == cn_scopes else (0.5 if pn_scopes & cn_scopes else 0.0) if pn_scopes else 0.5
        p_nums, c_nums = self._nums(prompt), self._nums(cand)
        if p_nums and c_nums:
            num_match = 1.0 / (1.0 + abs(p_nums[0] - c_nums[0]))
        elif not p_nums and not c_nums:
            num_match = 0.5
        else:
            num_match = 0.1
        state = [overlap, neg_match, num_match]
        # Evolve: logistic-like map constrained by prompt features
        reasons = []
        for step in range(steps):
            state[0] = 0.9 * state[0] + 0.1 * (state[1] * state[2])  # overlap attracted by consistency
            state[1] = min(1.0, state[1] + 0.05 * (state[0] - 0.5))  # neg match adjusts
            state[2] = min(1.0, state[2] + 0.05 * (state[0] - 0.5))  # num match adjusts
        final = sum(state) / len(state)
        divergence = abs(state[0] - state[1]) + abs(state[1] - state[2])
        if divergence > 0.5:
            reasons.append(f"execution:trajectory_divergent(d={divergence:.2f})")
        return max(0.0, min(1.0, final * (1.0 - 0.3 * divergence))), reasons

    # -- theory of mind --------------------------------------------------
    def _infer_intent(self, prompt):
        pl = prompt.lower()
        if re.search(r'^(is|are|was|were|do|does|did|can|could|should)\b', pl):
            return 'yes_no'
        if re.search(r'^(what|which|who|where|when|how|why)\b', pl):
            return 'wh_question'
        if any(w in pl for w in ['compare','rank','sort','order']):
            return 'ordering'
        return 'statement'

    def _tom_score(self, prompt, cand):
        """Score candidate by alignment with inferred communicative intent."""
        intent = self._infer_intent(prompt); cl = cand.lower(); reasons = []
        score = 0.0
        if intent == 'yes_no':
            if re.search(r'\b(yes|no|true|false|correct|incorrect)\b', cl):
                score += 0.3; reasons.append("structural:tom_yes_no_aligned")
            else:
                score += 0.1
        elif intent == 'wh_question':
            if len(cand.split()) >= 3:
                score += 0.25; reasons.append("structural:tom_wh_substantive")
            else:
                score += 0.05
        elif intent == 'ordering':
            cn = self._nums(cand)
            if len(cn) >= 2:
                score += 0.3; reasons.append("structural:tom_ordering_has_sequence")
            else:
                score += 0.05
        else:
            score += 0.15
        return score, reasons

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
        ante, cons = self._conditional(prompt)
        if ante and cons and ante in cl and cons not in cl:
            penalty += 0.3; reasons.append(f"structural:modus_ponens_fail('{ante}'->'{cons}')")
        s, o, _ = self._svo(prompt)
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
            scores.append(base + ((h % 10000) / 10000.0) * 0.2 - 0.1)
        avg = sum(scores) / len(scores)
        var = sum((s - avg)**2 for s in scores) / len(scores)
        return avg, 1.0 / (1.0 + var * 100)

    # -- public API ------------------------------------------------------
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        if not prompt or not candidates:
            return [{"candidate": c, "score": 0.0, "reasoning": "structural:empty_input"} for c in (candidates or [])]
        results = []
        for cand in candidates:
            parts = []
            if not cand or not cand.strip():
                results.append({"candidate": cand, "score": 0.0, "reasoning": "structural:empty_candidate"}); continue
            traj, traj_r = self._trajectory_sim(prompt, cand); parts.extend(traj_r)
            parts.append(f"execution:trajectory={traj:.3f}")
            tom, tom_r = self._tom_score(prompt, cand); parts.extend(tom_r)
            f_pen, f_reasons = self._falsify(prompt, cand); parts.extend(f_reasons)
            likelihood = math.exp(-3.0 * f_pen)
            if f_pen > 0: parts.append(f"falsified(penalty={f_pen:.2f})")
            else: parts.append("survived_falsification")
            erg_avg, erg_conv = self._ergodic_walk(prompt, cand)
            ergodic = 0.5 + 0.5 * erg_avg * erg_conv
            parts.append(f"ergodic(avg={erg_avg:.3f},conv={erg_conv:.3f})")
            ncd_sim = 1.0 - self._ncd(prompt, cand)
            score = 0.25 * traj + 0.20 * likelihood + 0.20 * tom + 0.20 * ergodic + 0.15 * ncd_sim
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
        return float(max(0.0, min(1.0, 0.3 * ans_score + 0.7 * sep)))
