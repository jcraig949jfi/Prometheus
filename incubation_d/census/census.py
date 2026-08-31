"""Meta-language census (spec sections 13-14).

Enumerates ALL typed Block->Block meta programs of a grammar candidate to the
preregistered horizon in shortlex canonical order, fingerprints them
structurally and object-semantically, audits edit shapes offline (human-side
only), and evaluates the preregistered kill gates.

Usage: python census.py <grammar_module>   e.g. python census.py grammar_v0
"""

import hashlib
import importlib
import json
import os
import sys
import time
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from vm.machine import (  # noqa: E402
    VMError, exec_meta, exec_object, ser, ser_instr, type_step,
)

PREREG = json.load(open(os.path.join(HERE, "prereg_census.json")))
HORIZON = PREREG["enumeration"]["horizon_L"]

PROBES = [tuple(p) for p in PREREG["probes"]["structural_probe_artifacts"]]
SEM_STACKS = [tuple(s) for s in PREREG["probes"]["semantic_probe_stacks"]]
CTRL_TOK = "o4"
PROBES_NO_CTRL = [p for p in PROBES if CTRL_TOK not in p]

CHEAP_WINDOW = 200
MAX_TEMPLATE_K = 6


# ---------- semantic fingerprinting ----------

def sem_of_artifact(block):
    out = []
    for st in SEM_STACKS:
        try:
            r = exec_object(block, st)
            out.append("(" + " ".join(ser(v) for v in r) + ")")
        except VMError as e:
            out.append("E%d" % e.code)
    return tuple(out)


SEM_INPUTS = [sem_of_artifact(p) for p in PROBES]


# ---------- offline shape audit (human-side only) ----------

def _flatten(b):
    """Recursive token stream of a block: descends into 'P' literals.

    A lit-push contributes a '#P' marker plus its content's tokens (or a
    '#<int>' marker for int literals). Protocol v1.1 repair: top-level
    multiset comparison misread quote-nesting as removal+introduction.
    """
    out = []
    for i in b:
        if isinstance(i, str):
            out.append(i)
        else:  # ('P', v)
            out.append("#P")
            v = i[1]
            if isinstance(v, tuple):
                out.extend(_flatten(v))
            else:
                out.append("#%d" % v)
    return out


def _instr_multiset(b):
    return Counter(_flatten(b))


def _is_subseq(needle, hay):
    it = iter(hay)
    return all(any(x == h for h in it) for x in needle)


def _restrict(seq_tokens, common):
    budget = dict(common)
    out = []
    for k in seq_tokens:
        if budget.get(k, 0) > 0:
            budget[k] -= 1
            out.append(k)
    return out


def classify(pairs):
    """pairs: list of (input_block, output_block), aligned with PROBES.

    Returns (shape, flags) where shape is a collapsed class and flags is a
    sorted tuple of behavior flags.
    """
    ins = [a for a, _ in pairs]
    outs = [b for _, b in pairs]

    # flags (protocol v1.1: recursive token streams; reorders = the input's
    # retained tokens no longer embed order-preservingly in the output)
    flags = set()
    for a, b in pairs:
        fa, fb = _flatten(a), _flatten(b)
        ma, mb = Counter(fa), Counter(fb)
        if any(mb[k] > ma.get(k, 0) for k in mb if k != "#P"):
            flags.add("introduces_tokens")
        if any(ma[k] > mb.get(k, 0) for k in ma if k != "#P"):
            flags.add("removes_tokens")
        common = {k: min(ma.get(k, 0), mb.get(k, 0)) for k in ma
                  if k != "#P"}
        if not _is_subseq(_restrict(fa, common), fb):
            flags.add("reorders")
        if mb.get("#P", 0) > ma.get("#P", 0):
            flags.add("introduces_lit")
    for p in PROBES_NO_CTRL:
        b = outs[PROBES.index(p)]
        if CTRL_TOK in _flatten(b):
            flags.add("introduces_control")
            break
    flags = tuple(sorted(flags))

    if all(a == b for a, b in pairs):
        return "identity", flags
    if len(set(outs)) == 1:
        return "constant", flags
    if all(b == (("P", a),) for a, b in pairs):
        return "quote", flags

    empty_out = outs[PROBES.index(())]

    s = empty_out
    if s and all(b == a + s for a, b in pairs):
        return "append", flags
    if s and all(b == s + a for a, b in pairs):
        return "prepend", flags
    if len(s) >= 2:
        for cut in range(1, len(s)):
            p, q = s[:cut], s[cut:]
            if all(b == p + a + q for a, b in pairs):
                return "wrap", flags
    if s:
        for k in range(1, MAX_TEMPLATE_K + 1):
            if all(b == a[:min(k, len(a))] + s + a[min(k, len(a)):]
                   for a, b in pairs):
                return "insert", flags
            if all(b == a[:max(0, len(a) - k)] + s + a[max(0, len(a) - k):]
                   for a, b in pairs):
                return "insert", flags
    for k in range(1, MAX_TEMPLATE_K + 1):
        if all(b == a[:min(k, len(a))] for a, b in pairs):
            return "take", flags
        if all(b == a[min(k, len(a)):] for a, b in pairs):
            return "dropfx", flags
    for a0 in range(0, MAX_TEMPLATE_K + 1):
        for d in range(1, MAX_TEMPLATE_K + 1):
            if all(b == a[:min(a0, len(a))] + a[min(a0 + d, len(a)):]
                   for a, b in pairs):
                if any(b != a for a, b in pairs):
                    return "delete", flags
    for n in range(2, 5):
        if all(b == a * n for a, b in pairs):
            return "selfcat", flags
    if all(len(b) == len(a) and
           sorted(ser_instr(i) for i in a) == sorted(ser_instr(i) for i in b)
           for a, b in pairs):
        return "perm", flags

    mix_flags = {"introduces_tokens", "removes_tokens", "reorders"}
    if len(mix_flags & set(flags)) >= 2:
        return "mixed", flags
    return "other", flags


def is_legacy(shape, flags):
    fams = set()
    if shape == "append":
        fams.add("append_like")
    if shape == "prepend":
        fams.add("pre_like")
    if shape == "wrap":
        fams.add("wrap_like")
    if "introduces_control" in flags:
        fams.add("route_like")
    return fams


# ---------- enumeration ----------

def run_census(grammar_module):
    gmod = importlib.import_module("meta_language.%s" % grammar_module)
    tokens = gmod.TOKENS
    spec_str = json.dumps(gmod.GRAMMAR_SPEC, sort_keys=True)
    grammar_hash = hashlib.sha256(spec_str.encode()).hexdigest()

    t0 = time.time()
    total_sequences = sum(len(tokens) ** l for l in range(1, HORIZON + 1))
    typed_sequences = 0        # prefixes that never crash the type checker
    valid_programs = 0         # typed with final stack exactly [B]
    runtime_failed = 0         # valid typed but VMError on some probe
    executed_ok = 0

    behaviors = {}             # structural fp -> record
    order = []                 # fps in rank order
    rank = 0

    level = [((), ("B",))]
    for length in range(1, HORIZON + 1):
        nxt = []
        for prefix, tstack in level:
            for tok in tokens:
                ts = type_step(tstack, tok)
                if ts is None:
                    continue
                typed_sequences += 1
                prog = prefix + (tok,)
                if ts == ("B",):
                    valid_programs += 1
                    pairs = []
                    try:
                        for p in PROBES:
                            st = exec_meta(prog, [p])
                            pairs.append((p, st[0]))
                    except VMError:
                        pairs = None
                    if pairs is None:
                        runtime_failed += 1
                    else:
                        executed_ok += 1
                        fp = hashlib.sha256(
                            "|".join(ser(b) for _, b in pairs).encode()
                        ).hexdigest()
                        if fp not in behaviors:
                            behaviors[fp] = {
                                "rank": rank,
                                "program": list(prog),
                                "length": length,
                                "pairs": pairs,
                            }
                            order.append(fp)
                        rank += 1
                if length < HORIZON:
                    nxt.append((prog, ts))
        level = nxt

    enum_secs = time.time() - t0

    # ---------- classify + semantics ----------
    t1 = time.time()
    sem_seen = set()
    n_noop = n_destructive = n_identity = 0
    for fp in order:
        rec = behaviors[fp]
        shape, flags = classify(rec["pairs"])
        rec["shape"], rec["flags"] = shape, flags
        rec["legacy"] = sorted(is_legacy(shape, flags))
        sem = tuple(sem_of_artifact(b) for _, b in rec["pairs"])
        sem_seen.add(sem)
        if shape == "identity":
            n_identity += 1
        elif sem == tuple(SEM_INPUTS):
            n_noop += 1
        if all(r.startswith("E") for grp in sem for r in grp):
            n_destructive += 1
        rec["sem_fp"] = hashlib.sha256(repr(sem).encode()).hexdigest()
    class_secs = time.time() - t1

    distinct_structural = len(order)
    distinct_semantic = len(sem_seen)

    # per-shape stats over ALL distinct behaviors
    shape_min_len = {}
    shape_counts = Counter()
    family_counts = Counter()
    n_mixed = 0
    for fp in order:
        rec = behaviors[fp]
        sh = rec["shape"]
        shape_counts[sh] += 1
        if sh not in shape_min_len or rec["length"] < shape_min_len[sh]:
            shape_min_len[sh] = rec["length"]
        for fam in rec["legacy"]:
            family_counts[fam] += 1
        if sh == "mixed":
            n_mixed += 1
    route_min_len = min(
        (behaviors[fp]["length"] for fp in order
         if "route_like" in behaviors[fp]["legacy"]), default=None)

    # cheap window: first CHEAP_WINDOW distinct non-identity, non-constant
    window = [fp for fp in order
              if behaviors[fp]["shape"] not in ("identity", "constant")
              ][:CHEAP_WINDOW]
    win_legacy = sum(1 for fp in window if behaviors[fp]["legacy"])
    win_shapes = sorted({behaviors[fp]["shape"] for fp in window})
    win_family = Counter()
    for fp in window:
        for fam in behaviors[fp]["legacy"]:
            win_family[fam] += 1
    legacy_shapes_present = sum(
        1 for s in ("append", "prepend", "wrap") if s in win_shapes)
    if any("route_like" in behaviors[fp]["legacy"] for fp in window):
        legacy_shapes_present += 1
    non_legacy_shapes = [s for s in win_shapes
                         if s not in ("append", "prepend", "wrap")]

    # ---------- gates ----------
    # CK1: single-token legacy realization
    ck1_hits = []
    for fp in order:
        rec = behaviors[fp]
        if rec["length"] == 1 and rec["legacy"]:
            ck1_hits.append(rec["program"])
    gates = {}
    gates["CK1_single_token_button"] = {
        "hits": ck1_hits, "kill": bool(ck1_hits)}

    win_share = win_legacy / len(window) if window else 1.0
    gates["CK2_cheap_region_share"] = {
        "window_size": len(window), "legacy_count": win_legacy,
        "legacy_share": round(win_share, 4), "threshold": 0.60,
        "per_family_in_window": dict(win_family),
        "kill": win_share > 0.60,
    }

    gates["CK3_shape_diversity_of_cheap_region"] = {
        "shapes_in_window": win_shapes,
        "n_shapes": len(win_shapes),
        "legacy_shapes_present": legacy_shapes_present,
        "non_legacy_shapes_present": len(non_legacy_shapes),
        "kill": (len(win_shapes) < 12) or (
            len(non_legacy_shapes) < 2 * legacy_shapes_present),
    }

    nontrivial = {s: l for s, l in shape_min_len.items()
                  if s not in ("identity", "constant")}
    if route_min_len is not None:
        nontrivial["route_like"] = route_min_len
    med_pool = sorted(nontrivial.values())
    median_min = (med_pool[len(med_pool) // 2] if med_pool else None)
    legacy_min = {f: None for f in
                  ("append", "prepend", "wrap", "route_like")}
    for f in list(legacy_min):
        legacy_min[f] = nontrivial.get(f)
    ck4_kill = any(v is not None and median_min is not None
                   and v <= median_min - 2 for v in legacy_min.values())
    gates["CK4_relative_cheapness"] = {
        "shape_min_lengths": nontrivial, "median_min_length": median_min,
        "legacy_min_lengths": legacy_min, "kill": ck4_kill,
    }

    need = ["append", "prepend", "wrap", "insert", "selfcat", "perm", "mixed"]
    missing = [s for s in need if shape_counts.get(s, 0) == 0]
    if not any(shape_counts.get(s, 0) for s in ("take", "dropfx", "delete")):
        missing.append("take|dropfx|delete")
    if route_min_len is None:
        missing.append("route_like")
    gates["CK5_reachability"] = {"missing": missing, "kill": bool(missing)}

    distinct_ratio = (distinct_structural / executed_ok
                      if executed_ok else 0.0)
    gates["CK6_diversity_floors"] = {
        "distinct_structural": distinct_structural,
        "executed_ok": executed_ok,
        "distinct_ratio": round(distinct_ratio, 5),
        "distinct_semantic": distinct_semantic,
        "kill": (distinct_ratio < 0.03 or distinct_structural < 500
                 or distinct_semantic < 300),
    }

    non_id = distinct_structural - n_identity
    mixed_density = n_mixed / non_id if non_id else 0.0
    gates["CK7_mixed_density"] = {
        "mixed": n_mixed, "distinct_non_identity": non_id,
        "density": round(mixed_density, 5), "kill": mixed_density < 0.01,
    }

    kills = [k for k, v in gates.items() if v["kill"]]
    leakage = [k for k in kills if k in
               ("CK1_single_token_button", "CK2_cheap_region_share",
                "CK4_relative_cheapness")]
    if not kills:
        verdict = "GRAMMAR_PASSED_CENSUS"
    elif leakage:
        verdict = "GRAMMAR_REJECTED_LEAKAGE"
    else:
        verdict = "GRAMMAR_REJECTED_POVERTY"

    result = {
        "grammar": gmod.GRAMMAR_ID,
        "grammar_hash": grammar_hash,
        "horizon_L": HORIZON,
        "counts": {
            "total_sequences": total_sequences,
            "typed_sequences": typed_sequences,
            "valid_programs": valid_programs,
            "runtime_failed": runtime_failed,
            "executed_ok": executed_ok,
            "distinct_structural": distinct_structural,
            "distinct_semantic": distinct_semantic,
            "identity": n_identity,
            "noop_semantic": n_noop,
            "destructive": n_destructive,
            "mixed": n_mixed,
        },
        "shape_counts": dict(shape_counts),
        "family_counts": dict(family_counts),
        "shape_min_lengths": shape_min_len,
        "route_like_min_length": route_min_len,
        "per_length_new_behaviors": _per_length(behaviors, order),
        "gates": gates,
        "kills": kills,
        "verdict": verdict,
        "timing": {"enumeration_s": round(enum_secs, 1),
                   "classification_s": round(class_secs, 1)},
        "audit_head": [
            {"rank": behaviors[fp]["rank"],
             "program": behaviors[fp]["program"],
             "shape": behaviors[fp]["shape"],
             "flags": list(behaviors[fp]["flags"]),
             "legacy": behaviors[fp]["legacy"],
             "out_on_P3": ser(behaviors[fp]["pairs"][3][1])}
            for fp in order[:60]
        ],
    }
    return result


def _per_length(behaviors, order):
    c = Counter(behaviors[fp]["length"] for fp in order)
    return {str(k): c[k] for k in sorted(c)}


if __name__ == "__main__":
    gm = sys.argv[1] if len(sys.argv) > 1 else "grammar_v0"
    res = run_census(gm)
    out = os.path.join(ROOT, "results", "census_%s.json" % res["grammar"])
    with open(out, "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps({k: res[k] for k in
                      ("grammar", "counts", "shape_counts", "family_counts",
                       "kills", "verdict", "timing")}, indent=1))
    print("written:", out)
