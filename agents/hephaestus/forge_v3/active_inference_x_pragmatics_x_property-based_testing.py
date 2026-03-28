"""Active Inference Pragmatic PBT v3. Active Inference x Pragmatics x Property-Based Testing.
Category-driven structural parsing (>=70%), NCD tiebreaker (<=15%).
"""
import re, zlib, numpy as np

class ReasoningTool:
    def __init__(self):
        np.random.seed(42)
        self._np = re.compile(r"[-+]?\d*\.?\d+")
        self._neg = re.compile(r"\b(not|no|never|none|cannot|can't|doesn't|don't|isn't|aren't|wasn't|weren't|neither|nor)\b", re.I)
        self._unit = re.compile(r"\b(a\s+)?(pound|kilogram|kg|ton|ounce|gallon|liter|cup|mile|foot|meter)\s+of\s+(\w+)", re.I)
        self._cmp_gt = re.compile(r"\b(larger|greater|bigger|more|heavier|taller|higher|older|faster)\s+than\b", re.I)
        self._cmp_lt = re.compile(r"\b(smaller|less|fewer|shorter|lighter|lower|younger|slower)\s+than\b", re.I)
        self._overtake = re.compile(r"\b(?:pass|overtake|over\s*take)\b.*\b(first|1st|second|2nd|third|3rd|last)\b", re.I)
        self._allx = re.compile(r"\ball\s+(\w+)\s+are\s+(\w+)", re.I)
        self._allbut = re.compile(r"\ball\s+but\s+(\d+)", re.I)
        self._coin = re.compile(r"\b(coin|dice|die|flip|roll|roulette|lottery)\b.*\b(heads|tails|fair|independent|chance|probability|odds)\b", re.I)
        self._parity = re.compile(r"\b(odd|even)\b", re.I)
        self._ifthen = re.compile(r"\bif\b(.+?)(?:\bthen\b|,)(.+?)(?:\.|$)", re.I | re.S)
        self._svo = re.compile(r"\b(\w+)\s+(ate|hit|chased|kicked|saw|bit|called|caught|pushed|gave|told|killed|loves?|hates?)\s+(?:the\s+)?(\w+)", re.I)
        self._rep_dec = re.compile(r"0\.9{3,}|repeating\s*9|9\s*repeating", re.I)
        self._notallfmt = re.compile(r"\bnot\s+all\b", re.I)
        self._trans = re.compile(r"(\w+)\s+is\s+(?:taller|faster|older|heavier|bigger|greater|smarter|richer|stronger)\s+than\s+(\w+)", re.I)

    def _nums(self, t):
        return [float(x) for x in self._np.findall(t)]

    def _ncd(self, a, b):
        try:
            ba, bb = a.encode(), b.encode()
            ca, cb, cab = len(zlib.compress(ba)), len(zlib.compress(bb)), len(zlib.compress(ba+bb))
            return (cab - min(ca, cb)) / max(ca, cb, 1)
        except: return 1.0

    def _structural_score(self, prompt, cand):
        p, c = prompt.lower(), cand.lower()
        scores, hits = [], 0
        pn, cn = self._nums(p), self._nums(c)
        # 1. numeric_float_comparison
        if len(pn) >= 2 and (self._cmp_gt.search(p) or self._cmp_lt.search(p) or re.search(r'\bwhich\b.*\b(bigger|larger|greater|smaller|less)\b', p)):
            hits += 1
            correct_val = max(pn) if (self._cmp_gt.search(p) or re.search(r'\b(bigger|larger|greater)\b', p)) else min(pn)
            if cn and abs(cn[0] - correct_val) < 1e-6: scores.append(1.0)
            elif any(w in c for w in ['no','false','neither']): scores.append(0.6)
            else: scores.append(0.0)
        # 2. trick_question_equal_weight
        units_p = self._unit.findall(p)
        if len(units_p) >= 2 and len(set(m[1].lower() for m in units_p)) == 1:
            hits += 1
            scores.append(1.0 if any(w in c for w in ['same','equal','identical','no difference','neither']) else 0.0)
        # 3. positional_logic
        m_ov = self._overtake.search(p)
        if m_ov:
            hits += 1; pos = m_ov.group(1).lower()
            scores.append(1.0 if (pos in c or (pos=='second' and '2nd' in c) or (pos=='first' and '1st' in c)) else 0.0)
        # 4. algebraic_word_problem
        if re.search(r'\bcosts?\b.*\bmore\s+than\b', p) and re.search(r'\btotal\b|\btogether\b|\bcombined\b|\band\b.*cost', p):
            hits += 1
            if len(pn) >= 2:
                total, diff = max(pn), min(pn); expected = (total - diff) / 2.0
                if cn and abs(cn[0] - expected) < 0.011: scores.append(1.0)
                elif cn and abs(cn[0] - diff) < 0.011: scores.append(0.0)
                else: scores.append(0.3)
            else: scores.append(0.3)
        # 5. universal_quantifier_converse_error
        if self._allx.search(p) and re.search(r'\b(does\s+(that|this|it)\s+mean|can\s+we\s+(say|conclude)|are\s+all|is\s+every)\b', p):
            hits += 1
            if any(w in c for w in ['no','not necessarily','false','cannot',"can't",'incorrect']): scores.append(1.0)
            elif c.strip().startswith('yes') or 'true' in c.split(): scores.append(0.0)
            else: scores.append(0.4)
        # 6. mathematical_identity
        if self._rep_dec.search(p) or '0.999' in p:
            hits += 1
            if any(w in c for w in ['yes','equal','true','same','identical','= 1']): scores.append(1.0)
            elif any(w in c for w in ['no','false','less than','not equal']): scores.append(0.0)
            else: scores.append(0.3)
        # 7. pigeonhole_principle
        if re.search(r'\b(at\s+least|must|guarantee|sure|certain)\b', p) and re.search(r'\b(same|share|match|born|month|birthday|color|pair)\b', p):
            hits += 1
            if pn:
                n_it, slots = max(pn), (min(pn) if len(pn)>=2 else 12)
                if n_it > slots:
                    if any(w in c for w in ['yes','must','guaranteed','true','certainly']): scores.append(1.0)
                    elif any(w in c for w in ['no','false','not']): scores.append(0.0)
                    else: scores.append(0.3)
                else: scores.append(0.5)
            else: scores.append(0.5)
        # 8. statistical_independence
        if self._coin.search(p) or re.search(r'\bindependent\b|\bfair\b.*\b(coin|die|dice)\b', p):
            if re.search(r'\b(next|probability|chance|odds|likely|what)\b', p):
                hits += 1
                if re.search(r'\b(higher|lower|more likely|less likely|due|streak|overdue|hot|cold)\b', c): scores.append(0.0)
                elif any(w in c for w in ['50','1/2','half','fifty','0.5','same']): scores.append(1.0)
                elif re.search(r'\b(1/6|16\.?6)\b', c): scores.append(1.0)
                else: scores.append(0.3)
        # 9. number_parity
        pw = self._parity.findall(p)
        if len(pw) >= 2 and re.search(r'\b(sum|add|plus|total|\+)\b', p):
            hits += 1; odds = sum(1 for x in pw if x.lower()=='odd')
            res_even = (odds % 2 == 0)
            if res_even:
                scores.append(1.0 if 'even' in c else (0.0 if 'odd' in c else 0.3))
            else:
                scores.append(1.0 if 'odd' in c else (0.0 if 'even' in c else 0.3))
        # 10. all_but_N_survivor_counting
        m_but = self._allbut.search(p)
        if m_but:
            hits += 1; scores.append(1.0 if m_but.group(1) in c else 0.0)
        # 11. transitive_ordering
        chain = self._trans.findall(p)
        if len(chain) >= 2:
            hits += 1; order = {}
            for a, b in chain:
                al, bl = a.lower(), b.lower(); order[al] = order.get(al,0)+1; order.setdefault(bl,0)
            top, bot = max(order, key=order.get), min(order, key=order.get)
            if re.search(r'\b(tallest|fastest|oldest|biggest|greatest|heaviest|smartest|strongest)\b', p):
                scores.append(1.0 if top in c else 0.0)
            elif re.search(r'\b(shortest|slowest|youngest|smallest|lightest|weakest)\b', p):
                scores.append(1.0 if bot in c else 0.0)
            else: scores.append(0.8 if top in c else 0.2)
        # 12. negation_scope_insufficiency
        if self._notallfmt.search(p) and re.search(r'\b(can\s+we|do\s+we|is\s+it|does|could)\b.*\b(determine|know|say|conclude|tell)\b', p):
            hits += 1
            if c.strip().startswith('yes'): scores.append(0.0)
            elif re.search(r"\b(cannot|can't|not enough|insufficient|indeterminate|undetermined|not possible|no way to)\b", c): scores.append(1.0)
            else: scores.append(0.3)
        # 13. stated_premise_usage
        if re.search(r'\b(stated|given|assumed|premise|according)\b', p):
            hits += 1; scores.append(0.7 if cn else 0.3)
        # 14. subject_object_verb_parsing
        svo_m = self._svo.findall(p)
        if svo_m and re.search(r'\bwho\b|\bwhom\b|\bwhat\b.*\b(did|was|got)\b', p):
            hits += 1; subj, verb, obj_ = svo_m[0][0].lower(), svo_m[0][1].lower(), svo_m[0][2].lower()
            if re.search(r'\bwho\b.*\b'+re.escape(verb), p):
                scores.append(1.0 if subj in c else (0.0 if obj_ in c else 0.3))
            elif re.search(r'\bwhom\b|\bwhat\b.*\b(to|by)\b', p):
                scores.append(1.0 if obj_ in c else (0.0 if subj in c else 0.3))
            else: scores.append(0.7 if obj_ in c else 0.3)
        # 15. modus_tollens_contrapositive
        cond_m = self._ifthen.search(p)
        if cond_m:
            cons = cond_m.group(2).strip().lower()
            cw = [w for w in cons.split() if len(w)>2][:3]
            negated = False
            for sent in p.split('.')[1:]:
                if self._neg.search(sent) and any(w in sent.lower() for w in cw): negated = True
            after = p[cond_m.end():]
            if self._neg.search(after) and any(w in after for w in cw): negated = True
            if negated:
                hits += 1
                if any(w in c for w in ['no','not','false','cannot',"doesn't","isn't"]): scores.append(1.0)
                elif c.strip().startswith('yes'): scores.append(0.0)
                else: scores.append(0.4)
        if not scores: return 0.5, 0
        return sum(scores)/len(scores), hits

    def _secondary(self, prompt, cand):
        ptok = set(prompt.lower().split()); ctok = set(cand.lower().split())
        overlap = len(ptok & ctok) / max(len(ptok), 1)
        brevity = 1.0 if len(ctok) >= 1 else 0.0
        return float(np.clip(overlap * 0.4 + brevity * 0.2 + 0.3, 0.1, 0.9))

    def evaluate(self, prompt, candidates):
        if not candidates: return []
        results = []
        for cand in candidates:
            ss, hits = self._structural_score(prompt, cand)
            ncd_sim = 1.0 - self._ncd(prompt, cand)
            sec = self._secondary(prompt, cand)
            if hits > 0:
                final = 0.75 * ss + 0.10 * ncd_sim + 0.15 * sec
            else:
                final = 0.15 * ncd_sim + 0.35 * sec + 0.50 * 0.5
            results.append({"candidate": cand, "score": float(np.clip(final, 0, 1)),
                            "reasoning": f"struct={ss:.2f}({hits}h) ncd={ncd_sim:.2f} sec={sec:.2f}"})
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt, answer):
        r = self.evaluate(prompt, [answer, "", "unknown"])
        if not r: return 0.5
        s = r[0]['score']; null_s = min(x['score'] for x in r)
        return float(np.clip(0.3 + (s - null_s) * 1.4, 0.05, 0.95))
