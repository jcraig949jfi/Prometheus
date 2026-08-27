"""mine.py — concept-candidate mining from the solver's own solved episodes.

Input: (boundary, solution_word) pairs from tasks the solver actually solved. Contiguous
n-grams (2..4) of the solutions are grouped by FUNCTION, not by syntax: two n-grams are
one candidate iff executing them from every probe state (the episodes' own start states,
through their own boundaries) yields identical results. Execution used for
fingerprinting is counted (discovery is not free).

Score = support * (len - 1): support is the number of episodes whose solution contains a
group member; (len - 1) is the composition-depth the group saves if reified. Candidates
below min_support_frac are rejected (no live consumers). The top group's shortest,
lexicographically-least member is emitted as the candidate word.

The miner sees only solver-side objects. It has no access to witnesses, worlds, or the
diagnostics module.
"""
from __future__ import annotations


def _ngrams(word, lo=2, hi=4):
    for n in range(lo, hi + 1):
        for i in range(len(word) - n + 1):
            yield tuple(word[i:i + n])


def fingerprint(word, episodes):
    out = []
    for bnd, _sol in episodes:
        v, fail = bnd.run_word(word, bnd.start)
        out.append(("FAIL", fail) if v is None else v)
    return tuple(out)


def mine(episodes, min_support_frac=0.25):
    """episodes: list of (boundary, solution_word). Returns (candidate_word, report)."""
    support = {}
    for idx, (_bnd, sol) in enumerate(episodes):
        for g in set(_ngrams(sol)):
            support.setdefault(g, set()).add(idx)
    min_support = max(2, int(min_support_frac * len(episodes)))
    groups = {}
    for g, tasks in sorted(support.items()):
        if len(tasks) < min_support:
            continue
        fp = fingerprint(g, episodes)
        entry = groups.setdefault(fp, {"members": [], "tasks": set()})
        entry["members"].append(g)
        entry["tasks"] |= tasks
    scored = []
    for fp, entry in groups.items():
        rep = min(entry["members"], key=lambda w: (len(w), w))
        score = len(entry["tasks"]) * (len(rep) - 1)
        scored.append({"word": rep, "support": len(entry["tasks"]),
                       "score": score, "n_members": len(entry["members"])})
    scored.sort(key=lambda r: (-r["score"], len(r["word"]), r["word"]))
    report = {"n_episodes": len(episodes), "min_support": min_support,
              "n_groups": len(scored), "top10": [
                  {**r, "word": list(r["word"])} for r in scored[:10]]}
    return (tuple(scored[0]["word"]) if scored else None), report
