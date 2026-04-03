"""T2 Temporal Complex Solver — targets temporal scheduling, rate of change,
temporal complex (timezone), compositional multi-step, plus standard T1 traps.

Strategy: Parse durations, dependencies, rates, timezone offsets. Build
timelines, compute critical paths, solve rate equations.
"""

import sys
import re
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "agents" / "hephaestus" / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from _t1_parsers import try_standard, DAYS
from forge_primitives_t2 import temporal_reason, self_critique


class ReasoningTool:

    def _make_result(self, idx, candidates):
        out = []
        for i, c in enumerate(candidates):
            out.append({"candidate": c, "score": 1.0 if i == idx else 0.0})
        return sorted(out, key=lambda x: x["score"], reverse=True)

    def _try_scheduling(self, prompt, candidates):
        p = prompt.lower()
        if 'task' not in p or 'minimum' not in p: return None
        tasks = re.findall(r'task\s+(\w)\s+takes\s+(\d+)h', p)
        if not tasks: return None
        durations = {l.upper(): int(d) for l, d in tasks}
        deps = {l: [] for l in durations}
        for label in durations:
            dep_m = re.search(r'task\s+' + label + r'\s+takes\s+\d+h\s*\(requires?\s+(.+?)\s+to\s+finish', p, re.IGNORECASE)
            if dep_m:
                deps[label] = [d for d in re.findall(r'([A-Z])', dep_m.group(1).upper()) if d in durations]
        earliest = {}; computed = set()
        for _ in range(len(durations) + 1):
            for lbl in durations:
                if lbl in computed: continue
                if all(d in computed for d in deps.get(lbl, [])):
                    earliest[lbl] = max((earliest[d] + durations[d] for d in deps.get(lbl, [])), default=0)
                    computed.add(lbl)
        if not earliest: return None
        min_time = max(earliest[l] + durations[l] for l in durations if l in earliest)
        for i, c in enumerate(candidates):
            if c.strip() == f"{min_time}h": return i, 0.9
        return None

    def _try_rate(self, prompt, candidates):
        p = prompt.lower()
        fill_m = re.search(r'fills?\s+(?:at\s+)?(\d+)\s*(?:l|liter).*?(?:/|\s*per\s*)min', p)
        drain_m = re.search(r'drains?\s+(?:at\s+)?(\d+)\s*(?:l|liter).*?(?:/|\s*per\s*)min', p)
        if fill_m and drain_m:
            fill, drain = int(fill_m.group(1)), int(drain_m.group(1))
            start_m = re.search(r'(?:from|at)\s+(\d+)\s*l', p)
            target_m = re.search(r'reaches?\s+(\d+)\s*l', p)
            if start_m and target_m:
                net = fill - drain
                if net > 0:
                    val = round((int(target_m.group(1)) - int(start_m.group(1))) / net, 1)
                    for i, c in enumerate(candidates):
                        if c.strip() == f"{val} minutes": return i, 0.9

        m_apart = re.search(r'(\d+)\s*km\s*apart', p)
        m_speeds = re.findall(r'(?:goes?|speed|at)\s+(\d+)\s*km/h', p)
        if m_apart and len(m_speeds) >= 2 and 'toward' in p:
            d = int(m_apart.group(1))
            v1, v2 = int(m_speeds[0]), int(m_speeds[1])
            val = round(d / (v1 + v2), 1)
            for i, c in enumerate(candidates):
                if c.strip() == f"{val} hours": return i, 0.9

        pop_m = re.search(r'(\d+)\s+people', p)
        birth_m = re.search(r'(\d+)\s+people\s+are\s+born', p)
        death_m = re.search(r'(\d+)\s+people\s+die', p)
        years_m = re.search(r'after\s+(\d+)\s+years', p)
        if pop_m and birth_m and death_m and years_m:
            final = int(pop_m.group(1)) + (int(birth_m.group(1)) - int(death_m.group(1))) * int(years_m.group(1))
            for i, c in enumerate(candidates):
                if c.strip() == str(final): return i, 0.9
        return None

    def _try_timezone(self, prompt, candidates):
        p = prompt.lower()
        m = re.search(
            r"it's\s+(\d+):00\s+\((\w+)\)\s+in\s+(.+?)\s+\(utc([+-]?\d+)\).*?"
            r"(\d+)-hour\s+flight.*?(?:to|for)\s+(.+?)\s+\(utc([+-]?\d+)\)", p)
        if not m: return None
        start_hour, start_day = int(m.group(1)), m.group(2).lower()
        tz1, flight_hours, tz2 = int(m.group(4)), int(m.group(5)), int(m.group(7))
        arrival_hour = start_hour + flight_hours + (tz2 - tz1)
        days_off = 0
        while arrival_hour >= 24: arrival_hour -= 24; days_off += 1
        while arrival_hour < 0: arrival_hour += 24; days_off -= 1
        try: day_idx = DAYS.index(start_day)
        except ValueError: return None
        arr_day = DAYS[(day_idx + days_off) % 7].capitalize()
        if arrival_hour == 0: ts = "12:00 AM (midnight)"
        elif arrival_hour < 12: ts = f"{arrival_hour}:00 AM"
        elif arrival_hour == 12: ts = "12:00 PM (noon)"
        else: ts = f"{arrival_hour - 12}:00 PM"
        for i, c in enumerate(candidates):
            if c.strip() == f"{arr_day} {ts}": return i, 0.9
        return None

    def _try_compositional(self, prompt, candidates):
        p = prompt.lower()
        day_m = re.search(r'today\s+is\s+(\w+)', p)
        offset_m = re.search(r'(?:in|after)\s+(\d+)\s+days', p)
        if day_m and offset_m and 'weekend' in p and 'monday' in p:
            try: idx = DAYS.index(day_m.group(1).lower())
            except ValueError: return None
            target = (idx + int(offset_m.group(1))) % 7
            final = "Monday" if target in (5, 6) else DAYS[target].capitalize()
            for i, c in enumerate(candidates):
                if c.strip().lower() == final.lower(): return i, 0.9

        km_m = re.search(r'travels?\s+(\d+)\s*km', p)
        rate_m = re.search(r'(\d+)\s+liters?\s+per\s+100\s*km', p)
        cost_m = re.search(r'\$?([\d.]+)(?:/|\s*per\s*)liter', p)
        if km_m and rate_m and cost_m:
            total = round(int(km_m.group(1)) * int(rate_m.group(1)) / 100 * float(cost_m.group(1)), 2)
            for i, c in enumerate(candidates):
                if c.strip() == f"${total}": return i, 0.9

        apples_m = re.search(r'has\s+(\d+)\s+apples.*?gives.*?(\d+)\s+more', p)
        if apples_m and 'one bag' in p:
            total = int(apples_m.group(1)) + int(apples_m.group(2))
            for i, c in enumerate(candidates):
                if c.strip() == str(total): return i, 0.9

        stock_m = re.search(r'starts?\s+at\s+\$?(\d+).*?rises?\s+(\d+)%.*?drops?\s+(\d+)%', p)
        if stock_m:
            base, up, down = int(stock_m.group(1)), int(stock_m.group(2)), int(stock_m.group(3))
            final = round(base * (1 + up / 100) * (1 - down / 100), 2)
            for i, c in enumerate(candidates):
                if c.strip() == f"${final}": return i, 0.9
        return None

    def evaluate(self, prompt, candidates):
        if not candidates: return []
        for solver in [self._try_scheduling, self._try_rate, self._try_timezone, self._try_compositional]:
            r = solver(prompt, candidates)
            if r is not None:
                return self._make_result(r[0], candidates)
        r = try_standard(prompt, candidates)
        if r is not None:
            return self._make_result(r[0], candidates)
        out = []
        for c in candidates:
            ca = len(zlib.compress(prompt.encode()))
            cb = len(zlib.compress(c.encode()))
            cab = len(zlib.compress((prompt + " " + c).encode()))
            d = (cab - min(ca, cb)) / max(ca, cb) if max(ca, cb) > 0 else 1.0
            out.append({"candidate": c, "score": 1.0 / (1.0 + d)})
        return sorted(out, key=lambda x: x["score"], reverse=True)

    def confidence(self, prompt, answer):
        r = self.evaluate(prompt, [answer, "DUMMY_WRONG"])
        return min(r[0]["score"], 0.95) if r and r[0]["candidate"] == answer else 0.1
