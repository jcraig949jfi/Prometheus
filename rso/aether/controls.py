"""C-018-T030 falsifiability audit of every claim-critical control (rso/qualify/FALSIFIABILITY.md; rso/qualify/falsifiable.py).

    python -m rso.aether.controls        -> qual/FALSIFIABILITY_AUDIT.json, exit 1 unless every registered row is ok

Each control is audited on the stored DEVELOPMENT / qualification records only (qual/records): fixtures, near-misses,
counterfeits, graded content and development native units. No confirmatory seed. Rows and their six answers are
PREREGISTRATION.md s4; this module is the executable half. A detector here is the evaluator's own function, so the audit
tests the instrument that will read the confirmatory data.
"""
import glob
import json
import os
import sys

import numpy as np

from rso.aether import adapter as A, evaluate as E, qualify as Q
from rso.qualify import falsifiable as FZ

OUT = os.path.join(os.path.dirname(Q.OUT), "FALSIFIABILITY_AUDIT.json")


def _units():
    out = {}
    for p in sorted(glob.glob(os.path.join(Q.REC, "*.json"))):
        out[os.path.basename(p)[:-5]] = A.load_unit(p[:-5])
    return out


def _all_equal(preds, truths):
    return list(preds) == list(truths)


def _scrub_recipe(x):
    """Remove only answer-bearing fields: the fixture name / case label a recipe reader would key on."""
    meta, a = x
    m = {k: v for k, v in meta.items() if k not in ("fixture", "case")}
    return m, a


def audit():
    U = _units()
    fix = {k: v for k, v in U.items() if k.startswith("fix_")}
    nat = {k: v for k, v in U.items() if k.startswith("native_")}
    case = lambda name: [fix["fix_%s_%d" % (name, s)] for s in Q.FSEEDS]       # noqa: E731
    rows = []

    # C1 locality (light cone). Native laws cannot violate it (4-neighbour gather): a SANITY GUARD, not evidence.
    lc = lambda x: "OK" if E.light_cone(*x)[0] else "VIOLATION"                 # noqa: E731
    cases = [(x, "OK") for x in case("A") + case("B") + list(nat.values())] + [(x, "VIOLATION") for x in case("TELEPORT")]
    rows.append(FZ.audit("C1 light cone", lc, _all_equal, cases, ["OK", "VIOLATION"], must_discriminate=["OK", "VIOLATION"],
                         scrub=_scrub_recipe, near_misses=[(x, "VIOLATION", "a local relay") for x in case("TELEPORT")]))

    # C2 + C3 ancestry class (clamp of the claimed ancestor + clamp of a divergent non-ancestor)
    anc = lambda x: E.ancestry(*x)["cls"]                                       # noqa: E731
    exp = {n: v[4] for n, v in Q.ANCESTRY_CASES.items()}
    cases = [(x, exp[n]) for n in exp for x in case(n)]
    nm = [(x, exp[n], what) for n, what in (("E", "a content relay (decodable, 7 t0 sites)"),
                                           ("A_wrongB", "an attributed ancestor"),
                                           ("A_misN", "a specific ancestor (its 'non-ancestor' is upstream)"),
                                           ("A_vacN", "a passed non-ancestor control (the clamp is the identity)"))
          for x in case(n)]
    rows.append(FZ.audit("C2/C3 interventional ancestry", anc, _all_equal, cases, list(E.CLASSES),
                         must_discriminate=["CONFIRMED", "NONSPECIFIC", "NOT_INTERVENTIONAL", "CONTROL_VACUOUS", "MULTI_SOURCE"],
                         scrub=_scrub_recipe, near_misses=nm))

    # C3 alone: a non-ancestor clamp that never diverges is the identity; the evaluator must call it VACUOUS, not a pass
    spec = lambda x: (lambda r: "VACUOUS" if r["cls"] == "CONTROL_VACUOUS" else            # noqa: E731
                      "NONSPECIFIC" if r["cls"] == "NONSPECIFIC" else "SPECIFIC")(E.ancestry(*x))
    cases = [(x, "SPECIFIC") for x in case("A") + case("B")] + [(x, "NONSPECIFIC") for x in case("A_misN")] + \
        [(x, "VACUOUS") for x in case("A_vacN")]
    rows.append(FZ.audit("C3 non-ancestor clamp", spec, _all_equal, cases, ["SPECIFIC", "NONSPECIFIC", "VACUOUS"],
                         must_discriminate=["SPECIFIC", "NONSPECIFIC", "VACUOUS"], scrub=_scrub_recipe,
                         near_misses=[(x, "VACUOUS", "a specific control") for x in case("A_vacN")] +
                         [(x, "NONSPECIFIC", "a specific control") for x in case("A_misN")]))

    # C4/C10 intervention identity (t0)
    t0 = lambda x: "SINGLE" if len(E.t0_sites(x[1])) == 1 else "MULTI"         # noqa: E731
    cases = [(x, "SINGLE") for x in case("A") + case("B") + case("G") + list(nat.values())] + \
        [(x, "MULTI") for x in case("E") + case("N")]
    rows.append(FZ.audit("C4/C10 t0 identity", t0, _all_equal, cases, ["SINGLE", "MULTI"], must_discriminate=["SINGLE", "MULTI"],
                         scrub=_scrub_recipe, near_misses=[(x, "MULTI", "a single-source impulse") for x in case("E")]))

    # C5/C7/C8 content: the decoder's verdict per fixture population (Aether decoder on stored features)
    def content(path):
        acc = E.decode(Q._feats(path))
        return "ABOVE" if E.excess_all(acc) >= E.MARGIN else "BELOW"
    rec = lambda f: os.path.join(Q.REC, f)                                     # noqa: E731
    cases = [(rec("content_A.npz"), "ABOVE"), (rec("content_E.npz"), "ABOVE"), (rec("content_B.npz"), "BELOW"),
             (rec("content_N.npz"), "BELOW"), (rec("graded_000.npz"), "BELOW"), (rec("graded_025.npz"), "ABOVE")]
    rows.append(FZ.audit("C5/C7/C8 content above margin", content, _all_equal, cases, ["ABOVE", "BELOW"],
                         must_discriminate=["ABOVE", "BELOW"],
                         near_misses=[(rec("content_B.npz"), "BELOW", "an ancestry chain (structure without content)"),
                                      (rec("content_N.npz"), "BELOW", "divergence (noise in the same cells)"),
                                      (rec("graded_000.npz"), "BELOW", "a relay whose labels are independent of the branch")]))

    # Native record binding: the evaluator must not trust a producer field (trusts_derived) and must refuse a tree that
    # disagrees with the observed divergence (near-miss: a tree with one site dropped)
    nl = list(nat.values())
    tc = lambda x: "CONSISTENT" if not E.tree_check(*x) else "INCONSISTENT"   # noqa: E731

    def drop_site(x):
        m = json.loads(json.dumps(x[0]))
        for k in ("site", "gen", "parent", "ftick", "type"):
            m["tree"][k] = m["tree"][k][:-1]
        return m, x[1]
    bad = [drop_site(x) for x in nl]
    rows.append(FZ.audit("native tree cross-check", tc, _all_equal, [(x, "CONSISTENT") for x in nl] +
                         [(x, "INCONSISTENT") for x in bad], ["CONSISTENT", "INCONSISTENT"],
                         must_discriminate=["CONSISTENT", "INCONSISTENT"],
                         near_misses=[(x, "INCONSISTENT", "Aether's attribution of the observed divergence") for x in bad]))
    an = lambda xs: [E.ancestry(*x)["cls"] for x in xs]                         # noqa: E731
    tamper = lambda xs: [(dict(m, producer_cls="CONFIRMED"), dict(a, ftick_cutB=a["ftick_impulse"].copy()))  # noqa: E731
                         for m, a in xs]
    derived = FZ.trusts_derived(an, case("A") + case("B"), tamper)
    out = {"rows": rows, "trusts_derived_producer_cls": derived, "n_native_dev": len(nl),
           "P4_C9": "UNSUPPORTED natively: not constructed (SELECTION.md s6; demand_result.json p4_express01_tables C3/REPLACE "
                    "output is a function of b alone)"}
    out["ok"] = all(r["ok"] for r in rows) and not derived
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(out, indent=1, sort_keys=True, default=str) + "\n")
    for r in rows:
        print(r["control"], "ok" if r["ok"] else "FINDING", {k: r[k] for k in ("cannot_discriminate", "constant_passes",
                                                                               "oracle_fails", "reads_answer", "near_miss_wrong")})
    print("trusts_derived", derived, "ALL OK" if out["ok"] else "NOT OK")
    return 0 if out["ok"] else 1


if __name__ == "__main__":
    sys.exit(audit())
