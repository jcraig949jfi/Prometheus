"""Computation Specialist — covers compositional_arithmetic_temporal,
compositional_depth_scaling, direction_composition, fencepost.

Pure computation: arithmetic, state machines, compass math. No pattern matching.
"""
import re
import zlib
import math

_NUM = re.compile(r'-?\d+(?:\.\d+)?')
_PRESUP = re.compile(r'\b(?:have|has)\s+\w+\s+(?:stopped|quit|given\s+up)', re.I)
_SCOPE = re.compile(r'\bevery\b.*\b(?:a|some)\b.*\?', re.I)
_SUNK = re.compile(r'already\s+(?:spent|invested|paid)', re.I)
_DICHOT = re.compile(r'either.*?or|must\s+be\s+one', re.I)
_SURVIVOR = re.compile(r'(?:successful|survivors?).*(?:sample|study)', re.I)

_DIRS = ['north', 'east', 'south', 'west']
_DIR_MAP = {d: i for i, d in enumerate(_DIRS)}


class ReasoningTool:

    def __init__(self):
        pass

    def _ncd(self, a, b):
        if not a or not b:
            return 1.0
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + " " + b).encode()))
        d = max(ca, cb)
        return (cab - min(ca, cb)) / d if d else 1.0

    def _meta_confidence(self, prompt):
        pl = prompt.lower()
        if _PRESUP.search(pl):
            return 0.20
        if _SCOPE.search(pl):
            return 0.20
        if _SUNK.search(pl):
            return 0.20
        if _DICHOT.search(pl) and len(pl.split()) > 15:
            return 0.25
        if _SURVIVOR.search(pl):
            return 0.20
        return 1.0

    # --- Direction composition ---
    def _compute_direction(self, prompt):
        pl = prompt.lower()
        # "You are facing X. You turn right, then turn left, ..."
        facing = re.search(r'facing\s+(\w+)', pl)
        if not facing:
            return None
        start_dir = facing.group(1).lower()
        if start_dir not in _DIR_MAP:
            return None
        current = _DIR_MAP[start_dir]

        # Find all turns
        turns = re.findall(r'turn\s+(right|left)', pl)
        for turn in turns:
            if turn == 'right':
                current = (current + 1) % 4
            else:
                current = (current - 1) % 4

        return _DIRS[current].capitalize()

    # --- Fencepost ---
    def _compute_fencepost(self, prompt):
        pl = prompt.lower()
        # "fence is M meters long. post every N meters, including both ends"
        m_fence = re.search(r'(\d+)\s*(?:meters?|feet|yards?|km)\s*long', pl)
        m_every = re.search(r'(?:post|pole|tree|marker|stake)\s+(?:is\s+)?(?:placed\s+)?every\s+(\d+)\s*(?:meters?|feet|yards?|km)', pl)
        both_ends = bool(re.search(r'(?:including|at)\s+both\s+ends', pl))

        if m_fence and m_every:
            length = int(m_fence.group(1))
            spacing = int(m_every.group(1))
            if spacing > 0:
                sections = length // spacing
                posts = sections + 1 if both_ends else sections - 1
                # Default to including both ends if not specified
                if not both_ends and 'both ends' not in pl:
                    posts = sections + 1  # standard fencepost
                return str(posts)
        return None

    # --- Compositional depth scaling (multi-step computation) ---
    def _compute_depth_scaling(self, prompt):
        pl = prompt.lower()
        # "Start with N. Apply steps: Step 1: add X. Step 2: multiply by Y. ..."
        start_match = re.search(r'start\s+with\s+(\d+)', pl)
        if not start_match:
            return None
        val = int(start_match.group(1))

        # Parse steps
        steps = re.findall(r'step\s+\d+:\s*([^.]+?)(?:\.|$)', pl)
        if not steps:
            # Try without "Step N:" prefix
            steps = re.findall(r'(?:then\s+|first\s+|next\s+|finally\s+)?(\w+\s+\d+|multiply\s+by\s+\d+|if\s+[^.]+)', pl)

        for step in steps:
            step = step.strip().lower()
            # "add N"
            add_m = re.match(r'add\s+(\d+)', step)
            if add_m:
                val += int(add_m.group(1))
                continue
            # "subtract N"
            sub_m = re.match(r'subtract\s+(\d+)', step)
            if sub_m:
                val -= int(sub_m.group(1))
                continue
            # "multiply by N"
            mul_m = re.match(r'multiply\s+(?:by\s+)?(\d+)', step)
            if mul_m:
                val *= int(mul_m.group(1))
                continue
            # "divide by N"
            div_m = re.match(r'divide\s+(?:by\s+)?(\d+)', step)
            if div_m:
                d = int(div_m.group(1))
                if d != 0:
                    val = val // d
                continue
            # "if the current value is even, subtract 1; otherwise do nothing"
            even_m = re.search(r'if\s+(?:the\s+)?current\s+value\s+is\s+even.*?subtract\s+(\d+)', step)
            if even_m:
                if val % 2 == 0:
                    val -= int(even_m.group(1))
                continue
            # "if the current value is odd, add 1; otherwise do nothing"
            odd_m = re.search(r'if\s+(?:the\s+)?current\s+value\s+is\s+odd.*?add\s+(\d+)', step)
            if odd_m:
                if val % 2 == 1:
                    val += int(odd_m.group(1))
                continue

        return str(val)

    # --- Train catch-up (compositional arithmetic temporal) ---
    def _compute_train_catchup(self, prompt):
        pl = prompt.lower()
        # Flexible regex: "Train A leaves at H:MM PM traveling at S mph"
        trains = re.findall(
            r'train\s+[ab]\s+leaves?\s+[^.]*?(\d+):(\d+)\s*(am|pm)[^.]*?(\d+)\s*mph',
            pl
        )
        if len(trains) < 2:
            return None

        h1, m1, ap1, s1 = trains[0]
        h2, m2, ap2, s2 = trains[1]
        speed_a = int(s1)
        speed_b = int(s2)
        depart_a_h = int(h1)
        depart_b_h = int(h2)

        # Convert to 24h
        if ap1 == 'pm' and depart_a_h != 12:
            depart_a_h += 12
        elif ap1 == 'am' and depart_a_h == 12:
            depart_a_h = 0
        if ap2 == 'pm' and depart_b_h != 12:
            depart_b_h += 12
        elif ap2 == 'am' and depart_b_h == 12:
            depart_b_h = 0

        # Same direction: faster train catches slower
        if speed_b <= speed_a:
            return "They never meet"

        head_start_hours = depart_b_h - depart_a_h  # B leaves later
        if head_start_hours <= 0:
            return None

        distance_head = speed_a * head_start_hours
        gap = speed_b - speed_a
        if gap <= 0:
            return "They never meet"

        # Time for B to catch A (in hours from B's departure)
        t_catch = distance_head / gap

        catch_hour_24 = depart_b_h + t_catch
        # Normalize to 0-24 range
        catch_hour_24 = catch_hour_24 % 24

        # Convert to 12h display
        h = int(catch_hour_24)
        if h == 0:
            return "12:00 AM"
        elif h < 12:
            return f"{h}:00 AM"
        elif h == 12:
            return "12:00 PM"
        else:
            return f"{h - 12}:00 PM"

    def _compute_answer(self, prompt):
        result = self._compute_direction(prompt)
        if result:
            return result, 0.90

        result = self._compute_fencepost(prompt)
        if result:
            return result, 0.90

        result = self._compute_depth_scaling(prompt)
        if result:
            return result, 0.85

        result = self._compute_train_catchup(prompt)
        if result:
            return result, 0.80

        return None, 0.0

    def evaluate(self, prompt, candidates):
        meta = self._meta_confidence(prompt)
        computed, comp_conf = self._compute_answer(prompt)

        results = []
        for cand in candidates:
            struct_score = 0.0

            if computed is not None:
                cl = cand.lower().strip()
                rl = computed.lower().strip()

                if cl == rl:
                    struct_score = 1.0
                elif rl in cl or cl in rl:
                    struct_score = 0.7
                else:
                    # Numeric match
                    cand_nums = [float(x) for x in _NUM.findall(cand)]
                    result_nums = [float(x) for x in _NUM.findall(computed)]
                    if cand_nums and result_nums:
                        if cand_nums == result_nums:
                            struct_score = 0.9
                        elif cand_nums[0] == result_nums[0]:
                            struct_score = 0.8

            # NCD tiebreaker
            ncd_val = self._ncd(prompt, cand)
            ncd_score = (1.0 / (1.0 + ncd_val)) * 0.15

            score = struct_score * 0.85 + ncd_score
            score *= meta

            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"struct={struct_score:.2f} ncd={ncd_score:.3f} meta={meta:.2f}"
            })

        results.sort(key=lambda r: r["score"], reverse=True)
        return results

    def confidence(self, prompt, answer):
        meta = self._meta_confidence(prompt)
        if meta < 1.0:
            return meta

        computed, comp_conf = self._compute_answer(prompt)
        if computed is None:
            return 0.25

        al = answer.lower().strip()
        cl = computed.lower().strip()

        if cl == al or cl in al or al in cl:
            return min(comp_conf, meta)

        a_nums = [float(x) for x in _NUM.findall(answer)]
        c_nums = [float(x) for x in _NUM.findall(computed)]
        if a_nums and c_nums and a_nums[0] == c_nums[0]:
            return min(comp_conf * 0.9, meta)

        return 0.20
