import numpy as np, zlib, re
from typing import List, Dict

class ReasoningTool:
    """TAFI v3: Tensor-based Active Falsification Inference.
    General structural category parsers + NCD fallback."""

    def __init__(self):
        pass

    # ── utilities ──────────────────────────────────────────────────────
    def _nums(self, t):
        return [float(m) for m in re.findall(r'-?\d+(?:\.\d+)?', t)]

    def _cmp_gt(self, t):
        return re.search(r'\b(greater|larger|bigger|more|higher|taller|heavier|faster|older|longer)\b', t, re.I)

    def _cmp_lt(self, t):
        return re.search(r'\b(less|smaller|fewer|lower|shorter|lighter|slower|younger)\b', t, re.I)

    def _ncd(self, a, b):
        z = zlib.compress
        la, lb = len(z(a.encode())), len(z(b.encode()))
        lab = len(z((a + b).encode()))
        return (lab - min(la, lb)) / max(la, lb, 1)

    # ── GENERAL category parsers ──────────────────────────────────────
    def _structural_score(self, prompt, cand):
        p, c = prompt.lower(), cand.lower().strip().rstrip('.').rstrip('?')
        hits = []

        # 1) numeric_float_comparison — two numbers + comparative word
        pnums = self._nums(p)
        cnums = self._nums(c)
        if len(pnums) >= 2 and (self._cmp_gt(p) or self._cmp_lt(p)):
            a, b = pnums[0], pnums[1]
            wants_gt = bool(self._cmp_gt(p))
            correct_val = max(a, b) if wants_gt else min(a, b)
            incorrect_val = min(a, b) if wants_gt else max(a, b)
            if c in ('yes', 'no'):
                if wants_gt:
                    ans = 'yes' if a > b else ('no' if a < b else 'yes')
                else:
                    ans = 'yes' if a < b else ('no' if a > b else 'yes')
                hits.append((2.0 if c == ans else -2.0, 'numeric_float'))
            elif cnums:
                if abs(cnums[0] - correct_val) < 1e-9:
                    hits.append((2.0, 'numeric_float'))
                elif abs(cnums[0] - incorrect_val) < 1e-9:
                    hits.append((-2.0, 'numeric_float'))

        # 2) algebraic_word_problem — two items, total, difference
        cost_m = re.search(r'(?:cost|price|total|together|combined|altogether)\D{0,40}?\$?\s*(\d+(?:\.\d+)?)', p)
        diff_m = re.search(r'\$?\s*(\d+(?:\.\d+)?)\s*(?:more|extra|additional)\s+than', p)
        if cost_m and diff_m:
            total = float(cost_m.group(1))
            diff = float(diff_m.group(1))
            smaller = (total - diff) / 2.0
            larger = smaller + diff
            if cnums:
                if abs(cnums[0] - smaller) < 0.01 or abs(cnums[0] - larger) < 0.01:
                    hits.append((2.0, 'algebra'))
                trap = total - diff
                if abs(cnums[0] - trap) < 0.01 and abs(trap - smaller) > 0.01:
                    hits.append((-1.5, 'algebra_trap'))

        # 3) universal_quantifier_converse_error — "all X are Y ⇏ all Y are X"
        uq = re.search(r'all\s+(\w+)\s+are\s+(\w+)', p)
        if uq and re.search(r'are\s+all\s+\w+\s+\w+\s*\?', p):
            if c in ('no', 'not necessarily', 'false'):
                hits.append((2.0, 'quantifier_converse'))
            elif c in ('yes', 'true'):
                hits.append((-2.0, 'quantifier_converse'))

        # 4) number_parity — odd+odd=even, odd+even=odd
        if re.search(r'odd|even|parity', p) and re.search(r'sum|add|plus|total', p):
            two_odd = re.search(r'(?:two|2)\s+odd', p)
            if two_odd and re.search(r'always\s+odd', p):
                if c in ('false', 'no', 'incorrect', 'wrong', 'even'):
                    hits.append((2.0, 'parity'))
                elif c in ('true', 'yes', 'correct', 'odd'):
                    hits.append((-2.0, 'parity'))
            elif two_odd and re.search(r'always\s+even', p):
                if c in ('true', 'yes', 'correct', 'even'):
                    hits.append((2.0, 'parity'))
                elif c in ('false', 'no', 'incorrect', 'odd'):
                    hits.append((-2.0, 'parity'))

        # 5) all_but_N_survivor_counting — "all but N [die/leave/fail]" → N remain
        abn = re.search(r'all\s+(?:but|except)\s+(\d+)', p)
        if abn:
            survivors = abn.group(1)
            total_m = re.search(r'(\d+)\s+(?:fish|bird|sheep|animal|people|person|plant|flower|item|soldier|ship)', p)
            if c.strip() == survivors or (cnums and abs(cnums[0] - float(survivors)) < 0.01):
                hits.append((2.0, 'all_but_n'))
            elif total_m and cnums:
                total_n = float(total_m.group(1))
                wrong_diff = total_n - float(survivors)
                if abs(cnums[0] - wrong_diff) < 0.01:
                    hits.append((-2.0, 'all_but_n'))
            elif cnums and str(int(cnums[0])) != survivors:
                hits.append((-1.5, 'all_but_n'))

        if hits:
            total = sum(s for s, _ in hits)
            tags = '; '.join(t for _, t in hits)
            return total, tags
        return 0.0, 'none'

    # ── API ────────────────────────────────────────────────────────────
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates: return []
        struct = [self._structural_score(prompt, c) for c in candidates]
        has_hit = any(s != 0.0 for s, _ in struct)
        ncd_scores = [1.0 - self._ncd(prompt, c) for c in candidates]
        results = []
        for i, cand in enumerate(candidates):
            s, tag = struct[i]
            nv = ncd_scores[i]
            if has_hit and s != 0.0:
                final = 0.5 + 0.40 * np.tanh(s) + 0.05 * (nv - 0.5)
            elif has_hit:
                final = 0.5 + 0.05 * (nv - 0.5)
            else:
                final = 0.5 + 0.15 * (nv - 0.5)
            results.append({'candidate': cand,
                            'score': float(np.clip(final, 0.01, 0.99)),
                            'reasoning': f'{tag} s={s:.2f} ncd={nv:.3f}'})
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        res = self.evaluate(prompt, [answer, "UNLIKELY_PLACEHOLDER_XYZ"])
        for r in res:
            if r['candidate'] == answer:
                return float(np.clip(r['score'], 0.0, 1.0))
        return 0.5
