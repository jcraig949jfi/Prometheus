"""Cycle-9 adjudication: bundle store + frozen manifest -> ADJUDICATION_C9.json.

Reads ONLY the bundle store (the P-7 record) and MANIFEST_FROZEN.json, which says which
bundle belongs to which hypothesis, specimen and stratum. Every verdict comes from
`hypotheses.py` with thresholds from the hash-covered constants object. An incomplete
bundle is counted and reported, never silently dropped: each hypothesis carries
n_bundles beside n_complete.

    python adjudicate_c9.py [observatory]
"""
from __future__ import annotations

import json
import pathlib
import sys
from collections import defaultdict

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import bundles as BD          # noqa: E402
import hypotheses as HY       # noqa: E402
from constants import C, CONSTANTS_SHA256   # noqa: E402
from run_campaign import spec_of            # noqa: E402


def load(obs, manifest):
    store = BD.BundleStore(pathlib.Path(obs) / "bundles")
    out = defaultdict(list)
    for b in manifest["bundles"]:
        spec = spec_of(b)
        st = store.get(spec.bundle_id)
        out[b["hypothesis_id"]].append({"bundle_id": spec.bundle_id, "meta": b,
                                        "results": (st.results if st else {})})
    return out


def adjudicate(obs, manifest):
    by = load(obs, manifest)
    res = {"constants_sha256": CONSTANTS_SHA256, "rules": dict(C), "hypotheses": {}}
    if by.get("H1"):
        res["hypotheses"]["H1"] = HY.h1(by["H1"])
    if by.get("H2"):
        specs = defaultdict(lambda: {"stratum": None, "bundles": []})
        for b in by["H2"]:
            sp = specs[b["meta"]["specimen"]]
            sp["stratum"] = b["meta"]["stratum"]
            sp["bundles"].append(b)
        complete = {k: v for k, v in specs.items()}
        panel = HY.h2_panel(complete)
        # A-16 sensitivity: the same panel rule read on literal last-write authorship depth
        lit = {k: {"stratum": v["stratum"],
                   "bundles": [{"results": {a: dict(s, max_causal_replication_depth=
                                                     s.get("max_causal_replication_depth_literal"))
                                            for a, s in b["results"].items()}}
                               for b in v["bundles"]]} for k, v in specs.items()}
        panel_lit = HY.h2_panel(lit)
        res["hypotheses"]["H2"] = {
            "verdict": panel["verdict"], "primary": panel,
            "sensitivity_literal_authorship": {"verdict": panel_lit["verdict"],
                                               "supporting": panel_lit["supporting"]},
            "n_bundles": len(by["H2"]),
            "n_complete": sum(1 for b in by["H2"] if len(b["results"]) == 3)}
    if by.get("H3"):
        per_cell = defaultdict(list)
        for b in by["H3"]:
            per_cell[b["meta"]["source_specimen"]].append(b)
        res["hypotheses"]["H3"] = dict(HY.h3(by["H3"]),
                                       per_cell_secondary={k: HY.h3(v) for k, v in per_cell.items()})
    return res


def main(argv):
    obs = HERE / (argv[1] if len(argv) > 1 else "observatory")
    manifest = json.loads((HERE / "MANIFEST_FROZEN.json").read_text())
    res = adjudicate(obs, manifest)
    (obs / "ADJUDICATION_C9.json").write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps({h: v["verdict"] for h, v in res["hypotheses"].items()}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
