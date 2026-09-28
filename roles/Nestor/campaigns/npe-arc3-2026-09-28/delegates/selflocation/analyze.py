"""Aggregate results.jsonl into classes, per-test counts and predictive tables -> selfloc_results.json.
Class and flag definitions are the ones frozen in DECLARATIONS.md."""
from __future__ import annotations

import collections
import json
import math
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
P = 0.5
OFFS = ("T1_d1", "T1_d4", "T1_d8", "T1_d16", "T1_d32", "T1_d48")
D32S = ("D32_HL_SELF", "D32_DE_PARTNER", "D32_HLDE", "D32_PTRSHIFT")
FOLLOW = ("ROT+1_FOLLOW", "ROT+4_FOLLOW", "ROT+16_FOLLOW", "ROT-4_FOLLOW")


def ok(r, c):
    return r["rates"][c] >= P


def classify(r):
    n_off = sum(ok(r, c) for c in OFFS)
    if n_off >= 5:
        cls = "LOCATOR"
    elif ok(r, "T1_d32"):
        cls = "PARTIAL"
    elif any(ok(r, c) for c in D32S):
        cls = "STATE_ANCHORED"
    else:
        cls = "TAPE_ANCHORED"
    flags = {
        "STATE_FREE": ok(r, "I_RAND") and ok(r, "I_CONST55") and ok(r, "I_CONSTFF"),
        "WRAP_DEPENDENT": not ok(r, "G256_ADJ"),
        "PARTNER_REL": not (ok(r, "P_NOEXEC") and ok(r, "P_BLANK")),
        "SENSE_READ": not ok(r, "SENSE_FLIP"),
        "ORDER_DEP": not ok(r, "ORDER_FLIP"),
        "POS_INDEP_CODE": sum(ok(r, c) for c in FOLLOW) >= 3,
    }
    return cls, flags, n_off


def fisher(a, b, c, d):
    """two-sided Fisher exact p for [[a,b],[c,d]]"""
    n = a + b + c + d
    r1, c1 = a + b, a + c

    def pr(x):
        return math.comb(c1, x) * math.comb(n - c1, r1 - x) / math.comb(n, r1)
    p0 = pr(a)
    lo, hi = max(0, r1 - (n - c1)), min(r1, c1)
    return min(1.0, sum(pr(x) for x in range(lo, hi + 1) if pr(x) <= p0 * (1 + 1e-9)))


def table(rows, fr, fc):
    t = collections.defaultdict(collections.Counter)
    for r in rows:
        t[fr(r)][fc(r)] += 1
    return {str(k): dict(v) for k, v in sorted(t.items(), key=lambda kv: str(kv[0]))}


def main():
    R = [json.loads(x) for x in open(HERE / "results.jsonl")]
    for r in R:
        r["lineage"] = r["origin_run"]
        ss = r["ss_rates"]
        r["poison"] = ("UNMEASURABLE" if ss[0] < 0.1 else ("SELF_POISON" if ss[1] < 0.25 * ss[0] else "SELF_OK"))
        r["reset_competent"] = ss[0] >= 0.5
        r["cls"], r["flags"], r["n_off"] = classify(r)
    elig = [r for r in R if ok(r, "REF")]
    out = {"n_results": len(R), "n_eligible": len(elig),
           "n_ineligible_by_selfdep": dict(collections.Counter(r["self_dep"] for r in R if not ok(r, "REF")))}
    conds = list(R[0]["rates"])
    # per-condition pass counts among eligible, by SELF-dependence
    pc = {}
    for c in conds:
        pc[c] = {"all": sum(ok(r, c) for r in elig),
                 "self_dep": sum(ok(r, c) for r in elig if r["self_dep"]),
                 "self_indep": sum(ok(r, c) for r in elig if not r["self_dep"]),
                 "mean_rate": round(sum(r["rates"][c] for r in elig) / len(elig), 3)}
    out["n_elig_self_dep"] = sum(r["self_dep"] for r in elig)
    out["n_elig_self_indep"] = sum(not r["self_dep"] for r in elig)
    out["home"] = table(elig, lambda r: r["self_dep"], lambda r: r["home"])
    out["per_condition_pass"] = pc
    out["offsets_passed_hist"] = table(elig, lambda r: r["n_off"], lambda r: r["self_dep"])
    out["class_counts"] = table(elig, lambda r: r["cls"], lambda r: "self_dep" if r["self_dep"] else "self_indep")
    out["class_by_cell"] = table(elig, lambda r: r["cls"], lambda r: r["cell"])
    out["class_lineages"] = {c: len({r["lineage"] for r in elig if r["cls"] == c}) for c in
                             sorted({r["cls"] for r in elig})}
    out["flag_counts"] = {f: {"true": sum(r["flags"][f] for r in elig),
                              "true_by_class": dict(collections.Counter(r["cls"] for r in elig if r["flags"][f]))}
                          for f in elig[0]["flags"]}
    # predictive tables
    out["a_class_x_poison"] = table(elig, lambda r: r["cls"], lambda r: r["poison"])
    out["a_statefree_x_poison"] = table(elig, lambda r: r["flags"]["STATE_FREE"], lambda r: r["poison"])
    out["a_class_statefree_x_poison"] = table(elig, lambda r: (r["cls"], r["flags"]["STATE_FREE"]),
                                              lambda r: r["poison"])
    out["b_class_x_reset_competent"] = table(elig, lambda r: r["cls"], lambda r: r["reset_competent"])
    out["b_statefree_x_reset_competent"] = table(elig, lambda r: r["flags"]["STATE_FREE"],
                                                 lambda r: r["reset_competent"])
    out["c_class_x_selfdep"] = table(elig, lambda r: r["cls"], lambda r: r["self_dep"])
    out["c_statefree_x_selfdep"] = table(elig, lambda r: r["flags"]["STATE_FREE"], lambda r: r["self_dep"])
    out["a_selfdep_x_poison"] = table(elig, lambda r: r["self_dep"], lambda r: r["poison"])
    # Fisher tests on 2x2 contrasts (measurable poison only)
    m = [r for r in elig if r["poison"] != "UNMEASURABLE"]

    def f2(pred, outcome, rows):
        a = sum(1 for r in rows if pred(r) and outcome(r))
        b = sum(1 for r in rows if pred(r) and not outcome(r))
        c = sum(1 for r in rows if not pred(r) and outcome(r))
        d = sum(1 for r in rows if not pred(r) and not outcome(r))
        return {"table[[pred&out,pred&~out],[~pred&out,~pred&~out]]": [[a, b], [c, d]], "p": fisher(a, b, c, d)}
    poi = lambda r: r["poison"] == "SELF_POISON"  # noqa: E731
    out["fisher"] = {
        "statefree_vs_poison": f2(lambda r: r["flags"]["STATE_FREE"], poi, m),
        "tape_vs_state_anchor_poison": f2(lambda r: r["cls"] == "STATE_ANCHORED", poi,
                                          [r for r in m if r["cls"] in ("STATE_ANCHORED", "TAPE_ANCHORED")]),
        "tape_vs_state_anchor_poison_selfindep": f2(
            lambda r: r["cls"] == "STATE_ANCHORED", poi,
            [r for r in m if r["cls"] in ("STATE_ANCHORED", "TAPE_ANCHORED") and not r["self_dep"]]),
        "class_given_statefree_false": f2(lambda r: r["cls"] == "STATE_ANCHORED", poi,
                                          [r for r in m if not r["flags"]["STATE_FREE"]
                                           and r["cls"] in ("STATE_ANCHORED", "TAPE_ANCHORED")]),
        "selfdep_vs_poison": f2(lambda r: r["self_dep"], poi, m),
        "statefree_vs_reset_competent": f2(lambda r: r["flags"]["STATE_FREE"], lambda r: r["reset_competent"], elig),
    }
    # lineage-level check: one vote per origin run (majority label)
    L = collections.defaultdict(list)
    for r in m:
        L[r["lineage"]].append(r)
    lv = []
    for k, v in L.items():
        sf = sum(r["flags"]["STATE_FREE"] for r in v) * 2 >= len(v)
        po = sum(poi(r) for r in v) * 2 >= len(v)
        lv.append((sf, po))
    out["lineage_statefree_x_poison"] = {"n_lineages": len(lv),
                                         "sf_poison": sum(1 for s, p in lv if s and p),
                                         "sf_ok": sum(1 for s, p in lv if s and not p),
                                         "nsf_poison": sum(1 for s, p in lv if not s and p),
                                         "nsf_ok": sum(1 for s, p in lv if not s and not p)}
    out["genomes"] = [{k: r[k] for k in ("hex", "vm", "cell", "origin_run", "nocopy_donor", "self_dep", "home",
                                         "cls", "flags", "n_off", "poison", "reset_competent", "ss_rates", "rates")}
                      for r in R]
    (HERE / "selfloc_results.json").write_text(json.dumps(out, indent=1))
    show = {k: v for k, v in out.items() if k != "genomes"}
    print(json.dumps(show, indent=1))


if __name__ == "__main__":
    main()
