"""ToM Perspective Shift Specialist — Frame D (Judgment Calibrator).
PRIMARY: tom_perspective_shift (spatial perspective-taking across facing agents).
Covers all standard parsers + Tier B meta-confidence."""
import re, zlib, math
from collections import defaultdict

_NUM = re.compile(r'-?\d+(?:\.\d+)?')

# === Perspective shift patterns ===
# Pattern 1: "X sees the Y on her left/right. Z faces X from the opposite side"
_PERSP1 = re.compile(
    r'(\w+)\s+sees?\s+(?:the\s+)?(\w+)\s+on\s+(?:her|his|their)\s+(left|right)'
    r'.*?(\w+)\s+faces?\s+\1\s+from\s+(?:the\s+)?opposite', re.I | re.S)
# Pattern 2: "From X's seat, the Y is on the left. Z sits directly across from X"
_PERSP2 = re.compile(
    r'[Ff]rom\s+(\w+)\'?s?\s+seat,?\s+(?:the\s+)?(\w+)\s+is\s+on\s+the\s+(left|right)'
    r'.*?(\w+)\s+sits?\s+(?:directly\s+)?(?:across|opposite)\s+(?:from\s+)?\1', re.I | re.S)
# Pattern 3: Reversed order - asker mentioned before seer
_PERSP3 = re.compile(
    r'(\w+)\s+(?:faces?|sits?\s+(?:directly\s+)?(?:across|opposite))\s+(?:from\s+)?(\w+)'
    r'.*?(?:the\s+)?(\w+)\s+(?:is\s+)?on\s+(\w+)\'?s?\s+(left|right)', re.I | re.S)

# === Causal intervention ===
_LEADS = re.compile(r'(\w[\w\s]*?)\s+(?:leads?\s+to|causes?|results?\s+in)\s+(\w[\w\s]*?)(?:[.,;]|$)', re.I)
_WHICH_LEADS = re.compile(r'which\s+leads?\s+to\s+(\w[\w\s]*?)(?:[.,;]|$)', re.I)
_INTERVENE = re.compile(r'(?:intervene\s+to\s+block|forcibly\s+prevent|block)\s+(\w[\w\s]*?)(?:[.,;?]|$)', re.I)
_FORCE = re.compile(r'(?:force|set|clamp|fix|intervene\s+on)\s*\(?\s*(\w+)\s*(?:=|to)\s*(\S+)', re.I)

# === Standard parsers ===
_BAT = re.compile(r'(?:cost|total)s?\s+\$?([\d.]+).*?costs?\s+\$?([\d.]+)\s+more', re.I)
_ALLBUT = re.compile(r'[Aa]ll\s+(?:but|except)\s+(\d+)', re.I)
_FENCE = re.compile(r'(\d+)\s*(?:fence\s*)?posts?\s.*?(\d+)\s*(?:meter|feet|ft|m|yard)', re.I)
_MOD = re.compile(r'(\d+)\s*(?:mod|%|modulo)\s*(\d+)', re.I)
_COINS = re.compile(r'(?:coin|flip|toss)', re.I)
_PARITY = re.compile(r'(odd|even)\s*(?:\+|plus|and|times|\*|minus|-)\s*(odd|even)', re.I)
_PIGEON = re.compile(r'(\d+)\s*(?:items?|objects?|pigeons?|people|balls?).*?(\d+)\s*(?:boxes|holes?|slots?|containers?)', re.I)
_PCT = re.compile(r'(?:increase|decrease).*?(\d+)\s*%', re.I)
_BASERATE = re.compile(r'(\d+)\s*(?:in|out\s*of)\s*(\d+)', re.I)
_SVO = re.compile(r'[Tt]he\s+(\w+)\s+(\w+ed)\s+the\s+(\w+)', re.I)
_ALLARB = re.compile(r'[Aa]ll\s+(\w+)\s+are\s+(\w+)')
_NOTALLARB = re.compile(r'[Nn]ot\s+all\s+(\w+)\s+are\s+(\w+)')
_COND = re.compile(r'[Ii]f\s+(.+?),?\s+then\s+(.+?)(?:[.,;]|$)')
_NEG = re.compile(r'\b(?:not|no|never|neither|nor)\b', re.I)
_DIR = re.compile(r'(north|south|east|west)', re.I)

# === Tier B ===
_TB = {'presup': r'(?:stopped|still|again|already|anymore)',
       'scope': r'(?:every.*?some|all.*?not|not.*?all)',
       'fdichotomy': r'(?:either.*?or|must\s+be\s+one)',
       'survivor': r'(?:successful|survivors?|winners?|made\s+it)',
       'sunk': r'(?:already\s+(?:spent|invested|paid)|too\s+late\s+to)'}
_TIERB = {k: re.compile(v, re.I) for k, v in _TB.items()}

def _ns(t): return [float(x) for x in _NUM.findall(t)]
def _h(t, *ws): return any(w in t for w in ws)


class ReasoningTool:

    def _ncd(self, a, b):
        if not a or not b: return 1.0
        ca, cb = len(zlib.compress(a.encode())), len(zlib.compress(b.encode()))
        d = max(ca, cb)
        return (len(zlib.compress((a + " " + b).encode())) - min(ca, cb)) / d if d else 1.0

    def _meta_confidence(self, p):
        pl = p.lower()
        if re.search(r'\b(?:have|has)\s+\w+\s+(?:stopped|quit|given\s+up)', pl): return 0.20
        if re.search(r'\bevery\b.*\b(?:a|some)\b.*\?', pl): return 0.20
        if re.search(r'already\s+(?:spent|invested|paid)', pl): return 0.20
        if re.search(r'either.*?or|must\s+be\s+one', pl) and len(pl.split()) > 15: return 0.25
        if re.search(r'(?:successful|survivors?).*(?:sample|study)', pl): return 0.20
        if re.search(r'non-?refundable', pl): return 0.20
        n = sum(1 for v in _TIERB.values() if v.search(pl))
        return max(0.20, 1.0 - 0.15 * n) if n else 1.0

    # ---- PRIMARY: perspective shift ----
    def _perspective_shift(self, p, c):
        pl, cl = p.lower(), c.lower()

        # Try all perspective patterns
        m = _PERSP1.search(p)
        if m:
            seer, obj, side, asker = m.group(1), m.group(2), m.group(3).lower(), m.group(4)
            opposite = 'right' if side == 'left' else 'left'
            asker_l = asker.lower()
            # When facing opposite, left↔right flips
            if opposite in cl:
                return 0.95
            if side in cl and 'same' not in cl:
                return 0.08
            if 'same' in cl or 'cannot' in cl:
                return 0.08
            return 0.50

        m = _PERSP2.search(p)
        if m:
            seer, obj, side, asker = m.group(1), m.group(2), m.group(3).lower(), m.group(4)
            opposite = 'right' if side == 'left' else 'left'
            if opposite in cl:
                return 0.95
            if side in cl and 'same' not in cl:
                return 0.08
            if 'same' in cl or 'cannot' in cl:
                return 0.08
            return 0.50

        m = _PERSP3.search(p)
        if m:
            asker, seer, obj, ref_name, side = m.group(1), m.group(2), m.group(3), m.group(4), m.group(5).lower()
            opposite = 'right' if side == 'left' else 'left'
            if opposite in cl:
                return 0.95
            if side in cl and 'same' not in cl:
                return 0.08
            if 'same' in cl or 'cannot' in cl:
                return 0.08
            return 0.50

        # Generic: detect "opposite side" + left/right in prompt
        if re.search(r'opposite\s+side', pl) and re.search(r'\b(left|right)\b', pl):
            side_m = re.search(r'on\s+(?:her|his|their)\s+(left|right)', pl) or re.search(r'on\s+the\s+(left|right)', pl)
            if side_m:
                side = side_m.group(1).lower()
                opposite = 'right' if side == 'left' else 'left'
                if opposite in cl: return 0.92
                if side in cl and 'same' not in cl: return 0.10
                if 'same' in cl or 'cannot' in cl: return 0.10

        return None

    # ---- Causal intervention ----
    def _causal_intervention(self, p, c):
        pl, cl = p.lower(), c.lower()
        chain = []
        leads = _LEADS.findall(p)
        wl = _WHICH_LEADS.findall(p)
        if leads:
            for a, b in leads:
                chain.append((a.strip().lower(), b.strip().lower()))
            for w in wl:
                if chain:
                    chain.append((chain[-1][1], w.strip().lower()))
        if not chain:
            return None
        blocked = None
        bm = _INTERVENE.search(p)
        if bm: blocked = bm.group(1).strip().lower()
        fm = _FORCE.search(p)
        if fm: blocked = fm.group(1).strip().lower()
        if not blocked: return None

        stops_words = ('stop', 'prevent', 'block', 'no longer', 'cease', 'halt')
        cannot_words = ('cannot determine', 'insufficient')
        if _h(cl, *cannot_words): return 0.10
        if _h(cl, 'still', 'continue', 'directly cause'): return 0.10
        if _h(cl, *stops_words): return 0.95
        return 0.50

    # ---- Standard parsers ----
    def _std(self, p, c):
        pl, cl = p.lower(), c.lower()
        cn, pn = _ns(c), _ns(p)

        bm = _BAT.search(pl)
        if bm:
            total, diff = float(bm.group(1)), float(bm.group(2))
            ans = (total - diff) / 2
            return 0.92 if cn and abs(cn[0] - ans) < 0.01 else 0.12

        abm = _ALLBUT.search(pl)
        if abm and 'how many' in pl:
            return 0.90 if cn and abs(cn[0] - int(abm.group(1))) < 0.5 else 0.12

        fm = _FENCE.search(p)
        if fm:
            ans = (int(fm.group(1)) - 1) * int(fm.group(2))
            return 0.90 if cn and abs(cn[0] - ans) < 0.5 else 0.12

        mm = _MOD.search(p)
        if mm:
            ans = int(mm.group(1)) % int(mm.group(2))
            return 0.90 if cn and abs(cn[0] - ans) < 0.01 else 0.12

        if _COINS.search(pl):
            if _h(cl, '1/2', '0.5', '50%', 'same', 'independent'): return 0.88
            if _h(cl, 'due', 'overdue', 'more likely'): return 0.12

        pm = _PARITY.search(pl)
        if pm:
            a, b = pm.group(1).lower(), pm.group(2).lower()
            op_text = pl[pm.start():pm.end()]
            if any(x in op_text for x in ('+', 'plus', 'and')):
                even = (a == b)
            else:
                even = (a == 'even' or b == 'even')
            expected = 'even' if even else 'odd'
            return 0.90 if expected in cl else 0.12

        pgm = _PIGEON.search(p)
        if pgm:
            items, boxes = int(pgm.group(1)), int(pgm.group(2))
            if items > boxes:
                ans = math.ceil(items / boxes)
                return 0.85 if cn and cn[0] >= ans else 0.15

        if _PCT.search(pl) and ('then' in pl or 'back' in pl):
            if _h(cl, 'not the same', 'less', 'lower', 'different'): return 0.85
            if _h(cl, 'same', 'original', 'equal'): return 0.12

        brm = _BASERATE.search(pl)
        if brm:
            num, den = float(brm.group(1)), float(brm.group(2))
            if den > 0 and num / den < 0.05:
                if _h(cl, 'low', 'unlikely', 'rare'): return 0.85
                if _h(cl, 'high', 'likely', 'certain'): return 0.12

        if pn and cn and re.search(r'(?:larger|greater|bigger)', pl):
            if len(pn) >= 2:
                ans = 'yes' if pn[0] > pn[1] else 'no'
                return 0.88 if _h(cl, ans) else 0.15

        cm = _COND.search(p)
        if cm and _NEG.search(p):
            if 'not' in cl or 'false' in cl: return 0.75
            return 0.35

        links = _ALLARB.findall(p)
        if len(links) >= 2:
            g = defaultdict(set)
            for a, b in links: g[a.lower()].add(b.lower())
            neg_links = _NOTALLARB.findall(p)
            broken = {(a.lower(), b.lower()) for a, b in neg_links}
            def reach(node, depth=0):
                if depth > 8: return set()
                r = set()
                for n in g.get(node, set()):
                    if (node, n) not in broken:
                        r.add(n); r |= reach(n, depth + 1)
                return r
            for nd in g:
                for t in reach(nd):
                    if nd in cl and t in cl:
                        if _h(cl, 'yes', 'true', 'is a', 'correct'): return 0.88
                        if _h(cl, 'no', 'false', 'not'): return 0.12

        svo = _SVO.search(p)
        if svo:
            ag, pt = svo.group(1).lower(), svo.group(3).lower()
            if 'who' in pl:
                if ag in cl: return 0.85
                if pt in cl: return 0.20

        dirs = _DIR.findall(p)
        if len(dirs) >= 2:
            dx, dy = 0, 0
            for d in dirs:
                d = d.lower()
                if d == 'north': dy += 1
                elif d == 'south': dy -= 1
                elif d == 'east': dx += 1
                elif d == 'west': dx -= 1
            result_parts = []
            if dy > 0: result_parts.append('north')
            elif dy < 0: result_parts.append('south')
            if dx > 0: result_parts.append('east')
            elif dx < 0: result_parts.append('west')
            if result_parts:
                return 0.88 if all(r in cl for r in result_parts) else 0.15

        if 'correlat' in pl and 'cause' in pl:
            return 0.85 if _h(cl, 'no', 'not', 'cannot') else 0.15

        if pn and cn and any(abs(a - b) < 0.01 for a in pn for b in cn):
            return 0.65

        return None

    def _score(self, p, c):
        for fn in (self._perspective_shift, self._causal_intervention):
            v = fn(p, c)
            if v is not None: return v, fn.__name__
        v = self._std(p, c)
        if v is not None: return v, 'standard'
        return 0.50 + (1.0 - self._ncd(p, c)) * 0.08, 'ncd_fallback'

    def evaluate(self, prompt: str, candidates: list) -> list:
        meta = self._meta_confidence(prompt)
        res = []
        for c in candidates:
            v, tag = self._score(prompt, c)
            res.append({
                'candidate': c,
                'score': round(v * (0.88 + 0.12 * meta), 4),
                'reasoning': tag,
                'meta': round(meta, 3)
            })
        res.sort(key=lambda r: r['score'], reverse=True)
        return res

    def confidence(self, prompt: str, answer: str) -> float:
        meta = self._meta_confidence(prompt)
        if meta < 0.30: return meta
        v, _ = self._score(prompt, answer)
        return round(min(meta, v), 4)
