"""BETA-03 E2: g12 -- ENDPOINT-ALIGNED ACCEPTANCE RULE (+ trap controls). Design: beta02/E4_DESIGN.md s3.

This module is new code only. It never edits an engine file. It plugs into gtc.donor_g through the same per-job patch
pattern as b02._set_rule: it replaces a17.select for the duration of ONE donor job and restores it in a `finally`.

THE RULE (all parameters are module constants below; they are to be frozen by the coordinator):
  1. VALIDATE (12 families at O10) is split into two seeded folds of 6. Seeding string FOLD_TAG % seed.
  2. Each candidate library C is walked on every VALIDATE cell that the donor builds (a17.R_VAL = 4 per family) to
     SEL_CAP charges, with walk.first_qualified and the T4-v1a tribunal (DIRECT, every positive confirmed through
     ARTIFACT). reach_f(C) = 1 iff, in >= 1 cell of family f, C reaches a qualified program AND INHERITED is
     censored in that same cell. This is the transfer endpoint's per-cell rule (b02._gains), moved onto validation.
  3. S(C) = min(reach_fold1, reach_fold2) - LAMBDA * DL(C). DL is the description length of the entries that C adds to
     INHERITED (see description_length()).
  4. C is eligible iff C != INHERITED, S(C) > 0, and every reached program passes the tribunal. The choice is
     max S; ties go to the larger total qualified-walk charge saving, then the smaller sha256. If nothing is eligible,
     the choice is INHERITED.
  5. Content-freedom: the rule reads no family labels, no schema text, and no candidate names (apart from the
     reference key INHERITED, which every selector shares). test_g12 checks this by renaming candidates.

TRAPS (planted candidates, scored by the same rule; each must NOT be chosen):
  PLANT_OFF   the gtc NULL plant: a17.schema_entry("g2_new", gtc.OFF_SCHEMA) + start (identical entries to gtc NULL).
  PLANT_MEMO  memorised library: one entry per distinct observed fold program (exact init, body and final). This is a
              second, stricter memoriser beside the natural MEMORISE candidate (which the rule never names).
  PLANT_NEAR  near-miss shortcut: the donor's best-supported derived schema (max LGG n_pairs; ties to the schema text)
              with its ROOT operator replaced by a different primitive (engine.PRIMITIVES), chosen by a seeded rng
              (NEAR_TAG % seed). It must instantiate >= 2 in-space bodies, and it must not be literally or
              extensionally equal (ruler v2.1) to any derived schema. It uses no transfer outcome and no validation
              outcome.
Every candidate's score depends only on (C, INHERITED, cells, folds). So ONE joint job scores the natural candidates and
all plants once, and the per-arm choices g12 / NULL12 / MEMO12 / NEAR12 are argmaxes over subsets of the same table
(arm_choice). test_g12 checks that this equals running each arm separately.
"""
import os
os.environ.setdefault("V2B_T51_DIR", "T04_T51")
import hashlib  # noqa: E402
import json  # noqa: E402
import random  # noqa: E402
import time  # noqa: E402

import paths  # noqa: E402,F401
import a17  # noqa: E402
import gtc  # noqa: E402
import walk  # noqa: E402
import instruments as INS  # noqa: E402
import identity as I  # noqa: E402
from a18 import FR, G, T3D  # noqa: E402

# ------------------------------------------------------------------ FROZEN-CANDIDATE PARAMETERS (E4 s3)
LAMBDA = 0.25                                   # per description-length unit ("entry")
FOLD_TAG = "APHRODITE/B03/G12/FOLDS/%d"         # % donor seed
NEAR_TAG = "APHRODITE/B03/G12/NEARMISS/%d"      # % donor seed
N_FOLDS = 2
SEL_CAP = 100_000                               # selection walk cap (charges); transfer cap stays 1M
CELLS_PER_FAMILY = None                         # None = every VALIDATE cell the donor builds (a17.R_VAL)
TRIBUNAL = ("v1a", "BOTH")
MAX_SPURIOUS = 10_000                           # walk.first_qualified default (unchanged)
FALLBACK = None                                 # E4 s5 fallback ("min >= 1 OR total >= 3") NOT enabled
TIE_BREAK = "max S, then max total qualified-walk charge saving vs INHERITED (censored = cap), then min sha256"
REF = "INHERITED"
PLANTS = ("PLANT_OFF", "PLANT_MEMO", "PLANT_NEAR")
ARMS = {"g12": (), "NULL12": ("PLANT_OFF",), "MEMO12": ("PLANT_MEMO",), "NEAR12": ("PLANT_NEAR",),
        "ALL12": PLANTS}
DIAG_I0 = True                                  # also record the I_0 (a17.select) table on the same candidates

# ------------------------------------------------------------------ description length
_H1, _FIN = frozenset(G.H1_SPACE), frozenset(G.FINAL_SPACE)


def _canon(e):
    return json.dumps({"inits": sorted(set(e.get("inits", []))), "bodies": sorted(FR.entry_bodies(e)),
                       "finals": sorted(set(e.get("finals", [])))}, sort_keys=True)


def entry_dl(e):
    """Number of irreducible items an entry STATES. A body generator costs 1: one schema template (key 'schema'), one
    per template in 'schemas', or, when the entry has no template, one per explicitly listed body. inits/finals cost 0
    when they are the full default space (nothing is stated), else 1 per listed item."""
    if e.get("schemas"):
        gen = len(e["schemas"])
    elif e.get("schema"):
        gen = 1
    else:
        gen = len(set(e.get("bodies") or []))
    ini = 0 if frozenset(e.get("inits", [])) == _H1 else len(set(e.get("inits", [])))
    fin = 0 if frozenset(e.get("finals", [])) == _FIN else len(set(e.get("finals", [])))
    return gen + ini + fin


def description_length(entries, start):
    """DL(C) = sum of entry_dl over the entries C adds to INHERITED (multiset difference on walked content).
    Entries C drops cost 0. A memorised entry that lists k concrete bodies costs k; a schema costs 1."""
    pool = {}
    for e in start:
        pool[_canon(e)] = pool.get(_canon(e), 0) + 1
    dl = 0
    for e in entries:
        k = _canon(e)
        if pool.get(k, 0) > 0:
            pool[k] -= 1
        else:
            dl += entry_dl(e)
    return dl


# ------------------------------------------------------------------ folds
def folds(families, seed):
    fams = sorted(set(families))
    rng = random.Random(I._seed(FOLD_TAG % seed))
    rng.shuffle(fams)
    h = (len(fams) + 1) // 2
    return [sorted(fams[:h]), sorted(fams[h:])]


# ------------------------------------------------------------------ the rule on a candidate table (pure; unit-tested)
def score_row(reach_by_fold, dl, all_qualified=True, saving=0, sha="", is_ref=False):
    m = min(reach_by_fold) if reach_by_fold else 0
    S = m - LAMBDA * dl
    if FALLBACK == "min1_or_total3":
        ok = m >= 1 or sum(reach_by_fold) >= 3
        S = max(m, 1 if ok else 0) - LAMBDA * dl
    return {"reach_by_fold": list(reach_by_fold), "reach_min": m, "reach_total": sum(reach_by_fold), "DL": dl,
            "S": round(S, 6), "saving": saving, "sha256": sha, "all_reached_qualified": bool(all_qualified),
            "eligible": (not is_ref) and S > 0 and bool(all_qualified)}


def choose(table, names=None):
    """table: name -> score_row. Max S, then max saving, then min sha; INHERITED if none eligible."""
    names = list(table) if names is None else [n for n in names if n in table]
    el = [n for n in names if n != REF and table[n]["eligible"]]
    if not el:
        return REF
    return min(el, key=lambda n: (-table[n]["S"], -table[n]["saving"], table[n]["sha256"]))


def arm_choice(table, arm):
    plants = ARMS[arm]
    return choose(table, [n for n in table if (not n.startswith("PLANT_")) or n in plants])


# ------------------------------------------------------------------ trap generators
def _split_args(s):
    depth, parts, cur = 0, [], ""
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(cur.strip())
            cur = ""
        else:
            cur += ch
    parts.append(cur.strip())
    return parts


def _matched(s):
    if not (s.startswith("(") and s.endswith(")")):
        return False
    d = 0
    for i, ch in enumerate(s):
        d += ch == "("
        d -= ch == ")"
        if d == 0 and i < len(s) - 1:
            return False
    return True


def root_split(schema):
    """(primitive, A, B) of the schema's root operator, or None for an atom."""
    s = schema.strip()
    if s.startswith("math.gcd(") and s.endswith(")"):
        p = _split_args(s[len("math.gcd("):-1])
        if len(p) == 2 and all(x.startswith("abs(") and x.endswith(")") for x in p):
            return "gcd", p[0][4:-1], p[1][4:-1]
        return None
    if s.startswith("pow(") and s.endswith(")"):
        p = _split_args(s[4:-1])
        return ("powr", p[0], p[1]) if len(p) == 2 else None
    if _matched(s):
        inner, depth = s[1:-1], 0
        for i, ch in enumerate(inner):
            depth += ch == "("
            depth -= ch == ")"
            if depth == 0:
                for name, op in (("add", " + "), ("sub", " - "), ("mul", " * "), ("fdiv", " // "), ("mod", " % ")):
                    if inner.startswith(op, i):
                        return name, inner[:i], inner[i + len(op):]
    return None


def near_miss(derived, seed):
    """derived: T3D.derive_schemas output (dicts with schema, n_pairs). Returns (schema, source) or (None, reason)."""
    import engine as E
    if not derived:
        return None, "no_derived_schema"
    src = min(derived, key=lambda d: (-d.get("n_pairs", 0), d["schema"]))["schema"]
    rt = root_split(src)
    if rt is None:
        return None, "source_has_no_root_operator"
    prim, a, b = rt
    alts = [n for n in sorted(E.PRIMITIVES) if n != prim]
    rng = random.Random(I._seed(NEAR_TAG % seed))
    rng.shuffle(alts)
    known = [d["schema"] for d in derived]
    for n in alts:
        w = E.PRIMITIVES[n][1].format(a, b)
        if len(T3D.instantiate(w)) < 2 or w in known:
            continue
        if any(INS.equal_extensional(w, k) for k in known):
            continue
        return w, src
    return None, "no_valid_perturbation"


def memo_plant(classes):
    """One entry per distinct observed FOLD program (verbatim). Expression programs have no fold entry; skipped."""
    progs = []
    for c in classes:
        for p in c["observed"]:
            if p[0] == "fold" and tuple(p) not in progs:
                progs.append(tuple(p))
    return [{"name": "memo_plant_%d" % k, "inits": [p[1]], "bodies": [p[2]], "finals": [p[3]]}
            for k, p in enumerate(sorted(progs))]


# ------------------------------------------------------------------ scoring by qualified walks
def _cells_used(cells):
    if CELLS_PER_FAMILY is None:
        return list(cells)
    seen, out = {}, []
    for c in cells:
        seen[c.family] = seen.get(c.family, 0) + 1
        if seen[c.family] <= CELLS_PER_FAMILY:
            out.append(c)
    return out


def walk_table(cands, cells, prov, cap=SEL_CAP):
    """name -> list of per-cell first_qualified results (same order as cells). Identical libraries walk once."""
    import meta_tribunal as M
    import tribunal_t4 as T4v1
    saved = (M._P, T4v1._P)
    try:
        quals = {}
        cache, out, n_walks = {}, {}, 0
        for name, ents in cands.items():
            lib = FR.KLib(ents)
            key = hashlib.sha256(lib.content()).hexdigest()
            if key not in cache:
                res = []
                for c in cells:
                    if c.family not in quals:
                        quals[c.family] = INS.qualifier(prov, c.family, *TRIBUNAL)
                    a17.M.use_provider(prov)
                    res.append(walk.first_qualified(lib, c, cap, quals[c.family], MAX_SPURIOUS))
                    n_walks += 1
                cache[key] = res
            out[name] = cache[key]
        return out, n_walks
    finally:
        M._P, T4v1._P = saved


def table_from_walks(walks, cands, start, cells, fold_sets, sha_of, cap=SEL_CAP, prov=None):
    ok = lambda r: bool(r) and not r.get("censored", True)  # noqa: E731
    inh = walks[REF]
    fold_of = {f: k for k, fs in enumerate(fold_sets) for f in fs}
    table = {}
    for name in cands:
        rs = walks[name]
        hit = set()
        allq = True
        for c, r, p in zip(cells, rs, inh):
            if ok(r) and not ok(p):
                hit.add(c.family)
                if prov is not None:   # explicit re-check of every reached program (DIRECT path, v1a)
                    allq = allq and INS.qualify_direct(prov, c.family, r["program"], TRIBUNAL[0])[0]
        rb = [sum(1 for f in hit if fold_of.get(f) == k) for k in range(len(fold_sets))]
        ch = lambda r: r["charge"] if ok(r) else cap  # noqa: E731
        saving = sum(ch(p) - ch(r) for r, p in zip(rs, inh))
        row = score_row(rb, description_length(cands[name], start), allq, saving, sha_of[name], name == REF)
        row.update({"reached_families": sorted(hit), "n_cells": len(rs),
                    "mean_paired_saving": round(saving / max(1, len(rs)), 2), "lower95_one_sided": None,
                    "qualified_cells": sum(1 for r in rs if ok(r))})
        table[name] = row
    return table


# ------------------------------------------------------------------ per-job patch (install / reset)
_ORIG = {}
LAST = {}


def _originals():
    """The true engine functions (never a b02/g12 wrapper): checked by module + name."""
    if not _ORIG:
        _ORIG["select"], _ORIG["cands"] = a17.select, a17.candidates_from
    for k, mod, nm in (("select", "a17", "select"), ("cands", "a17", "candidates_from")):
        f = _ORIG[k]
        assert f.__module__ == mod and f.__name__ == nm, "g12: captured a wrapper, not the engine %s" % nm
    return _ORIG


def install(seed, prov, arm="g12", plants=True):
    o = _originals()
    ctx = {"seed": seed, "derived": None, "classes": None}
    LAST.clear()

    def cands_hook(derived, start, classes):
        ctx["derived"], ctx["classes"] = derived, classes
        return o["cands"](derived, start, classes)

    def select12(cands, start, cells):
        t0 = time.perf_counter()
        info = {}
        if plants:
            cands["PLANT_OFF"] = [a17.schema_entry("g2_new", gtc.OFF_SCHEMA)] + start
            mp = memo_plant(ctx["classes"] or [])
            if mp:
                cands["PLANT_MEMO"] = mp + start
            info["memo_plant_programs"] = len(mp)
            nm, src = near_miss(ctx["derived"] or [], seed)
            if nm:
                cands["PLANT_NEAR"] = [a17.schema_entry("g2_new", nm)] + start
            info["near_miss"] = {"schema": nm, "source_or_reason": src}
        used = _cells_used(cells)
        fs = folds([c.family for c in used], seed)
        sha_of = {n: FR.KLib(e).sha256() for n, e in cands.items()}
        W, nw = walk_table(cands, used, prov)
        t1 = time.perf_counter()
        table = table_from_walks(W, cands, start, used, fs, sha_of, SEL_CAP, prov)
        arms = {a: arm_choice(table, a) for a in ARMS}
        i0 = None
        t2 = time.perf_counter()
        if DIAG_I0:
            ch0, tab0, _ = o["select"](cands, start, cells)
            i0 = {"chosen": ch0, "table": {k: {x: v[x] for x in ("mean_paired_saving", "lower95_one_sided",
                                                                 "eligible")} for k, v in tab0.items()}}
        LAST.update({"folds": fs, "table": table, "arms": arms, "info": info, "i0": i0, "n_walks": nw,
                     "n_cells": len(used), "walk_seconds": round(t1 - t0, 1),
                     "i0_seconds": round(time.perf_counter() - t2, 1), "cands": cands,
                     "walks": {n: [[r["charge"], bool(r["censored"]), r.get("stopped")] for r in W[n]] for n in W},
                     "cell_ids": [[c.family, c.r] for c in used]})
        vcost = sum(r[0] for v in LAST["walks"].values() for r in v)
        return arms[arm], table, vcost

    a17.select = select12
    a17.candidates_from = cands_hook


def reset():
    if _ORIG:
        a17.select, a17.candidates_from = _ORIG["select"], _ORIG["cands"]


# ------------------------------------------------------------------ donor job
def donor12(a):
    """a = (tag, mode, width, seed, fams, panel, start). mode 'g12' = g12 rule with plants (joint arms);
    'g12_noplant' = g12 rule, natural candidates only; 'off' = no patch at all (continuity: plain gtc g0 donor).
    Mirrors b02._donor exactly apart from the selector."""
    import b02
    tag, mode, width, s, fams, panel, start = a
    b02.T.init_worker()
    import a18_c1
    a17.R_VAL = a18_c1.R_VAL_C1
    b02._set_rule("g0")                     # neutralise any b02 patch (no-op when none is installed)
    fl = [dict(f, qualified_dev_size=f["Q2_size"]) for f in fams]
    specs = {f["name"]: (f["body"], f["final"], f["init"]) for f in fl}
    t0 = time.perf_counter()
    try:
        if mode != "off":
            install(s, a17.Prov(specs), "g12", plants=(mode == "g12"))
        args = ("LIN%d" % s, "P", s, fl, specs, panel, True) + ((start,) if start is not None else ())
        r = gtc.donor_g("g0", args)
    finally:
        reset()
    row = {"tag": tag, "rule": mode, "width": width, "seed": s, "selected": r["selected"],
           "selected_schema": r["selected_schema"], "selected_origin": r["selected_origin"],
           "selected_entries": r["selected_entries"], "n_observed": r["n_observed"], "n_derived": r["n_derived"],
           "classes": r["classes"], "seconds": r["seconds"], "memorise_selected": r["selected"] == "MEMORISE"}
    if mode != "off":
        L = LAST
        row["g12"] = {
            "params": params(), "folds": L["folds"], "n_cells": L["n_cells"], "n_walks": L["n_walks"],
            "walk_seconds": L["walk_seconds"], "i0_seconds": L["i0_seconds"], "info": L["info"],
            "table": {k: {x: v[x] for x in ("reach_by_fold", "reach_min", "reach_total", "DL", "S", "saving",
                                            "eligible", "all_reached_qualified", "reached_families", "sha256",
                                            "qualified_cells")} for k, v in L["table"].items()},
            "arms": {a_: {"chosen": c, "entries_sha": hashlib.sha256(json.dumps(L["cands"][c], sort_keys=True)
                                                                       .encode()).hexdigest()[:16],
                          "plant_selected": c.startswith("PLANT_")} for a_, c in L["arms"].items()},
            "arm_entries": {a_: L["cands"][c] for a_, c in L["arms"].items()},
            "i0_diag": L["i0"], "walks": L["walks"], "cell_ids": L["cell_ids"],
            "schemas": {k: (v[0].get("schema") or v[0].get("schemas") or v[0].get("name"))
                        for k, v in L["cands"].items() if k != REF}}
        row["seconds_total"] = round(time.perf_counter() - t0, 1)
    return row


def run_job(j):
    """(kind, args): kind 'g12' -> donor12(args); 'b02' -> b02._donor(args). For mixed sequences in one worker."""
    import b02
    kind, a = j
    return donor12(a) if kind == "g12" else b02._donor(a)


def params():
    return {"LAMBDA": LAMBDA, "FOLD_TAG": FOLD_TAG, "NEAR_TAG": NEAR_TAG, "N_FOLDS": N_FOLDS, "SEL_CAP": SEL_CAP,
            "CELLS_PER_FAMILY": CELLS_PER_FAMILY, "TRIBUNAL": list(TRIBUNAL), "MAX_SPURIOUS": MAX_SPURIOUS,
            "FALLBACK": FALLBACK, "TIE_BREAK": TIE_BREAK, "DL": "entry_dl (generators + non-default inits/finals)"}


# ------------------------------------------------------------------ post-hoc re-scoring of a recorded job (no walks)
def rescore(row, cap=None, cells_per_family=None, lam=None):
    """Re-derive the table + arm choices from a donor12 row's recorded walks at a LOWER cap and/or fewer cells per
    family. Exact for cap <= SEL_CAP (a first-qualified charge <= cap is the same walk prefix). Used for the cost/
    sensitivity note only."""
    g = row["g12"]
    cap = cap or g["params"]["SEL_CAP"]
    lam = LAMBDA if lam is None else lam
    ids = g["cell_ids"]
    keep, seen = [], {}
    for i, (f, _r) in enumerate(ids):
        seen[f] = seen.get(f, 0) + 1
        if cells_per_family is None or seen[f] <= cells_per_family:
            keep.append(i)
    ok = lambda w: (not w[1]) and w[0] <= cap  # noqa: E731
    fold_of = {f: k for k, fs in enumerate(g["folds"]) for f in fs}
    inh = g["walks"][REF]
    tab = {}
    for n, ws in g["walks"].items():
        hit = {ids[i][0] for i in keep if ok(ws[i]) and not ok(inh[i])}
        rb = [sum(1 for f in hit if fold_of[f] == k) for k in range(len(g["folds"]))]
        sv = sum((inh[i][0] if ok(inh[i]) else cap) - (ws[i][0] if ok(ws[i]) else cap) for i in keep)
        dl = g["table"][n]["DL"]
        S = min(rb) - lam * dl
        tab[n] = {"S": S, "saving": sv, "sha256": g["table"][n]["sha256"], "reach_by_fold": rb,
                  "eligible": n != REF and S > 0 and g["table"][n]["all_reached_qualified"], "DL": dl}
    return tab, {a: arm_choice(tab, a) for a in ARMS}
