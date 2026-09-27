"""Apply the frozen NPE lens (adapters/npe.py) to the preserved replay records (no re-execution)."""
from __future__ import annotations

import collections
import json
from pathlib import Path

from archaeon.causal_lens.adapters import npe as A
from archaeon.causal_lens.fossils_npe import EVID, OUT


def main():
    res = {}
    for p in sorted(EVID.glob("*__s*__*.replay.json")):
        rec = json.loads(p.read_text(encoding="utf-8")); L = A.lens(rec)
        ev = L["events"]; name = p.name[:-len(".replay.json")]
        pair = [e for e in ev if e["kind"] == "PAIR_OVERWRITE"]
        joint = collections.Counter()
        for e in pair:
            n = e["native"]
            joint["lens=%s|p11pass=%s|C4=%s|C5=%s|parent_is_donor=%s" % ("resolved" if e["resulting_hu"] != "NOT_IDENTIFIABLE" else "NI",
                  n.get("p11_pass"), n.get("p11_C4"), n.get("p11_C5"), e["native_parent_is_donor"])] += 1
        shares = [e["donor_authored_share"] for e in pair if e["donor_authored_share"] is not None]
        spont = collections.Counter((e["kind"], e["lens_spontaneous"]) for e in ev)
        res[name] = {"job": rec["job"] if "job" in rec else None, "births": len(ev), "by_kind": dict(collections.Counter(e["kind"] for e in ev)),
                     "pair_joint_lens_native": dict(joint), "donor_authored_share": {"n": len(shares), "ge_0.5": sum(1 for s in shares if s >= 0.5),
                     "min": min(shares) if shares else None, "median": sorted(shares)[len(shares) // 2] if shares else None},
                     "lens_spontaneous_by_kind": {"%s|%s" % k: v for k, v in spont.items()}, "hu_origin_classes": sorted(set(L["hu_origin"].values())),
                     "founders": L["founders"], "priv_events": len(rec["priv"]), "pair_events_observed": len(rec["pair"]),
                     "wall_s": rec.get("wall_s")}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "NPE_LENS_SUMMARY.json").write_text(json.dumps(res, indent=1, default=str) + "\n", encoding="utf-8", newline="\n")
    for k, v in res.items():
        print(k.split("__", 1)[1], v["births"], v["by_kind"], v["donor_authored_share"], v["lens_spontaneous_by_kind"])
        for kk, vv in sorted(v["pair_joint_lens_native"].items(), key=lambda x: -x[1])[:5]: print("     ", vv, kk)


if __name__ == "__main__":
    main()
