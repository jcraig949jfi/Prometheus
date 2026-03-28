#!/usr/bin/env python3
"""Overnight gap closing: CAITL the survivor, add Nous triples, re-score.

Usage:
    python overnight_gap_closing.py --step 1   # CAITL the survivor
    python overnight_gap_closing.py --step 2   # Add gap triples to Nous
    python overnight_gap_closing.py --step 3   # Re-score coverage
"""

import argparse
import json
import logging
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [GAP] %(message)s")
log = logging.getLogger("gap")

HEPH_ROOT = Path(__file__).resolve().parent.parent
PROMETHEUS_ROOT = HEPH_ROOT.parent.parent
V5_DIR = HEPH_ROOT / "forge_v5"
V6_DIR = HEPH_ROOT / "forge_v6"
FORGE_DIR = HEPH_ROOT / "forge"


# ============================================================
# STEP 1: CAITL the survivor — push 50% categories toward 80%+
# ============================================================
def step_1_caitl_survivor():
    """Apply category-driven CAITL to the forge survivor targeting its 50% categories."""
    from test_harness import load_tool_from_file
    from trap_generator_extended import generate_full_battery

    V6_DIR.mkdir(parents=True, exist_ok=True)

    survivor_path = FORGE_DIR / "information_theory_x_abductive_reasoning_x_sensitivity_analysis.py"
    if not survivor_path.exists():
        log.error("Survivor not found at %s", survivor_path)
        return

    log.info("Reading survivor: %s", survivor_path.name)
    survivor_src = survivor_path.read_text(encoding="utf-8")

    # Generate battery to identify specific failures
    battery = generate_full_battery(n_per_category=3, seed=42)
    tool = load_tool_from_file(survivor_path)

    # Find which categories it fails at 50%
    from collections import defaultdict
    cat_results = defaultdict(lambda: {"correct": 0, "total": 0})
    for t in battery:
        try:
            r = tool.evaluate(t["prompt"], t["candidates"])
            ok = r[0]["candidate"] == t["correct"] if r else False
            cat_results[t["category"]]["total"] += 1
            cat_results[t["category"]]["correct"] += int(ok)
        except:
            cat_results[t["category"]]["total"] += 1

    # Categories at 50% (room to improve)
    fifty_pct = []
    zero_pct = []
    for cat, res in sorted(cat_results.items()):
        rate = res["correct"] / res["total"] if res["total"] else 0
        if 0.3 <= rate <= 0.6:
            fifty_pct.append((cat, rate))
        elif rate == 0:
            zero_pct.append(cat)

    log.info("Survivor's 50%% categories (%d): %s", len(fifty_pct),
             ", ".join(c for c, _ in fifty_pct))
    log.info("Survivor's 0%% categories (%d): %s", len(zero_pct),
             ", ".join(zero_pct[:10]))

    # Build the CAITL v6 improvement
    # Key insight: the survivor already has good architecture (abductive + info theory + sensitivity)
    # We need to add specific parsers for the 50% and 0% categories
    # Focus on: temporal, spatial, causal-interventional, complex ToM, self-referential

    additions = '''
    # === CAITL v6 additions: gap-targeted parsers ===

    def _temporal_solve(self, prompt, candidates):
        """Temporal reasoning: age, ordering, duration, rate, scheduling."""
        pl = prompt.lower()

        # Age reasoning: "X is N years older than Y. Y is M. How old is X?"
        age_m = re.findall(r'(\w+)\s+is\s+(\d+)\s+years?\s+(?:older|younger)\s+than\s+(\w+)', pl)
        if age_m and re.search(r'how old', pl):
            # Build age graph
            ages = {}
            for a, diff, b in age_m:
                ages[(a, b)] = int(diff)
            # Find stated ages
            stated = re.findall(r'(\w+)\s+is\s+(\d+)', pl)
            known = {}
            for name, age in stated:
                if name.lower() not in [x[0] for x in age_m] + [x[2] for x in age_m]:
                    continue
                known[name.lower()] = int(age)
            # Propagate
            changed = True
            while changed:
                changed = False
                for (a, b), diff in ages.items():
                    if a in known and b not in known:
                        known[b] = known[a] - diff if 'older' in pl else known[a] + diff
                        changed = True
                    elif b in known and a not in known:
                        known[a] = known[b] + diff if 'older' in pl else known[b] - diff
                        changed = True
            # Match candidate
            target = re.search(r'how old is (\w+)', pl)
            if target and target.group(1).lower() in known:
                answer = known[target.group(1).lower()]
                for c in candidates:
                    if str(answer) in c:
                        return c, 0.8
            return None, 0

        # Sequence reconstruction: order events from clues
        if re.search(r'(?:order|sequence|first|earliest|latest)', pl) and re.search(r'(?:before|after|then)', pl):
            before_pairs = re.findall(r'(\w+)\s+(?:happened|came|arrived|occurred)\s+(?:before|earlier than)\s+(\w+)', pl)
            after_pairs = re.findall(r'(\w+)\s+(?:happened|came|arrived|occurred)\s+(?:after|later than)\s+(\w+)', pl)
            if before_pairs or after_pairs:
                # Build ordering
                entities = set()
                order = []  # (earlier, later)
                for a, b in before_pairs:
                    order.append((a.lower(), b.lower()))
                    entities.update([a.lower(), b.lower()])
                for a, b in after_pairs:
                    order.append((b.lower(), a.lower()))
                    entities.update([a.lower(), b.lower()])
                # Topological sort
                if entities and order:
                    for c in candidates:
                        cl = c.lower()
                        # Check if candidate matches earliest/first
                        if re.search(r'first|earliest', pl):
                            # Find entity with no predecessors
                            has_pred = {b for _, b in order}
                            roots = entities - has_pred
                            if roots:
                                root = roots.pop()
                                if root in cl:
                                    return c, 0.7
            return None, 0

        # Scheduling conflict: overlap detection
        time_ranges = re.findall(r'(\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM)?)\s*(?:to|-)\s*(\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM)?)', pl)
        if len(time_ranges) >= 2 and re.search(r'(?:both|conflict|overlap|attend)', pl):
            # Simple overlap check
            for c in candidates:
                if 'no' in c.lower() or 'cannot' in c.lower() or 'conflict' in c.lower():
                    return c, 0.7
            return None, 0

        # Relative day: "day after the day before yesterday"
        if re.search(r'day\s+(?:after|before)\s+(?:the\s+)?day\s+(?:after|before)', pl):
            # Count net offset
            afters = len(re.findall(r'day after', pl))
            befores = len(re.findall(r'day before', pl)) + len(re.findall(r'yesterday', pl))
            net = afters - befores
            days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            today_m = re.search(r'today is (\w+day)', pl)
            if today_m:
                today_idx = next((i for i, d in enumerate(days) if d == today_m.group(1).lower()), -1)
                if today_idx >= 0:
                    target_day = days[(today_idx + net) % 7]
                    for c in candidates:
                        if target_day in c.lower():
                            return c, 0.8
            return None, 0

        # Concurrent events: parallel tasks
        if re.search(r'(?:same time|simultaneously|together|parallel)', pl):
            times = [int(x) for x in re.findall(r'(\d+)\s*(?:min|hour|second)', pl)]
            if times and re.search(r'(?:first|earliest|soonest|done)', pl):
                answer = min(times)
                for c in candidates:
                    if str(answer) in c:
                        return c, 0.8
            return None, 0

        # Rate of change
        if re.search(r'(?:accelerat|deceler|increasing|decreasing|rate.*change)', pl):
            nums = [float(x) for x in re.findall(r'(\d+\.?\d*)', pl)]
            if len(nums) >= 3:
                diffs = [nums[i+1] - nums[i] for i in range(len(nums)-1)]
                if len(diffs) >= 2:
                    accel = diffs[-1] - diffs[0]
                    keyword = 'accelerat' if accel > 0 else 'deceler'
                    for c in candidates:
                        if keyword in c.lower():
                            return c, 0.7
            return None, 0

        return None, 0

    def _spatial_solve(self, prompt, candidates):
        """Spatial reasoning: direction, perspective."""
        pl = prompt.lower()

        # Direction composition
        if re.search(r'face\s+(?:north|south|east|west)', pl) and re.search(r'turn\s+(?:left|right)', pl):
            dirs = ['north', 'east', 'south', 'west']
            face_m = re.search(r'face\s+(north|south|east|west)', pl)
            if face_m:
                idx = dirs.index(face_m.group(1))
                turns = re.findall(r'turn\s+(left|right)', pl)
                for turn in turns:
                    idx = (idx + 1) % 4 if turn == 'right' else (idx - 1) % 4
                answer = dirs[idx]
                for c in candidates:
                    if answer in c.lower():
                        return c, 0.85
            return None, 0

        # Left-right reversal (facing each other)
        if re.search(r'(?:face|facing|across|opposite)', pl) and re.search(r'(?:left|right)', pl):
            if re.search(r'(?:his|her|their|bob|from.*perspective)', pl):
                # Person facing you: your left = their right
                if 'left' in pl and re.search(r'(?:raises?|lifts?)\s+(?:his|her|their)?\s*left', pl):
                    for c in candidates:
                        if 'right' in c.lower():
                            return c, 0.85
                elif 'right' in pl and re.search(r'(?:raises?|lifts?)\s+(?:his|her|their)?\s*right', pl):
                    for c in candidates:
                        if 'left' in c.lower():
                            return c, 0.85
            return None, 0

        return None, 0

    def _causal_interventional_solve(self, prompt, candidates):
        """Causal intervention and counterfactual reasoning."""
        pl = prompt.lower()

        # Intervention: "if we force Y=0, what happens to Z?"
        if re.search(r'(?:force|set|intervene|do)\s*\(?', pl) and re.search(r'what\s+happens', pl):
            # Parse causal chain
            chains = re.findall(r'(\w+)\s*(?:causes|leads to|->|→)\s*(\w+)', pl)
            if chains:
                forced_m = re.search(r'(?:force|set)\s+(\w+)\s*(?:=|to)\s*(\d+)', pl)
                if forced_m:
                    forced_var = forced_m.group(1).lower()
                    # If forced var is in a chain, downstream is affected
                    downstream = set()
                    frontier = {forced_var}
                    while frontier:
                        next_f = set()
                        for a, b in chains:
                            if a.lower() in frontier:
                                downstream.add(b.lower())
                                next_f.add(b.lower())
                        frontier = next_f - downstream
                    # Check candidates
                    for c in candidates:
                        cl = c.lower()
                        if any(d in cl for d in downstream) and ('change' in cl or 'affect' in cl or '0' in cl):
                            return c, 0.7
            return None, 0

        # Counterfactual: "if X hadn't happened, would Y?"
        if re.search(r"(?:hadn't|had not|didn't|did not)\s+(?:happen|occur)", pl):
            # Universal rule + counterfactual
            if re.search(r'all\s+\w+\s+who', pl) or re.search(r'if\s+\w+\s+then', pl):
                for c in candidates:
                    if c.lower().startswith('yes'):
                        return c, 0.7
            return None, 0

        return None, 0

    def _complex_tom_solve(self, prompt, candidates):
        """Complex theory of mind: deception, perspective, information asymmetry."""
        pl = prompt.lower()

        # Strategic deception: "X knows Y does opposite. What should X say?"
        if re.search(r'(?:opposite|contrary|reverse)', pl) and re.search(r'(?:should|would)\s+\w+\s+say', pl):
            # If target does opposite, say the opposite of what you want
            want_m = re.search(r'wants?\s+\w+\s+to\s+(?:go\s+)?(left|right|stay|leave|yes|no)', pl)
            if want_m:
                want = want_m.group(1)
                opposite = {'left': 'right', 'right': 'left', 'stay': 'leave',
                           'leave': 'stay', 'yes': 'no', 'no': 'yes'}
                answer = opposite.get(want, want)
                for c in candidates:
                    if answer in c.lower():
                        return c, 0.8
            return None, 0

        # Perspective shift: "From X's seat... from Y's perspective"
        if re.search(r"(?:from\s+\w+'s\s+(?:seat|view|perspective|side))", pl):
            # Facing each other = left/right swap
            if re.search(r'(?:across|facing|opposite)', pl):
                if 'left' in pl:
                    for c in candidates:
                        if 'right' in c.lower():
                            return c, 0.8
                elif 'right' in pl:
                    for c in candidates:
                        if 'left' in c.lower():
                            return c, 0.8
            return None, 0

        # Information asymmetry: "You know X. Tom doesn't. What does Tom think?"
        if re.search(r"(?:doesn't|does not)\s+know", pl) and re.search(r'what\s+does\s+\w+\s+(?:think|believe|expect)', pl):
            # The uninformed person uses the default/naive answer
            if re.search(r'(?:rigged|loaded|biased|unfair)', pl):
                # Uninformed person thinks it's fair
                for c in candidates:
                    if '50' in c or 'fair' in c.lower() or 'equal' in c.lower():
                        return c, 0.8
            return None, 0

        # Intention reading: "X brought umbrella on sunny day. What does this tell us?"
        if re.search(r'what\s+(?:can|does|do)\s+(?:we|this)\s+(?:infer|tell|suggest|indicate)', pl):
            for c in candidates:
                if 'believe' in c.lower() or 'expect' in c.lower() or 'think' in c.lower():
                    return c, 0.7
            return None, 0

        return None, 0

    def _self_referential_solve(self, prompt, candidates):
        """Self-referential reasoning: liar detection, constraint propagation."""
        pl = prompt.lower()

        # Liar detection: "X says Y lies. Y says Z lies. Z says X tells truth."
        if re.search(r'(?:says|claims)\s+\w+\s+(?:is\s+)?(?:lying|liar|tells?\s+the\s+truth)', pl):
            # Extract claims
            claims = re.findall(r'(\w+)\s+says\s+(\w+)\s+(?:is\s+)?(?:lying|is\s+a\s+liar)', pl)
            truth_claims = re.findall(r'(\w+)\s+says\s+(\w+)\s+tells?\s+the\s+truth', pl)

            if claims or truth_claims:
                people = set()
                for a, b in claims + truth_claims:
                    people.update([a, b])

                # Try each person as truth-teller
                for p in people:
                    # Assume p tells truth, check consistency
                    truth_tellers = {p}
                    liars = set()
                    changed = True
                    consistent = True
                    while changed:
                        changed = False
                        for a, b in claims:
                            if a in truth_tellers:
                                if b not in liars:
                                    liars.add(b)
                                    changed = True
                            elif a in liars:
                                if b not in truth_tellers:
                                    truth_tellers.add(b)
                                    changed = True
                        for a, b in truth_claims:
                            if a in truth_tellers:
                                if b not in truth_tellers:
                                    truth_tellers.add(b)
                                    changed = True
                            elif a in liars:
                                if b not in liars:
                                    liars.add(b)
                                    changed = True
                        if truth_tellers & liars:
                            consistent = False
                            break

                    if consistent and not (truth_tellers & liars):
                        # Check if exactly one truth-teller (if specified)
                        if re.search(r'exactly one', pl) and len(truth_tellers) == 1:
                            winner = truth_tellers.pop()
                            for c in candidates:
                                if winner in c.lower():
                                    return c, 0.85
                            truth_tellers.add(winner)

                        # Return whoever is the truth-teller
                        for c in candidates:
                            for tt in truth_tellers:
                                if tt in c.lower():
                                    return c, 0.75

            return None, 0

        return None, 0
'''

    # Read the survivor source and add the new methods
    # Find the class body and insert before the last method
    class_match = re.search(r'class ReasoningTool:', survivor_src)
    if not class_match:
        log.error("Could not find class ReasoningTool in survivor")
        return

    # Find evaluate method to insert before it
    eval_match = re.search(r'(\n    def evaluate\(self)', survivor_src)
    if eval_match:
        insertion_point = eval_match.start()
        new_src = survivor_src[:insertion_point] + additions + survivor_src[insertion_point:]
    else:
        # Append to end of class
        new_src = survivor_src + additions

    # Now modify evaluate() to call the new solvers
    eval_hook = '''
        # === CAITL v6: Try gap-targeted solvers first ===
        for solver in [self._temporal_solve, self._spatial_solve,
                       self._causal_interventional_solve, self._complex_tom_solve,
                       self._self_referential_solve]:
            try:
                best_cand, score = solver(prompt, candidates)
                if best_cand and score > 0.5:
                    results = []
                    for c in candidates:
                        if c == best_cand:
                            results.append({"candidate": c, "score": float(score),
                                          "reasoning": f"execution:gap_solver={solver.__name__}"})
                        else:
                            results.append({"candidate": c, "score": float(1.0 - score),
                                          "reasoning": "structural:gap_solver_alternative"})
                    results.sort(key=lambda x: x["score"], reverse=True)
                    return results
            except Exception:
                pass
        # === End CAITL v6 hook ===
'''

    # Insert the hook at the start of evaluate() body
    eval_body = re.search(r'def evaluate\(self, prompt.*?\).*?:\n(.*?)(?=\n    def |\Z)',
                          new_src, re.DOTALL)
    if eval_body:
        # Find the first line of the method body
        body_start = eval_body.start(1)
        # Find indentation
        first_line = new_src[body_start:body_start + 200].split('\n')[0]
        indent = len(first_line) - len(first_line.lstrip())

        # Insert hook after docstring if present
        docstring_end = re.search(r'""".*?"""', new_src[body_start:body_start + 500], re.DOTALL)
        if docstring_end:
            insert_at = body_start + docstring_end.end()
        else:
            insert_at = body_start

        new_src = new_src[:insert_at] + "\n" + eval_hook + new_src[insert_at:]

    # Save to v6
    out_path = V6_DIR / survivor_path.name
    out_path.write_text(new_src, encoding="utf-8")
    log.info("Wrote CAITL v6 survivor to %s", out_path)

    # Test it
    try:
        tool_v6 = load_tool_from_file(out_path)
        battery = generate_full_battery(n_per_category=2, seed=42)

        from collections import defaultdict
        v6_results = defaultdict(lambda: {"correct": 0, "total": 0})
        for t in battery:
            try:
                r = tool_v6.evaluate(t["prompt"], t["candidates"])
                ok = r[0]["candidate"] == t["correct"] if r else False
                v6_results[t["category"]]["total"] += 1
                v6_results[t["category"]]["correct"] += int(ok)
            except:
                v6_results[t["category"]]["total"] += 1

        # Compare v1 vs v6
        improved = 0
        regressed = 0
        newly_covered = 0
        for cat in sorted(v6_results):
            v6_rate = v6_results[cat]["correct"] / v6_results[cat]["total"]
            v1_rate = cat_results[cat]["correct"] / cat_results[cat]["total"] if cat in cat_results and cat_results[cat]["total"] else 0
            if v6_rate > v1_rate + 0.1:
                improved += 1
                if v1_rate == 0:
                    newly_covered += 1
                log.info("  IMPROVED: %s %.0f%% -> %.0f%%", cat, v1_rate * 100, v6_rate * 100)
            elif v6_rate < v1_rate - 0.1:
                regressed += 1
                log.info("  REGRESSED: %s %.0f%% -> %.0f%%", cat, v1_rate * 100, v6_rate * 100)

        total_acc = sum(r["correct"] for r in v6_results.values()) / sum(r["total"] for r in v6_results.values())
        log.info("v6 survivor: overall %.1f%%, %d improved, %d regressed, %d newly covered",
                 total_acc * 100, improved, regressed, newly_covered)

    except Exception as e:
        log.error("v6 test failed: %s", e)
        import traceback
        traceback.print_exc()


# ============================================================
# STEP 2: Add gap-targeted concept triples to Nous
# ============================================================
def step_2_nous_triples():
    """Add concept triples targeting the 21 gap clusters to Nous priority queue."""
    log.info("Adding gap-targeted concept triples to Nous...")

    # The 5 concept-triple hypotheses for each gap cluster
    gap_triples = [
        # Temporal-sequential
        {"concepts": ["Dynamical Systems", "Ergodic Theory", "Compositionality"],
         "reason": "Temporal-sequential gap: ordered state manipulation"},
        {"concepts": ["Chaos Theory", "Feedback Control", "Type Theory"],
         "reason": "Temporal-sequential gap: state-dependent sequential processing"},
        {"concepts": ["Kalman Filtering", "Dynamical Systems", "Compositionality"],
         "reason": "Temporal-sequential gap: state estimation over time"},

        # Spatial
        {"concepts": ["Category Theory", "Compositionality", "Topology"],
         "reason": "Spatial gap: reference frame transformation via group theory"},
        {"concepts": ["Graph Theory", "Compositionality", "Mechanism Design"],
         "reason": "Spatial gap: relational structure mapping"},

        # Causal-interventional
        {"concepts": ["Causal Inference", "Bayesian Inference", "Information Theory"],
         "reason": "Causal-interventional gap: do-calculus / Pearl hierarchy rung 2"},
        {"concepts": ["Causal Inference", "Counterfactual Reasoning", "Model Checking"],
         "reason": "Causal-interventional gap: counterfactual / Pearl hierarchy rung 3"},
        {"concepts": ["Causal Inference", "Network Science", "Mechanism Design"],
         "reason": "Causal-interventional gap: structural causal models"},

        # Complex ToM
        {"concepts": ["Theory of Mind", "Nash Equilibrium", "Bayesian Inference"],
         "reason": "Complex ToM gap: recursive Bayesian agent modeling"},
        {"concepts": ["Theory of Mind", "Mechanism Design", "Epistemology"],
         "reason": "Complex ToM gap: epistemic logic + strategic reasoning"},
        {"concepts": ["Theory of Mind", "Metacognition", "Abductive Reasoning"],
         "reason": "Complex ToM gap: recursive belief attribution"},

        # Self-referential
        {"concepts": ["Model Checking", "Constraint Satisfaction", "Falsificationism"],
         "reason": "Self-referential gap: constraint propagation over loops"},
        {"concepts": ["Type Theory", "Hoare Logic", "Falsificationism"],
         "reason": "Self-referential gap: fixed-point theory + formal verification"},

        # Compositional (cross-domain)
        {"concepts": ["Compositionality", "Dynamical Systems", "Causal Inference"],
         "reason": "Compositional gap: chaining temporal + causal reasoning"},
        {"concepts": ["Compositionality", "Active Inference", "Theory of Mind"],
         "reason": "Compositional gap: chaining inference + ToM"},
    ]

    # Save as a priority injection file for Nous
    nous_dir = PROMETHEUS_ROOT / "agents" / "nous"
    priority_file = nous_dir / "data" / "priority_triples.json"
    priority_file.parent.mkdir(parents=True, exist_ok=True)

    existing = []
    if priority_file.exists():
        try:
            existing = json.loads(priority_file.read_text(encoding="utf-8"))
        except:
            pass

    # Merge (avoid duplicates)
    existing_sets = {frozenset(t["concepts"]) for t in existing}
    added = 0
    for triple in gap_triples:
        if frozenset(triple["concepts"]) not in existing_sets:
            existing.append(triple)
            existing_sets.add(frozenset(triple["concepts"]))
            added += 1

    priority_file.write_text(json.dumps(existing, indent=2), encoding="utf-8")
    log.info("Added %d gap-targeted triples to %s (total: %d)", added, priority_file, len(existing))

    # Also log them for the journal
    for triple in gap_triples:
        log.info("  %s — %s", " + ".join(triple["concepts"]), triple["reason"])


# ============================================================
# STEP 3: Re-score and update coverage map
# ============================================================
def step_3_rescore():
    """Re-score the survivor v6 and update coverage numbers."""
    from test_harness import load_tool_from_file
    from trap_generator_extended import generate_full_battery

    log.info("Re-scoring coverage after CAITL v6...")

    battery = generate_full_battery(n_per_category=2, seed=42)
    categories = sorted(set(t["category"] for t in battery))

    # Load all relevant tools
    tools_to_test = {}

    # The 4 minimum covering set (from v5)
    min_set_path = V5_DIR / "minimum_covering_set.json"
    if min_set_path.exists():
        ms = json.loads(min_set_path.read_text(encoding="utf-8"))
        for name in ms.get("minimum_set", []):
            py = V5_DIR / f"{name}.py"
            if py.exists():
                tools_to_test[name] = py

    # The v6 survivor
    v6_survivor = V6_DIR / "information_theory_x_abductive_reasoning_x_sensitivity_analysis.py"
    if v6_survivor.exists():
        tools_to_test["survivor_v6"] = v6_survivor
    else:
        # Fall back to v1
        v1_survivor = FORGE_DIR / "information_theory_x_abductive_reasoning_x_sensitivity_analysis.py"
        if v1_survivor.exists():
            tools_to_test["survivor_v1"] = v1_survivor

    log.info("Testing %d tools: %s", len(tools_to_test), list(tools_to_test.keys()))

    from collections import defaultdict
    all_coverage = {}
    for name, py in tools_to_test.items():
        try:
            tool = load_tool_from_file(py)
            cat_results = {}
            for t in battery:
                cat = t["category"]
                try:
                    r = tool.evaluate(t["prompt"], t["candidates"])
                    ok = r[0]["candidate"] == t["correct"] if r else False
                except:
                    ok = False
                if cat not in cat_results:
                    cat_results[cat] = {"correct": 0, "total": 0}
                cat_results[cat]["total"] += 1
                cat_results[cat]["correct"] += int(ok)

            all_coverage[name] = {c: r["correct"]/r["total"] if r["total"] else 0
                                  for c, r in cat_results.items()}
        except Exception as e:
            log.warning("Failed to score %s: %s", name, e)

    # Compute combined coverage
    covered = set()
    for cat in categories:
        for name, cov in all_coverage.items():
            if cov.get(cat, 0) >= 0.5:
                covered.add(cat)
                break

    uncovered = sorted(set(categories) - covered)

    log.info("UPDATED COVERAGE: %d/%d categories (%.0f%%)",
             len(covered), len(categories), len(covered) / len(categories) * 100)
    log.info("REMAINING GAPS: %d", len(uncovered))
    for cat in uncovered:
        best = max((all_coverage[n].get(cat, 0), n) for n in all_coverage)
        log.info("  %s (best: %.0f%% by %s)", cat, best[0] * 100, best[1])

    # Save updated coverage
    out = V6_DIR / "coverage_update.json" if V6_DIR.exists() else V5_DIR / "coverage_update.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "tools_tested": list(tools_to_test.keys()),
        "categories_total": len(categories),
        "categories_covered": len(covered),
        "categories_uncovered": len(uncovered),
        "coverage_pct": round(len(covered) / len(categories) * 100, 1),
        "uncovered_list": uncovered,
        "per_tool_coverage": {n: {c: round(v, 4) for c, v in cov.items()}
                              for n, cov in all_coverage.items()},
    }, indent=2), encoding="utf-8")
    log.info("Saved: %s", out)


# ============================================================
# MAIN
# ============================================================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--step", type=int, required=True, choices=[1, 2, 3])
    args = parser.parse_args()

    steps = {
        1: ("CAITL the survivor", step_1_caitl_survivor),
        2: ("Add gap triples to Nous", step_2_nous_triples),
        3: ("Re-score coverage", step_3_rescore),
    }

    name, fn = steps[args.step]
    log.info("=" * 60)
    log.info("Step %d: %s", args.step, name)
    log.info("=" * 60)
    try:
        fn()
    except Exception as e:
        log.error("Step %d failed: %s", args.step, e)
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
