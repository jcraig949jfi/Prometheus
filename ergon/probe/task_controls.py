"""Non-LLM controls on the TASK family. No API calls, no sampling of a model, $0.

The probe's existing controls are LLM-scored (does a solver do better with X than Y) or
classifier-based (can a model separate the arms). Both are inference. The checks here are
computations over the manifest and the rendered packets, and several of them are decidable.

Each control states which failure it exists to catch and which DIRECTION its failure pushes
relative to the hypothesis — because a confound that pushes toward the hypothesis is the
dangerous kind, and this probe has already shipped two that did.

    python ergon/probe/task_controls.py
"""
import collections
import json
import math
import pathlib
import random
import re
import statistics
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

METHOD_VOCAB = ["trial-division", "fermat-test", "miller-rabin", "sqrt-bound",
                "parity-or-last-digit", "digit-sum-rule", "modular-arithmetic",
                "factorization-attempt"]
_INTS = re.compile(r"\((?:[1-5])\)\s+(\d+)")


def parse_task(row):
    return [int(x) for x in _INTS.findall(row["prompt"])]


# ---------------------------------------------------------------- C1: well-posedness

def deterministic_solver(rows):
    """A program must recover the gold from the PROMPT TEXT alone, exactly.

    Catches: mis-posed tasks, wrong gold, ambiguous prompt parsing. If this is not 1.0000,
    no LLM number computed on this manifest means anything.
    """
    from ergon.probe.task_gen_v3 import is_prime
    bad = []
    for r in rows:
        ns = parse_task(r)
        if len(ns) != 5:
            bad.append((r["uid"], f"parsed {len(ns)} integers"))
            continue
        got = sum(1 for n in ns if is_prime(n))
        if got != r["gold_int"]:
            bad.append((r["uid"], f"computed {got} vs gold {r['gold_int']}"))
    return {"agreement": (len(rows) - len(bad)) / max(1, len(rows)),
            "disagreements": bad[:5], "n": len(rows)}


# ---------------------------------------------------------------- C2: surface shortcuts

def _cv_lookup(pairs, folds=5, seed=0):
    """Cross-validated majority-class lookup. NOT fit-and-score-on-the-same-rows: a lookup
    table over few cells memorizes, and the naive number on this family read 0.40 where the
    honest one reads 0.29."""
    d = list(pairs)
    random.Random(seed).shuffle(d)
    maj = collections.Counter(g for _, g in d).most_common(1)[0][0]
    accs = []
    for f in range(folds):
        test = d[f::folds]
        train = [x for i, x in enumerate(d) if i % folds != f]
        tab = collections.defaultdict(collections.Counter)
        for k, g in train:
            tab[k][g] += 1
        pred = {k: c.most_common(1)[0][0] for k, c in tab.items()}
        accs.append(sum(1 for k, g in test if pred.get(k, maj) == g) / max(1, len(test)))
    return sum(accs) / len(accs)


def _perm_null(pairs, trials=200):
    keys = [k for k, _ in pairs]
    labels = [g for _, g in pairs]
    out = []
    for s in range(trials):
        lab = list(labels)
        random.Random(s).shuffle(lab)
        out.append(_cv_lookup(list(zip(keys, lab)), seed=s))
    out.sort()
    return {"mean": sum(out) / len(out), "p95": out[int(0.95 * len(out))]}


SURFACE = {
    "coprime_to_30": lambda ns: sum(1 for n in ns if all(n % p for p in (2, 3, 5))),
    "count_odd": lambda ns: sum(1 for n in ns if n % 2),
    "endings_1379": lambda ns: sum(1 for n in ns if n % 10 in (1, 3, 7, 9)),
    "max_digit_len": lambda ns: max(len(str(n)) for n in ns),
}


def surface_shortcuts(rows, fresh_rows=None):
    """How well can the answer be predicted WITHOUT doing any primality work?

    Catches: a task family whose answer is readable off trivial arithmetic. This sets the
    real *attainable-without-reasoning* floor, which is NOT the chance floor the band was
    reasoned against.

    DIRECTION: a high floor inflates any residue effect that merely reminds the solver of a
    trivial procedure — i.e. it pushes TOWARD the hypothesis.
    """
    tasks = [(parse_task(r), r["gold_int"]) for r in rows]
    tasks = [(ns, g) for ns, g in tasks if len(ns) == 5]
    chance = max(collections.Counter(g for _, g in tasks).values()) / len(tasks)
    out = {"chance_majority_class": round(chance, 4), "n": len(tasks), "features": {}}
    for name, f in SURFACE.items():
        pairs = [(f(ns), g) for ns, g in tasks]
        entry = {"cv_accuracy": round(_cv_lookup(pairs), 4)}
        if fresh_rows:
            ft = [(parse_task(r), r["gold_int"]) for r in fresh_rows]
            ft = [(ns, g) for ns, g in ft if len(ns) == 5]
            tab = collections.defaultdict(collections.Counter)
            for ns, g in tasks:
                tab[f(ns)][g] += 1
            maj = collections.Counter(g for _, g in tasks).most_common(1)[0][0]
            pred = {k: c.most_common(1)[0][0] for k, c in tab.items()}
            entry["held_out_fresh_seed"] = round(
                sum(1 for ns, g in ft if pred.get(f(ns), maj) == g) / len(ft), 4)
            entry["fresh_n"] = len(ft)
        out["features"][name] = entry
    return out


# ---------------------------------------------------------------- C3: uid decorrelation

def uid_decorrelation(rows):
    """The v1 defect was a manifest whose INDEX predicted the answer at 0.921. The generator
    now enforces decorrelation; this verifies it independently of the generator's own guard.

    A guard that is only checked by the code that implements it is not checked.
    """
    idx = [(int(r["uid"].rsplit("-", 1)[1]), r["gold_int"]) for r in rows]
    xs = [a for a, _ in idx]
    ys = [b for _, b in idx]
    mx, my = statistics.mean(xs), statistics.mean(ys)
    den = math.sqrt(sum((a - mx) ** 2 for a in xs) * sum((b - my) ** 2 for b in ys))
    r = (sum((a - mx) * (b - my) for a, b in idx) / den) if den else 0.0
    return {"pearson_r": round(r, 4), "abs_r_under_0_1": abs(r) < 0.1}


# ---------------------------------------------------------------- C4: residue channel

def residue_answer_channel(rows, gold, arms):
    """Does the D0 residue packet predict the answer, with NO reasoning?

    Catches: the leak the whole redaction/projection design exists to prevent. Scored
    cross-validated against a PERMUTATION NULL, because a lookup table over 19 cells and 200
    rows reads 0.40 naively and 0.29 honestly.

    DIRECTION: F-prom carries THIS task's residue and F-null another task's, so any real
    channel here inflates Delta_carry — toward the hypothesis.
    """
    pairs = []
    for r in rows:
        body = arms.prom_body(r["uid"]).lower()
        pairs.append((tuple(sorted(v for v in METHOD_VOCAB if v in body)), gold[r["uid"]]))
    cv = _cv_lookup(pairs)
    null = _perm_null(pairs)
    return {"cv_accuracy": round(cv, 4),
            "permutation_null_mean": round(null["mean"], 4),
            "permutation_null_p95": round(null["p95"], 4),
            "distinct_packets": len(set(k for k, _ in pairs)),
            "channel_detected": cv > null["p95"]}


def main():
    from ergon.probe.task_gen_v3 import generate
    import ergon.probe.campaign as C

    rows = C.manifest()
    gold = {r["uid"]: r["gold_int"] for r in rows}
    fresh = generate("M30", 400, 987654)          # same generator, different seed

    res = {
        "C1_well_posedness": deterministic_solver(rows),
        "C2_surface_shortcuts": surface_shortcuts(rows, fresh),
        "C3_uid_decorrelation": uid_decorrelation(rows),
    }
    try:
        arms = C.Arms(rows, gold)
        res["C4_residue_answer_channel"] = residue_answer_channel(rows, gold, arms)
    except Exception as e:                        # no prepass pool yet
        res["C4_residue_answer_channel"] = {"skipped": f"{type(e).__name__}: {e}"}

    out = ROOT / "ergon/probe/ledgers/task_controls"
    out.mkdir(parents=True, exist_ok=True)
    (out / "controls.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    print(json.dumps(res, indent=2)[:2400])
    return 0


if __name__ == "__main__":
    sys.exit(main())
