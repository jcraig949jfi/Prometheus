"""Nyx 2026-09-12: is cluster_bootstrap degenerate when the cluster count is a power of two?
Hypothesis: _Lcg.below(n) = state % n uses the low bits of a (mod 2^31) LCG; for n = 2^k the low k bits
cycle through every residue in order, so each resample of n draws picks every cluster exactly once and
the bootstrap distribution collapses to the point estimate. Appends to RECEIPT_N2_<date>.json."""
from __future__ import annotations
import datetime as _dt, importlib.util, json, random
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[3]
SRC = ROOT / "roles/Diomedes/coordinate_census.py"
spec = importlib.util.spec_from_file_location("coordinate_census", SRC)
cc = importlib.util.module_from_spec(spec); spec.loader.exec_module(cc)  # type: ignore
rng = random.Random(1)
out = {}
for n in (4, 5, 8, 16, 17, 24, 32, 100):
    clusters = {f"c{i}": [rng.gauss(0.5, 0.2) for _ in range(3)] for i in range(n)}
    cb = cc.cluster_bootstrap(clusters, n_boot=300)
    lcg = cc._Lcg(20260826)
    picks = [lcg.below(n) for _ in range(n)]
    picks2 = [lcg.below(n) for _ in range(n)]
    out[str(n)] = {"half_width": cb["half_width"], "distinct_in_first_resample": len(set(picks)),
                   "distinct_in_second": len(set(picks2)), "first_resample_is_a_permutation": sorted(picks) == list(range(n))}
rec_path = sorted(HERE.glob("RECEIPT_N2_*.json"))[-1]
rec = json.loads(rec_path.read_text(encoding="utf-8"))
rec["blocks"].append({"name": "C06-probe_lcg_power_of_two_degeneracy", "predicted": "half_width 0 and each resample a permutation exactly when n is a power of two; nonzero otherwise",
                      "observed": out, "error": None, "date": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")})
rec_path.write_text(json.dumps(rec, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
print(json.dumps(out, indent=1))
