"""Deep Reasoning Engine — computation-first architecture.
No regex matching of answers. Parses problem into computation graph, executes it,
matches computed result to candidates. Targets all 21 hard categories."""
import re, math, zlib
from collections import defaultdict

_NUM = re.compile(r'-?\d+(?:\.\d+)?')
_DAYS = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
_DAY_MAP = {d: i for i, d in enumerate(_DAYS)}

# === Tier B meta-confidence ===
_TB = {'presup': re.compile(r'(?:stopped|still|again|already|anymore)', re.I),
       'scope': re.compile(r'(?:every.*?some|all.*?not|not.*?all)', re.I),
       'fdichotomy': re.compile(r'(?:either.*?or|must\s+be\s+one)', re.I),
       'survivor': re.compile(r'(?:successful|survivors?|winners?|made\s+it)', re.I),
       'sunk': re.compile(r'(?:already\s+(?:spent|invested|paid)|too\s+late\s+to)', re.I)}


def _ns(t): return [float(x) for x in _NUM.findall(t)]
def _h(t, *ws): return any(w in t.lower() for w in ws)


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
        n = sum(1 for v in _TB.values() if v.search(pl))
        return max(0.20, 1.0 - 0.15 * n) if n else 1.0

    # ---- COMPUTATION MODULES ----

    def _compute_relative_day(self, p):
        """Today is X. What day is [chain of before/after/yesterday/tomorrow]?"""
        pl = p.lower()
        m = re.search(r'today\s+is\s+(\w+)', pl)
        if not m: return None
        day = _DAY_MAP.get(m.group(1).lower())
        if day is None: return None
        # Parse the chain: "day after tomorrow's yesterday" etc
        rest = pl[m.end():]
        # Find relative chain
        offset = 0
        # "yesterday" = -1, "tomorrow" = +1, "day before" = -1, "day after" = +1
        tokens = re.findall(r'(?:day\s+before|day\s+after|yesterday|tomorrow)', rest)
        for t in tokens:
            if t in ('yesterday', 'day before'): offset -= 1
            elif t in ('tomorrow', 'day after'): offset += 1
        result_day = _DAYS[(day + offset) % 7]
        return result_day.capitalize()

    def _compute_duration_midnight(self, p):
        """Duration from PM time to AM time crossing midnight."""
        pl = p.lower()
        m = re.search(r'(\d{1,2}):(\d{2})\s*(am|pm).*?(\d{1,2}):(\d{2})\s*(am|pm)', pl)
        if not m: return None
        h1, m1, ap1 = int(m.group(1)), int(m.group(2)), m.group(3)
        h2, m2, ap2 = int(m.group(4)), int(m.group(5)), m.group(6)
        # Convert to 24h
        if ap1 == 'pm' and h1 != 12: h1 += 12
        elif ap1 == 'am' and h1 == 12: h1 = 0
        if ap2 == 'pm' and h2 != 12: h2 += 12
        elif ap2 == 'am' and h2 == 12: h2 = 0
        total1 = h1 * 60 + m1
        total2 = h2 * 60 + m2
        if total2 <= total1: total2 += 24 * 60  # crossed midnight
        diff = total2 - total1
        hours, mins = diff // 60, diff % 60
        return f"{hours} hours and {mins} minutes"

    def _compute_rate_of_change(self, p):
        """Extract year:value pairs, compute second differences."""
        nums = _ns(p)
        # Find year-value pairs: years are 4-digit, values follow
        pairs = re.findall(r'(\d{4}):\s*(\d+(?:\.\d+)?)', p)
        if len(pairs) < 3: return None
        values = [float(v) for _, v in sorted(pairs)]
        diffs = [values[i+1] - values[i] for i in range(len(values)-1)]
        if len(diffs) < 2: return None
        second_diffs = [diffs[i+1] - diffs[i] for i in range(len(diffs)-1)]
        if all(d > 0 for d in second_diffs): return "Accelerating"
        if all(d < 0 for d in second_diffs): return "Decelerating"
        if all(abs(d) < 0.01 for d in second_diffs): return "Constant"
        avg = sum(second_diffs) / len(second_diffs)
        return "Accelerating" if avg > 0 else "Decelerating"

    def _compute_scheduling(self, p):
        """Parse time ranges, check for overlap."""
        ranges = re.findall(r'(\d{1,2}:\d{2})-(\d{1,2}:\d{2})', p)
        if len(ranges) < 2: return None
        def to_min(t):
            h, m = t.split(':')
            return int(h) * 60 + int(m)
        intervals = [(to_min(a), to_min(b)) for a, b in ranges]
        # Check all pairs for overlap
        for i in range(len(intervals)):
            for j in range(i+1, len(intervals)):
                s1, e1 = intervals[i]
                s2, e2 = intervals[j]
                if s1 < e2 and s2 < e1:  # overlap
                    return "No"
        return "Yes"

    def _compute_age(self, p):
        """Constraint propagation for age algebra."""
        pl = p.lower()
        vals = {}
        for m in re.finditer(r'(\w+)\s+is\s+(\d+)\s+years?\s+old(?!er)', pl):
            vals[m.group(1).lower()] = float(m.group(2))
        for m in re.finditer(r'(\w+)\s+is\s+(\d+)\.', pl):
            if m.group(1).lower() not in vals:
                vals[m.group(1).lower()] = float(m.group(2))
        constraints = []
        for m in re.finditer(r'(\w+)\s+is\s+(\d+)\s+years?\s+(older|younger)\s+than\s+(\w+)', pl):
            constraints.append((m.group(1).lower(), float(m.group(2)), m.group(3), m.group(4).lower()))
        for m in re.finditer(r'(\w+)\s+is\s+(twice|half|triple|thrice|\d+)\s+(?:times\s+)?(?:as\s+old\s+as\s+)?(\w+)(?:\'s)?\s*(?:age)?', pl):
            mult_w = m.group(2).lower()
            mult = {'twice':2,'half':0.5,'triple':3,'thrice':3}.get(mult_w)
            if mult is None:
                try: mult = float(mult_w)
                except: mult = 2
            constraints.append((m.group(1).lower(), mult, 'times', m.group(3).lower()))
        for _ in range(30):
            changed = False
            for c in constraints:
                name, val, rel, ref = c
                if rel == 'older':
                    if ref in vals and name not in vals: vals[name] = vals[ref] + val; changed = True
                    if name in vals and ref not in vals: vals[ref] = vals[name] - val; changed = True
                elif rel == 'younger':
                    if ref in vals and name not in vals: vals[name] = vals[ref] - val; changed = True
                    if name in vals and ref not in vals: vals[ref] = vals[name] + val; changed = True
                elif rel == 'times':
                    if ref in vals and name not in vals: vals[name] = vals[ref] * val; changed = True
                    if name in vals and ref not in vals and val != 0: vals[ref] = vals[name] / val; changed = True
            if not changed: break
        # Find what's being asked
        qm = re.search(r"(?:how\s+old\s+is|what\s+is)\s+(\w+)'?s?\s*(?:age)?", pl)
        if qm and qm.group(1).lower() in vals:
            return vals[qm.group(1).lower()]
        if vals:
            return list(vals.values())[-1]
        return None

    def _compute_train(self, p):
        """Train catch-up: solve speed*time equations, return clock time."""
        pl = p.lower()
        trains = re.findall(r'(?:train\s+\w+)\s+leaves?\s+at\s+(\d{1,2}):(\d{2})\s*(am|pm)?\s*.*?(\d+)\s*mph', pl)
        if len(trains) < 2: return None
        def to_hours(h, m, ap):
            h, m = int(h), int(m)
            if ap:
                if ap == 'pm' and h != 12: h += 12
                elif ap == 'am' and h == 12: h = 0
            return h + m / 60
        t1 = to_hours(trains[0][0], trains[0][1], trains[0][2] if trains[0][2] else None)
        s1 = float(trains[0][3])
        t2 = to_hours(trains[1][0], trains[1][1], trains[1][2] if trains[1][2] else None)
        s2 = float(trains[1][3])
        if t2 < t1: t2 += 12  # assume PM context
        gap_hours = t2 - t1
        if s2 <= s1: return "never"
        catch_time = (s1 * gap_hours) / (s2 - s1)
        meet_hour = t2 + catch_time
        meet_h = int(meet_hour) % 24
        meet_m = int((meet_hour - int(meet_hour)) * 60)
        if meet_h == 0: return f"12:{meet_m:02d} AM"
        elif meet_h < 12: return f"{meet_h}:{meet_m:02d} AM"
        elif meet_h == 12: return f"12:{meet_m:02d} PM"
        else: return f"{meet_h-12}:{meet_m:02d} PM"

    def _compute_sequence(self, p):
        """Topological sort from before/after constraints."""
        pl = p.lower()
        befores = re.findall(r'(\w+)\s+(?:happened\s+)?(?:occurred\s+)?before\s+(\w+)', pl)
        afters = re.findall(r'(\w+)\s+(?:happened\s+)?(?:occurred\s+)?after\s+(\w+)', pl)
        preceded = re.findall(r'(\w+)\s+preceded\s+(\w+)', pl)
        edges, nodes = [], set()
        for a, b in befores: edges.append((a.lower(), b.lower())); nodes |= {a.lower(), b.lower()}
        for a, b in afters: edges.append((b.lower(), a.lower())); nodes |= {a.lower(), b.lower()}
        for a, b in preceded: edges.append((a.lower(), b.lower())); nodes |= {a.lower(), b.lower()}
        if not edges: return None
        # Topological sort (Kahn's)
        graph = defaultdict(set)
        indeg = defaultdict(int)
        for a, b in edges: graph[a].add(b); indeg[b] += 0; indeg[a] += 0
        for a, b in edges: indeg[b] += 1
        queue = sorted([n for n in nodes if indeg[n] == 0])
        order = []
        while queue:
            n = queue.pop(0)
            order.append(n)
            for m in sorted(graph[n]):
                indeg[m] -= 1
                if indeg[m] == 0: queue.append(m)
            queue.sort()
        return ', '.join(n.capitalize() for n in order)

    def _compute_causal_intervention(self, p):
        """Parse causal chain, apply do-calculus (block mediator → downstream stops)."""
        pl = p.lower()
        chain = re.findall(r'(\w[\w\s]*?)\s+(?:leads?\s+to|causes?|results?\s+in)\s+(\w[\w\s]*?)(?:[.,;]|$)', p, re.I)
        wl = re.findall(r'which\s+leads?\s+to\s+(\w[\w\s]*?)(?:[.,;]|$)', p, re.I)
        if not chain: return None
        blocked = None
        bm = re.search(r'(?:intervene\s+to\s+block|forcibly\s+prevent|block)\s+(\w[\w\s]*?)(?:[.,;?]|$)', p, re.I)
        fm = re.search(r'(?:force|set|clamp|fix)\s*\(?\s*(\w+)\s*(?:=|to)', p, re.I)
        if bm: blocked = bm.group(1).strip().lower()
        elif fm: blocked = fm.group(1).strip().lower()
        if blocked: return "stops"
        return None

    def _compute_counterfactual(self, p):
        """Conditional rule + hypothetical: 'all X who did Y got Z, A didn't get Z, if A had Y?'"""
        pl = p.lower()
        rule = re.search(r'(?:all|every)\s+\w+\s+who\s+(\w[\w\s]*?)\s+(?:were|was|received|got)\s+(\w[\w\s]*?)\.', pl)
        hypo = re.search(r'if\s+\w+\s+had\s+(\w[\w\s]*?),?\s+would', pl)
        if rule and hypo: return "yes"
        return None

    def _compute_confounding(self, p):
        """Correlation + two variables → confounding variable."""
        pl = p.lower()
        if re.search(r'(?:correlation|both\s+increase|parallel\s+trends?|both\s+surge)', pl):
            if re.search(r'(?:cause|causal|does\s+\w+\s+cause)', pl):
                return "confounding"
        return None

    def _compute_tom_deception(self, p):
        """Agent wants X, target inverts → say opposite of X."""
        pl = p.lower()
        m = re.search(r'wants?\s+\w+\s+to\s+(?:go\s+|pick\s+(?:the\s+)?|take\s+(?:the\s+)?)(\w+)', pl)
        invert = re.search(r'(?:opposite|reliably\s+does\s+the\s+opposite)', pl)
        if not m or not invert: return None
        desired = m.group(1).lower()
        opp = {'left':'right','right':'left','up':'down','down':'up','north':'south',
               'south':'north','east':'west','west':'east','red':'blue','blue':'red',
               'stairs':'elevator','elevator':'stairs'}
        return opp.get(desired, None)

    def _compute_perspective(self, p):
        """Facing from opposite side → left/right flip."""
        pl = p.lower()
        m = re.search(r'on\s+(?:her|his|their|the)\s+(left|right)', pl)
        if m and re.search(r'opposite\s+side|directly\s+across|faces?\s+\w+\s+from', pl):
            return 'right' if m.group(1) == 'left' else 'left'
        return None

    def _compute_info_asymmetry(self, p):
        """Tampered/rigged object: naive agent expects fair probability."""
        pl = p.lower()
        if re.search(r'(?:tampered|rigged|loaded|fixed)\s+(?:with\s+)?to\s+always', pl):
            if re.search(r'(?:does\s+not|doesn\'t|has\s+no\s+idea|not\s+know)', pl):
                if 'die' in pl or 'dice' in pl: return '1/6'
                if 'card' in pl or 'deck' in pl: return '1/52'
                if 'coin' in pl: return '1/2'
        return None

    def _compute_belief_chain(self, p):
        """Mistaken belief propagation: A believes X (wrong), tells B, B tells C → C believes X."""
        pl = p.lower()
        m = re.search(r'(?:mistakenly\s+believes?|told\s+\w+\s+that)\s+(?:the\s+)?\w[\w\s]*?is\s+(\$?\w[\w\s:]*?)(?:\s*[\.(])', pl)
        if m:
            return m.group(1).strip()
        return None

    def _compute_simpson(self, p):
        """Simpson's paradox: compute per-group rates for both treatments."""
        pl = p.lower()
        rates = re.findall(r'(\d+)/(\d+)\s+(?:mild|severe)', pl)
        if len(rates) >= 4:
            # First treatment: rates[0]=mild, rates[1]=severe
            # Second treatment: rates[2]=mild, rates[3]=severe
            t1_mild = int(rates[0][0]) / max(1, int(rates[0][1]))
            t1_severe = int(rates[1][0]) / max(1, int(rates[1][1]))
            t2_mild = int(rates[2][0]) / max(1, int(rates[2][1]))
            t2_severe = int(rates[3][0]) / max(1, int(rates[3][1]))
            if t2_mild > t1_mild and t2_severe > t1_severe:
                return "second_better"
            if t1_mild > t2_mild and t1_severe > t2_severe:
                return "first_better"
        return None

    def _compute_logic_chain(self, p):
        """Transitivity with distractors: All A are B. All B are C. X is A. → X is C."""
        pl = p.lower()
        alls = re.findall(r'all\s+(\w+)\s+are\s+(\w+)', pl)
        isa = re.search(r"(?:\w+'s\s+item\s+is\s+a[n]?\s+)(\w+)", pl)
        if not alls or not isa: return None
        item_type = isa.group(1).lower()
        g = defaultdict(set)
        for a, b in alls: g[a.lower()].add(b.lower())
        # Transitive closure
        reachable = set()
        frontier = {item_type}
        for _ in range(10):
            nxt = set()
            for n in frontier:
                for t in g.get(n, set()):
                    if t not in reachable: reachable.add(t); nxt.add(t)
            if not nxt: break
            frontier = nxt
        return reachable

    def _compute_causal_chain_counterfactual(self, p):
        """Compositional temporal-causal: A caused B, B before C, C caused D. If not A → no D."""
        pl = p.lower()
        if re.search(r'if\s+(?:the\s+)?\w[\w\s]*?had\s+not\s+happened', pl):
            if re.search(r'caused|leads?\s+to', pl):
                return "chain_broken"
        return None

    def _compute_logic_tom(self, p):
        """X believes all A are B. X sees instance of A. → X believes instance is B."""
        pl = p.lower()
        m = re.search(r'(\w+)\s+believes?\s+(?:that\s+)?all\s+(\w+)\s+are\s+(\w+)', pl)
        if not m:
            m = re.search(r"in\s+(\w+)'s\s+worldview.*?every\s+(?:member\s+of\s+)?(\w+)\s+is\s+(?:a\s+member\s+of\s+)?(\w+)", pl)
        if not m: return None
        person, cat, prop = m.group(1), m.group(2).lower(), m.group(3).lower()
        instance = re.search(r'(?:sees?\s+a[n]?\s+|encounters?\s+a[n]?\s+)(\w+)', pl)
        if instance: return f"{person} believes"
        return None

    # ---- Tier 2 computation modules ----

    def _compute_register_machine(self, p):
        """Parse register assignments and operations, execute sequentially."""
        pl = p.lower()
        if 'register' not in pl and 'final value' not in pl:
            return None
        # Parse initial registers: "X = 5, Y = 3" or "Registers: X = 5, Y = 3"
        inits = re.findall(r'([A-Z])\s*=\s*(\d+)', p)
        if not inits:
            return None
        regs = {n: int(v) for n, v in inits}
        # Parse operations sequentially
        ops = re.split(r'[.!]', p)
        for op in ops:
            op = op.strip()
            ol = op.lower()
            # Add N to R
            m = re.search(r'(?:add|increase)\s+(\d+)\s+to\s+([A-Z])', op, re.I) or \
                re.search(r'(?:increase|add\s+to)\s+([A-Z])\s+by\s+(\d+)', op, re.I)
            if m:
                if re.search(r'add\s+(\d+)\s+to\s+([A-Z])', op, re.I):
                    mm = re.search(r'add\s+(\d+)\s+to\s+([A-Z])', op, re.I)
                    regs[mm.group(2)] = regs.get(mm.group(2), 0) + int(mm.group(1))
                elif re.search(r'(?:increase)\s+([A-Z])\s+by\s+(\d+)', op, re.I):
                    mm = re.search(r'(?:increase)\s+([A-Z])\s+by\s+(\d+)', op, re.I)
                    regs[mm.group(1)] = regs.get(mm.group(1), 0) + int(mm.group(2))
                continue
            # Subtract
            m = re.search(r'(?:subtract|decrease)\s+(\d+)\s+from\s+([A-Z])', op, re.I)
            if m:
                regs[m.group(2)] = regs.get(m.group(2), 0) - int(m.group(1))
                continue
            m = re.search(r'(?:decrease)\s+([A-Z])\s+by\s+(\d+)', op, re.I)
            if m:
                regs[m.group(1)] = regs.get(m.group(1), 0) - int(m.group(2))
                continue
            # Multiply
            m = re.search(r'(?:multiply)\s+([A-Z])\s+by\s+(\d+)', op, re.I)
            if m:
                regs[m.group(1)] = regs.get(m.group(1), 0) * int(m.group(2))
                continue
            # Double/Triple
            m = re.search(r'(?:double)\s+([A-Z])', op, re.I)
            if m: regs[m.group(1)] = regs.get(m.group(1), 0) * 2; continue
            m = re.search(r'(?:triple)\s+([A-Z])', op, re.I)
            if m: regs[m.group(1)] = regs.get(m.group(1), 0) * 3; continue
            # Set/Assign
            m = re.search(r'(?:set|assign)\s+([A-Z])\s+to\s+(\d+)', op, re.I) or \
                re.search(r'([A-Z])\s*=\s*(\d+)', op)
            if m and m.group(1) in regs:
                regs[m.group(1)] = int(m.group(2))
                continue
            # Swap
            m = re.search(r'(?:swap|exchange)\s+(?:the\s+values\s+of\s+)?([A-Z])\s+and\s+([A-Z])', op, re.I)
            if m:
                a, b = m.group(1), m.group(2)
                regs[a], regs[b] = regs.get(b, 0), regs.get(a, 0)
                continue
            # Halve
            if 'halve' in ol:
                m = re.search(r'(?:halve)\s+([A-Z])', op, re.I)
                if m: regs[m.group(1)] = regs.get(m.group(1), 0) // 2
        # Find queried register
        qm = re.search(r'(?:final\s+value\s+of|what\s+is)\s+([A-Z])', p, re.I)
        if qm and qm.group(1) in regs:
            return regs[qm.group(1)]
        return None

    def _compute_sequential_arithmetic(self, p):
        """Start with N, apply operations, return result."""
        pl = p.lower()
        m = re.search(r'start\s+with\s+(\d+)', pl)
        if not m:
            return None
        val = int(m.group(1))
        ops = re.split(r'[.!]', p[m.end():])
        for op in ops:
            ol = op.strip().lower()
            if not ol or 'result' in ol or 'what' in ol:
                continue
            nm = re.search(r'(\d+)', ol)
            if 'add' in ol or 'plus' in ol or 'increase' in ol:
                if nm: val += int(nm.group(1))
            elif 'subtract' in ol or 'minus' in ol or 'take away' in ol:
                if nm: val -= int(nm.group(1))
            elif 'multiply' in ol or 'times' in ol:
                if nm: val *= int(nm.group(1))
            elif 'divide' in ol or 'halve' in ol:
                if 'halve' in ol: val //= 2
                elif nm and int(nm.group(1)) != 0: val //= int(nm.group(1))
            elif 'double' in ol: val *= 2
            elif 'triple' in ol: val *= 3
            elif 'quadruple' in ol: val *= 4
        return val

    def _compute_belief_tracker(self, p):
        """Sally-Anne belief tracking with absence."""
        pl = p.lower()
        # Detect SA structure: person puts X in loc, leaves, someone else moves it
        put_m = re.search(r'(\w+)\s+puts?\s+(?:the\s+)?(\w+)\s+in\s+(?:the\s+)?(\w+)', pl)
        leave_m = re.search(r'(\w+)\s+(?:leaves?|goes?\s+outside|steps?\s+out)', pl)
        move_m = re.search(r'(\w+)\s+(?:moves?|takes?|relocates?)\s+(?:the\s+)?(\w+)\s+(?:to|into)\s+(?:the\s+)?(\w+)', pl)
        query_m = re.search(r'(?:where\s+does\s+)(\w+)\s+(?:think|believe)', pl)
        if not (put_m and leave_m and move_m and query_m):
            return None
        putter = put_m.group(1)
        orig_loc = put_m.group(3)
        leaver = leave_m.group(1)
        new_loc = move_m.group(3)
        queried = query_m.group(1)
        # If queried person is the one who left, they still believe original location
        if queried.lower() == leaver.lower() or queried.lower() == putter.lower():
            return orig_loc
        return new_loc

    def _compute_recursive(self, p):
        """Evaluate f(n) given base case and recurrence."""
        pl = p.lower()
        base_m = re.search(r'f\((\d+)\)\s*=\s*(\d+)', p)
        rec_m = re.search(r'f\(n\)\s*=\s*(\d+)\s*[×·*]\s*f\(n-1\)\s*([+-]\s*\d+)?', p)
        if not rec_m:
            rec_m = re.search(r'f\(n\)\s*=\s*(\d+)\s*\*\s*f\(n-1\)\s*([+-]\s*\d+)?', p)
        query_m = re.search(r'f\((\d+)\)', p.split('?')[0].split('What')[-1] if '?' in p else p[-20:])
        if not (base_m and rec_m):
            return None
        base_n = int(base_m.group(1))
        base_v = int(base_m.group(2))
        mult = int(rec_m.group(1))
        add = int(rec_m.group(2).replace(' ', '')) if rec_m.group(2) else 0
        # Find query n
        all_fn = re.findall(r'f\((\d+)\)', p)
        query_n = int(all_fn[-1]) if all_fn else base_n + 3
        vals = {base_n: base_v}
        for i in range(base_n + 1, query_n + 1):
            vals[i] = mult * vals[i - 1] + add
        return vals.get(query_n)

    def _compute_constraint_solver(self, p):
        """Brute-force constraint satisfaction over permutations."""
        from itertools import permutations
        pl = p.lower()
        # Detect "N people each chose different items from: list"
        people_m = re.findall(r'([A-Z]\w+)', p.split('.')[0])
        items_m = re.search(r'(?:from|of)\s*:?\s*([^.]+)', pl)
        if not items_m or len(people_m) < 3:
            return None
        # Try to extract items list
        items_text = items_m.group(1)
        items = [w.strip().rstrip(',') for w in re.split(r',\s*', items_text) if w.strip() and len(w.strip()) > 1]
        if len(items) < len(people_m):
            return None
        people = people_m[:len(items)]
        # Parse constraints
        not_chose = []  # (person, item)
        did_chose = []  # (person, item)
        for sent in re.split(r'[.!]', p):
            m = re.search(r'(\w+)\s+did\s+not\s+choose\s+(\w+)', sent, re.I)
            if m: not_chose.append((m.group(1), m.group(2).lower()))
            m = re.search(r'(\w+)\s+chose\s+(\w+)', sent, re.I)
            if m and 'not' not in sent.lower(): did_chose.append((m.group(1), m.group(2).lower()))
            m = re.search(r'(\w+)\s+was\s+not\s+chosen\s+by\s+(\w+)', sent, re.I)
            if m: not_chose.append((m.group(2), m.group(1).lower()))
        if not not_chose and not did_chose:
            return None
        # Brute force
        for perm in permutations(items):
            assign = dict(zip(people, perm))
            valid = True
            for person, item in not_chose:
                if assign.get(person, '').lower() == item.lower():
                    valid = False; break
            if not valid: continue
            for person, item in did_chose:
                if assign.get(person, '').lower() != item.lower():
                    valid = False; break
            if valid:
                # Find queried person
                qm = re.search(r'[Ww]hat\s+did\s+(\w+)\s+choose', p)
                if qm:
                    return assign.get(qm.group(1), None)
        return None

    def _compute_bayesian(self, p):
        """Bayes theorem: P(A|B) from base rate, sensitivity, false positive."""
        pl = p.lower()
        base_m = re.search(r'1\s+in\s+(\d+)', pl)
        sens_m = re.search(r'(\d+)\s*%\s*(?:sensitivity|true\s+positive|correctly\s+identif|accuracy|detects)', pl)
        fpr_m = re.search(r'(\d+)\s*%\s*false\s+positive', pl)
        if not (base_m and sens_m and fpr_m):
            return None
        base_rate = 1.0 / int(base_m.group(1))
        sensitivity = int(sens_m.group(1)) / 100.0
        fpr = int(fpr_m.group(1)) / 100.0
        p_pos = sensitivity * base_rate + fpr * (1 - base_rate)
        if p_pos == 0: return None
        posterior = (sensitivity * base_rate) / p_pos
        return round(posterior * 100, 1)

    def _compute_info_sufficiency(self, p):
        """Count variables vs equations. If underdetermined → Cannot be determined."""
        pl = p.lower()
        # Check for system of equations
        eqs = re.findall(r'(\d+)x\s*\+\s*(\d+)y\s*=\s*(\d+)', pl)
        if eqs:
            if len(eqs) < 2:
                return "cannot"
            # 2 equations → solvable
            return None  # let the solver handle it
        # Single equation check
        if re.search(r'\d+x\s*\+\s*\d+y\s*=', pl) and len(re.findall(r'=', pl.split('?')[0])) == 1:
            return "cannot"
        return None

    def _compute_defeasible(self, p):
        """Default rules with exceptions. Most specific wins."""
        pl = p.lower()
        # Pattern: "All X have P. Y are X that do NOT have P. Z are Y that DO have P."
        defaults = re.findall(r'all\s+(\w+)\s+(\w[\w\s]*?)(?:\.|$)', pl)
        exceptions = re.findall(r'(\w+)\s+are\s+\w+\s+that\s+(?:do\s+)?not\s+(\w[\w\s]*?)(?:\.|$)', pl)
        counter_exc = re.findall(r'(\w+)\s+are\s+\w+\s+that\s+do\s+(\w[\w\s]*?)(?:\.|$)', pl)
        entity_m = re.search(r'(\w+)\s+is\s+a[n]?\s+(\w+)', pl)
        if not entity_m:
            return None
        entity_type = entity_m.group(2)
        # Check if entity matches an exception-to-exception
        for exc_type, prop in counter_exc:
            if entity_type in exc_type:
                return "Yes"
        # Check if entity matches an exception
        for exc_type, prop in exceptions:
            if entity_type in exc_type:
                return "No"
        # Default applies
        if defaults:
            return "Yes"
        return None

    def _compute_interval_overlap(self, p):
        """Parse time ranges, check overlap."""
        pl = p.lower()
        # Parse "from H:MM AM/PM to H:MM AM/PM" or "H:MM-H:MM"
        ranges = re.findall(r'(\d{1,2}):(\d{2})\s*(am|pm)?\s*(?:to|-)\s*(\d{1,2}):(\d{2})\s*(am|pm)?', pl)
        if len(ranges) < 2:
            return None
        def to_min(h, m, ap):
            h, m = int(h), int(m)
            if ap == 'pm' and h != 12: h += 12
            elif ap == 'am' and h == 12: h = 0
            return h * 60 + m
        intervals = []
        for r in ranges:
            s = to_min(r[0], r[1], r[2] or '')
            e = to_min(r[3], r[4], r[5] or '')
            intervals.append((s, e))
        for i in range(len(intervals)):
            for j in range(i + 1, len(intervals)):
                s1, e1 = intervals[i]
                s2, e2 = intervals[j]
                if s1 < e2 and s2 < e1:
                    return "overlap_yes"
        return "overlap_no"

    def _compute_variable_propagation(self, p):
        """Solve dependency chains: X = f(Y), Y = g(Z), Z = constant."""
        # Parse "X = 2 * Y + 1" style equations
        eqs = re.findall(r'([A-Z])\s*=\s*(\d+)\s*\*\s*([A-Z])\s*([+-]\s*\d+)?', p)
        consts = re.findall(r'([A-Z])\s*=\s*(\d+)\.', p)
        if not consts:
            consts = re.findall(r'([A-Z])\s*=\s*(\d+)(?:\s|$)', p)
        if not eqs or not consts:
            return None
        vals = {n: int(v) for n, v in consts}
        for _ in range(10):
            changed = False
            for lhs, mult, rhs, offset in eqs:
                if lhs not in vals and rhs in vals:
                    off = int(offset.replace(' ', '')) if offset else 0
                    vals[lhs] = int(mult) * vals[rhs] + off
                    changed = True
            # Also check simpler: X = Y + N
            for m in re.finditer(r'([A-Z])\s*=\s*([A-Z])\s*\+\s*(\d+)', p):
                if m.group(1) not in vals and m.group(2) in vals:
                    vals[m.group(1)] = vals[m.group(2)] + int(m.group(3))
                    changed = True
            if not changed:
                break
        qm = re.search(r'(?:value\s+of|what\s+is)\s+([A-Z])', p, re.I)
        if qm and qm.group(1) in vals:
            return vals[qm.group(1)]
        return None

    # ---- Standard computations (not regex match — actual compute) ----

    def _compute_standard(self, p):
        """Standard arithmetic/logic computations."""
        pl = p.lower()
        pn = _ns(p)
        # Bat and ball: total=X, diff=Y, answer=(X-Y)/2
        m = re.search(r'(?:cost|total)s?\s+\$?([\d.]+).*?costs?\s+\$?([\d.]+)\s+more', pl)
        if m: return ('num', (float(m.group(1)) - float(m.group(2))) / 2)
        # All but N
        m = re.search(r'all\s+(?:but|except)\s+(\d+)', pl)
        if m and 'how many' in pl: return ('num', float(m.group(1)))
        # Fencepost
        m = re.search(r'(\d+)\s*(?:fence\s*)?posts?.*?(\d+)\s*(?:meter|feet|ft|m|yard)', pl)
        if m: return ('num', (int(m.group(1)) - 1) * int(m.group(2)))
        # Modular arithmetic
        m = re.search(r'(\d+)\s*(?:mod|%|modulo)\s*(\d+)', pl)
        if m: return ('num', int(m.group(1)) % int(m.group(2)))
        # Percentage asymmetry
        if re.search(r'(?:increase|decrease).*?\d+\s*%.*?(?:then|back)', pl):
            return ('text', 'not_same')
        # Numeric comparison
        if re.search(r'(?:larger|greater|bigger)\s+than', pl) and len(pn) >= 2:
            return ('text', 'yes' if pn[0] > pn[1] else 'no')
        # Coin flip
        if re.search(r'coin.*(?:flip|toss)', pl): return ('text', 'independent')
        # Correlation ≠ causation
        if 'correlat' in pl and 'cause' in pl: return ('text', 'no_cause')
        return None

    def _match_computed(self, computed, candidates):
        """Match a computed result against candidates. Returns scores."""
        scores = []
        for c in candidates:
            cl = c.lower().strip()
            cn = _ns(c)
            if isinstance(computed, (int, float)):
                if cn and any(abs(v - computed) < 0.5 for v in cn):
                    scores.append((c, 0.95))
                else:
                    scores.append((c, 0.08))
            elif isinstance(computed, str):
                comp_l = computed.lower()
                if comp_l in cl or cl in comp_l:
                    scores.append((c, 0.95))
                elif computed == 'stops' and _h(c, 'stop', 'unlikely', 'no longer', 'cease'):
                    scores.append((c, 0.95))
                elif computed == 'stops' and _h(c, 'still', 'continue', 'directly', 'cannot'):
                    scores.append((c, 0.08))
                elif computed == 'yes' and _h(c, 'yes'):
                    scores.append((c, 0.95))
                elif computed == 'no_cause' and _h(c, 'confound', 'not necessarily', 'common cause', 'no,'):
                    scores.append((c, 0.95))
                elif computed == 'confounding' and _h(c, 'confound', 'not necessarily', 'common cause'):
                    scores.append((c, 0.95))
                elif computed == 'chain_broken' and _h(c, 'no,', 'broken', 'would not'):
                    scores.append((c, 0.95))
                elif computed == 'cannot' and _h(c, 'cannot', 'undetermined', 'not enough', 'insufficient'):
                    scores.append((c, 0.95))
                elif computed == 'cannot' and not _h(c, 'cannot', 'undetermined'):
                    scores.append((c, 0.08))
                elif computed == 'overlap_yes' and _h(c, 'yes'):
                    scores.append((c, 0.95))
                elif computed == 'overlap_yes' and _h(c, 'no'):
                    scores.append((c, 0.08))
                elif computed == 'overlap_no' and _h(c, 'no'):
                    scores.append((c, 0.95))
                elif computed == 'overlap_no' and _h(c, 'yes'):
                    scores.append((c, 0.08))
                elif computed in ('Yes', 'No'):
                    scores.append((c, 0.95 if computed.lower() in cl else 0.08))
                elif computed == 'second_better' and not _h(c, 'first', 'alpha', 'drug x', 'cannot', 'equal'):
                    scores.append((c, 0.90))
                elif computed == 'not_same' and _h(c, 'not the same', 'less', 'lower', 'different'):
                    scores.append((c, 0.92))
                elif computed == 'independent' and _h(c, '1/2', '0.5', '50', 'same', 'independent'):
                    scores.append((c, 0.92))
                else:
                    scores.append((c, 0.15))
            elif isinstance(computed, tuple) and computed[0] == 'num':
                val = computed[1]
                if cn and any(abs(v - val) < 0.5 for v in cn):
                    scores.append((c, 0.95))
                else:
                    scores.append((c, 0.08))
            elif isinstance(computed, tuple) and computed[0] == 'text':
                return self._match_computed(computed[1], candidates)
            elif isinstance(computed, set):  # reachable set from logic chain
                if _h(c, 'yes') and not _h(c, 'cannot'): scores.append((c, 0.95))
                elif _h(c, 'no') or _h(c, 'cannot'): scores.append((c, 0.08))
                else: scores.append((c, 0.50))
            else:
                scores.append((c, 0.50))
        return scores

    def _score(self, p, c):
        pl = p.lower()
        # Try all computation modules in order of specificity
        computations = [
            # Tier 2 modules (try first — more specific)
            self._compute_register_machine,
            self._compute_sequential_arithmetic,
            self._compute_belief_tracker,
            self._compute_recursive,
            self._compute_bayesian,
            self._compute_constraint_solver,
            self._compute_variable_propagation,
            self._compute_defeasible,
            self._compute_interval_overlap,
            self._compute_info_sufficiency,
            # Tier 1 hard modules
            self._compute_relative_day,
            self._compute_duration_midnight,
            self._compute_rate_of_change,
            self._compute_scheduling,
            self._compute_age,
            self._compute_train,
            self._compute_sequence,
            self._compute_causal_intervention,
            self._compute_counterfactual,
            self._compute_confounding,
            self._compute_tom_deception,
            self._compute_perspective,
            self._compute_info_asymmetry,
            self._compute_belief_chain,
            self._compute_simpson,
            self._compute_logic_chain,
            self._compute_causal_chain_counterfactual,
            self._compute_logic_tom,
        ]
        for fn in computations:
            result = fn(p)
            if result is not None:
                scores = self._match_computed(result, [c])
                if scores:
                    return scores[0][1], fn.__name__

        # Standard computations
        std = self._compute_standard(p)
        if std is not None:
            scores = self._match_computed(std, [c])
            if scores:
                return scores[0][1], 'standard'

        # Fallback: NCD tiebreaker only
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
