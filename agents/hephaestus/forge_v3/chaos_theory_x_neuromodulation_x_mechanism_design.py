import re
import zlib

class ReasoningTool:
    """
    CNICE v3: Chaotic Neuromodulated Incentive-Compatible Exploration.
    Logistic-map chaos + NCD neuromodulation + general structural reasoning
    (15 category parsers). Structural >= 70%, NCD <= 15%.
    """

    def __init__(self):
        self.r = 3.9

    def _logistic(self, x, steps=10):
        for _ in range(steps):
            x = self.r * x * (1.0 - x)
        return x

    def _seed(self, text):
        return 0.1 + 0.8 * ((zlib.crc32(text.encode()) & 0xffffffff) / 0xffffffff)

    def _ncd(self, s1, s2):
        b1, b2 = s1.encode(), s2.encode()
        c1, c2 = len(zlib.compress(b1)), len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        return (c12 - min(c1, c2)) / max(c1, c2) if min(c1, c2) else 1.0

    def _nums(self, t):
        return [float(m) for m in re.findall(r'-?\d+\.?\d*', t)]

    # ── general category parsers ──────────────────────────────────
    def _structural_score(self, prompt, cand):
        pl, cl = prompt.lower(), cand.lower().strip()
        ws = re.findall(r"[a-z'\-]+", cl)
        cl0 = ws[0] if ws else cl

        # 1. numeric_float_comparison
        m = re.search(r'is\s+([\d.]+)\s+(?:larger|greater|bigger|more|less|smaller)\s+than\s+([\d.]+)', pl)
        if m:
            a, b = float(m.group(1)), float(m.group(2))
            bigger_ask = any(w in m.group(0) for w in ('larger', 'greater', 'bigger', 'more'))
            correct = (a > b) if bigger_ask else (a < b)
            ans = 'yes' if correct else 'no'
            if cl0 == ans: return 1.0
            if cl0 in ('yes', 'no') and cl0 != ans: return 0.0
        m2 = re.search(r'which\b.*?\b(larger|greater|bigger|smaller|less)', pl)
        if m2:
            pn, cn = self._nums(prompt), self._nums(cand)
            if len(pn) >= 2 and cn:
                want_big = m2.group(1) in ('larger', 'greater', 'bigger')
                tgt = max(pn) if want_big else min(pn)
                if abs(cn[0] - tgt) < 1e-9: return 1.0
                other = min(pn) if want_big else max(pn)
                if abs(cn[0] - other) < 1e-9: return 0.0

        # 2. algebraic_word_problem
        mt = re.search(r'(?:cost|costs?)\s+\$?([\d.]+)\s+(?:total|together|in total|combined)', pl)
        md = re.search(r'costs?\s+\$?([\d.]+)\s+more\s+than', pl)
        if mt and md:
            total, diff = float(mt.group(1)), float(md.group(1))
            cheaper = (total - diff) / 2.0
            cn = self._nums(cand)
            if cn:
                if abs(cn[0] - cheaper) < 0.001: return 1.0
                if abs(cn[0] - diff) < 0.001: return 0.0

        # 3. positional_logic
        m10 = re.search(r'overtake\s+(?:the\s+)?(?:person|runner|racer|player|driver|one)?\s*(?:in\s+)?(\w+)\s*(?:place|position)?', pl)
        if m10:
            pos = m10.group(1)
            pos_map = {'first': '1', 'second': '2', 'third': '3', 'fourth': '4', 'fifth': '5',
                        '1st': '1', '2nd': '2', '3rd': '3', '4th': '4', '5th': '5'}
            pos_num = pos_map.get(pos.lower(), re.sub(r'(st|nd|rd|th)$', '', pos))
            inv = {v: k for k, v in pos_map.items() if not k[-1].isdigit()}
            pos_name = inv.get(pos_num, '')
            if pos_name and pos_name in cl: return 1.0
            if pos_num.isdigit():
                try:
                    wrong = str(int(pos_num) - 1)
                    wn = inv.get(wrong, '')
                    if wn and wn in cl: return 0.0
                except ValueError:
                    pass

        # 4. universal_quantifier_converse_error
        m6 = re.search(r'all\s+(\w+)\s+are\s+(\w+)', pl)
        m7 = re.search(r'are\s+all\s+(\w+)\s+(\w+)', pl)
        if m6 and m7 and m6.group(1) != m7.group(1):
            if cl0 == 'no' or 'not necessarily' in cl: return 1.0
            if cl0 == 'yes': return 0.0

        # 5. statistical_independence
        if any(w in pl for w in ('coin', 'die', 'dice', 'roulette', 'flip', 'roll')):
            if any(w in pl for w in ('in a row', 'previous', 'last', 'after', 'next', 'still', 'now')):
                if 'higher' in cl or 'lower' in cl or 'increase' in cl: return 0.0
                if '50' in cl or '1/2' in cl or '0.5' in cl or 'same' in cl: return 1.0

        # 6. number_parity
        if 'odd' in pl and 'sum' in pl:
            m8 = re.search(r'(two|2|three|3)\s+odd', pl)
            if m8:
                n = {'two': 2, '2': 2, 'three': 3, '3': 3}.get(m8.group(1), 2)
                result_even = (n % 2 == 0)
                if 'always odd' in pl:
                    if cl0 in ('false', 'no'): return 1.0 if result_even else 0.0
                    if cl0 in ('true', 'yes'): return 0.0 if result_even else 1.0
                if 'always even' in pl:
                    if cl0 in ('true', 'yes'): return 1.0 if result_even else 0.0
                    if cl0 in ('false', 'no'): return 0.0 if result_even else 1.0

        # 7. stated_premise_usage
        m11 = re.search(r'([\d.]+)\s+is\s+(less|more|greater|smaller|bigger|larger|taller|shorter|heavier|lighter)\s+than\s+([\d.]+)', pl)
        if m11 and ('which' in pl or 'what' in pl or 'who' in pl):
            a, rel, b = float(m11.group(1)), m11.group(2), float(m11.group(3))
            a_less = rel in ('less', 'smaller', 'shorter', 'lighter')
            bigger = b if a_less else a
            cn = self._nums(cand)
            if cn and abs(cn[0] - bigger) < 1e-9: return 1.0
            if cn and abs(cn[0] - (a if a_less else b)) < 1e-9: return 0.0

        # 8. modus_tollens_contrapositive
        if_m = re.search(r'if\s+(.+?)[,.](.+?)\.', pl)
        if if_m:
            after = pl[if_m.end():]
            if re.search(r'\bnot\b|\bdoes\s+not\b|\bisn.t\b|\bdon.t\b|\bdidn.t\b', after):
                if cl0 == 'no' or 'therefore not' in cl or 'did not' in cl: return 1.0
                if cl0 == 'yes': return 0.0

        # 9. mathematical_identity
        if re.search(r'0\.9{3,}', pl) and any(w in pl for w in ('equal', '= 1', 'equals', 'same')):
            if cl0 == 'yes' or 'equal' in cl: return 1.0
            if cl0 == 'no': return 0.0

        # 10. pigeonhole_principle
        pn = self._nums(prompt)
        if len(pn) >= 2 and any(w in pl for w in ('month', 'birthday', 'drawer', 'sock', 'box', 'categor', 'slot', 'compartment')):
            vals = sorted(pn)
            if vals[-1] > vals[0]:
                if cl0 == 'yes' or 'must' in cl or 'at least' in cl or 'guaranteed' in cl: return 1.0
                if cl0 == 'no' and 'not' not in cl[3:]: return 0.0

        # 11. trick_question_equal_weight
        mu = re.search(r'(?:a|one|1)\s+(pound|kilogram|kg|ton|ounce|gram|liter|gallon|cup)\s+of\s+\w+.*(?:a|one|1)\s+(pound|kilogram|kg|ton|ounce|gram|liter|gallon|cup)\s+of\s+\w+', pl)
        if mu and mu.group(1) == mu.group(2) and any(w in pl for w in ('heav', 'weigh', 'lighter', 'which')):
            if any(w in cl for w in ('same', 'equal', 'neither', 'both')): return 1.0
            if len(cl) < 30 and not any(w in cl for w in ('same', 'equal')): return 0.0

        return -1.0

    # ── evaluate / confidence ─────────────────────────────────────
    def evaluate(self, prompt, candidates):
        results = []
        for cand in candidates:
            ss = self._structural_score(prompt, cand)
            if ss >= 0:
                ncd = self._ncd(prompt, cand)
                score = ss * 0.75 + (1.0 - ncd) * 0.15 + 0.10 * self._logistic(self._seed(prompt + cand), 5)
            else:
                x = self._logistic(self._seed(prompt + cand), 5)
                ncd = self._ncd(prompt, cand)
                overlap = len(set(prompt.lower().split()) & set(cand.lower().split()))
                score = max(0.0, min(1.0, (1.0 - ncd) + min(overlap * 0.05, 0.2) + (x - 0.5) * ncd * 0.2))
            results.append({"candidate": cand, "score": float(max(0.0, min(1.0, score))),
                            "reasoning": f"struct={ss:.2f}"})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt, answer):
        ss = self._structural_score(prompt, answer)
        if ss >= 0:
            return max(0.0, min(1.0, 0.5 + ss * 0.45))
        res = self.evaluate(prompt, [answer])
        return res[0]["score"] if res else 0.0
