"""gen_clean_canary_v01.py — generate the 50-task clean canary suite.

Designed to buffer Gemini's Q6 concern: the existing trap battery has a
"longest candidate" Goodhart hole at 52%. Branch C running against the
unaudited battery would breed length-maximizers.

Design principles for this canary:
  1. Each task has 4 candidates. Candidate lengths are deliberately
     equalized OR adversarially inverted (correct answer is the shortest)
     so the longest-candidate heuristic scores at chance or worse.
  2. Candidate order is randomized per-task so candidate-position is not
     predictive.
  3. Categories drawn from the Frame H primitive families our prototype
     can actually reason about (numeric, transitivity, simple logic,
     temporal, vacuous truth, all-but-n).
  4. Correct answers are unambiguous and machine-verifiable.

Writes apollo/data/clean_canary_v01.json. Idempotent (deterministic seed).

Usage:
    python gen_clean_canary_v01.py
"""
import json
import random
from pathlib import Path
from typing import Callable


RNG = random.Random(20260527)


def _pad_to_length(s: str, target_len: int) -> str:
    """Pad a candidate string to a target length by appending uninformative
    suffix tokens. Preserves first-token semantics."""
    if len(s) >= target_len:
        return s
    fillers = [" exactly", " precisely", " as stated", " by definition",
               " in this case", " unambiguously", " specifically"]
    out = s
    while len(out) < target_len:
        out += RNG.choice(fillers)
        if len(out) > target_len + 10:
            break
    return out[:target_len].rstrip()


def _equalize_lengths(candidates: list[str], target_len: int = None) -> list[str]:
    """Pad all candidates to the same approximate length so length is not
    a discriminative feature."""
    if target_len is None:
        target_len = max(len(c) for c in candidates) + RNG.randint(3, 12)
    return [_pad_to_length(c, target_len) for c in candidates]


def _shuffle(candidates: list[str], correct: str) -> tuple[list[str], str]:
    """Randomize candidate order; return (shuffled_candidates, correct)."""
    pairs = list(enumerate(candidates))
    RNG.shuffle(pairs)
    new_candidates = [c for _, c in pairs]
    return new_candidates, correct


# ── Per-category generators ───────────────────────────────────────────


def gen_numeric_comparison() -> dict:
    """'Is X larger than Y?' with length-equalized Yes/No candidates."""
    a = round(RNG.uniform(0.1, 100), 2)
    b = round(RNG.uniform(0.1, 100), 2)
    while abs(a - b) < 0.5:
        b = round(RNG.uniform(0.1, 100), 2)
    prompt = f"Is {a} larger than {b}?"
    correct = "Yes" if a > b else "No"
    raw_candidates = ["Yes", "No", "Cannot be determined", "Insufficient information"]
    # Length-equalize — Yes/No are short; pad them
    candidates = _equalize_lengths(raw_candidates, target_len=30)
    # Map correct to its padded version
    correct_padded = candidates[raw_candidates.index(correct)]
    candidates, correct_padded = _shuffle(candidates, correct_padded)
    return {
        "category": "numeric_comparison",
        "prompt": prompt,
        "candidates": candidates,
        "correct": correct_padded,
    }


def gen_numeric_stated_premise() -> dict:
    """'X is less than Y. Which is larger?' candidates are the two numbers."""
    a = round(RNG.uniform(1, 100), 2)
    b = round(RNG.uniform(1, 100), 2)
    while abs(a - b) < 0.5:
        b = round(RNG.uniform(1, 100), 2)
    lo, hi = (a, b) if a < b else (b, a)
    prompt = f"{lo} is less than {hi}. Which number is larger?"
    correct = str(hi)
    # Length-equalize: pad the two numeric candidates + add distractors
    raw = [str(lo), str(hi), "They are equal", "Cannot be determined"]
    candidates = _equalize_lengths(raw, target_len=30)
    correct_padded = candidates[raw.index(correct)]
    candidates, correct_padded = _shuffle(candidates, correct_padded)
    return {
        "category": "numeric_stated_premise",
        "prompt": prompt,
        "candidates": candidates,
        "correct": correct_padded,
    }


_NAMES = ["Alice", "Bob", "Carol", "Dave", "Eve", "Frank", "Grace", "Hank"]


def gen_transitivity() -> dict:
    """3-5 entities in a chain; ask who is tallest. Length-balanced."""
    n = RNG.choice([3, 4, 5])
    names = RNG.sample(_NAMES, n)
    # Build a chain: names[0] > names[1] > ... > names[-1]
    # The tallest is names[0]. We will randomize the order of stated
    # relations and which question is asked so position is not predictive.
    relations = []
    for i in range(n - 1):
        relations.append((names[i], names[i + 1]))
    RNG.shuffle(relations)
    parts = [f"{a} is taller than {b}" for a, b in relations]
    prompt = ", and ".join(parts) + ". Who is tallest?"
    correct = names[0]
    # Candidates are 4 distinct names; pad lengths
    raw = list(set([names[0], names[-1], names[len(names) // 2]]))
    extras = [n for n in _NAMES if n not in raw]
    while len(raw) < 4:
        raw.append(extras.pop(0))
    raw = raw[:4]
    if correct not in raw:
        raw[0] = correct
    candidates = _equalize_lengths(raw, target_len=15)
    correct_padded = candidates[raw.index(correct)]
    candidates, correct_padded = _shuffle(candidates, correct_padded)
    return {
        "category": "transitivity",
        "prompt": prompt,
        "candidates": candidates,
        "correct": correct_padded,
    }


def gen_all_but_n() -> dict:
    """'I have 10 apples. I give away 3. How many remain?'"""
    total = RNG.randint(5, 50)
    given = RNG.randint(1, total - 1)
    remain = total - given
    prompt = f"There were {total} items. {given} were removed. How many remain?"
    correct = str(remain)
    # Distractors: total, given, remain+1, remain-1 with length equalization
    distractors = list({str(total), str(given), str(remain + 1), str(remain - 1)} - {correct})
    raw = [correct] + distractors[:3]
    candidates = _equalize_lengths(raw, target_len=20)
    correct_padded = candidates[raw.index(correct)]
    candidates, correct_padded = _shuffle(candidates, correct_padded)
    return {
        "category": "all_but_n",
        "prompt": prompt,
        "candidates": candidates,
        "correct": correct_padded,
    }


def gen_temporal_ordering() -> dict:
    """'A happened before B. B happened before C. What happened first?'"""
    n = RNG.choice([3, 4])
    events = RNG.sample(["dawn", "noon", "dusk", "midnight", "sunrise", "sunset",
                         "tea time", "lunchtime"], n)
    parts = [f"{events[i]} happened before {events[i+1]}" for i in range(n - 1)]
    RNG.shuffle(parts)
    prompt = ", and ".join(parts) + ". What happened first?"
    correct = events[0]
    raw = events[:4] if len(events) >= 4 else events + ["nothing"]
    raw = raw[:4]
    if correct not in raw:
        raw[0] = correct
    candidates = _equalize_lengths(raw, target_len=18)
    correct_padded = candidates[raw.index(correct)]
    candidates, correct_padded = _shuffle(candidates, correct_padded)
    return {
        "category": "temporal_ordering",
        "prompt": prompt,
        "candidates": candidates,
        "correct": correct_padded,
    }


def gen_vacuous_truth() -> dict:
    """'All unicorns have horns. Is the statement true?' with reasoning."""
    statements_correct = [
        ("All unicorns have horns. Is this true by definition?", "Yes"),
        ("If there are no flying pigs, are all flying pigs pink?", "Yes"),
        ("Every element of the empty set is even. True?", "Yes"),
    ]
    s, correct = RNG.choice(statements_correct)
    raw = ["Yes", "No", "Depends on context", "Cannot be determined"]
    candidates = _equalize_lengths(raw, target_len=30)
    correct_padded = candidates[raw.index(correct)]
    candidates, correct_padded = _shuffle(candidates, correct_padded)
    return {
        "category": "vacuous_truth",
        "prompt": s,
        "candidates": candidates,
        "correct": correct_padded,
    }


def gen_consistency_check() -> dict:
    """A small constraint-consistency task. 'A > B and B > C and C > A. Consistent?'
    Half the time consistent, half inconsistent."""
    if RNG.random() < 0.5:
        # Inconsistent cycle
        chain = "A is taller than B, B is taller than C, and C is taller than A. Are these consistent?"
        correct = "No"
    else:
        # Consistent
        chain = "A is taller than B, B is taller than C, and A is taller than C. Are these consistent?"
        correct = "Yes"
    raw = ["Yes", "No", "Cannot be determined", "Depends on interpretation"]
    candidates = _equalize_lengths(raw, target_len=30)
    correct_padded = candidates[raw.index(correct)]
    candidates, correct_padded = _shuffle(candidates, correct_padded)
    return {
        "category": "consistency_check",
        "prompt": chain,
        "candidates": candidates,
        "correct": correct_padded,
    }


# ── Suite assembly ────────────────────────────────────────────────────


CATEGORIES = [
    (gen_numeric_comparison, 10),
    (gen_numeric_stated_premise, 10),
    (gen_transitivity, 10),
    (gen_all_but_n, 5),
    (gen_temporal_ordering, 5),
    (gen_vacuous_truth, 5),
    (gen_consistency_check, 5),
]


def main():
    tasks = []
    for gen_fn, n in CATEGORIES:
        for _ in range(n):
            tasks.append(gen_fn())

    # Length-balance audit: per task, what's the length difference between
    # the correct answer and the longest candidate? If correct is the
    # longest, that's a length-exploit risk.
    n_longest_is_correct = 0
    n_shortest_is_correct = 0
    for t in tasks:
        lens = [len(c) for c in t["candidates"]]
        max_len = max(lens)
        min_len = min(lens)
        c_len = len(t["correct"])
        if c_len == max_len and max_len != min_len:
            n_longest_is_correct += 1
        if c_len == min_len and max_len != min_len:
            n_shortest_is_correct += 1

    out_path = Path(__file__).parent.parent / "data" / "clean_canary_v01.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out = {
        "version": "v01",
        "n_tasks": len(tasks),
        "by_category": {c: n for c, n in [(g.__name__.replace("gen_", ""), n) for g, n in CATEGORIES]},
        "audit": {
            "n_tasks_where_longest_is_correct": n_longest_is_correct,
            "n_tasks_where_shortest_is_correct": n_shortest_is_correct,
            "longest_candidate_chance_rate": round(n_longest_is_correct / max(len(tasks), 1), 3),
            "shortest_candidate_chance_rate": round(n_shortest_is_correct / max(len(tasks), 1), 3),
        },
        "tasks": tasks,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print(f"Wrote {len(tasks)} tasks to {out_path}")
    print(f"  by category: {out['by_category']}")
    print(f"  audit: longest-is-correct on {n_longest_is_correct}/{len(tasks)} tasks ({n_longest_is_correct/len(tasks):.1%})")
    print(f"         shortest-is-correct on {n_shortest_is_correct}/{len(tasks)} tasks ({n_shortest_is_correct/len(tasks):.1%})")
    print(f"  failure-signature reading on length-balancing:")
    if n_longest_is_correct / len(tasks) <= 0.30:
        print(f"    SIGNATURE_OK: longest-candidate hack would score ≤30% on this canary")
    else:
        print(f"    SIGNATURE_LENGTH_BIAS: longest-candidate could score >30%; re-balancing needed")


if __name__ == "__main__":
    main()
