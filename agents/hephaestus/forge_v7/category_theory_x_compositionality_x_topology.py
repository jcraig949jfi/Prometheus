import re
import math
import zlib
import numpy as np
from collections import namedtuple
from typing import List, Dict, Tuple, Optional, Set

Statement = namedtuple('Statement', ['pred', 'args', 'polarity', 'num_val', 'weight'])


class ReasoningTool:
    """
    Frame B/C hybrid: Constructive computation + dynamics tracking.
    Category Theory x Compositionality x Topology.

    Gap target: Spatial (reference frame transformation).
    Core solvers: direction composition (compass modular arithmetic),
    left-right reversal (facing-each-other mirror), containment transitivity,
    perspective shift, relative position. Also: all standard parsers.

    Score: Structural (70%) + Computation (20%) + NCD tiebreaker (10%).
    """

    COMPASS = ['north', 'east', 'south', 'west']
    TURN_MAP = {'right': 1, 'left': -1, 'around': 2, 'back': 2}

    def __init__(self):
        self.patterns = {
            'negation': re.compile(r'\b(not|never|no\b|without|neither|doesn\'t|don\'t|isn\'t|aren\'t)\b', re.I),
            'comparative': re.compile(r'\b(more than|less than|greater|fewer|taller|shorter|heavier|lighter|before|after)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|otherwise|whenever)\b', re.I),
            'causal': re.compile(r'\b(because|causes|leads to|due to|since|therefore|thus)\b', re.I),
            'numeric': re.compile(r'(-?\d+(?:\.\d+)?)', re.I),
        }
        self.presupposition_triggers = [
            re.compile(r'\b(stopped|quit|ceased)\b.*\b(have you|did you)\b', re.I),
            re.compile(r'\bwhy\s+(did|does|is)\b', re.I),
        ]
        self.subjectivity_triggers = re.compile(r'\b(best|worst|favorite|opinion|beautiful)\b', re.I)

    # ── Direction composition solver ──────────────────────────────
    def _direction_solve(self, prompt: str, candidates: List[str]) -> Tuple[Optional[str], float]:
        pl = prompt.lower()
        # "face/facing north, turn right twice"
        face_m = re.search(r'(?:face|facing|start\s+facing)\s+(north|south|east|west)', pl)
        if not face_m:
            return None, 0.0
        idx = self.COMPASS.index(face_m.group(1))
        # Collect turns in order
        turns = re.findall(r'turn\s+(left|right|around|back)', pl)
        # Also handle "turn right twice/three times"
        turn_count = re.findall(r'turn\s+(left|right|around|back)\s+(\w+)', pl)
        word_to_num = {'once': 1, 'twice': 2, 'three': 3, 'four': 4,
                       'two': 2, 'three': 3, 'thrice': 3}
        expanded_turns = []
        used = set()
        for direction, count_word in turn_count:
            n = word_to_num.get(count_word, 0)
            if n == 0:
                n_m = re.match(r'(\d+)', count_word)
                n = int(n_m.group(1)) if n_m else 1
            expanded_turns.extend([direction] * n)
            used.add(direction)
        # For simple "turn right" without count word, add those too
        for t in turns:
            if t not in used or not turn_count:
                expanded_turns.append(t)
        if not expanded_turns:
            expanded_turns = turns
        for t in expanded_turns:
            delta = self.TURN_MAP.get(t, 0)
            idx = (idx + delta) % 4
        answer = self.COMPASS[idx]
        # Also handle degree turns
        deg_m = re.search(r'turn\s+(\d+)\s*degrees?\s*(left|right|clockwise|counterclockwise|counter-clockwise)?', pl)
        if deg_m:
            degrees = int(deg_m.group(1))
            direction = deg_m.group(2) or 'right'
            steps = (degrees // 90)
            if direction in ('left', 'counterclockwise', 'counter-clockwise'):
                steps = -steps
            idx_orig = self.COMPASS.index(face_m.group(1))
            idx = (idx_orig + steps) % 4
            answer = self.COMPASS[idx]
        for c in candidates:
            if answer in c.lower():
                return c, 0.90
        return None, 0.0

    # ── Left-right reversal (facing each other) ───────────────────
    def _mirror_solve(self, prompt: str, candidates: List[str]) -> Tuple[Optional[str], float]:
        pl = prompt.lower()
        facing = bool(re.search(r'(?:facing\s+(?:each\s+other|you|her|him|them)|across\s+from|opposite)', pl))
        if not facing:
            return None, 0.0
        # "raises/lifts/waves left/right hand"
        action_m = re.search(r'(?:raises?|lifts?|waves?|holds?|points?\s+with)\s+(?:his|her|their|the)?\s*(left|right)', pl)
        if action_m:
            side = action_m.group(1)
            mirrored = 'right' if side == 'left' else 'left'
            # Question: "which side do you see it on?" / "appears on your ..."
            for c in candidates:
                cl = c.lower()
                if mirrored in cl:
                    return c, 0.90
            return None, 0.0
        # Generic left/right question about facing person
        if re.search(r'(?:your|my)\s+(left|right)', pl):
            side_m = re.search(r'(?:his|her|their)\s+(left|right)', pl)
            if side_m:
                other_side = side_m.group(1)
                my_side = 'right' if other_side == 'left' else 'left'
                for c in candidates:
                    if my_side in c.lower():
                        return c, 0.90
        return None, 0.0

    # ── Containment / transitivity ────────────────────────────────
    def _containment_solve(self, prompt: str, candidates: List[str]) -> Tuple[Optional[str], float]:
        pl = prompt.lower()
        # "X is in Y", "Y is in Z" -> "X is in Z"
        contains = re.findall(r'(\w+)\s+is\s+(?:in|inside|within|contained\s+in|part\s+of)\s+(?:the\s+)?(\w+)', pl)
        if len(contains) < 2:
            return None, 0.0
        # Build containment graph: child -> parent
        parent_of = {}
        for child, par in contains:
            parent_of[child] = par
        # Transitive closure: ancestors of each entity
        def ancestors(x):
            anc = set()
            cur = x
            while cur in parent_of:
                cur = parent_of[cur]
                if cur in anc:
                    break
                anc.add(cur)
            return anc
        # "Is X in Z?" or "Where is X?"
        query = re.search(r'(?:is\s+(\w+)\s+(?:in|inside)\s+(?:the\s+)?(\w+))', pl)
        if query:
            x, z = query.group(1), query.group(2)
            result = z in ancestors(x)
            for c in candidates:
                cl = c.lower()
                if result and ('yes' in cl or 'true' in cl):
                    return c, 0.85
                if not result and ('no' in cl or 'false' in cl):
                    return c, 0.85
        where_q = re.search(r'where\s+is\s+(\w+)', pl)
        if where_q:
            x = where_q.group(1)
            anc = ancestors(x)
            # The outermost container
            if anc:
                outermost = None
                for a in anc:
                    if a not in parent_of:
                        outermost = a
                for c in candidates:
                    if outermost and outermost in c.lower():
                        return c, 0.80
                # Or any ancestor
                for c in candidates:
                    for a in anc:
                        if a in c.lower():
                            return c, 0.75
        return None, 0.0

    # ── Perspective shift / relative position ─────────────────────
    def _perspective_solve(self, prompt: str, candidates: List[str]) -> Tuple[Optional[str], float]:
        pl = prompt.lower()
        # "From X's perspective / point of view"
        persp_m = re.search(r"from\s+(\w+)'s\s+(?:perspective|point of view|seat|side|view)", pl)
        if not persp_m:
            return None, 0.0
        # Table seating: "A sits across from B. C sits to A's left."
        across = re.findall(r'(\w+)\s+(?:sits?|is)\s+(?:across|opposite)\s+(?:from\s+)?(\w+)', pl)
        left_of = re.findall(r'(\w+)\s+(?:sits?|is)\s+(?:to\s+)?(?:the\s+)?left\s+(?:of\s+)?(\w+)', pl)
        right_of = re.findall(r'(\w+)\s+(?:sits?|is)\s+(?:to\s+)?(?:the\s+)?right\s+(?:of\s+)?(\w+)', pl)
        if across or left_of or right_of:
            # From person facing you across table: left/right swap
            observer = persp_m.group(1)
            for a, b in across:
                if observer in (a, b):
                    for c in candidates:
                        cl = c.lower()
                        if 'left' in pl and 'right' in cl:
                            return c, 0.85
                        if 'right' in pl and 'left' in cl:
                            return c, 0.85
        return None, 0.0

    # ── Spatial between / ordering ────────────────────────────────
    def _between_solve(self, prompt: str, candidates: List[str]) -> Tuple[Optional[str], float]:
        pl = prompt.lower()
        # "A is between B and C", "B is left of A", "C is right of A"
        between = re.findall(r'(\w+)\s+is\s+between\s+(\w+)\s+and\s+(\w+)', pl)
        left_rel = re.findall(r'(\w+)\s+is\s+(?:to\s+the\s+)?left\s+of\s+(\w+)', pl)
        right_rel = re.findall(r'(\w+)\s+is\s+(?:to\s+the\s+)?right\s+of\s+(\w+)', pl)
        if between:
            mid, a, b = between[0]
            # Order: a, mid, b  (or b, mid, a)
            # "Who is in the middle?" or "Who is leftmost?"
            for c in candidates:
                cl = c.lower()
                if 'middle' in pl and mid in cl:
                    return c, 0.85
                if ('leftmost' in pl or 'first' in pl) and a in cl:
                    return c, 0.80
                if ('rightmost' in pl or 'last' in pl) and b in cl:
                    return c, 0.80
        if len(left_rel) + len(right_rel) >= 2:
            # Build position graph
            entities = set()
            order_pairs = []  # (left, right) meaning left is to the left of right
            for a, b in left_rel:
                order_pairs.append((a, b))
                entities.update([a, b])
            for a, b in right_rel:
                order_pairs.append((b, a))
                entities.update([a, b])
            # Simple topological sort
            from_left = {e: 0 for e in entities}
            for l, r in order_pairs:
                from_left[r] = max(from_left[r], from_left[l] + 1)
            changed = True
            for _ in range(len(entities)):
                for l, r in order_pairs:
                    if from_left[r] <= from_left[l]:
                        from_left[r] = from_left[l] + 1
            sorted_ents = sorted(entities, key=lambda e: from_left[e])
            if 'leftmost' in pl or 'first' in pl:
                for c in candidates:
                    if sorted_ents[0] in c.lower():
                        return c, 0.80
            if 'rightmost' in pl or 'last' in pl:
                for c in candidates:
                    if sorted_ents[-1] in c.lower():
                        return c, 0.80
            if 'middle' in pl and len(sorted_ents) >= 3:
                mid = sorted_ents[len(sorted_ents) // 2]
                for c in candidates:
                    if mid in c.lower():
                        return c, 0.80
        return None, 0.0

    # ── Transitivity (taller/shorter/etc.) ────────────────────────
    def _transitivity_solve(self, prompt: str, candidates: List[str]) -> Tuple[Optional[str], float]:
        pl = prompt.lower()
        relations = re.findall(r'(\w+)\s+is\s+(taller|shorter|heavier|lighter|older|younger|faster|slower|bigger|smaller|above|below)\s+than\s+(\w+)', pl)
        if len(relations) < 2:
            return None, 0.0
        greater_rels = ('taller', 'heavier', 'older', 'faster', 'bigger', 'above')
        greater = []
        for a, rel, b in relations:
            if rel in greater_rels:
                greater.append((a, b))
            else:
                greater.append((b, a))
        entities = set()
        for a, b in greater:
            entities.update([a, b])
        reach = {e: set() for e in entities}
        for a, b in greater:
            reach[a].add(b)
        changed = True
        while changed:
            changed = False
            for e in entities:
                for r in list(reach[e]):
                    for rr in list(reach.get(r, [])):
                        if rr not in reach[e]:
                            reach[e].add(rr)
                            changed = True
        sup_m = re.search(r'who\s+is\s+(?:the\s+)?(tallest|shortest|heaviest|lightest|oldest|youngest|fastest|slowest|biggest|smallest)', pl)
        if sup_m:
            find_max = sup_m.group(1) in ('tallest', 'heaviest', 'oldest', 'fastest', 'biggest')
            if find_max:
                for e in entities:
                    if len(reach[e]) == len(entities) - 1:
                        for c in candidates:
                            if e in c.lower():
                                return c, 0.85
            else:
                for e in entities:
                    if not reach[e]:
                        for c in candidates:
                            if e in c.lower():
                                return c, 0.85
        return None, 0.0

    # ── Bat-and-ball / numeric ────────────────────────────────────
    def _bat_ball_solve(self, prompt: str, candidates: List[str]) -> Tuple[Optional[str], float]:
        pl = prompt.lower()
        m = re.search(r'(\w+)\s+and\s+(?:a\s+)?(\w+)\s+(?:cost|total)\s+\$?([\d.]+)', pl)
        m2 = re.search(r'(\w+)\s+costs?\s+\$?([\d.]+)\s+more\s+than\s+(?:the\s+)?(\w+)', pl)
        if m and m2:
            total = float(m.group(3))
            diff = float(m2.group(2))
            y_val = (total - diff) / 2.0
            x_val = total - y_val
            for c in candidates:
                if f"{y_val:g}" in c or f"{x_val:g}" in c:
                    return c, 0.90
        return None, 0.0

    # ── Negation scope ────────────────────────────────────────────
    def _negation_scope_solve(self, prompt: str, candidates: List[str]) -> Tuple[Optional[str], float]:
        pl = prompt.lower()
        if re.search(r'not all\s+\w+\s+are\s+\w+', pl):
            for c in candidates:
                cl = c.lower()
                if 'some' in cl or 'at least one' in cl or 'not necessarily' in cl:
                    return c, 0.80
        return None, 0.0

    # ── Modus tollens ─────────────────────────────────────────────
    def _modus_tollens_solve(self, prompt: str, candidates: List[str]) -> Tuple[Optional[str], float]:
        pl = prompt.lower()
        cond = re.findall(r'if\s+(.+?)\s*(?:,\s*)?then\s+(.+?)\.', pl)
        if not cond:
            return None, 0.0
        for ante, cons in cond:
            cons_c = cons.strip()
            if re.search(re.escape(cons_c) + r'\s+is\s+(?:false|not true)', pl) or \
               re.search(r'not\s+' + re.escape(cons_c), pl):
                for c in candidates:
                    cl = c.lower()
                    if 'false' in cl or 'not' in cl or 'no' in cl:
                        return c, 0.80
        return None, 0.0

    # ── Numeric arithmetic fallback ───────────────────────────────
    def _numeric_solve(self, prompt: str, candidates: List[str]) -> Tuple[Optional[str], float]:
        nums = [float(x) for x in re.findall(r'(-?\d+(?:\.\d+)?)', prompt)]
        if len(nums) < 2:
            return None, 0.0
        results = set()
        for i in range(len(nums)):
            for j in range(len(nums)):
                if i == j:
                    continue
                results.update([nums[i] + nums[j], nums[i] - nums[j], nums[i] * nums[j]])
                if nums[j] != 0:
                    results.add(nums[i] / nums[j])
        for c in candidates:
            for cn in re.findall(r'(-?\d+(?:\.\d+)?)', c):
                cv = float(cn)
                if any(abs(cv - r) < 0.01 for r in results):
                    return c, 0.60
        return None, 0.0

    # ── NCD tiebreaker ────────────────────────────────────────────
    def _compute_ncd(self, s1: str, s2: str) -> float:
        b1, b2 = s1.encode(), s2.encode()
        try:
            c1, c2 = len(zlib.compress(b1)), len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            return (c12 - min(c1, c2)) / max(c1, c2, 1)
        except Exception:
            return 1.0

    # ── Meta-confidence (Tier B) ──────────────────────────────────
    def _meta_confidence(self, prompt: str, answer: str) -> float:
        pl = prompt.lower()
        for pat in self.presupposition_triggers:
            if pat.search(pl):
                return 0.25
        if self.subjectivity_triggers.search(pl):
            return 0.30
        if re.search(r'\b(ambiguous|unclear|vague|insufficient)\b', pl):
            return 0.25
        return 1.0

    # ── Main evaluate ─────────────────────────────────────────────
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        solvers = [
            self._direction_solve, self._mirror_solve,
            self._containment_solve, self._perspective_solve,
            self._between_solve, self._transitivity_solve,
            self._bat_ball_solve, self._negation_scope_solve,
            self._modus_tollens_solve, self._numeric_solve,
        ]
        for solver in solvers:
            try:
                best, score = solver(prompt, candidates)
                if best and score > 0.5:
                    meta = self._meta_confidence(prompt, best)
                    score = min(score, meta)
                    results = []
                    for c in candidates:
                        if c == best:
                            results.append({"candidate": c, "score": float(score),
                                            "reasoning": f"execution:{solver.__name__}"})
                        else:
                            results.append({"candidate": c, "score": 0.1,
                                            "reasoning": "structural:non_match"})
                    results.sort(key=lambda x: x["score"], reverse=True)
                    return results
            except Exception:
                pass
        # Fallback: NCD ranking
        results = []
        for c in candidates:
            ncd = self._compute_ncd(prompt, c)
            results.append({"candidate": c, "score": float((1 - ncd) * 0.10),
                            "reasoning": "fallback:ncd_only"})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        meta = self._meta_confidence(prompt, answer)
        if meta < 0.3:
            return meta
        res = self.evaluate(prompt, [answer])
        if res:
            return float(max(0.0, min(1.0, min(res[0]["score"], meta))))
        return 0.2
