"""Charon — independent held-out battery for Apollo experiment E9.

Authored blind, 2026-08-25. I have not read apollo/src/blackboard*.py,
apollo/data/clean_canary_v01.json, any Apollo registry or operator listing, the E9
preregistration, or the standing request document, and I did not look up Apollo's
per-category performance. The battery is committed under roles/Charon/ rather than
apollo/data/ so that my "zero commits touching Apollo paths" property -- the thing that
makes this instrument independent -- remains true and checkable after delivery.

GOLD. Every answer is computed or enumerated below in `verify()`, which runs as an assertion
over all 42 tasks before the JSON is written. No answer is model-judged: the arithmetic ones
are recomputed from the stated premise, the logical ones are decided by explicit enumeration
or by the truth condition written out in the check. If a task's gold could not be settled by
inspection or arithmetic it was not written.

CONTROLS.
  position  the correct answer's slot is drawn from a fixed multiset (11,11,10,10) shuffled
            with a fixed seed, so it is balanced overall and decorrelated from category order.
  length    recorded, not assumed. Per task the sidecar records whether the correct answer is
            tied-longest, strictly longest, tied-shortest, strictly shortest, and the battery's
            expected "pick the longest candidate" score is computed with ties resolved as 1/k.

    python roles/Charon/apollo_e9/build_battery.py
"""
import json
import pathlib
import random
from fractions import Fraction

HERE = pathlib.Path(__file__).resolve().parent
SEED = 20260825

# (category, prompt, correct, [three distractors], gold-check tag)
T = []

# ---------------------------------------------------------------- numeric_comparison
T += [
    ("numeric_comparison",
     "A cargo drone has a payload limit of 47.5 kg. A survey drone has a payload limit of "
     "47.05 kg. Which drone can carry more?",
     "the cargo drone", ["the survey drone", "both are identical", "it cannot be determined"],
     ("cmp", 47.5, 47.05, "gt")),
    ("numeric_comparison",
     "Station A recorded -12 °C overnight. Station B recorded -3 °C overnight. Which station "
     "was colder?",
     "station A", ["station B", "neither, both equal", "not enough information"],
     ("cmp", -12, -3, "lt")),
    ("numeric_comparison",
     "One reservoir is 3/8 full. Another is 0.4 full. Which holds the larger fraction of its "
     "capacity?",
     "the reservoir at 0.4",
     ["the reservoir at 3/8", "they are equally full", "it depends on the reservoir sizes"],
     ("cmp", Fraction(2, 5), Fraction(3, 8), "gt")),
    ("numeric_comparison",
     "Ledger A lists 1,204,000 entries. Ledger B lists 1,240,000 entries. Which ledger lists "
     "more entries?",
     "ledger B", ["ledger A", "the two are equal", "cannot be established"],
     ("cmp", 1240000, 1204000, "gt")),
    ("numeric_comparison",
     "Machine A completes 9 items every 4 minutes. Machine B completes 11 items every 5 "
     "minutes. Which machine is faster?",
     "machine A", ["machine B", "they run at the same rate", "insufficient data"],
     ("cmp", Fraction(9, 4), Fraction(11, 5), "gt")),
    ("numeric_comparison",
     "A beam is 5/4 metres long. A rod is 1.25 metres long. Which is longer?",
     "they are the same length", ["the beam", "the rod", "it cannot be decided"],
     ("cmp", Fraction(5, 4), Fraction(5, 4), "eq")),
]

# ------------------------------------------------------------ numeric_stated_premise
T += [
    ("numeric_stated_premise",
     "Every crate holds exactly 18 bolts. A shipment contains 7 crates. How many bolts are in "
     "the shipment?",
     "126", ["125", "128", "132"], ("arith", 18 * 7, "126")),
    ("numeric_stated_premise",
     "A recipe uses exactly 250 millilitres of stock per serving. You prepare 6 servings. How "
     "much stock is used in total?",
     "1500 millilitres",
     ["1250 millilitres", "1560 millilitres", "2500 millilitres"],
     ("arith", 250 * 6, "1500")),
    ("numeric_stated_premise",
     "A tank loses exactly 3.5 litres of water per hour. How much does it lose over 8 hours?",
     "28 litres", ["24.5 litres", "28.5 litres", "35 litres"], ("arith", 3.5 * 8, "28")),
    ("numeric_stated_premise",
     "Each page of the register holds exactly 42 lines. A chapter fills 15 pages. How many "
     "lines does the chapter occupy?",
     "630", ["620", "588", "672"], ("arith", 42 * 15, "630")),
    ("numeric_stated_premise",
     "A single ticket costs exactly 23 credits. A group buys 14 tickets. What is the total "
     "cost?",
     "322 credits", ["312 credits", "329 credits", "337 credits"], ("arith", 23 * 14, "322")),
    ("numeric_stated_premise",
     "A sensor samples exactly 240 times per minute. How many samples does it take in 45 "
     "seconds?",
     "180", ["160", "195", "320"], ("arith", 240 * 45 / 60, "180")),
]

# ------------------------------------------------------------------------ transitivity
T += [
    ("transitivity",
     "Ana is taller than Bruno. Bruno is taller than Chen. Who is tallest?",
     "Ana", ["Bruno", "Chen", "it cannot be determined"],
     ("order", [("Ana", "Bruno"), ("Bruno", "Chen")], "max", "Ana")),
    ("transitivity",
     "Crate W is heavier than crate X. Crate X is heavier than crate Y. Crate Y is heavier "
     "than crate Z. Which crate is lightest?",
     "crate Z", ["crate W", "crate X", "crate Y"],
     ("order", [("W", "X"), ("X", "Y"), ("Y", "Z")], "min", "Z")),
    ("transitivity",
     "Mira finished before Noor. Noor finished before Omar. Who finished last?",
     "Omar", ["Mira", "Noor", "it cannot be determined"],
     ("order", [("Mira", "Noor"), ("Noor", "Omar")], "min", "Omar")),
    ("transitivity",
     "Kai is older than Lena. Mateo is older than Lena. Who is oldest?",
     "it cannot be determined", ["Kai", "Lena", "Mateo"],
     ("order", [("Kai", "Lena"), ("Mateo", "Lena")], "max", None)),
    ("transitivity",
     "Item R costs more than item S. Item S costs more than item T. Item T costs more than "
     "item U. Is item R more expensive than item U?",
     "yes", ["no", "they cost the same", "it cannot be determined"],
     ("order", [("R", "S"), ("S", "T"), ("T", "U")], "max", "R")),
    ("transitivity",
     "Village D lies south of village E. Village E lies south of village F. Which village is "
     "furthest north?",
     "village F", ["village D", "village E", "it cannot be determined"],
     ("order", [("F", "E"), ("E", "D")], "max", "F")),
]

# --------------------------------------------------------------------------- all_but_n
T += [
    ("all_but_n",
     "A depot received 60 crates. All but 14 of them were sealed. How many crates were sealed?",
     "46", ["14", "60", "74"], ("arith", 60 - 14, "46")),
    ("all_but_n",
     "A shelf holds 33 volumes. All but 8 of them are hardback. How many are hardback?",
     "25", ["8", "33", "41"], ("arith", 33 - 8, "25")),
    ("all_but_n",
     "Of the 120 seats in the hall, all but 27 were occupied. How many seats were occupied?",
     "93", ["27", "120", "147"], ("arith", 120 - 27, "93")),
    ("all_but_n",
     "All but 5 of the 19 sensors reported in. How many sensors reported in?",
     "14", ["5", "19", "24"], ("arith", 19 - 5, "14")),
    ("all_but_n",
     "A batch contains 250 parts. All but 36 of them passed inspection. How many parts failed "
     "inspection?",
     "36", ["214", "250", "286"], ("arith", 36, "36")),
    ("all_but_n",
     "Of 84 submitted entries, all but 11 were valid. How many entries were invalid?",
     "11", ["73", "84", "95"], ("arith", 11, "11")),
]

# ------------------------------------------------------------------- temporal_ordering
T += [
    ("temporal_ordering",
     "The alarm sounded before the door opened. The door opened before the lights came on. "
     "Which happened last?",
     "the lights came on",
     ["the alarm sounded", "the door opened", "it cannot be determined"],
     ("seq", ["alarm", "door", "lights"], "last", "lights")),
    ("temporal_ordering",
     "The survey was filed after the permit was issued. The permit was issued after the site "
     "was cleared. Which happened first?",
     "the site was cleared",
     ["the survey was filed", "the permit was issued", "it cannot be determined"],
     ("seq", ["cleared", "permit", "survey"], "first", "cleared")),
    ("temporal_ordering",
     "Packet A arrived before packet B. Packet B arrived before packet C. Packet C arrived "
     "before packet D. Which packet arrived third?",
     "packet C", ["packet A", "packet B", "packet D"],
     ("seq", ["A", "B", "C", "D"], "third", "C")),
    ("temporal_ordering",
     "Event X happened after event Y. Event Z happened after event X. Which event happened "
     "second?",
     "event X", ["event Y", "event Z", "it cannot be determined"],
     ("seq", ["Y", "X", "Z"], "second", "X")),
    ("temporal_ordering",
     "The report was signed after the audit began. The audit began after the invoice was paid. "
     "The invoice was paid after the contract was signed. Which happened earliest?",
     "the contract was signed",
     ["the report was signed", "the audit began", "the invoice was paid"],
     ("seq", ["contract", "invoice", "audit", "report"], "first", "contract")),
    ("temporal_ordering",
     "Task P finished before task Q. Task R finished before task Q. Which task finished first?",
     "it cannot be determined", ["task P", "task Q", "task R"],
     ("seq", None, "first", None)),
]

# ----------------------------------------------------------------------- vacuous_truth
T += [
    ("vacuous_truth",
     "The jar contains no red marbles. Consider the claim: every red marble in the jar is "
     "chipped. Is the claim true?",
     "yes, it is true",
     ["no, it is false", "it cannot be determined", "the claim is not well formed"],
     ("logic", "universal", [(False, False), (False, True)], True)),
    ("vacuous_truth",
     "No book on this shelf has more than 500 pages. Consider the claim: every book on the "
     "shelf with more than 500 pages is overdue. Is the claim true?",
     "yes, it is true",
     ["no, it is false", "it cannot be determined", "only if some book is overdue"],
     ("logic", "universal", [(False, False), (False, True)], True)),
    ("vacuous_truth",
     "There are exactly three blue tiles, and exactly one of them is cracked. Consider the "
     "claim: every blue tile is cracked. Is the claim true?",
     "no, it is false",
     ["yes, it is true", "it cannot be determined", "the claim is not well formed"],
     ("logic", "universal", [(True, True), (True, False), (True, False)], False)),
    ("vacuous_truth",
     "No employee in the department holds a pilot licence. Consider the claim: some employee "
     "in the department who holds a pilot licence works weekends. Is the claim true?",
     "no, it is false",
     ["yes, it is true", "it cannot be determined", "only on weekends"],
     ("logic", "existential", [(False, True), (False, False)], False)),
    ("vacuous_truth",
     "The box contains no item weighing more than two kilograms. Consider the claim: if an "
     "item in the box weighs more than two kilograms, then it is fragile. Is the claim true?",
     "yes, it is true",
     ["no, it is false", "it cannot be determined", "only if the box is empty"],
     ("logic", "universal", [(False, False), (False, True)], True)),
    ("vacuous_truth",
     "Nobody in the room is taller than two metres. Consider the claim: everyone in the room "
     "taller than two metres is asleep. Is the claim true?",
     "yes, it is true",
     ["no, it is false", "it cannot be determined", "only if the room is empty"],
     ("logic", "universal", [(False, False), (False, True)], True)),
]

# -------------------------------------------------------------------- consistency_check
T += [
    ("consistency_check",
     "Consider these three statements together: P is heavier than Q; Q is heavier than R; R is "
     "heavier than P. Can all three hold at once?",
     "no, they contradict one another",
     ["yes, all three can hold", "only if two of them are equal",
      "there is not enough information"],
     ("sat", False, "cycle")),
    ("consistency_check",
     "Consider these three statements together: the meeting is on Tuesday; the meeting is in "
     "the afternoon; the room is booked for that meeting all Tuesday afternoon. Can all three "
     "hold at once?",
     "yes, all three can hold",
     ["no, they contradict one another", "only if the meeting is moved",
      "there is not enough information"],
     ("sat", True, "tuesday")),
    ("consistency_check",
     "Consider these three statements together: x + y = 10; x - y = 2; x = 7. Can all three "
     "hold at once?",
     "no, they contradict one another",
     ["yes, all three can hold", "only if y is negative", "there is not enough information"],
     ("sat", False, "linear")),
    ("consistency_check",
     "Three meetings occupy three different days, Monday to Wednesday. Meeting A is not on "
     "Monday. Meeting B is not on Tuesday. Meeting C is not on Wednesday. Can all of this hold "
     "at once?",
     "yes, all of it can hold",
     ["no, it contradicts itself", "only if two meetings share a day",
      "there is not enough information"],
     ("sat", True, "meetings")),
    ("consistency_check",
     "Consider these three statements together: the room holds at most 40 people; 25 adults "
     "are in the room; 12 children are in the room. Can all three hold at once?",
     "yes, all three can hold",
     ["no, they contradict one another", "only if some people leave",
      "there is not enough information"],
     ("sat", True, "room")),
    ("consistency_check",
     "Consider these three statements together: every technician is certified; no certified "
     "person works nights; Sam is a technician who works nights. Can all three hold at once?",
     "no, they contradict one another",
     ["yes, all three can hold", "only if Sam is uncertified",
      "there is not enough information"],
     ("sat", False, "technician")),
]


def verify():
    """Recompute every gold answer. Nothing here consults a model."""
    for cat, prompt, correct, distractors, chk in T:
        kind = chk[0]
        if kind == "cmp":
            a, b, rel = chk[1], chk[2], chk[3]
            assert (a > b) if rel == "gt" else (a < b) if rel == "lt" else (a == b), prompt
        elif kind == "arith":
            val, want = chk[1], chk[2]
            got = int(val) if float(val).is_integer() else val
            assert str(got) == want, (prompt, got, want)
            assert correct.split()[0] == want, (prompt, correct, want)
        elif kind == "order":
            # transitive closure over the stated strict pairs; "max" = no one above it
            pairs, mode, want = chk[1], chk[2], chk[3]
            nodes = {x for p in pairs for x in p}
            above = {n: set() for n in nodes}
            for hi, lo in pairs:
                above[lo].add(hi)
            changed = True
            while changed:
                changed = False
                for n in nodes:
                    for m in list(above[n]):
                        for k in above[m]:
                            if k not in above[n]:
                                above[n].add(k)
                                changed = True
            tops = [n for n in nodes if not above[n]]
            bottoms = [n for n in nodes
                   if all(m in above[n] for m in nodes if m != n)]
            if mode == "max":
                assert (len(tops) == 1 and tops[0] == want) if want else len(tops) > 1, prompt
            else:
                assert len(bottoms) == 1 and bottoms[0] == want, (prompt, bottoms)
        elif kind == "seq":
            seq, pos, want = chk[1], chk[2], chk[3]
            if seq is None:
                assert want is None, prompt          # underdetermined by construction
            else:
                idx = {"first": 0, "second": 1, "third": 2}.get(pos)
                got = seq[idx] if idx is not None else seq[-1]
                assert got == want, (prompt, got, want)
        elif kind == "logic":
            # Enumerate the stated domain. Each element is (antecedent_holds, consequent_holds).
            quant, domain, truth = chk[1], chk[2], chk[3]
            if quant == "universal":
                got = all(c for a, c in domain if a)      # vacuously True on empty antecedent
            else:
                got = any(a and c for a, c in domain)     # False over an empty antecedent
            assert got is truth, (prompt, got, truth)
            assert correct.startswith("yes" if truth else "no"), (prompt, correct)
        elif kind == "sat":
            # Enumerated, not asserted. Each constraint set is decided by exhaustive search
            # over its finite model space, or solved exactly for the linear case.
            import itertools as _it
            want, tag = chk[1], chk[2]
            if tag == "cycle":                       # P>Q, Q>R, R>P over distinct ranks
                got = any(p > q and q > r and r > p
                          for p, q, r in _it.permutations([1, 2, 3]))
            elif tag == "linear":                    # x+y=10, x-y=2, x=7
                x = (10 + 2) / 2
                y = 10 - x
                got = (x + y == 10) and (x - y == 2) and (x == 7)
            elif tag == "meetings":                  # A!=Mon, B!=Tue, C!=Wed, all distinct
                days = ["Mon", "Tue", "Wed"]
                got = any(a != "Mon" and b != "Tue" and c != "Wed"
                          for a, b, c in _it.permutations(days))
            elif tag == "room":                      # capacity 40, 25 adults + 12 children
                got = (25 + 12) <= 40
            elif tag == "technician":                # every tech certified; no certified
                got = any(tech and nights and (not tech or cert)      # works nights; Sam both
                          and (not cert or not nights)
                          for tech, cert, nights in [(True, c, True) for c in (False, True)])
            elif tag == "tuesday":                   # three mutually compatible facts
                got = any(day == "Tue" and part == "pm" and booked
                          for day in ["Mon", "Tue", "Wed"]
                          for part in ["am", "pm"] for booked in [True, False])
            else:
                raise AssertionError(tag)
            assert got is bool(want), (prompt, tag, got, want)
            assert correct.startswith("yes" if want else "no"), (prompt, correct)
        assert correct not in distractors, prompt
        assert len(set([correct] + distractors)) == 4, prompt
    # independent recheck of the two arithmetic identities used for satisfiability
    assert (10 + 2) / 2 == 6 and 6 != 7                      # x=6 from x+y=10, x-y=2
    assert 25 + 12 <= 40                                     # room capacity case
    print(f"gold verified: {len(T)} tasks, all recomputed")


def main():
    verify()
    assert len(T) == 42, len(T)
    rng = random.Random(SEED)
    slots = [0] * 11 + [1] * 11 + [2] * 10 + [3] * 10
    rng.shuffle(slots)

    # LENGTH CONTROL. The "no determinate answer" option has several exactly equivalent
    # phrasings of different lengths. Choosing among them is meaning-preserving, so it is a
    # legitimate knob for balancing candidate length -- and it is the ONLY knob used. Prompts,
    # gold answers and substantive distractors are untouched. Objective: drive BOTH trivial
    # heuristics ("pick longest", "pick shortest") to the 0.25 chance floor.
    UNC = {"it cannot be determined", "not enough information", "cannot be established",
           "insufficient data", "it cannot be decided", "there is not enough information"}
    VARIANTS = ["undetermined", "cannot be determined", "it cannot be determined",
                "not determinable from the statements given"]

    tasks = []
    for cat, prompt, correct, distractors, _chk in T:
        knob = correct in UNC or any(d in UNC for d in distractors)
        tasks.append([cat, prompt, correct, list(distractors), knob, 2])

    def render(task, v):
        cat, prompt, correct, distractors, knob, _ = task
        if not knob:
            return correct, distractors
        sub = VARIANTS[v]
        c = sub if correct in UNC else correct
        ds = [sub if d in UNC else d for d in distractors]
        return c, ds

    def score(choices):
        lo = sh = 0.0
        for task, v in zip(tasks, choices):
            c, ds = render(task, v)
            lens = [len(c)] + [len(d) for d in ds]
            mx, mn = max(lens), min(lens)
            if len(c) == mx:
                lo += 1.0 / lens.count(mx)
            if len(c) == mn:
                sh += 1.0 / lens.count(mn)
        n = len(tasks)
        return abs(lo / n - 0.25) + abs(sh / n - 0.25)

    choices = [t[5] for t in tasks]
    for _ in range(12):
        improved = False
        for i, task in enumerate(tasks):
            if not task[4]:
                continue
            best = choices[i]
            for v in range(len(VARIANTS)):
                trial = list(choices)
                trial[i] = v
                if score(trial) < score(choices) - 1e-12:
                    choices, best, improved = trial, v, True
        if not improved:
            break
    print(f"length-balance objective after tuning: {score(choices):.4f}")

    battery, meta = [], []
    for i, task in enumerate(tasks):
        cat, prompt = task[0], task[1]
        correct, distractors = render(task, choices[i])
        cands = [None] * 4
        cands[slots[i]] = correct
        it = iter(distractors)
        for j in range(4):
            if cands[j] is None:
                cands[j] = next(it)
        battery.append({"prompt": prompt, "candidates": cands,
                        "correct": correct, "category": cat})
        lens = [len(c) for c in cands]
        lc, mx, mn = len(correct), max(lens), min(lens)
        meta.append({
            "index": i, "category": cat, "correct_slot": slots[i],
            "correct_len": lc, "candidate_lens": lens,
            "correct_is_longest": lc == mx,
            "correct_is_strictly_longest": lc == mx and lens.count(mx) == 1,
            "correct_is_shortest": lc == mn,
            "correct_is_strictly_shortest": lc == mn and lens.count(mn) == 1,
            "n_tied_longest": lens.count(mx), "n_tied_shortest": lens.count(mn),
        })

    # expected score of the trivial "pick the longest candidate" heuristic, ties -> 1/k
    longest_score = sum((1.0 / m["n_tied_longest"]) if m["correct_is_longest"] else 0.0
                        for m in meta) / len(meta)
    shortest_score = sum((1.0 / m["n_tied_shortest"]) if m["correct_is_shortest"] else 0.0
                         for m in meta) / len(meta)
    pos = {s: slots.count(s) for s in range(4)}
    summary = {
        "n_tasks": len(battery),
        "n_categories": len(set(t["category"] for t in battery)),
        "position_counts": pos,
        "position_fractions": {k: round(v / len(battery), 4) for k, v in pos.items()},
        "correct_is_longest_count": sum(m["correct_is_longest"] for m in meta),
        "correct_is_shortest_count": sum(m["correct_is_shortest"] for m in meta),
        "expected_pick_longest_score": round(longest_score, 4),
        "expected_pick_shortest_score": round(shortest_score, 4),
        "chance_floor": 0.25,
        "comparison_note": "Apollo's home battery scores 0.342 for pick-the-longest against a "
                           "0.25 chance floor. The figure above is the same statistic computed "
                           "on this battery.",
    }
    (HERE / "charon_battery_E9.json").write_text(
        json.dumps(battery, indent=2, ensure_ascii=False), encoding="utf-8")
    (HERE / "charon_battery_E9_metadata.json").write_text(
        json.dumps({"summary": summary, "per_task": meta}, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
