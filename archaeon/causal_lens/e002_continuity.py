"""E-002 (C-001, TH-001): the candidate continuity criterion C-OP (T-007_CRITERION.md) beside the frozen v0.2.1 MAJORITY rule (C-MAJ).

Stdlib only. v0.2 / v0.3 are not modified. `continuity_op` is the candidate; `schema_v02.continuity` is the incumbent.

    python3 -m archaeon.causal_lens.e002_continuity fixtures OUT.json     (T-008: all 15 synthetic fixtures)
"""
from __future__ import annotations

import copy
import json
import math
import sys
from typing import Dict, Optional

from archaeon.causal_lens import corpus_v02 as C
from archaeon.causal_lens.schema_v02 import ILL, NI, NONE, continuity

MAJ = C.MAJ


def continuity_op(shares: Dict[str, object], operator: Optional[dict], roles: Optional[Dict[str, str]] = None) -> dict:
    """C-OP. shares {hu: share|NI}; operator None (undeclared) or
    {"name", "code_ref", "exchangeable": [[role, ...], ...], "rule": hu_rule for the privileged case}; roles {hu: role}."""
    if not shares: return {"hu_continuity": NONE, "clause": "no contributors"}
    if operator is None or not operator.get("code_ref"):
        if len(shares) == 1: return {"hu_continuity": next(iter(shares)), "clause": "single contributor (no operator needed)"}
        return {"hu_continuity": NI, "clause": "2: operator undeclared"}
    roles = roles or {h: h for h in shares}
    live = {h for h, v in shares.items() if v == NI or v > 0}
    for cls in operator.get("exchangeable", []):
        members = {h for h in live if roles.get(h) in cls}
        if len(members) >= 2:
            return {"hu_continuity": ILL, "clause": "3: exchangeable operator",
                    "ill_posed": {"rule": {"kind": "OPERATOR", "operator": operator["name"], "code_ref": operator["code_ref"]},
                                  "evidence": {"exchangeable_class": sorted(members), "shares": shares},
                                  "why": "operator %s privileges none of %s" % (operator["name"], sorted(members))}}
    r = continuity(shares, operator.get("rule", MAJ)); r["clause"] = "4: privileged operator -> declared rule"; return r


def binom_two_sided_p(k: int, n: int) -> float:
    """exact two-sided p of k successes in n under Binomial(n, 1/2) (M2)."""
    pk = math.comb(n, k); tot = 2 ** n
    return min(1.0, sum(math.comb(n, j) for j in range(n + 1) if math.comb(n, j) <= pk) / tot)


# ------------------------------------------------------------------------------------------------ T-008
EXCH = {"name": "declared_exchangeable", "code_ref": "(hypothetical declaration; the fixture records none)", "exchangeable": [["*"]]}
PRIV = {"name": "declared_privileged_first", "code_ref": "(hypothetical declaration; the fixture records none)", "exchangeable": [],
        "rule": MAJ}


def _shares_of(g, t):
    fc = g.nodes[t]["fields"].get("factual_contributors")
    if not fc: return None
    if fc.get("shares"): return dict(fc["shares"])
    if isinstance(fc["value"], list) and len(fc["value"]) == 1: return {fc["value"][0]: 1.0}
    return None


def _with_value(g, t, res):
    """re-express the fixture with C-OP's value and run the frozen v0.2 validator (representability check)."""
    h = copy.deepcopy(g); v = res["hu_continuity"]
    if v == ILL:
        h.field(t, "hu_continuity", ILL, "DERIVED", ill_posed=res["ill_posed"]); h.field(t, "resulting_hu", ILL, "DERIVED", ill_posed=res["ill_posed"])
        prods = set(h.out(t, "produced"))
        h.edges = [e for e in h.edges if not (e[1] == "member_of" and e[0] in prods)]; C._rebuild(h)
    elif v == NI:
        h.field(t, "hu_continuity", NI, "DERIVED"); h.field(t, "resulting_hu", NI, "DERIVED")
        prods = set(h.out(t, "produced"))
        h.edges = [e for e in h.edges if not (e[1] == "member_of" and e[0] in prods)]; C._rebuild(h)
    return h.check()


def fixtures() -> dict:
    out = {}
    for name, f in C.FIXTURES.items():
        g, exp, _ = f()
        for t in g.of_kind("TRANSFORMATION"):
            fd = g.nodes[t]["fields"]
            if "hu_continuity" not in fd: continue
            sh = _shares_of(g, t)
            row = {"fixture": name, "event": t, "shares": sh, "fixture_value": fd["hu_continuity"]["value"],
                   "declared_operator_in_fixture": g.nodes[t].get("operator") or g.meta.get("operator")}
            if sh is None or any(v == NI for v in sh.values()):
                row["C-MAJ"] = continuity(sh, MAJ)["hu_continuity"] if sh else fd["hu_continuity"]["value"]
                row["note"] = "no complete share evidence in the fixture"; out["%s/%s" % (name, t)] = row; continue
            row["C-MAJ"] = continuity(sh, MAJ)["hu_continuity"]
            for lab, op in (("C-OP|undeclared", None), ("C-OP|exchangeable", EXCH), ("C-OP|privileged", PRIV)):
                roles = {h: "*" for h in sh} if op is EXCH else {h: h for h in sh}
                r = continuity_op(sh, op, roles)
                row[lab] = r["hu_continuity"]; row[lab + ":clause"] = r["clause"]
                row[lab + ":v02_violations"] = _with_value(g, t, r)
            vals = {row[k] for k in ("C-OP|undeclared", "C-OP|exchangeable", "C-OP|privileged")}
            row["verdict_depends_on_declaration"] = len(vals) > 1
            out["%s/%s" % (name, t)] = row
    return out


def main(argv):
    what, path = argv[0], argv[1]
    res = {"fixtures": fixtures}[what]()
    with open(path, "w", encoding="utf-8", newline="\n") as fh: json.dump(res, fh, indent=1, sort_keys=True, default=str); fh.write("\n")
    return res


if __name__ == "__main__":
    r = main(sys.argv[1:])
    for k, v in r.items():
        print(k, {kk: vv for kk, vv in v.items() if not kk.endswith(":v02_violations") and not kk.endswith(":clause")})
