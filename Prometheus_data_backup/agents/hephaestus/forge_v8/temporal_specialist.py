"""Temporal Specialist — covers temporal_age_reasoning, temporal_causal_ordering,
temporal_concurrent_events, temporal_relative_day.

Computation-first: parses temporal structure into numeric/symbolic representation,
computes answer, matches against candidates. NCD as tiebreaker only.
"""
import re
import zlib
import math

_DAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
_DAY_MAP = {d: i for i, d in enumerate(_DAYS)}
_NUM = re.compile(r'-?\d+(?:\.\d+)?')
_ORDINAL = re.compile(r'(\d+)(?:st|nd|rd|th)')

# Tier B meta-confidence patterns
_PRESUP = re.compile(r'\b(?:have|has)\s+\w+\s+(?:stopped|quit|given\s+up)', re.I)
_SCOPE = re.compile(r'\bevery\b.*\b(?:a|some)\b.*\?', re.I)
_SUNK = re.compile(r'already\s+(?:spent|invested|paid)', re.I)
_DICHOT = re.compile(r'either.*?or|must\s+be\s+one', re.I)
_SURVIVOR = re.compile(r'(?:successful|survivors?).*(?:sample|study)', re.I)


class ReasoningTool:

    def __init__(self):
        pass

    # --- NCD (tiebreaker only, max 15% weight) ---
    def _ncd(self, a, b):
        if not a or not b:
            return 1.0
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + " " + b).encode()))
        d = max(ca, cb)
        return (cab - min(ca, cb)) / d if d else 1.0

    # --- Meta-confidence for Tier B ---
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

    # --- Temporal: relative day computation ---
    def _compute_relative_day(self, prompt):
        pl = prompt.lower()
        m = re.search(r'today\s+is\s+(\w+)', pl)
        if not m:
            return None
        day_name = m.group(1).lower()
        if day_name not in _DAY_MAP:
            return None
        day_idx = _DAY_MAP[day_name]
        rest = pl[m.end():]
        tokens = re.findall(r'(?:day\s+before|day\s+after|yesterday|tomorrow)', rest)
        offset = 0
        for t in tokens:
            if t in ('yesterday', 'day before'):
                offset -= 1
            elif t in ('tomorrow', 'day after'):
                offset += 1
        # Also handle "two days after", "three days before"
        num_shifts = re.findall(r'(\w+)\s+days?\s+(before|after)', rest)
        word_nums = {'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6}
        for w, direction in num_shifts:
            n = word_nums.get(w)
            if n is None:
                try:
                    n = int(w)
                except ValueError:
                    continue
            if direction == 'before':
                offset -= n
            else:
                offset += n
        # Subtract the simple token offsets that were already counted
        # (the "day before"/"day after" in num_shifts overlap with token parse)
        # Actually the num_shifts regex captures "two days before" but not "day before"
        # so no double counting. The "day before" in tokens is distinct from "two days before".
        result = _DAYS[(day_idx + offset) % 7]
        return result.capitalize()

    # --- Temporal: age reasoning ---
    def _compute_age(self, prompt):
        pl = prompt.lower()
        # Extract all named entities and their age relationships
        # Pattern: "X is N years older than Y" => age(X) = age(Y) + N
        # Pattern: "Y is M times as old as Z" / "Y is M times Z's age" => age(Y) = M * age(Z)
        # Pattern: "Z is N" / "Z is N years old" => age(Z) = N
        names_mentioned = set()
        age_facts = {}
        relations = []

        # Direct age: "X is N years old" or "X is N." but NOT "X is N times"
        for m in re.finditer(r'(\w+)\s+is\s+(\d+)(?:\s+years?\s+old)?(?:\.|,|\s)', pl):
            name = m.group(1).capitalize()
            age = int(m.group(2))
            # Don't match if followed by "times" or "years older/younger"
            after = pl[m.end():m.end()+20]
            if re.match(r'\s*times', after):
                continue
            if re.match(r'\s*years?\s+(?:older|younger)', after):
                continue
            age_facts[name] = age
            names_mentioned.add(name)

        # "X is N years older than Y"
        for m in re.finditer(r'(\w+)\s+is\s+(\d+)\s+years?\s+older\s+than\s+(\w+)', pl):
            x = m.group(1).capitalize()
            diff = int(m.group(2))
            y = m.group(3).capitalize()
            relations.append(('older', x, y, diff))
            names_mentioned.update([x, y])

        # "X is N years younger than Y"
        for m in re.finditer(r'(\w+)\s+is\s+(\d+)\s+years?\s+younger\s+than\s+(\w+)', pl):
            x = m.group(1).capitalize()
            diff = int(m.group(2))
            y = m.group(3).capitalize()
            relations.append(('younger', x, y, diff))
            names_mentioned.update([x, y])

        # "Y is M times as old as Z" / "Y is M times Z's age"
        for m in re.finditer(r'(\w+)\s+is\s+(\d+)\s+times?\s+(?:as\s+old\s+as\s+)?(\w+)', pl):
            y = m.group(1).capitalize()
            mult = int(m.group(2))
            z = m.group(3).capitalize()
            relations.append(('times', y, z, mult))
            names_mentioned.update([y, z])

        # Resolve ages iteratively
        for _ in range(10):
            for rel_type, a, b, val in relations:
                if rel_type == 'older' and b in age_facts and a not in age_facts:
                    age_facts[a] = age_facts[b] + val
                elif rel_type == 'older' and a in age_facts and b not in age_facts:
                    age_facts[b] = age_facts[a] - val
                elif rel_type == 'younger' and b in age_facts and a not in age_facts:
                    age_facts[a] = age_facts[b] - val
                elif rel_type == 'younger' and a in age_facts and b not in age_facts:
                    age_facts[b] = age_facts[a] + val
                elif rel_type == 'times' and b in age_facts and a not in age_facts:
                    age_facts[a] = age_facts[b] * val
                elif rel_type == 'times' and a in age_facts and b not in age_facts:
                    age_facts[b] = age_facts[a] // val

        # Find what's being asked: "How old is X?" or "What is X's age?"
        asked = re.search(r'how\s+old\s+is\s+(\w+)', pl)
        if not asked:
            asked = re.search(r"what\s+is\s+(\w+)'s\s+age", pl)
        if asked:
            target = asked.group(1).capitalize()
            if target in age_facts:
                return str(age_facts[target])
        return None

    # --- Temporal: concurrent events ---
    def _compute_concurrent(self, prompt):
        pl = prompt.lower()
        # Extract "X takes N minutes" patterns
        tasks = re.findall(r'(\w[\w\s]*?)\s+takes?\s+(\d+)\s+minutes?', pl)
        if not tasks:
            return None
        min_dur = None
        fastest = None
        for name, dur_str in tasks:
            dur = int(dur_str)
            if min_dur is None or dur < min_dur:
                min_dur = dur
                fastest = name.strip()
        if fastest and min_dur is not None:
            return f"{fastest.capitalize()} after {min_dur} minutes"
        return None

    # --- Temporal: causal ordering ---
    def _compute_causal_order(self, prompt):
        pl = prompt.lower()

        # Method 1: "event at/on Day N" pattern — extract events with day numbers
        day_events = re.findall(r'(?:the\s+)?(\w[\w\s]*?)\s+(?:at|on|was\s+(?:made|reported|deployed|done)\s+(?:at|on))\s+day\s+(\d+)', pl)
        if not day_events:
            # Try alternate patterns: "X began on Day N", "X was made on Day N"
            day_events = re.findall(r'(\w[\w\s]*?)\s+(?:began|started|occurred|happened|was\s+\w+)\s+(?:at|on)\s+day\s+(\d+)', pl)

        if day_events:
            # Sort by day number and find earliest/latest
            events_with_days = [(name.strip(), int(d)) for name, d in day_events]
            events_with_days.sort(key=lambda x: x[1])

            # Check what's being asked
            if re.search(r'earliest|first|came\s+first', pl):
                earliest_name = events_with_days[0][0]
                return earliest_name
            elif re.search(r'latest|last|most\s+recent', pl):
                return events_with_days[-1][0]
            else:
                # Return chronological order
                return ", ".join(name for name, _ in events_with_days)

        # Method 2: "X happened before Y" / "Y occurred after X"
        befores = []
        for m in re.finditer(r'(\w+)\s+(?:happened|occurred|came)\s+before\s+(\w+)', pl):
            befores.append((m.group(1).capitalize(), m.group(2).capitalize()))
        for m in re.finditer(r'(\w+)\s+preceded\s+(\w+)', pl):
            befores.append((m.group(1).capitalize(), m.group(2).capitalize()))
        for m in re.finditer(r'(\w+)\s+(?:happened|occurred|came)\s+after\s+(\w+)', pl):
            befores.append((m.group(2).capitalize(), m.group(1).capitalize()))

        if not befores:
            for m in re.finditer(r'(\w[\w\s]*?)\s+(?:causes?|leads?\s+to|results?\s+in)\s+(\w[\w\s]*?)(?:\.|,|;)', pl):
                befores.append((m.group(1).strip().capitalize(), m.group(2).strip().capitalize()))

        if not befores:
            return None

        from collections import defaultdict
        graph = defaultdict(set)
        all_nodes = set()
        for a, b in befores:
            graph[a].add(b)
            all_nodes.update([a, b])

        order = []
        visited = set()
        def visit(node):
            if node in visited:
                return
            visited.add(node)
            for a, b in befores:
                if b == node and a not in visited:
                    visit(a)
            order.append(node)
        for node in all_nodes:
            visit(node)
        if order:
            return ", ".join(order)
        return None

    # --- Main scoring ---
    def _compute_answer(self, prompt):
        # Try each computation module
        result = self._compute_relative_day(prompt)
        if result:
            return result, 0.85

        result = self._compute_age(prompt)
        if result:
            return result, 0.85

        result = self._compute_concurrent(prompt)
        if result:
            return result, 0.80

        result = self._compute_causal_order(prompt)
        if result:
            return result, 0.70

        return None, 0.0

    def evaluate(self, prompt, candidates):
        meta = self._meta_confidence(prompt)
        computed, comp_conf = self._compute_answer(prompt)

        results = []
        for cand in candidates:
            # Structural match score
            struct_score = 0.0
            if computed is not None:
                cl = cand.lower().strip()
                rl = computed.lower().strip()
                if cl == rl:
                    struct_score = 1.0
                elif rl in cl or cl in rl:
                    struct_score = 0.7
                else:
                    # Check if numeric answer matches
                    cand_nums = [float(x) for x in _NUM.findall(cand)]
                    result_nums = [float(x) for x in _NUM.findall(computed)]
                    if cand_nums and result_nums and cand_nums == result_nums:
                        struct_score = 0.9

            # NCD tiebreaker (max 15%)
            ncd_val = self._ncd(prompt, cand)
            ncd_score = (1.0 / (1.0 + ncd_val)) * 0.15

            # Combined score
            score = struct_score * 0.85 + ncd_score
            score *= meta

            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"struct={struct_score:.2f} ncd_tb={ncd_score:.3f} meta={meta:.2f}"
            })

        results.sort(key=lambda r: r["score"], reverse=True)
        return results

    def confidence(self, prompt, answer):
        meta = self._meta_confidence(prompt)
        if meta < 1.0:
            return meta

        computed, comp_conf = self._compute_answer(prompt)
        if computed is None:
            return 0.25  # honest uncertainty

        al = answer.lower().strip()
        cl = computed.lower().strip()
        if cl == al or cl in al or al in cl:
            return min(comp_conf, meta)

        # Check numeric match
        a_nums = [float(x) for x in _NUM.findall(answer)]
        c_nums = [float(x) for x in _NUM.findall(computed)]
        if a_nums and c_nums and a_nums == c_nums:
            return min(comp_conf * 0.9, meta)

        return 0.20
